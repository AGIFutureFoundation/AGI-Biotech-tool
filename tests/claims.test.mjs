// Re-measures the quantitative claims the whitepaper makes about this repository.
//
// docs/WHITE_PAPER.md carries an Appendix A listing every figure it states next to the command that
// produces it, and it says in as many words: "do not trust it, run the commands ... any figure that is not
// reproducible should be treated as deleted." That is the right rule and it had quietly stopped holding.
// Before iteration 17 the appendix claimed 763 tests passing, 775 collected and 2,034 lines of test code,
// against an actual 1,438 passing, ~1,496 collected and 9,203 lines — and it did not mention the JavaScript
// suites at all. Nobody had lied; the document had simply been written once and the repository had kept
// moving.
//
// Prose cannot notice that happening. This can. Every claim below is measured from the filesystem and
// compared against what the document says, so a figure and its reality cannot drift apart again without a
// test going red.
//
// Deliberately NOT asserted here: the exact Python collection count. Another session commits to this
// repository concurrently and adds Python tests, so that number moves between runs — it was 1,499 and
// 1,496 within the same hour. Asserting it would produce a test that fails for reasons unrelated to the
// claim it guards. What is asserted instead is that the document states when it measured, which is the
// project's own rule for a figure that cannot be pinned.
//
//   node --test tests/claims.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (rel) => readFileSync(join(ROOT, rel), 'utf8');
const WHITEPAPER = read('docs/WHITE_PAPER.md');

const lineCount = (files) => files.reduce((n, f) => n + read(f).split('\n').length, 0) - files.length
  + files.filter((f) => read(f).endsWith('\n')).length;

const testFiles = (ext) => readdirSync(join(ROOT, 'tests'))
  .filter((f) => f.endsWith(ext)).map((f) => `tests/${f}`);

// `wc -l` counts newlines, which is what the commands in the appendix use.
const wcL = (files) => files.reduce((n, f) => n + (read(f).match(/\n/g) || []).length, 0);

// A claimed number as the appendix writes it, with or without thousands separators.
function claimed(pattern) {
  const m = WHITEPAPER.match(pattern);
  assert.ok(m, `the whitepaper no longer states a figure matching ${pattern}`);
  return Number(m[1].replace(/,/g, ''));
}

test('the whitepaper says when it measured, because some figures cannot be pinned', () => {
  // The project's own rule: a number carries the command that produced it and the date it was produced.
  assert.match(WHITEPAPER, /Measured 6 October 2026/,
    'the test-suite section must state its measurement date');
  assert.match(WHITEPAPER, /re-measured on 6 October 2026/,
    'Appendix A must state when its figures were last re-measured');
});

test('the claimed line count of test code is the line count of the test code', () => {
  const files = [...testFiles('.py'), ...testFiles('.mjs')];
  const actual = wcL(files);
  const stated = claimed(/([\d,]+) lines of test code/);
  assert.equal(stated, actual,
    `the whitepaper claims ${stated} lines of test code; cat tests/*.py tests/*.mjs | wc -l gives ${actual}`);
});

test('the claimed number of JavaScript modules is the number of JavaScript modules', () => {
  const actual = readdirSync(join(ROOT, 'js')).filter((f) => f.endsWith('.js')).length;
  const stated = claimed(/([\d,]+) JS modules/);
  assert.equal(stated, actual, `the whitepaper claims ${stated} JS modules; ls js/*.js gives ${actual}`);
});

test('the claimed line count of Python source is the line count of the Python source', () => {
  const files = ['server', 'scripts'].flatMap((d) =>
    readdirSync(join(ROOT, d)).filter((f) => f.endsWith('.py')).map((f) => `${d}/${f}`));
  const actual = wcL(files);
  const stated = claimed(/([\d,]+) lines of Python/);
  assert.equal(stated, actual,
    `the whitepaper claims ${stated} lines of Python; cat server/*.py scripts/*.py | wc -l gives ${actual}`);
});

test('the claimed test-file counts are the test-file counts', () => {
  const m = WHITEPAPER.match(/(\d+) Python and (\d+) JavaScript test files/);
  assert.ok(m, 'the whitepaper should state how many test files there are');
  assert.equal(Number(m[1]), testFiles('.py').length, 'Python test file count');
  assert.equal(Number(m[2]), testFiles('.mjs').length, 'JavaScript test file count');
});

test('the claimed JavaScript test count is the number of cases declared', () => {
  // Counting declarations rather than running the runner from inside itself. Every suite in this repository
  // writes one `test(` per case at the start of a line, so the two agree; if a suite ever starts generating
  // cases in a loop this test should be changed to run the runner, not loosened.
  let declared = 0;
  for (const f of testFiles('.mjs')) {
    declared += (read(f).match(/^test\(/gm) || []).length;
  }
  const stated = claimed(/([\d,]+) JavaScript tests pass/);
  assert.equal(stated, declared,
    `the whitepaper claims ${stated} JavaScript tests; ${declared} cases are declared across the suites`);
});

test('the whitepaper states the Python result honestly, failures included', () => {
  // The number that matters is not the flattering one. Five tests fail here because they bind a local port
  // and the sandbox refuses; the document must say so rather than quoting a clean run.
  assert.match(WHITEPAPER, /5 failed, 1438 passed/,
    'the suite line must carry the failures alongside the passes');
  assert.match(WHITEPAPER, /bind a local (TCP )?port/,
    'and must say why those five fail, so a reader can judge whether it matters to them');
  assert.ok(!/^\s*1438 passed[^,]*$/m.test(WHITEPAPER),
    'the passing count must never appear without its failures');
});

// Every surface that publishes the benchmark. docs/pitchdeck.html is deliberately absent: the other
// session has uncommitted changes to it, and a guard that fails on someone else's in-flight edit is a bad
// guard. It is a queue item in docs/ROADMAP_LOOP.md, not an oversight.
const BENCHMARK_SURFACES = [
  'docs/WHITE_PAPER.md', 'docs/wiki/Home.md', 'docs/wiki/Docking-and-Scoring.md', 'docs/wiki/Testing.md',
  'docs/progress-report.html', 'docs/investor-brief.html',
];

// An inflated pass rate, in digits or in words. The investor brief spells its numbers out — "Two of four
// within 2 Å" — so a digit-only check would have let "Three of four" through the one document where an
// overstatement costs the most. Found by auditing that file rather than by the check working.
const INFLATED = /\b(3|4|three|four)\s+of\s+(4|four)\b[^.]{0,40}within\s+2/i;

test('the benchmark figure is the measured one, everywhere it is published', () => {
  // The weakest claim in the product, and the one with the most incentive to drift upward.
  for (const f of BENCHMARK_SURFACES) {
    for (const [i, line] of read(f).split('\n').entries()) {
      // A phrase inside quotation marks is being discussed, not asserted — the progress report quotes the
      // forbidden wording in order to describe this very check. The quote must sit IMMEDIATELY before the
      // phrase: an earlier draft allowed any quote anywhere on the line, which in an HTML file matched the
      // quotes around a style attribute and so exempted almost every line in the documents that matter
      // most. A mutation test caught that; the escape hatch is now as narrow as its purpose.
      const quoted = /["“”'](?:\s*)(3|4|three|four)\s+of\s+(4|four)\b/i.test(line);
      assert.ok(quoted || !INFLATED.test(line),
        `${f}:${i + 1} overstates the benchmark pass rate: ${line.trim()}`);
      for (const m of line.matchAll(/median\s+([\d.]+)\s*(Å|A)\b/gi)) {
        assert.equal(m[1], '2.54', `${f}:${i + 1} gives a median of ${m[1]}; the measured value is 2.54 Å`);
      }
    }
  }
});

test('the inflation check actually catches an inflated claim, in digits and in words', () => {
  // A guard this cheap to get wrong is worth proving against known-bad input rather than trusting.
  for (const bad of ['3 of 4 within 2 Å', 'Four of four within 2 Å, median 2.54 Å',
    'three of 4 within 2 A', '4 of 4 within 2 Å']) {
    assert.ok(INFLATED.test(bad), `the check should reject "${bad}"`);
  }
  for (const good of ['2 of 4 within 2 Å', 'Two of four within 2 Å, median 2.54 Å',
    'two of 4 within 2 A', 'four of the compounds were screened']) {
    assert.ok(!INFLATED.test(good), `the check should accept "${good}"`);
  }
});

test('the quoted-phrase exemption is narrow enough to be useless as a loophole', () => {
  // The exemption exists so a page can quote the forbidden wording while describing this check. It must not
  // let an actual claim through just because a quotation mark appears earlier on the line — which is what
  // happens in HTML, where every attribute carries quotes.
  const exempt = (line) => /["“”'](?:\s*)(3|4|three|four)\s+of\s+(4|four)\b/i.test(line);
  assert.ok(exempt('<li>Any line claiming "4 of 4 within 2 Å" fails the suite</li>'),
    'a directly quoted phrase should be exempt');
  assert.ok(!exempt('<p style="margin-top:12px"><strong>Three of four within 2 Å</strong></p>'),
    'an HTML attribute quote must not exempt a claim made later on the same line');
  assert.ok(!exempt('We achieved four of four within 2 Å on the panel we chose'),
    'an unquoted claim is never exempt');
});

test('a surface that publishes the benchmark also publishes the failures', () => {
  // The honest version of this figure is the table, not the headline. A page that says "2 of 4 within 2 Å"
  // and drops the two failing rows has kept the number and lost the point of it.
  for (const f of BENCHMARK_SURFACES) {
    const text = read(f);
    if (!/\b(2|two)\s+of\s+(4|four)\b/i.test(text)) continue;
    assert.ok(/thrombin/i.test(text) && /BCL/i.test(text),
      `${f} states the benchmark pass rate without naming the two cases that fail`);
    assert.ok(/fail/i.test(text), `${f} should say plainly that those cases failed`);
  }
});

test('no published surface gives the docking score an energy unit without disclaiming it', () => {
  const surfaces = ['docs/WHITE_PAPER.md', 'docs/wiki/Docking-and-Scoring.md', 'docs/wiki/Known-Limits.md',
    'docs/progress-report.html', 'docs/investor-brief.html'];
  const disclaims = /\bnot\b|\bnever\b|\bno\b|\bwithout\b|rather than|unvalidated|unitless|disclaim/i;
  const warns = /looks like|read as|mistaken|misread|convert|do not/i;
  for (const f of surfaces) {
    for (const [i, line] of read(f).split('\n').entries()) {
      if (!/kcal\/mol|kJ\/mol/i.test(line)) continue;
      assert.ok(disclaims.test(line) || warns.test(line),
        `${f}:${i + 1} mentions an energy unit without disclaiming it: ${line.trim()}`);
    }
  }
});

test('Appendix A pairs every claim with a command, with no empty rows', () => {
  const start = WHITEPAPER.indexOf('## Appendix A');
  assert.ok(start > 0, 'the whitepaper must still have its claims appendix');
  const rows = WHITEPAPER.slice(start).split('\n')
    .filter((l) => l.startsWith('|') && !/^\|\s*-+/.test(l) && !/^\|\s*Claim\s*\|/.test(l));
  assert.ok(rows.length >= 15, `the appendix should list the claims, found ${rows.length} rows`);
  for (const row of rows) {
    // An escaped \| inside a backticked command is not a cell separator.
    const cells = row.replace(/\\\|/g, '\u0001').split('|')
      .map((c) => c.trim().replace(/\u0001/g, '|'))
      .filter((c, i, a) => i > 0 && i < a.length - 1);
    assert.equal(cells.length, 2, `a claims row should be claim and command: ${row}`);
    assert.ok(cells[0].length > 3, `a claim cannot be blank: ${row}`);
    // "same" is the table's way of pointing at the command in the row above, which is a command.
    assert.ok(/`/.test(cells[1]) || /^same$/i.test(cells[1]),
      `every claim needs a command, in backticks or "same" as the row above: ${row}`);
  }
});

test('the whitepaper records what the tests found, not only that they pass', () => {
  // A suite that only confirms expectations is weak evidence, and a document that reports only a pass count
  // is making exactly that weak argument. The defects the tests located belong in it.
  assert.match(WHITEPAPER, /What the tests found/i, 'the whitepaper should list what the tests caught');
  for (const defect of [/planarity/i, /insertion code/i, /lark two|LRRK2/i]) {
    assert.ok(defect.test(WHITEPAPER), `the defect list should mention ${defect}`);
  }
  assert.match(WHITEPAPER, /removed from its \*end\*|removed from its end/i,
    'and the hash-chain truncation limit, which was documented rather than fixed');
});
