// Offline checks for js/refine.js on synthetic geometry.
//
// A real re-docking benchmark needs structures from the network. These tests instead build a small
// receptor and a ligand whose best placement is known by construction, displace it, and check that
// refinement moves back toward it. That proves the optimiser does what it claims; it says nothing about
// the four-complex benchmark, which has not been re-measured.
//
//   node --test tests/refine.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { Structure } from '../js/structure.js';
import { ProteinGrid, vinaScore, rmsd } from '../js/dock.js';
import { refinePose, refineAll } from '../js/refine.js';

// A shallow cup of carbon atoms: a ring in the z = 0 plane with a floor below it, so there is one
// obvious seat for a small ligand just above the origin.
function cupReceptor() {
  const atoms = [];
  const push = (x, y, z, name) => atoms.push({ name, resName: 'ALA', chain: 'A', resSeq: atoms.length + 1,
    x, y, z, element: 'C', het: 0 });
  for (let k = 0; k < 12; k++) {
    const a = (k / 12) * Math.PI * 2;
    push(5.2 * Math.cos(a), 5.2 * Math.sin(a), 0, `CR${k}`);
  }
  for (let gx = -4; gx <= 4; gx += 4) {
    for (let gy = -4; gy <= 4; gy += 4) push(gx, gy, -4.6, `CF${gx}${gy}`);
  }
  return new Structure(atoms, { name: 'cup' });
}

// A rigid three-atom ligand, small enough that its best seat is unambiguous.
function probeLigand() {
  const atoms = [
    { x: 0, y: 0, z: 0, element: 'C', name: 'C1', het: 1 },
    { x: 1.5, y: 0, z: 0, element: 'C', name: 'C2', het: 1 },
    { x: -1.5, y: 0, z: 0, element: 'C', name: 'C3', het: 1 },
  ];
  return new Structure(atoms, { bonds: [0, 1, 1, 0, 2, 1], kind: 'small', name: 'probe' });
}

function shifted(coords, dx, dy, dz) {
  const out = Float32Array.from(coords);
  for (let i = 0; i < out.length; i += 3) { out[i] += dx; out[i + 1] += dy; out[i + 2] += dz; }
  return out;
}

test('refinement never returns a worse pose than it was given', () => {
  const grid = new ProteinGrid(cupReceptor(), 4);
  const lig = probeLigand();
  for (const offset of [[0, 0, 0], [1.4, 0.6, 0.9], [-2.1, 1.2, -0.4], [0.3, -1.8, 2.2]]) {
    const start = shifted(lig.pos, ...offset);
    const before = vinaScore(grid, lig, start);
    const out = refinePose(grid, lig, start);
    assert.ok(out.score <= before + 1e-9, `score worsened from ${before} to ${out.score}`);
    assert.ok(out.improved >= 0, 'improvement must never be negative');
  }
});

test('the input coordinates are left untouched', () => {
  const grid = new ProteinGrid(cupReceptor(), 4);
  const lig = probeLigand();
  const start = shifted(lig.pos, 1.5, 1.0, 0.8);
  const copy = Float32Array.from(start);
  refinePose(grid, lig, start);
  assert.deepEqual(Array.from(start), Array.from(copy), 'refinePose must not mutate its argument');
});

test('a displaced pose moves back toward the seat the geometry defines', () => {
  const grid = new ProteinGrid(cupReceptor(), 4);
  const lig = probeLigand();
  // Find the seat by refining from the origin, then displace from there and check we return.
  const seat = refinePose(grid, lig, Float32Array.from(lig.pos), { step: 0.8 }).coords;
  const displaced = shifted(seat, 1.8, 1.4, 0.0);
  const before = rmsd(displaced, seat, lig.n);
  const after = rmsd(refinePose(grid, lig, displaced, { step: 0.8 }).coords, seat, lig.n);
  assert.ok(after < before, `refinement should close the gap: ${before.toFixed(2)} -> ${after.toFixed(2)}`);
});

test('refinement is deterministic: the same input gives the same output', () => {
  const grid = new ProteinGrid(cupReceptor(), 4);
  const lig = probeLigand();
  const start = shifted(lig.pos, 0.9, -1.1, 0.5);
  const a = refinePose(grid, lig, start);
  const b = refinePose(grid, lig, start);
  assert.equal(a.score, b.score);
  assert.deepEqual(Array.from(a.coords), Array.from(b.coords));
});

test('the evaluation budget is respected', () => {
  const grid = new ProteinGrid(cupReceptor(), 4);
  const lig = probeLigand();
  const out = refinePose(grid, lig, shifted(lig.pos, 2, 2, 2), { maxEvaluations: 40 });
  assert.ok(out.evaluations <= 41, `used ${out.evaluations} evaluations against a budget of 40`);
});

test('a finer minimum step searches harder and never does worse', () => {
  const grid = new ProteinGrid(cupReceptor(), 4);
  const lig = probeLigand();
  const start = shifted(lig.pos, 1.3, 0.7, 1.1);
  const coarse = refinePose(grid, lig, start, { minStep: 0.4 });
  const fine = refinePose(grid, lig, start, { minStep: 0.02 });
  assert.ok(fine.score <= coarse.score + 1e-9, 'a finer search should not score worse');
  assert.ok(fine.evaluations >= coarse.evaluations, 'a finer search should cost at least as much');
});

test('refineAll re-sorts, because refinement can change the ranking', () => {
  const grid = new ProteinGrid(cupReceptor(), 4);
  const lig = probeLigand();
  const make = (dx, dy, dz) => {
    const coords = shifted(lig.pos, dx, dy, dz);
    return { coords, score: vinaScore(grid, lig, coords) };
  };
  // Deliberately out of order: a pose that starts worse may refine into a better basin.
  const poses = [make(0.2, 0.1, 0.3), make(3.4, 2.2, 1.6), make(1.1, -0.8, 0.4)];
  const refined = refineAll(grid, lig, poses);
  assert.equal(refined.length, 3);
  for (let i = 1; i < refined.length; i++) {
    assert.ok(refined[i - 1].score <= refined[i].score, 'output must be sorted best first');
  }
  for (const [i, p] of refined.entries()) {
    assert.ok(typeof p.refinedBy === 'number' && p.refinedBy >= 0, `pose ${i} lost its improvement record`);
  }
});

test('rotation pivots on the ligand centroid, so a pure rotation does not drift', () => {
  const grid = new ProteinGrid(cupReceptor(), 4);
  const lig = probeLigand();
  const start = Float32Array.from(lig.pos);
  const out = refinePose(grid, lig, start, { step: 1e-6, minStep: 1e-7, angle: 0.3 });
  // With translation effectively disabled, the centroid must stay where it was.
  const c0 = [0, 1, 2].map((d) => [0, 1, 2].reduce((s, i) => s + start[i * 3 + d], 0) / 3);
  const c1 = [0, 1, 2].map((d) => [0, 1, 2].reduce((s, i) => s + out.coords[i * 3 + d], 0) / 3);
  for (let d = 0; d < 3; d++) {
    assert.ok(Math.abs(c0[d] - c1[d]) < 1e-3, `centroid drifted on axis ${d}`);
  }
});
