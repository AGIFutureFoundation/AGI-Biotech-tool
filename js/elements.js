// Element data: covalent radius (Å), van der Waals radius (Å), mass (amu), CPK/Jmol colour.
const T = {
  H: [0.31, 1.10, 1.008, 0xffffff], C: [0.76, 1.70, 12.011, 0x909090], N: [0.71, 1.55, 14.007, 0x3050f8],
  O: [0.66, 1.52, 15.999, 0xff0d0d], F: [0.57, 1.47, 18.998, 0x90e050], P: [1.07, 1.80, 30.974, 0xff8000],
  S: [1.05, 1.80, 32.06, 0xffff30], CL: [1.02, 1.75, 35.45, 0x1ff01f], BR: [1.20, 1.85, 79.904, 0xa62929],
  I: [1.39, 1.98, 126.9, 0x940094], B: [0.84, 1.92, 10.81, 0xffb5b5], SE: [1.20, 1.90, 78.97, 0xffa100],
  NA: [1.66, 2.27, 22.99, 0xab5cf2], MG: [1.41, 1.73, 24.305, 0x8aff00], K: [2.03, 2.75, 39.098, 0x8f40d4],
  CA: [1.76, 2.31, 40.078, 0x3dff00], MN: [1.39, 2.0, 54.938, 0x9c7ac7], FE: [1.32, 2.0, 55.845, 0xe06633],
  CO: [1.26, 2.0, 58.933, 0xf090a0], NI: [1.24, 1.63, 58.693, 0x50d050], CU: [1.32, 1.40, 63.546, 0xc88033],
  ZN: [1.22, 1.39, 65.38, 0x7d80b0], SI: [1.11, 2.10, 28.085, 0xf0c8a0],
};
const DEF = [0.8, 1.8, 12.0, 0xff1493];

export const el = (s) => T[(s || 'C').toUpperCase()] || DEF;
export const covRadius = (s) => el(s)[0];
export const vdwRadius = (s) => el(s)[1];
export const mass = (s) => el(s)[2];
export const cpk = (s) => el(s)[3];

// Chain palette (colour-blind-safe-ish, bright for dark VR backgrounds).
export const CHAIN_COLORS = [0x4cc9f0, 0xf72585, 0x7bd389, 0xffbe0b, 0xb388eb, 0xff7f51, 0x4895ef, 0xe9edc9,
  0x06d6a0, 0xef476f, 0x118ab2, 0xffd166];

// Kyte-Doolittle hydropathy.
export const HYDRO = { ILE: 4.5, VAL: 4.2, LEU: 3.8, PHE: 2.8, CYS: 2.5, MET: 1.9, ALA: 1.8, GLY: -0.4, THR: -0.7,
  SER: -0.8, TRP: -0.9, TYR: -1.3, PRO: -1.6, HIS: -3.2, GLU: -3.5, GLN: -3.5, ASP: -3.5, ASN: -3.5, LYS: -3.9, ARG: -4.5 };

export const AA3 = { ALA: 'A', ARG: 'R', ASN: 'N', ASP: 'D', CYS: 'C', GLN: 'Q', GLU: 'E', GLY: 'G', HIS: 'H', ILE: 'I',
  LEU: 'L', LYS: 'K', MET: 'M', PHE: 'F', PRO: 'P', SER: 'S', THR: 'T', TRP: 'W', TYR: 'Y', VAL: 'V', MSE: 'M',
  HID: 'H', HIE: 'H', HIP: 'H', CYX: 'C', SEC: 'U', PYL: 'O' };

export const WATER = new Set(['HOH', 'WAT', 'DOD', 'H2O', 'TIP', 'TIP3', 'SOL']);
export const IONS = new Set(['NA', 'CL', 'K', 'MG', 'CA', 'ZN', 'MN', 'FE', 'FE2', 'CU', 'CU1', 'NI', 'CO', 'CD', 'IOD', 'BR']);

// AlphaFold pLDDT colour bands (same thresholds as the AlphaFold DB viewer).
export function plddtColor(b) {
  if (b >= 90) return 0x0053d6;
  if (b >= 70) return 0x65cbf3;
  if (b >= 50) return 0xffdb13;
  return 0xff7d45;
}

// Lerp blue -> white -> red for a value in [0,1].
export function divergent(t) {
  t = Math.max(0, Math.min(1, t));
  const lerp = (a, b, u) => Math.round(a + (b - a) * u);
  if (t < 0.5) { const u = t / 0.5; return (lerp(0x3a, 0xf2, u) << 16) | (lerp(0x86, 0xf2, u) << 8) | lerp(0xff, 0xf2, u); }
  const u = (t - 0.5) / 0.5; return (lerp(0xf2, 0xe6, u) << 16) | (lerp(0xf2, 0x39, u) << 8) | lerp(0xf2, 0x46, u);
}

export function rainbow(t) {
  const h = (1 - Math.max(0, Math.min(1, t))) * 0.7; // blue (N-term) -> red (C-term)
  const f = (n) => { const k = (n + h * 12) % 12; return 0.5 - 0.5 * Math.max(-1, Math.min(k - 3, 9 - k, 1)); };
  return (Math.round(f(0) * 255) << 16) | (Math.round(f(8) * 255) << 8) | Math.round(f(4) * 255);
}
