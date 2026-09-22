// The workspace as a set of callable tools, plus the console that drives them.
//
// Everything a researcher can do from the panels is also a named tool with a typed schema. That gives
// three ways in: type a sentence in the command bar, say it out loud, or call it from outside over the
// server's command channel (see server/mcp_server.py). The schema is the single source of truth, so a
// new tool appears in all three at once.
import { parseCommand, INTENTS } from './voice.js';
import { scan, plain, note, tierInfo, DOCK_TIER, SCORE_UNIT } from './provenance.js';

// Stamped on every result that carries a dock score, so an external agent reading the JSON sees it too.
const DOCK_PROVENANCE = `ESTIMATE: ${tierInfo(DOCK_TIER).note}`;

// ---------------------------------------------------------------- registry
// `app` is supplied by main.js: the bound functions and state getters the tools act on.
export function buildTools(app) {
  const t = (name, description, parameters, run, opts = {}) => ({ name, description, parameters, run, ...opts });
  const S = () => app.state;

  return [
    t('load_target', 'Load a curated target by gene symbol, or any gene by name. Uses the AlphaFold model when there is no preferred experimental structure.',
      { type: 'object', properties: { query: { type: 'string', description: 'gene symbol such as SOD1, LRRK2, BCL2L1' } }, required: ['query'] },
      async ({ query }) => {
        const hit = app.findTarget(query);
        if (hit) { await app.openTarget(hit); return { loaded: hit.symbol, source: 'curated target', structure: S().protein?.name }; }
        const genes = await app.searchGene(query);
        if (!genes.length) throw new Error(`no target matched "${query}"`);
        await app.loadAlphaFold(genes[0].uniprot, { symbol: genes[0].symbol });
        return { loaded: genes[0].symbol, uniprot: genes[0].uniprot, source: 'UniProt + AlphaFold' };
      }),

    t('load_structure', 'Load an experimental structure from the Protein Data Bank by its four-character entry id.',
      { type: 'object', properties: { id: { type: 'string', description: 'PDB id such as 2YXJ' } }, required: ['id'] },
      async ({ id }) => { await app.loadPdb(id); return { loaded: id.toUpperCase(), atoms: S().protein?.n, ligands: S().protein?.ligands.length }; }),

    t('find_pockets', 'Detect and rank binding pockets on the loaded structure by volume and how buried they are.',
      { type: 'object', properties: {} },
      async () => { await app.doPockets(); return { pockets: S().pockets.map((p, i) => ({ rank: i + 1, volume: Math.round(p.volume), buriedness: +p.buriedness.toFixed(2), residues: p.label })) }; }),

    t('load_compound', 'Put a molecule in the binding site, given a SMILES string, a compound id from the library, or a drug name looked up in PubChem.',
      { type: 'object', properties: { smiles: { type: 'string' }, id: { type: 'string' }, name: { type: 'string' } } },
      async ({ smiles, id, name }) => {
        if (id) { const e = app.findCompound(id); if (!e) throw new Error(`no compound ${id} in the library`); await app.loadCompound(e); return { ligand: e.agiId, smiles: e.canonical }; }
        if (name) { await app.loadDrugByName(name); return { ligand: S().ligand?.name }; }
        if (smiles) { await app.loadSmiles(smiles); return { ligand: S().ligand?.name, atoms: S().ligand?.n }; }
        throw new Error('give a smiles, an id, or a name');
      }),

    t('extract_ligand', 'Lift a ligand out of the loaded crystal structure so it can be re-docked or simulated.',
      { type: 'object', properties: { resName: { type: 'string', description: 'three-letter chemical component id; omit for the largest' } } },
      async ({ resName }) => {
        const ligs = S().protein?.ligands || [];
        const lig = resName ? ligs.find((l) => l.resName.toUpperCase() === resName.toUpperCase())
          : ligs.slice().sort((a, b) => b.atoms.length - a.atoms.length)[0];
        if (!lig) throw new Error('this structure has no bound ligand');
        await app.extractCocrystal(lig);
        return { ligand: lig.resName, atoms: lig.atoms.length, score: app.round(S().lastScore?.total), provenance: DOCK_PROVENANCE };
      }),

    t('dock', 'Dock the current ligand into the active site with a flexible Monte Carlo search, and report the ranked poses.',
      { type: 'object', properties: { runs: { type: 'integer', minimum: 1, maximum: 24 }, steps: { type: 'integer', minimum: 200, maximum: 8000 } } },
      async ({ runs, steps } = {}) => {
        await app.doDock({ runs, steps });
        const sc = S().lastScore;
        return { best: app.round(S().poses[0]?.score), poses: S().poses.length, hbonds: sc?.hbonds.length,
          contacts: sc?.contactResidues.length, units: `${SCORE_UNIT}, lower is better; not kcal/mol`, provenance: DOCK_PROVENANCE };
      }, { slow: true }),

    t('screen_library', 'Dock every compound in the library against the active site and rank them.',
      { type: 'object', properties: { limit: { type: 'integer', minimum: 1, maximum: 500 }, runs: { type: 'integer' }, steps: { type: 'integer' } } },
      async (args = {}) => {
        await app.screenLibrary(args);
        const ranked = app.rankedLibrary().slice(0, 10);
        return { screened: ranked.length, ranking: ranked.map((c) => ({ id: c.agiId, score: c.dockScore })),
          units: `${SCORE_UNIT}, lower is better; not kcal/mol`, provenance: DOCK_PROVENANCE };
      }, { slow: true }),

    t('simulate', 'Start or stop the interactive molecular dynamics in the viewport.',
      { type: 'object', properties: { action: { type: 'string', enum: ['start', 'stop'] }, rigidProtein: { type: 'boolean' } } },
      async ({ action = 'start', rigidProtein }) => {
        if (action === 'stop') { app.stopMD(); return { running: false }; }
        app.startMD({ rigidProtein });
        return { running: true, temperature: app.state.md?.T, note: 'coarse interactive model; use run_backend_md for all-atom' };
      }),

    t('run_backend_md', 'Run all-atom molecular dynamics on the local server with OpenMM and play the trajectory back.',
      { type: 'object', properties: { steps: { type: 'integer' }, temperature: { type: 'number' } } },
      async (args) => app.runBackendMD(args), { slow: true }),

    t('gather_evidence', 'Collect target evidence from the public databases: domains, pathways, interaction partners, expression, population constraint, trials and literature.',
      { type: 'object', properties: {} },
      async () => app.gatherEvidence(), { slow: true }),

    t('similar_folds', 'Search the current fold against the AlphaFold database and the whole Protein Data Bank with Foldseek.',
      { type: 'object', properties: {} }, async () => app.findSimilarFolds(), { slow: true }),

    t('known_drugs', 'List clinical drugs and candidates for the loaded target, with mechanism and trial stage.',
      { type: 'object', properties: {} }, async () => app.knownDrugs()),

    t('set_view', 'Change how the structure is drawn or coloured, or re-frame the camera.',
      { type: 'object', properties: {
        representation: { type: 'string', enum: ['cartoon', 'cartoon+pocket', 'ballstick', 'sticks', 'spacefill', 'lines'] },
        colour: { type: 'string', enum: ['element', 'chain', 'ss', 'plddt', 'rainbow', 'hydrophobic', 'missense', 'carbon-accent'] },
        reset: { type: 'boolean' } } },
      async (args) => app.setView(args)),

    t('analyse_pose', 'Classify every contact the bound ligand makes, residue by residue: hydrogen bonds, salt bridges, aromatic stacking, halogen bonds and hydrophobic contacts. Also reports whether the pocket sits where mutations are poorly tolerated.',
      { type: 'object', properties: {} }, async () => app.analysePose()),

    t('selectivity', 'Dock the current compound against related targets and compare the scores, as a read on selectivity.',
      { type: 'object', properties: { limit: { type: 'integer', minimum: 1, maximum: 8 } } },
      async (args) => app.selectivity(args), { slow: true }),

    t('compound_series', 'Group the compound library into structural series by fingerprint similarity, with the best scoring member of each.',
      { type: 'object', properties: { cut: { type: 'number', minimum: 0.3, maximum: 0.95 } } },
      async (args) => app.series(args)),

    t('measure', 'Report the distance between two selected atoms, or the angle across three.',
      { type: 'object', properties: {} }, async () => app.measure()),

    t('describe_scene', 'Describe what is currently loaded and the latest result, in one short paragraph. Use this to answer "what am I looking at".',
      { type: 'object', properties: {} }, async () => app.describe()),

    t('library_search', 'Search the compound library by text, substructure SMARTS, or property filters.',
      { type: 'object', properties: { text: { type: 'string' }, smarts: { type: 'string' },
        maxMw: { type: 'number' }, cnsOnly: { type: 'boolean' } } },
      async (args) => app.librarySearch(args)),

    t('next_compound', 'Load the next compound in the library.', { type: 'object', properties: {} },
      async () => app.cycleCompound(1)),

    t('prev_compound', 'Load the previous compound in the library.', { type: 'object', properties: {} },
      async () => app.cycleCompound(-1)),

    t('ledger', 'Verify or export the provenance hash chain.',
      { type: 'object', properties: { action: { type: 'string', enum: ['verify', 'export', 'list'] } } },
      async ({ action = 'verify' }) => app.ledger(action)),
  ];
}

// JSON-Schema view of the registry, for an LLM, an MCP server, or the help text.
export function toolSchemas(tools) {
  return tools.map(({ name, description, parameters }) => ({ name, description, parameters }));
}

// ---------------------------------------------------------------- intent -> tool
// The spoken/typed grammar in voice.js produces intents; this maps them onto tool calls.
// The spoken grammar uses friendly words; the renderer uses its own ids.
const COLOUR_WORDS = { confidence: 'plddt', plddt: 'plddt', missense: 'missense', chain: 'chain',
  hydrophobicity: 'hydrophobic', hydrophobic: 'hydrophobic', secondary_structure: 'ss', ss: 'ss',
  rainbow: 'rainbow', element: 'element' };
const REP_WORDS = { cartoon: 'cartoon+pocket', ribbon: 'cartoon+pocket', spacefill: 'spacefill',
  sticks: 'sticks', ball_and_stick: 'ballstick', ballstick: 'ballstick', surface: 'spacefill', lines: 'lines' };

const INTENT_TO_TOOL = {
  load_target: (s) => ['load_target', { query: s.query }],
  load_pdb: (s) => ['load_structure', { id: s.id }],
  dock: () => ['dock', {}],
  find_pockets: () => ['find_pockets', {}],
  screen: (s) => ['screen_library', s.limit ? { limit: s.limit } : {}],
  start_md: () => ['simulate', { action: 'start' }],
  stop_md: () => ['simulate', { action: 'stop' }],
  colour_by: (s) => ['set_view', { colour: COLOUR_WORDS[s.mode] || s.mode }],
  representation: (s) => ['set_view', { representation: REP_WORDS[s.rep] || s.rep }],
  reset_view: () => ['set_view', { reset: true }],
  evidence: () => ['gather_evidence', {}],
  explain: () => ['describe_scene', {}],
  measure: () => ['measure', {}],
  next_compound: () => ['next_compound', {}],
  prev_compound: () => ['prev_compound', {}],
  search: (s) => ['load_target', { query: s.query }],
};

export class AgentRuntime extends EventTarget {
  constructor(tools, { onLog } = {}) {
    super();
    this.tools = tools;
    this.byName = new Map(tools.map((x) => [x.name, x]));
    this.onLog = onLog || (() => {});
    this.history = [];
  }

  vocabulary() { return this.extraVocab || []; }
  setVocabulary(words) { this.extraVocab = words; }

  async call(name, args = {}, { source = 'api' } = {}) {
    const tool = this.byName.get(name);
    if (!tool) throw new Error(`no tool called "${name}"`);
    const started = Date.now();
    this.dispatchEvent(new CustomEvent('start', { detail: { name, args, source } }));
    try {
      const result = await tool.run(args || {});
      const entry = { name, args, result, ms: Date.now() - started, source, ok: true };
      this.history.push(entry);
      this.dispatchEvent(new CustomEvent('result', { detail: entry }));
      return result;
    } catch (e) {
      const entry = { name, args, error: e.message, ms: Date.now() - started, source, ok: false };
      this.history.push(entry);
      this.dispatchEvent(new CustomEvent('result', { detail: entry }));
      throw e;
    }
  }

  // Natural language in, tool call out. Local and deterministic; no model needed.
  async run(text, { source = 'console' } = {}) {
    const parsed = parseCommand(text, this.vocabulary());
    const map = INTENT_TO_TOOL[parsed.intent];
    if (!map) {
      const guess = this.tools.find((x) => x.name.replace(/_/g, ' ') === text.trim().toLowerCase());
      if (guess) return { tool: guess.name, result: await this.call(guess.name, {}, { source }) };
      return { tool: null, parsed, help: 'Say or type: load SOD1 · find pockets · dock · screen the library · start dynamics · colour by missense · gather evidence · explain this' };
    }
    const [name, args] = map(parsed.slots || {});
    return { tool: name, parsed, result: await this.call(name, args, { source }) };
  }

  // One line a person (or a speech synthesiser) can read back.
  static summarise(name, result) {
    if (result == null) return `${name.replace(/_/g, ' ')} done`;
    switch (name) {
      case 'load_target': return `Loaded ${result.loaded}${result.uniprot ? `, ${result.uniprot}` : ''}.`;
      case 'load_structure': return `Loaded ${result.loaded}: ${result.atoms} atoms, ${result.ligands} bound ligands.`;
      case 'find_pockets': return `Found ${result.pockets.length} pockets. The largest is ${result.pockets[0]?.volume} cubic angstroms.`;
      // Spoken aloud too, so the qualifier is in words, not only in a badge.
      case 'dock': return `Best pose has an estimated, unvalidated score of ${plain(result.best, scan(result))} with ${result.hbonds} hydrogen bonds.`;
      case 'screen_library': return `Screened ${result.screened}. Best is ${result.ranking[0]?.id} at an estimated ${plain(result.ranking[0]?.score, scan(result))}.`;
      case 'simulate': return result.running ? 'Dynamics running.' : 'Dynamics stopped.';
      case 'describe_scene': return result.text || '';
      case 'measure': return result.text || 'Nothing selected.';
      case 'ledger': return result.text || `${result.records} records, chain ${result.ok ? 'verified' : 'broken'}.`;
      default: return typeof result === 'string' ? result : `${name.replace(/_/g, ' ')} done.`;
    }
  }
}

// ---------------------------------------------------------------- console UI
export class AgentConsole {
  constructor(root, runtime, { onSpeak } = {}) {
    this.root = root; this.rt = runtime; this.onSpeak = onSpeak;
    root.innerHTML = `
      <div class="agent-log" id="agentLog"></div>
      <form class="agent-input" id="agentForm">
        <input id="agentText" placeholder="Ask or instruct: load LRRK2, find pockets, dock, explain this" autocomplete="off">
        <button type="submit" class="primary">Run</button>
        <button type="button" id="agentMic" title="Voice control">🎙</button>
      </form>
      <div class="agent-hint" id="agentHint"></div>`;
    this.log = root.querySelector('#agentLog');
    this.input = root.querySelector('#agentText');
    root.querySelector('#agentForm').addEventListener('submit', (e) => { e.preventDefault(); this.submit(this.input.value); });
    this.say('system', 'Type an instruction, or press the microphone. Everything here is also callable by an external agent.');
  }

  get micButton() { return this.root.querySelector('#agentMic'); }

  say(who, text, cls = '') {
    const d = document.createElement('div');
    d.className = `agent-msg ${who} ${cls}`;
    d.innerHTML = text;
    this.log.appendChild(d);
    this.log.scrollTop = this.log.scrollHeight;
    return d;
  }

  async submit(text, source = 'console') {
    text = (text || '').trim();
    if (!text) return;
    this.input.value = '';
    this.say('user', text);
    const pending = this.say('agent', '<span class="dots">working…</span>');
    try {
      const out = await this.rt.run(text, { source });
      if (!out.tool) { pending.innerHTML = out.help; return; }
      const line = AgentRuntime.summarise(out.tool, out.result);
      pending.innerHTML = `<b>${out.tool.replace(/_/g, ' ')}</b> — ${escapeHtml(line)}${note(scan(out.result))}`
        + (out.result && typeof out.result === 'object' ? `<pre>${escapeHtml(JSON.stringify(out.result, null, 1)).slice(0, 700)}</pre>` : '');
      this.onSpeak && this.onSpeak(line);
    } catch (e) {
      pending.innerHTML = `<span class="bad">${escapeHtml(e.message)}</span>`;
      this.onSpeak && this.onSpeak(`That failed: ${e.message}`);
    }
  }
}

function escapeHtml(s) { return String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])); }

// ---------------------------------------------------------------- remote control channel
// Lets an external agent (see server/mcp_server.py) call the same tools in a live browser session.
export function connectCommandChannel(runtime, { onStatus } = {}) {
  let es;
  const connect = () => {
    es = new EventSource('/api/command/events');
    es.onopen = () => onStatus && onStatus('connected');
    es.onerror = () => { onStatus && onStatus('disconnected'); es.close(); setTimeout(connect, 4000); };
    es.onmessage = async (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch { return; }
      if (!msg.id || !msg.tool) return;
      try {
        const result = await runtime.call(msg.tool, msg.args || {}, { source: 'remote' });
        await post(msg.id, { ok: true, result });
      } catch (e) {
        await post(msg.id, { ok: false, error: e.message });
      }
    };
  };
  const post = (id, body) => fetch('/api/command/result', { method: 'POST', body: JSON.stringify({ id, ...body }) }).catch(() => {});
  connect();
  return { close: () => es && es.close() };
}

export { INTENTS };
