// Rescoring: three terms the Vina-shaped function in dock.js does not have.
//
// The eleven-case re-docking benchmark says where the problem is. Nine of eleven cases are *reachable* —
// the search generates a pose within 2 Å of the crystal — and four of the six failures are ranking
// failures, where that good pose was found and the scoring function put something wrong above it. In the
// GSK-3β case it ranked a 0.54 Å pose below a 6.82 Å one. Perfect ranking over poses already being produced
// would take the benchmark from 45% to 82% without touching the search.
//
// So this is a rescoring pass, not a search change. It adds three terms chosen because each one is a known
// blind spot of this class of function and each matches a recorded failure:
//
//   1. BURIED UNSATISFIED POLAR. Desolvating a donor or acceptor and giving it nothing to hydrogen bond to
//      costs real energy. vinaScore charges nothing for it: gauss1, gauss2 and hydrophobic all reward the
//      close packing, and the missing hydrogen bond simply fails to earn its own bonus. A decoy that buries
//      a polar group in a greasy sub-pocket therefore scores like a good pose. Kinase sites — CDK5, GSK-3β,
//      both recorded scoring failures — are full of places to do exactly that.
//
//   2. METAL COORDINATION. vinaScore has no metal term at all. Carbonic anhydrase II (1OQ5) is a recorded
//      scoring failure, and celecoxib binds it by putting a sulfonamide nitrogen on the catalytic zinc; a
//      pose that makes that bond earns nothing for it, so a decoy elsewhere in the pocket can win. MetAP2
//      (1R58) is a dinuclear metalloenzyme and also fails.
//
//   3. INTERNAL CLASH. vinaScore sees protein–ligand pairs only, which iteration 8 noted and did not fix:
//      a conformer folded through itself is free. Any pose whose own atoms interpenetrate should lose.
//
// WEIGHTS ARE NOT CALIBRATED. This is the honest centre of the module. Fitting them means running the
// eleven-case benchmark, measuring how often each term flips a ranking the right way, and tuning against
// that — which needs structures from the RCSB and a network this environment does not have. The defaults
// below are round numbers chosen to be the same order as the Vina terms they sit beside, every caller can
// override them, and every result this module returns carries the disclaimer. A rescoring function with
// invented weights that is *described* as calibrated would be a worse artefact than no rescoring at all.
import { vinaScore } from './dock.js';
import { topoDist } from './md.js';

// Divalent and transition metals that coordinate ligand heteroatoms. Deliberately not the full IONS set
// from elements.js: a chloride or a sodium in a structure is usually a counter-ion or a crystallisation
// additive, and treating one as a coordination centre would reward poses for sitting next to salt.
export const COORDINATING_METALS = new Set(['ZN', 'MG', 'MN', 'FE', 'FE2', 'CU', 'CU1', 'NI', 'CO', 'CD']);

export const WEIGHTS_ARE_UNCALIBRATED =
  'rescoring weights are uncalibrated: fitting them needs the eleven-case benchmark, which needs the network';

export const DEFAULT_WEIGHTS = {
  unsatisfied: 0.45,   // per buried polar atom with no partner — a penalty
  metal: -0.80,        // per coordinating contact — a reward, so negative like the other favourable terms
  clash: 1.20,         // per interpenetrating intra-ligand pair — a penalty
};

const BURIAL_RADIUS = 5.0;      // Å, the shell counted to decide whether an atom is buried
const BURIAL_COUNT = 12;        // protein heavy atoms within that shell before "buried" is fair
const HBOND_MAX = 3.5;          // Å, donor-acceptor heavy-atom distance that counts as satisfied
const METAL_MIN = 1.7;          // Å, below this the atoms are interpenetrating, not coordinating
const METAL_MAX = 2.7;          // Å, a generous upper bound on a first coordination shell
const CLASH_DISTANCE = 2.6;     // Å, intra-ligand heavy atoms closer than this are interpenetrating

/**
 * Count the three terms for one pose. Returns plain counts, so a caller can weight them differently or
 * inspect them without re-deriving anything.
 *
 * { unsatisfied, metal, clash, buried, polar }
 */
export function rescoreTerms(grid, lig, coords) {
  const st = grid.st;
  const near = [];
  let unsatisfied = 0, metal = 0, buried = 0, polar = 0;

  for (const i of lig.heavy) {
    const x = coords[i * 3], y = coords[i * 3 + 1], z = coords[i * 3 + 2];
    const isDonor = lig.donor[i], isAcceptor = lig.acceptor[i];

    // Metal coordination: any ligand heteroatom in the first shell of a coordinating metal.
    if (isDonor || isAcceptor || lig.element[i] === 'S') {
      grid.near(x, y, z, METAL_MAX, near);
      for (const j of near) {
        if (!COORDINATING_METALS.has(st.element[j])) continue;
        const d = Math.hypot(st.pos[j * 3] - x, st.pos[j * 3 + 1] - y, st.pos[j * 3 + 2] - z);
        if (d >= METAL_MIN) { metal++; break; } // one contact per ligand atom, not per metal
      }
    }

    if (!(isDonor || isAcceptor)) continue;
    polar++;

    // Burial, then satisfaction. Both are measured from the same neighbour query.
    grid.near(x, y, z, BURIAL_RADIUS, near);
    if (near.length < BURIAL_COUNT) continue;
    buried++;

    let satisfied = false;
    for (const j of near) {
      const d = Math.hypot(st.pos[j * 3] - x, st.pos[j * 3 + 1] - y, st.pos[j * 3 + 2] - z);
      // A metal satisfies a lone pair as well as a hydrogen bond would, but only at coordination distance.
      // An earlier draft accepted a metal anywhere in the 5 Å burial shell, which let a zinc 4 Å away
      // excuse a completely unsatisfied oxygen. Probing the module on synthetic geometry caught it.
      if (COORDINATING_METALS.has(st.element[j])) {
        if (d <= METAL_MAX) { satisfied = true; break; }
        continue;
      }
      const partner = (isDonor && st.acceptor[j]) || (isAcceptor && st.donor[j]);
      if (partner && d <= HBOND_MAX) { satisfied = true; break; }
    }
    if (!satisfied) unsatisfied++;
  }

  return { unsatisfied, metal, clash: internalClashes(lig, coords), buried, polar };
}

/**
 * Intra-ligand heavy-atom pairs four or more bonds apart that are closer than CLASH_DISTANCE. Pairs nearer
 * than that in the bond graph are held by the geometry itself and must not be counted.
 */
export function internalClashes(lig, coords) {
  const n = lig.n;
  const topo = topoDist(lig, 4);
  let clashes = 0;
  for (let a = 0; a < lig.heavy.length; a++) {
    for (let b = a + 1; b < lig.heavy.length; b++) {
      const i = lig.heavy[a], j = lig.heavy[b];
      if (topo[i * n + j] < 4) continue;
      const dx = coords[i * 3] - coords[j * 3];
      const dy = coords[i * 3 + 1] - coords[j * 3 + 1];
      const dz = coords[i * 3 + 2] - coords[j * 3 + 2];
      if (dx * dx + dy * dy + dz * dz < CLASH_DISTANCE * CLASH_DISTANCE) clashes++;
    }
  }
  return clashes;
}

/**
 * vinaScore plus the weighted terms. Returns { base, total, delta, terms, weights, note }.
 *
 * With every weight set to zero, `total` equals `base` exactly — so the rescoring can always be turned off
 * and shown to have been turned off, which is the property a reviewer should check first.
 */
export function rescore(grid, lig, coords, { weights = {}, nrot = null } = {}) {
  const w = { ...DEFAULT_WEIGHTS, ...weights };
  const base = vinaScore(grid, lig, coords, { nrot });
  const terms = rescoreTerms(grid, lig, coords);
  const delta = w.unsatisfied * terms.unsatisfied + w.metal * terms.metal + w.clash * terms.clash;
  return {
    base,
    total: base + delta,
    delta: +delta.toFixed(4),
    terms,
    weights: w,
    note: WEIGHTS_ARE_UNCALIBRATED,
  };
}

/**
 * Rescore a ranked list and re-sort. Each pose keeps `base`, `total` and `rankChange` — how far it moved —
 * because the only interesting thing a rescoring pass does is change an order, and a caller that cannot see
 * what moved cannot judge whether it helped.
 *
 * Returns { poses, moved, note }: `moved` is how many poses changed position.
 */
export function rerank(grid, lig, poses, opts = {}) {
  const scored = poses.map((p, i) => {
    const r = rescore(grid, lig, p.coords, opts);
    return { ...p, base: r.base, score: r.total, rescoreTerms: r.terms, rescoreDelta: r.delta, wasRank: i };
  });
  scored.sort((a, b) => a.score - b.score);
  let moved = 0;
  scored.forEach((p, i) => { p.rankChange = p.wasRank - i; if (p.rankChange !== 0) moved++; });
  return { poses: scored, moved, note: WEIGHTS_ARE_UNCALIBRATED };
}
