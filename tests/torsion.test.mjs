// Offline checks for js/torsion.js on synthetic geometry.
//
// The first group is pure geometry: a torsion rotation must change one dihedral and leave every bond length
// and every bond angle alone. That is checkable exactly, with no reference to the scoring function. The
// second group checks the search discipline the module claims. Nothing here says anything about the 4-case
// re-docking benchmark, which needs the network and has not been re-measured.
//
//   node --test tests/torsion.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { Structure } from '../js/structure.js';
import { ProteinGrid, vinaScore, rotatableBonds } from '../js/dock.js';
import { torsionAxis, rotateTorsion, refineTorsions, refineFlexible, refineAllFlexible } from '../js/torsion.js';
import { refinePose } from '../js/refine.js';

// A zig-zag carbon chain, built with real sp3 geometry so bond angles are meaningful: 1.53 A bonds at
// 112 degrees, laid out in the xy plane. Six carbons give three rotatable bonds.
function chainLigand(n = 6) {
  const bond = 1.53, theta = (112 * Math.PI) / 180;
  const atoms = [];
  let x = 0, y = 0, dir = 1;
  for (let i = 0; i < n; i++) {
    atoms.push({ x, y, z: 0, element: 'C', name: `C${i + 1}`, het: 1 });
    const bend = (Math.PI - theta) / 2;
    x += bond * Math.cos(bend);
    y += dir * bond * Math.sin(bend);
    dir = -dir;
  }
  const bonds = [];
  for (let i = 0; i < n - 1; i++) bonds.push(i, i + 1, 1);
  return new Structure(atoms, { bonds, kind: 'small', name: 'chain' });
}

// A straight groove of carbons along x: an extended chain lies in it, a folded one does not.
function grooveReceptor() {
  const atoms = [];
  let k = 0;
  for (let gx = -4; gx <= 10; gx += 2) {
    for (const gy of [-4.2, 4.2]) {
      atoms.push({ name: `CW${k}`, resName: 'ALA', chain: 'A', resSeq: ++k, x: gx, y: gy, z: 0, element: 'C', het: 0 });
      atoms.push({ name: `CB${k}`, resName: 'ALA', chain: 'A', resSeq: ++k, x: gx, y: gy * 0.45, z: -4.3, element: 'C', het: 0 });
    }
  }
  return new Structure(atoms, { name: 'groove' });
}

const dist = (c, i, j) => Math.hypot(c[i * 3] - c[j * 3], c[i * 3 + 1] - c[j * 3 + 1], c[i * 3 + 2] - c[j * 3 + 2]);

function angleAt(c, i, j, k) { // angle i-j-k in radians
  const v = [c[i * 3] - c[j * 3], c[i * 3 + 1] - c[j * 3 + 1], c[i * 3 + 2] - c[j * 3 + 2]];
  const w = [c[k * 3] - c[j * 3], c[k * 3 + 1] - c[j * 3 + 1], c[k * 3 + 2] - c[j * 3 + 2]];
  const dot = v[0] * w[0] + v[1] * w[1] + v[2] * w[2];
  return Math.acos(Math.max(-1, Math.min(1, dot / (Math.hypot(...v) * Math.hypot(...w)))));
}

function dihedral(c, i, j, k, l) {
  const sub = (p, q) => [c[p * 3] - c[q * 3], c[p * 3 + 1] - c[q * 3 + 1], c[p * 3 + 2] - c[q * 3 + 2]];
  const cross = (u, v) => [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
  const dot = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
  const b1 = sub(j, i), b2 = sub(k, j), b3 = sub(l, k);
  const n1 = cross(b1, b2), n2 = cross(b2, b3);
  const m = cross(n1, b2.map((q) => q / Math.hypot(...b2)));
  return Math.atan2(dot(m, n2), dot(n1, n2));
}

test('the chain gives the rotatable bonds the geometry implies', () => {
  const lig = chainLigand(6);
  const rot = rotatableBonds(lig);
  // C2-C3, C3-C4, C4-C5 qualify; the two terminal bonds do not, each having an atom with one heavy neighbour.
  assert.equal(rot.length, 3, `expected 3 rotatable bonds, got ${rot.length}`);
  for (const t of rot) {
    assert.ok(!t.moving.includes(t.a), 'the fixed hinge atom must not be in the moving set');
    assert.ok(t.moving.includes(t.b), 'the moving set is the side carrying atom b');
    assert.ok(t.moving.length <= lig.n / 2, 'the smaller side is the one that moves');
  }
});

test('a torsion rotation preserves every bond length and bond angle', () => {
  const lig = chainLigand(6);
  const rot = rotatableBonds(lig);
  const before = Float32Array.from(lig.pos);
  const after = Float32Array.from(lig.pos);
  assert.ok(rotateTorsion(after, rot[1], 0.9));

  for (let k = 0; k < lig.bonds.length; k += 3) {
    const i = lig.bonds[k], j = lig.bonds[k + 1];
    assert.ok(Math.abs(dist(before, i, j) - dist(after, i, j)) < 1e-4,
      `bond ${i}-${j} changed length by ${(dist(after, i, j) - dist(before, i, j)).toFixed(5)} A`);
  }
  for (let j = 1; j < lig.n - 1; j++) {
    const d = Math.abs(angleAt(before, j - 1, j, j + 1) - angleAt(after, j - 1, j, j + 1));
    assert.ok(d < 1e-4, `bond angle at atom ${j} changed by ${((d * 180) / Math.PI).toFixed(4)} degrees`);
  }
});

test('a torsion rotation changes its own dihedral by the angle asked for, and no other', () => {
  const lig = chainLigand(6);
  const rot = rotatableBonds(lig);
  const t = rot.find((r) => (r.a === 2 && r.b === 3) || (r.a === 3 && r.b === 2));
  assert.ok(t, 'the central C3-C4 bond should be rotatable');

  const before = Float32Array.from(lig.pos);
  const after = Float32Array.from(before);
  rotateTorsion(after, t, 0.5);

  // The dihedral spanning the rotated bond moves by 0.5 rad; the two flanking it do not move at all.
  const spanning = Math.abs(dihedral(after, 1, 2, 3, 4) - dihedral(before, 1, 2, 3, 4));
  assert.ok(Math.abs(spanning - 0.5) < 1e-3, `spanning dihedral moved ${spanning.toFixed(4)} rad, expected 0.5`);
  for (const [i, j, k, l] of [[0, 1, 2, 3], [2, 3, 4, 5]]) {
    const d = Math.abs(dihedral(after, i, j, k, l) - dihedral(before, i, j, k, l));
    assert.ok(d < 1e-3, `dihedral ${i}-${j}-${k}-${l} should not have moved, but moved ${d.toFixed(4)} rad`);
  }
});

test('the hinge atoms and the fixed side do not move', () => {
  const lig = chainLigand(6);
  const t = rotatableBonds(lig)[1];
  const before = Float32Array.from(lig.pos);
  const after = Float32Array.from(before);
  rotateTorsion(after, t, 1.2);
  const moving = new Set(t.moving);
  for (let i = 0; i < lig.n; i++) {
    const moved = dist0(before, after, i);
    if (i === t.a || i === t.b) assert.ok(moved < 1e-4, `hinge atom ${i} moved ${moved.toFixed(5)} A`);
    else if (!moving.has(i)) assert.ok(moved < 1e-4, `fixed-side atom ${i} moved ${moved.toFixed(5)} A`);
  }
  function dist0(p, q, i) {
    return Math.hypot(p[i * 3] - q[i * 3], p[i * 3 + 1] - q[i * 3 + 1], p[i * 3 + 2] - q[i * 3 + 2]);
  }
});

test('a rotation and its inverse return the original coordinates', () => {
  const lig = chainLigand(6);
  const t = rotatableBonds(lig)[0];
  const before = Float32Array.from(lig.pos);
  const after = Float32Array.from(before);
  rotateTorsion(after, t, 0.7);
  rotateTorsion(after, t, -0.7);
  for (let i = 0; i < before.length; i++) {
    assert.ok(Math.abs(before[i] - after[i]) < 1e-4, `coordinate ${i} did not return: ${before[i]} vs ${after[i]}`);
  }
});

test('a bond with coincident atoms is skipped rather than dividing by zero', () => {
  const lig = chainLigand(6);
  const t = rotatableBonds(lig)[1];
  const coords = Float32Array.from(lig.pos);
  for (let d = 0; d < 3; d++) coords[t.b * 3 + d] = coords[t.a * 3 + d];
  assert.equal(torsionAxis(coords, t), null);
  assert.equal(rotateTorsion(coords, t, 0.5), false);
  assert.ok(coords.every(Number.isFinite), 'coordinates must not become NaN');
});

test('torsional refinement never returns a worse pose than it was given', () => {
  const grid = new ProteinGrid(grooveReceptor(), 4);
  const lig = chainLigand(6);
  for (const bend of [0, 0.6, -1.1, 2.0]) {
    const start = Float32Array.from(lig.pos);
    for (const t of rotatableBonds(lig)) rotateTorsion(start, t, bend);
    const before = vinaScore(grid, lig, start);
    const out = refineTorsions(grid, lig, start);
    assert.ok(out.score <= before + 1e-9, `score worsened from ${before} to ${out.score}`);
    assert.ok(out.improved >= 0, 'the reported improvement must never be negative');
  }
});

test('torsional refinement leaves bond lengths intact, pose after pose', () => {
  const grid = new ProteinGrid(grooveReceptor(), 4);
  const lig = chainLigand(6);
  const start = Float32Array.from(lig.pos);
  for (const t of rotatableBonds(lig)) rotateTorsion(start, t, 1.4);
  const out = refineTorsions(grid, lig, start);
  for (let k = 0; k < lig.bonds.length; k += 3) {
    const i = lig.bonds[k], j = lig.bonds[k + 1];
    assert.ok(Math.abs(dist(out.coords, i, j) - 1.53) < 1e-3,
      `bond ${i}-${j} is ${dist(out.coords, i, j).toFixed(4)} A after refinement, not 1.53`);
  }
});

test('refinement is deterministic and does not mutate its input', () => {
  const grid = new ProteinGrid(grooveReceptor(), 4);
  const lig = chainLigand(6);
  const start = Float32Array.from(lig.pos);
  for (const t of rotatableBonds(lig)) rotateTorsion(start, t, 0.8);
  const copy = Float32Array.from(start);
  const a = refineTorsions(grid, lig, start);
  const b = refineTorsions(grid, lig, start);
  assert.deepEqual(Array.from(start), Array.from(copy), 'refineTorsions must not mutate its argument');
  assert.equal(a.score, b.score);
  assert.deepEqual(Array.from(a.coords), Array.from(b.coords));
});

test('the evaluation budget is respected, and a finer step never scores worse', () => {
  const grid = new ProteinGrid(grooveReceptor(), 4);
  const lig = chainLigand(6);
  const start = Float32Array.from(lig.pos);
  for (const t of rotatableBonds(lig)) rotateTorsion(start, t, 1.0);
  const capped = refineTorsions(grid, lig, start, { maxEvaluations: 30 });
  assert.ok(capped.evaluations <= 31, `used ${capped.evaluations} evaluations against a budget of 30`);
  const coarse = refineTorsions(grid, lig, start, { minAngle: 0.3 });
  const fine = refineTorsions(grid, lig, start, { minAngle: 0.01 });
  assert.ok(fine.score <= coarse.score + 1e-9, 'a finer angular search should not score worse');
});

test('a rigid ligand with no rotatable bonds is returned unchanged', () => {
  const grid = new ProteinGrid(grooveReceptor(), 4);
  const lig = chainLigand(3); // three atoms: no bond has two heavy neighbours on both sides
  assert.equal(rotatableBonds(lig).length, 0);
  const start = Float32Array.from(lig.pos);
  const out = refineTorsions(grid, lig, start);
  assert.deepEqual(Array.from(out.coords), Array.from(start));
  assert.equal(out.improved, 0);
  assert.equal(out.evaluations, 1, 'a rigid ligand should cost exactly one scoring call');
});

test('flexible refinement is at least as good as rigid-body refinement alone', () => {
  const grid = new ProteinGrid(grooveReceptor(), 4);
  const lig = chainLigand(6);
  const start = Float32Array.from(lig.pos);
  for (const t of rotatableBonds(lig)) rotateTorsion(start, t, 1.3);
  const rigidOnly = refinePose(grid, lig, start);
  const flex = refineFlexible(grid, lig, start);
  assert.ok(flex.score <= rigidOnly.score + 1e-9,
    `flexible ${flex.score.toFixed(3)} should not be worse than rigid ${rigidOnly.score.toFixed(3)}`);
  assert.ok(flex.passes >= 1 && flex.passes <= 4, `passes out of range: ${flex.passes}`);
  assert.equal(flex.torsions, 3);
});

test('flexible refinement stops once a full pass stops helping', () => {
  const grid = new ProteinGrid(grooveReceptor(), 4);
  const lig = chainLigand(6);
  // Starting from a pose already refined, a further pass should find nothing and stop on the first one.
  const settled = refineFlexible(grid, lig, Float32Array.from(lig.pos), { maxPasses: 4 });
  const again = refineFlexible(grid, lig, settled.coords, { maxPasses: 4 });
  assert.equal(again.passes, 1, `a settled pose should stop after one pass, took ${again.passes}`);
  assert.ok(again.improved <= 1e-3, `a settled pose should barely improve, gained ${again.improved}`);
});

test('refineAllFlexible re-sorts and keeps a gain record for every pose', () => {
  const grid = new ProteinGrid(grooveReceptor(), 4);
  const lig = chainLigand(6);
  const bend = (k) => {
    const c = Float32Array.from(lig.pos);
    for (const t of rotatableBonds(lig)) rotateTorsion(c, t, k);
    return { coords: c, score: vinaScore(grid, lig, c) };
  };
  const refined = refineAllFlexible(grid, lig, [bend(1.5), bend(0.2), bend(-0.9)]);
  assert.equal(refined.length, 3);
  for (let i = 1; i < refined.length; i++) {
    assert.ok(refined[i - 1].score <= refined[i].score, 'output must be sorted best first');
  }
  for (const [i, p] of refined.entries()) {
    assert.ok(typeof p.refinedBy === 'number' && p.refinedBy >= 0, `pose ${i} lost its gain record`);
    assert.ok(p.passes >= 1, `pose ${i} recorded no passes`);
  }
});
