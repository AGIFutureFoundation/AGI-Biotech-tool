// Hands-free voice control for the molecular workspace.
// Web Speech API only (SpeechRecognition + speechSynthesis); no network services of our own.

export const INTENTS = [
  { intent: 'load_target', slots: ['query'], examples: ['load SOD1', 'show me LRRK2', 'open parkin'] },
  { intent: 'load_pdb', slots: ['id'], examples: ['load 2YXJ', 'structure two y x j'] },
  { intent: 'search', slots: ['query'], examples: ['search for amyotrophic lateral sclerosis'] },
  { intent: 'dock', slots: [], examples: ['dock it', 'dock the ligand', 'run docking'] },
  { intent: 'find_pockets', slots: [], examples: ['find pockets', 'where are the pockets'] },
  { intent: 'screen', slots: ['limit?'], examples: ['screen the library', 'screen twelve compounds'] },
  { intent: 'start_md', slots: [], examples: ['start dynamics', 'run the simulation'] },
  { intent: 'stop_md', slots: [], examples: ['stop dynamics', 'stop the simulation'] },
  { intent: 'colour_by', slots: ['mode'], examples: ['colour by confidence', 'colour by missense', 'colour by chain', 'colour by hydrophobicity', 'colour by secondary structure', 'colour by rainbow'] },
  { intent: 'representation', slots: ['rep'], examples: ['show cartoon', 'show spacefill', 'show sticks', 'show ball and stick', 'show surface'] },
  { intent: 'next_compound', slots: [], examples: ['next compound', 'next'] },
  { intent: 'prev_compound', slots: [], examples: ['previous compound', 'previous'] },
  { intent: 'evidence', slots: [], examples: ['gather evidence', 'what do we know about this'] },
  { intent: 'explain', slots: [], examples: ['explain this', 'what am I looking at', 'read me the score'] },
  { intent: 'measure', slots: [], examples: ['measure', 'measure the distance'] },
  { intent: 'reset_view', slots: [], examples: ['reset view', 'recentre'] },
  { intent: 'undo', slots: [], examples: ['undo', 'undo that'] },
  { intent: 'help', slots: [], examples: ['help', 'what can I say'] },
  { intent: 'unknown', slots: [], examples: [] },
];
const DIGIT = { zero: '0', one: '1', two: '2', three: '3', four: '4', five: '5', six: '6', seven: '7', eight: '8', nine: '9' };
const NUM = { ...Object.fromEntries(Object.entries(DIGIT).map(([k, v]) => [k, +v])), ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17, eighteen: 18, nineteen: 19, twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70, eighty: 80, ninety: 90, hundred: 100 };
// How recognisers commonly write individual spoken letters.
const LETTER = { bee: 'b', be: 'b', see: 'c', sea: 'c', dee: 'd', gee: 'g', jay: 'j', kay: 'k', el: 'l', em: 'm', en: 'n', pee: 'p', cue: 'q', queue: 'q', are: 'r', ess: 's', tee: 't', tea: 't', you: 'u', vee: 'v', ex: 'x', why: 'y', zed: 'z', zee: 'z' };
const COLOUR_MODES = {
  confidence: ['confidence', 'plddt', 'pl ddt', 'b factor', 'alphafold confidence'],
  missense: ['missense', 'alphamissense', 'alpha missense', 'pathogenicity', 'variants', 'mutations'],
  chain: ['chain', 'chains'],
  hydrophobicity: ['hydrophobicity', 'hydrophobic', 'hydropathy'],
  secondary_structure: ['secondary structure', 'secondary', 'structure', 'ss'],
  rainbow: ['rainbow', 'spectrum', 'n to c'],
};
const REPS = {
  ball_and_stick: ['ball and stick', 'balls and sticks', 'ball stick'],
  cartoon: ['cartoon', 'ribbon', 'ribbons'],
  spacefill: ['spacefill', 'space fill', 'space filling', 'spheres', 'cpk'],
  sticks: ['sticks', 'stick', 'licorice', 'liquorice'],
  surface: ['surface', 'molecular surface'],
};
const RULES = [
  ['help', /^(help|what can i say|what can you do|list commands|commands)\b/],
  ['stop_md', /\b(stop|end|pause|halt|freeze)\b.*\b(dynamics|simulation|md)\b/],
  ['start_md', /\b(start|run|begin|play|resume|launch)\b.*\b(dynamics|simulation|md)\b/],
  ['dock', /\bdock(ing)?\b/],
  ['find_pockets', /\bpockets?\b|\bbinding sites?\b/],
  ['next_compound', /^next\b|\bnext (compound|ligand|molecule|hit|one)\b/],
  ['prev_compound', /^(previous|prev)\b|\b(previous|prev|last) (compound|ligand|molecule|hit|one)\b/],
  ['evidence', /\bevidence\b|\bwhat do (we|you) know\b/],
  ['explain', /\bexplain\b|\bwhat am i (looking at|seeing)\b|\bread (me )?the scores?\b|\bwhat(s| is) the score\b/],
  ['measure', /\bmeasure\b|\bdistance\b/],
  ['reset_view', /^reset\b|\breset( the)? (view|camera)\b|\brecent(er|re)\b|\bcent(er|re) the view\b/],
  ['undo', /^undo\b|\bundo that\b|\btake that back\b/],
];

export function levenshtein(a, b) {
  if (a === b) return 0;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    prev = cur;
  }
  return prev[b.length];
}
const compact = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
const similarity = (a, b) => (!a || !b ? 0 : 1 - levenshtein(a, b) / Math.max(a.length, b.length));

// Best vocabulary match for a phrase: tries the whole phrase squashed together, each word, and word pairs.
// Gene symbols nearly all end in a digit, and a recogniser hands that digit back as a word: LRRK2
// arrives as "lark two", SOD1 as "sod one". Comparing those letter by letter never gets close, so the
// spelled-out trailing number is also offered to the matcher as a digit.
function digitiseTail(phrase) {
  const words = String(phrase).split(' ').filter(Boolean);
  if (words.length < 2) return null;
  const last = words[words.length - 1];
  if (!(last in NUM) || NUM[last] > 20) return null;
  return [...words.slice(0, -1), String(NUM[last])].join(' ');
}

function fuzzyVocab(phrase, vocabulary, threshold = 0.7) {
  if (!vocabulary.length || !phrase) return null;
  const words = phrase.split(' ').filter(Boolean);
  const cands = new Set([compact(phrase), ...words.map(compact)]);
  for (let i = 0; i < words.length - 1; i++) cands.add(compact(words[i] + words[i + 1]));
  const digitised = digitiseTail(phrase);
  if (digitised) cands.add(compact(digitised));
  let best = null;
  for (const word of vocabulary) for (const c of cands) {
    const score = similarity(c, compact(word));
    if (score >= threshold && (!best || score > best.score)) best = { word, score };
  }
  return best;
}

// Joins runs of spelled-out letters and digits: "s o d one" -> "sod1", "two why ex jay" -> "2yxj".
// A run needs at least two letters and three tokens, so ordinary words like "a" survive.
function collapseSpelled(tokens) {
  const out = [];
  let run = [];
  const flush = () => {
    const letters = run.filter((t) => /^[a-z]$/.test(t.v)).length;
    const genuine = run.some((t) => t.raw.length === 1 || DIGIT[t.raw]);
    out.push(...(letters >= 2 && run.length >= 3 && genuine ? [run.map((t) => t.v).join('')] : run.map((t) => t.raw)));
    run = [];
  };
  for (const raw of tokens) {
    const v = /^[a-z0-9]$/.test(raw) ? raw : DIGIT[raw] || LETTER[raw];
    if (v) run.push({ raw, v });
    else { flush(); out.push(raw); }
  }
  flush();
  return out;
}

function normalise(text) {
  let t = String(text || '').toLowerCase().replace(/colour/g, 'color').replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
  t = t.replace(/^(hey |ok |okay |please |now |so |and )+/, '')
    .replace(/^(can you|could you|would you|will you|lets|let us|i want to|i would like to|go ahead and)\s+/, '')
    .replace(/\s+please$/, '');
  return collapseSpelled(t.split(' ').filter(Boolean)).join(' ');
}
function parseNumber(words) {
  let total = 0, found = false;
  for (const w of words) {
    if (/^\d+$/.test(w)) { total += +w; found = true; } else if (w === 'hundred') { total = (total || 1) * 100; found = true; } else if (w in NUM) { total += NUM[w]; found = true; } else if (found && w !== 'and') break;
  }
  return found ? total : undefined;
}
function matchAlias(phrase, table, fuzzy = true) {
  const padded = ` ${phrase} `;
  for (const [key, aliases] of Object.entries(table)) if (aliases.some((a) => padded.includes(` ${a} `))) return key;
  if (!fuzzy) return null;
  let best = null;
  for (const [key, aliases] of Object.entries(table)) for (const a of aliases) {
    const score = similarity(compact(phrase), compact(a));
    if (score >= 0.7 && (!best || score > best.score)) best = { key, score };
  }
  return best && best.key;
}
function targetSlots(query, vocabulary) {
  const q = query.replace(/\s+(structure|protein|gene|please)$/, '').trim();
  if (/^[0-9][a-z0-9]{3}$/.test(compact(q)) && q.split(' ').length <= 4) return ['load_pdb', { id: compact(q).toUpperCase() }];
  const hit = fuzzyVocab(q, vocabulary);
  if (hit) return ['load_target', { query: hit.word, heard: q, score: +hit.score.toFixed(2) }];
  // Looks like a gene symbol ("sod 1", "lrrk2"): squash and upper-case it. A spelled-out trailing
  // number counts as a digit here too, so "sod one" works with no vocabulary loaded.
  const spoken = digitiseTail(q);
  if (spoken && spoken.split(' ').length <= 2 && compact(spoken).length <= 8) {
    return ['load_target', { query: compact(spoken).toUpperCase(), heard: q }];
  }
  const words = q.split(' ');
  if (words.length <= 2 && /\d/.test(q) && compact(q).length <= 8) return ['load_target', { query: compact(q).toUpperCase() }];
  return ['load_target', { query: q }];
}

export function parseCommand(text, vocabulary = []) {
  const transcript = String(text || '').trim();
  const t = normalise(transcript);
  const out = (intent, slots = {}) => ({ intent, slots, transcript, confidence: 1 });
  if (!t) return out('unknown');

  for (const [intent, re] of RULES) if (re.test(t)) return out(intent);

  if (/^screen\b/.test(t) || /\bscreen (the )?(library|compounds)\b/.test(t)) {
    const limit = parseNumber(t.split(' ').slice(1));
    return out('screen', limit ? { limit } : {});
  }
  const colour = t.match(/\bcolou?r(?:ed|s)?\b(?: it| them| the \w+)?(?: by| on| according to| with)?\s*(.*)$/);
  if (colour) return out('colour_by', { mode: matchAlias(colour[1], COLOUR_MODES) });

  if (/^(show|display|switch to|switch|use|render|draw|make it|change to|as)\b/.test(t) || matchAlias(t, REPS, false) && t.split(' ').length <= 3) {
    const rep = matchAlias(t.replace(/^(show|display|switch to|switch|use|render|draw|make it|change to|as)( me)?( the| a| as)?\s*/, ''), REPS, false);
    if (rep) return out('representation', { rep });
  }
  const search = t.match(/^(?:search|look up|lookup|find|query)\s+(?:for\s+|about\s+)?(.+)$/);
  if (search) return out('search', { query: search[1] });

  const load = t.match(/^(?:load|show(?: me)?|open|fetch|get|display|pull up|bring up|go to|view|structure)\s+(?:the\s+)?(?:structure\s+|protein\s+|gene\s+|target\s+|pdb\s+|entry\s+)?(.+)$/);
  if (load) { const [intent, slots] = targetSlots(load[1], vocabulary); return out(intent, slots); }

  // A bare vocabulary word ("SOD1") is taken as a request to load it.
  const bare = fuzzyVocab(t, vocabulary, 0.85);
  if (bare && t.split(' ').length <= 2) return out('load_target', { query: bare.word, heard: t, score: +bare.score.toFixed(2) });
  if (/^[0-9][a-z0-9]{3}$/.test(t)) return out('load_pdb', { id: t.toUpperCase() });
  return out('unknown');
}

export class VoiceControl extends EventTarget {
  constructor({ onCommand, onPartial, onState, lang = 'en-US' } = {}) {
    super();
    Object.assign(this, { onCommand, onPartial, onState, lang });
    this.vocabulary = [];
    Object.assign(this, { _wake: null, _armedUntil: 0, _wanted: false, _listening: false, _fails: 0, _mutedUntil: 0 });
  }
  static get supported() {
    return typeof window !== 'undefined' && !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  }
  get listening() { return this._listening; }
  setWakeWord(word) { this._wake = word ? normalise(word) : null; this._armedUntil = 0; }
  addVocabulary(words) {
    for (const w of [].concat(words || [])) if (typeof w === 'string' && w && !this.vocabulary.includes(w)) this.vocabulary.push(w);
  }
  _setState(state, detail) {
    this.state = state;
    if (this.onState) this.onState(state, detail);
    this.dispatchEvent(new CustomEvent('state', { detail: { state, detail } }));
  }
  start() {
    if (!VoiceControl.supported) { this._setState('unsupported'); return false; }
    this._wanted = true;
    if (!this._rec) this._rec = this._build();
    this._begin();
    return true;
  }
  stop() {
    this._wanted = false;
    clearTimeout(this._timer);
    try { this._rec && this._rec.abort(); } catch { /* already stopped */ }
    this._listening = false;
    this._setState('idle');
  }
  _begin() { this._startedAt = Date.now(); try { this._rec.start(); } catch { /* InvalidStateError: already running */ } }

  _build() {
    const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    Object.assign(rec, { continuous: true, interimResults: true, maxAlternatives: 3, lang: this.lang });
    rec.onstart = () => { this._listening = true; this._setState('listening'); };
    rec.onresult = (e) => {
      this._fails = 0;
      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) this._final(Array.from(e.results[i]));
        else interim += e.results[i][0].transcript;
      }
      if (interim && Date.now() > this._mutedUntil && this.onPartial) this.onPartial(interim.trim());
    };
    rec.onerror = (e) => {
      if (e.error === 'not-allowed' || e.error === 'service-not-allowed') { this._wanted = false; this._setState('denied', e.error); }
      else if (e.error !== 'no-speech' && e.error !== 'aborted') this._setState('error', e.error);
    };
    // Chrome ends "continuous" sessions silently (silence timeouts, tab switches, network blips).
    // Restart straight away after a normal session; back off only when sessions die almost at once.
    rec.onend = () => {
      this._listening = false;
      if (!this._wanted) return this._setState('idle');
      const quick = Date.now() - this._startedAt < 1000;
      this._fails = quick ? this._fails + 1 : 0;
      const delay = quick ? Math.min(250 * 2 ** this._fails, 10000) : 100;
      this._setState('restarting', { delay });
      clearTimeout(this._timer);
      this._timer = setTimeout(() => this._wanted && this._begin(), delay);
    };
    return rec;
  }

  // Returns the text after the wake word, '' if only the wake word was said, or null if it was absent.
  _afterWake(text) {
    const words = normalise(text).split(' ');
    const wake = this._wake.split(' ');
    for (let i = 0; i + wake.length <= words.length; i++) if (similarity(words.slice(i, i + wake.length).join(''), wake.join('')) >= 0.75) return words.slice(i + wake.length).join(' ');
    return null;
  }

  _final(alternatives) {
    if (Date.now() < this._mutedUntil) return; // ignore our own voice coming back through the mic
    let candidates = alternatives.map((a) => ({ text: a.transcript.trim(), conf: a.confidence }));
    if (this._wake) {
      const woken = candidates.map((c) => ({ ...c, text: this._afterWake(c.text) })).filter((c) => c.text !== null);
      if (woken.length) {
        if (!woken.some((c) => c.text)) { this._armedUntil = Date.now() + 8000; return this._setState('armed'); }
        candidates = woken.filter((c) => c.text);
      } else if (Date.now() > this._armedUntil) return;
      this._armedUntil = 0;
    }
    let chosen = null;
    for (const c of candidates) {
      const parsed = parseCommand(c.text, this.vocabulary);
      // A confidence of 0 means the browser did not report one (Safari, some Android builds).
      const low = c.conf > 0 && c.conf < 0.4;
      if (low && !fuzzyVocab(normalise(c.text), this.vocabulary)) continue;
      parsed.confidence = c.conf || null;
      if (!chosen || (chosen.intent === 'unknown' && parsed.intent !== 'unknown')) chosen = parsed;
      if (chosen.intent !== 'unknown') break;
    }
    if (!chosen) return;
    if (this.onCommand) this.onCommand(chosen);
    this.dispatchEvent(new CustomEvent('command', { detail: chosen }));
  }
  speak(text, { interrupt = true, rate = 1.05 } = {}) {
    const synth = typeof window !== 'undefined' && window.speechSynthesis;
    if (!synth || !window.SpeechSynthesisUtterance || !text) return Promise.resolve(false);
    if (interrupt) synth.cancel();
    return new Promise((resolve) => {
      const u = new window.SpeechSynthesisUtterance(String(text));
      Object.assign(u, { rate, lang: this.lang });
      this._utterance = u; // Chrome can garbage-collect an unreferenced utterance and never fire 'end'
      const guard = Math.max(4000, String(text).length * 120) / rate;
      this._mutedUntil = Date.now() + guard;
      let settled = false;
      const done = (ok) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        this._mutedUntil = Date.now() + 400; // let the speakers fall quiet before trusting the mic again
        resolve(ok);
      };
      const timer = setTimeout(() => done(false), guard + 2000); // some engines never fire 'end'
      u.onend = () => done(true);
      u.onerror = () => done(false);
      synth.speak(u);
    });
  }
}
