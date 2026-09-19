// three.js representations of a Structure: ball-and-stick, sticks, spacefill, lines, cartoon.
import * as THREE from 'three';
import { cpk, vdwRadius, CHAIN_COLORS, HYDRO, plddtColor, divergent, rainbow } from './elements.js';

const SPHERE = new THREE.IcosahedronGeometry(1, 2);
const SPHERE_LO = new THREE.IcosahedronGeometry(1, 1);
const CYL = new THREE.CylinderGeometry(1, 1, 1, 8, 1, true);
const UP = new THREE.Vector3(0, 1, 0);
const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _v = new THREE.Vector3(), _s = new THREE.Vector3(), _c = new THREE.Color();
const _a = new THREE.Vector3(), _b = new THREE.Vector3();

export const REPS = ['cartoon', 'cartoon+pocket', 'ballstick', 'sticks', 'spacefill', 'lines'];
export const COLORS = ['element', 'chain', 'ss', 'plddt', 'rainbow', 'hydrophobic', 'missense', 'carbon-accent'];

export class MolView {
  constructor(st, opts = {}) {
    this.st = st;
    this.group = new THREE.Group();
    this.group.name = st.name;
    this.style = { rep: st.isSmall ? 'ballstick' : 'cartoon+pocket', color: st.isSmall ? 'carbon-accent' : 'chain', showH: false,
      showWater: false, accent: opts.accent || 0x39d98a, ligandRep: 'ballstick', opacity: 1, ...opts.style };
    this.missense = null; // Map resSeq -> mean pathogenicity
    this.pocketResidues = new Set();
    this.highlight = new Set();
    this.material = new THREE.MeshStandardMaterial({ roughness: 0.45, metalness: 0.05 });
    this.cartoonMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.5, metalness: 0.0, side: THREE.DoubleSide });
    this.build();
  }

  setStyle(patch) { Object.assign(this.style, patch); this.build(); }

  dispose() {
    for (const c of [...this.group.children]) { c.geometry && c.geometry !== SPHERE && c.geometry !== CYL && c.geometry !== SPHERE_LO && c.geometry.dispose(); this.group.remove(c); }
  }

  atomColors() {
    const st = this.st, mode = this.style.color, n = st.n, out = new Uint32Array(n);
    const nres = st.residues.length;
    for (let i = 0; i < n; i++) {
      const e = st.element[i], r = st.atomRes[i], res = st.residues[r];
      let c = cpk(e);
      switch (mode) {
        case 'chain': c = e === 'C' || !res.polymer ? CHAIN_COLORS[st.chains.indexOf(st.chain[i]) % CHAIN_COLORS.length] : cpk(e); if (!res.polymer && e === 'C') c = this.style.accent; break;
        case 'ss': c = res.polymer ? [0xcfd8dc, 0xff4f79, 0xffc145][st.ss[r]] : (e === 'C' ? this.style.accent : cpk(e)); break;
        case 'plddt': c = res.polymer ? plddtColor(st.bfac[i]) : cpk(e); break;
        case 'rainbow': c = res.polymer ? rainbow(r / Math.max(1, nres - 1)) : cpk(e); break;
        case 'hydrophobic': { const h = HYDRO[res.resName]; c = h === undefined ? cpk(e) : divergent((h + 4.5) / 9 * -1 + 1); break; }
        case 'missense': { const m = this.missense && this.missense.get(res.resSeq); c = m === undefined ? 0x55606a : divergent(m); break; }
        case 'carbon-accent': c = e === 'C' ? this.style.accent : cpk(e); break;
        default: break;
      }
      out[i] = c;
    }
    for (const i of this.highlight) out[i] = 0xffff00;
    return out;
  }

  visibleAtom(i) {
    const st = this.st, e = st.element[i];
    if (e === 'H' && !this.style.showH) return false;
    const res = st.residues[st.atomRes[i]];
    if (res.water) return this.style.showWater;
    return true;
  }

  build() {
    this.dispose();
    const st = this.st, rep = this.style.rep;
    this.colors = this.atomColors();
    // Which atoms get sphere/stick treatment?
    const atomMode = new Uint8Array(st.n); // 0 hidden, 1 ball-stick, 2 sticks, 3 spacefill, 4 lines
    const repCode = { ballstick: 1, sticks: 2, spacefill: 3, lines: 4 };
    const ligCode = repCode[this.style.ligandRep] || 1;
    for (let i = 0; i < st.n; i++) {
      if (!this.visibleAtom(i)) continue;
      const res = st.residues[st.atomRes[i]];
      if (!res.polymer) { atomMode[i] = rep === 'spacefill' ? 3 : ligCode; if (res.ion) atomMode[i] = 3; continue; }
      if (rep === 'cartoon') continue;
      if (rep === 'cartoon+pocket') { if (this.pocketResidues.has(res.idx) || this.highlightRes?.has(res.idx)) atomMode[i] = 2; continue; }
      atomMode[i] = repCode[rep];
    }
    this.atomMode = atomMode;
    this.buildAtoms(); this.buildBonds();
    if (!st.isSmall && (rep === 'cartoon' || rep === 'cartoon+pocket')) this.buildCartoon();
  }

  buildAtoms() {
    const st = this.st, idx = [];
    for (let i = 0; i < st.n; i++) if (this.atomMode[i] && this.atomMode[i] !== 4) idx.push(i);
    this.sphereIdx = Int32Array.from(idx);
    if (!idx.length) { this.atomsMesh = null; return; }
    const mesh = new THREE.InstancedMesh(idx.length > 6000 ? SPHERE_LO : SPHERE, this.material, idx.length);
    mesh.name = 'atoms';
    this.atomsMesh = mesh;
    this.updateAtoms();
    for (let k = 0; k < idx.length; k++) mesh.setColorAt(k, _c.setHex(this.colors[idx[k]]));
    this.group.add(mesh);
  }

  atomRadius(i) {
    const m = this.atomMode[i], e = this.st.element[i];
    if (m === 3) return vdwRadius(e);
    if (m === 2) return 0.16;
    return e === 'H' ? 0.16 : 0.3;
  }

  updateAtoms() {
    const mesh = this.atomsMesh; if (!mesh) return;
    const P = this.st.pos, idx = this.sphereIdx;
    for (let k = 0; k < idx.length; k++) {
      const i = idx[k], r = this.atomRadius(i);
      _m.makeScale(r, r, r).setPosition(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]);
      mesh.setMatrixAt(k, _m);
    }
    mesh.instanceMatrix.needsUpdate = true;
    mesh.computeBoundingSphere();
  }

  buildBonds() {
    const st = this.st, B = st.bonds, list = [];
    for (let k = 0; k < B.length; k += 3) {
      const i = B[k], j = B[k + 1], mi = this.atomMode[i], mj = this.atomMode[j];
      if (!mi || !mj || mi === 3 || mj === 3) continue;
      const ord = st.isSmall ? B[k + 2] : 1;
      for (let o = 0; o < ord; o++) list.push(i, j, ord, o);
    }
    this.bondList = Int32Array.from(list);
    const nb = list.length / 4;
    if (!nb) { this.bondsMesh = null; return; }
    const lines = this.style.rep === 'lines' && !st.isSmall;
    const mesh = new THREE.InstancedMesh(CYL, this.material, nb * 2);
    mesh.name = 'bonds'; this.bondsMesh = mesh; this.lineBonds = lines;
    this.updateBonds();
    for (let b = 0; b < nb; b++) {
      mesh.setColorAt(b * 2, _c.setHex(this.colors[this.bondList[b * 4]]));
      mesh.setColorAt(b * 2 + 1, _c.setHex(this.colors[this.bondList[b * 4 + 1]]));
    }
    this.group.add(mesh);
  }

  bondOffset(i, j, out) {
    // Perpendicular in the plane of a neighbouring atom, for drawing double/triple bonds.
    const st = this.st, P = st.pos;
    _a.set(P[j * 3] - P[i * 3], P[j * 3 + 1] - P[i * 3 + 1], P[j * 3 + 2] - P[i * 3 + 2]).normalize();
    const ref = st.nbr[i].find((k) => k !== j && st.element[k] !== 'H') ?? st.nbr[j].find((k) => k !== i && st.element[k] !== 'H');
    if (ref !== undefined) _b.set(P[ref * 3] - P[i * 3], P[ref * 3 + 1] - P[i * 3 + 1], P[ref * 3 + 2] - P[i * 3 + 2]);
    else _b.set(0, 0, 1);
    out.copy(_b).addScaledVector(_a, -_b.dot(_a));
    if (out.lengthSq() < 1e-6) out.set(1, 0, 0).addScaledVector(_a, -_a.x);
    return out.normalize();
  }

  updateBonds() {
    const mesh = this.bondsMesh; if (!mesh) return;
    const P = this.st.pos, L = this.bondList, nb = L.length / 4;
    const off = new THREE.Vector3();
    for (let b = 0; b < nb; b++) {
      const i = L[b * 4], j = L[b * 4 + 1], ord = L[b * 4 + 2], o = L[b * 4 + 3];
      const small = this.st.isSmall;
      let r = this.atomMode[i] === 2 || this.atomMode[j] === 2 ? 0.16 : 0.12;
      if (this.lineBonds) r = 0.05;
      _a.set(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]); _b.set(P[j * 3], P[j * 3 + 1], P[j * 3 + 2]);
      if (small && ord > 1) {
        r = 0.075;
        this.bondOffset(i, j, off);
        const shift = ord === 2 ? (o === 0 ? -0.09 : 0.09) : (o - 1) * 0.14;
        _a.set(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]).addScaledVector(off, shift);
        _b.set(P[j * 3], P[j * 3 + 1], P[j * 3 + 2]).addScaledVector(off, shift);
      }
      const mid = _v.copy(_a).add(_b).multiplyScalar(0.5);
      for (let h = 0; h < 2; h++) {
        const from = h === 0 ? _a : _b;
        const dir = _s.copy(mid).sub(from); const len = dir.length();
        _q.setFromUnitVectors(UP, dir.divideScalar(len || 1));
        _m.compose(from.clone().addScaledVector(dir, len / 2), _q, new THREE.Vector3(r, len, r));
        mesh.setMatrixAt(b * 2 + h, _m);
      }
    }
    mesh.instanceMatrix.needsUpdate = true;
    mesh.computeBoundingSphere();
  }

  // Cartoon: smooth tube through CA atoms with per-residue radius (helix fat, strand medium, coil thin).
  buildCartoon() {
    const st = this.st, P = st.pos;
    const segs = []; let cur = [];
    for (const r of st.residues) {
      if (r.ca < 0) continue;
      const prev = cur[cur.length - 1];
      // Chain change or a CA-CA gap (missing residues) starts a new tube segment.
      if (prev && (prev.chain !== r.chain || dist(P, prev.ca, r.ca) > 4.3)) { if (cur.length > 1) segs.push(cur); cur = []; }
      cur.push(r);
    }
    if (cur.length > 1) segs.push(cur);
    this.cartoonSegs = segs;
    this.cartoonMeshes = [];
    for (const seg of segs) {
      const geo = tubeGeometry(seg, P, this.st, this.colors);
      const mesh = new THREE.Mesh(geo, this.cartoonMat);
      mesh.name = 'cartoon'; mesh.userData.seg = seg;
      this.group.add(mesh); this.cartoonMeshes.push(mesh);
    }
  }

  updateCartoon() {
    if (!this.cartoonMeshes) return;
    for (const mesh of this.cartoonMeshes) {
      const g = tubeGeometry(mesh.userData.seg, this.st.pos, this.st, this.colors);
      mesh.geometry.dispose(); mesh.geometry = g;
    }
  }

  // Called after st.pos changes (MD, docking moves).
  refresh({ cartoon = true } = {}) {
    this.updateAtoms(); this.updateBonds();
    if (cartoon && this.cartoonMeshes && this.cartoonMeshes.length && this.cartoonMeshes[0].parent) this.updateCartoon();
  }

  recolor() {
    this.colors = this.atomColors();
    if (this.atomsMesh) { for (let k = 0; k < this.sphereIdx.length; k++) this.atomsMesh.setColorAt(k, _c.setHex(this.colors[this.sphereIdx[k]])); this.atomsMesh.instanceColor.needsUpdate = true; }
    if (this.bondsMesh) { const L = this.bondList; for (let b = 0; b < L.length / 4; b++) { this.bondsMesh.setColorAt(b * 2, _c.setHex(this.colors[L[b * 4]])); this.bondsMesh.setColorAt(b * 2 + 1, _c.setHex(this.colors[L[b * 4 + 1]])); } this.bondsMesh.instanceColor.needsUpdate = true; }
    if (this.cartoonMeshes) this.updateCartoon();
  }

  // Map a raycast hit back to an atom index.
  hitToAtom(hit) {
    if (hit.object === this.atomsMesh) return this.sphereIdx[hit.instanceId];
    if (hit.object === this.bondsMesh) { const b = Math.floor(hit.instanceId / 2); return this.bondList[b * 4 + (hit.instanceId % 2)]; }
    if (hit.object.name === 'cartoon') {
      const resAttr = hit.object.geometry.getAttribute('residx');
      const vi = hit.face ? hit.face.a : 0;
      const ridx = resAttr.getX(vi);
      return this.st.residues[ridx].ca;
    }
    return -1;
  }

  pickables() { return this.group.children; }
}

function dist(P, i, j) { return Math.hypot(P[i * 3] - P[j * 3], P[i * 3 + 1] - P[j * 3 + 1], P[i * 3 + 2] - P[j * 3 + 2]); }

const RADIUS = [0.28, 0.85, 0.55]; // coil, helix, strand
const WIDTH = [1, 1, 2.2]; // strands drawn as flattened ribbons (ellipse)

function tubeGeometry(seg, P, st, colors) {
  const pts = seg.map((r) => new THREE.Vector3(P[r.ca * 3], P[r.ca * 3 + 1], P[r.ca * 3 + 2]));
  const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
  const per = 5, N = (pts.length - 1) * per + 1, radial = 8;
  const pos = new Float32Array(N * radial * 3), nor = new Float32Array(N * radial * 3), col = new Float32Array(N * radial * 3), rid = new Float32Array(N * radial);
  const frames = curve.computeFrenetFrames(N - 1, false);
  const p = new THREE.Vector3(), n = new THREE.Vector3(), c = new THREE.Color();
  for (let s = 0; s < N; s++) {
    const t = s / (N - 1);
    curve.getPointAt(t, p);
    const fi = Math.min(seg.length - 1, Math.round(t * (seg.length - 1)));
    const res = seg[fi], ss = st.ss[res.idx];
    // Smoothly blend radius near SS boundaries.
    const r = RADIUS[ss], w = WIDTH[ss];
    c.setHex(colors[res.ca]);
    const N0 = frames.normals[s], B0 = frames.binormals[s];
    for (let k = 0; k < radial; k++) {
      const ang = (k / radial) * Math.PI * 2, cs = Math.cos(ang), sn = Math.sin(ang);
      n.set(0, 0, 0).addScaledVector(N0, cs * w).addScaledVector(B0, sn);
      const o = (s * radial + k) * 3;
      pos[o] = p.x + n.x * r * (ss === 2 ? 0.45 : 1); pos[o + 1] = p.y + n.y * r * (ss === 2 ? 0.45 : 1); pos[o + 2] = p.z + n.z * r * (ss === 2 ? 0.45 : 1);
      n.normalize(); nor[o] = n.x; nor[o + 1] = n.y; nor[o + 2] = n.z;
      col[o] = c.r; col[o + 1] = c.g; col[o + 2] = c.b; rid[s * radial + k] = res.idx;
    }
  }
  const index = [];
  for (let s = 0; s < N - 1; s++) for (let k = 0; k < radial; k++) {
    const a = s * radial + k, b = s * radial + (k + 1) % radial, c2 = (s + 1) * radial + k, d = (s + 1) * radial + (k + 1) % radial;
    index.push(a, c2, b, b, c2, d);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  g.setAttribute('residx', new THREE.BufferAttribute(rid, 1));
  g.setIndex(index);
  g.computeBoundingSphere();
  return g;
}

// ---------------------------------------------------------------- labels + measurement helpers
export function textSprite(text, { color = '#e8f1ff', bg = 'rgba(12,18,28,0.82)', size = 44 } = {}) {
  const cv = document.createElement('canvas'); const ctx = cv.getContext('2d');
  ctx.font = `600 ${size}px system-ui, sans-serif`;
  const w = Math.ceil(ctx.measureText(text).width) + 28, h = size + 22;
  cv.width = w; cv.height = h;
  ctx.font = `600 ${size}px system-ui, sans-serif`;
  ctx.fillStyle = bg; roundRect(ctx, 0, 0, w, h, 12); ctx.fill();
  ctx.fillStyle = color; ctx.textBaseline = 'middle'; ctx.fillText(text, 14, h / 2 + 2);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const spr = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true }));
  spr.renderOrder = 10;
  spr.scale.set(w / h * 1.2, 1.2, 1);
  return spr;
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}

export function dashedLine(a, b, color = 0xffe066) {
  const g = new THREE.BufferGeometry().setFromPoints([a, b]);
  const l = new THREE.Line(g, new THREE.LineDashedMaterial({ color, dashSize: 0.25, gapSize: 0.15, depthTest: false }));
  l.computeLineDistances(); l.renderOrder = 9;
  return l;
}
