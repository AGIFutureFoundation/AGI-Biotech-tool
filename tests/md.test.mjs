// Offline checks for the dynamics engine in js/md.js, and for the exact planarity restraint in
// js/planarity.js.
//
// A force field has one property worth more than all the others: the force must be the negative gradient
// of the energy. If it is not, a minimiser can be steered the wrong way and dynamics does no definite
// work, and nothing in the output says so — the molecule just behaves slightly oddly in a way that reads
// as "physics is hard". So the centrepiece here is a central finite-difference gradient check, run in
// double precision and at three step sizes so that second-order convergence is visible rather than assumed.
//
// Everything is synthetic: an alkane chain whose geometry is built from real sp3 angles, an sp2 centre with
// three substituents, and a carbon ring standing in for a receptor. No network, no browser, no server.
//
//   node --test tests/md.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { Structure } from '../js/structure.js';
import { buildLigandFF, ligandForces, minimize, setFourteenRef, MDEngine } from '../js/md.js';
import { planarityForce, planarityForces, outOfPlane } from '../js/planarity.js';
import { readFileSync } from 'node:fs';

// --- fixtures -------------------------------------------------------------------------------------------

// A zig-zag alkane: 1.53 A bonds at 112 degrees. All sp3, all single bonds, so no planarity and no 1-4
// terms — the clean case for a gradient check of bonds, angles and non-bonded repulsion.
function chain(n = 5, bond = 1.53) {
  const atoms = [];
  let x = 0, y = 0, dir = 1;
  const bend = (Math.PI - (112 * Math.PI) / 180) / 2;
  for (let i = 0; i < n; i++) {
    atoms.push({ x, y, z: 0, element: 'C', name: `C${i + 1}`, het: 1 });
    x += bond * Math.cos(bend); y += dir * bond * Math.sin(bend); dir = -dir;
  }
  const bonds = [];
  for (let i = 0; i < n - 1; i++) bonds.push(i, i + 1, 1);
  return new Structure(atoms, { bonds, kind: 'small', name: 'chain' });
}

// An sp2 centre: C1=C2, with C3 and C4 on C1. Atom 0 is the sp2 centre with three neighbours.
function sp2Centre() {
  const atoms = [
    { x: 0, y: 0, z: 0, element: 'C', name: 'C1', het: 1 },
    { x: 1.33, y: 0, z: 0, element: 'C', name: 'C2', het: 1 },
    { x: -0.77, y: 1.2, z: 0, element: 'C', name: 'C3', het: 1 },
    { x: -0.77, y: -1.2, z: 0, element: 'C', name: 'C4', het: 1 },
    { x: 2.1, y: 1.2, z: 0, element: 'C', name: 'C5', het: 1 },
  ];
  return new Structure(atoms, { bonds: [0, 1, 2, 0, 2, 1, 0, 3, 1, 1, 4, 1], kind: 'small', name: 'sp2' });
}

function ringReceptor(R = 7, n = 14) {
  const atoms = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    atoms.push({ name: 'CA', resName: 'ALA', chain: 'A', resSeq: i + 1, element: 'C', het: 0,
      x: R * Math.cos(a), y: R * Math.sin(a), z: 0 });
  }
  return new Structure(atoms, { name: 'ring' });
}

function probeLigand() {
  return new Structure([
    { x: 0, y: 0, z: 0, element: 'C', name: 'C1', het: 1 },
    { x: 1.5, y: 0, z: 0, element: 'C', name: 'C2', het: 1 },
    { x: -1.5, y: 0, z: 0, element: 'C', name: 'C3', het: 1 },
  ], { bonds: [0, 1, 1, 0, 2, 1], kind: 'small', name: 'probe' });
}

// --- gradient machinery ---------------------------------------------------------------------------------

// Worst relative disagreement between the analytic force and a central finite difference of the energy.
// Double precision throughout: a Float32Array would floor this around 1e-3 and hide a real error.
function worstGradientError(energyAndForce, coords, h) {
  const P = Float64Array.from(coords);
  const F = new Float64Array(P.length);
  energyAndForce(P, F);
  let worst = 0;
  for (let k = 0; k < P.length; k++) {
    const G = new Float64Array(P.length);
    const save = P[k];
    P[k] = save + h; const Ep = energyAndForce(P, G);
    P[k] = save - h; G.fill(0); const Em = energyAndForce(P, G);
    P[k] = save;
    const numeric = -(Ep - Em) / (2 * h);
    worst = Math.max(worst, Math.abs(numeric - F[k]) / (Math.abs(F[k]) + 1));
  }
  return worst;
}

const netForce = (F, n) => {
  const s = [0, 0, 0];
  for (let i = 0; i < n; i++) for (let d = 0; d < 3; d++) s[d] += F[i * 3 + d];
  return s;
};

const displaced = (st, scale = 1) => Array.from(st.pos).map((v, i) =>
  v + scale * (i % 3 === 0 ? 0.11 : -0.07) * ((i % 5) - 2));

// --- the force field it builds --------------------------------------------------------------------------

test('the force field has one term per piece of topology', () => {
  const st = chain(5);
  const ff = buildLigandFF(st);
  assert.equal(ff.n, 5);
  assert.equal(ff.bonds.length / 4, 4, 'one bond term per bond');
  assert.equal(ff.angles.length / 4, 3, 'one angle term per neighbour pair around a centre');
  assert.equal(ff.planar.length / 4, 0, 'an all-sp3 chain has no planarity terms');
  assert.equal(ff.fourteen.length / 2, 0, 'no double or aromatic bonds, so no 1-4 restraints');
});

test('non-bonded pairs are only atoms three or more bonds apart', () => {
  const ff = buildLigandFF(chain(5));
  const got = [];
  for (let k = 0; k < ff.pairs.length; k += 2) got.push([ff.pairs[k], ff.pairs[k + 1]]);
  assert.deepEqual(got, [[0, 3], [0, 4], [1, 4]],
    'a 5-chain has exactly these 1-4 and 1-5 pairs; a 1-2 or 1-3 pair here would be double-counted against a bond or angle term');
});

test('bond rest lengths shorten with bond order', () => {
  const single = buildLigandFF(chain(2)).bonds[2];
  const mk = (order) => new Structure([
    { x: 0, y: 0, z: 0, element: 'C', name: 'C1', het: 1 },
    { x: 1.4, y: 0, z: 0, element: 'C', name: 'C2', het: 1 },
  ], { bonds: [0, 1, order], kind: 'small', name: `o${order}` });
  const double = buildLigandFF(mk(2)).bonds[2];
  const triple = buildLigandFF(mk(3)).bonds[2];
  assert.ok(triple < double && double < single,
    `expected triple < double < single, got ${triple.toFixed(3)} / ${double.toFixed(3)} / ${single.toFixed(3)}`);
  assert.ok(Math.abs(single - 1.52) < 0.05, `a C-C single bond should rest near 1.52 A, got ${single.toFixed(3)}`);
});

test('the 1-3 restraint distance follows the law of cosines at the sp3 angle', () => {
  const ff = buildLigandFF(chain(3));
  const r = ff.bonds[2]; // both bonds share a rest length
  const expected = Math.sqrt(2 * r * r * (1 - Math.cos((109.5 * Math.PI) / 180)));
  assert.ok(Math.abs(ff.angles[2] - expected) < 1e-3,
    `1-3 distance ${ff.angles[2].toFixed(4)} does not match the law of cosines value ${expected.toFixed(4)}`);
});

test('an sp2 centre with three substituents gets a planarity term; an sp3 one does not', () => {
  assert.equal(buildLigandFF(sp2Centre()).planar.length / 4, 1);
  assert.equal(buildLigandFF(chain(5)).planar.length / 4, 0);
});

// --- the forces it produces -----------------------------------------------------------------------------

test('energy is zero at the reference geometry and a stretched bond costs k dr squared', () => {
  const st = chain(2);
  const ff = buildLigandFF(st);
  const r0 = ff.bonds[2], k = ff.bonds[3];
  const at = (r) => {
    const P = Float64Array.from([0, 0, 0, r, 0, 0]);
    return ligandForces(ff, P, new Float64Array(6));
  };
  assert.ok(at(r0) < 1e-9, `a bond at its rest length should cost nothing, got ${at(r0)}`);
  for (const dr of [0.1, -0.1, 0.25]) {
    assert.ok(Math.abs(at(r0 + dr) - k * dr * dr) < 1e-6,
      `a bond stretched by ${dr} should cost ${(k * dr * dr).toFixed(4)}, got ${at(r0 + dr).toFixed(4)}`);
  }
});

test('the forces obey Newton’s third law', () => {
  const st = chain(5);
  const ff = buildLigandFF(st);
  const P = Float64Array.from(displaced(st));
  const F = new Float64Array(P.length);
  ligandForces(ff, P, F);
  for (const [d, s] of netForce(F, ff.n).entries()) {
    assert.ok(Math.abs(s) < 1e-9, `net force on axis ${d} is ${s.toExponential(2)}, should be zero`);
  }
});

test('the force is the exact negative gradient of the energy, converging at second order', () => {
  const st = chain(5);
  const ff = buildLigandFF(st);
  const coords = displaced(st);
  const f = (P, F) => ligandForces(ff, P, F);
  const e3 = worstGradientError(f, coords, 1e-3);
  const e4 = worstGradientError(f, coords, 1e-4);
  assert.ok(e4 < 1e-6, `gradient error at h=1e-4 is ${e4.toExponential(3)}, expected under 1e-6`);
  // Halving h by ten should cut a second-order error by about a hundred. Allow a wide factor, because this
  // asserts the trend, not the constant.
  assert.ok(e3 / e4 > 20,
    `error should fall as h^2: ${e3.toExponential(2)} at 1e-3 vs ${e4.toExponential(2)} at 1e-4`);
});

test('non-bonded repulsion is silent beyond its cutoff and positive inside it', () => {
  const ff = buildLigandFF(chain(5));
  // Strip the bonded terms, so moving an atom changes the repulsion and nothing else. The first attempt at
  // this test moved a bonded atom and measured the bond term by mistake, which drowned the effect entirely.
  const pairsOnly = { ...ff, bonds: [], angles: [], planar: [], fourteen: [], fourteenRef: null,
    pairs: [0, 1] };
  const energyAt = (sep) => {
    const P = Float64Array.from([0, 0, 0, sep, 0, 0]);
    return ligandForces(pairsOnly, P, new Float64Array(6), { repel: 3.1, krep: 4 });
  };
  assert.equal(energyAt(3.1), 0, 'exactly at the cutoff the pair costs nothing');
  assert.equal(energyAt(4.0), 0, 'beyond the cutoff the term is silent');
  let last = 0;
  for (const sep of [3.0, 2.5, 2.0, 1.0]) {
    const E = energyAt(sep);
    assert.ok(E > last, `closing the pair to ${sep} A should cost more, got ${E.toFixed(4)} after ${last.toFixed(4)}`);
    last = E;
  }
  // The functional form is quadratic in the overlap: krep * (repel - r)^2.
  assert.ok(Math.abs(energyAt(2.1) - 4 * 1.0 ** 2) < 1e-6, `expected 4.0 at 1 A of overlap, got ${energyAt(2.1)}`);
  // And it pushes apart, not together.
  const F = new Float64Array(6);
  ligandForces(pairsOnly, Float64Array.from([0, 0, 0, 2.0, 0, 0]), F, { repel: 3.1, krep: 4 });
  assert.ok(F[0] < 0 && F[3] > 0, `repulsion must separate the pair, got forces ${F[0]} and ${F[3]}`);
});

// --- the minimiser --------------------------------------------------------------------------------------

test('minimisation lowers the energy and pulls bonds back toward their rest length', () => {
  const st = chain(5);
  const ff = buildLigandFF(st);
  const P = Float32Array.from(displaced(st, 1.5));
  const before = ligandForces(ff, Float64Array.from(P), new Float64Array(P.length));
  const after = minimize(P, (Q, F) => ligandForces(ff, Q, F), { steps: 600 });
  assert.ok(after < before, `energy should fall: ${before.toFixed(3)} -> ${after.toFixed(3)}`);
  const r0 = ff.bonds[2];
  for (let k = 0; k < ff.bonds.length; k += 4) {
    const i = ff.bonds[k], j = ff.bonds[k + 1];
    const r = Math.hypot(P[i * 3] - P[j * 3], P[i * 3 + 1] - P[j * 3 + 1], P[i * 3 + 2] - P[j * 3 + 2]);
    assert.ok(Math.abs(r - r0) < 0.1, `bond ${i}-${j} relaxed to ${r.toFixed(3)} A, rest length ${r0.toFixed(3)}`);
  }
  assert.ok(Array.from(P).every(Number.isFinite), 'minimisation must not produce NaN');
});

test('minimisation barely moves a geometry already at its minimum', () => {
  const st = chain(5);
  const ff = buildLigandFF(st);
  const settled = Float32Array.from(st.pos);
  minimize(settled, (Q, F) => ligandForces(ff, Q, F), { steps: 600 });
  const again = Float32Array.from(settled);
  minimize(again, (Q, F) => ligandForces(ff, Q, F), { steps: 600 });
  let worst = 0;
  for (let i = 0; i < settled.length; i++) worst = Math.max(worst, Math.abs(settled[i] - again[i]));
  assert.ok(worst < 0.05, `a settled geometry drifted by ${worst.toFixed(4)} A on a second pass`);
});

// --- the engine -----------------------------------------------------------------------------------------

test('dynamics stays stable: no NaN, bonds intact, a sane temperature', () => {
  const lig = probeLigand();
  const md = new MDEngine({ protein: ringReceptor(), ligand: lig, temperature: 300 });
  md.relax(200);
  md.step(400);
  assert.ok(Array.from(lig.pos).every(Number.isFinite), 'the trajectory must not blow up to NaN');
  for (const [i, j] of [[0, 1], [0, 2]]) {
    const r = Math.hypot(lig.pos[i * 3] - lig.pos[j * 3], lig.pos[i * 3 + 1] - lig.pos[j * 3 + 1],
      lig.pos[i * 3 + 2] - lig.pos[j * 3 + 2]);
    assert.ok(r > 1.2 && r < 2.0, `bond ${i}-${j} is ${r.toFixed(3)} A after 400 steps; the molecule came apart`);
  }
  const T = md.kineticTemperature();
  assert.ok(T > 0 && T < 3000, `kinetic temperature ${T.toFixed(1)} K is not physical for a 300 K bath`);
  assert.ok(md.ligandRMSD() >= 0 && Number.isFinite(md.ligandRMSD()), 'ligand RMSD must be a finite number');
});

test('relaxation lowers the energy it reports', () => {
  const md = new MDEngine({ protein: ringReceptor(), ligand: probeLigand(), temperature: 300 });
  const first = md.relax(200);
  const second = md.relax(200);
  assert.ok(Number.isFinite(first), `relax should report an energy, got ${first}`);
  assert.ok(second <= first + 1e-6, `a second relaxation should not raise the energy: ${first} -> ${second}`);
});

test('a frozen protein does not move at all', () => {
  const prot = ringReceptor();
  const md = new MDEngine({ protein: prot, ligand: probeLigand(), temperature: 300 });
  md.frozenProtein = true;
  const before = Float32Array.from(prot.pos);
  md.step(150);
  md.syncProtein();
  for (let i = 0; i < prot.pos.length; i++) {
    assert.equal(prot.pos[i], before[i], `frozen protein coordinate ${i} moved`);
  }
});

test('the steric guard pushes a clash apart, by no more than it is allowed to', () => {
  const prot = ringReceptor();
  const lig = probeLigand();
  const md = new MDEngine({ protein: prot, ligand: lig, temperature: 300 });
  md.buildNeighborList();
  // Put ligand atom 0 just inside a receptor atom — a real clash, not a coincidence.
  md.lp[0] = prot.pos[0] - 0.4; md.lp[1] = prot.pos[1]; md.lp[2] = prot.pos[2];
  const sepBefore = Math.hypot(md.lp[0] - prot.pos[0], md.lp[1] - prot.pos[1], md.lp[2] - prot.pos[2]);
  const was = [md.lp[0], md.lp[1], md.lp[2]];

  md.buildNeighborList();
  md.stericGuard(0.8, 0.25);

  const sepAfter = Math.hypot(md.lp[0] - prot.pos[0], md.lp[1] - prot.pos[1], md.lp[2] - prot.pos[2]);
  const shift = Math.hypot(md.lp[0] - was[0], md.lp[1] - was[1], md.lp[2] - was[2]);
  assert.ok(md.lastGuardFixes >= 1, `the guard should have reported a fix, got ${md.lastGuardFixes}`);
  assert.ok(sepAfter > sepBefore, `separation should grow: ${sepBefore.toFixed(3)} -> ${sepAfter.toFixed(3)}`);
  assert.ok(shift <= 0.25 + 1e-6, `the guard shifted an atom ${shift.toFixed(3)} A, over its 0.25 A limit`);
});

test('the steric guard leaves coincident atoms alone rather than dividing by zero', () => {
  const prot = ringReceptor();
  const lig = probeLigand();
  const md = new MDEngine({ protein: prot, ligand: lig, temperature: 300 });
  md.buildNeighborList();
  md.lp[0] = prot.pos[0]; md.lp[1] = prot.pos[1]; md.lp[2] = prot.pos[2];
  md.buildNeighborList();
  md.stericGuard(0.8, 0.25);
  assert.ok(Array.from(md.lp).every(Number.isFinite),
    'an exactly coincident pair has no push direction and must be skipped, not turned into NaN');
});

// --- the exact planarity restraint ----------------------------------------------------------------------

test('the exact restraint vanishes at planarity and grows as the centre leaves the plane', () => {
  const P = Float64Array.from([0, 0, 0, 1, 0, 0, 0, 1, 0, -1, -1, 0]); // c at origin, a/b/d in the z=0 plane
  assert.ok(Math.abs(outOfPlane(P, 0, 1, 2, 3)) < 1e-12, 'a coplanar centre is at zero displacement');
  assert.equal(planarityForce(P, new Float64Array(12), 0, 1, 2, 3, 40), 0);
  let last = 0;
  for (const z of [0.1, 0.3, 0.9]) {
    P[2] = z;
    const E = planarityForce(P, new Float64Array(12), 0, 1, 2, 3, 40);
    assert.ok(E > last, `energy should rise with displacement: ${z} A gave ${E.toFixed(4)}`);
    last = E;
  }
});

test('the restraint is the exact gradient at every pyramidalisation, not just small ones', () => {
  const st = sp2Centre();
  const ff = buildLigandFF(st);
  assert.equal(ff.planar.length / 4, 1);
  const f = (P, F) => planarityForces(ff, P, F, 40);
  // Pyramidalise the sp2 centre on its own, holding the substituents still. This is the geometry that
  // exposed the defect in the term this one replaced: distorting the substituent plane as well made the
  // errors cancel, and an earlier check read clean because of it. Small displacements are also the regime a
  // minimiser spends its time in, so they matter most.
  for (const z of [0.1, 0.3, 0.9, 1.6]) {
    const coords = Array.from(st.pos);
    coords[2] = z;
    const err = worstGradientError(f, coords, 1e-5);
    assert.ok(err < 1e-7, `gradient error ${err.toExponential(3)} at z=${z} A, expected under 1e-7`);
  }
});

test('the exact restraint conserves momentum, so it cannot push the molecule anywhere', () => {
  const P = Float64Array.from([0.2, 0.31, 0.4, 1.1, -0.2, 0.05, -0.3, 1.2, -0.1, -0.9, -1.1, 0.25]);
  const F = new Float64Array(12);
  planarityForce(P, F, 0, 1, 2, 3, 40);
  for (const [d, s] of netForce(F, 4).entries()) {
    assert.ok(Math.abs(s) < 1e-12, `net force on axis ${d} is ${s.toExponential(2)}, should be zero`);
  }
});

test('degenerate substituent geometry contributes nothing instead of dividing by zero', () => {
  // Three collinear substituents define no plane.
  const P = Float64Array.from([0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 0, 0]);
  const F = new Float64Array(12);
  assert.equal(planarityForce(P, F, 0, 1, 2, 3, 40), 0);
  assert.ok(Array.from(F).every((v) => v === 0), 'no plane means no force, not an infinite one');
  assert.equal(outOfPlane(P, 0, 1, 2, 3), 0);
});

test('ligandForces is gradient-exact on an sp2 molecule, planarity term included', () => {
  // This is the test that proves the swap landed. Until iteration 13 the planarity term in js/md.js held
  // its plane normal fixed, so the whole force field was about 19 percent off its own gradient wherever an
  // sp2 centre was pyramidalised. It now calls planarityForce, so the complete force field — bonds, angles,
  // 1-4 restraints, planarity and repulsion together — must pass the same check the simple terms do.
  const st = sp2Centre();
  const ff = buildLigandFF(st);
  assert.equal(ff.planar.length / 4, 1, 'this fixture must exercise the planarity term');
  assert.ok(ff.fourteen.length / 2 > 0, 'and the 1-4 restraints, since it has a double bond');
  setFourteenRef(ff, Float64Array.from(st.pos));

  const f = (P, F) => ligandForces(ff, P, F);
  for (const z of [0.1, 0.3, 0.9, 1.6]) {
    const coords = Array.from(st.pos);
    coords[2] = z; // pyramidalise the sp2 centre on its own: the geometry that exposed the defect
    const err = worstGradientError(f, coords, 1e-5);
    assert.ok(err < 1e-6,
      `ligandForces gradient error ${err.toExponential(3)} at z=${z} A; the planarity term is inexact again`);
  }
});

test('the whole force field still conserves momentum after the swap', () => {
  const st = sp2Centre();
  const ff = buildLigandFF(st);
  setFourteenRef(ff, Float64Array.from(st.pos));
  const P = Float64Array.from(displaced(st));
  const F = new Float64Array(P.length);
  ligandForces(ff, P, F);
  for (const [d, sum] of netForce(F, ff.n).entries()) {
    assert.ok(Math.abs(sum) < 1e-9, `net force on axis ${d} is ${sum.toExponential(2)}, should be zero`);
  }
});

test('the superseded in-place planarity implementation is gone, not merely unused', () => {
  // A second implementation left behind is a second implementation someone will call by mistake.
  const src = readFileSync(new URL('../js/md.js', import.meta.url), 'utf8');
  assert.ok(!/^function planarity\(/m.test(src), 'js/md.js still defines its own planarity function');
  assert.match(src, /planarityForce/, 'js/md.js should call the restraint from js/planarity.js');
});
