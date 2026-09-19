// Interactive molecular dynamics that runs in the headset at frame rate.
//
// Model (clearly coarse — the OpenMM backend does full all-atom physics):
//   * Ligand: all heavy atoms, harmonic bonds, 1-3 angle distances, sp2 planarity, soft intra-ligand repulsion.
//   * Protein: anisotropic elastic network on C-alpha atoms (10 Å cutoff, k = 1 kcal/mol/Å²); every atom of a
//     residue rides on its C-alpha.
//   * Protein-ligand: Lennard-Jones 12-6 contact term with H-bond pairs deepened (donor/acceptor typing).
//   * Langevin thermostat; user steering spring for "grab the ligand and pull" interactive MD.
// Units: Å, ps, amu, kcal/mol.  Acceleration factor F/m -> Å/ps² is 418.4.
import { vdwRadius, covRadius, mass as elMass } from './elements.js';

const ACC = 418.4;
const KB = 0.0019872041;

function gauss() { let u = 0, v = 0; while (!u) u = Math.random(); while (!v) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }

// ---------------------------------------------------------------- ligand force field
export function buildLigandFF(st, info = {}) {
  const n = st.n, P = st.pos;
  const aromA = new Set(info.aromaticAtoms || []);
  const rings = info.rings || [];
  const ringOf = (i, j) => rings.find((r) => r.includes(i) && r.includes(j));
  const bonds = [], angles = [], planar = [], pairs = [];
  const isSp2 = new Uint8Array(n), isSp = new Uint8Array(n);
  for (let k = 0; k < st.bonds.length; k += 3) {
    const i = st.bonds[k], j = st.bonds[k + 1], o = st.bonds[k + 2];
    if (o === 2) { isSp2[i] = isSp2[j] = 1; }
    if (o === 3) { isSp[i] = isSp[j] = 1; }
  }
  for (const a of aromA) isSp2[a] = 1;
  // Conjugated N / O next to sp2 (amides, anilines, esters) are planar too.
  for (let i = 0; i < n; i++) if ((st.element[i] === 'N') && !isSp2[i] && st.nbr[i].some((j) => isSp2[j]) && st.nbr[i].length <= 3) isSp2[i] = 2;

  const aromBond = new Set((info.aromaticBondPairs || []).map(([a, b]) => (a < b ? a * 1e5 + b : b * 1e5 + a)));
  for (let k = 0; k < st.bonds.length; k += 3) {
    const i = st.bonds[k], j = st.bonds[k + 1], o = st.bonds[k + 2];
    let r0 = covRadius(st.element[i]) + covRadius(st.element[j]);
    const key = i < j ? i * 1e5 + j : j * 1e5 + i;
    if (aromBond.has(key)) r0 *= 0.915; else if (o === 2) r0 *= 0.87; else if (o === 3) r0 *= 0.78;
    else if (isSp2[i] && isSp2[j]) r0 *= 0.96;
    bonds.push(i, j, r0, 350);
  }
  const bondLen = (i, j) => { for (let k = 0; k < bonds.length; k += 4) if ((bonds[k] === i && bonds[k + 1] === j) || (bonds[k] === j && bonds[k + 1] === i)) return bonds[k + 2]; return 1.5; };
  for (let c = 0; c < n; c++) {
    const nb = st.nbr[c];
    for (let a = 0; a < nb.length; a++) for (let b = a + 1; b < nb.length; b++) {
      const i = nb[a], j = nb[b];
      let theta = isSp[c] ? 180 : isSp2[c] ? 120 : 109.5;
      const ring = ringOf(i, c) && ringOf(c, j) && rings.find((r) => r.includes(i) && r.includes(c) && r.includes(j));
      if (ring) theta = ring.length === 3 ? 60 : ring.length === 4 ? 90 : ring.length === 5 ? (isSp2[c] ? 108 : 104) : ring.length === 6 ? (isSp2[c] ? 120 : 111) : theta;
      const r1 = bondLen(i, c), r2 = bondLen(c, j);
      const d0 = Math.sqrt(r1 * r1 + r2 * r2 - 2 * r1 * r2 * Math.cos(theta * Math.PI / 180));
      angles.push(i, j, d0, 120);
    }
    if (isSp2[c] && nb.length === 3) planar.push(c, nb[0], nb[1], nb[2]);
  }
  // Keep cis/trans across double bonds and aromatic ring flatness from the input geometry (1-4 distances).
  const fourteen = [];
  for (let k = 0; k < st.bonds.length; k += 3) {
    const i = st.bonds[k], j = st.bonds[k + 1];
    const key = i < j ? i * 1e5 + j : j * 1e5 + i;
    if (!(st.bonds[k + 2] === 2 || aromBond.has(key))) continue;
    for (const a of st.nbr[i]) if (a !== j) for (const b of st.nbr[j]) if (b !== i && a !== b) fourteen.push(a, b);
  }
  // Topological distances for the non-bonded list (>= 3 bonds apart).
  const topo = topoDist(st, 3);
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (topo[i * n + j] >= 3) pairs.push(i, j);
  return { n, bonds, angles, planar, pairs, fourteen, fourteenRef: null, isSp2 };
}

export function setFourteenRef(ff, P) {
  const T = ff.fourteen; ff.fourteenRef = new Float32Array(T.length / 2);
  for (let k = 0; k < T.length; k += 2) { const i = T[k], j = T[k + 1]; ff.fourteenRef[k / 2] = Math.hypot(P[i * 3] - P[j * 3], P[i * 3 + 1] - P[j * 3 + 1], P[i * 3 + 2] - P[j * 3 + 2]); }
}

export function topoDist(st, cap = 4) {
  const n = st.n, D = new Uint8Array(n * n).fill(255);
  for (let s = 0; s < n; s++) {
    D[s * n + s] = 0; let front = [s];
    for (let d = 1; d <= cap && front.length; d++) {
      const nxt = [];
      for (const u of front) for (const v of st.nbr[u]) if (D[s * n + v] === 255) { D[s * n + v] = d; nxt.push(v); }
      front = nxt;
    }
  }
  return D;
}

// Energy + forces (added into F) for the ligand FF. Returns energy.
export function ligandForces(ff, P, F, { repel = 3.1, krep = 4 } = {}) {
  let E = 0;
  const B = ff.bonds;
  for (let k = 0; k < B.length; k += 4) E += spring(P, F, B[k], B[k + 1], B[k + 2], B[k + 3]);
  const A = ff.angles;
  for (let k = 0; k < A.length; k += 4) E += spring(P, F, A[k], A[k + 1], A[k + 2], A[k + 3]);
  if (ff.fourteenRef) { const T = ff.fourteen; for (let k = 0; k < T.length; k += 2) E += spring(P, F, T[k], T[k + 1], ff.fourteenRef[k / 2], 25); }
  const PL = ff.planar;
  for (let k = 0; k < PL.length; k += 4) E += planarity(P, F, PL[k], PL[k + 1], PL[k + 2], PL[k + 3], 40);
  const PR = ff.pairs;
  for (let k = 0; k < PR.length; k += 2) {
    const i = PR[k], j = PR[k + 1];
    const dx = P[i * 3] - P[j * 3], dy = P[i * 3 + 1] - P[j * 3 + 1], dz = P[i * 3 + 2] - P[j * 3 + 2];
    const r2 = dx * dx + dy * dy + dz * dz;
    if (r2 >= repel * repel) continue;
    const r = Math.sqrt(r2) || 1e-3, dr = repel - r;
    E += krep * dr * dr;
    const f = 2 * krep * dr / r;
    F[i * 3] += f * dx; F[i * 3 + 1] += f * dy; F[i * 3 + 2] += f * dz;
    F[j * 3] -= f * dx; F[j * 3 + 1] -= f * dy; F[j * 3 + 2] -= f * dz;
  }
  return E;
}

function spring(P, F, i, j, r0, k) {
  const dx = P[i * 3] - P[j * 3], dy = P[i * 3 + 1] - P[j * 3 + 1], dz = P[i * 3 + 2] - P[j * 3 + 2];
  const r = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-4, dr = r - r0;
  const f = -2 * k * dr / r;
  F[i * 3] += f * dx; F[i * 3 + 1] += f * dy; F[i * 3 + 2] += f * dz;
  F[j * 3] -= f * dx; F[j * 3 + 1] -= f * dy; F[j * 3 + 2] -= f * dz;
  return k * dr * dr;
}

function planarity(P, F, c, a, b, d, k) {
  const ax = P[a * 3], ay = P[a * 3 + 1], az = P[a * 3 + 2];
  const ux = P[b * 3] - ax, uy = P[b * 3 + 1] - ay, uz = P[b * 3 + 2] - az;
  const vx = P[d * 3] - ax, vy = P[d * 3 + 1] - ay, vz = P[d * 3 + 2] - az;
  let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
  const nl = Math.hypot(nx, ny, nz) || 1; nx /= nl; ny /= nl; nz /= nl;
  const h = (P[c * 3] - ax) * nx + (P[c * 3 + 1] - ay) * ny + (P[c * 3 + 2] - az) * nz;
  const f = -2 * k * h;
  F[c * 3] += f * nx; F[c * 3 + 1] += f * ny; F[c * 3 + 2] += f * nz;
  for (const o of [a, b, d]) { F[o * 3] -= f * nx / 3; F[o * 3 + 1] -= f * ny / 3; F[o * 3 + 2] -= f * nz / 3; }
  return k * h * h;
}

// FIRE minimiser (used for the fast in-browser 3D embedding and for pose relaxation).
export function minimize(P, forceFn, { steps = 800, dtMax = 0.12, fTol = 0.02 } = {}) {
  const n = P.length, V = new Float32Array(n), F = new Float32Array(n);
  let dt = 0.02, alpha = 0.1, npos = 0, E = 0;
  for (let s = 0; s < steps; s++) {
    F.fill(0); E = forceFn(P, F);
    let pw = 0, fn = 0, vn = 0;
    for (let i = 0; i < n; i++) { pw += F[i] * V[i]; fn += F[i] * F[i]; vn += V[i] * V[i]; }
    fn = Math.sqrt(fn); vn = Math.sqrt(vn);
    if (fn / (n / 3) < fTol) break;
    if (pw > 0) {
      for (let i = 0; i < n; i++) V[i] = (1 - alpha) * V[i] + alpha * F[i] / (fn || 1) * vn;
      if (++npos > 5) { dt = Math.min(dt * 1.1, dtMax); alpha *= 0.99; }
    } else { V.fill(0); dt *= 0.5; alpha = 0.1; npos = 0; }
    for (let i = 0; i < n; i++) { V[i] += F[i] * dt; const step = V[i] * dt; P[i] += Math.max(-0.3, Math.min(0.3, step)); }
  }
  return E;
}

// ---------------------------------------------------------------- MD engine
export class MDEngine {
  constructor({ protein = null, ligand = null, ligandFF = null, temperature = 300, dt = 0.002, gamma = 5, enmCutoff = 10, enmK = 1.0 } = {}) {
    this.protein = protein; this.ligand = ligand; this.T = temperature; this.dt = dt; this.gamma = gamma;
    this.time = 0; this.steer = null; this.frozenProtein = false;
    this.energy = { inter: 0, lig: 0, enm: 0 };
    if (protein) this.setupProtein(enmCutoff, enmK);
    if (ligand) this.setupLigand(ligandFF);
  }

  setupProtein(cut, k) {
    const st = this.protein;
    const ca = st.residues.filter((r) => r.ca >= 0);
    this.caRes = ca;
    const m = ca.length;
    this.caPos = new Float32Array(m * 3); this.caRef = new Float32Array(m * 3);
    ca.forEach((r, i) => { for (let d = 0; d < 3; d++) this.caPos[i * 3 + d] = this.caRef[i * 3 + d] = st.pos[r.ca * 3 + d]; });
    this.caV = new Float32Array(m * 3); this.caF = new Float32Array(m * 3);
    this.caMass = 110;
    this.protRef = Float32Array.from(st.pos);
    this.atomCa = new Int32Array(st.n).fill(-1);
    const resToCa = new Map(ca.map((r, i) => [r.idx, i]));
    for (let i = 0; i < st.n; i++) { const c = resToCa.get(st.atomRes[i]); if (c !== undefined) this.atomCa[i] = c; }
    const springs = [];
    const P = this.caPos;
    for (let i = 0; i < m; i++) for (let j = i + 1; j < m; j++) {
      const dx = P[i * 3] - P[j * 3], dy = P[i * 3 + 1] - P[j * 3 + 1], dz = P[i * 3 + 2] - P[j * 3 + 2];
      const r = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (r < cut) springs.push(i, j, r, j === i + 1 && ca[i].chain === ca[j].chain ? k * 10 : k);
    }
    this.enm = springs;
    // Heavy protein atoms for the interaction grid.
    this.protHeavy = Array.from(st.heavy).filter((i) => !st.residues[st.atomRes[i]].water && !(st.excluded && st.excluded[i]));
  }

  setupLigand(ff) {
    const st = this.ligand;
    this.ff = ff || buildLigandFF(st, st.chem || {});
    if (!this.ff.fourteenRef) setFourteenRef(this.ff, st.pos);
    this.lp = st.pos; // simulate in place
    this.lv = new Float32Array(st.n * 3); this.lf = new Float32Array(st.n * 3);
    this.lm = Float32Array.from(st.element, (e) => elMass(e));
    this.lr = Float32Array.from(st.element, (e) => vdwRadius(e));
    this.ligRef = Float32Array.from(st.pos);
    this.nlistAge = 1e9;
    for (let i = 0; i < st.n; i++) { const s = Math.sqrt(KB * this.T * ACC / this.lm[i]); for (let d = 0; d < 3; d++) this.lv[i * 3 + d] = gauss() * s; }
  }

  buildNeighborList() {
    const L = this.ligand, Pp = this.protein.pos, pairs = [];
    const lp = this.lp;
    let cx = 0, cy = 0, cz = 0; for (let i = 0; i < L.n; i++) { cx += lp[i * 3]; cy += lp[i * 3 + 1]; cz += lp[i * 3 + 2]; }
    cx /= L.n; cy /= L.n; cz /= L.n;
    let rad = 0; for (let i = 0; i < L.n; i++) rad = Math.max(rad, Math.hypot(lp[i * 3] - cx, lp[i * 3 + 1] - cy, lp[i * 3 + 2] - cz));
    const near = [];
    const R = rad + 10;
    for (const j of this.protHeavy) {
      const dx = Pp[j * 3] - cx, dy = Pp[j * 3 + 1] - cy, dz = Pp[j * 3 + 2] - cz;
      if (dx * dx + dy * dy + dz * dz < R * R) near.push(j);
    }
    for (let i = 0; i < L.n; i++) for (const j of near) pairs.push(i, j);
    this.nlist = pairs; this.nlistAge = 0;
  }

  // Protein-ligand LJ + H-bond contact forces. Protein forces are routed to C-alpha beads.
  interForces() {
    const L = this.ligand, Pr = this.protein, lp = this.lp, pp = Pr.pos, F = this.lf, CF = this.caF;
    let E = 0; const NL = this.nlist;
    for (let k = 0; k < NL.length; k += 2) {
      const i = NL[k], j = NL[k + 1];
      const dx = lp[i * 3] - pp[j * 3], dy = lp[i * 3 + 1] - pp[j * 3 + 1], dz = lp[i * 3 + 2] - pp[j * 3 + 2];
      const r2 = dx * dx + dy * dy + dz * dz;
      if (r2 > 64) continue;
      const hb = (L.donor[i] && Pr.acceptor[j]) || (L.acceptor[i] && Pr.donor[j]);
      const rm = hb ? 2.9 : (this.lr[i] + vdwRadius(Pr.element[j])) * 0.95;
      const eps = hb ? 1.6 : (L.hydrophobic[i] && Pr.hydrophobic[j] ? 0.28 : 0.14);
      const s2 = (rm * rm) / Math.max(r2, 0.64), s6 = s2 * s2 * s2, s12 = s6 * s6;
      E += eps * (s12 - 2 * s6);
      let f = 12 * eps * (s12 - s6) / Math.max(r2, 0.64);
      if (f > 60) f = 60; else if (f < -60) f = -60;
      F[i * 3] += f * dx; F[i * 3 + 1] += f * dy; F[i * 3 + 2] += f * dz;
      const c = this.atomCa[j];
      if (c >= 0 && !this.frozenProtein) { CF[c * 3] -= f * dx; CF[c * 3 + 1] -= f * dy; CF[c * 3 + 2] -= f * dz; }
    }
    return E;
  }

  enmForces() {
    const S = this.enm, P = this.caPos, F = this.caF; let E = 0;
    for (let k = 0; k < S.length; k += 4) E += spring(P, F, S[k], S[k + 1], S[k + 2], S[k + 3]);
    return E;
  }

  // Squeeze out starting clashes so the thermostat does not have to absorb a huge initial force.
  relax(steps = 300) {
    if (!this.ligand) return 0;
    const F = new Float32Array(this.ligand.n * 3);
    if (this.protein) this.buildNeighborList();
    const e = minimize(this.lp, (P, Fout) => {
      let E = ligandForces(this.ff, P, Fout);
      if (this.protein) {
        F.fill(0); const saveCa = this.caF; this.caF = new Float32Array(this.caPos.length);
        const before = this.lf; this.lf = Fout;
        E += this.interForces();
        this.lf = before; this.caF = saveCa;
      }
      return E;
    }, { steps, dtMax: 0.08 });
    this.lv.fill(0);
    for (let i = 0; i < this.ligand.n; i++) { const s = Math.sqrt(KB * this.T * ACC / this.lm[i]); for (let d = 0; d < 3; d++) this.lv[i * 3 + d] = gauss() * s; }
    this.ligRef = Float32Array.from(this.lp);
    return e;
  }

  setSteer(target, k = 20) { this.steer = target ? { ...target, k } : null; } // {x,y,z, atoms?:[...]} in Å

  step(n = 10) {
    const dt = this.dt, g = this.gamma, T = this.T;
    const c1 = Math.exp(-g * dt);
    for (let s = 0; s < n; s++) {
      if (this.ligand) {
        this.lf.fill(0);
        this.energy.lig = ligandForces(this.ff, this.lp, this.lf);
      }
      if (this.protein) { this.caF.fill(0); this.energy.enm = this.frozenProtein ? 0 : this.enmForces(); }
      if (this.ligand && this.protein) {
        if (this.nlistAge++ > 25) this.buildNeighborList();
        this.energy.inter = this.interForces();
      }
      if (this.ligand && this.steer) {
        const atoms = this.steer.atoms || [...Array(this.ligand.n).keys()];
        let cx = 0, cy = 0, cz = 0; for (const i of atoms) { cx += this.lp[i * 3]; cy += this.lp[i * 3 + 1]; cz += this.lp[i * 3 + 2]; }
        cx /= atoms.length; cy /= atoms.length; cz /= atoms.length;
        const k = this.steer.k;
        for (const i of atoms) { this.lf[i * 3] += k * (this.steer.x - cx) / atoms.length * 3; this.lf[i * 3 + 1] += k * (this.steer.y - cy) / atoms.length * 3; this.lf[i * 3 + 2] += k * (this.steer.z - cz) / atoms.length * 3; }
      }
      // Langevin (Euler-Maruyama with exact friction factor), per-degree-of-freedom.
      if (this.ligand) langevin(this.lp, this.lv, this.lf, this.lm, dt, c1, T);
      if (this.protein && !this.frozenProtein) {
        const m = this.caMass;
        langevin(this.caPos, this.caV, this.caF, null, dt, c1, T, m);
      }
      this.time += dt;
    }
    if (this.protein && !this.frozenProtein) this.syncProtein();
  }

  syncProtein() {
    const st = this.protein, P = st.pos, R = this.protRef, C = this.caPos, C0 = this.caRef;
    for (let i = 0; i < st.n; i++) {
      const c = this.atomCa[i]; if (c < 0) continue;
      P[i * 3] = R[i * 3] + C[c * 3] - C0[c * 3];
      P[i * 3 + 1] = R[i * 3 + 1] + C[c * 3 + 1] - C0[c * 3 + 1];
      P[i * 3 + 2] = R[i * 3 + 2] + C[c * 3 + 2] - C0[c * 3 + 2];
    }
  }

  // Keep protein reference in sync if the protein was replaced by an external frame.
  resetProteinReference() { if (this.protein) this.setupProtein(10, 1); }

  kineticTemperature() {
    let ke = 0, dof = 0;
    if (this.ligand) for (let i = 0; i < this.ligand.n; i++) { for (let d = 0; d < 3; d++) ke += 0.5 * this.lm[i] * this.lv[i * 3 + d] ** 2; dof += 3; }
    if (this.protein && !this.frozenProtein) for (let i = 0; i < this.caV.length; i++) { ke += 0.5 * this.caMass * this.caV[i] ** 2; dof++; }
    return dof ? (2 * ke / ACC) / (dof * KB) : 0;
  }

  ligandRMSD() {
    if (!this.ligand) return 0; let s = 0; const n = this.ligand.n;
    for (let i = 0; i < n * 3; i++) s += (this.lp[i] - this.ligRef[i]) ** 2;
    return Math.sqrt(s / n);
  }

  proteinRMSF() {
    if (!this.protein) return 0; let s = 0; const m = this.caPos.length / 3;
    for (let i = 0; i < m * 3; i++) s += (this.caPos[i] - this.caRef[i]) ** 2;
    return Math.sqrt(s / m);
  }
}

function langevin(P, V, F, M, dt, c1, T, mScalar) {
  const n = P.length / 3;
  for (let i = 0; i < n; i++) {
    const m = M ? M[i] : mScalar;
    const sig = Math.sqrt((1 - c1 * c1) * KB * T * ACC / m);
    for (let d = 0; d < 3; d++) {
      const k = i * 3 + d;
      V[k] += F[k] / m * ACC * dt;
      V[k] = c1 * V[k] + sig * gauss();
      if (V[k] > 40) V[k] = 40; else if (V[k] < -40) V[k] = -40; // safety clamp (Å/ps)
      P[k] += V[k] * dt;
    }
  }
}
