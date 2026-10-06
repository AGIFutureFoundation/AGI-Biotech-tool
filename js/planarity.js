// An exact-gradient planarity restraint for sp2 centres.
//
// js/md.js has a planarity term that keeps an sp2 centre in the plane of its three substituents. It pushes
// in the right direction and its forces sum to zero, but its force is not the exact gradient of its energy:
// it treats the plane normal as fixed, ignoring that the normal moves when the substituents do. Measured
// against a central finite difference, the error is about 19 percent when the centre is pyramidalised by
// 0.3 A and falls off from there — small displacements are the worst case, which is exactly the regime a
// minimiser spends its time in.
//
// That matters for two reasons. The FIRE minimiser steers on the sign of F·V and the energy together, so an
// inconsistent pair can make it shrink its timestep when it should grow it. And a force that is not a
// gradient does no definite work, so energy is not conserved along that coordinate during dynamics.
//
// This module is the drop-in replacement, derived properly. It is a new file rather than an edit to md.js
// because another session is working in that file; swapping it in is a one-line change recorded in
// docs/ROADMAP_LOOP.md.
//
// The geometry: with w = c - a, u = b - a, v = d - a, the plane normal is n = (u x v) / |u x v| and the
// signed distance from the centre to the substituent plane is h = w . n. The restraint is E = k h^2, and
// the gradient follows by differentiating h through the normalised cross product:
//
//   dh/dc = n
//   dh/db = v x g        where g = (w - h n) / |u x v|
//   dh/dd = g x u
//   dh/da = -(dh/dc + dh/db + dh/dd)        by translation invariance
//
// The dh/da line is not a shortcut: h depends on a only through w, u and v, all of which shift together
// when a moves, and the sum of the other three derivatives is exactly that dependence with the sign
// flipped. Taking it this way makes the forces sum to zero identically, in floating point as well as in
// algebra.

const cross = (ax, ay, az, bx, by, bz) => [ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx];

/**
 * Add the planarity restraint force for centre `c` against the plane of `a`, `b`, `d`, and return its
 * energy. Accumulates into `F` the way the other force terms in md.js do.
 *
 * Degenerate substituent geometry — three collinear or coincident substituents, where the plane is not
 * defined — contributes no energy and no force rather than a division by zero.
 */
export function planarityForce(P, F, c, a, b, d, k) {
  const ax = P[a * 3], ay = P[a * 3 + 1], az = P[a * 3 + 2];
  const ux = P[b * 3] - ax, uy = P[b * 3 + 1] - ay, uz = P[b * 3 + 2] - az;
  const vx = P[d * 3] - ax, vy = P[d * 3 + 1] - ay, vz = P[d * 3 + 2] - az;
  const wx = P[c * 3] - ax, wy = P[c * 3 + 1] - ay, wz = P[c * 3 + 2] - az;

  const [mx, my, mz] = cross(ux, uy, uz, vx, vy, vz);
  const A = Math.hypot(mx, my, mz);
  if (!(A > 1e-9)) return 0; // no plane to restrain to

  const nx = mx / A, ny = my / A, nz = mz / A;
  const h = wx * nx + wy * ny + wz * nz;

  // g = (w - h n) / A, the derivative of h with respect to the unnormalised normal.
  const gx = (wx - h * nx) / A, gy = (wy - h * ny) / A, gz = (wz - h * nz) / A;

  const [bx_, by_, bz_] = cross(vx, vy, vz, gx, gy, gz); // dh/db = v x g
  const [dx_, dy_, dz_] = cross(gx, gy, gz, ux, uy, uz); // dh/dd = g x u

  // Force is -dE/dx = -2 k h dh/dx.
  const s = -2 * k * h;
  F[c * 3] += s * nx; F[c * 3 + 1] += s * ny; F[c * 3 + 2] += s * nz;
  F[b * 3] += s * bx_; F[b * 3 + 1] += s * by_; F[b * 3 + 2] += s * bz_;
  F[d * 3] += s * dx_; F[d * 3 + 1] += s * dy_; F[d * 3 + 2] += s * dz_;
  F[a * 3] -= s * (nx + bx_ + dx_);
  F[a * 3 + 1] -= s * (ny + by_ + dy_);
  F[a * 3 + 2] -= s * (nz + bz_ + dz_);

  return k * h * h;
}

/**
 * The signed out-of-plane distance on its own, for tests and diagnostics. Returns 0 when the substituent
 * plane is degenerate, matching planarityForce.
 */
export function outOfPlane(P, c, a, b, d) {
  const ax = P[a * 3], ay = P[a * 3 + 1], az = P[a * 3 + 2];
  const ux = P[b * 3] - ax, uy = P[b * 3 + 1] - ay, uz = P[b * 3 + 2] - az;
  const vx = P[d * 3] - ax, vy = P[d * 3 + 1] - ay, vz = P[d * 3 + 2] - az;
  const [mx, my, mz] = cross(ux, uy, uz, vx, vy, vz);
  const A = Math.hypot(mx, my, mz);
  if (!(A > 1e-9)) return 0;
  return ((P[c * 3] - ax) * mx + (P[c * 3 + 1] - ay) * my + (P[c * 3 + 2] - az) * mz) / A;
}

/**
 * Apply the restraint to every sp2 centre in a ligand force field built by md.js's buildLigandFF, which
 * stores them as a flat [c, a, b, d, ...] list in `ff.planar`. Returns the total energy, so this can stand
 * in for the planarity block of ligandForces directly.
 */
export function planarityForces(ff, P, F, k = 40) {
  let E = 0;
  const PL = ff.planar;
  for (let i = 0; i < PL.length; i += 4) E += planarityForce(P, F, PL[i], PL[i + 1], PL[i + 2], PL[i + 3], k);
  return E;
}
