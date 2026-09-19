// Molecular structure model + parsers (PDB, mmCIF incl. AlphaFold 3 output, MDL molfile/SDF).
import { covRadius, WATER, IONS, AA3 } from './elements.js';

const NUC = new Set(['A', 'C', 'G', 'U', 'T', 'DA', 'DC', 'DG', 'DT', 'DU', 'I', 'DI']);

export class Structure {
  constructor(atoms, opts = {}) {
    const n = atoms.length;
    this.name = opts.name || 'structure';
    this.source = opts.source || '';
    this.kind = opts.kind || 'macromolecule'; // 'macromolecule' | 'small'
    this.n = n;
    this.pos = new Float32Array(n * 3);
    this.element = new Array(n); this.atomName = new Array(n); this.resName = new Array(n);
    this.chain = new Array(n); this.resSeq = new Int32Array(n); this.bfac = new Float32Array(n);
    this.het = new Uint8Array(n); this.charge = new Int8Array(n);
    atoms.forEach((a, i) => {
      this.pos[i * 3] = a.x; this.pos[i * 3 + 1] = a.y; this.pos[i * 3 + 2] = a.z;
      this.element[i] = a.element; this.atomName[i] = a.name || a.element; this.resName[i] = a.resName || 'LIG';
      this.chain[i] = a.chain || 'A'; this.resSeq[i] = a.resSeq || 1; this.bfac[i] = a.b || 0;
      this.het[i] = a.het ? 1 : 0; this.charge[i] = a.charge || 0;
    });
    this.helices = opts.helices || []; this.sheets = opts.sheets || [];
    this.bonds = opts.bonds || null; // flat [i,j,order,...]
    this.hcount = opts.hcount || null; // implicit H per atom (heavy-atom models from SMILES)
    this.chem = opts.chem || null; // RDKit-derived info: aromatic atoms/bonds, rings
    if (!this.bonds) this.bonds = perceiveBonds(this, opts.conect);
    this.buildResidues();
    this.buildNeighbors();
    this.assignSecondary();
    this.typeAtoms();
  }

  get isSmall() { return this.kind === 'small'; }

  // Mark atoms that should not act as receptor (e.g. a ligand lifted out for re-docking).
  excludeAtoms(indices) {
    this.excluded = this.excluded || new Uint8Array(this.n);
    for (const i of indices) this.excluded[i] = 1;
  }
  includeAll() { this.excluded = null; }

  buildResidues() {
    this.residues = [];
    let cur = null;
    for (let i = 0; i < this.n; i++) {
      const key = this.chain[i] + ':' + this.resSeq[i] + ':' + this.resName[i];
      if (!cur || cur.key !== key) {
        const rn = this.resName[i];
        cur = { key, chain: this.chain[i], resSeq: this.resSeq[i], resName: rn, start: i, end: i, ca: -1,
          polymer: !!AA3[rn] || NUC.has(rn), water: WATER.has(rn), ion: IONS.has(rn), idx: this.residues.length };
        this.residues.push(cur);
      }
      cur.end = i;
      const an = this.atomName[i];
      if (an === 'CA' && cur.polymer && AA3[cur.resName]) cur.ca = i;
      if (an === "C4'" && NUC.has(cur.resName) && cur.ca < 0) cur.ca = i;
    }
    this.atomRes = new Int32Array(this.n);
    for (const r of this.residues) for (let i = r.start; i <= r.end; i++) this.atomRes[i] = r.idx;
    // Ligands: non-polymer, non-water, non-ion residue groups.
    this.ligands = this.residues.filter((r) => !r.polymer && !r.water && !r.ion && (r.end - r.start) >= 4)
      .map((r) => ({ resName: r.resName, chain: r.chain, resSeq: r.resSeq, atoms: range(r.start, r.end) }));
    this.chains = [...new Set(this.chain)];
  }

  buildNeighbors() {
    this.nbr = Array.from({ length: this.n }, () => []);
    this.bondOrderMap = new Map();
    for (let k = 0; k < this.bonds.length; k += 3) {
      const i = this.bonds[k], j = this.bonds[k + 1];
      this.nbr[i].push(j); this.nbr[j].push(i);
      this.bondOrderMap.set(i < j ? i * 1e6 + j : j * 1e6 + i, this.bonds[k + 2]);
    }
  }

  bondOrder(i, j) { return this.bondOrderMap.get(i < j ? i * 1e6 + j : j * 1e6 + i) || 1; }

  // Secondary structure: use HELIX/SHEET records when present, otherwise a CA-geometry estimate.
  assignSecondary() {
    this.ss = new Uint8Array(this.residues.length); // 0 coil, 1 helix, 2 strand
    const byKey = new Map(this.residues.map((r) => [r.chain + ':' + r.resSeq, r.idx]));
    const mark = (list, v) => list.forEach((h) => {
      for (let s = h.start; s <= h.end; s++) { const idx = byKey.get(h.chain + ':' + s); if (idx !== undefined) this.ss[idx] = v; }
    });
    if (this.helices.length || this.sheets.length) { mark(this.helices, 1); mark(this.sheets, 2); return; }
    const R = this.residues, P = this.pos;
    const d = (a, b) => Math.hypot(P[a * 3] - P[b * 3], P[a * 3 + 1] - P[b * 3 + 1], P[a * 3 + 2] - P[b * 3 + 2]);
    for (let i = 0; i < R.length; i++) {
      const r = R[i]; if (r.ca < 0) continue;
      const same = (k) => R[k] && R[k].ca >= 0 && R[k].chain === r.chain;
      if (same(i + 3) && same(i + 4)) {
        const d3 = d(r.ca, R[i + 3].ca), d4 = d(r.ca, R[i + 4].ca);
        if (d3 > 4.5 && d3 < 5.7 && d4 > 5.6 && d4 < 6.9) for (let k = i; k <= i + 4; k++) this.ss[k] = 1;
      }
    }
    for (let i = 1; i < R.length - 1; i++) {
      if (this.ss[i] || R[i].ca < 0 || !R[i - 1] || !R[i + 1] || R[i - 1].ca < 0 || R[i + 1].ca < 0) continue;
      if (R[i - 1].chain !== R[i].chain || R[i + 1].chain !== R[i].chain) continue;
      if (d(R[i - 1].ca, R[i + 1].ca) > 6.4) this.ss[i] = 2;
    }
    // Remove isolated strand residues (need >=3 in a row to count).
    for (let i = 0; i < R.length; i++) if (this.ss[i] === 2 && this.ss[i - 1] !== 2 && this.ss[i + 1] !== 2) this.ss[i] = 0;
  }

  // Vina-style atom typing: hydrophobic carbon/halogen, H-bond donor, H-bond acceptor.
  typeAtoms() {
    const n = this.n;
    this.hydrophobic = new Uint8Array(n); this.donor = new Uint8Array(n); this.acceptor = new Uint8Array(n);
    this.heavy = [];
    for (let i = 0; i < n; i++) {
      const e = this.element[i];
      if (e === 'H') continue;
      this.heavy.push(i);
      const nb = this.nbr[i];
      if (e === 'C') this.hydrophobic[i] = nb.every((j) => this.element[j] !== 'N' && this.element[j] !== 'O') ? 1 : 0;
      else if (e === 'F' || e === 'CL' || e === 'BR' || e === 'I' || e === 'Cl' || e === 'Br') this.hydrophobic[i] = 1;
      else if (e === 'N' || e === 'O') {
        const hasH = nb.some((j) => this.element[j] === 'H') || !!(this.hcount && this.hcount[i] > 0);
        const heavyDeg = nb.filter((j) => this.element[j] !== 'H').length;
        const anyH = this.element.includes('H') || !!this.hcount;
        if (e === 'O') {
          this.acceptor[i] = 1;
          this.donor[i] = hasH || (!anyH && heavyDeg === 1 && this.bondOrder(i, nb[0]) === 1 && !this.isCarboxylO(i)) ? 1 : 0;
        } else {
          const aromaticLike = nb.some((j) => this.bondOrder(i, j) >= 2);
          this.donor[i] = hasH || (!anyH && heavyDeg <= 2 && !(aromaticLike && heavyDeg === 2)) ? 1 : 0;
          this.acceptor[i] = (heavyDeg < 3 && !hasH) || (!anyH && aromaticLike) ? 1 : 0;
        }
      }
    }
    if (!this.isSmall) this.typeProtein();
    this.heavy = Int32Array.from(this.heavy);
  }

  isCarboxylO(i) {
    const c = this.nbr[i][0];
    return c !== undefined && this.element[c] === 'C' && this.nbr[c].some((j) => j !== i && this.element[j] === 'O' && this.bondOrder(c, j) === 2);
  }

  typeProtein() {
    const D = { N: 1, OG: 1, OG1: 1, OH: 1, ND2: 1, NE2: 1, ND1: 1, NZ: 1, NE: 1, NH1: 1, NH2: 1, NE1: 1, O: 0 };
    const A = { O: 1, OXT: 1, OG: 1, OG1: 1, OH: 1, OD1: 1, OD2: 1, OE1: 1, OE2: 1, ND1: 1, NE2: 1 };
    for (let i = 0; i < this.n; i++) {
      if (this.het[i]) continue;
      const an = this.atomName[i], rn = this.resName[i];
      if (this.element[i] === 'N' || this.element[i] === 'O') {
        this.donor[i] = D[an] ? 1 : 0;
        this.acceptor[i] = A[an] ? 1 : 0;
        if (rn === 'GLN' && an === 'NE2') this.acceptor[i] = 0;
        if (an === 'N' && rn === 'PRO') this.donor[i] = 0;
      }
    }
  }

  center(atoms) {
    const idx = atoms || null; let x = 0, y = 0, z = 0, c = 0;
    const it = idx || range(0, this.n - 1);
    for (const i of it) { x += this.pos[i * 3]; y += this.pos[i * 3 + 1]; z += this.pos[i * 3 + 2]; c++; }
    return c ? [x / c, y / c, z / c] : [0, 0, 0];
  }

  radius(atoms) {
    const [cx, cy, cz] = this.center(atoms); let r = 0;
    for (const i of atoms || range(0, this.n - 1)) r = Math.max(r, Math.hypot(this.pos[i * 3] - cx, this.pos[i * 3 + 1] - cy, this.pos[i * 3 + 2] - cz));
    return r;
  }

  sequence(chainId) {
    return this.residues.filter((r) => r.chain === (chainId || this.chains[0]) && AA3[r.resName]).map((r) => AA3[r.resName]).join('');
  }

  // Extract a subset (e.g. a co-crystallised ligand) as its own small-molecule Structure.
  subset(indices, opts = {}) {
    const map = new Map(indices.map((i, k) => [i, k]));
    const atoms = indices.map((i) => ({ x: this.pos[i * 3], y: this.pos[i * 3 + 1], z: this.pos[i * 3 + 2], element: this.element[i],
      name: this.atomName[i], resName: this.resName[i], chain: this.chain[i], resSeq: this.resSeq[i], b: this.bfac[i], het: 1 }));
    const bonds = [];
    for (let k = 0; k < this.bonds.length; k += 3) {
      const a = map.get(this.bonds[k]), b = map.get(this.bonds[k + 1]);
      if (a !== undefined && b !== undefined) bonds.push(a, b, this.bonds[k + 2]);
    }
    return new Structure(atoms, { bonds, kind: 'small', name: opts.name || this.resName[indices[0]], source: this.name });
  }

  toPDB() {
    const L = [];
    for (let i = 0; i < this.n; i++) {
      const rec = this.het[i] ? 'HETATM' : 'ATOM  ';
      const nm = this.atomName[i].length < 4 ? ' ' + this.atomName[i].padEnd(3) : this.atomName[i].slice(0, 4);
      L.push(`${rec}${String(i + 1).padStart(5)} ${nm} ${this.resName[i].padStart(3).slice(-3)} ${(this.chain[i] || 'A')[0]}${String(this.resSeq[i]).padStart(4)}    ` +
        `${this.pos[i * 3].toFixed(3).padStart(8)}${this.pos[i * 3 + 1].toFixed(3).padStart(8)}${this.pos[i * 3 + 2].toFixed(3).padStart(8)}  1.00${this.bfac[i].toFixed(2).padStart(6)}          ${this.element[i].padStart(2)}`);
    }
    L.push('END');
    return L.join('\n');
  }

  toMolblock() {
    const L = [this.name, '  biodao.chain', ''];
    L.push(`${String(this.n).padStart(3)}${String(this.bonds.length / 3).padStart(3)}  0  0  0  0  0  0  0  0999 V2000`);
    for (let i = 0; i < this.n; i++) {
      const e = this.element[i]; const sym = e.length > 1 ? e[0] + e.slice(1).toLowerCase() : e;
      L.push(`${this.pos[i * 3].toFixed(4).padStart(10)}${this.pos[i * 3 + 1].toFixed(4).padStart(10)}${this.pos[i * 3 + 2].toFixed(4).padStart(10)} ${sym.padEnd(3)} 0  0  0  0  0  0  0  0  0  0  0  0`);
    }
    for (let k = 0; k < this.bonds.length; k += 3) L.push(`${String(this.bonds[k] + 1).padStart(3)}${String(this.bonds[k + 1] + 1).padStart(3)}${String(this.bonds[k + 2]).padStart(3)}  0`);
    L.push('M  END');
    return L.join('\n');
  }
}

export function range(a, b) { const r = []; for (let i = a; i <= b; i++) r.push(i); return r; }

function normEl(e, name) {
  let s = (e || '').trim();
  if (!s) { s = (name || '').replace(/[^A-Za-z]/g, ''); s = /^(CL|BR|FE|ZN|MG|NA|MN|CU|CA|SE)$/i.test(s.slice(0, 2)) && name.trim().length <= 2 ? s.slice(0, 2) : s.slice(0, 1); }
  return s.toUpperCase();
}

// Distance-based bonding with a uniform grid (O(n)).
export function perceiveBonds(st, conect) {
  const n = st.n, P = st.pos, cell = 3.0, grid = new Map(), bonds = [];
  const key = (x, y, z) => `${x},${y},${z}`;
  for (let i = 0; i < n; i++) {
    const k = key(Math.floor(P[i * 3] / cell), Math.floor(P[i * 3 + 1] / cell), Math.floor(P[i * 3 + 2] / cell));
    (grid.get(k) || grid.set(k, []).get(k)).push(i);
  }
  const seen = new Set();
  if (conect) for (const [a, b] of conect) {
    const k = a < b ? a * 1e6 + b : b * 1e6 + a; if (seen.has(k)) continue; seen.add(k); bonds.push(a, b, 1);
  }
  for (let i = 0; i < n; i++) {
    const cx = Math.floor(P[i * 3] / cell), cy = Math.floor(P[i * 3 + 1] / cell), cz = Math.floor(P[i * 3 + 2] / cell);
    const ri = covRadius(st.element[i]), hi = st.element[i] === 'H';
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
      const list = grid.get(key(cx + dx, cy + dy, cz + dz)); if (!list) continue;
      for (const j of list) {
        if (j <= i) continue;
        if (hi && st.element[j] === 'H') continue;
        if (st.het[i] !== st.het[j] && !(st.resName[i] === st.resName[j])) continue; // no protein-ligand bonds
        const ddx = P[i * 3] - P[j * 3], ddy = P[i * 3 + 1] - P[j * 3 + 1], ddz = P[i * 3 + 2] - P[j * 3 + 2];
        const d2 = ddx * ddx + ddy * ddy + ddz * ddz, max = ri + covRadius(st.element[j]) + 0.4;
        if (d2 > 0.16 && d2 < max * max) {
          const k = i * 1e6 + j; if (seen.has(k)) continue; seen.add(k); bonds.push(i, j, 1);
        }
      }
    }
  }
  return bonds;
}

// ---------------------------------------------------------------- PDB
export function parsePDB(text, opts = {}) {
  const atoms = [], helices = [], sheets = [], serialMap = new Map(), conectRaw = [];
  let model = 0;
  for (const line of text.split(/\r?\n/)) {
    const rec = line.slice(0, 6);
    if (rec === 'MODEL ') { model++; if (model > 1 && !opts.allModels) break; continue; }
    if (rec === 'ENDMDL' && !opts.allModels) { if (atoms.length) break; }
    if (rec === 'HELIX ') helices.push({ chain: line[19], start: +line.slice(21, 25), end: +line.slice(33, 37) });
    else if (rec === 'SHEET ') sheets.push({ chain: line[21], start: +line.slice(22, 26), end: +line.slice(33, 37) });
    else if (rec === 'ATOM  ' || rec === 'HETATM') {
      const alt = line[16]; if (alt !== ' ' && alt !== 'A' && alt !== undefined) continue;
      const name = line.slice(12, 16).trim();
      const element = normEl(line.slice(76, 78), line.slice(12, 14));
      serialMap.set(+line.slice(6, 11), atoms.length);
      atoms.push({ name, resName: line.slice(17, 20).trim(), chain: (line[21] || 'A').trim() || 'A', resSeq: +line.slice(22, 26),
        x: +line.slice(30, 38), y: +line.slice(38, 46), z: +line.slice(46, 54), b: +line.slice(60, 66) || 0, element, het: rec === 'HETATM' });
    } else if (rec === 'CONECT') {
      const a = +line.slice(6, 11);
      for (let c = 11; c < 31; c += 5) { const b = +line.slice(c, c + 5); if (b) conectRaw.push([a, b]); }
    }
  }
  const conect = conectRaw.map(([a, b]) => [serialMap.get(a), serialMap.get(b)]).filter(([a, b]) => a !== undefined && b !== undefined && atoms[a].het && atoms[b].het);
  // AMBER-style HETATM for standard residues (e.g. MSE) should behave as polymer.
  for (const a of atoms) if (a.het && AA3[a.resName]) a.het = false;
  return new Structure(atoms, { helices, sheets, conect: conect.length ? conect : null, ...opts });
}

// Multi-model PDB (trajectory) -> array of Float32Array coordinate frames.
export function parsePDBFrames(text) {
  const frames = []; let cur = [];
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith('ENDMDL')) { if (cur.length) frames.push(Float32Array.from(cur)); cur = []; }
    else if (line.startsWith('ATOM') || line.startsWith('HETATM')) {
      const alt = line[16]; if (alt !== ' ' && alt !== 'A') continue;
      cur.push(+line.slice(30, 38), +line.slice(38, 46), +line.slice(46, 54));
    }
  }
  if (cur.length) frames.push(Float32Array.from(cur));
  return frames;
}

// ---------------------------------------------------------------- mmCIF
function cifTokens(line) {
  const out = []; let i = 0;
  while (i < line.length) {
    const c = line[i];
    if (c === ' ' || c === '\t') { i++; continue; }
    if (c === "'" || c === '"') {
      let j = i + 1; while (j < line.length && !(line[j] === c && (j + 1 === line.length || line[j + 1] === ' '))) j++;
      out.push(line.slice(i + 1, j)); i = j + 1;
    } else { let j = i; while (j < line.length && line[j] !== ' ' && line[j] !== '\t') j++; out.push(line.slice(i, j)); i = j; }
  }
  return out;
}

export function parseMmCIF(text, opts = {}) {
  const lines = text.split(/\r?\n/);
  const atoms = [], helices = [], sheets = [];
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() !== 'loop_') continue;
    const cols = []; let j = i + 1;
    while (j < lines.length && lines[j].startsWith('_')) { cols.push(lines[j].trim().split(/\s+/)[0]); j++; }
    const cat = cols[0] ? cols[0].split('.')[0] : '';
    if (cat !== '_atom_site' && cat !== '_struct_conf' && cat !== '_struct_sheet_range') { i = j - 1; continue; }
    const ix = (name) => cols.indexOf(`${cat}.${name}`);
    const rows = [];
    let buf = [];
    for (; j < lines.length; j++) {
      const l = lines[j];
      if (l.startsWith('loop_') || l.startsWith('_') || l.startsWith('#') || l.startsWith('data_')) break;
      buf.push(...cifTokens(l));
      while (buf.length >= cols.length) { rows.push(buf.slice(0, cols.length)); buf = buf.slice(cols.length); }
    }
    i = j - 1;
    if (cat === '_atom_site') {
      const g = ix('group_PDB'), ts = ix('type_symbol'), an = ix('auth_atom_id') >= 0 ? ix('auth_atom_id') : ix('label_atom_id');
      const rn = ix('auth_comp_id') >= 0 ? ix('auth_comp_id') : ix('label_comp_id');
      const ch = ix('auth_asym_id') >= 0 ? ix('auth_asym_id') : ix('label_asym_id');
      const rs = ix('auth_seq_id') >= 0 ? ix('auth_seq_id') : ix('label_seq_id');
      const x = ix('Cartn_x'), y = ix('Cartn_y'), z = ix('Cartn_z'), b = ix('B_iso_or_equiv'), mdl = ix('pdbx_PDB_model_num'), alt = ix('label_alt_id');
      let firstModel = null; let seqCounter = 0; let lastKey = '';
      for (const r of rows) {
        if (mdl >= 0) { if (firstModel === null) firstModel = r[mdl]; if (r[mdl] !== firstModel) break; }
        if (alt >= 0 && r[alt] !== '.' && r[alt] !== '?' && r[alt] !== 'A') continue;
        let seq = parseInt(r[rs], 10);
        const key = r[ch] + r[rn];
        if (Number.isNaN(seq)) { if (key !== lastKey) seqCounter++; seq = seqCounter; } // ligands in AF3 output use '.'
        lastKey = key;
        const rname = r[rn].replace(/"/g, '');
        atoms.push({ name: r[an].replace(/"/g, ''), resName: rname, chain: r[ch], resSeq: seq, x: +r[x], y: +r[y], z: +r[z],
          b: b >= 0 ? +r[b] : 0, element: (r[ts] || '').toUpperCase(), het: g >= 0 ? r[g] === 'HETATM' && !AA3[rname] : !AA3[rname] });
      }
    } else if (cat === '_struct_conf') {
      const c = ix('beg_auth_asym_id'), s = ix('beg_auth_seq_id'), e = ix('end_auth_seq_id'), t = ix('conf_type_id');
      for (const r of rows) if (!r[t] || r[t].startsWith('HELX')) helices.push({ chain: r[c], start: +r[s], end: +r[e] });
    } else if (cat === '_struct_sheet_range') {
      const c = ix('beg_auth_asym_id'), s = ix('beg_auth_seq_id'), e = ix('end_auth_seq_id');
      for (const r of rows) sheets.push({ chain: r[c], start: +r[s], end: +r[e] });
    }
  }
  if (!atoms.length) throw new Error('No _atom_site records found in mmCIF');
  return new Structure(atoms, { helices, sheets, ...opts });
}

// ---------------------------------------------------------------- MDL molfile / SDF (V2000 + V3000)
export function parseMolblock(text, opts = {}) {
  const lines = text.split(/\r?\n/);
  const name = (lines[0] || '').trim() || opts.name || 'ligand';
  const counts = lines[3] || '';
  const atoms = [], bonds = [];
  if (counts.includes('V3000')) {
    let mode = '';
    for (const l of lines.slice(4)) {
      if (l.includes('BEGIN ATOM')) { mode = 'a'; continue; }
      if (l.includes('END ATOM')) { mode = ''; continue; }
      if (l.includes('BEGIN BOND')) { mode = 'b'; continue; }
      if (l.includes('END BOND')) { mode = ''; continue; }
      const t = l.replace('M  V30', '').trim().split(/\s+/);
      if (mode === 'a') {
        const chg = (t.find((s) => s.startsWith('CHG=')) || 'CHG=0').slice(4);
        atoms.push({ element: t[1].toUpperCase(), x: +t[2], y: +t[3], z: +t[4], name: t[1] + t[0], charge: +chg, het: 1 });
      }
      if (mode === 'b') bonds.push(+t[2] - 1, +t[3] - 1, Math.min(+t[1], 3));
    }
  } else {
    const na = parseInt(counts.slice(0, 3), 10), nb = parseInt(counts.slice(3, 6), 10);
    const counters = {};
    for (let i = 0; i < na; i++) {
      const l = lines[4 + i];
      const e = l.slice(31, 34).trim().toUpperCase();
      counters[e] = (counters[e] || 0) + 1;
      const cc = parseInt(l.slice(36, 39), 10) || 0;
      atoms.push({ x: +l.slice(0, 10), y: +l.slice(10, 20), z: +l.slice(20, 30), element: e, name: e + counters[e],
        charge: cc ? 4 - cc : 0, het: 1 });
    }
    for (let i = 0; i < nb; i++) {
      const l = lines[4 + na + i];
      const ord = parseInt(l.slice(6, 9), 10);
      bonds.push(parseInt(l.slice(0, 3), 10) - 1, parseInt(l.slice(3, 6), 10) - 1, ord === 4 ? 2 : Math.min(ord, 3)); // aromatic -> 2 for display
    }
    for (const l of lines.slice(4 + na + nb)) {
      if (l.startsWith('M  CHG')) { const t = l.trim().split(/\s+/); for (let k = 3; k < t.length; k += 2) atoms[+t[k] - 1].charge = +t[k + 1]; }
      if (l.startsWith('M  END')) break;
    }
  }
  atoms.forEach((a) => { a.resName = opts.resName || 'LIG'; a.chain = 'L'; a.resSeq = 1; });
  return new Structure(atoms, { bonds, kind: 'small', name: opts.name || name, source: opts.source || '' });
}

export function parseAny(text, filename = '', opts = {}) {
  const f = filename.toLowerCase();
  if (f.endsWith('.cif') || f.endsWith('.mmcif') || /^data_/m.test(text.slice(0, 200)) && text.includes('_atom_site.')) return parseMmCIF(text, opts);
  if (f.endsWith('.sdf') || f.endsWith('.mol') || /M {2}END/.test(text)) return parseMolblock(text, opts);
  return parsePDB(text, opts);
}
