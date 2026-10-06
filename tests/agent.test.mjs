// Offline checks for js/agent.js: the registry, the schemas it publishes, and the seam between the
// spoken grammar and the renderer's own vocabulary.
//
// The app object is a stub that records calls, so every tool runs without a browser, a structure or a
// network. That seam is where a hands-free session breaks quietly: voice.js speaks in friendly words
// ("confidence", "ball and stick") and the renderer answers to different ids ("plddt", "ballstick").
//
//   node --test tests/agent.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { buildTools, toolSchemas, AgentRuntime } from '../js/agent.js';

// A stub standing in for the live workspace. Each method records that it was called and returns
// something shaped like the real thing.
function stubApp(overrides = {}) {
  const calls = [];
  const record = (name) => (...args) => { calls.push([name, ...args]); return undefined; };
  const app = {
    calls,
    state: {
      protein: { name: 'SOD1 (AlphaFold)', n: 1118, ligands: [{ resName: 'LIG', atoms: [1, 2, 3, 4, 5] }],
        residues: [{ polymer: true }, { polymer: true }] },
      ligand: { name: 'N3C', n: 56 },
      target: { symbol: 'SOD1', program: 'ALS', disease: 'familial ALS' },
      pockets: [{ volume: 291.4, buriedness: 0.79, label: 'LEU127 ASN87' }],
      poses: [{ score: -9.97 }, { score: -8.1 }],
      lastScore: { total: -9.96, hbonds: [{}], contactResidues: [1, 2, 3] },
      library: { compounds: [{ agiId: 'REF-001', dockScore: -6.1 }] },
      md: { T: 300 },
      ledger: { records: [{}, {}], head: 'abc123def456', verify: async () => ({ ok: true, length: 2 }) },
      proteinView: { style: { rep: 'cartoon+pocket', color: 'chain' } },
    },
    round: (v) => (v == null || Number.isNaN(v) ? null : +(+v).toFixed(2)),
    findTarget: (q) => (String(q).toUpperCase() === 'SOD1' ? { symbol: 'SOD1' } : null),
    findCompound: (id) => (String(id).toUpperCase() === 'REF-001' ? { agiId: 'REF-001', canonical: 'CCO' } : null),
    searchGene: async () => [],
    openTarget: async (...a) => { calls.push(['openTarget', ...a]); },
    loadPdb: async (...a) => { calls.push(['loadPdb', ...a]); },
    loadAlphaFold: async (...a) => { calls.push(['loadAlphaFold', ...a]); },
    loadCompound: async (...a) => { calls.push(['loadCompound', ...a]); },
    loadDrugByName: async (...a) => { calls.push(['loadDrugByName', ...a]); },
    loadSmiles: async (...a) => { calls.push(['loadSmiles', ...a]); },
    extractCocrystal: async (...a) => { calls.push(['extractCocrystal', ...a]); },
    doPockets: async () => { calls.push(['doPockets']); },
    doDock: async (...a) => { calls.push(['doDock', ...a]); },
    screenLibrary: async (...a) => { calls.push(['screenLibrary', ...a]); },
    rankedLibrary: () => [{ agiId: 'REF-001', dockScore: -6.1 }],
    startMD: record('startMD'),
    stopMD: record('stopMD'),
    runBackendMD: async (...a) => { calls.push(['runBackendMD', ...a]); return { started: true }; },
    gatherEvidence: async () => { calls.push(['gatherEvidence']); return { trials: 1004 }; },
    findSimilarFolds: async () => { calls.push(['findSimilarFolds']); return { hits: 2 }; },
    knownDrugs: () => ({ target: 'SOD1', drugs: [] }),
    setView: (...a) => { calls.push(['setView', ...a]); return { representation: 'cartoon+pocket', colour: 'plddt' }; },
    measure: () => ({ text: 'nothing selected' }),
    librarySearch: async (...a) => { calls.push(['librarySearch', ...a]); return { matches: 0, compounds: [] }; },
    ledger: async (...a) => { calls.push(['ledger', ...a]); return { ok: true, records: 2, text: 'Chain verified' }; },
    describe: () => ({ text: 'SOD1 (AlphaFold), 2 residues.' }),
    analysePose: () => ({ summary: 'one hydrogen bond', counts: { hbond: 1 }, residues: [] }),
    selectivity: async (...a) => { calls.push(['selectivity', ...a]); return { compared: [] }; },
    series: (...a) => { calls.push(['series', ...a]); return { series: 1, groups: [] }; },
    cycleCompound: (...a) => { calls.push(['cycleCompound', ...a]); return { ligand: 'REF-002' }; },
    ...overrides,
  };
  return app;
}

const toolsOf = (app) => new Map(buildTools(app).map((t) => [t.name, t]));

test('every tool publishes a name, a description and a valid JSON-Schema object', () => {
  const tools = buildTools(stubApp());
  assert.ok(tools.length >= 15, `only ${tools.length} tools registered`);
  const names = new Set();
  for (const t of tools) {
    assert.match(t.name, /^[a-z][a-z0-9_]*$/, `${t.name} is not a snake_case identifier`);
    assert.ok(!names.has(t.name), `${t.name} is registered twice`);
    names.add(t.name);
    assert.ok(t.description && t.description.length > 20, `${t.name} needs a usable description`);
    assert.equal(t.parameters.type, 'object', `${t.name} parameters must be an object schema`);
    assert.ok(t.parameters.properties, `${t.name} has no properties map`);
    for (const req of t.parameters.required || []) {
      assert.ok(req in t.parameters.properties, `${t.name} requires "${req}" but never declares it`);
    }
    assert.equal(typeof t.run, 'function', `${t.name} has no implementation`);
  }
});

test('the published schema carries exactly what an MCP client needs, and no implementation', () => {
  const tools = buildTools(stubApp());
  const schema = toolSchemas(tools);
  assert.equal(schema.length, tools.length);
  for (const entry of schema) {
    assert.deepEqual(Object.keys(entry).sort(), ['description', 'name', 'parameters']);
    assert.equal(typeof entry.run, 'undefined', 'the schema must not leak the function');
  }
});

test('a spoken colour word reaches the renderer id, not the word itself', async () => {
  const app = stubApp();
  const rt = new AgentRuntime(buildTools(app));
  // "confidence" is what a person says; "plddt" is what the renderer answers to.
  await rt.run('colour by confidence');
  const call = app.calls.find((c) => c[0] === 'setView');
  assert.ok(call, 'setView was never reached');
  assert.equal(call[1].colour, 'plddt');
});

test('a spoken representation reaches the renderer id', async () => {
  const app = stubApp();
  const rt = new AgentRuntime(buildTools(app));
  await rt.run('show cartoon');
  const call = app.calls.find((c) => c[0] === 'setView');
  assert.equal(call[1].representation, 'cartoon+pocket');
});

test('spoken intents route to the tool a researcher meant', async () => {
  const cases = [
    ['dock it', 'doDock'],
    ['find pockets', 'doPockets'],
    ['gather evidence', 'gatherEvidence'],
    ['screen the library', 'screenLibrary'],
    ['start dynamics', 'startMD'],
    ['stop the simulation', 'stopMD'],
    ['next compound', 'cycleCompound'],
  ];
  for (const [said, expected] of cases) {
    const app = stubApp();
    const rt = new AgentRuntime(buildTools(app));
    await rt.run(said);
    assert.ok(app.calls.some((c) => c[0] === expected), `"${said}" should reach ${expected}`);
  }
});

test('an unrecognised sentence offers help instead of guessing a tool', async () => {
  const app = stubApp();
  const rt = new AgentRuntime(buildTools(app));
  const out = await rt.run('what is the weather in london');
  assert.equal(out.tool, null);
  assert.match(out.help, /load/i);
  assert.equal(app.calls.length, 0, 'nothing may be executed on an unrecognised sentence');
});

test('calling an unknown tool by name is refused', async () => {
  const rt = new AgentRuntime(buildTools(stubApp()));
  await assert.rejects(() => rt.call('delete_everything', {}), /no tool called/);
});

test('history records both outcomes, and a failure is not silently swallowed', async () => {
  const app = stubApp({ doPockets: async () => { throw new Error('no structure loaded'); } });
  const rt = new AgentRuntime(buildTools(app));
  await rt.call('describe_scene', {});
  await assert.rejects(() => rt.call('find_pockets', {}), /no structure loaded/);
  assert.equal(rt.history.length, 2);
  assert.equal(rt.history[0].ok, true);
  assert.equal(rt.history[1].ok, false);
  assert.match(rt.history[1].error, /no structure loaded/);
  assert.ok(typeof rt.history[0].ms === 'number');
});

test('events fire for both a success and a failure, carrying the source', async () => {
  const app = stubApp({ doDock: async () => { throw new Error('nope'); } });
  const rt = new AgentRuntime(buildTools(app));
  const seen = [];
  rt.addEventListener('start', (e) => seen.push(['start', e.detail.name, e.detail.source]));
  rt.addEventListener('result', (e) => seen.push(['result', e.detail.name, e.detail.ok]));
  await rt.call('describe_scene', {}, { source: 'voice' });
  await rt.call('dock', {}, { source: 'remote' }).catch(() => {});
  assert.deepEqual(seen, [
    ['start', 'describe_scene', 'voice'], ['result', 'describe_scene', true],
    ['start', 'dock', 'remote'], ['result', 'dock', false],
  ]);
});

test('load_target falls back to a gene search when the symbol is not curated', async () => {
  const app = stubApp({
    findTarget: () => null,
    searchGene: async () => [{ uniprot: 'Q5S007', symbol: 'LRRK2' }],
  });
  const rt = new AgentRuntime(buildTools(app));
  const out = await rt.call('load_target', { query: 'LRRK2' });
  assert.equal(out.loaded, 'LRRK2');
  assert.equal(out.uniprot, 'Q5S007');
  assert.ok(app.calls.some((c) => c[0] === 'loadAlphaFold'));
});

test('load_target says so plainly when nothing matches', async () => {
  const app = stubApp({ findTarget: () => null, searchGene: async () => [] });
  const rt = new AgentRuntime(buildTools(app));
  await assert.rejects(() => rt.call('load_target', { query: 'zzzz' }), /no target matched/);
});

test('load_compound needs one of smiles, id or name and says which', async () => {
  const rt = new AgentRuntime(buildTools(stubApp()));
  await assert.rejects(() => rt.call('load_compound', {}), /smiles.*id.*name/);
  const byId = await rt.call('load_compound', { id: 'REF-001' });
  assert.equal(byId.ligand, 'REF-001');
  await assert.rejects(() => rt.call('load_compound', { id: 'NOPE-999' }), /no compound/);
});

test('extract_ligand refuses a structure with nothing bound', async () => {
  const app = stubApp();
  app.state.protein.ligands = [];
  const rt = new AgentRuntime(buildTools(app));
  await assert.rejects(() => rt.call('extract_ligand', {}), /no bound ligand/);
});

test('dock reports the units and that the score is approximate', async () => {
  const rt = new AgentRuntime(buildTools(stubApp()));
  const out = await rt.call('dock', {});
  assert.equal(out.best, -9.97);
  assert.equal(out.poses, 2);
  // The wording has been tightened over time ("approximate" became "unitless ... not kcal/mol"); what
  // matters is that the field disclaims exactness rather than which phrase does it.
  assert.match(out.units, /approximate|unitless|not kcal/i, 'a score must never be presented as exact');
});

test('simulate starts and stops, and flags the model as coarse', async () => {
  const app = stubApp();
  const rt = new AgentRuntime(buildTools(app));
  const started = await rt.call('simulate', { action: 'start' });
  assert.equal(started.running, true);
  assert.match(started.note, /coarse/i);
  const stopped = await rt.call('simulate', { action: 'stop' });
  assert.equal(stopped.running, false);
  assert.ok(app.calls.some((c) => c[0] === 'stopMD'));
});

test('summarise reads back something a person or a voice can use', () => {
  assert.match(AgentRuntime.summarise('dock', { best: -9.9, hbonds: 2 }), /-9\.9/);
  assert.match(AgentRuntime.summarise('find_pockets', { pockets: [{ volume: 291 }] }), /291/);
  assert.equal(AgentRuntime.summarise('describe_scene', { text: 'A protein.' }), 'A protein.');
  assert.ok(AgentRuntime.summarise('anything_else', null).length > 0, 'never returns an empty line');
});

test('the metered tools are the ones that actually cost compute', () => {
  const tools = toolsOf(stubApp());
  for (const name of ['dock', 'screen_library', 'run_backend_md', 'selectivity']) {
    assert.equal(tools.get(name)?.slow, true, `${name} should be marked slow`);
  }
  assert.notEqual(tools.get('describe_scene')?.slow, true, 'describing the scene is not expensive');
});
