import { parsePDB, parseMolblock } from '../../js/structure.js';
import { ProteinGrid, dockLigand, rmsd, centroid } from '../../js/dock.js';
const UA = { 'User-Agent': 'seedtest/1.0' };
const text = async (u) => (await fetch(u, { headers: UA })).text();
const protein = parsePDB(await text('https://files.rcsb.org/download/1Q41.pdb'), { name: '1Q41' });
const sdf = await text('https://models.rcsb.org/v1/1q41/ligand?label_comp_id=IXM&encoding=sdf');
const lig = parseMolblock(sdf, { name: 'IXM' });
for (const l of protein.ligands.filter((x) => x.resName === 'IXM')) protein.excludeAtoms(l.atoms);
const grid = new ProteinGrid(protein, 4);
const centre = centroid(Float32Array.from(lig.pos), lig.n);
const run = async (seed) => {
  const poses = await dockLigand(grid, lig, centre, { runs: 4, steps: 800, box: 8, seed });
  return poses.map((p) => p.score.toFixed(4)).join(',');
};
const a = await run(42), b = await run(42), c = await run(43), d = await run(null), e = await run(null);
console.log('seed 42 twice  :', a === b ? 'IDENTICAL' : 'DIFFER');
console.log('seed 42 vs 43  :', a === c ? 'identical (bad)' : 'differ (good)');
console.log('unseeded twice :', d === e ? 'identical (bad)' : 'differ (good)');
console.log('scores(42)     :', a.slice(0, 60));
