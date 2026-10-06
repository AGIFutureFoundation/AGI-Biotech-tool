// What a medicinal chemist actually reads off a pose: which residue does what, and whether the pocket
// sits somewhere mutation would matter. Geometry only, no external services.
//
// The interaction rules follow the usual structural-biology cut-offs (PLIP and similar use much the same
// numbers). They are heuristics on heavy-atom geometry: with no hydrogens placed, a "hydrogen bond" here
// means a donor and acceptor close enough and roughly aligned, not a proven one.

const AROMATIC_RINGS = {
  PHE: [['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ']],
  TYR: [['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ']],
  TRP: [['CD2', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2'], ['CG', 'CD1', 'NE1', 'CE2', 'CD2']],
  HIS: [['CG', 'ND1', 'CD2', 'CE1', 'NE2']],
};
const POSITIVE = { ARG: ['NH1', 'NH2', 'NE'], LYS: ['NZ'], HIS: ['ND1', 'NE2'] };
const NEGATIVE = { ASP: ['OD1', 'OD2'], GLU: ['OE1', 'OE2'] };
const HALOGENS = new Set(['CL', 'BR', 'I', 'F']);

const v = (P, i) => [P[i * 3], P[i * 3 + 1], P[i * 3 + 2]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const mean = (pts) => pts.reduce((acc, p) => [acc[0] + p[0] / pts.length, acc[1] + p[1] / pts.length, acc[2] + p[2] / pts.length], [0, 0, 0]);

function ringPlane(points) {
  const c = mean(points);
  // Newell's method: a stable normal even when the ring is not perfectly planar.
  let n = [0, 0, 0];
  for (let i = 0; i < points.length; i++) {
    const a = points[i], b = points[(i + 1) % points.length];
    n = [n[0] + (a[1] - b[1]) * (a[2] + b[2]), n[1] + (a[2] - b[2]) * (a[0] + b[0]), n[2] + (a[0] - b[0]) * (a[1] + b[1])];
  }
  return { centre: c, normal: norm(n) };
}

function proteinRings(protein, residueIdx) {
  const r = protein.residues[residueIdx];
  const defs = AROMATIC_RINGS[r.resName];
  if (!defs) return [];
  const out = [];
  for (const names of defs) {
    const pts = [];
    for (let i = r.start; i <= r.end; i++) if (names.includes(protein.atomName[i])) pts.push(v(protein.pos, i));
    if (pts.length === names.length) out.push(ringPlane(pts));
  }
  return out;
}

function ligandRings(ligand) {
  const rings = ligand.chem?.rings || [];
  const arom = new Set(ligand.chem?.aromaticAtoms || []);
  const fromChem = rings.filter((ring) => ring.length >= 5 && ring.every((i) => arom.has(i)));
  if (fromChem.length) return fromChem.map((ring) => ringPlane(ring.map((i) => v(ligand.pos, i))));
  // A ligand lifted out of a crystal has no cheminformatics record, so find its flat rings by geometry.
  return geometricAromaticRings(ligand).map((ring) => ringPlane(ring.map((i) => v(ligand.pos, i))));
}

// Five- and six-membered rings whose atoms are planar and unsaturated: good enough to call aromatic for
// the purpose of spotting stacking, without a chemistry toolkit.
export function geometricAromaticRings(lig, { flatness = 0.25 } = {}) {
  const heavy = new Set(Array.from(lig.heavy));
  const found = [], seen = new Set();
  const nbrs = (i) => lig.nbr[i].filter((j) => heavy.has(j));
  for (const start of heavy) {
    // Walk short cycles back to the starting atom.
    const stack = [[start, [start]]];
    while (stack.length) {
      const [node, path] = stack.pop();
      if (path.length > 6) continue;
      for (const nb of nbrs(node)) {
        if (nb === start && path.length >= 5) {
          const key = [...path].sort((a, b) => a - b).join(',');
          if (!seen.has(key)) { seen.add(key); found.push([...path]); }
        } else if (!path.includes(nb) && path.length < 6) {
          stack.push([nb, [...path, nb]]);
        }
      }
    }
  }
  return found.filter((ring) => {
    // Every ring atom must carry a double bond (sp2), and the ring must be flat.
    const unsaturated = ring.every((i) => nbrs(i).some((j) => ring.includes(j) && lig.bondOrder(i, j) >= 2)
      || lig.element[i] === 'N' || lig.element[i] === 'O' || lig.element[i] === 'S');
    if (!unsaturated) return false;
    const pts = ring.map((i) => v(lig.pos, i));
    const { centre, normal } = ringPlane(pts);
    return pts.every((p) => Math.abs(dot(sub(p, centre), normal)) < flatness);
  });
}

/**
 * Classify every contact between the ligand and the protein, grouped by residue.
 * Returns { residues: [...], counts: {...}, summary: string }.
 */
export function interactionFingerprint(protein, ligand, { cutoff = 4.5 } = {}) {
  const byRes = new Map();
  const add = (resIdx, type, detail) => {
    if (!byRes.has(resIdx)) byRes.set(resIdx, { residue: resIdx, types: {}, details: [] });
    const e = byRes.get(resIdx);
    e.types[type] = (e.types[type] || 0) + 1;
    // Hydrophobic contacts come by the dozen and would crowd out the single stacking or salt-bridge
    // record a chemist actually wants to see, so only they are capped.
    if (type !== 'hydrophobic' || e.details.filter((d) => d.type === 'hydrophobic').length < 6) {
      e.details.push({ type, ...detail });
    }
  };

  const lHeavy = Array.from(ligand.heavy);
  const pHeavy = Array.from(protein.heavy).filter((i) => {
    const r = protein.residues[protein.atomRes[i]];
    return r.polymer && !(protein.excluded && protein.excluded[i]);
  });

  for (const li of lHeavy) {
    const lp = v(ligand.pos, li);
    for (const pi of pHeavy) {
      const pp = v(protein.pos, pi);
      const d = dist(lp, pp);
      if (d > cutoff) continue;
      const resIdx = protein.atomRes[pi];
      const res = protein.residues[resIdx];
      const pName = protein.atomName[pi], lEl = ligand.element[li], pEl = protein.element[pi];

      // Hydrogen bond: donor/acceptor pair within 3.5 Å.
      if (d <= 3.5 && ((ligand.donor[li] && protein.acceptor[pi]) || (ligand.acceptor[li] && protein.donor[pi]))) {
        add(resIdx, 'hbond', { distance: +d.toFixed(2), ligandAtom: ligand.atomName[li], proteinAtom: pName });
      }
      // Hydrophobic: carbon to carbon, both apolar, 3.3 to 4.5 Å.
      else if (d >= 3.3 && ligand.hydrophobic[li] && protein.hydrophobic[pi]) {
        add(resIdx, 'hydrophobic', { distance: +d.toFixed(2), proteinAtom: pName });
      }
      // Salt bridge: formally charged groups within 4 Å.
      if (d <= 4.0) {
        const pPos = (POSITIVE[res.resName] || []).includes(pName);
        const pNeg = (NEGATIVE[res.resName] || []).includes(pName);
        const lNeg = ligand.charge[li] < 0 || (lEl === 'O' && ligand.acceptor[li] && isCarboxylate(ligand, li));
        const lPos = ligand.charge[li] > 0 || (lEl === 'N' && ligand.nbr[li].filter((x) => ligand.element[x] !== 'H').length >= 3);
        if ((pPos && lNeg) || (pNeg && lPos)) add(resIdx, 'saltBridge', { distance: +d.toFixed(2), proteinAtom: pName });
      }
      // Halogen bond: ligand halogen to protein oxygen or nitrogen, 3.0 to 4.0 Å.
      if (HALOGENS.has(lEl) && (pEl === 'O' || pEl === 'N') && d >= 2.8 && d <= 4.0) {
        add(resIdx, 'halogen', { distance: +d.toFixed(2), ligandAtom: ligand.atomName[li], proteinAtom: pName });
      }
    }
  }

  // Aromatic stacking, ring to ring: parallel under 5.5 Å, or edge-to-face (T-shaped) under 6 Å.
  const lRings = ligandRings(ligand);
  if (lRings.length) {
    const seen = new Set();
    for (const pi of pHeavy) {
      const resIdx = protein.atomRes[pi];
      if (seen.has(resIdx)) continue;
      seen.add(resIdx);
      for (const pr of proteinRings(protein, resIdx)) {
        for (const lr of lRings) {
          const d = dist(pr.centre, lr.centre);
          if (d > 6) continue;
          const angle = Math.acos(Math.min(1, Math.abs(dot(pr.normal, lr.normal)))) * 180 / Math.PI;
          if (d <= 5.5 && angle <= 30) add(resIdx, 'piStacking', { distance: +d.toFixed(2), angle: +angle.toFixed(0), geometry: 'parallel' });
          else if (d <= 6.0 && angle >= 60) add(resIdx, 'piStacking', { distance: +d.toFixed(2), angle: +angle.toFixed(0), geometry: 'T-shaped' });
        }
      }
    }
  }

  const residues = [...byRes.values()].map((e) => {
    const r = protein.residues[e.residue];
    return { ...e, label: `${r.resName}${r.resSeq}`, chain: r.chain, resSeq: r.resSeq,
      total: Object.values(e.types).reduce((a, b) => a + b, 0) };
  }).sort((a, b) => b.total - a.total);

  const counts = {};
  for (const r of residues) for (const [k, n] of Object.entries(r.types)) counts[k] = (counts[k] || 0) + n;

  return { residues, counts, summary: describeFingerprint(residues, counts) };
}

function isCarboxylate(lig, i) {
  const c = lig.nbr[i].find((x) => lig.element[x] === 'C');
  return c !== undefined && lig.nbr[c].filter((x) => lig.element[x] === 'O').length >= 2;
}

function describeFingerprint(residues, counts) {
  if (!residues.length) return 'No contacts within 4.5 Å: the ligand is not in a pocket.';
  const parts = [];
  const named = (type) => residues.filter((r) => r.types[type]).map((r) => r.label);
  if (counts.hbond) parts.push(`${counts.hbond} hydrogen bond${counts.hbond > 1 ? 's' : ''} to ${named('hbond').slice(0, 4).join(', ')}`);
  if (counts.saltBridge) parts.push(`${counts.saltBridge} salt bridge${counts.saltBridge > 1 ? 's' : ''} to ${named('saltBridge').slice(0, 3).join(', ')}`);
  if (counts.piStacking) parts.push(`aromatic stacking with ${named('piStacking').slice(0, 3).join(', ')}`);
  if (counts.halogen) parts.push(`${counts.halogen} halogen bond${counts.halogen > 1 ? 's' : ''}`);
  if (counts.hydrophobic) parts.push(`${counts.hydrophobic} hydrophobic contacts across ${named('hydrophobic').length} residues`);
  return parts.join('; ') + '.';
}

/**
 * Does this pocket sit where mutations matter? Intersects the pocket lining with AlphaMissense scores.
 * `missense` is the Map of residue number to mean pathogenicity from the AlphaFold database.
 */
export function pocketVariantOverlap(protein, pocket, missense, { threshold = 0.564 } = {}) {
  // 0.564 is the AlphaMissense "likely pathogenic" cut-off.
  if (!missense || !pocket?.residues?.length) return null;
  const rows = [];
  for (const idx of pocket.residues) {
    const r = protein.residues[idx];
    if (!r?.polymer) continue;
    const score = missense.get(r.resSeq);
    if (score == null) continue;
    rows.push({ label: `${r.resName}${r.resSeq}`, resSeq: r.resSeq, score: +score.toFixed(3), pathogenic: score >= threshold });
  }
  if (!rows.length) return null;
  rows.sort((a, b) => b.score - a.score);
  const pathogenic = rows.filter((r) => r.pathogenic);
  const all = [...missense.values()];
  const background = all.reduce((a, b) => a + b, 0) / all.length;
  const pocketMean = rows.reduce((a, r) => a + r.score, 0) / rows.length;
  return {
    residues: rows, pathogenic: pathogenic.length, lining: rows.length,
    pocketMean: +pocketMean.toFixed(3), proteinMean: +background.toFixed(3),
    enrichment: +(pocketMean / (background || 1)).toFixed(2),
    summary: `${pathogenic.length} of ${rows.length} pocket-lining residues are in the likely-pathogenic band `
      + `(mean ${pocketMean.toFixed(2)} against ${background.toFixed(2)} across the protein, `
      + `${(pocketMean / (background || 1)).toFixed(2)}× enriched). `
      + (pocketMean > background * 1.15
        ? 'Binding here touches positions where variation is poorly tolerated.'
        : 'This pocket is no more variant-sensitive than the protein as a whole.'),
  };
}

/**
 * Group a compound library into series by fingerprint similarity (single linkage).
 * `fpOf(compound)` must return a Uint8Array; `tanimoto` is passed in to avoid a circular import.
 */
export function clusterSeries(compounds, fpOf, tanimoto, { cut = 0.55 } = {}) {
  const items = compounds.filter((c) => fpOf(c));
  const n = items.length;
  const parent = [...Array(n).keys()];
  const find = (i) => (parent[i] === i ? i : (parent[i] = find(parent[i])));
  const union = (a, b) => { const ra = find(a), rb = find(b); if (ra !== rb) parent[rb] = ra; };
  const fps = items.map(fpOf);
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) if (tanimoto(fps[i], fps[j]) >= cut) union(i, j);
  }
  const groups = new Map();
  items.forEach((c, i) => {
    const root = find(i);
    if (!groups.has(root)) groups.set(root, []);
    groups.get(root).push(c);
  });
  return [...groups.values()]
    .map((members) => ({
      size: members.length,
      members,
      best: members.filter((m) => m.dockScore != null).sort((a, b) => a.dockScore - b.dockScore)[0] || null,
      label: members[0].agiId || members[0].label || 'series',
    }))
    .sort((a, b) => b.size - a.size);
}
