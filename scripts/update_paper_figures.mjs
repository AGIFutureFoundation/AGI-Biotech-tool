// Rewrite the measured figures in docs/WHITE_PAPER.md from the filesystem.
//
// Appendix A says of itself: "do not trust it, run the commands ... any figure
// that is not reproducible should be treated as deleted." tests/claims.test.mjs
// enforces that by re-measuring. This is the other half -- the thing that makes
// the figures right again when they drift, so the fix is a command rather than
// a person retyping numbers, which is how they drifted in the first place.
//
// It measures exactly what claims.test.mjs measures, deliberately duplicating
// those expressions rather than importing them: a shared helper would let a
// mistake in the measurement satisfy its own test.
//
//   node scripts/update_paper_figures.mjs            # all but the suite line
//   node scripts/update_paper_figures.mjs --suite "5 failed, 1558 passed, ..."
//
// The suite line is passed in rather than measured here, because running the
// suite from inside this script would report a different number than the run
// the document quotes.
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (rel) => readFileSync(join(ROOT, rel), 'utf8');
const wcL = (files) => files.reduce((n, f) => n + (read(f).match(/\n/g) || []).length, 0);
const testFiles = (ext) => readdirSync(join(ROOT, 'tests'))
  .filter((f) => f.endsWith(ext)).map((f) => `tests/${f}`);

const py = testFiles('.py');
const mjs = testFiles('.mjs');
const src = ['server', 'scripts'].flatMap((d) =>
  readdirSync(join(ROOT, d)).filter((f) => f.endsWith('.py')).map((f) => `${d}/${f}`));

const m = {
  testLines: wcL([...py, ...mjs]),
  pyLines: wcL(src),
  jsModules: readdirSync(join(ROOT, 'js')).filter((f) => f.endsWith('.js')).length,
  pyFiles: py.length,
  mjsFiles: mjs.length,
  jsTests: mjs.reduce((n, f) => n + (read(f).match(/^test\(/gm) || []).length, 0),
};

const argv = process.argv.slice(2);
const suiteIdx = argv.indexOf('--suite');
const suite = suiteIdx === -1 ? null : argv[suiteIdx + 1];
const group = (n) => n.toLocaleString('en-US');

let w = read('docs/WHITE_PAPER.md');
const before = w;
const sub = (re, to) => { w = w.replace(re, to); };

sub(/[\d,]+ lines of test code/g, `${group(m.testLines)} lines of test code`);
sub(/[\d,]+ lines of Python/g, `${group(m.pyLines)} lines of Python`);
sub(/[\d,]+ JS modules/g, `${group(m.jsModules)} JS modules`);
sub(/\d+ Python files and \d+ JavaScript files/g,
    `${m.pyFiles} Python files and ${m.mjsFiles} JavaScript files`);
sub(/\d+ Python and \d+ JavaScript test files/g,
    `${m.pyFiles} Python and ${m.mjsFiles} JavaScript test files`);
sub(/[\d,]+ JavaScript tests pass/g, `${group(m.jsTests)} JavaScript tests pass`);
sub(/pass \d+  fail 0/g, `pass ${m.jsTests}  fail 0`);

if (suite) {
  sub(/\d+ failed, [\d,]+ passed, \d+ skipped, 1 xfailed, \d+ warnings in [\d.]+s(?: \(\d:\d\d:\d\d\))?/g, suite);
  const short = suite.match(/(\d+ failed, [\d,]+ passed, \d+ skipped, 1 xfailed)/);
  if (short) sub(/\| \d+ failed, [\d,]+ passed, \d+ skipped, 1 xfailed \|/g, `| ${short[1]} |`);
}

writeFileSync(join(ROOT, 'docs/WHITE_PAPER.md'), w);
console.log(JSON.stringify({ ...m, suite: suite ?? '(unchanged)', changed: before !== w }, null, 1));
