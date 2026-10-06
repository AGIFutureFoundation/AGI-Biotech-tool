// Torsional refinement of a docked pose.
//
// js/refine.js tightens a pose as a rigid body: it slides and turns the whole molecule. But a ligand with
// rotatable bonds has more freedom than that, and the Monte Carlo search in dock.js samples those torsions
// coarsely. This module searches them directly, one dihedral at a time, with the same discipline refine.js
// uses: a shrinking angular step, and only ever a strict improvement, so a refined pose cannot score worse
// than the one it started from.
//
// Rotating the atoms on one side of a bond about that bond's own axis changes exactly one dihedral. Every
// bond length and every bond angle in the molecule is left alone, because the hinge atoms lie on the axis
// and nothing crosses between the two sides. That is the invariant the tests check first.
//
// What this does not do: change the scoring function, add an internal-strain term, or let the ligand pass
// through itself. vinaScore sees protein-ligand contacts only, so a torsion that folds the ligand onto
// itself costs nothing here. refineFlexible therefore stays close to the conformer it was handed — it
// polishes a pose, it does not do conformer generation.
import { vinaScore, rotatableBonds } from './dock.js';
import { refinePose } from './refine.js';

/** The hinge for one rotatable bond: a unit axis from atom `a` to atom `b`, pivoting at `a`. */
export function torsionAxis(coords, t) {
  const ax = coords[t.a * 3], ay = coords[t.a * 3 + 1], az = coords[t.a * 3 + 2];
  let ux = coords[t.b * 3] - ax, uy = coords[t.b * 3 + 1] - ay, uz = coords[t.b * 3 + 2] - az;
  const len = Math.hypot(ux, uy, uz);
  if (!(len > 1e-9)) return null; // coincident atoms have no axis; skip the bond rather than divide by zero
  ux /= len; uy /= len; uz /= len;
  return { pivot: [ax, ay, az], axis: [ux, uy, uz] };
}

/**
 * Rotate the moving side of one rotatable bond in place. Returns false if the bond has no usable axis.
 */
export function rotateTorsion(coords, t, angle) {
  const h = torsionAxis(coords, t);
  if (!h) return false;
  const [px, py, pz] = h.pivot, [ux, uy, uz] = h.axis;
  const c = Math.cos(angle), s = Math.sin(angle), k = 1 - c;
  for (const i of t.moving) {
    const x = coords[i * 3] - px, y = coords[i * 3 + 1] - py, z = coords[i * 3 + 2] - pz;
    coords[i * 3] = px + (k * ux * ux + c) * x + (k * ux * uy - s * uz) * y + (k * ux * uz + s * uy) * z;
    coords[i * 3 + 1] = py + (k * ux * uy + s * uz) * x + (k * uy * uy + c) * y + (k * uy * uz - s * ux) * z;
    coords[i * 3 + 2] = pz + (k * ux * uz - s * uy) * x + (k * uy * uz + s * ux) * y + (k * uz * uz + c) * z;
  }
  return true;
}

/**
 * Search the ligand's rotatable bonds by pattern search. Each round probes every torsion in both
 * directions at the current step; when no probe helps, the step shrinks.
 *
 * Returns { coords, score, startScore, improved, evaluations, torsions }. `coords` is a new array and the
 * input is never modified. A ligand with no rotatable bonds returns its input unchanged, scored once.
 */
export function refineTorsions(grid, lig, coords, {
  angle = 0.35,          // radians, starting step — about 20 degrees
  minAngle = 0.03,       // about 1.7 degrees
  shrink = 0.5,
  maxEvaluations = 2000,
  torsions = null,
  nrot = null,
} = {}) {
  const rot = torsions || rotatableBonds(lig);
  const best = Float32Array.from(coords);
  const trial = new Float32Array(best.length);
  let evaluations = 0;
  const score = (c) => { evaluations++; return vinaScore(grid, lig, c, { nrot }); };

  const startScore = score(best);
  let bestScore = startScore;

  let a = angle;
  while (rot.length && a >= minAngle && evaluations < maxEvaluations) {
    let moved = false;
    for (const t of rot) {
      for (const sign of [1, -1]) {
        if (evaluations >= maxEvaluations) break;
        trial.set(best);
        if (!rotateTorsion(trial, t, a * sign)) continue;
        const sc = score(trial);
        if (sc < bestScore) { best.set(trial); bestScore = sc; moved = true; }
      }
    }
    if (!moved) a *= shrink;
  }

  return {
    coords: best,
    score: bestScore,
    startScore,
    improved: +(startScore - bestScore).toFixed(4),
    evaluations,
    torsions: rot.length,
  };
}

/**
 * Alternate rigid-body and torsional refinement until a full pass of both stops helping. Moving a torsion
 * shifts the atoms the rigid-body step was balancing, and vice versa, so one pass of each is not enough.
 *
 * Returns the same shape as refineTorsions plus `passes`.
 */
export function refineFlexible(grid, lig, coords, {
  maxPasses = 4,
  rigid = {},
  torsional = {},
  nrot = null,
} = {}) {
  const rot = rotatableBonds(lig);
  let current = Float32Array.from(coords);
  let startScore = null;
  let bestScore = null;
  let evaluations = 0;
  let passes = 0;

  for (let p = 0; p < maxPasses; p++) {
    passes++;
    const r = refinePose(grid, lig, current, { ...rigid, nrot });
    const t = refineTorsions(grid, lig, r.coords, { ...torsional, torsions: rot, nrot });
    evaluations += r.evaluations + t.evaluations;
    if (startScore === null) { startScore = r.startScore; bestScore = r.startScore; }
    // Both stages only accept strict improvements, so t.score is the best this pass reached. Each pass
    // restarts the rigid step coarse, so a pass that gains nothing is the signal to stop.
    const gained = bestScore - t.score;
    current = t.coords;
    bestScore = t.score;
    if (gained <= 1e-9) break;
  }

  return {
    coords: current,
    score: bestScore,
    startScore,
    improved: +(startScore - bestScore).toFixed(4),
    evaluations,
    torsions: rot.length,
    passes,
  };
}

/**
 * Refine every pose in a ranked list flexibly and re-sort, since refinement can change the order.
 * Poses are plain `{ coords, score }` objects as dockLigand returns them.
 */
export function refineAllFlexible(grid, lig, poses, opts = {}) {
  const refined = poses.map((p) => {
    const r = refineFlexible(grid, lig, p.coords, opts);
    return { ...p, coords: r.coords, score: r.score, refinedBy: r.improved, passes: r.passes };
  });
  refined.sort((a, b) => a.score - b.score);
  return refined;
}
