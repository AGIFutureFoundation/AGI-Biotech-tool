// Re-docking benchmark: take a ligand out of the crystal structure it was solved in, dock it back blind,
// and measure how far the top-scoring pose is from where the experiment put it.
//
// Under 2 Å is the usual bar for calling a re-docking successful. This runs the app's own scoring and
// search code in Node, with no browser, so the numbers come from the shipped implementation.
//
//   node evals/redock.mjs            # the default set
//   node evals/redock.mjs 2V5Z:SAG   # one case
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
const text = async (url) => { const r = await fetch(url, { headers: UA }); if (!r.ok) throw new Error(`${url} -> ${r.status}`); return r.text(); };

export async function runCase({ pdb, lig, note }, { runs = 12, steps = 3000 } = {}) {
  const t0 = Date.now();
  const protein = parsePDB(await text(`https://files.rcsb.org/download/${pdb}.pdb`), { name: pdb });
  const sdf = await text(`https://models.rcsb.org/v1/${pdb.toLowerCase()}/ligand?label_comp_id=${lig}&encoding=sdf`);
  const ligand = parseMolblock(sdf, { name: lig });

  // Every copy of this ligand must stop acting as receptor, or the pose clashes with itself.
  for (const l of protein.ligands.filter((x) => x.resName === lig)) protein.excludeAtoms(l.atoms);
  const grid = new ProteinGrid(protein, 4);

  const crystal = Float32Array.from(ligand.pos);
  const centre = centroid(crystal, ligand.n);
  const crystalScore = vinaScore(grid, ligand, crystal, { details: true });

  const poses = await dockLigand(grid, ligand, centre, { runs, steps, box: 8 });
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

export async function runAll(cases = CASES, opts) {
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
  const arg = process.argv[2];
  const cases = arg ? [{ pdb: arg.split(':')[0], lig: arg.split(':')[1], note: 'ad hoc' }] : CASES;
  const out = await runAll(cases);
  for (const r of out.results) {
    if (r.error) { console.log(`${r.pdb}  ERROR  ${r.error}`); continue; }
    console.log(`${r.pdb}/${r.lig}  top ${String(r.topRmsd).padStart(5)} Å  best ${String(r.bestRmsd).padStart(5)} Å  `
      + `score ${String(r.topScore).padStart(6)} (crystal ${r.crystalScore})  ${r.success ? 'PASS' : 'fail'}  ${r.seconds}s`);
  }
  const su = out.summary;
  console.log(`\n${su.succeeded}/${su.cases} within ${SUCCESS_A} Å, median ${su.medianRmsd} Å`);
  console.log(`${su.reachable}/${su.cases} reachable — a near-native pose was generated, ranked or not`);
  if (su.scoringFailures.length) {
    console.log(`\nscoring failures (${su.scoringFailures.length}) — the pose was found and mis-ranked:`);
    for (const f of su.scoringFailures) console.log(`  ${f}`);
  }
  if (su.samplingFailures.length) {
    console.log(`\nsampling failures (${su.samplingFailures.length}) — no near-native pose was generated:`);
    for (const f of su.samplingFailures) console.log(`  ${f}`);
  }
}
