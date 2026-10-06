// Offline checks for pocket detection in js/dock.js, on synthetic geometry.
//
// findPockets is the first stage of the docking chain and the only one that had no JavaScript test. If it
// ranks a surface dent above a buried cavity, everything downstream — the search, the refinement, the
// scoring, the analysis — runs correctly against the wrong site, and nothing in the output says so. A wrong
// answer from a wrong pocket looks exactly like a wrong answer from a wrong score.
//
// So these build receptors where the cavity is known by construction: hollow spheres whose interior free
// volume follows from the radius and the probe margin, a solid ball with no interior at all, and a shallow
// dimple pressed into a plate. The expected numbers below were measured against the current implementation
// and are asserted with tolerances tight enough to fail on a real change — a centre to 0.5 A, a buriedness
// to 0.02 — rather than wide enough to pass on anything.
//
//   node --test tests/pockets.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { Structure } from '../js/structure.js';
import { findPockets } from '../js/dock.js';

let seq = 0;
const atom = (x, y, z, chain = 'A') => ({
  name: 'CB', resName: 'ALA', chain, resSeq: ++seq, element: 'C', het: 0, x, y, z,
});

// A Fibonacci sphere of carbons: evenly spread, so 300 points on a radius-9 shell sit about 2.9 A apart —
// closer than the 2.8 A occlusion radius, which makes the shell a sealed wall.
function shell(atoms, cx, R, n) {
  for (let i = 0; i < n; i++) {
    const y = 1 - (i / (n - 1)) * 2, r = Math.sqrt(Math.max(0, 1 - y * y));
    const th = Math.PI * (1 + Math.sqrt(5)) * i;
    atoms.push(atom(cx + R * Math.cos(th) * r, R * y, R * Math.sin(th) * r));
  }
  return atoms;
}

// A solid ball on a 2.4 A lattice: no interior free space for a pocket to live in.
function ball(atoms, cx, R, step = 2.4) {
  for (let x = -R; x <= R; x += step) {
    for (let y = -R; y <= R; y += step) {
      for (let z = -R; z <= R; z += step) {
        if (x * x + y * y + z * z <= R * R) atoms.push(atom(cx + x, y, z));
      }
    }
  }
  return atoms;
}

const hollow = (R = 9, n = 300) => { seq = 0; return new Structure(shell([], 0, R, n), { name: 'hollow' }); };
const norm = (v) => Math.hypot(v[0], v[1], v[2]);
const minAtomDistance = (st, c) => {
  let m = Infinity;
  for (let i = 0; i < st.n; i++) {
    m = Math.min(m, Math.hypot(st.pos[i * 3] - c[0], st.pos[i * 3 + 1] - c[1], st.pos[i * 3 + 2] - c[2]));
  }
  return m;
};

test('a hollow shell gives exactly one pocket, in the cavity, filling it', () => {
  const p = findPockets(hollow(), { spacing: 1.0 });
  assert.equal(p.length, 1, `expected 1 pocket in a single-cavity shell, got ${p.length}`);
  assert.ok(norm(p[0].center) < 0.5, `centre is ${norm(p[0].center).toFixed(2)} A off the cavity centre`);
  // A radius-9 shell occluded to 2.8 A leaves a free sphere of radius 6.2: about 1000 cubic A.
  assert.ok(p[0].volume > 900 && p[0].volume < 1200, `volume ${p[0].volume} is not the cavity's ~1000 A^3`);
  assert.ok(p[0].buriedness > 0.95, `a sealed cavity should be near-fully buried, got ${p[0].buriedness}`);
});

test('the pocket centre is inside the cavity, not sitting on the wall', () => {
  const st = hollow();
  const p = findPockets(st, { spacing: 1.0 });
  // The wall is 9 A out. A centre on or near it would be within a few A of an atom.
  const d = minAtomDistance(st, p[0].center);
  assert.ok(d > 6, `nearest receptor atom is ${d.toFixed(2)} A from the centre; expected over 6`);
  assert.ok(d < 10, `centre should be inside the shell, not outside it: ${d.toFixed(2)} A`);
});

test('the reported geometry is internally consistent', () => {
  const spacing = 1.0;
  for (const p of findPockets(hollow(), { spacing })) {
    assert.equal(p.volume, p.points.length * spacing ** 3, 'volume must be the point count times the cell volume');
    assert.ok(p.buriedness > 0 && p.buriedness <= 1, `buriedness ${p.buriedness} is outside (0, 1]`);
    assert.ok(p.druggability >= 0 && p.druggability <= 1, `druggability ${p.druggability} is outside [0, 1]`);
    assert.ok(Number.isFinite(p.score) && p.score > 0, `score ${p.score} is not a usable ranking value`);
    assert.ok(p.center.every(Number.isFinite), 'the centre must be finite');
  }
});

test('two cavities are both found, and the larger one ranks first', () => {
  seq = 0;
  const atoms = shell([], 0, 9, 300);
  shell(atoms, 40, 6, 180);
  const p = findPockets(new Structure(atoms, { name: 'two' }), { spacing: 1.0 });
  assert.equal(p.length, 2, `expected 2 pockets, got ${p.length}`);
  assert.ok(Math.abs(p[0].center[0] - 0) < 1.0, `the first pocket should be the big cavity at x=0`);
  assert.ok(Math.abs(p[1].center[0] - 40) < 1.0, `the second should be the small cavity at x=40`);
  assert.ok(p[0].volume > p[1].volume * 3, 'the radius-9 cavity should be several times the radius-6 one');
  assert.ok(p[0].score > p[1].score, 'ranking must put the larger, equally buried cavity first');
  assert.ok(p[0].druggability > p[1].druggability, 'and call the bigger one more druggable');
});

test('a solid blob has no interior, so it has no pocket', () => {
  seq = 0;
  const st = new Structure(ball([], 0, 9), { name: 'solid' });
  assert.ok(st.n > 150, `the lattice should be dense enough to seal: only ${st.n} atoms`);
  assert.deepEqual(findPockets(st, { spacing: 1.0 }), [],
    'a convex solid must not report a pocket; interstices are not cavities');
});

test('a shallow surface dent does not outrank a buried cavity', () => {
  seq = 0;
  const atoms = shell([], 0, 9, 300);
  // A plate at y=0 with a hemispherical divot pressed into it, 25 A away from the sealed cavity.
  for (let x = 25; x <= 55; x += 2.4) {
    for (let z = -15; z <= 15; z += 2.4) {
      const d = Math.hypot(x - 40, z);
      atoms.push(atom(x, d < 6 ? -Math.sqrt(36 - d * d) * 0.6 : 0, z, 'B'));
    }
  }
  const p = findPockets(new Structure(atoms, { name: 'dent' }), { spacing: 1.0 });
  assert.ok(p.length >= 1, 'the buried cavity must still be found');
  assert.ok(norm(p[0].center) < 1.0, `the top pocket should be the buried cavity, not the dent at x=40`);
  // If the dent registers at all it must rank below; an open dimple is not a binding site.
  for (const q of p.slice(1)) {
    assert.ok(q.score < p[0].score, 'nothing open to the solvent may outrank a sealed cavity');
  }
});

test('opening the wall opens the pocket: exclusion is honoured', () => {
  const st = hollow();
  const sealed = findPockets(st, { spacing: 1.0 })[0];

  const cap = [];
  for (let i = 0; i < st.n; i++) if (st.pos[i * 3] > 3) cap.push(i);
  assert.ok(cap.length > 50, `the cap should be a substantial piece of wall, got ${cap.length} atoms`);
  st.excludeAtoms(cap);
  const opened = findPockets(st, { spacing: 1.0 })[0];

  assert.ok(opened, 'a cavity open on one side is still a pocket');
  assert.ok(opened.buriedness < sealed.buriedness - 0.1,
    `buriedness should fall materially: ${sealed.buriedness.toFixed(3)} -> ${opened.buriedness.toFixed(3)}`);
  assert.ok(opened.score < sealed.score * 0.75,
    `score should fall with it: ${sealed.score.toFixed(0)} -> ${opened.score.toFixed(0)}`);
  // The centre of mass of the buried region retreats away from the opening, which is at +x.
  assert.ok(opened.center[0] < -0.5, `centre should retreat from the opening, sits at x=${opened.center[0].toFixed(2)}`);
});

test('thinning a wall uniformly does not fake an opening', () => {
  // Worth asserting because it is the result that surprised: removing every other atom halves the wall's
  // atom count but leaves the remaining atoms about 2.9 A apart, which still occludes a 2.8 A probe. The
  // cavity stays sealed and its volume grows slightly as the wall thins. Buriedness must not drop.
  const st = hollow();
  const sealed = findPockets(st, { spacing: 1.0 })[0];
  st.excludeAtoms(Array.from({ length: 150 }, (_, i) => i * 2));
  const thinned = findPockets(st, { spacing: 1.0 })[0];
  assert.ok(thinned, 'a thinned but sealed wall still encloses a pocket');
  assert.ok(thinned.buriedness > sealed.buriedness - 0.02,
    `a sealed-but-thinner wall must stay buried: ${sealed.buriedness.toFixed(3)} -> ${thinned.buriedness.toFixed(3)}`);
  assert.ok(thinned.volume >= sealed.volume, 'a thinner wall leaves more free interior, not less');
});

test('the answer does not depend on the grid spacing', () => {
  const results = [1.0, 1.25, 1.5].map((spacing) => {
    const p = findPockets(hollow(), { spacing });
    assert.equal(p.length, 1, `spacing ${spacing} found ${p.length} pockets, expected 1`);
    return { spacing, ...p[0] };
  });
  for (const r of results) {
    assert.ok(norm(r.center) < 0.5, `spacing ${r.spacing} put the centre ${norm(r.center).toFixed(2)} A off`);
    assert.ok(r.buriedness > 0.95, `spacing ${r.spacing} gave buriedness ${r.buriedness.toFixed(3)}`);
  }
  const vols = results.map((r) => r.volume);
  assert.ok(Math.max(...vols) / Math.min(...vols) < 1.15,
    `volume should be stable across spacings, spread was ${vols.map((v) => v.toFixed(0)).join(' / ')}`);
});

test('maxPockets caps the list without disturbing the ranking', () => {
  seq = 0;
  const atoms = [];
  for (let i = 0; i < 4; i++) shell(atoms, i * 30, 9, 300);
  const st = new Structure(atoms, { name: 'four' });
  assert.equal(findPockets(st, { spacing: 1.0, maxPockets: 6 }).length, 4);
  const two = findPockets(st, { spacing: 1.0, maxPockets: 2 });
  assert.equal(two.length, 2);
  for (let i = 1; i < two.length; i++) assert.ok(two[i - 1].score >= two[i].score, 'still ranked best first');
});

test('nothing to search returns nothing rather than throwing', () => {
  seq = 0;
  // A structure with no polymer residues: findPockets considers polymer heavy atoms only.
  const het = [{ name: 'C1', resName: 'LIG', chain: 'A', resSeq: 1, element: 'C', het: 1, x: 0, y: 0, z: 0 }];
  assert.deepEqual(findPockets(new Structure(het, { name: 'het' }), { spacing: 1.0 }), []);

  const st = hollow();
  st.excludeAtoms(Array.from({ length: st.n }, (_, i) => i));
  assert.deepEqual(findPockets(st, { spacing: 1.0 }), [], 'excluding everything leaves nothing to search');
});

test('each pocket names the residues that line it', () => {
  const st = hollow();
  const p = findPockets(st, { spacing: 1.0 })[0];
  assert.ok(Array.isArray(p.residues) && p.residues.length > 0, 'a pocket must report its lining residues');
  for (const r of p.residues) {
    assert.ok(Number.isInteger(r) && r >= 0 && r < st.residues.length,
      `residue index ${r} is not a residue of this structure`);
  }
  assert.ok(typeof p.label === 'string' && p.label.length > 0, 'a pocket needs a label a person can read');
  assert.ok(/ALA\d/.test(p.label), `the label should name real residues, got "${p.label}"`);
});
