// Cheminformatics: RDKit.js (WASM) for parsing, descriptors, fingerprints, depiction, substructure search;
// 3D coordinates from the server's RDKit ETKDG+MMFF when available, otherwise a fast in-browser embedder.
import { parseMolblock, Structure } from './structure.js';
import { buildLigandFF, ligandForces, minimize, setFourteenRef } from './md.js';

const RDKIT_VER = '2025.3.4-1.0.0';
const RDKIT_BASE = `https://cdn.jsdelivr.net/npm/@rdkit/rdkit@${RDKIT_VER}/dist/`;
let rdkitPromise = null;

export function loadRDKit() {
  if (rdkitPromise) return rdkitPromise;
  rdkitPromise = new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = RDKIT_BASE + 'RDKit_minimal.js';
    s.onload = () => window.initRDKitModule({ locateFile: (f) => RDKIT_BASE + f }).then((RD) => { window.RDKit = RD; resolve(RD); }, reject);
    s.onerror = () => reject(new Error('Could not load RDKit.js from the CDN'));
    document.head.appendChild(s);
  });
  return rdkitPromise;
}

function withMol(RD, smiles, fn) {
  const m = RD.get_mol(smiles || '');
  if (!m || !m.is_valid()) { m && m.delete(); return null; }
  try { return fn(m); } finally { m.delete(); }
}

export async function canonical(smiles) {
  const RD = await loadRDKit();
  return withMol(RD, smiles, (m) => m.get_smiles());
}

// Wager et al. 2010 CNS MPO, 5 of 6 components (pKa unavailable in-browser; logD approximated by cLogP).
function cnsMpo(d) {
  const lin = (x, good, bad) => (good < bad ? (x <= good ? 1 : x >= bad ? 0 : 1 - (x - good) / (bad - good)) : 0);
  const tpsa = d.tpsa < 20 ? 0 : d.tpsa < 40 ? (d.tpsa - 20) / 20 : d.tpsa <= 90 ? 1 : d.tpsa >= 120 ? 0 : 1 - (d.tpsa - 90) / 30;
  return lin(d.clogp, 3, 5) + lin(d.clogp, 2, 4) + lin(d.mw, 360, 500) + tpsa + lin(d.hbd, 0.5, 3.5);
}

export async function analyze(smiles) {
  const RD = await loadRDKit();
  return withMol(RD, smiles, (m) => {
    const d = JSON.parse(m.get_descriptors());
    const desc = { mw: d.amw, exactMass: d.exactmw, clogp: d.CrippenClogP, tpsa: d.tpsa, hbd: d.NumHBD, hba: d.NumHBA,
      rotb: d.NumRotatableBonds, heavy: d.NumHeavyAtoms, rings: d.NumRings, aromRings: d.NumAromaticRings, fsp3: d.FractionCSP3,
      stereo: d.NumAtomStereoCenters, heteroatoms: d.NumHeteroatoms };
    const lip = [desc.mw > 500, desc.clogp > 5, d.lipinskiHBD > 5, d.lipinskiHBA > 10].filter(Boolean).length;
    const veber = desc.rotb <= 10 && desc.tpsa <= 140;
    const mpo = cnsMpo(desc);
    const bbb = desc.tpsa < 90 && desc.mw < 450 && desc.hbd <= 3 && desc.clogp > 0.5 && desc.clogp < 5;
    let inchikey = '';
    try { const inchi = m.get_inchi(); inchikey = RD.get_inchikey_for_inchi(inchi); } catch { /* optional */ }
    return {
      canonical: m.get_smiles(), inchikey, desc,
      rules: { lipinskiViolations: lip, veber, cnsMpo5: +mpo.toFixed(2), bbbLikely: bbb },
      svg: m.get_svg(260, 190),
      fp: m.get_morgan_fp_as_uint8array(JSON.stringify({ radius: 2, nBits: 2048 })),
    };
  });
}

export function tanimoto(a, b) {
  if (!a || !b) return 0;
  let inter = 0, uni = 0;
  for (let i = 0; i < a.length; i++) { inter += popcnt(a[i] & b[i]); uni += popcnt(a[i] | b[i]); }
  return uni ? inter / uni : 0;
}
function popcnt(x) { x -= (x >> 1) & 0x55; x = (x & 0x33) + ((x >> 2) & 0x33); return (x + (x >> 4)) & 0x0f; }

export async function fingerprint(smiles) {
  const RD = await loadRDKit();
  return withMol(RD, smiles, (m) => m.get_morgan_fp_as_uint8array(JSON.stringify({ radius: 2, nBits: 2048 })));
}

// Substructure filter: query may be SMARTS or SMILES.
export async function substructFilter(query, smilesList) {
  const RD = await loadRDKit();
  const q = RD.get_qmol(query);
  if (!q || !q.is_valid()) throw new Error('Invalid SMARTS/SMILES query');
  try {
    return smilesList.map((s) => withMol(RD, s, (m) => JSON.parse(m.get_substruct_match(q) || '{}').atoms !== undefined) || false);
  } finally { q.delete(); }
}

export async function depict(smiles, w = 260, h = 190) {
  const RD = await loadRDKit();
  return withMol(RD, smiles, (m) => m.get_svg(w, h));
}

// Aromaticity / ring info (atom indices follow the SMILES atom order, which RDKit keeps for heavy atoms).
async function chemInfo(smiles) {
  const RD = await loadRDKit();
  return withMol(RD, smiles, (m) => {
    const j = JSON.parse(m.get_json()).molecules[0];
    const ext = (j.extensions || []).find((e) => e.name === 'rdkitRepresentation') || {};
    const bonds = j.bonds.map((b) => b.atoms);
    return {
      aromaticAtoms: ext.aromaticAtoms || [], rings: ext.atomRings || [],
      aromaticBondPairs: (ext.aromaticBonds || []).map((k) => bonds[k]),
      hcount: j.atoms.map((a) => a.impHs || 0),
    };
  });
}

let serverHasRDKit = null;
export function setServerCaps(caps) { serverHasRDKit = !!(caps && caps.rdkit); }

// Heavy-atom-only small molecule with implicit H counts (used by docking typing + MD).
function stripHydrogens(st, name, chem) {
  const keep = []; const hcount = [];
  for (let i = 0; i < st.n; i++) if (st.element[i] !== 'H') keep.push(i);
  for (const i of keep) hcount.push(st.nbr[i].filter((j) => st.element[j] === 'H').length);
  const sub = st.subset(keep, { name });
  return new Structure(keep.map((i, k) => ({ x: sub.pos[k * 3], y: sub.pos[k * 3 + 1], z: sub.pos[k * 3 + 2], element: sub.element[k],
    name: sub.atomName[k], resName: 'LIG', chain: 'L', resSeq: 1, het: 1, charge: st.charge[i] })),
  { bonds: sub.bonds, kind: 'small', name, hcount: chem?.hcount || hcount, chem });
}

// SMILES -> 3D heavy-atom Structure.
export async function smilesTo3D(smiles, { name = 'ligand', preferServer = true } = {}) {
  const RD = await loadRDKit();
  const chem = await chemInfo(smiles);
  if (!chem) throw new Error('Invalid SMILES');
  if (preferServer && serverHasRDKit) {
    try {
      const r = await fetch('/api/embed', { method: 'POST', body: JSON.stringify({ smiles }) });
      if (r.ok) {
        const j = await r.json();
        const st = parseMolblock(j.conformers[0].molblock, { name });
        const out = stripHydrogens(st, name, chem);
        out.embedMethod = `RDKit ETKDGv3 + ${j.forcefield} (server)`;
        return out;
      }
    } catch { /* fall back to browser embedding */ }
  }
  // Browser: 2D depiction coordinates -> relaxed 3D with the ligand force field.
  const mb = withMol(RD, smiles, (m) => { m.set_new_coords(); return m.get_molblock(); });
  const flat = parseMolblock(mb, { name });
  const st = new Structure(Array.from({ length: flat.n }, (_, i) => ({ x: flat.pos[i * 3], y: flat.pos[i * 3 + 1], z: flat.pos[i * 3 + 2],
    element: flat.element[i], name: flat.atomName[i], resName: 'LIG', chain: 'L', resSeq: 1, het: 1, charge: flat.charge[i] })),
  { bonds: flat.bonds, kind: 'small', name, hcount: chem.hcount, chem });
  const ff = buildLigandFF(st, chem);
  // Scale 2D (RDKit uses 1.5 Å bonds) to ~1.4 Å and keep cis/trans references from the flat drawing.
  for (let i = 0; i < st.pos.length; i++) st.pos[i] *= 0.95;
  setFourteenRef(ff, st.pos);
  let seed = 7;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647 - 0.5; };
  for (let i = 0; i < st.n; i++) st.pos[i * 3 + 2] = rnd() * 0.8;
  minimize(st.pos, (P, F) => ligandForces(ff, P, F), { steps: 1500 });
  st.embedMethod = 'in-browser distance-geometry relaxation (stereocentres not enforced)';
  return st;
}

// Remove H from any small-molecule structure (e.g. PubChem 3D SDF) for a consistent heavy-atom model.
export function heavyAtomModel(st, name) { return st.element.includes('H') ? stripHydrogens(st, name || st.name, null) : st; }
