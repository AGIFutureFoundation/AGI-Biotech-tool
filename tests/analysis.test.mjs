// Offline checks for js/analysis.js on synthetic geometry.
//
// No network, no browser, no RDKit: a hand-built "protein" of five residues and a hand-built ligand
// placed at known distances, so each interaction class has one unambiguous expected hit.
//
//   node --test tests/analysis.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { Structure } from '../js/structure.js';
import { interactionFingerprint, geometricAromaticRings, pocketVariantOverlap, clusterSeries } from '../js/analysis.js';

const R = 1.39; // aromatic C–C
const ring = (cx, cy, cz) => [0, 1, 2, 3, 4, 5].map((k) => {
  const a = (k / 6) * Math.PI * 2;
  return { x: cx + R * Math.cos(a), y: cy + R * Math.sin(a), z: cz };
});

// Five residues, each placed so exactly one ligand atom reaches it.
function syntheticProtein() {
  const atoms = [];
  const res = (resName, resSeq, list) => list.forEach(([name, x, y, z, element]) =>
    atoms.push({ name, resName, chain: 'A', resSeq, x, y, z, element, het: 0 }));
  const names = ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'];
  res('PHE', 10, ring(0, 0, 0).map((p, i) => [names[i], p.x, p.y, p.z, 'C']));   // aromatic ring in z = 0
  res('ASP', 20, [['CG', 8.8, 0.4, 0.9, 'C'], ['OD1', 8, 0, 0, 'O'], ['OD2', 8.6, 1.2, 0, 'O']]);
  res('SER', 30, [['CB', -9.4, 0, 0, 'C'], ['OG', -8, 0, 0, 'O']]);
  res('LEU', 40, [['CD1', 0, 8, 0, 'C']]);
  res('GLY', 50, [['CA', 0, 0, -30, 'C']]);                                  // far away, must never appear
  return new Structure(atoms, { name: 'synthetic' });
}

// Benzene stacked 3.7 Å above the PHE ring, plus three probe atoms aimed at the other residues.
function syntheticLigand({ withChem = true } = {}) {
  const atoms = ring(0, 0, 3.7).map((p, i) => ({ ...p, element: 'C', name: `C${i + 1}`, het: 1 }));
  atoms.push({ x: -5.1, y: 0, z: 0, element: 'N', name: 'N1', het: 1 });                 // 2.9 Å from SER OG
  atoms.push({ x: 5.1, y: 0, z: 0, element: 'N', name: 'N2', het: 1, charge: 1 });      // 2.9 Å from ASP OD1
  atoms.push({ x: 0, y: 4.2, z: 0, element: 'C', name: 'C7', het: 1 });                 // 3.8 Å from LEU CD1
  const bonds = [];
  for (let i = 0; i < 6; i++) bonds.push(i, (i + 1) % 6, i % 2 ? 1 : 2);                // kekulé ring
  const hcount = [1, 1, 1, 1, 1, 1, 2, 1, 3];
  const chem = withChem ? { rings: [[0, 1, 2, 3, 4, 5]], aromaticAtoms: [0, 1, 2, 3, 4, 5] } : null;
  return new Structure(atoms, { bonds, kind: 'small', name: 'probe', hcount, chem });
}

test('fingerprint finds one of each interaction class at the planted geometry', () => {
  const fp = interactionFingerprint(syntheticProtein(), syntheticLigand());
  const by = Object.fromEntries(fp.residues.map((r) => [r.label, r.types]));
  assert.ok(by.PHE10?.piStacking >= 1, 'parallel stacking with PHE10');
  assert.ok(by.SER30?.hbond >= 1, 'hydrogen bond to SER30 OG');
  assert.ok(by.ASP20?.saltBridge >= 1, 'salt bridge to ASP20');
  assert.ok(by.LEU40?.hydrophobic >= 1, 'hydrophobic contact with LEU40');
  assert.equal(by.GLY50, undefined, 'a residue 30 Å away is not a contact');
  assert.match(fp.summary, /hydrogen bond/);
  assert.match(fp.summary, /stacking with PHE10/);
});

test('stacking detail reports the geometry as parallel at the planted angle', () => {
  const fp = interactionFingerprint(syntheticProtein(), syntheticLigand());
  const phe = fp.residues.find((r) => r.label === 'PHE10');
  const stack = phe.details.find((d) => d.type === 'piStacking');
  assert.equal(stack.geometry, 'parallel');
  assert.ok(Math.abs(stack.distance - 3.7) < 0.05, `centroid distance ${stack.distance}`);
});

test('a ligand with no chemistry record still gets its aromatic ring found geometrically', () => {
  const fp = interactionFingerprint(syntheticProtein(), syntheticLigand({ withChem: false }));
  assert.ok(fp.counts.piStacking >= 1);
});

test('geometric ring detection accepts a flat unsaturated ring and rejects the alternatives', () => {
  const flat = syntheticLigand({ withChem: false });
  assert.equal(geometricAromaticRings(flat).length, 1);
  assert.equal(geometricAromaticRings(flat)[0].length, 6);

  // Same connectivity, puckered: alternate atoms lifted well past the flatness tolerance.
  const puckered = ring(0, 0, 0).map((p, i) => ({ ...p, z: i % 2 ? 0.6 : -0.6, element: 'C', name: `C${i}`, het: 1 }));
  const pb = []; for (let i = 0; i < 6; i++) pb.push(i, (i + 1) % 6, i % 2 ? 1 : 2);
  assert.equal(geometricAromaticRings(new Structure(puckered, { bonds: pb, kind: 'small' })).length, 0);

  // Flat but saturated: single bonds everywhere, so not aromatic.
  const sat = ring(0, 0, 0).map((p, i) => ({ ...p, element: 'C', name: `C${i}`, het: 1 }));
  const sb = []; for (let i = 0; i < 6; i++) sb.push(i, (i + 1) % 6, 1);
  assert.equal(geometricAromaticRings(new Structure(sat, { bonds: sb, kind: 'small' })).length, 0);
});

test('nothing within cutoff means an honest empty summary', () => {
  const protein = syntheticProtein();
  const lig = syntheticLigand();
  for (let i = 0; i < lig.n; i++) lig.pos[i * 3 + 2] += 40;    // slide the whole ligand away
  const fp = interactionFingerprint(protein, lig);
  assert.equal(fp.residues.length, 0);
  assert.match(fp.summary, /not in a pocket/);
});

test('pocket variant overlap computes enrichment against the protein background', () => {
  const protein = syntheticProtein();
  const idx = (seq) => protein.residues.findIndex((r) => r.resSeq === seq);
  const pocket = { residues: [idx(10), idx(20)] };
  const missense = new Map([[10, 0.9], [20, 0.2], [30, 0.5], [40, 0.5], [50, 0.5]]);
  const o = pocketVariantOverlap(protein, pocket, missense);
  assert.equal(o.lining, 2);
  assert.equal(o.pathogenic, 1);                      // 0.9 passes the 0.564 cut-off, 0.2 does not
  assert.equal(o.pocketMean, 0.55);
  assert.equal(o.proteinMean, 0.52);
  assert.ok(Math.abs(o.enrichment - 0.55 / 0.52) < 0.01);
  assert.equal(o.residues[0].label, 'PHE10');         // sorted by score, highest first
  assert.equal(pocketVariantOverlap(protein, { residues: [] }, missense), null);
  assert.equal(pocketVariantOverlap(protein, pocket, null), null);
});

test('series clustering groups by fingerprint similarity and keeps the best scorer', () => {
  const tanimoto = (a, b) => {
    let inter = 0, uni = 0;
    for (let i = 0; i < a.length; i++) { inter += (a[i] & b[i]) ? 1 : 0; uni += (a[i] | b[i]) ? 1 : 0; }
    return uni ? inter / uni : 0;
  };
  const fpA = Uint8Array.from([1, 1, 1, 1, 0, 0, 0, 0]);
  const fpB = Uint8Array.from([1, 1, 1, 0, 0, 0, 0, 0]);   // 3/4 similar to A
  const fpC = Uint8Array.from([0, 0, 0, 0, 1, 1, 1, 1]);   // disjoint from A and B
  const compounds = [
    { agiId: 'A', fp: fpA, dockScore: -6.1 },
    { agiId: 'B', fp: fpB, dockScore: -7.4 },
    { agiId: 'C', fp: fpC, dockScore: null },
    { agiId: 'D', fp: null },                                // no fingerprint: left out
  ];
  const groups = clusterSeries(compounds, (c) => c.fp, tanimoto, { cut: 0.55 });
  assert.equal(groups.length, 2);
  assert.equal(groups[0].size, 2);
  assert.deepEqual(groups[0].members.map((m) => m.agiId).sort(), ['A', 'B']);
  assert.equal(groups[0].best.agiId, 'B');                 // lower score wins
  assert.equal(groups[1].best, null);                      // nothing docked in that series
});
