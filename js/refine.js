// Local refinement of a docked pose.
//
// The Monte Carlo search in dock.js samples widely but lands near a minimum rather than in it: its last
// accepted move is whatever random step happened to be accepted, not the best pose in that basin. Vina
// itself follows every MC step with a quasi-Newton polish for exactly this reason. This is the cheap
// equivalent — a pattern search over the six rigid-body degrees of freedom with a shrinking step — and
// it only ever accepts a strict improvement, so a refined pose can never score worse than the one it
// started from.
//
// What this does not do: change the scoring function, or move torsions. It tightens a pose inside the
// basin the search already found. A pose placed in the wrong pocket is still in the wrong pocket.
import { vinaScore, centroid } from './dock.js';

const AXES = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];

/** Rotate `coords` in place about `pivot` around a unit axis. */
function rotate(coords, n, pivot, axis, angle) {
  const [ux, uy, uz] = axis;
  const c = Math.cos(angle), s = Math.sin(angle), t = 1 - c;
  const [px, py, pz] = pivot;
  for (let i = 0; i < n; i++) {
    const x = coords[i * 3] - px, y = coords[i * 3 + 1] - py, z = coords[i * 3 + 2] - pz;
    coords[i * 3] = px + (t * ux * ux + c) * x + (t * ux * uy - s * uz) * y + (t * ux * uz + s * uy) * z;
    coords[i * 3 + 1] = py + (t * ux * uy + s * uz) * x + (t * uy * uy + c) * y + (t * uy * uz - s * ux) * z;
    coords[i * 3 + 2] = pz + (t * ux * uz - s * uy) * x + (t * uy * uz + s * ux) * y + (t * uz * uz + c) * z;
  }
}

function translate(coords, n, dx, dy, dz) {
  for (let i = 0; i < n; i++) {
    coords[i * 3] += dx; coords[i * 3 + 1] += dy; coords[i * 3 + 2] += dz;
  }
}

/**
 * Tighten a pose by pattern search over translation and rotation.
 *
 * Returns { coords, score, startScore, improved, evaluations }. `coords` is a new array; the input is
 * never modified, so a caller can compare before and after.
 */
export function refinePose(grid, lig, coords, {
  step = 0.6,            // ångström, starting translation step
  angle = 0.12,          // radians, starting rotation step
  minStep = 0.05,
  shrink = 0.5,
  maxEvaluations = 1500,
  nrot = null,
} = {}) {
  const n = lig.n;
  const best = Float32Array.from(coords);
  const trial = new Float32Array(best.length);
  let evaluations = 0;
  const score = (c) => { evaluations++; return vinaScore(grid, lig, c, { nrot }); };

  const startScore = score(best);
  let bestScore = startScore;
  let s = step, a = angle;

  while (s >= minStep && evaluations < maxEvaluations) {
    let movedThisRound = false;

    // Six translation probes: plus and minus along each axis.
    for (const [ax, ay, az] of AXES) {
      for (const sign of [1, -1]) {
        if (evaluations >= maxEvaluations) break;
        trial.set(best);
        translate(trial, n, ax * s * sign, ay * s * sign, az * s * sign);
        const sc = score(trial);
        if (sc < bestScore) { best.set(trial); bestScore = sc; movedThisRound = true; }
      }
    }

    // Six rotation probes about the ligand's own centroid, so a rotation never also translates it.
    const pivot = centroid(best, n);
    for (const axis of AXES) {
      for (const sign of [1, -1]) {
        if (evaluations >= maxEvaluations) break;
        trial.set(best);
        rotate(trial, n, pivot, axis, a * sign);
        const sc = score(trial);
        if (sc < bestScore) { best.set(trial); bestScore = sc; movedThisRound = true; }
      }
    }

    // Nothing helped at this scale, so look more finely.
    if (!movedThisRound) { s *= shrink; a *= shrink; }
  }

  return {
    coords: best,
    score: bestScore,
    startScore,
    improved: +(startScore - bestScore).toFixed(4),
    evaluations,
  };
}

/**
 * Refine every pose in a ranked list and re-sort, since refinement can change the order.
 * Poses are plain `{ coords, score }` objects as dockLigand returns them.
 */
export function refineAll(grid, lig, poses, opts = {}) {
  const refined = poses.map((p) => {
    const r = refinePose(grid, lig, p.coords, opts);
    return { ...p, coords: r.coords, score: r.score, refinedBy: r.improved };
  });
  refined.sort((a, b) => a.score - b.score);
  return refined;
}
