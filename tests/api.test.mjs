// Offline checks for the public-database layer in js/api.js.
//
// The wiki's Data Sources page makes a claim about this module: "a failed lookup is reported as a failed
// lookup. The panel says the source could not be reached; it does not fall back to a cached guess and
// present it as current, and it does not fill the gap with a plausible number." Nothing checked that.
//
// It is checkable without a network, because the thing being tested is how the module behaves when a
// request fails — and a stubbed `fetch` can fail on demand far more reliably than a real one. Every test
// here installs its own stub, records what was requested, and asserts both the result and the requests
// made. Nothing reaches the network; the stub would throw if anything tried.
//
// The property that matters most is not about data at all: the CORS fallback re-sends a failed request
// through the local server's read-only proxy, and it must never do that to a POST. Replaying a write
// through a proxy because the first attempt looked like a CORS failure is the kind of bug that is invisible
// until it is very much not.
//
//   node --test tests/api.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { rcsb, alphafold, uniprot, pubchem } from '../js/api.js';

// js/api.js memoises on the request URL for the lifetime of the module, which is correct for a research
// session and inconvenient for a test file. Every test therefore uses identifiers nothing else uses, so no
// two tests can collide in the cache.
let served;

/**
 * Install a fetch stub. `handler(url, init)` returns a response descriptor, or throws to simulate a network
 * or CORS failure. Returns the log of requests made.
 */
function stubFetch(handler) {
  served = [];
  globalThis.fetch = async (url, init = {}) => {
    served.push({ url: String(url), method: init.method || 'GET', body: init.body });
    const out = await handler(String(url), init);
    return {
      ok: out.status === undefined ? true : out.status >= 200 && out.status < 300,
      status: out.status === undefined ? 200 : out.status,
      json: async () => out.json,
      text: async () => out.text ?? '',
    };
  };
  return served;
}

const okJson = (json) => ({ status: 200, json });
const okText = (text) => ({ status: 200, text });

test.afterEach(() => { delete globalThis.fetch; });

test('a successful lookup returns the parsed body', async () => {
  stubFetch(() => okJson({ rcsb_id: '1A00', struct: { title: 'HAEMOGLOBIN' } }));
  const entry = await rcsb.entry('1a00');
  assert.equal(entry.rcsb_id, '1A00');
  assert.equal(served.length, 1);
  assert.match(served[0].url, /^https:\/\/data\.rcsb\.org\/rest\/v1\/core\/entry\/1A00$/,
    'the identifier should be upper-cased into the canonical URL');
  assert.equal(served[0].method, 'GET');
});

test('an HTTP error is thrown, naming the host and the status', async () => {
  // The honesty claim: a failed lookup fails. It does not come back as an empty object that reads like
  // "this protein has no data", which is a different and much worse statement.
  stubFetch(() => ({ status: 404, json: { message: 'not found' } }));
  await assert.rejects(() => rcsb.entry('9zz1'), (e) => {
    assert.match(e.message, /data\.rcsb\.org/, 'the error should name the source that failed');
    assert.match(e.message, /404/, 'and the status it failed with');
    return true;
  });
});

test('a server error is thrown too, not quietly turned into no data', async () => {
  stubFetch(() => ({ status: 503, json: null }));
  await assert.rejects(() => rcsb.entry('9zz2'), /503/);
});

test('a failed GET is retried once through the local read-only proxy', async () => {
  // Several of these APIs send no CORS headers, so the browser refuses the direct call and the only way
  // through is the server's allowlisted proxy. The retry must target the original URL, encoded.
  let attempt = 0;
  stubFetch((url) => {
    attempt++;
    if (attempt === 1) throw new TypeError('Failed to fetch'); // what a CORS refusal looks like
    assert.match(url, /^\/api\/proxy\?url=/, 'the retry must go through the proxy');
    return okJson({ rcsb_id: '9ZZ3' });
  });
  const entry = await rcsb.entry('9zz3');
  assert.equal(entry.rcsb_id, '9ZZ3');
  assert.equal(served.length, 2, 'exactly one retry, not a loop');
  assert.equal(
    decodeURIComponent(served[1].url.replace('/api/proxy?url=', '')),
    'https://data.rcsb.org/rest/v1/core/entry/9ZZ3',
    'the proxy must be asked for the URL that was originally wanted',
  );
});

test('a POST is NEVER replayed through the proxy', async () => {
  // This is the one that matters. The proxy is read-only, and re-sending a request body because the first
  // attempt looked like a CORS failure would mean a silent duplicate submission. A POST must fail closed.
  stubFetch(() => { throw new TypeError('Failed to fetch'); });
  await assert.rejects(() => rcsb.text('amyloid'), /Failed to fetch/);
  assert.equal(served.length, 1, `a POST was retried ${served.length} times; it must be attempted once`);
  assert.equal(served[0].method, 'POST');
  assert.ok(!served.some((r) => r.url.startsWith('/api/proxy')), 'no POST may reach the proxy');
});

test('a POST that fails with an HTTP status is also not replayed', async () => {
  stubFetch(() => ({ status: 500, json: null }));
  await assert.rejects(() => rcsb.byUniprot('P99991'), /500/);
  assert.equal(served.length, 1, 'a failed POST must not be retried through the proxy either');
});

test('an aborted request is not retried, so a timeout is not served twice', async () => {
  stubFetch(() => { const e = new Error('aborted'); e.name = 'AbortError'; throw e; });
  await assert.rejects(() => rcsb.entry('9zz4'));
  assert.equal(served.length, 1, 'an abort must not trigger the proxy retry and double the wait');
});

test('a 204 with no content is null, not a parse error', async () => {
  stubFetch(() => ({ status: 204, json: undefined }));
  assert.equal(await rcsb.entry('9zz5'), null);
});

test('a repeated lookup is served from cache and not re-requested', async () => {
  stubFetch(() => okJson({ rcsb_id: '9ZZ6' }));
  const a = await rcsb.entry('9zz6');
  const b = await rcsb.entry('9zz6');
  assert.deepEqual(a, b);
  assert.equal(served.length, 1, 'the same URL should be fetched once per session');
});

test('an HTTP error also goes through the proxy before giving up', async () => {
  // Noted because it is not obvious from the call site: the fallback catches any failure of a GET, not only
  // a CORS refusal, so a 403 or a 502 from a source is retried via the proxy too. That is defensible — the
  // proxy may be allowed where the browser is not — but it means a single lookup can cost two requests, and
  // a test that stubs only the first attempt will measure the wrong thing.
  let attempt = 0;
  stubFetch((url) => {
    attempt++;
    if (attempt === 1) return { status: 502, json: null };
    assert.match(url, /^\/api\/proxy/, 'the second attempt is the proxy');
    return okJson({ rcsb_id: '9ZZ7' });
  });
  const entry = await rcsb.entry('9zz7');
  assert.equal(entry.rcsb_id, '9ZZ7');
  assert.equal(served.length, 2);
});

test('a failure is evicted from the cache, so a later attempt can still succeed', async () => {
  // Caching a rejected promise forever would mean one flaky moment poisons a source for the whole session.
  // Both the direct call and the proxy retry must fail for the lookup itself to fail.
  let call = 0;
  stubFetch(() => { call++; if (call <= 2) return { status: 502, json: null }; return okJson({ rcsb_id: '9ZZA' }); });
  await assert.rejects(() => rcsb.entry('9zza'), /502/);
  assert.equal(served.length, 2, 'direct then proxy, both failing');
  const entry = await rcsb.entry('9zza');
  assert.equal(entry.rcsb_id, '9ZZA', 'the failed promise must not have been kept in the cache');
});

test('a structure file falls back from PDB format to mmCIF', async () => {
  // Large and newer entries have no legacy PDB file. The fallback is what makes those loadable at all.
  stubFetch((url) => {
    if (url.endsWith('.pdb')) return { status: 404, text: '' };
    if (url.endsWith('.cif')) return okText('data_9ZZ8\n_entry.id 9ZZ8\n');
    throw new Error(`unexpected request to ${url}`);
  });
  const got = await rcsb.file('9zz8');
  assert.ok(got.cif, 'an mmCIF fallback should be tagged as cif so the caller parses it correctly');
  assert.match(got.cif, /data_9ZZ8/);
  assert.ok(served.some((r) => r.url.endsWith('.pdb')), 'it should try PDB format first');
});

test('a structure that exists in neither format fails rather than returning empty text', async () => {
  stubFetch(() => ({ status: 404, text: '' }));
  await assert.rejects(() => rcsb.file('9zz9'),
    'both formats missing must be an error, not an empty structure that parses to zero atoms');
});

test('an empty identifier list short-circuits without a request', async () => {
  stubFetch(() => { throw new Error('should not have been called'); });
  assert.deepEqual(await rcsb.details([]), []);
  assert.equal(served.length, 0, 'asking about nothing should not ask the source anything');
});

test('a search with no hits returns an empty list, which is a real answer', async () => {
  // Distinct from a failure: the source answered, and the answer is that there is nothing. Both must be
  // representable, and they must not look the same.
  stubFetch(() => okJson({ total_count: 0, result_set: [] }));
  const r = await rcsb.byUniprot('P99992');
  assert.deepEqual(r, { total: 0, ids: [] });
});

test('a falsy search response is an empty result, not a crash', async () => {
  stubFetch(() => ({ status: 204, json: undefined }));
  assert.deepEqual(await rcsb.byUniprot('P99993'), { total: 0, ids: [] });
});

test('other providers share the same failure contract', async () => {
  // The contract is in the shared helper, so it should hold everywhere. Spot-checked across three more
  // providers rather than assumed from one.
  stubFetch(() => ({ status: 404, json: null }));
  await assert.rejects(() => alphafold.structure('P99994'), /404|No AlphaFold model/);

  stubFetch(() => ({ status: 500, json: null }));
  await assert.rejects(() => uniprot.entry('P99995'), /500/);

  stubFetch(() => ({ status: 503, json: null }));
  await assert.rejects(() => pubchem.byName('notarealcompound-xyz'), /503/);
});

test('every provider URL is https, or the local proxy', async () => {
  // The egress check in `make egress` covers which hosts appear in the source. This covers the scheme: a
  // plain-http request would be blocked by the browser from an https page and silently fail.
  const calls = [];
  stubFetch((url) => { calls.push(url); return okJson({ total_count: 0, result_set: [], data: { entries: [] } }); });
  await Promise.allSettled([
    rcsb.entry('9zy1'), rcsb.byUniprot('P99996'), rcsb.text('kinase'), rcsb.details(['9ZY1']),
    rcsb.ligandSdf('9zy1', 'ATP'), alphafold.prediction('P99997'), uniprot.entry('P99998'),
    pubchem.byName('aspirin-test'),
  ]);
  assert.ok(calls.length >= 6, `expected several provider calls, saw ${calls.length}`);
  for (const url of calls) {
    assert.ok(url.startsWith('https://') || url.startsWith('/api/'),
      `${url} is neither https nor a local path`);
  }
});
