// Re-docking benchmark: take a ligand out of the crystal structure it was solved in, dock it back blind,
// and measure how far the top-scoring pose is from where the experiment put it.
//
// Under 2 Å is the usual bar for calling a re-docking successful. This runs the app's own scoring and
// search code in Node, with no browser, so the numbers come from the shipped implementation.
//
//   node evals/redock.mjs            # the default set
//   node evals/redock.mjs 2V5Z:SAG   # one case
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { parsePDB, parseMolblock } from '../js/structure.js';
import { ProteinGrid, vinaScore, dockLigand, rmsd, centroid } from '../js/dock.js';

// Each case is a complex where the bound ligand is drug-like and the site is well defined.
//
// Four cases was a smoke test: with one success or failure worth 25 points, a
// single lucky run looked like a validation study. These eleven still are not
// one -- the Astex Diverse Set is 85 -- but they span kinase, protease,
// nuclear-receptor, metalloenzyme and protein-protein-interface sites rather
// than four targets that happen to suit a shape-and-hydrophobicity score.
//
// Ligand codes were resolved from the RCSB entry API rather than typed from
// memory, and every SDF was confirmed to download before the case was added.
// 1P62 was considered and dropped: its largest ligand is ADP, a cofactor, so
// re-docking it would measure nucleotide placement and be reported as drug
// docking.
export const CASES = [
  // --- original four -------------------------------------------------------
  { pdb: '2V5Z', lig: 'SAG', note: 'MAO-B with safinamide (Parkinson\'s)' },
  { pdb: '2YXJ', lig: 'N3C', note: 'BCL-XL with ABT-737' },
  { pdb: '1OYT', lig: 'FSN', note: 'thrombin with an inhibitor' },
  { pdb: '3ERT', lig: 'OHT', note: 'oestrogen receptor with 4-hydroxytamoxifen' },

  // --- kinases: the ATP pocket is the most-docked site in the field ---------
  { pdb: '1YWR', lig: 'LI9', note: 'p38 MAP kinase, inactive conformation' },
  { pdb: '1UNL', lig: 'RRC', note: 'CDK5/p25 with roscovitine analogue' },
  { pdb: '1Q41', lig: 'IXM', note: 'GSK-3 beta with indirubin-3-monoxime' },

  // --- other site chemistries ---------------------------------------------
  { pdb: '1S19', lig: 'MC9', note: 'vitamin D receptor, a buried lipophilic pocket' },
  { pdb: '1OQ5', lig: 'CEL', note: 'carbonic anhydrase II with celecoxib (zinc site)' },
  { pdb: '2BM2', lig: 'PM2', note: 'beta-II tryptase, a serine protease' },
  { pdb: '1R58', lig: 'AO5', note: 'MetAP2 with A-357300, a dinuclear metalloenzyme' },
];

// The standard re-docking criterion. Named once because it appears in the
// success test, the near-native test and the failure classification, and
// three literals drift apart.
export const SUCCESS_A = 2.0;

const UA = { 'User-Agent': 'biodao-evals/1.0' };
const fetchText = async (url) => {
  const r = await fetch(url, { headers: UA });
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return r.text();
};

// Structures are cached on disk and committed.
//
// Two reasons, and the second is the one that matters. The first is practical:
// this benchmark spent twenty iterations marked "needs the network", and every
// run re-fetched eleven structures from the RCSB. The second is that a published
// figure measured against a file the RCSB can revise is not reproducible. The
// PDB does re-release entries; if 1OYT changes, the benchmark silently measures
// something else and the number in the whitepaper stops meaning what it said.
// Pinning the inputs is what makes a re-run a re-run.
//
// ~3 MB for the eleven cases. Refresh deliberately with --refresh-structures.
const CACHE = join(dirname(fileURLToPath(import.meta.url)), 'structures');
const REFRESH = process.argv.includes('--refresh-structures');

async function cached(name, url) {
  const file = join(CACHE, name);
  if (!REFRESH) {
    try { return await readFile(file, 'utf8'); } catch { /* fall through to fetch */ }
  }
  const body = await fetchText(url);
  await mkdir(CACHE, { recursive: true });
  await writeFile(file, body);
  return body;
}

/** Every structure the benchmark needs, so a run can be checked for completeness before it starts. */
export function cacheStatus(cases) {
  return cases.map(({ pdb, lig }) => ({
    pdb,
    lig,
    protein: existsSync(join(CACHE, `${pdb}.pdb`)),
    ligand: existsSync(join(CACHE, `${pdb}_${lig}.sdf`)),
  }));
}

export async function runCase({ pdb, lig, note }, { runs = 12, steps = 3000, seed = null } = {}) {
  const t0 = Date.now();
  const protein = parsePDB(
    await cached(`${pdb}.pdb`, `https://files.rcsb.org/download/${pdb}.pdb`), { name: pdb });
  const sdf = await cached(`${pdb}_${lig}.sdf`,
    `https://models.rcsb.org/v1/${pdb.toLowerCase()}/ligand?label_comp_id=${lig}&encoding=sdf`);
  const ligand = parseMolblock(sdf, { name: lig });

  // Every copy of this ligand must stop acting as receptor, or the pose clashes with itself.
  for (const l of protein.ligands.filter((x) => x.resName === lig)) protein.excludeAtoms(l.atoms);
  const grid = new ProteinGrid(protein, 4);

  const crystal = Float32Array.from(ligand.pos);
  const centre = centroid(crystal, ligand.n);
  const crystalScore = vinaScore(grid, ligand, crystal, { details: true });

    // A per-case seed derived from the run seed, so cases stay independent
  // while the whole benchmark remains reproducible from one number.
  const caseSeed = seed == null ? null : seed + [...pdb].reduce((a, c) => a + c.charCodeAt(0), 0);
  const poses = await dockLigand(grid, ligand, centre, { runs, steps, box: 8, seed: caseSeed });
  const rmsds = poses.map((p) => +rmsd(p.coords, crystal, ligand.n).toFixed(2));
  const top = rmsds[0] ?? null;
  const best = rmsds.length ? Math.min(...rmsds) : null;

  return {
    pdb, lig, note, atoms: ligand.n, rotatable: ligand._nrot ?? null,
    crystalScore: +crystalScore.total.toFixed(2),
    topScore: poses[0] ? +poses[0].score.toFixed(2) : null,
    topRmsd: top, bestRmsd: best,
    success: top != null && top <= SUCCESS_A,    // the standard criterion
    nearNative: best != null && best <= SUCCESS_A, // a near-native pose found anywhere in the ranking
    poses: poses.length, seconds: +((Date.now() - t0) / 1000).toFixed(1),
  };
}

/**
 * Run every case over K seeds and report the distribution rather than one draw.
 *
 * This is the answer to "make the benchmark repeat itself", and the answer is
 * that it already does: a seeded run reproduces bit for bit
 * (tests/redock-reproducibility.test.mjs). What never repeated was the
 * *reported figure*, because one seed is one sample of a wide distribution and
 * the benchmark printed it as an integer. Three runs gave 5, 6 and 4 of 11 for
 * exactly that reason.
 *
 * So the statistic changes shape. A case is no longer pass/fail; it has a pass
 * fraction over K seeds. The benchmark figure becomes a mean with a range, and
 * a case that passes 3 of 5 seeds is visible as what it is rather than being
 * rounded to whichever side the one chosen seed landed on.
 *
 * The cost is linear: K times a full run, and a full run is ~11 x 150 s. That
 * is the real reason this was never done, and it is worth saying rather than
 * pretending K=5 is free.
 */
export async function runEnsemble(cases = CASES, { seeds = [1, 2, 3, 4, 5], ...opts } = {}) {
  const perCase = new Map(cases.map((c) => [c.pdb, { ...c, draws: [] }]));

  for (const seed of seeds) {
    for (const c of cases) {
      try {
        const r = await runCase(c, { ...opts, seed });
        perCase.get(c.pdb).draws.push({ seed, topRmsd: r.topRmsd, success: r.success, nearNative: r.nearNative });
      } catch (e) {
        perCase.get(c.pdb).draws.push({ seed, error: e.message });
      }
    }
  }

  const cases_ = [...perCase.values()].map((c) => {
    const measured = c.draws.filter((d) => !d.error);
    const passes = measured.filter((d) => d.success).length;
    const rmsds = measured.map((d) => d.topRmsd).filter((v) => v != null).sort((a, b) => a - b);
    return {
      pdb: c.pdb,
      lig: c.lig,
      seedsRun: c.draws.length,
      measured: measured.length,
      passFraction: measured.length ? +(passes / measured.length).toFixed(3) : null,
      rmsdRange: rmsds.length ? [rmsds[0], rmsds[rmsds.length - 1]] : null,
      // A case that passes every seed and a case that passes none are both
      // settled; the ones in between are where the benchmark has no opinion.
      settled: measured.length ? passes === 0 || passes === measured.length : false,
    };
  });

  const perSeed = seeds.map((seed) => ({
    seed,
    succeeded: cases_.reduce((n, c) => n + (perCase.get(c.pdb).draws.find((d) => d.seed === seed)?.success ? 1 : 0), 0),
  }));
  const rates = perSeed.map((p) => p.succeeded);

  return {
    cases: cases.length,
    seeds,
    perSeed,
    succeededRange: [Math.min(...rates), Math.max(...rates)],
    meanSucceeded: +(rates.reduce((a, b) => a + b, 0) / rates.length).toFixed(2),
    alwaysPass: cases_.filter((c) => c.passFraction === 1).map((c) => c.pdb),
    neverPass: cases_.filter((c) => c.passFraction === 0).map((c) => c.pdb),
    unsettled: cases_.filter((c) => !c.settled).map((c) => c.pdb),
    perCase: cases_,
  };
}

export async function runAll(cases = CASES, opts = {}) {
  const results = [];
  for (const c of cases) {
    try { results.push(await runCase(c, opts)); }
    catch (e) { results.push({ ...c, error: e.message }); }
  }
  const ok = results.filter((r) => r.success).length;
  const scored = results.filter((r) => r.topRmsd != null);

  // Separate the two ways a re-docking case fails, because they call for
  // opposite work and a single success rate hides which one you have.
  //
  //   sampling  the search never generated a near-native pose at all; the best
  //             of everything it produced is still wrong. More runs, more
  //             steps, or a better move set.
  //   scoring   a near-native pose WAS generated and the scoring function
  //             ranked something wrong above it. More sampling cannot help;
  //             the energy terms are what is wrong.
  //
  // 1Q41 is the clearest instance: top pose 6.81 A, best pose 0.32 A. The
  // search solved it and the scorer threw the answer away.
  for (const r of results) {
    if (r.topRmsd == null) { r.failureMode = r.error ? 'error' : null; continue; }
    if (r.success) r.failureMode = null;
    else if (r.nearNative) r.failureMode = 'scoring';
    else r.failureMode = 'sampling';
  }
  const scoringFailures = results.filter((r) => r.failureMode === 'scoring');
  const samplingFailures = results.filter((r) => r.failureMode === 'sampling');

  return {
    results,
    summary: {
      cases: results.length,
      succeeded: ok,
      successRate: results.length ? +(ok / results.length).toFixed(2) : 0,
      medianRmsd: median(scored.map((r) => r.topRmsd)),
      // What the search could reach if ranking were perfect -- the ceiling the
      // scoring function is currently costing us.
      reachable: scored.filter((r) => r.nearNative).length,
      scoringFailures: scoringFailures.map((r) => `${r.pdb}: top ${r.topRmsd} A, best ${r.bestRmsd} A`),
      samplingFailures: samplingFailures.map((r) => `${r.pdb}: best ${r.bestRmsd} A`),
      failed: results.filter((r) => r.error).map((r) => `${r.pdb}: ${r.error}`),
    },
  };
}

function median(xs) {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return +(s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2).toFixed(2);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const argv = process.argv.slice(2);
  const seedAt = argv.indexOf('--seed');
  // Seeded runs exist so two scoring functions can be compared on identical
  // random draws. Unseeded, the run-to-run spread is about three cases out of
  // eleven, which hides any change smaller than that.
  const seed = seedAt >= 0 ? Number(argv[seedAt + 1]) : null;
  const arg = argv.find((a) => a.includes(':') && !a.startsWith('--'));
  const cases = arg ? [{ pdb: arg.split(':')[0], lig: arg.split(':')[1], note: 'ad hoc' }] : CASES;
  if (seed != null) console.log(`seed ${seed} — this run is reproducible\n`);

  // --seeds N reports the distribution instead of one draw. A single seeded run
  // reproduces exactly, so the thing that never repeated was not the benchmark
  // but the decision to publish one sample of it as an integer.
  const seedsAt = argv.indexOf('--seeds');
  if (seedsAt >= 0) {
    const k = Number(argv[seedsAt + 1]) || 5;
    const seeds = Array.from({ length: k }, (_, i) => (seed ?? 1) + i);
    console.log(`ensemble over ${k} seeds: ${seeds.join(', ')}`);
    console.log(`this is ${k}x a full run — roughly ${Math.round(k * cases.length * 150 / 60)} minutes\n`);
    const e = await runEnsemble(cases, { seeds });
    for (const c of e.perCase) {
      const pct = c.passFraction == null ? '  n/a' : `${String(Math.round(c.passFraction * 100)).padStart(3)}%`;
      const range = c.rmsdRange ? `${c.rmsdRange[0]}–${c.rmsdRange[1]} Å` : '—';
      console.log(`${c.pdb}/${c.lig}  passes ${pct} of seeds  top-pose RMSD ${range}`);
    }
    console.log(`\nper seed: ${e.perSeed.map((p) => `${p.seed}:${p.succeeded}`).join('  ')}`);
    console.log(`mean ${e.meanSucceeded} of ${e.cases}, range ${e.succeededRange.join('–')}`);
    console.log(`always pass: ${e.alwaysPass.join(', ') || 'none'}`);
    console.log(`never pass : ${e.neverPass.join(', ') || 'none'}`);
    console.log(`unsettled  : ${e.unsettled.join(', ') || 'none'}  <- where the benchmark has no opinion`);
  } else {
  const out = await runAll(cases, { seed });
  for (const r of out.results) {
    if (r.error) { console.log(`${r.pdb}  ERROR  ${r.error}`); continue; }
    console.log(`${r.pdb}/${r.lig}  top ${String(r.topRmsd).padStart(5)} Å  best ${String(r.bestRmsd).padStart(5)} Å  `
      + `score ${String(r.topScore).padStart(6)} (crystal ${r.crystalScore})  ${r.success ? 'PASS' : 'fail'}  ${r.seconds}s`);
  }
  const su = out.summary;
  // A run where every case errored used to print "0/11 within 2 Å", which is a benchmark-shaped number for
  // a run that measured nothing — the most misleading thing this script could emit, and easy to paste into
  // a document as a result. A rate is only reported when there is something to rate.
  const errored = out.results.filter((r) => r.error).length;
  const measured = su.cases - errored;
  if (!measured) {
    console.log(`\nNOTHING MEASURED: all ${su.cases} cases failed to run. This is not a benchmark result.`);
    if (/fetch failed|ENOTFOUND/i.test(out.results.map((r) => r.error || '').join(' '))) {
      console.log("Structures could not be fetched. node's fetch ignores HTTPS_PROXY unless you set "
        + 'NODE_USE_ENV_PROXY=1 — try `NODE_USE_ENV_PROXY=1 node evals/redock.mjs`.');
    }
    process.exitCode = 1;
  } else {
    // Write the result where the documents can be checked against it. Until today every published figure
    // was a number somebody had typed into prose a second time, which is how this repository spent ten
    // iterations citing a superseded benchmark (iteration 19). tests/claims.test.mjs reads this file, so a
    // document and the last real run cannot disagree without a test going red.
    const { writeFileSync } = await import('node:fs');
    const record = {
      generated: new Date().toISOString(),
      seed, cases: su.cases, measured, errored,
      succeeded: su.succeeded, reachable: su.reachable, medianRmsd: su.medianRmsd,
      partial: errored > 0,
      perCase: out.results.map((r) => (r.error
        ? { pdb: r.pdb, error: r.error }
        : { pdb: r.pdb, lig: r.lig, topRmsd: r.topRmsd, bestRmsd: r.bestRmsd, success: !!r.success,
            failureMode: r.failureMode || null })),
      scoringFailures: su.scoringFailures,
      samplingFailures: su.samplingFailures,
    };
    writeFileSync(new URL('./last-run.json', import.meta.url), `${JSON.stringify(record, null, 2)}\n`);
    const scope = `${measured} measured` + (errored ? ` (${errored} of ${su.cases} failed to run)` : '');
    console.log(`\n${su.succeeded}/${measured} within ${SUCCESS_A} Å, median ${su.medianRmsd} Å — ${scope}`);
    console.log(`${su.reachable}/${measured} reachable — a near-native pose was generated, ranked or not`);
    if (errored) console.log('A partial run is not comparable with a full one; re-run before quoting it.');
  }
  if (su.scoringFailures.length) {
    console.log(`\nscoring failures (${su.scoringFailures.length}) — the pose was found and mis-ranked:`);
    for (const f of su.scoringFailures) console.log(`  ${f}`);
  }
  if (su.samplingFailures.length) {
    console.log(`\nsampling failures (${su.samplingFailures.length}) — no near-native pose was generated:`);
    for (const f of su.samplingFailures) console.log(`  ${f}`);
  }
  }
}
