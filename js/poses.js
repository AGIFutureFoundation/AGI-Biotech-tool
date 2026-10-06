// Binding modes, and whether the score actually chose between them.
//
// dockLigand returns a ranked list, already thinned so no two poses are within 1.5 A of each other. A
// ranked list invites one reading: the first row is the answer. For the two complexes this tool gets right
// that reading is fair. For the two it gets wrong — a long flexible ligand in a shallow groove — it is not,
// and the reason is visible in the numbers the list throws away. Several placements score within a hair of
// each other, the search picks whichever won by a rounding error, and the list presents it as a result.
//
// So this module does two things. It groups the surviving poses into binding modes at a cutoff coarser than
// the de-duplication, which is the unit a chemist actually reasons about. And it reports whether the best
// mode is separated from the next one by more than a stated margin — that is, whether the ranking carries
// information or is noise wearing a sort order.
//
// What this does not do: make the score better. Nothing here changes a single term. It makes an existing
// weakness legible instead of hiding it behind a sorted table, which is the most useful thing that can be
// done about a weakness you cannot yet fix.
import { rmsd } from './dock.js';

// The default margin below which two modes are called indistinguishable.
//
// This is a CONVENTION, not a measurement. Calibrating it would mean running the re-docking benchmark and
// asking how large a score gap has to be before the better-scoring pose is reliably the closer one to the
// crystal — and that benchmark needs structures fetched over the network. Until that is run, 0.5 is a
// round number chosen to be cautious, every caller may override it, and the note this module produces says
// so in as many words rather than implying a rigour it does not have.
export const DEFAULT_MARGIN = 0.5;
export const MARGIN_IS_UNCALIBRATED =
  'margin is a convention, not a measured score resolution: the calibrating benchmark has not been run';

/**
 * Group poses into binding modes by greedy leader clustering in score order.
 *
 * The best-scoring pose starts the first mode; each remaining pose joins the first mode whose leader it is
 * within `cutoff` of, or starts a new one. Leader clustering is what AutoDock and Vina report, and taking
 * the leaders in score order means each mode is represented by its own best pose.
 *
 * Returns modes sorted best score first, each:
 *   { leader, members, population, best, worst, spread, rmsdToBest }
 * `members` are indices into the input array, so a caller can map back to its own pose objects.
 */
export function clusterPoses(poses, n, { cutoff = 2.5 } = {}) {
  if (!poses || !poses.length) return [];
  const order = poses.map((p, i) => i).sort((a, b) => poses[a].score - poses[b].score);
  const modes = [];
  for (const i of order) {
    const home = modes.find((m) => rmsd(poses[i].coords, poses[m.leader].coords, n) < cutoff);
    if (home) home.members.push(i);
    else modes.push({ leader: i, members: [i] });
  }
  const bestCoords = poses[order[0]].coords;
  return modes.map((m) => {
    const scores = m.members.map((i) => poses[i].score);
    return {
      leader: m.leader,
      members: m.members,
      population: m.members.length,
      best: Math.min(...scores),
      worst: Math.max(...scores),
      spread: +(Math.max(...scores) - Math.min(...scores)).toFixed(3),
      rmsdToBest: +rmsd(poses[m.leader].coords, bestCoords, n).toFixed(2),
    };
  }).sort((a, b) => a.best - b.best);
}

/**
 * Did the score choose, or did it shrug?
 *
 * Returns { discriminates, modes, gap, runnerUpRmsd, margin, note }. `gap` is the score difference between
 * the best mode and the next one; `discriminates` is false when that gap is below `margin`, meaning the
 * ranking should not be read as a preference. With one mode there is nothing to discriminate between and
 * `discriminates` is null rather than true — absence of a rival is not evidence of a choice.
 */
export function discrimination(modes, { margin = DEFAULT_MARGIN } = {}) {
  if (!modes || !modes.length) {
    return { discriminates: null, modes: 0, gap: null, runnerUpRmsd: null, margin, note: 'no poses' };
  }
  if (modes.length === 1) {
    return {
      discriminates: null, modes: 1, gap: null, runnerUpRmsd: null, margin,
      note: `one binding mode found; nothing to compare it against (${MARGIN_IS_UNCALIBRATED})`,
    };
  }
  // Decide on the raw gap, present the rounded one. Rounding first made the
  // comparison lie at the boundary: a 0.4996 gap becomes 0.500, which passes
  // `>= 0.5` and reports a preference the measurement does not support. The
  // whole point of this function is to refuse to call a near-tie a choice, so
  // getting it wrong exactly at the margin is the one place it cannot afford to.
  const rawGap = modes[1].best - modes[0].best;
  const gap = +rawGap.toFixed(3);
  const runnerUpRmsd = modes[1].rmsdToBest;
  const discriminates = rawGap >= margin;
  const note = discriminates
    ? `top mode leads the next by ${gap} at ${runnerUpRmsd} A, above the ${margin} margin `
      + `(${MARGIN_IS_UNCALIBRATED})`
    : `${modes.length} modes within ${margin}: the next-best sits ${runnerUpRmsd} A away and only ${gap} `
      + `behind, so this ranking is not a preference (${MARGIN_IS_UNCALIBRATED})`;
  return { discriminates, modes: modes.length, gap, runnerUpRmsd, margin, note };
}

/**
 * Cluster and judge in one call. Returns { modes, verdict } with the shapes above.
 */
export function poseSummary(poses, n, { cutoff = 2.5, margin = DEFAULT_MARGIN } = {}) {
  const modes = clusterPoses(poses, n, { cutoff });
  return { modes, verdict: discrimination(modes, { margin }) };
}
