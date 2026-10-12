// What "make the benchmark repeat itself" actually requires.
//
// Iteration 22 measured the benchmark three times, got 5, 6 and 4 of 11, and
// withdrew the single figure. The natural reading is that the benchmark is
// flaky. It is not: given a seed it reproduces bit for bit. What varies is the
// seed, and a single seeded run is one draw from a wide distribution that the
// benchmark then reports as an integer.
//
// That distinction decides the remedy. "Flaky" would mean hunting
// nondeterminism -- unordered iteration, a clock, a hash seed. There is none to
// find. "One draw reported as the answer" means the remedy is to report the
// distribution: run K seeds and publish the per-case pass fraction.
//
// These tests hold the foundation that argument rests on, with small search
// parameters so they run in seconds rather than the ~150 s a benchmark case
// takes at full settings.
import test from 'node:test';
import assert from 'node:assert/strict';

import { CASES, runCase, cacheStatus } from '../evals/redock.mjs';

const FAST = { runs: 2, steps: 400 };
const CASE = CASES.find((c) => c.pdb === '1OYT') ?? CASES[0];

const cached = () => {
  const s = cacheStatus([CASE])[0];
  return s.protein && s.ligand;
};

test('every benchmark case has its structures committed', () => {
  // The benchmark spent twenty iterations marked "needs the network". A figure
  // measured against a file the RCSB can revise is not reproducible either.
  const missing = cacheStatus(CASES).filter((c) => !c.protein || !c.ligand);
  assert.deepEqual(missing, [],
    `uncached: ${missing.map((m) => m.pdb).join(', ')} — run with --refresh-structures`);
});

test('the same seed gives the same answer, exactly', { skip: !cached() && 'structures not cached' },
  async () => {
    const a = await runCase(CASE, { ...FAST, seed: 7 });
    const b = await runCase(CASE, { ...FAST, seed: 7 });

    assert.equal(a.topRmsd, b.topRmsd, 'top-pose RMSD moved between identical seeded runs');
    assert.equal(a.topScore, b.topScore, 'top score moved between identical seeded runs');
    assert.equal(a.bestRmsd, b.bestRmsd);
    assert.equal(a.success, b.success);
  });

test('a different seed is a different draw, not a repeat',
  { skip: !cached() && 'structures not cached' }, async () => {
    // If this ever stops being true the seed has stopped reaching the sampler,
    // and every "seeded" figure in the repository would be one number wearing
    // several labels.
    const seeds = [11, 12, 13];
    const results = [];
    for (const seed of seeds) results.push(await runCase(CASE, { ...FAST, seed }));

    const distinct = new Set(results.map((r) => `${r.topRmsd}/${r.topScore}`));
    assert.ok(distinct.size > 1,
      `seeds ${seeds.join(', ')} all produced ${[...distinct][0]} — the seed is not reaching the sampler`);
  });

test('an unseeded run is not silently seeded', { skip: !cached() && 'structures not cached' },
  async () => {
    const a = await runCase(CASE, FAST);
    const b = await runCase(CASE, FAST);
    // Unseeded runs may coincide by chance on a 2-run search, so this asserts
    // the weaker, reliable thing: an unseeded run is not pinned to the seeded one.
    const seeded = await runCase(CASE, { ...FAST, seed: 7 });
    assert.ok(a.topScore !== seeded.topScore || b.topScore !== seeded.topScore,
      'unseeded runs reproduce the seeded result, so seed=null is not actually random');
  });

test('the ensemble reports a distribution, not a verdict',
  { skip: !cached() && 'structures not cached' }, async () => {
    const { runEnsemble } = await import('../evals/redock.mjs');
    const e = await runEnsemble([CASE], { seeds: [21, 22], ...FAST });

    assert.equal(e.seeds.length, 2);
    assert.equal(e.perCase.length, 1);

    const c = e.perCase[0];
    assert.ok(c.passFraction >= 0 && c.passFraction <= 1, 'pass fraction must be a proportion');
    assert.ok(Array.isArray(c.rmsdRange) && c.rmsdRange[0] <= c.rmsdRange[1], 'rmsdRange must be ordered');

    // The point of the whole exercise: a case is classified by how often it
    // passes, so one that is 50/50 is reported as unsettled rather than being
    // rounded to whichever side the chosen seed landed on.
    const unsettled = c.passFraction > 0 && c.passFraction < 1;
    assert.equal(c.settled, !unsettled);
    assert.equal(e.unsettled.includes(CASE.pdb), unsettled);

    assert.ok(e.succeededRange[0] <= e.meanSucceeded && e.meanSucceeded <= e.succeededRange[1],
      'the mean must lie inside the range it summarises');
  });
