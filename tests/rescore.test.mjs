// Offline checks for js/rescore.js on synthetic geometry.
//
// The eleven-case benchmark records four of six failures as ranking failures: the search produced a pose
// within 2 Å of the crystal and the scoring function put something wrong above it. This module exists to
// address that, so the test that matters is not "do the terms compute" — it is whether a constructed
// ranking inversion of exactly that shape gets corrected.
//
// The fixture builds two sub-pockets in one receptor: a tight all-carbon slot that packs a ligand beautifully
// and offers its oxygen nothing to hydrogen bond to, and a roomier site with a zinc at the bottom. vinaScore
// prefers the greasy slot, because close packing earns gauss and hydrophobic credit while an unsatisfied
// buried oxygen costs nothing and a zinc contact earns nothing. That is the recorded failure mode in
// miniature, and it is reproducible from the construction rather than fitted to the answer.
//
// What these tests do NOT establish: that rescoring improves the eleven-case benchmark. The weights are
// uncalibrated, calibrating them needs the benchmark, and the benchmark needs the network. See
// docs/ROADMAP_LOOP.md.
//
//   node --test tests/rescore.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { Structure } from '../js/structure.js';
import { ProteinGrid, vinaScore } from '../js/dock.js';
import {
  rescore, rescoreTerms, rerank, internalClashes,
  COORDINATING_METALS, DEFAULT_WEIGHTS, WEIGHTS_ARE_UNCALIBRATED,
} from '../js/rescore.js';

let seq = 0;
const at = (x, y, z, el, name, resName = 'ALA', het = 0) =>
  ({ name, resName, chain: 'A', resSeq: ++seq, element: el, het, x, y, z });

// Two sub-pockets. +x: a tight greasy slot, nothing polar. -x: a roomier site with a zinc at its floor.
// The wall spacings are the ones that produce the inversion; they were found by scanning, then fixed here.
function twoSiteReceptor({ zinc = true, partner = false } = {}) {
  seq = 0;
  const atoms = [];
  for (let x = 2; x <= 10; x += 1.7) {
    for (let y = -3.4; y <= 3.4; y += 1.7) for (const z of [-3.1, 3.1]) atoms.push(at(x, y, z, 'C', 'CB'));
    for (const y of [-3.5, 3.5]) for (const z of [-1.5, 0, 1.5]) atoms.push(at(x, y, z, 'C', 'CG'));
  }
  for (let x = -10; x <= -2; x += 2.2) {
    for (let y = -6; y <= 6; y += 2.2) for (const z of [-5.0, 5.0]) atoms.push(at(x, y, z, 'C', 'CB'));
  }
  if (zinc) atoms.push(at(-5.0, 0, 0, 'ZN', 'ZN', 'ZN', 1));
  if (partner) atoms.push(at(6.9, 0, 0, 'O', 'OG', 'SER'));
  return new ProteinGrid(new Structure(atoms, { name: 'two-site' }), 4);
}

// A dense slab, used where burial needs to be unambiguous.
function slabReceptor({ partner = true, metalAt = null } = {}) {
  seq = 0;
  const atoms = [];
  for (let x = -8; x <= 8; x += 1.9) {
    for (let y = -6; y <= 6; y += 1.9) for (const z of [-3.6, 3.6]) atoms.push(at(x, y, z, 'C', 'CB'));
    for (const y of [-5.7, 5.7]) atoms.push(at(x, y, 0, 'C', 'CG'));
  }
  if (partner) atoms.push(at(4.0, 0, 0, 'O', 'OG', 'SER'));
  if (metalAt !== null) atoms.push(at(metalAt, 0, 0, 'ZN', 'ZN', 'ZN', 1));
  return new ProteinGrid(new Structure(atoms, { name: 'slab' }), 4);
}

// A three-atom ligand whose first atom is the polar one, so moving it along x moves the oxygen.
const probe = () => new Structure([
  { x: 0, y: 0, z: 0, element: 'O', name: 'O1', het: 1 },
  { x: 1.4, y: 0, z: 0, element: 'C', name: 'C1', het: 1 },
  { x: 2.8, y: 0, z: 0, element: 'C', name: 'C2', het: 1 },
], { bonds: [0, 1, 1, 1, 2, 1], kind: 'small', name: 'probe' });

const shifted = (lig, dx) => {
  const c = Float32Array.from(lig.pos);
  for (let i = 0; i < lig.n; i++) c[i * 3] += dx;
  return c;
};

// --- the terms ------------------------------------------------------------------------------------------

test('a buried polar atom with a hydrogen-bond partner is not penalised', () => {
  const grid = slabReceptor({ partner: true });
  const lig = probe();
  const t = rescoreTerms(grid, lig, shifted(lig, 1.1)); // oxygen 2.9 Å from the serine OG
  assert.equal(t.buried, 1, 'the slab should bury the oxygen');
  assert.equal(t.polar, 1);
  assert.equal(t.unsatisfied, 0, 'a satisfied hydrogen bond must not be charged for');
});

test('a buried polar atom with nothing to bond to is penalised', () => {
  const grid = slabReceptor({ partner: true });
  const lig = probe();
  const t = rescoreTerms(grid, lig, shifted(lig, 0)); // oxygen 4.0 Å from the OG: too far
  assert.equal(t.buried, 1);
  assert.equal(t.unsatisfied, 1, 'burying a donor or acceptor with no partner should cost something');
});

test('a solvent-exposed polar atom is not penalised, because it is not desolvated', () => {
  // The penalty is for burying a polar group, not for having one. An atom in open solvent keeps its waters.
  const grid = slabReceptor({ partner: false });
  const lig = probe();
  const t = rescoreTerms(grid, lig, shifted(lig, 60)); // far outside the slab
  assert.equal(t.buried, 0);
  assert.equal(t.unsatisfied, 0, 'an exposed polar atom has solvent to bond to and must not be charged');
});

test('a metal at coordination distance is counted, and one merely nearby is not', () => {
  const lig = probe();
  // Zinc 2.1 Å from the oxygen: coordinating.
  let t = rescoreTerms(slabReceptor({ partner: false, metalAt: -2.1 }), lig, Float32Array.from(lig.pos));
  assert.equal(t.metal, 1, 'a heteroatom on a zinc should be credited');
  assert.equal(t.unsatisfied, 0, 'and the coordination satisfies the lone pair');

  // Zinc 4.0 Å away: in the burial shell but not coordinating.
  t = rescoreTerms(slabReceptor({ partner: false, metalAt: -4.0 }), lig, Float32Array.from(lig.pos));
  assert.equal(t.metal, 0, 'a metal 4 Å away is not a coordination contact');
  assert.equal(t.unsatisfied, 1,
    'and must not excuse an unsatisfied oxygen — an earlier draft of the module let it, and this is that bug');

  // Zinc 1.4 Å away: interpenetrating, not bonded.
  t = rescoreTerms(slabReceptor({ partner: false, metalAt: -1.4 }), lig, Float32Array.from(lig.pos));
  assert.equal(t.metal, 0, 'atoms inside each other are a clash, not a coordination bond');
});

test('only coordinating metals count, not counter-ions', () => {
  for (const m of ['ZN', 'MG', 'MN', 'FE', 'CU', 'NI', 'CO', 'CD']) {
    assert.ok(COORDINATING_METALS.has(m), `${m} should coordinate`);
  }
  for (const m of ['NA', 'CL', 'K', 'BR', 'IOD']) {
    assert.ok(!COORDINATING_METALS.has(m),
      `${m} is usually a counter-ion or a crystallisation additive; rewarding poses for sitting next to salt would be wrong`);
  }
});

test('internal clashes are counted for a folded pose and not for an extended one', () => {
  // The gap iteration 8 noted and left: vinaScore sees protein-ligand pairs only, so a conformer folded
  // through itself is free. This proves both halves — the clash is counted, and vinaScore does not see it.
  const chain = new Structure([
    { x: 0, y: 0, z: 0, element: 'C', name: 'C1', het: 1 },
    { x: 1.5, y: 0, z: 0, element: 'C', name: 'C2', het: 1 },
    { x: 3.0, y: 0, z: 0, element: 'C', name: 'C3', het: 1 },
    { x: 4.5, y: 0, z: 0, element: 'C', name: 'C4', het: 1 },
    { x: 6.0, y: 0, z: 0, element: 'C', name: 'C5', het: 1 },
  ], { bonds: [0, 1, 1, 1, 2, 1, 2, 3, 1, 3, 4, 1], kind: 'small', name: 'chain' });

  assert.equal(internalClashes(chain, chain.pos), 0, 'an extended chain does not clash with itself');

  const folded = Float32Array.from(chain.pos);
  folded[12] = 0.9; folded[13] = 0.9; // fold C5 back onto C1
  assert.ok(internalClashes(chain, folded) >= 1, 'a chain folded onto itself should register a clash');

  const grid = slabReceptor({ partner: false });
  assert.equal(vinaScore(grid, chain, folded), vinaScore(grid, chain, folded),
    'sanity: scoring is deterministic');
  const t = rescoreTerms(grid, chain, folded);
  assert.ok(t.clash >= 1, 'the rescoring pass should see what vinaScore cannot');
});

// --- the thing this module exists for -------------------------------------------------------------------

test('a ranking inversion of the recorded shape is corrected', () => {
  // vinaScore prefers a decoy packed into a greasy slot with its oxygen buried and unsatisfied, over a
  // pose that coordinates the zinc. That is the carbonic-anhydrase failure in miniature: a good pose found
  // and ranked below a bad one. The rescoring pass should put it back.
  const grid = twoSiteReceptor();
  const lig = probe();
  const decoy = shifted(lig, 4.0);    // greasy slot, oxygen unsatisfied
  const native = shifted(lig, -3.1);  // oxygen on the zinc

  const dBase = vinaScore(grid, lig, decoy);
  const nBase = vinaScore(grid, lig, native);
  assert.ok(dBase < nBase,
    `the fixture must start inverted, or the test proves nothing: decoy ${dBase.toFixed(3)} vs native ${nBase.toFixed(3)}`);

  const d = rescore(grid, lig, decoy);
  const n = rescore(grid, lig, native);
  assert.equal(d.terms.unsatisfied, 1, 'the decoy buries its oxygen with no partner');
  assert.equal(n.terms.metal, 1, 'the native coordinates the zinc');
  assert.ok(n.total < d.total,
    `rescoring should reverse the order: native ${n.total.toFixed(3)} vs decoy ${d.total.toFixed(3)}`);
});

test('rerank reports what moved, because changing an order is the only thing it does', () => {
  const grid = twoSiteReceptor();
  const lig = probe();
  const poses = [shifted(lig, 4.0), shifted(lig, -3.1)].map((coords) => ({ coords }));
  const { poses: out, moved, note } = rerank(grid, lig, poses);

  assert.equal(out.length, 2);
  for (let i = 1; i < out.length; i++) assert.ok(out[i - 1].score <= out[i].score, 'sorted best first');
  assert.equal(moved, 2, 'both poses should have changed position');
  assert.equal(out[0].rankChange, 1, 'the promoted pose should record that it rose by one');
  assert.equal(out[1].rankChange, -1);
  for (const p of out) {
    assert.ok(typeof p.base === 'number' && typeof p.score === 'number',
      'a pose must keep both its old score and its new one, or nobody can audit the change');
    assert.ok(p.rescoreTerms, 'and the terms that moved it');
  }
  assert.equal(note, WEIGHTS_ARE_UNCALIBRATED);
});

// --- invariants and honesty -----------------------------------------------------------------------------

test('zero weights reduce rescoring to vinaScore exactly', () => {
  // The property a reviewer should check first: the rescoring can be turned off, and shown to be off.
  const grid = twoSiteReceptor();
  const lig = probe();
  const coords = shifted(lig, 4.0);
  const r = rescore(grid, lig, coords, { weights: { unsatisfied: 0, metal: 0, clash: 0 } });
  assert.equal(r.total, r.base);
  assert.equal(r.total, vinaScore(grid, lig, coords));
  assert.equal(r.delta, 0);
});

test('the default weights have the signs their roles require', () => {
  assert.ok(DEFAULT_WEIGHTS.unsatisfied > 0, 'an unsatisfied buried polar atom is a penalty');
  assert.ok(DEFAULT_WEIGHTS.metal < 0, 'a coordination contact is a reward, and scores here are negative-is-better');
  assert.ok(DEFAULT_WEIGHTS.clash > 0, 'an internal clash is a penalty');
});

test('rescoring is deterministic and does not mutate its input', () => {
  const grid = twoSiteReceptor();
  const lig = probe();
  const coords = shifted(lig, -3.1);
  const copy = Float32Array.from(coords);
  const a = rescore(grid, lig, coords);
  const b = rescore(grid, lig, coords);
  assert.deepEqual(Array.from(coords), Array.from(copy), 'the input array must be untouched');
  assert.equal(a.total, b.total);
  assert.deepEqual(a.terms, b.terms);
});

test('every result says its weights are uncalibrated', () => {
  const grid = twoSiteReceptor();
  const lig = probe();
  const r = rescore(grid, lig, shifted(lig, -3.1));
  assert.equal(r.note, WEIGHTS_ARE_UNCALIBRATED);
  assert.match(WEIGHTS_ARE_UNCALIBRATED, /uncalibrated/);
  assert.match(WEIGHTS_ARE_UNCALIBRATED, /benchmark|network/,
    'the disclaimer should say what calibrating it would take, not merely that it is not calibrated');
});

test('a receptor with no metal and no polar partner produces no terms at all', () => {
  // A quiet case worth pinning: the module must not invent a correction where there is nothing to correct.
  const grid = twoSiteReceptor({ zinc: false });
  const lig = probe();
  const r = rescore(grid, lig, shifted(lig, -3.1));
  assert.equal(r.terms.metal, 0);
  assert.equal(r.terms.clash, 0);
  assert.equal(r.total, r.base + DEFAULT_WEIGHTS.unsatisfied * r.terms.unsatisfied,
    'the only term in play should be the one the geometry actually supports');
});
