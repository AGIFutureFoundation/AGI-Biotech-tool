// Reference side of the port-equivalence check: score a ligand molblock against
// a receptor PDB using the repo's own js/dock.js and print every term as JSON.
// Nothing here re-implements anything -- it only calls the JavaScript that the
// Python port in server/vina_score.py was ported from.
//
//   node tests/fixtures/score_with_dock_js.mjs <receptor.pdb> <ligand.mol>
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const js = path.resolve(here, '..', '..', 'js');
const { parsePDB, parseMolblock } = await import(path.join(js, 'structure.js'));
const { ProteinGrid, vinaScore, rotatableBonds } = await import(path.join(js, 'dock.js'));

const [pdbPath, molPath] = process.argv.slice(2);
const rec = parsePDB(fs.readFileSync(pdbPath, 'utf8'));
const lig = parseMolblock(fs.readFileSync(molPath, 'utf8'));
const grid = new ProteinGrid(rec);
const out = vinaScore(grid, lig, lig.pos, { details: true });

out.nrotBonds = rotatableBonds(lig).length;
out.ligHeavy = lig.heavy.length;
out.recAtoms = grid.atoms.length;
// Atom typing drives every term, so compare the typing counts too: two
// implementations can agree on a total while disagreeing about the chemistry.
out.ligTypes = {
  hydrophobic: [...lig.heavy].filter((i) => lig.hydrophobic[i]).length,
  donor: [...lig.heavy].filter((i) => lig.donor[i]).length,
  acceptor: [...lig.heavy].filter((i) => lig.acceptor[i]).length,
};
out.recTypes = {
  hydrophobic: grid.atoms.filter((i) => rec.hydrophobic[i]).length,
  donor: grid.atoms.filter((i) => rec.donor[i]).length,
  acceptor: grid.atoms.filter((i) => rec.acceptor[i]).length,
};
console.log(JSON.stringify(out));
