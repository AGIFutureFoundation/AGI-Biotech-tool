// Why does the scorer prefer a 6.8 Å pose to a 0.54 Å one, every single time?
//
// 1Q41 (GSK-3β, ligand IXM) is the only case in the benchmark where that
// question can currently be asked and answered. Across ten seeds its top pose
// moved 0.01 Å while failing by 6.8 Å: the search reliably generates a
// near-native pose and the scoring function reliably ranks something wrong
// above it. Nine of the other ten cases move further than the 2 Å threshold
// that decides pass from fail, so on those a change and a lucky seed are
// indistinguishable. Here they are not.
//
// That makes this the one place a scoring change can be evaluated today, and
// this script is the measurement it would be evaluated against: it scores the
// crystal pose and the pose the search actually ranks first, term by term, and
// prints the difference. The term with the largest gap in the wrong direction
// is the one preferring the decoy.
//
//   node evals/why-1q41-fails.mjs            # 1Q41, the reproducible case
//   node evals/why-1q41-fails.mjs 1R58:AO5   # the other consistent failure
//
// Needs no network: the structures are committed. One docking run, so a couple
// of minutes rather than the hours a benchmark takes.
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { parsePDB, parseMolblock } from '../js/structure.js';
import { ProteinGrid, vinaScore, dockLigand, rmsd, centroid } from '../js/dock.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const CACHE = join(HERE, 'structures');

const arg = process.argv.find((a) => a.includes(':') && !a.startsWith('--')) || '1Q41:IXM';
const [PDB, LIG] = arg.split(':');
// indexOf returns -1 when the flag is absent, and argv[-1 + 1] is argv[0] --
// the node binary path, which Number()s to NaN. The first version of this
// script seeded the search with NaN and printed "seed NaN", which would have
// made its own result unreproducible while looking fine.
const seedAt = process.argv.indexOf('--seed');
const SEED = seedAt >= 0 ? Number(process.argv[seedAt + 1]) : 1;
if (!Number.isFinite(SEED)) throw new Error(`--seed must be a number, got ${process.argv[seedAt + 1]}`);
const kAt = process.argv.indexOf('--seeds');
const K = kAt >= 0 ? Number(process.argv[kAt + 1]) : 3;
if (!Number.isFinite(K) || K < 1) throw new Error(`--seeds must be a positive number`);

const protein = parsePDB(await readFile(join(CACHE, `${PDB}.pdb`), 'utf8'), { name: PDB });
const ligand = parseMolblock(await readFile(join(CACHE, `${PDB}_${LIG}.sdf`), 'utf8'), { name: LIG });
for (const l of protein.ligands.filter((x) => x.resName === LIG)) protein.excludeAtoms(l.atoms);

const grid = new ProteinGrid(protein, 4);
const crystal = Float32Array.from(ligand.pos);
const centre = centroid(crystal, ligand.n);
const score = (coords) => vinaScore(grid, ligand, coords, { details: true });
const f = (x) => (x >= 0 ? ' ' : '') + x.toFixed(3);
const A = (x) => x.toFixed(2);

// Across seeds, not one. A first version reported "the largest single
// contribution" from a single run and named a different term each time it was
// run -- repulsion, then hydrophobic, then repulsion. That is the same
// single-draw error this benchmark has been publishing all along, reproduced
// inside the tool built to diagnose it. One run cannot say which term is
// responsible; what it can say is what every run agrees on.
const SEEDS = Array.from({ length: K }, (_, i) => SEED + i);
const runs = [];

for (const seed of SEEDS) {
  const caseSeed = seed + [...PDB].reduce((a, c) => a + c.charCodeAt(0), 0);
  const poses = await dockLigand(grid, ligand, centre, { runs: 12, steps: 3000, box: 8, seed: caseSeed });
  const top = poses[0];
  const nearest = poses.reduce((b, p) =>
    rmsd(p.coords, crystal, ligand.n) < rmsd(b.coords, crystal, ligand.n) ? p : b, poses[0]);
  runs.push({
    seed,
    topRmsd: rmsd(top.coords, crystal, ligand.n),
    nearRmsd: rmsd(nearest.coords, crystal, ligand.n),
    T: score(top.coords), N: score(nearest.coords),
  });
  process.stdout.write(`  seed ${seed} done\r`);
}

const C = score(crystal);
const nb = (r) => (Array.isArray(r.hbonds) ? r.hbonds.length : r.hbonds);
const usable = runs.filter((r) => r.nearRmsd <= 2.0);

console.log(`${PDB}/${LIG}  ${SEEDS.length} seeds (${SEEDS[0]}–${SEEDS[SEEDS.length - 1]})\n`);
console.log(`crystal pose             score ${f(C.total)}   ${nb(C)} h-bonds`);
for (const r of runs) {
  console.log(`seed ${String(r.seed).padStart(3)}  ranked ${f(r.T.total)} @ ${A(r.topRmsd)} Å`
    + `   best generated ${f(r.N.total)} @ ${A(r.nearRmsd)} Å`);
}

if (!usable.length) {
  console.log(`\nNo seed generated a near-native pose: this is a SAMPLING failure.`);
  console.log(`Rescoring cannot fix it — there is nothing better in the set to promote.`);
  process.exit(0);
}

// The scoring function's optimum is not the experimental structure, which is a
// stronger statement than "it ranked the wrong pose" and worth checking first.
const betterThanCrystal = runs.filter((r) => r.T.total < C.total).length;
if (betterThanCrystal === runs.length) {
  console.log(`\nEvery seed's chosen pose scores BETTER than the crystal structure`
    + ` (${f(C.total)}).\nThe function's optimum is not the experimental pose, so this is not a`
    + `\nnear-miss in ranking — it prefers the decoy on its own terms.`);
}

const terms = Object.keys(runs[0].T.terms);
const deltas = Object.fromEntries(terms.map((k) =>
  [k, usable.map((r) => r.T.terms[k] - r.N.terms[k])]));

console.log(`\nRanked pose minus near-native, per term, over ${usable.length} usable seeds.`);
console.log(`Negative favours the wrongly-ranked pose.\n`);
console.log(`  ${'term'.padEnd(12)} ${'mean'.padStart(8)} ${'min'.padStart(8)} ${'max'.padStart(8)}  verdict`);

const rows = terms.map((k) => {
  const v = deltas[k];
  const mean = v.reduce((a, b) => a + b, 0) / v.length;
  return { k, mean, min: Math.min(...v), max: Math.max(...v) };
}).sort((a, b) => a.mean - b.mean);

for (const r of rows) {
  const consistent = r.max < 0 ? 'always favours the decoy'
    : r.min > 0 ? 'always favours near-native'
    : 'flips sign across seeds — not attributable';
  console.log(`  ${r.k.padEnd(12)} ${f(r.mean).padStart(8)} ${f(r.min).padStart(8)} ${f(r.max).padStart(8)}  ${consistent}`);
}

const blamed = rows.filter((r) => r.max < 0);
const gaps = usable.map((r) => r.N.total - r.T.total);
console.log(`\ngap to close: ${f(Math.min(...gaps))} to ${f(Math.max(...gaps))}`);
if (blamed.length) {
  console.log(`consistently responsible: ${blamed.map((r) => r.k).join(', ')}`);
  console.log(`A change to ${blamed.length === 1 ? 'that term' : 'those terms'} can be evaluated here,`
    + ` because this case's\nfailure reproduces where the rest of the benchmark's does not.`);
} else {
  console.log(`No term favours the decoy in every seed: the preference is not attributable`);
  console.log(`to one term at this sample size. Raise --seeds before concluding.`);
}
