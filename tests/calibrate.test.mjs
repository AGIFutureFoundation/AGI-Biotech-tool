// Offline checks for evals/calibrate.mjs.
//
// A calibration harness is a machine for producing a number that will be published, which makes it exactly
// the kind of code that should not be trusted because it looks right. The tests here build dumps whose
// correct answer follows from the construction — a term that genuinely separates good poses from bad ones,
// a term that is pure noise — and require the harness to find the first and refuse to be impressed by the
// second.
//
// The case that matters most is the last one: a dump where the terms carry no signal at all. Fitting three
// weights to eleven cases will still produce an in-sample gain there, because that is what fitting does, and
// leave-one-out must not. If that test ever starts passing for the wrong reason, the harness is a machine
// for generating false confidence.
//
//   node --test tests/calibrate.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  rescoreValue, evaluate, candidateGrid, sweep, fit, leaveOneOut, describe,
  OVERFITTING_WARNING, SUCCESS_THRESHOLD,
} from '../evals/calibrate.mjs';

const pose = (rmsd, base, terms = {}) => ({
  rmsd, base, terms: { unsatisfied: 0, metal: 0, clash: 0, ...terms },
});

// A case where vinaScore ranks a decoy first, and the metal term is what distinguishes them. The near-native
// pose has the worse base score and the coordination contact — the carbonic-anhydrase shape.
const metalCase = (id) => ({
  id,
  poses: [
    pose(5.5, -9.0),                   // decoy: better base, no metal contact
    pose(0.8, -8.0, { metal: 1 }),     // near-native: worse base, coordinates the metal
  ],
});

// A case where nothing distinguishes the poses: the decoy simply scores better and no term fires.
const hopelessCase = (id) => ({ id, poses: [pose(6.0, -9.0), pose(0.9, -7.0)] });

// A case already solved by the base score, which no weighting should break.
const easyCase = (id) => ({ id, poses: [pose(0.7, -9.5), pose(6.2, -8.0)] });

const dumpOf = (cases) => ({ generated: 'test', cases });

const GRID = candidateGrid({
  unsatisfied: [0, 0.5, 1.0],
  metal: [0, -0.5, -1.0, -2.0],
  clash: [0, 1.0],
});

test('the rescored value is the base score plus the weighted terms', () => {
  const p = pose(1.0, -8.0, { unsatisfied: 2, metal: 1, clash: 3 });
  const v = rescoreValue(p, { unsatisfied: 0.5, metal: -1, clash: 2 });
  assert.ok(Math.abs(v - (-8.0 + 1.0 - 1.0 + 6.0)) < 1e-9, `got ${v}`);
  assert.equal(rescoreValue(p, {}), -8.0, 'with no weights it is the base score');
  assert.equal(rescoreValue(pose(1, -5), { metal: -3 }), -5, 'a term that did not fire contributes nothing');
});

test('evaluation picks the best-scoring pose per case and reports its RMSD', () => {
  const dump = dumpOf([metalCase('A')]);
  const noWeights = evaluate(dump, { unsatisfied: 0, metal: 0, clash: 0 });
  assert.equal(noWeights.solved, 0, 'the base score alone picks the decoy');
  assert.equal(noWeights.topRmsds[0], 5.5);

  const withMetal = evaluate(dump, { unsatisfied: 0, metal: -2.0, clash: 0 });
  assert.equal(withMetal.solved, 1, 'a metal weight large enough to overcome the base gap fixes it');
  assert.equal(withMetal.topRmsds[0], 0.8);
});

test('the ceiling is reported, and does not move with the weights', () => {
  // Any gain has to be read against what was reachable, not against zero.
  const dump = dumpOf([metalCase('A'), hopelessCase('B'), easyCase('C')]);
  const a = evaluate(dump, { metal: 0 });
  const b = evaluate(dump, { metal: -5 });
  assert.equal(a.reachable, 3, 'all three cases contain a pose within 2 Å');
  assert.equal(b.reachable, a.reachable, 'the ceiling is a property of the poses, not of the weights');
  assert.ok(a.solved < a.reachable, 'and the base score does not reach it');
});

test('a case already solved by the base score is not broken by a modest weight', () => {
  const dump = dumpOf([easyCase('C')]);
  assert.equal(evaluate(dump, { metal: 0 }).solved, 1);
  assert.equal(evaluate(dump, { unsatisfied: 0.5, metal: -1.0, clash: 1.0 }).solved, 1);
});

test('a tie between poses resolves deterministically', () => {
  const dump = dumpOf([{ id: 'T', poses: [pose(4.0, -8.0), pose(1.0, -8.0)] }]);
  const a = evaluate(dump, { metal: 0 });
  const b = evaluate(dump, { metal: 0 });
  assert.equal(a.topRmsds[0], b.topRmsds[0], 'the same input must give the same answer');
  assert.equal(a.topRmsds[0], 4.0, 'ties go to the earlier pose, so a sweep is reproducible');
});

test('the candidate grid is the full product, in a stable order', () => {
  const g = candidateGrid({ unsatisfied: [0, 1], metal: [0, -1], clash: [2] });
  assert.equal(g.length, 4);
  assert.deepEqual(g[0], { unsatisfied: 0, metal: 0, clash: 2 });
  assert.deepEqual(candidateGrid({ unsatisfied: [0, 1], metal: [0, -1], clash: [2] }), g,
    'the order must be stable, or two sweeps disagree about which of two equal candidates won');
  assert.equal(candidateGrid().length, 1, 'with no candidates it is the all-zero weight set');
});

test('the sweep finds the weight that separates the cases, when one exists', () => {
  const dump = dumpOf([metalCase('A'), metalCase('B'), easyCase('C')]);
  const best = fit(dump, GRID);
  assert.equal(best.solved, 3, 'all three should be solvable by weighting the metal term');
  assert.ok(best.weights.metal <= -1.0, `expected a real metal weight, got ${best.weights.metal}`);
});

test('the sweep prefers the smaller correction when two do equally well', () => {
  // Otherwise the harness drifts toward large weights that happen to tie, which is how a calibration ends
  // up recommending a term far stronger than the evidence supports.
  // -1.0 exactly ties the decoy here, and a tie goes to the earlier pose, so it does not solve the case.
  // -2.0 and -5.0 both do, and the weaker of those should be chosen.
  const dump = dumpOf([metalCase('A')]);
  assert.equal(fit(dump, candidateGrid({ metal: [-1.0] })).solved, 0, 'an exact tie is not a win');
  const best = fit(dump, candidateGrid({ metal: [-2.0, -5.0] }));
  assert.equal(best.solved, 1);
  assert.equal(best.weights.metal, -2.0, 'the weakest weight that works should win');
});

test('the sweep returns candidates ranked, best first', () => {
  const results = sweep(dumpOf([metalCase('A'), metalCase('B')]), GRID);
  assert.ok(results.length === GRID.length);
  for (let i = 1; i < results.length; i++) {
    assert.ok(results[i - 1].solved >= results[i].solved, 'solved counts must be non-increasing');
  }
});

test('leave-one-out never lets a case influence the weights applied to it', () => {
  const dump = dumpOf([metalCase('A'), metalCase('B'), metalCase('C'), easyCase('D')]);
  const loo = leaveOneOut(dump, GRID);
  assert.equal(loo.total, 4);
  assert.equal(loo.perCase.length, 4);
  assert.deepEqual(loo.perCase.map((p) => p.id), ['A', 'B', 'C', 'D']);
  // The signal here is real and consistent, so it should generalise to the held-out case.
  assert.equal(loo.outOfSampleSolved, 4, 'a genuine, consistent term should hold up out of sample');
  assert.ok(loo.inSample, 'the in-sample figure is returned alongside, so the two cannot be quoted apart');
});

test('the held-out case does not influence the weights applied to it', () => {
  // Found by mutation: replacing the fold split with the whole dump broke no test, which means a
  // cross-validation harness could silently stop holding anything out and keep reporting its numbers as
  // out-of-sample. This is the discriminator.
  //
  // Ten cases are solved by a metal weight and are indifferent to the clash weight. One case — the one held
  // out — is solved ONLY when the clash weight is on. Fitting on the other ten therefore never has a reason
  // to turn the clash weight on: it ties on solved count and the smaller-correction tiebreak rejects it. So
  // the odd case must fail out-of-sample. If the split leaked, fitting would see it, switch the clash weight
  // on at no cost to the other ten, and "solve" it.
  const cases = [];
  for (let i = 0; i < 10; i++) {
    cases.push({
      id: `M${i}`,
      poses: [pose(5.0, -9.0), pose(0.8, -8.0, { metal: 1 })],
    });
  }
  const odd = {
    id: 'ODD',
    poses: [pose(6.0, -9.0, { clash: 1 }), pose(0.5, -8.5)],
  };
  const grid = candidateGrid({ unsatisfied: [0], metal: [0, -2.0], clash: [0, 1.0] });

  // Fitting on the ten alone: the clash weight is not worth turning on.
  const onTen = fit(dumpOf(cases), grid);
  assert.equal(onTen.solved, 10, 'the metal weight should solve all ten');
  assert.equal(onTen.weights.clash, 0, 'and the clash weight should stay off, having earned nothing');

  // Fitting on all eleven: now the clash weight pays for itself.
  const onAll = fit(dumpOf([...cases, odd]), grid);
  assert.equal(onAll.weights.clash, 1.0, 'with the odd case visible, the clash weight becomes worth turning on');
  assert.equal(onAll.solved, 11);

  // So a correct leave-one-out must fail the odd case, and a leaking one would pass it.
  const loo = leaveOneOut(dumpOf([...cases, odd]), grid);
  assert.equal(loo.inSample.solved, 11, 'in-sample sees everything and solves everything');
  const oddFold = loo.perCase.find((p) => p.id === 'ODD');
  assert.equal(oddFold.solved, false,
    'the held-out case must be judged by weights fitted without it — if this passes, the fold is leaking');
  assert.equal(oddFold.weights.clash, 0, 'and those weights must be the ones the other ten chose');
  assert.ok(loo.outOfSampleSolved < loo.inSample.solved,
    `out-of-sample must be lower here: ${loo.outOfSampleSolved} vs ${loo.inSample.solved}`);
});

test('the in-sample and out-of-sample figures are always returned together', () => {
  const loo = leaveOneOut(dumpOf([metalCase('A'), hopelessCase('B')]), GRID);
  assert.ok(typeof loo.outOfSampleSolved === 'number');
  assert.ok(typeof loo.inSample.solved === 'number');
  assert.equal(loo.warning, OVERFITTING_WARNING);
  assert.match(describe(loo), /out-of-sample/);
  assert.match(describe(loo), /ceiling/, 'the summary must name the ceiling a gain is measured against');
  assert.match(describe(loo), /not evidence/, 'and carry the warning');
});

test('pure noise still produces an in-sample gain, which is why the warning exists', () => {
  // The test this harness exists to pass, and the one that changed what the module claims. Eleven cases
  // with term counts drawn from a seeded PRNG — no relationship whatever to which pose is near-native — and
  // a base score that solves none of them. Fitting three weights over a 24-candidate grid finds a "gain"
  // anyway, because that is what fitting three parameters to eleven binary outcomes does.
  //
  // Measured across five seeds while writing this: in-sample gains of 1, 3, 4, 3 and 6 out of eleven from a
  // base of zero, with out-of-sample at 0, 0, 4, 1 and 6. So leave-one-out is usually more pessimistic and
  // SOMETIMES IS NOT — on this few cases the same weight set often wins in every fold. That is why the
  // warning says leave-one-out is not a guarantee, and why the honest output of this harness is a hypothesis
  // rather than a validated weight set.
  const mulberry32 = (a) => () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };

  for (const seed of [1, 2, 3, 7, 42]) {
    const r = mulberry32(seed);
    const cases = [];
    for (let i = 0; i < 11; i++) {
      const terms = () => ({
        unsatisfied: Math.floor(r() * 3), metal: Math.floor(r() * 2), clash: Math.floor(r() * 2),
      });
      cases.push({
        id: `N${i}`,
        poses: [
          { rmsd: 4 + r() * 3, base: -9.0, terms: terms() },   // decoy, always the better base score
          { rmsd: 0.4 + r() * 1.2, base: -8.0, terms: terms() }, // near-native, always worse
        ],
      });
    }
    const dump = dumpOf(cases);
    assert.equal(evaluate(dump, {}).solved, 0,
      `seed ${seed}: the base score must solve none, so any gain comes from the weights`);

    const loo = leaveOneOut(dump, GRID);
    assert.ok(loo.inSample.solved > 0,
      `seed ${seed}: fitting WILL find an in-sample gain from noise; if it does not, this test is not testing what it claims`);
    assert.ok(loo.outOfSampleSolved <= loo.inSample.solved,
      `seed ${seed}: out-of-sample must never exceed in-sample, got ${loo.outOfSampleSolved} vs ${loo.inSample.solved}`);
  }
});

test('the warning says leave-one-out is not a guarantee, because it is not', () => {
  assert.match(OVERFITTING_WARNING, /not evidence/);
  assert.match(OVERFITTING_WARNING, /not a guarantee/,
    'the measured behaviour is that leave-one-out can report a spurious gain on eleven cases, and the warning must say so');
  assert.match(OVERFITTING_WARNING, /hypothesis/, 'and what the result may honestly be used for');
});

test('an empty or malformed dump is handled rather than throwing', () => {
  const empty = evaluate(dumpOf([]), { metal: -1 });
  assert.equal(empty.solved, 0);
  assert.equal(empty.total, 0);
  assert.equal(empty.meanTopRmsd, null);

  const noPoses = evaluate(dumpOf([{ id: 'X', poses: [] }, { id: 'Y' }]), { metal: -1 });
  assert.equal(noPoses.solved, 0);
  assert.deepEqual(noPoses.topRmsds, [null, null], 'a case with no poses is unscored, not scored zero');

  assert.equal(leaveOneOut(dumpOf([]), GRID).outOfSampleSolved, 0);
});

test('the success threshold matches the one evals/redock.mjs uses', () => {
  // Two files deciding separately what "solved" means is how two published numbers come to disagree.
  assert.equal(SUCCESS_THRESHOLD, 2.0);
  const dump = dumpOf([{ id: 'E', poses: [pose(2.0, -9.0)] }]);
  assert.equal(evaluate(dump, {}).solved, 1, 'exactly at the threshold counts as solved');
  assert.equal(evaluate(dumpOf([{ id: 'E', poses: [pose(2.01, -9.0)] }]), {}).solved, 0);
});
