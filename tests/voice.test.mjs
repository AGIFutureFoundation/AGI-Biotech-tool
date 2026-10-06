// Offline checks for the spoken-command parser in js/voice.js.
//
// Speech recognisers mangle gene symbols, drop articles and spell things out, so the parser is the
// place a hands-free session quietly goes wrong. These cases run without a browser, a microphone or
// the Web Speech API: parseCommand is a pure function.
//
//   node --test tests/voice.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { parseCommand, levenshtein, INTENTS } from '../js/voice.js';

const VOCAB = ['SOD1', 'LRRK2', 'TARDBP', 'BCL2L1', 'GBA1', 'AGI-001'];
const parse = (s) => parseCommand(s, VOCAB);

test('plain commands reach the intent a researcher meant', () => {
  const cases = [
    ['dock it', 'dock'],
    ['dock the ligand', 'dock'],
    ['run docking', 'dock'],
    ['find pockets', 'find_pockets'],
    ['where are the pockets', 'find_pockets'],
    ['start dynamics', 'start_md'],
    ['stop the simulation', 'stop_md'],
    ['gather evidence', 'evidence'],
    ['what am i looking at', 'explain'],
    ['explain this', 'explain'],
    ['next compound', 'next_compound'],
    ['previous compound', 'prev_compound'],
    ['help', 'help'],
  ];
  for (const [said, want] of cases) {
    assert.equal(parse(said).intent, want, `"${said}" should be ${want}`);
  }
});

test('a target is loaded whether or not the verb and articles are there', () => {
  for (const said of ['load SOD1', 'show me SOD1', 'open the target SOD1', 'SOD1']) {
    const r = parse(said);
    assert.equal(r.intent, 'load_target', `"${said}"`);
    assert.equal(String(r.slots.query).toUpperCase(), 'SOD1', `"${said}" query`);
  }
});

test('a gene symbol spoken aloud resolves through the vocabulary', () => {
  // A recogniser returns the trailing digit as a word: LRRK2 comes back as "lark two".
  const r = parse('load lark two');
  assert.equal(r.intent, 'load_target');
  assert.equal(String(r.slots.query).toUpperCase(), 'LRRK2', `heard "${r.slots.heard ?? ''}"`);
});

test('a spoken trailing digit works with no vocabulary loaded', () => {
  const r = parseCommand('load sod one');
  assert.equal(r.intent, 'load_target');
  assert.equal(String(r.slots.query).toUpperCase(), 'SOD1');
});

test('a four-character PDB code is recognised as a structure, not a gene', () => {
  for (const said of ['load 2yxj', '2yxj']) {
    const r = parse(said);
    assert.equal(r.intent, 'load_pdb', `"${said}"`);
    assert.equal(r.slots.id, '2YXJ');
  }
});

test('colour commands map onto the renderer modes', () => {
  const want = {
    'colour by confidence': 'confidence',
    'color by missense': 'missense',
    'colour by chain': 'chain',
    'colour by rainbow': 'rainbow',
  };
  for (const [said, mode] of Object.entries(want)) {
    const r = parse(said);
    assert.equal(r.intent, 'colour_by', `"${said}"`);
    assert.equal(r.slots.mode, mode, `"${said}" mode`);
  }
});

test('an unintelligible colour is reported as unknown rather than guessed', () => {
  const r = parse('colour by wibble');
  assert.equal(r.intent, 'colour_by');
  assert.equal(r.slots.mode, null, 'a wrong colour is worse than no colour');
});

test('representation commands map onto the renderer styles', () => {
  for (const [said, rep] of [['show cartoon', 'cartoon'], ['show spacefill', 'spacefill'], ['show sticks', 'sticks']]) {
    const r = parse(said);
    assert.equal(r.intent, 'representation', `"${said}"`);
    assert.equal(r.slots.rep, rep, `"${said}" rep`);
  }
});

test('a screen command carries a spoken number when one is given', () => {
  assert.equal(parse('screen the library').intent, 'screen');
  assert.equal(parse('screen the library').slots.limit, undefined);
  const twelve = parse('screen twelve compounds');
  assert.equal(twelve.intent, 'screen');
  assert.equal(twelve.slots.limit, 12, 'spoken numbers arrive as words, never digits');
});

test('search is distinguished from loading', () => {
  const r = parse('search for amyotrophic lateral sclerosis');
  assert.equal(r.intent, 'search');
  assert.match(r.slots.query, /amyotrophic lateral sclerosis/);
});

test('silence and noise are unknown, and never a destructive command', () => {
  for (const said of ['', '   ', 'um', 'the weather in london tomorrow']) {
    const r = parse(said);
    assert.equal(r.intent, 'unknown', `"${said}" must not trigger an action`);
  }
});

test('every parsed result carries the transcript back for the caller to show', () => {
  const r = parse('dock it');
  assert.equal(r.transcript, 'dock it');
  assert.ok(typeof r.confidence === 'number');
  assert.ok(r.slots && typeof r.slots === 'object');
});

test('levenshtein behaves as the fuzzy matcher assumes', () => {
  assert.equal(levenshtein('sod1', 'sod1'), 0);
  assert.equal(levenshtein('sod1', 'sod one'), 4);
  assert.ok(levenshtein('lrrk2', 'lark2') <= 2);
  assert.equal(levenshtein('', 'abc'), 3);
});

test('the published intent list covers what the parser can return', () => {
  assert.ok(Array.isArray(INTENTS) && INTENTS.length > 0);
  const published = new Set(INTENTS.map((i) => i.intent));
  // Anything the parser emits must be documented, or the help text and the LLM schema go stale.
  const emitted = ['dock', 'find_pockets', 'screen', 'start_md', 'stop_md', 'colour_by',
    'representation', 'load_target', 'load_pdb', 'search', 'evidence', 'explain',
    'next_compound', 'prev_compound', 'help', 'unknown'];
  for (const intent of emitted) {
    assert.ok(published.has(intent), `INTENTS is missing "${intent}"`);
  }
  for (const entry of INTENTS) {
    if (entry.intent === 'unknown') continue;   // the fallback has nothing to exemplify
    assert.ok(Array.isArray(entry.examples) && entry.examples.length > 0, `${entry.intent} has no examples`);
  }
});

test('every published example parses to the intent it is published under', () => {
  const skip = new Set(['unknown']);
  for (const entry of INTENTS) {
    if (skip.has(entry.intent)) continue;
    for (const example of entry.examples) {
      assert.equal(parse(example).intent, entry.intent,
        `example "${example}" is published under ${entry.intent}`);
    }
  }
});
