// Standalone verification of an exported provenance ledger.
//
// js/ledger.js says its export is something "whose root hash you can anchor on-chain, in a DAO proposal, or
// in a lab notebook, and later verify". Until now there was nothing to verify it with: `Ledger.verify()` is
// a method on a live Ledger, which loads from localStorage, so checking a file someone emailed you meant
// reconstructing a workspace around it. This module takes the exported document on its own and checks it
// end to end — no Ledger instance, no browser storage, no network.
//
// It also checks two things the live method cannot, because a live Ledger computes them rather than reading
// them: that the document's claimed `head` is the hash it actually ends on, and that its claimed `length`
// matches how many records it carries. A header that disagrees with its own body is the first thing a
// careless forgery gets wrong.
//
// WHAT THIS CANNOT DETECT, stated here because it is the limit that matters:
//
//   Dropping records off the END of the chain leaves a chain that verifies perfectly. A hash chain proves
//   that the records it contains have not been altered and are in the order they were written. It cannot
//   prove that nothing was removed from the tail, because the remaining prefix is a valid chain in its own
//   right. The only fix is an external reference: a head hash recorded somewhere the author of the ledger
//   does not control, at a time you can establish. Pass that as `expectedHead` and truncation is caught;
//   without it, it is not, and `limits` in the result says so on every call.
//
//   Equally: this proves provenance, not correctness. A tamper-evident record of an unvalidated docking
//   score is still an unvalidated docking score.

export const GENESIS = '0'.repeat(64);

/** The exact string js/ledger.js hashes. Key order is fixed, so a re-hash reproduces it. */
export function canonicalRecord(rec) {
  return JSON.stringify([rec.index, rec.time, rec.kind, rec.actor, rec.prev, rec.payload]);
}

export async function sha256Hex(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

const LIMITS = [
  'truncation: records removed from the end of the chain cannot be detected without an external head hash',
  'provenance only: an intact chain says a record was not altered, not that its contents are correct',
];

/**
 * Verify an exported ledger document — the object `Ledger.export()` produces, or its JSON round-trip.
 *
 * Returns { ok, length, head, limits, checked } on success, and on failure adds { brokenAt, reason } where
 * `brokenAt` is the record index that failed, or null for a problem with the document itself.
 *
 * Pass `expectedHead` — a head hash you recorded elsewhere, earlier — to close the truncation hole.
 */
export async function verifyExport(doc, { expectedHead = null } = {}) {
  const fail = (reason, brokenAt = null) => ({ ok: false, reason, brokenAt, limits: LIMITS });

  if (!doc || typeof doc !== 'object') return fail('not a ledger document');
  if (!Array.isArray(doc.records)) return fail('document has no records array');

  let prev = GENESIS;
  for (const [position, rec] of doc.records.entries()) {
    if (!rec || typeof rec !== 'object') return fail('record is not an object', position);
    if (rec.index !== position) {
      return fail(`record at position ${position} claims index ${rec.index}`, position);
    }
    if (rec.prev !== prev) return fail('previous hash does not match', rec.index);
    if (typeof rec.hash !== 'string') return fail('record carries no hash', rec.index);
    const again = await sha256Hex(canonicalRecord(rec));
    if (again !== rec.hash) return fail('record contents were altered', rec.index);
    prev = rec.hash;
  }

  // The header must agree with the body it describes.
  if (doc.length !== undefined && doc.length !== doc.records.length) {
    return fail(`document claims ${doc.length} records but carries ${doc.records.length}`);
  }
  if (doc.head !== undefined && doc.head !== prev) {
    return fail('document head does not match the chain it contains');
  }
  if (expectedHead !== null && expectedHead !== prev) {
    return fail('chain does not end at the expected head: records may have been removed from the end');
  }

  return {
    ok: true,
    length: doc.records.length,
    head: prev,
    checked: {
      hashes: true,
      linkage: true,
      indices: true,
      header: doc.head !== undefined || doc.length !== undefined,
      againstExternalHead: expectedHead !== null,
    },
    limits: LIMITS,
  };
}

/**
 * A one-line summary a person can read, which states the truncation limit rather than leaving it implied.
 * An "ok" that quietly means "ok except for the part I cannot check" is worse than no check at all.
 */
export function describeResult(result) {
  if (!result.ok) {
    return result.brokenAt === null
      ? `INVALID: ${result.reason}`
      : `INVALID at record ${result.brokenAt}: ${result.reason}`;
  }
  const anchored = result.checked.againstExternalHead;
  return `${result.length} records intact, head ${result.head.slice(0, 12)}…`
    + (anchored
      ? ' · matches the external head, so nothing was removed from the end'
      : ' · no external head given, so records removed from the end would not show');
}
