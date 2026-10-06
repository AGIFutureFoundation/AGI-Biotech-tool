// Offline checks for the provenance ledger: js/ledger.js and js/ledger-verify.js.
//
// The ledger is the project's central honesty mechanism. Every claim about traceability rests on one
// property: if a record is altered, verification fails. The wiki says so, the whitepaper says so, and until
// now nothing checked it. A tamper-evident log whose tamper detection is untested is decoration.
//
// So the tests here actually tamper: they edit a score, swap a hash, reorder records, splice one out, and
// forge a document header, and require each to be caught at the right index with the right reason. The
// limits are tested too — truncation from the tail is NOT detectable without an external head, and that is
// asserted as a fact rather than left as a footnote, because an honesty mechanism that overstates itself is
// the worst kind.
//
//   node --test tests/ledger.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { Ledger } from '../js/ledger.js';
import { verifyExport, describeResult, canonicalRecord, sha256Hex, GENESIS } from '../js/ledger-verify.js';

// js/ledger.js reads and writes localStorage inside try/catch, so it works unchanged under Node — the reads
// throw ReferenceError, are caught, and the ledger starts empty. That is the behaviour these tests rely on.
const freshLedger = () => new Ledger();

async function withRecords() {
  const led = freshLedger();
  led.actor = 'tester';
  await led.append('structure', { name: 'SOD1' });
  await led.append('dock', {
    compound: 'AGI-0001', target: 'SOD1', score: -8.4, poses: 12,
    provenance: 'ESTIMATE: unvalidated in-browser score, not kcal/mol',
  });
  await led.append('md', { engine: 'OpenMM', target: 'SOD1', ps: 250 });
  return led;
}

const roundTrip = (doc) => JSON.parse(JSON.stringify(doc));

test('an empty ledger starts at the genesis hash and verifies', async () => {
  const led = freshLedger();
  assert.equal(led.records.length, 0, 'localStorage is unavailable under Node, so the ledger starts empty');
  assert.equal(led.head, GENESIS);
  const v = await led.verify();
  assert.equal(v.ok, true);
  assert.equal(v.length, 0);
});

test('each record chains to the one before it', async () => {
  const led = await withRecords();
  assert.equal(led.records.length, 3);
  assert.equal(led.records[0].prev, GENESIS, 'the first record points at genesis');
  for (let i = 1; i < led.records.length; i++) {
    assert.equal(led.records[i].prev, led.records[i - 1].hash,
      `record ${i} does not point at record ${i - 1}`);
  }
  assert.equal(led.head, led.records[2].hash);
  led.records.forEach((r, i) => {
    assert.equal(r.index, i);
    assert.equal(r.actor, 'tester');
    assert.match(r.hash, /^[0-9a-f]{64}$/, 'a hash should be 64 hex characters of SHA-256');
    assert.match(r.time, /^\d{4}-\d{2}-\d{2}T/, 'a record should be timestamped');
  });
});

test('a clean chain verifies', async () => {
  const led = await withRecords();
  const v = await led.verify();
  assert.equal(v.ok, true, `a chain nobody touched should verify: ${v.reason}`);
  assert.equal(v.length, 3);
  assert.equal(v.head, led.head);
});

test('altering a payload is caught, at the record that was altered', async () => {
  const led = await withRecords();
  led.records[1].payload.score = -12.9; // make the result look better than it was
  const v = await led.verify();
  assert.equal(v.ok, false, 'editing a score must break verification');
  assert.equal(v.brokenAt, 1);
  assert.match(v.reason, /altered/);
});

test('stripping the estimate disclaimer off a record is caught like any other edit', async () => {
  // The caveat is a field in the record, not a note on a web page, so removing it is tampering and is
  // detected as tampering. That is the whole reason it lives there.
  const led = await withRecords();
  delete led.records[1].payload.provenance;
  const v = await led.verify();
  assert.equal(v.ok, false, 'removing the "not kcal/mol" caveat must break the chain');
  assert.equal(v.brokenAt, 1);
});

test('rewriting a hash to match an edited payload still fails, because the next record points at the old one', async () => {
  const led = await withRecords();
  led.records[1].payload.score = -12.9;
  led.records[1].hash = await sha256Hex(canonicalRecord(led.records[1])); // a careful forger
  const v = await led.verify();
  assert.equal(v.ok, false, 'a re-hashed record breaks its successor’s linkage');
  assert.equal(v.brokenAt, 2, 'the failure surfaces at the record that pointed at the old hash');
  assert.match(v.reason, /previous hash/);
});

test('reordering records is caught', async () => {
  const led = await withRecords();
  [led.records[1], led.records[2]] = [led.records[2], led.records[1]];
  const v = await led.verify();
  assert.equal(v.ok, false, 'swapping two records must break the chain');
});

test('splicing a record out of the middle is caught', async () => {
  const led = await withRecords();
  led.records.splice(1, 1);
  const v = await led.verify();
  assert.equal(v.ok, false, 'removing a record from the body must break the chain');
});

test('the honest limit: truncating the tail is NOT detected', async () => {
  // This is not a bug to fix, it is a property of hash chains. The remaining prefix is a valid chain. It is
  // asserted so that nobody later writes documentation claiming the ledger detects deletion, and so the
  // only real remedy — an external head hash — stays visible.
  const led = await withRecords();
  const realHead = led.head;
  led.records.pop();
  const v = await led.verify();
  assert.equal(v.ok, true, 'a truncated chain verifies, which is exactly why an external anchor is needed');
  assert.notEqual(v.head, realHead, 'but the head has changed, which an anchored head would expose');
});

test('an external head closes the truncation hole', async () => {
  const led = await withRecords();
  const anchored = led.head; // the hash you wrote in a lab notebook at the time
  const full = roundTrip(led.export());
  assert.equal((await verifyExport(full, { expectedHead: anchored })).ok, true);

  led.records.pop();
  const truncated = roundTrip(led.export());
  const bare = await verifyExport(truncated);
  assert.equal(bare.ok, true, 'on its own the shortened chain is internally consistent');
  const checked = await verifyExport(truncated, { expectedHead: anchored });
  assert.equal(checked.ok, false, 'against the anchored head, the missing record shows');
  assert.match(checked.reason, /removed from the end/);
});

test('an exported document survives a JSON round trip and still verifies', async () => {
  // The realistic risk: the canonical string hashes the payload with JSON.stringify, so if a round trip
  // through a file or localStorage reordered keys, an untouched record would fail to verify. It does not,
  // and this proves it rather than assuming it.
  const led = await withRecords();
  const doc = roundTrip(led.export());
  const v = await verifyExport(doc);
  assert.equal(v.ok, true, `a round-tripped export must still verify: ${v.reason}`);
  assert.equal(v.length, 3);
  assert.equal(v.head, led.head);
  assert.equal(v.checked.hashes, true);
  assert.equal(v.checked.linkage, true);
});

test('the standalone verifier agrees with the live one, so the two canonical forms have not drifted', async () => {
  // js/ledger.js keeps its canonical() private, so this is the cross-check: if the two implementations
  // disagreed about what string gets hashed, every hash would mismatch and this would fail.
  const led = await withRecords();
  const live = await led.verify();
  const standalone = await verifyExport(roundTrip(led.export()));
  assert.equal(live.ok, standalone.ok);
  assert.equal(live.head, standalone.head);
  assert.equal(live.length, standalone.length);
});

test('a forged document header is caught even when every record is intact', async () => {
  const led = await withRecords();

  const wrongHead = roundTrip(led.export());
  wrongHead.head = '0'.repeat(64);
  const a = await verifyExport(wrongHead);
  assert.equal(a.ok, false, 'a head that does not match the records must be rejected');
  assert.match(a.reason, /head does not match/);

  const wrongLength = roundTrip(led.export());
  wrongLength.length = 99;
  const b = await verifyExport(wrongLength);
  assert.equal(b.ok, false, 'a length that does not match the records must be rejected');
  assert.match(b.reason, /claims 99 records/);
});

test('a record whose index was renumbered is caught', async () => {
  const led = await withRecords();
  const doc = roundTrip(led.export());
  doc.records[2].index = 7;
  const v = await verifyExport(doc);
  assert.equal(v.ok, false);
  assert.equal(v.brokenAt, 2);
  assert.match(v.reason, /claims index 7/);
});

test('malformed documents are rejected rather than throwing', async () => {
  for (const bad of [null, undefined, 42, 'a string', {}, { records: 'not an array' }]) {
    const v = await verifyExport(bad);
    assert.equal(v.ok, false, `${JSON.stringify(bad)} should be rejected`);
    assert.ok(typeof v.reason === 'string' && v.reason.length > 0, 'a rejection must say why');
  }
  const noHash = { records: [{ index: 0, time: 't', kind: 'k', actor: 'a', prev: GENESIS, payload: {} }] };
  const v = await verifyExport(noHash);
  assert.equal(v.ok, false);
  assert.match(v.reason, /no hash/);
});

test('every verification result states its own limits', async () => {
  const led = await withRecords();
  const good = await verifyExport(roundTrip(led.export()));
  const bad = await verifyExport({ records: 'nope' });
  for (const r of [good, bad]) {
    assert.ok(Array.isArray(r.limits) && r.limits.length >= 2, 'limits must be reported on every call');
    assert.ok(r.limits.some((l) => /truncation/.test(l)), 'the truncation limit must be stated');
    assert.ok(r.limits.some((l) => /not that its contents are correct/.test(l)),
      'and that provenance is not correctness');
  }
});

test('the human summary says whether truncation was ruled out, rather than implying it', async () => {
  const led = await withRecords();
  const doc = roundTrip(led.export());
  const unanchored = describeResult(await verifyExport(doc));
  assert.match(unanchored, /3 records intact/);
  assert.match(unanchored, /removed from the end would not show/,
    'an unanchored pass must not read as a clean bill of health');

  const anchored = describeResult(await verifyExport(doc, { expectedHead: led.head }));
  assert.match(anchored, /nothing was removed from the end/);

  led.records[1].payload.score = -1;
  const broken = describeResult(await verifyExport(roundTrip(led.export())));
  assert.match(broken, /^INVALID at record 1/);
});

test('clearing the ledger empties it and returns it to genesis', async () => {
  const led = await withRecords();
  led.clear();
  assert.equal(led.records.length, 0);
  assert.equal(led.head, GENESIS);
  assert.equal((await led.verify()).ok, true);
});

test('appending after a clear starts a fresh chain at genesis', async () => {
  const led = await withRecords();
  led.clear();
  const rec = await led.append('structure', { name: 'LRRK2' });
  assert.equal(rec.index, 0);
  assert.equal(rec.prev, GENESIS);
  assert.equal((await led.verify()).ok, true);
});

test('append emits an event carrying the record, so the UI cannot fall out of step', async () => {
  const led = freshLedger();
  const seen = [];
  led.addEventListener('append', (e) => seen.push(e.detail));
  await led.append('structure', { name: 'SOD1' });
  await led.append('dock', { compound: 'x', target: 'SOD1', score: -7 });
  assert.equal(seen.length, 2);
  assert.equal(seen[1].kind, 'dock');
  assert.equal(seen[1].index, 1);
});

test('the UI line for a dock score never omits that it is an estimate', async () => {
  // Three places have to agree that this number is not kcal/mol: the record, the wiki, and the line a
  // person actually reads. This checks the third.
  const line = Ledger.describe({ kind: 'dock', payload: { compound: 'AGI-0001', target: 'SOD1', score: -8.4 } });
  assert.match(line, /AGI-0001/);
  assert.match(line, /SOD1/);
  assert.match(line, /est\./, 'a dock score shown to a person must be marked as an estimate');
  assert.ok(!/kcal/i.test(line), 'and must not carry an energy unit');

  const screen = Ledger.describe({ kind: 'screen', payload: { compounds: 40, target: 'SOD1', best: -9.1 } });
  assert.match(screen, /est\./, 'a screening best score is the same kind of number');

  // Kinds without an estimated score say what happened, with no spurious caveat.
  assert.match(Ledger.describe({ kind: 'import', payload: { count: 425, source: 'AGI collection' } }), /425/);
  assert.equal(Ledger.describe({ kind: 'something-new', payload: {} }), 'something-new',
    'an unknown kind falls back to its name rather than rendering "undefined"');
});
