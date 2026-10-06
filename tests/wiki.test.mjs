// Offline checks for the GitHub wiki pages in docs/wiki/.
//
// Prose is not compiled, so it rots silently. These checks are the compiler: every internal link resolves,
// the sidebar and the page set agree, and the three claims the project cannot afford to get wrong are
// asserted mechanically rather than trusted to a reviewer's eye.
//
//   node --test tests/wiki.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'docs', 'wiki');
const files = readdirSync(DIR).filter((f) => f.endsWith('.md')).sort();
const read = (f) => readFileSync(join(DIR, f), 'utf8');
const pages = Object.fromEntries(files.map((f) => [f, read(f)]));

// README.md is publishing instructions, not a wiki page; _Sidebar.md is navigation, not content.
const CONTENT = files.filter((f) => f !== 'README.md' && f !== '_Sidebar.md');
const titles = new Set(CONTENT.map((f) => f.replace(/\.md$/, '')));

test('the page set is present and nothing is empty', () => {
  for (const must of ['Home.md', '_Sidebar.md', 'README.md']) {
    assert.ok(files.includes(must), `docs/wiki/${must} is required by GitHub's wiki conventions`);
  }
  assert.ok(CONTENT.length >= 8, `expected at least 8 content pages, found ${CONTENT.length}`);
  for (const f of files) assert.ok(pages[f].trim().length > 400, `${f} is too short to be a real page`);
});

test('every content page opens with exactly one H1', () => {
  for (const f of CONTENT) {
    const h1 = pages[f].split('\n').filter((l) => /^# \S/.test(l));
    assert.equal(h1.length, 1, `${f} has ${h1.length} H1 headings, expected exactly 1`);
    assert.ok(/^# \S/.test(pages[f].split('\n')[0]), `${f} must start with its H1`);
  }
});

test('every internal wiki link resolves to a page that exists', () => {
  // A GitHub wiki link is [Text](Page-Name) — no extension, no slash, no scheme.
  for (const f of files) {
    for (const m of pages[f].matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
      const t = m[1];
      if (/^(https?:|mailto:|#|\.\.?\/)/.test(t)) continue; // external, anchor, or a repo-relative path
      if (t.includes('.') || t.includes('/')) continue;     // a file reference, not a wiki page link
      assert.ok(titles.has(t), `${f} links to [${t}], which is not a page in docs/wiki/`);
    }
  }
});

test('the sidebar and the page set agree in both directions', () => {
  const linked = new Set();
  for (const m of pages['_Sidebar.md'].matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
    if (!/^(https?:|mailto:)/.test(m[1])) linked.add(m[1]);
  }
  for (const t of titles) assert.ok(linked.has(t), `${t} exists but is not in the sidebar`);
  for (const t of linked) assert.ok(titles.has(t), `the sidebar links to ${t}, which has no page`);
});

test('every content page is reachable from Home or the sidebar', () => {
  const reachable = new Set();
  for (const src of ['Home.md', '_Sidebar.md']) {
    for (const m of pages[src].matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) reachable.add(m[1]);
  }
  for (const t of titles) {
    if (t === 'Home') continue;
    assert.ok(reachable.has(t), `${t} is orphaned: neither Home nor the sidebar links to it`);
  }
});

// --- The three claims the project cannot afford to get wrong --------------------------------------------

test('the docking score is never given affinity units', () => {
  for (const f of files) {
    for (const [i, line] of pages[f].split('\n').entries()) {
      // Mentioning the unit to disclaim it is the point; asserting the score is in it is the failure.
      if (!/kcal\/mol|kJ\/mol/i.test(line)) continue;
      const disclaims = /\bnot\b|\bnever\b|\bno\b|\bwithout\b|rather than|unvalidated|disclaim|unitless/i;
      const warns = /looks like|read as|mistaken|misread|convert|do not/i;
      assert.ok(disclaims.test(line) || warns.test(line),
        `${f}:${i + 1} mentions an energy unit without disclaiming it: ${line.trim()}`);
    }
  }
});

test('the benchmark figure is stated honestly wherever it appears', async () => {
  // This check used to REQUIRE "2 of 4" -- it asserted every `N of 4` claim said 2, and that at
  // least two such claims existed. Written when four cases was the measurement, it then outlived
  // it: once evals/redock.mjs was widened to eleven, the test was holding the retired figure in
  // place on these pages and failing anyone who corrected them. A guard that enforces a stale
  // number is worse than no guard, because it looks like the number was checked.
  //
  // What is enforced now is the rule, not the digits: the case count comes from the eval, no page
  // may overstate the pass rate, and a four-case figure is allowed only where it is explicitly
  // labelled as superseded history.
  const { CASES } = await import('../evals/redock.mjs');
  const SUCCESS = 5, REACHABLE = 9;

  const stated = [];
  for (const f of files) {
    for (const [i, line] of pages[f].split('\n').entries()) {
      const where = `${f}:${i + 1}`;

      // Nothing may claim a better pass rate than was measured, in digits or in words.
      assert.ok(!/\b(6|7|8|9|10|11|six|seven|eight|nine|ten|eleven)\s+of\s+(11|eleven)\b[^.]{0,40}(within|succeed)/i
        .test(line) || /reachable/i.test(line),
        `${where} overstates the benchmark: ${line.trim()}`);

      // A four-case figure is history. It may appear only on a line that says so.
      if (/\b(\d|two|three|four)\s+of\s+(4|four)\b/i.test(line)) {
        assert.ok(/superseded|retired|until iteration|earlier|historical|previously|no longer/i.test(line),
          `${where} cites the four-case benchmark as if current: ${line.trim()}`);
      }

      if (new RegExp(`\\b${SUCCESS} of ${CASES.length}\\b`).test(line)) stated.push({ f, i, line });
    }
  }

  assert.ok(stated.length >= 2,
    `the ${SUCCESS} of ${CASES.length} result should appear on Home and on the docking page`);

  // Where a page gives the reachable figure it must be the measured one.
  for (const f of files) {
    for (const m of pages[f].matchAll(/\b(\d+)\s+of\s+11\s+are\s+reachable/gi)) {
      assert.equal(Number(m[1]), REACHABLE,
        `${f} says ${m[1]} of 11 reachable; the measurement is ${REACHABLE}`);
    }
  }

  // The 2.54 Å median belongs to the retired four-case set and has no eleven-case counterpart.
  for (const f of files) {
    for (const [i, line] of pages[f].split('\n').entries()) {
      if (!/median\s+[\d.]+\s*Å/i.test(line)) continue;
      assert.ok(/superseded|retired|until iteration|earlier|historical|previously/i.test(line),
        `${f}:${i + 1} gives a median as a current figure; the eleven-case set has none: ${line.trim()}`);
    }
  }
});

test('the pages that cite the benchmark say it was carried forward, not re-measured', () => {
  for (const f of ['Home.md', 'Docking-and-Scoring.md', 'Testing.md']) {
    assert.ok(/carried forward|needs the network|\*\*Needs the network\*\*/i.test(pages[f]),
      `${f} cites the benchmark without saying it was carried forward rather than re-measured`);
  }
});

test('the limits page is linked from the front page and covers the standing caveats', () => {
  assert.ok(/\(Known-Limits\)/.test(pages['Home.md']), 'Home must link to Known Limits');
  const limits = pages['Known-Limits.md'];
  for (const topic of [/wet lab/i, /Ray-Ban/i, /settle|facilitator/i, /not a blockchain|blockchain/i,
    /no revenue|signed customer/i, /Ed25519/i]) {
    assert.ok(topic.test(limits), `Known-Limits.md does not cover ${topic}`);
  }
});

test('the ledger page refuses the blockchain claim outright', () => {
  const p = pages['Provenance-Ledger.md'];
  assert.ok(/not a blockchain/i.test(p), 'the ledger page must say plainly that it is not a blockchain');
  assert.ok(/no consensus|single-writer|local/i.test(p), 'it must say why: local, single-writer, no consensus');
});

test('no page promises narration, settlement or lab validation as done', () => {
  const forbidden = [
    /\bnarrated\b/i,
    /settlement (is|has been) (live|wired|complete)/i,
    /\b(validated|confirmed) in (a|the) (wet )?lab\b/i,
  ];
  // A sentence that denies the claim is the opposite of the failure, so a negated line is fine. This is
  // the crude part of a crude check: it catches a confident assertion, not a carefully hedged one.
  const negated = /\b(not|nothing|never|no|none|without|yet to be|waiting|blocked|cannot)\b/i;
  for (const f of files) {
    for (const [i, line] of pages[f].split('\n').entries()) {
      if (negated.test(line)) continue;
      for (const re of forbidden) {
        assert.ok(!re.test(line), `${f}:${i + 1} claims something unproven as done: ${line.trim()}`);
      }
    }
  }
});

test('the tool and intent counts on the wiki match the modules', async () => {
  const { INTENTS } = await import('../js/voice.js');
  const voicePage = pages['Voice-and-Agent-Control.md'];
  const stated = voicePage.match(/The (\w+) intents/);
  assert.ok(stated, 'the voice page should name how many intents there are');
  const words = { nineteen: 19, eighteen: 18, twenty: 20, seventeen: 17 };
  assert.equal(words[stated[1].toLowerCase()], INTENTS.length,
    `the wiki says "${stated[1]}" intents but js/voice.js publishes ${INTENTS.length}`);
  // Every intent name must appear on the page, so a new intent cannot ship undocumented.
  for (const { intent } of INTENTS) {
    assert.ok(voicePage.includes(`\`${intent}\``), `intent ${intent} is not documented on the voice page`);
  }
});

test('every data-source host on the wiki is one the client actually calls', () => {
  const api = readFileSync(join(DIR, '..', '..', 'js', 'api.js'), 'utf8');
  const real = new Set([...api.matchAll(/https:\/\/([a-z0-9.-]+)/g)].map((m) => m[1]));
  const page = pages['Data-Sources.md'];
  const listed = new Set([...page.matchAll(/`([a-z0-9]+(?:\.[a-z0-9-]+)+)`/g)].map((m) => m[1]));
  for (const host of listed) {
    if (!host.includes('.') || /\.(js|py|mjs|md|html|json)$/.test(host)) continue;
    assert.ok(real.has(host), `Data-Sources.md lists ${host}, which js/api.js never calls`);
  }
  assert.ok(listed.size >= 15, `only ${listed.size} hosts listed; js/api.js calls ${real.size}`);
});
