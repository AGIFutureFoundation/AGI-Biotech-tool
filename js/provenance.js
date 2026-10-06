// Where a number came from, and how loudly the UI says so. Three tiers:
//   real       retrieved or computed exactly from real inputs: PDB/AlphaFold coordinates, RDKit descriptors,
//              PubChem/ChEMBL hits. Shown plain. No mark at all, so a mark always means something.
//   estimate   an unvalidated model ran on real inputs: the in-browser Vina-like dock score (js/dock.js).
//              Not a measured or calibrated energy, so it drops kcal/mol and carries a quiet EST tag.
//   synthetic  no model ran: a placeholder. server/synthetic_provenance.py stamps these "[SYNTHETIC]" on the
//              value and "SYNTHETIC: ..." on the record's `provenance`. Loud, filled SYNTHETIC tag.
// Every mark is text plus shape (dashed vs filled tag, hatched bars), never hue alone, so it survives
// greyscale screenshots and colour-blind viewing.

export const MARKER = 'SYNTHETIC';
export const DOCK_TIER = 'estimate';                 // every dock score this client computes
export const SCORE_UNIT = 'unitless Vina-like score'; // replaces kcal/mol: nothing here is calibrated to it

const T = {
  estimate: { cls: 'pv-est', tag: 'EST', plain: '(est.)', rank: 1,
    note: 'Unvalidated in-browser Vina-like score. Not a measured or calibrated binding energy (not kcal/mol); use only to rank.' },
  synthetic: { cls: 'pv-syn', tag: MARKER, plain: `[${MARKER}]`, rank: 2,
    note: 'Placeholder: no docking, MD, ADMET or assay model produced this. Do not report it as a result.' },
};
export const tierInfo = (tier) => T[tier] || null;

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const hasMarker = (v) => typeof v === 'string' && v.includes(MARKER);

// A value may arrive as a number or as the backend's "-8.4 [SYNTHETIC]" string. Returns the number.
export function num(v) {
  if (v == null) return null;
  const n = typeof v === 'number' ? v : parseFloat(String(v));
  return Number.isNaN(n) ? null : n;
}

// Tier of `field` on `rec`. A record stamped "SYNTHETIC: ... Placeholder fields: a, b." marks only those
// fields; a stamp with no list marks every field. Otherwise the caller's base tier stands.
export function tierOf(rec, field, base = null) {
  if (hasMarker(rec?.[field])) return 'synthetic';
  const p = rec?.provenance;
  if (typeof p === 'string' && p.startsWith(MARKER)) {
    const m = p.match(/Placeholder fields: ([^.]*)\./);
    if (!m || m[1].split(',').map((s) => s.trim()).includes(field)) return 'synthetic';
  }
  if (typeof p === 'string' && p.startsWith('ESTIMATE') && base !== 'synthetic') return 'estimate';
  return base;
}

export const worst = (...tiers) => tiers.reduce((a, t) => ((T[t]?.rank || 0) > (T[a]?.rank || 0) ? t : a), null);

// Worst tier anywhere in a tool result or API payload.
export function scan(obj, depth = 0) {
  if (obj == null || depth > 6) return null;
  if (hasMarker(obj)) return 'synthetic';
  if (typeof obj !== 'object') return null;
  let t = null;
  if (typeof obj.provenance === 'string') t = obj.provenance.startsWith(MARKER) ? 'synthetic' : obj.provenance.startsWith('ESTIMATE') ? 'estimate' : null;
  for (const v of Object.values(obj)) t = worst(t, scan(v, depth + 1));
  return t;
}

// HTML: the value with its tag. Real values come back escaped and unmarked.
export function mark(text, tier) {
  const t = T[tier];
  if (!t) return esc(text);
  return `<span class="pv ${t.cls}" title="${esc(t.note)}"><span class="pv-v">${esc(text)}</span><i class="pv-tag" aria-label="${esc(tier)}">${t.tag}</i></span>`;
}

// Just the tag, for headings.
export const tag = (tier) => (T[tier] ? `<i class="pv-tag pv-tag-solo ${T[tier].cls}" title="${esc(T[tier].note)}">${T[tier].tag}</i>` : '');

// Plain text (reports, speech, ledger, toasts): the marker travels inside the string.
export const plain = (text, tier) => (T[tier] ? `${text} ${T[tier].plain}` : String(text));

// One strip per card saying what the marked values are. Nothing for real data.
export function note(tier, extra = '') {
  const t = T[tier];
  if (!t) return '';
  return `<p class="pv-note ${t.cls}" role="note"><b>${tier === 'synthetic' ? MARKER : 'ESTIMATE'}</b> ${esc(t.note)}${extra ? ' ' + esc(extra) : ''}</p>`;
}

// Canvas pill for world-space panels in the headset, where DOM marks do not exist. Returns its width.
export function paintTag(ctx, tier, xRight, yBase, px = 18) {
  const t = T[tier];
  if (!t) return 0;
  ctx.save();
  ctx.font = `700 ${px}px ui-monospace, Menlo, monospace`;
  const w = ctx.measureText(t.tag).width + px * 0.9, h = px * 1.35, x = xRight - w, y = yBase - px * 1.05;
  const col = tier === 'synthetic' ? '#ff5d73' : '#ffbe0b';
  ctx.lineWidth = 2;
  if (tier === 'synthetic') { ctx.fillStyle = col; ctx.fillRect(x, y, w, h); ctx.fillStyle = '#070b12'; }
  else { ctx.setLineDash([5, 3]); ctx.strokeStyle = col; ctx.strokeRect(x, y, w, h); ctx.fillStyle = col; }
  ctx.fillText(t.tag, x + px * 0.45, yBase);
  ctx.restore();
  return w;
}
