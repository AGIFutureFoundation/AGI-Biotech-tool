import { yieldToEventLoop } from './util.js';

// Docking toolkit: Vina-like empirical scoring, pocket detection, flexible Monte Carlo docking.
// The scoring terms and weights follow AutoDock Vina (Trott & Olson 2010); this is a re-implementation for
// interactive use, not a validated replacement for Vina/Glide. Treat scores as relative rankings.

const XS = { C: 1.9, N: 1.8, O: 1.7, S: 2.0, P: 2.1, F: 1.5, CL: 1.8, BR: 2.0, I: 2.2, SE: 2.1 };
const xs = (e) => XS[e] || 1.2; // metals & others
// Shared with the dynamics engine so simulation contact distances match what the score expects.
export const contactRadius = xs;
const W = { g1: -0.0356, g2: -0.00516, rep: 0.84, hyd: -0.0351, hb: -0.587, rot: 0.0585 };
const CUT = 8;

export class ProteinGrid {
  constructor(st, cell = 4) {
    this.st = st; this.cell = cell; this.map = new Map();
    this.atoms = Array.from(st.heavy).filter((i) => { const r = st.residues[st.atomRes[i]]; return !r.water && !(st.excluded && st.excluded[i]); });
    this.rebuild();
  }
  rebuild() {
    this.map.clear(); const P = this.st.pos, c = this.cell;
    for (const i of this.atoms) {
      const k = this.key(Math.floor(P[i * 3] / c), Math.floor(P[i * 3 + 1] / c), Math.floor(P[i * 3 + 2] / c));
      (this.map.get(k) || this.map.set(k, []).get(k)).push(i);
    }
  }
  key(x, y, z) { return (x + 512) * 1048576 + (y + 512) * 1024 + (z + 512); }
  near(x, y, z, r, out) {
    const c = this.cell, P = this.st.pos, r2 = r * r; out.length = 0;
    const x0 = Math.floor((x - r) / c), x1 = Math.floor((x + r) / c), y0 = Math.floor((y - r) / c), y1 = Math.floor((y + r) / c), z0 = Math.floor((z - r) / c), z1 = Math.floor((z + r) / c);
    for (let a = x0; a <= x1; a++) for (let b = y0; b <= y1; b++) for (let d = z0; d <= z1; d++) {
      const l = this.map.get(this.key(a, b, d)); if (!l) continue;
      for (const j of l) { const dx = P[j * 3] - x, dy = P[j * 3 + 1] - y, dz = P[j * 3 + 2] - z; if (dx * dx + dy * dy + dz * dz < r2) out.push(j); }
    }
    return out;
  }
}

export function rotatableBonds(lig) {
  const rot = [];
  const inRing = ringBonds(lig);
  for (let k = 0; k < lig.bonds.length; k += 3) {
    const i = lig.bonds[k], j = lig.bonds[k + 1], o = lig.bonds[k + 2];
    if (o !== 1 || inRing.has(i < j ? i * 1e5 + j : j * 1e5 + i)) continue;
    const hi = lig.nbr[i].filter((x) => lig.element[x] !== 'H').length, hj = lig.nbr[j].filter((x) => lig.element[x] !== 'H').length;
    if (hi < 2 || hj < 2) continue;
    // Amide C-N is effectively rigid.
    const amide = (a, b) => lig.element[a] === 'C' && lig.element[b] === 'N' && lig.nbr[a].some((x) => lig.element[x] === 'O' && lig.bondOrder(a, x) === 2);
    if (amide(i, j) || amide(j, i)) continue;
    // Atoms on j's side.
    const side = new Set([j]); const stack = [j];
    while (stack.length) { const u = stack.pop(); for (const v of lig.nbr[u]) if (v !== i && !side.has(v)) { side.add(v); stack.push(v); } }
    if (side.has(i)) continue;
    const moving = side.size <= lig.n / 2 ? [...side] : [...Array(lig.n).keys()].filter((x) => !side.has(x));
    const [a, b] = side.size <= lig.n / 2 ? [i, j] : [j, i];
    rot.push({ a, b, moving });
  }
  return rot;
}

function ringBonds(st) {
  // A bond is in a ring if removing it leaves its atoms connected.
  const out = new Set();
  for (let k = 0; k < st.bonds.length; k += 3) {
    const i = st.bonds[k], j = st.bonds[k + 1];
    const seen = new Set([i]); const q = [i]; let found = false;
    while (q.length && !found) { const u = q.shift(); for (const v of st.nbr[u]) { if (u === i && v === j) continue; if (v === j) { found = true; break; } if (!seen.has(v)) { seen.add(v); q.push(v); } } }
    if (found) out.add(i < j ? i * 1e5 + j : j * 1e5 + i);
  }
  return out;
}

// Score ligand coordinates L (Float32Array, same order as lig atoms) against the protein.
export function vinaScore(grid, lig, L = lig.pos, { details = false, nrot = null } = {}) {
  const pr = grid.st, P = pr.pos, near = [];
  let g1 = 0, g2 = 0, rep = 0, hyd = 0, hb = 0;
  const hbonds = [], contacts = new Set();
  for (const i of lig.heavy) {
    const x = L[i * 3], y = L[i * 3 + 1], z = L[i * 3 + 2], ri = xs(lig.element[i]);
    grid.near(x, y, z, CUT, near);
    for (const j of near) {
      const r = Math.hypot(P[j * 3] - x, P[j * 3 + 1] - y, P[j * 3 + 2] - z);
      const d = r - ri - xs(pr.element[j]);
      g1 += Math.exp(-((d / 0.5) ** 2));
      g2 += Math.exp(-(((d - 3) / 2) ** 2));
      if (d < 0) rep += d * d;
      if (lig.hydrophobic[i] && pr.hydrophobic[j]) hyd += d < 0.5 ? 1 : d < 1.5 ? 1.5 - d : 0;
      if ((lig.donor[i] && pr.acceptor[j]) || (lig.acceptor[i] && pr.donor[j])) {
        const h = d < -0.7 ? 1 : d < 0 ? -d / 0.7 : 0;
        hb += h;
        if (details && h > 0.3) hbonds.push({ lig: i, prot: j, r });
      }
      if (details && r < 4.0) contacts.add(pr.atomRes[j]);
    }
  }
  const nr = nrot ?? (lig._nrot ??= rotatableBonds(lig).length);
  const inter = W.g1 * g1 + W.g2 * g2 + W.rep * rep + W.hyd * hyd + W.hb * hb;
  const total = inter / (1 + W.rot * nr);
  if (!details) return total;
  return { total, inter, terms: { gauss1: W.g1 * g1, gauss2: W.g2 * g2, repulsion: W.rep * rep, hydrophobic: W.hyd * hyd, hbond: W.hb * hb },
    hbonds, contactResidues: [...contacts], nrot: nr, ligandEfficiency: total / lig.heavy.length };
}

// Pocket detection: grid points that are empty but deeply buried (ray casting), clustered.
export function findPockets(st, { spacing = 1.0, maxPockets = 6 } = {}) {
  const heavy = Array.from(st.heavy).filter((i) => { const r = st.residues[st.atomRes[i]]; return r.polymer && !(st.excluded && st.excluded[i]); });
  if (!heavy.length) return [];
  const P = st.pos;
  let mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9];
  for (const i of heavy) for (let d = 0; d < 3; d++) { mn[d] = Math.min(mn[d], P[i * 3 + d]); mx[d] = Math.max(mx[d], P[i * 3 + d]); }
  mn = mn.map((v) => v - 2); mx = mx.map((v) => v + 2);
  const dims = mn.map((v, d) => Math.ceil((mx[d] - v) / spacing) + 1);
  const [nx, ny, nz] = dims, N = nx * ny * nz;
  if (N > 4e6) return findPocketsCoarse(st, spacing * 1.5, maxPockets);
  const occ = new Uint8Array(N);
  const id = (a, b, c) => (a * ny + b) * nz + c;
  for (const i of heavy) {
    const r = 1.6 + 1.2; // atom radius + probe-ish margin
    const cx = (P[i * 3] - mn[0]) / spacing, cy = (P[i * 3 + 1] - mn[1]) / spacing, cz = (P[i * 3 + 2] - mn[2]) / spacing, rr = r / spacing;
    for (let a = Math.max(0, Math.floor(cx - rr)); a <= Math.min(nx - 1, Math.ceil(cx + rr)); a++)
      for (let b = Math.max(0, Math.floor(cy - rr)); b <= Math.min(ny - 1, Math.ceil(cy + rr)); b++)
        for (let c = Math.max(0, Math.floor(cz - rr)); c <= Math.min(nz - 1, Math.ceil(cz + rr)); c++)
          if ((a - cx) ** 2 + (b - cy) ** 2 + (c - cz) ** 2 <= rr * rr) occ[id(a, b, c)] = 1;
  }
  const dirs = [];
  for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) if (a || b || c) dirs.push([a, b, c]);
  const maxStep = Math.round(10 / spacing);
  const buried = new Uint8Array(N);
  for (let a = 1; a < nx - 1; a++) for (let b = 1; b < ny - 1; b++) for (let c = 1; c < nz - 1; c++) {
    if (occ[id(a, b, c)]) continue;
    let hits = 0;
    for (let di = 0; di < dirs.length; di++) {
      const [dx, dy, dz] = dirs[di];
      for (let s = 1; s <= maxStep; s++) {
        const x = a + dx * s, y = b + dy * s, z = c + dz * s;
        if (x < 0 || y < 0 || z < 0 || x >= nx || y >= ny || z >= nz) break;
        if (occ[id(x, y, z)]) { hits++; break; }
      }
      if (hits + (dirs.length - di - 1) < 19) break; // cannot reach the buriedness threshold any more
    }
    if (hits >= 19) buried[id(a, b, c)] = hits;
  }
  // Connected components.
  const label = new Int32Array(N).fill(-1); const clusters = [];
  for (let s = 0; s < N; s++) {
    if (!buried[s] || label[s] >= 0) continue;
    const q = [s]; label[s] = clusters.length; const pts = [];
    while (q.length) {
      const u = q.pop(); pts.push(u);
      const a = Math.floor(u / (ny * nz)), b = Math.floor(u / nz) % ny, c = u % nz;
      for (const [dx, dy, dz] of dirs) {
        const x = a + dx, y = b + dy, z = c + dz;
        if (x < 0 || y < 0 || z < 0 || x >= nx || y >= ny || z >= nz) continue;
        const v = id(x, y, z); if (buried[v] && label[v] < 0) { label[v] = clusters.length; q.push(v); }
      }
    }
    clusters.push(pts);
  }
  const out = clusters.filter((c) => c.length >= 15).map((pts) => {
    let sx = 0, sy = 0, sz = 0, bur = 0;
    const coords = pts.map((u) => { const a = Math.floor(u / (ny * nz)), b = Math.floor(u / nz) % ny, c = u % nz; const p = [mn[0] + a * spacing, mn[1] + b * spacing, mn[2] + c * spacing]; sx += p[0]; sy += p[1]; sz += p[2]; bur += buried[u]; return p; });
    const center = [sx / pts.length, sy / pts.length, sz / pts.length];
    const volume = pts.length * spacing ** 3;
    return { center, volume, buriedness: bur / pts.length / 26, points: coords, score: volume * (bur / pts.length / 26) ** 2 };
  }).sort((a, b) => b.score - a.score).slice(0, maxPockets);
  // Lining residues.
  const grid = new ProteinGrid(st, 4), near = [];
  for (const p of out) {
    const res = new Set();
    for (const q of p.points.filter((_, k) => k % 2 === 0)) for (const j of grid.near(q[0], q[1], q[2], 4.0, near)) res.add(st.atomRes[j]);
    p.residues = [...res];
    p.label = p.residues.slice(0, 6).map((r) => st.residues[r].resName + st.residues[r].resSeq).join(' ');
    p.druggability = Math.min(1, (p.volume / 600) * p.buriedness * 1.2);
  }
  return out;
}

function findPocketsCoarse(st, spacing, maxPockets) { return findPockets(st, { spacing, maxPockets }); }

// ---------------------------------------------------------------- Monte Carlo docking
function rotateAbout(L, atoms, ax, ay, az, ux, uy, uz, ang) {
  const c = Math.cos(ang), s = Math.sin(ang), t = 1 - c;
  for (const i of atoms) {
    const x = L[i * 3] - ax, y = L[i * 3 + 1] - ay, z = L[i * 3 + 2] - az;
    L[i * 3] = ax + (t * ux * ux + c) * x + (t * ux * uy - s * uz) * y + (t * ux * uz + s * uy) * z;
    L[i * 3 + 1] = ay + (t * ux * uy + s * uz) * x + (t * uy * uy + c) * y + (t * uy * uz - s * ux) * z;
    L[i * 3 + 2] = az + (t * ux * uz - s * uy) * x + (t * uy * uz + s * ux) * y + (t * uz * uz + c) * z;
  }
}

export function centroid(L, n) { let x = 0, y = 0, z = 0; for (let i = 0; i < n; i++) { x += L[i * 3]; y += L[i * 3 + 1]; z += L[i * 3 + 2]; } return [x / n, y / n, z / n]; }

function randomUnit() { const z = Math.random() * 2 - 1, t = Math.random() * Math.PI * 2, r = Math.sqrt(1 - z * z); return [r * Math.cos(t), r * Math.sin(t), z]; }

function intraClash(lig, L, pairs) {
  let e = 0;
  for (let k = 0; k < pairs.length; k += 2) {
    const i = pairs[k], j = pairs[k + 1];
    const d = Math.hypot(L[i * 3] - L[j * 3], L[i * 3 + 1] - L[j * 3 + 1], L[i * 3 + 2] - L[j * 3 + 2]);
    if (d < 3.0) e += (3.0 - d) ** 2;
  }
  return e * 0.5;
}

export async function dockLigand(grid, lig, center, { runs = 8, steps = 1500, box = 8, onProgress, pairs = null, shouldStop } = {}) {
  const rot = rotatableBonds(lig); lig._nrot = rot.length;
  const n = lig.n, all = [...Array(n).keys()];
  const base = Float32Array.from(lig.pos);
  const c0 = centroid(base, n);
  for (let i = 0; i < n; i++) { base[i * 3] -= c0[0]; base[i * 3 + 1] -= c0[1]; base[i * 3 + 2] -= c0[2]; }
  const intraPairs = pairs || [];
  const poses = [];
  const energy = (L) => vinaScore(grid, lig, L, { nrot: rot.length }) + intraClash(lig, L, intraPairs) + boxPenalty(L, n, center, box);
  for (let run = 0; run < runs; run++) {
    const L = Float32Array.from(base);
    // random orientation + position in box
    const u = randomUnit(); rotateAbout(L, all, 0, 0, 0, u[0], u[1], u[2], Math.random() * Math.PI * 2);
    for (const b of rot) { const [ux, uy, uz] = axis(L, b); rotateAbout(L, b.moving, L[b.a * 3], L[b.a * 3 + 1], L[b.a * 3 + 2], ux, uy, uz, Math.random() * Math.PI * 2); }
    const off = randomUnit().map((v) => v * Math.random() * box * 0.4);
    for (let i = 0; i < n; i++) { L[i * 3] += center[0] + off[0]; L[i * 3 + 1] += center[1] + off[1]; L[i * 3 + 2] += center[2] + off[2]; }
    let e = energy(L), best = Float32Array.from(L), bestE = e;
    const trial = new Float32Array(L.length);
    for (let s = 0; s < steps; s++) {
      const temp = 1.2 * (1 - s / steps) + 0.05;
      trial.set(L);
      const mv = Math.random();
      if (mv < 0.4) { const d = randomUnit(), m = Math.random() * 1.0; for (let i = 0; i < n; i++) { trial[i * 3] += d[0] * m; trial[i * 3 + 1] += d[1] * m; trial[i * 3 + 2] += d[2] * m; } }
      else if (mv < 0.75 || !rot.length) { const c = centroid(trial, n), a = randomUnit(); rotateAbout(trial, all, c[0], c[1], c[2], a[0], a[1], a[2], (Math.random() - 0.5) * 0.6); }
      else { const b = rot[Math.floor(Math.random() * rot.length)]; const [ux, uy, uz] = axis(trial, b); rotateAbout(trial, b.moving, trial[b.a * 3], trial[b.a * 3 + 1], trial[b.a * 3 + 2], ux, uy, uz, (Math.random() - 0.5) * 2.0); }
      const et = energy(trial);
      if (et < e || Math.random() < Math.exp(-(et - e) / temp)) { L.set(trial); e = et; if (e < bestE) { bestE = e; best.set(L); } }
      if (s % 250 === 0) {
        if (shouldStop && shouldStop()) break;
        onProgress && onProgress({ run, step: s, best: poses.length ? Math.min(bestE, poses[0].score) : bestE, coords: best });
        await yieldToEventLoop();
      }
    }
    // Rank by the energy the search actually minimised, report the affinity.
    //
    // These were the same number before, and that was the bug. Each run picks
    // its best pose under vinaScore + intraClash + boxPenalty, then the pose
    // was stored and ranked by vinaScore alone -- so across runs a pose
    // carrying internal strain, or hanging outside the box, could outrank a
    // clean one because the terms that made the search avoid it were thrown
    // away at comparison time. A ligand folded through itself has no business
    // ranking first, whatever its intermolecular score says.
    //
    // `score` stays vinaScore because that is the affinity estimate callers
    // read and display. `rank` is the full search energy, and is what the sort
    // uses, so the pose the search preferred is the pose that comes out first.
    poses.push({
      coords: best,
      score: vinaScore(grid, lig, best, { nrot: rot.length }),
      rank: bestE,
    });
    poses.sort((a, b) => a.rank - b.rank);
    if (shouldStop && shouldStop()) break;
  }
  // Keep distinct poses (RMSD >= 1.5 Å apart) and drop ones that never resolved their clashes.
  const uniq = [];
  for (const p of poses) if (!uniq.some((q) => rmsd(p.coords, q.coords, n) < 1.5)) uniq.push(p);
  const good = uniq.filter((p) => p.score < 0);
  return good.length ? good : uniq.slice(0, 1);
}

function axis(L, b) { const ux = L[b.b * 3] - L[b.a * 3], uy = L[b.b * 3 + 1] - L[b.a * 3 + 1], uz = L[b.b * 3 + 2] - L[b.a * 3 + 2]; const l = Math.hypot(ux, uy, uz) || 1; return [ux / l, uy / l, uz / l]; }
function boxPenalty(L, n, c, box) { let e = 0; for (let i = 0; i < n; i++) for (let d = 0; d < 3; d++) { const o = Math.abs(L[i * 3 + d] - c[d]) - box; if (o > 0) e += o * o; } return e; }
export function rmsd(A, B, n) { let s = 0; for (let i = 0; i < n * 3; i++) s += (A[i] - B[i]) ** 2; return Math.sqrt(s / n); }
