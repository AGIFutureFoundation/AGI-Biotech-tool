// Offline checks for js/poses.js on synthetic pose sets.
//
// Clustering is easy to get subtly wrong in a way nothing notices: an off-by-one in the leader order, a
// cutoff compared the wrong way round, a mode that silently absorbs a pose 10 A away. So these tests build
// pose sets whose mode structure is fixed by construction — three tight knots at known separations — and
// assert the clustering recovers exactly that.
//
// The discrimination check is the honest half of the module, so it is tested for honesty too: the note it
// produces must say its margin is uncalibrated, and a single mode must not be reported as a confident
// choice.
//
//   node --test tests/poses.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { clusterPoses, discrimination, poseSummary, DEFAULT_MARGIN, MARGIN_IS_UNCALIBRATED } from '../js/poses.js';

const N = 4; // four atoms per pose, so rmsd has something to average over

// A pose at a given offset from the origin, jittered by `wobble` so members of one knot are near but not
// identical. Deterministic: no RNG.
function pose(offset, score, wobble = 0) {
  const coords = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    coords[i * 3] = offset + i * 1.4 + wobble;
    coords[i * 3 + 1] = i % 2 ? 0.7 : -0.7;
    coords[i * 3 + 2] = wobble * 0.5;
  }
  return { coords, score };
}

// Three knots: at x = 0, x = 6 and x = 14. Within a knot the wobble is 0.3 A, so members are far closer to
// each other than knots are to each other, whatever cutoff between 1 and 5 is chosen.
function threeKnots() {
  return [
    pose(0, -9.0), pose(0, -8.8, 0.3), pose(0, -8.6, -0.3),
    pose(6, -8.2), pose(6, -8.0, 0.3),
    pose(14, -7.1),
  ];
}

test('three knots cluster into three modes with the populations they were built with', () => {
  const modes = clusterPoses(threeKnots(), N, { cutoff: 2.5 });
  assert.equal(modes.length, 3, `expected 3 modes, got ${modes.length}`);
  assert.deepEqual(modes.map((m) => m.population), [3, 2, 1]);
  assert.equal(modes.reduce((s, m) => s + m.population, 0), 6, 'every pose must land in exactly one mode');
});

test('every pose belongs to exactly one mode, and no index is invented', () => {
  const poses = threeKnots();
  const modes = clusterPoses(poses, N, { cutoff: 2.5 });
  const seen = modes.flatMap((m) => m.members).sort((a, b) => a - b);
  assert.deepEqual(seen, [0, 1, 2, 3, 4, 5]);
});

test('modes come out best score first, and each is led by its own best pose', () => {
  const poses = threeKnots();
  const modes = clusterPoses(poses, N, { cutoff: 2.5 });
  for (let i = 1; i < modes.length; i++) {
    assert.ok(modes[i - 1].best <= modes[i].best, 'modes must be sorted by best score');
  }
  for (const m of modes) {
    const memberScores = m.members.map((i) => poses[i].score);
    assert.equal(poses[m.leader].score, Math.min(...memberScores),
      'the leader must be the best-scoring member of its own mode');
  }
});

test('spread and rmsdToBest describe the mode they are attached to', () => {
  const poses = threeKnots();
  const modes = clusterPoses(poses, N, { cutoff: 2.5 });
  assert.equal(modes[0].best, -9.0);
  assert.equal(modes[0].worst, -8.6);
  assert.ok(Math.abs(modes[0].spread - 0.4) < 1e-6, `spread was ${modes[0].spread}`);
  assert.equal(modes[0].rmsdToBest, 0, 'the best mode is zero from itself');
  assert.ok(modes[1].rmsdToBest > 4, `the second mode sits ${modes[1].rmsdToBest} A away, expected over 4`);
});

test('a coarser cutoff merges modes and a finer one splits them', () => {
  const poses = threeKnots();
  assert.equal(clusterPoses(poses, N, { cutoff: 2.5 }).length, 3);
  assert.equal(clusterPoses(poses, N, { cutoff: 20 }).length, 1, 'a cutoff past every separation gives one mode');
  assert.equal(clusterPoses(poses, N, { cutoff: 0.01 }).length, 6, 'a cutoff under the wobble gives one mode per pose');
});

test('an empty list clusters to nothing rather than throwing', () => {
  assert.deepEqual(clusterPoses([], N), []);
  assert.deepEqual(clusterPoses(null, N), []);
});

test('a clear winner is reported as discriminating, with the gap stated', () => {
  const modes = clusterPoses(threeKnots(), N, { cutoff: 2.5 });
  const v = discrimination(modes);
  assert.equal(v.discriminates, true);
  assert.ok(Math.abs(v.gap - 0.8) < 1e-6, `gap was ${v.gap}, expected 0.8`);
  assert.equal(v.modes, 3);
  assert.equal(v.margin, DEFAULT_MARGIN);
});

test('modes within the margin are reported as not a preference', () => {
  // Two knots 6 A apart whose scores differ by 0.1 — well inside any plausible margin.
  const poses = [pose(0, -9.0), pose(6, -8.9)];
  const v = discrimination(clusterPoses(poses, N, { cutoff: 2.5 }));
  assert.equal(v.discriminates, false);
  assert.ok(Math.abs(v.gap - 0.1) < 1e-6);
  assert.match(v.note, /not a preference/);
  assert.ok(v.runnerUpRmsd > 4, 'the note must carry how far away the rival pose actually is');
});

test('the margin is honoured, so a caller can set its own threshold', () => {
  const modes = clusterPoses(threeKnots(), N, { cutoff: 2.5 }); // gap 0.8
  assert.equal(discrimination(modes, { margin: 0.5 }).discriminates, true);
  assert.equal(discrimination(modes, { margin: 1.5 }).discriminates, false);
  assert.equal(discrimination(modes, { margin: 0.8 }).discriminates, true, 'a gap exactly at the margin counts');
});

test('one mode is null, not true: no rival is not the same as a choice', () => {
  const v = discrimination(clusterPoses([pose(0, -9.0)], N, { cutoff: 2.5 }));
  assert.equal(v.discriminates, null);
  assert.equal(v.modes, 1);
  assert.equal(v.gap, null);
  assert.match(v.note, /nothing to compare/);
});

test('no poses at all is reported, not guessed at', () => {
  const v = discrimination([]);
  assert.equal(v.discriminates, null);
  assert.equal(v.modes, 0);
  assert.equal(v.note, 'no poses');
});

test('every verdict that states a margin admits the margin is uncalibrated', () => {
  const cases = [
    discrimination(clusterPoses(threeKnots(), N, { cutoff: 2.5 })),
    discrimination(clusterPoses([pose(0, -9.0), pose(6, -8.9)], N, { cutoff: 2.5 })),
    discrimination(clusterPoses([pose(0, -9.0)], N, { cutoff: 2.5 })),
  ];
  for (const v of cases) {
    assert.ok(v.note.includes(MARGIN_IS_UNCALIBRATED),
      `a verdict that leans on the margin must say it is uncalibrated: ${v.note}`);
  }
  assert.match(MARGIN_IS_UNCALIBRATED, /not a measured|convention/,
    'the disclaimer must actually disclaim, not just exist');
});

test('poseSummary gives the same answer as calling both halves', () => {
  const poses = threeKnots();
  const s = poseSummary(poses, N, { cutoff: 2.5 });
  const modes = clusterPoses(poses, N, { cutoff: 2.5 });
  assert.deepEqual(s.modes, modes);
  assert.deepEqual(s.verdict, discrimination(modes));
});

test('clustering does not mutate the poses it was given', () => {
  const poses = threeKnots();
  const before = poses.map((p) => Array.from(p.coords));
  const order = poses.map((p) => p.score);
  clusterPoses(poses, N, { cutoff: 2.5 });
  assert.deepEqual(poses.map((p) => Array.from(p.coords)), before, 'coordinates must be untouched');
  assert.deepEqual(poses.map((p) => p.score), order, 'the input array must not be re-sorted in place');
});
