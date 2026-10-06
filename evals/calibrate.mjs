// Weight calibration for js/rescore.js.
//
// Iteration 20 added three rescoring terms with round-number weights and said plainly that they were not
// calibrated, because calibrating them means running the eleven-case re-docking benchmark and the network is
// blocked. This module is the part of that job that does NOT need the network, so that when the network
// returns the calibration is one command rather than a design problem.
//
// The split that makes it work: docking a case and computing its rescoring terms is expensive and needs
// structures from the RCSB, but it only has to happen once. What comes out is, per case, a list of poses
// each carrying its RMSD to the crystal, its base vinaScore, and its term counts. Searching weight space
// over that is pure arithmetic — no structures, no network, no docking. So `collect` needs the network and
// everything after it does not, including re-running the sweep later with different candidates.
//
// THE STATISTICAL PROBLEM, stated before the code rather than after it. There are eleven cases and three
// free weights. Fitting three parameters to eleven binary outcomes will produce an in-sample improvement
// almost regardless of whether the terms are real — that is what fitting does. An in-sample success count
// from this harness is therefore not evidence of anything, and `evaluate` is not the function to publish.
// `leaveOneOut` is the better one: it fits on ten cases and tests on the eleventh, eleven times over, so the
// number it reports was never seen during fitting.
//
// But it is not a cure, and the tests measured that rather than assuming it. Feeding this harness eleven
// cases with pure-noise term counts produces an in-sample "gain" of between one and six cases out of eleven
// depending on the seed — from a base score that solves none — and leave-one-out sometimes reports exactly
// the same gain, because on this few cases the same weight set often wins in every fold. So leave-one-out is
// the less flattering number and still not a guarantee. The honest use of this harness is to generate a
// hypothesis about which terms matter, to be tested on cases outside the eleven; it cannot validate one.
// Every result carries the warning, and the in-sample and out-of-sample figures are returned together so
// they cannot be quoted apart.

export const OVERFITTING_WARNING =
  'eleven cases, three free weights: an in-sample gain is not evidence, and leave-one-out is less flattering '
  + 'but not a guarantee — on this few cases it can report a spurious gain too. Treat any result as a '
  + 'hypothesis to test on cases outside the benchmark.';

export const SUCCESS_THRESHOLD = 2.0; // Å, the same threshold evals/redock.mjs uses to call a case solved

/** The rescored value of one pose under one weight set. The arithmetic that `js/rescore.js` does, replayed. */
export function rescoreValue(pose, weights) {
  const t = pose.terms || {};
  return pose.base
    + (weights.unsatisfied || 0) * (t.unsatisfied || 0)
    + (weights.metal || 0) * (t.metal || 0)
    + (weights.clash || 0) * (t.clash || 0);
}

/**
 * Score one weight set against a collected dump.
 *
 * Returns { solved, total, reachable, meanTopRmsd, topRmsds, weights, warning }.
 *
 * `reachable` is the number of cases where *some* pose is within the threshold. It does not depend on the
 * weights, and it is the ceiling any rescoring can reach — printed here so a gain can always be read
 * against what was available rather than against zero.
 */
export function evaluate(dump, weights, { threshold = SUCCESS_THRESHOLD } = {}) {
  const topRmsds = [];
  let solved = 0, reachable = 0;
  for (const c of dump.cases) {
    if (!c.poses || !c.poses.length) { topRmsds.push(null); continue; }
    if (c.poses.some((p) => p.rmsd <= threshold)) reachable++;
    // Deterministic argmin: ties go to the earlier pose, so a sweep is reproducible.
    let best = c.poses[0], bestVal = rescoreValue(c.poses[0], weights);
    for (const p of c.poses.slice(1)) {
      const v = rescoreValue(p, weights);
      if (v < bestVal) { best = p; bestVal = v; }
    }
    topRmsds.push(best.rmsd);
    if (best.rmsd <= threshold) solved++;
  }
  const scored = topRmsds.filter((r) => r != null);
  return {
    solved,
    total: dump.cases.length,
    reachable,
    meanTopRmsd: scored.length ? +(scored.reduce((a, b) => a + b, 0) / scored.length).toFixed(3) : null,
    topRmsds,
    weights,
    warning: OVERFITTING_WARNING,
  };
}

/** Every combination of the candidate values, in a deterministic order. */
export function candidateGrid({ unsatisfied = [0], metal = [0], clash = [0] } = {}) {
  const out = [];
  for (const u of unsatisfied) for (const m of metal) for (const c of clash) {
    out.push({ unsatisfied: u, metal: m, clash: c });
  }
  return out;
}

// Better means more cases solved; on a tie, a lower mean top-pose RMSD; on a further tie, the weight set
// closer to all-zero, so the harness prefers the smaller correction when two do equally well.
function better(a, b) {
  if (a.solved !== b.solved) return a.solved > b.solved;
  const am = a.meanTopRmsd ?? Infinity, bm = b.meanTopRmsd ?? Infinity;
  if (am !== bm) return am < bm;
  const mag = (w) => Math.abs(w.unsatisfied) + Math.abs(w.metal) + Math.abs(w.clash);
  return mag(a.weights) < mag(b.weights);
}

/** Evaluate every candidate and return them ranked best first. */
export function sweep(dump, candidates, opts = {}) {
  const results = candidates.map((w) => evaluate(dump, w, opts));
  results.sort((a, b) => (better(a, b) ? -1 : better(b, a) ? 1 : 0));
  return results;
}

/** The single best candidate, by the ordering above. */
export function fit(dump, candidates, opts = {}) {
  return sweep(dump, candidates, opts)[0] || null;
}

/**
 * Leave-one-out cross-validation: for each case, fit on the other ten and test on the held-out one.
 *
 * This is the figure to publish. It is pessimistic by construction, which is the point — the held-out case
 * never influenced the weights that were applied to it, so a gain here is a gain on a case the fit had not
 * seen. With eleven cases it is still a small sample and still not a validated model; it is simply the
 * least self-flattering number this data can produce.
 *
 * Returns { outOfSampleSolved, total, perCase, inSample, chosenWeights, warning }.
 */
export function leaveOneOut(dump, candidates, opts = {}) {
  const threshold = opts.threshold ?? SUCCESS_THRESHOLD;
  const perCase = [];
  let outOfSampleSolved = 0;

  for (let held = 0; held < dump.cases.length; held++) {
    const trainCases = dump.cases.filter((_, i) => i !== held);
    if (!trainCases.length) break;
    const chosen = fit({ ...dump, cases: trainCases }, candidates, opts);
    const test = evaluate({ ...dump, cases: [dump.cases[held]] }, chosen.weights, opts);
    const ok = test.solved === 1;
    if (ok) outOfSampleSolved++;
    perCase.push({
      id: dump.cases[held].id ?? held,
      weights: chosen.weights,
      topRmsd: test.topRmsds[0],
      solved: ok,
    });
  }

  return {
    outOfSampleSolved,
    total: dump.cases.length,
    perCase,
    // Returned alongside so the two can never be quoted apart. The in-sample figure is the flattering one.
    inSample: fit(dump, candidates, opts),
    threshold,
    warning: OVERFITTING_WARNING,
  };
}

/**
 * A one-line summary that leads with the out-of-sample number and names the ceiling, because an in-sample
 * success count quoted on its own is the most misleading thing this module could produce.
 */
export function describe(loo) {
  const inS = loo.inSample;
  return `${loo.outOfSampleSolved}/${loo.total} solved out-of-sample `
    + `(in-sample ${inS.solved}/${inS.total}, ceiling ${inS.reachable}/${inS.total}) · ${OVERFITTING_WARNING}`;
}

/**
 * Collect a dump. THIS IS THE ONLY FUNCTION HERE THAT NEEDS THE NETWORK: it docks each benchmark case and
 * records every pose with its RMSD, base score and rescoring terms. Everything above operates on its output
 * and runs offline, so a dump written once can be swept repeatedly without re-docking.
 *
 * It is written but has never been run — the sandbox this was built in blocks the RCSB. When it first runs,
 * check that the pose counts are plausible and that `reachable` from `evaluate` matches the `reachable`
 * figure `evals/redock.mjs` reports, which is a cross-check between two independent paths to the same
 * number.
 */
export async function collect(cases, { runs = 12, steps = 3000, seed = 20260101 } = {}) {
  const { runCase } = await import('./redock.mjs');
  const { ProteinGrid } = await import('../js/dock.js');
  const { rescoreTerms } = await import('../js/rescore.js');
  const out = [];
  for (const c of cases) {
    const r = await runCase(c, { runs, steps, seed });
    if (r.error || !r.poses) { out.push({ id: c.pdb, error: r.error || 'no poses returned' }); continue; }
    const grid = new ProteinGrid(r.protein, 4);
    out.push({
      id: c.pdb,
      poses: r.poses.map((p) => ({
        rmsd: p.rmsd,
        base: p.score,
        terms: rescoreTerms(grid, r.ligand, p.coords),
      })),
    });
  }
  return { generated: new Date().toISOString(), runs, steps, seed, cases: out };
}
