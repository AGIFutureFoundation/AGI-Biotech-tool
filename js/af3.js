// AlphaFold 3 interoperability.
//
// AlphaFold 3 has no public API: the AlphaFold Server (alphafoldserver.com) is a web app, and the AF3
// model weights are released by Google DeepMind for non-commercial use on request. So this module does the
// two things that can be automated: it writes job files in both AF3 input dialects, and it reads AF3
// output back in (mmCIF + confidence JSON) so predicted complexes land in the same workspace as everything else.
import { parseMmCIF } from './structure.js';
import { rmsd } from './dock.js';

// Local AlphaFold 3 input (run_alphafold.py --json_path=...). Arbitrary ligand SMILES are supported here.
export function af3LocalJob({ name, chains, ligands = [], seeds = [1] }) {
  const sequences = [];
  chains.forEach((c) => sequences.push({ protein: { id: c.id, sequence: c.sequence.replace(/[^A-Z]/g, '') } }));
  ligands.forEach((l) => sequences.push({ ligand: l.ccd ? { id: l.id, ccdCodes: [l.ccd] } : { id: l.id, smiles: l.smiles } }));
  return { name: name.replace(/[^\w\-.]+/g, '_').toLowerCase(), modelSeeds: seeds, sequences, dialect: 'alphafold3', version: 1 };
}

// AlphaFold Server job (alphafoldserver.com "Upload JSON"). The server only accepts ligands from its own
// fixed CCD list, so a custom SMILES cannot be included — the protein job is exported and the caller warned.
export function afServerJob({ name, chains, ligands = [], seeds = [] }) {
  const sequences = chains.map((c) => ({ proteinChain: { sequence: c.sequence.replace(/[^A-Z]/g, ''), count: 1 } }));
  const dropped = [];
  for (const l of ligands) {
    if (l.ccd) sequences.push({ ligand: { ligand: l.ccd.startsWith('CCD_') ? l.ccd : `CCD_${l.ccd}`, count: 1 } });
    else dropped.push(l);
  }
  return { job: [{ name: name.slice(0, 60), modelSeeds: seeds, sequences }], dropped };
}

export function downloadJson(obj, filename) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

export function downloadText(text, filename, type = 'text/plain') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type })); a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}

// Read an AF3 (or Boltz / Chai) mmCIF prediction. B-factor column carries pLDDT.
export function readPrediction(cifText, name = 'AF3 prediction') {
  const st = parseMmCIF(cifText, { name, source: 'AlphaFold 3 output' });
  let sum = 0, n = 0;
  for (const r of st.residues) if (r.ca >= 0) { sum += st.bfac[r.ca]; n++; }
  st.meanPlddt = n ? sum / n : null;
  return st;
}

export function readConfidences(json) {
  const j = typeof json === 'string' ? JSON.parse(json) : json;
  return { ptm: j.ptm, iptm: j.iptm, ranking: j.ranking_score, chainPairIptm: j.chain_pair_iptm, hasPae: !!j.pae };
}

// Compare a predicted ligand pose with a docked pose (same atom order assumed after matching by element).
export function poseAgreement(docked, predicted) {
  if (!docked || !predicted || docked.n !== predicted.n) return null;
  return { rmsd: rmsd(docked.pos, predicted.pos, docked.n) };
}
