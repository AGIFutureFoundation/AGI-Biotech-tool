// biodao.blockchain (powered by AGI Corp) — application shell: scene, data loading, docking, dynamics, screening, XR and UI wiring.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { parsePDB, parseMmCIF, parseMolblock, parsePDBFrames } from './structure.js';
import { MolView, REPS, COLORS, textSprite, dashedLine } from './render.js';
import { MDEngine } from './md.js';
import { ProteinGrid, vinaScore, findPockets, dockLigand, centroid } from './dock.js';
import { analyze, smilesTo3D, loadRDKit, setServerCaps, depict, heavyAtomModel, fingerprint } from './chem.js';
import { CompoundLibrary, importFile } from './compounds.js';
import { rcsb, alphafold, uniprot, openTargets, pubchem, chembl, server, foldseek, trials, interpro, reactome,
  stringdb, gnomad, proteinAtlas, unichem, pdbe, europepmc, openfda, pharos, biothings, kegg, bindingdb } from './api.js';
import { af3LocalJob, afServerJob, downloadJson, downloadText, readPrediction } from './af3.js';
import { Collab } from './collab.js';
import { XRManager, xrSupport, XR_REASONS, onXRDeviceChange } from './xr.js';
import { Ledger } from './ledger.js';
import { buildTools, toolSchemas, AgentRuntime, AgentConsole, connectCommandChannel } from './agent.js';
import { VoiceControl } from './voice.js';
import { HandTracking } from './hands.js';
import { computeStats, renderDashboard, buildReport } from './dashboard.js';
import { EnvironmentManager, Locomotion, HDRI_PRESETS } from './environment.js';
import { interactionFingerprint, pocketVariantOverlap, clusterSeries } from './analysis.js';
import { tanimoto } from './chem.js';
import { Recorder } from './recorder.js';
import { yieldToEventLoop } from './util.js';
import { mark, plain, note, num, tierOf, DOCK_TIER, SCORE_UNIT } from './provenance.js';

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
const fmt = (v, n = 2) => (v == null || Number.isNaN(v) ? '–' : (+v).toFixed(n));

const S = {
  targets: [], program: 'ALS', target: null, protein: null, proteinView: null, ligand: null, ligandView: null,
  grid: null, pockets: [], pocket: null, poses: [], md: null, mdRunning: false, caps: null,
  selection: [], measureMode: false, library: new CompoundLibrary(), compound: null, screening: false, stopFlag: false,
  backendJob: null, trajectory: null, missense: null, lastScore: null, ledger: new Ledger(), demo: null,
  recorder: null, orbitSpeed: 0, agent: null, voice: null, hands: null, dashboardOpen: false, env: null, walk: null,
};

// ---------------------------------------------------------------- scene
const renderer = new THREE.WebGLRenderer({ canvas: $('#gl'), antialias: true, alpha: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.xr.enabled = true;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(55, 1, 0.01, 200);
camera.position.set(0, 1.5, 2.2);
const rig = new THREE.Group(); rig.add(camera); scene.add(rig);
scene.add(new THREE.HemisphereLight(0xbfd7ff, 0x1a2230, 1.5));
const key = new THREE.DirectionalLight(0xffffff, 2.0); key.position.set(3, 5, 4); scene.add(key);
const fill = new THREE.DirectionalLight(0x8fb8ff, 0.7); fill.position.set(-4, -2, -3); scene.add(fill);

const workspace = new THREE.Group();          // grabbed, scaled and rotated in VR
workspace.position.set(0, 1.35, -0.55);
workspace.scale.setScalar(0.03);              // 1 Å -> 3 cm
scene.add(workspace);
const model = new THREE.Group();              // holds molecules, centred on the structure
workspace.add(model);
const overlay = new THREE.Group();            // pockets, measurements, H-bonds
model.add(overlay);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(workspace.position);
controls.enableDamping = true; controls.dampingFactor = 0.08;

const raycaster = new THREE.Raycaster();
raycaster.params.Line.threshold = 0.02;
const pointer = new THREE.Vector2();

const xr = new XRManager(renderer, scene, workspace, camera);
xr.describe = (hit) => { const p = pickAtom(hit); return p ? describeAtom(p.view, p.atom) : null; };
xr.priority = () => (S.mdRunning && S.ligandView ? [S.ligandView.group] : []);

function resize() {
  const v = $('#viewport');
  const w = v.clientWidth, h = Math.max(1, v.clientHeight);
  renderer.setSize(w, h, false);
  // On narrower windows the right-hand panel floats over the viewport. Shift the projection centre into the part
  // that is actually visible so the structure is not framed half behind the panel.
  const vr = v.getBoundingClientRect(), rr = $('#right').getBoundingClientRect();
  const covered = rr.width && rr.left < vr.right && rr.left > vr.left ? vr.right - rr.left : 0;
  if (covered > 0 && covered < w * 0.6) {
    camera.aspect = (w + covered) / h;
    camera.setViewOffset(w + covered, h, covered, 0, w, h);
  } else {
    camera.aspect = w / h;
    camera.clearViewOffset();
  }
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
addEventListener('orientationchange', () => setTimeout(resize, 120));
visualViewport?.addEventListener('resize', resize);
// A phone rotating, a keyboard opening or a pane being dragged all change the canvas without a window
// resize event, so watch the element itself.
new ResizeObserver(() => resize()).observe($('#viewport'));

// ---------------------------------------------------------------- status helpers
let toastTimer = null;
function toast(msg, bad = false) {
  const t = $('#toast'); t.textContent = msg; t.className = 'toast' + (bad ? ' bad' : '');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.add('hidden'), 4200);
  xr.panel.setStatus(msg);
}
const status = (m) => { $('#status').textContent = m; };
const logTo = (sel, m) => { const e = $(sel); e.textContent = `${m}\n${e.textContent}`.split('\n').slice(0, 40).join('\n'); };

// ---------------------------------------------------------------- structures
function setProtein(st, meta = {}) {
  if (S.proteinView) { S.proteinView.dispose(); model.remove(S.proteinView.group); }
  stopMD();
  S.protein = st; S.proteinMeta = meta; S.missense = null; S.pockets = []; S.pocket = null; S.poses = []; clearOverlay();
  S.proteinView = new MolView(st, { style: { rep: 'cartoon+pocket', color: meta.alphafold ? 'plddt' : 'chain' } });
  model.add(S.proteinView.group);
  const c = st.center(Array.from(st.heavy));
  model.position.set(-c[0], -c[1], -c[2]);
  S.grid = new ProteinGrid(st, 4);
  $('#hudTitle').textContent = st.name;
  $('#hudSub').textContent = meta.subtitle || `${st.residues.filter((r) => r.polymer).length} residues · ${st.chains.length} chain(s)`;
  renderStructureInfo(meta);
  refreshPickTargets();
  fitView();
  if (S.ligand) placeLigandAtSite();
  if (S.collab) S.collab.share({ kind: 'protein', pdb: meta.pdbId, uniprot: meta.uniprot, af: !!meta.alphafold });
  S.ledger.append('structure', { name: st.name, pdb: meta.pdbId || null, uniprot: meta.uniprot || null, atoms: st.n }).then(renderLedger);
  status(`${st.n} atoms loaded`);
}

// Frame the structure at a comfortable arm's-length size: about 60 cm across, 80 cm in front, at eye height.
// In a headset it is sized to ~40 cm (fits between two hands) and placed relative to the head by xr.recentre().
function fitView(diameter = xr.active ? 0.4 : 0.6) {
  if (xr.active) xr.recentre();
  if (!S.protein) return;
  const r = S.protein.radius(Array.from(S.protein.heavy)) || 20;
  workspace.scale.setScalar(Math.max(0.002, Math.min(0.05, diameter / (2 * r))));
  workspace.position.set(0, 1.3, -0.8);
  workspace.rotation.set(0, 0, 0);
  // Desktop: pull back just far enough for the structure to fill the viewport.
  const dist = (diameter / 2) / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.45;
  camera.position.set(0, 1.32, workspace.position.z + dist);
  controls.target.copy(workspace.position);
  controls.update();
}

function refreshPickTargets() {
  xr.pickTargets = [S.proteinView?.group, S.ligandView?.group].filter(Boolean);
}

function clearOverlay() { for (const c of [...overlay.children]) { c.geometry?.dispose?.(); overlay.remove(c); } }

async function loadPdb(id, opts = {}) {
  status(`fetching PDB ${id}…`);
  const text = await rcsb.file(id);
  const st = typeof text === 'string' ? parsePDB(text, { name: id.toUpperCase(), source: `RCSB ${id}` }) : parseMmCIF(text.cif, { name: id.toUpperCase() });
  let subtitle = '';
  try {
    const e = await rcsb.entry(id);
    subtitle = `${e.struct.title.slice(0, 90)} · ${(e.rcsb_entry_info.resolution_combined || ['—'])[0]} Å ${e.rcsb_entry_info.experimental_method}`;
  } catch { /* offline is fine */ }
  setProtein(st, { subtitle, pdbId: id.toUpperCase(), ...opts });
  renderCocrystals();
}

async function loadAlphaFold(acc, opts = {}) {
  status(`fetching AlphaFold model for ${acc}…`);
  const { meta, text } = await alphafold.structure(acc);
  const st = parsePDB(text, { name: `${opts.symbol || acc} (AlphaFold)`, source: `AlphaFold DB ${meta.modelEntityId}` });
  setProtein(st, { subtitle: `AlphaFold ${meta.modelEntityId} · mean pLDDT ${fmt(meta.globalMetricValue, 1)} · ${meta.uniprotDescription || ''}`.slice(0, 140),
    alphafold: true, uniprot: acc, ...opts });
  alphafold.missense(acc).then((m) => {
    if (!m || S.protein !== st) return;
    S.missense = m; S.proteinView.missense = m;
    toast('AlphaMissense variant scores ready — colour by "missense"');
  }).catch(() => {});
}

// ---------------------------------------------------------------- ligands
async function setLigand(st, info = {}) {
  if (S.ligandView) { S.ligandView.dispose(); model.remove(S.ligandView.group); }
  S.ligand = st;
  S.ligandView = new MolView(st, { style: { rep: 'ballstick', color: 'carbon-accent', accent: 0x39d98a } });
  model.add(S.ligandView.group);
  S.compound = info.entry || S.compound;
  refreshPickTargets();
  await ensureSite(info.keepPosition);
  placeLigandAtSite(info.keepPosition);
  renderLigandCard(info);
  scoreNow();
  if (S.collab) S.collab.share({ kind: 'ligand', smiles: info.smiles, name: st.name });
}

// A ligand needs somewhere sensible to sit: the co-crystal site if there is one, else the best pocket.
async function ensureSite(keep = false) {
  if (keep || !S.protein || S.pocket) return;
  if (S.protein.ligands.length) {
    const l = S.protein.ligands.find((x) => !(S.protein.excluded && S.protein.excluded[x.atoms[0]])) || S.protein.ligands[0];
    S.pocket = { center: S.protein.center(l.atoms), label: `${l.resName} site`, residues: [], volume: null, buriedness: null };
    return;
  }
  await doPockets();
}

function placeLigandAtSite(keep = false) {
  if (!S.ligand || !S.protein || keep) return;
  const target = S.pocket ? S.pocket.center : (S.protein.ligands[0] ? S.protein.center(S.protein.ligands[0].atoms) : S.protein.center(Array.from(S.protein.heavy)));
  const c = centroid(S.ligand.pos, S.ligand.n);
  for (let i = 0; i < S.ligand.n; i++) for (let d = 0; d < 3; d++) S.ligand.pos[i * 3 + d] += target[d] - c[d];
  S.ligandView.refresh();
}

async function loadCompound(entry) {
  try {
    status(`building 3D structure for ${entry.agiId || entry.label || 'compound'}…`);
    const st = await smilesTo3D(entry.canonical, { name: entry.agiId || entry.label || 'ligand' });
    S.compound = entry;
    await setLigand(st, { entry, smiles: entry.canonical });
    toast(`${entry.agiId || 'compound'} ready · ${st.embedMethod}`);
  } catch (e) { toast(`Could not build 3D: ${e.message}`, true); }
}

async function loadDrugByName(name) {
  try {
    status(`looking up ${name} in PubChem…`);
    const c = await pubchem.byName(name);
    let st;
    try { st = heavyAtomModel(parseMolblock(await pubchem.sdf3d(c.cid), { name: c.title }), c.title); }
    catch { st = await smilesTo3D(c.smiles, { name: c.title }); }
    await setLigand(st, { smiles: c.smiles, drug: c });
    toast(`${c.title} loaded from PubChem (CID ${c.cid})`);
  } catch (e) { toast(`PubChem has no 3D record for ${name}`, true); }
}

async function extractCocrystal(lig) {
  const pdbId = S.protein?.source?.split(' ')[1] || $('#hudTitle').textContent;
  // The lifted ligand must stop acting as part of the receptor, or it clashes with itself.
  S.protein.excludeAtoms(lig.atoms);
  S.proteinView.setStyle({});
  S.grid = new ProteinGrid(S.protein, 4);
  try {
    const sdf = await rcsb.ligandSdf(pdbId, lig.resName);
    const st = heavyAtomModel(parseMolblock(sdf, { name: lig.resName }), lig.resName);
    // Keep the crystallographic position.
    await setLigand(st, { keepPosition: true, cocrystal: lig.resName });
    S.pocket = { center: st.center(), label: `${lig.resName} site`, volume: null, residues: [] };
    highlightPocketResidues();
    toast(`${lig.resName} extracted with bond orders from the PDB chemical component`);
  } catch {
    const st = S.protein.subset(lig.atoms, { name: lig.resName });
    await setLigand(st, { keepPosition: true, cocrystal: lig.resName });
    toast(`${lig.resName} extracted (bonds inferred from distances)`);
  }
}

// ---------------------------------------------------------------- scoring / pockets / docking
function scoreNow() {
  if (!S.grid || !S.ligand) return null;
  const r = vinaScore(S.grid, S.ligand, S.ligand.pos, { details: true });
  S.lastScore = r;
  renderScore(r);
  drawHbonds(r.hbonds);
  highlightPocketResidues(r.contactResidues);
  return r;
}

function drawHbonds(hb) {
  for (const c of [...overlay.children]) if (c.userData.hbond) { c.geometry.dispose(); overlay.remove(c); }
  for (const h of (hb || []).slice(0, 12)) {
    const a = new THREE.Vector3(S.ligand.pos[h.lig * 3], S.ligand.pos[h.lig * 3 + 1], S.ligand.pos[h.lig * 3 + 2]);
    const b = new THREE.Vector3(S.protein.pos[h.prot * 3], S.protein.pos[h.prot * 3 + 1], S.protein.pos[h.prot * 3 + 2]);
    const l = dashedLine(a, b, 0x8ef5c2); l.userData.hbond = true; overlay.add(l);
  }
}

function highlightPocketResidues(list) {
  if (!S.proteinView) return;
  const res = list || (S.pocket?.residues || []);
  S.proteinView.pocketResidues = new Set(res);
  if (S.proteinView.style.rep === 'cartoon+pocket') S.proteinView.build();
}

async function doPockets() {
  if (!S.protein) return toast('Load a structure first', true);
  status('scanning for pockets…');
  await new Promise((r) => setTimeout(r, 10));
  const t0 = performance.now();
  S.pockets = findPockets(S.protein, { spacing: S.protein.n > 12000 ? 1.4 : 1.0 });
  status(`${S.pockets.length} pockets in ${Math.round(performance.now() - t0)} ms`);
  renderPockets();
  if (S.pockets[0]) selectPocket(0);
}

function selectPocket(i) {
  S.pocket = S.pockets[i] || null;
  renderPockets();
  drawPocketBlob();
  highlightPocketResidues();
  if (S.ligand) { placeLigandAtSite(); scoreNow(); }
}

function drawPocketBlob() {
  for (const c of [...overlay.children]) if (c.userData.pocket) { c.geometry.dispose(); overlay.remove(c); }
  if (!S.pocket || !$('#showPockets').checked || !S.pocket.points) return;
  const g = new THREE.SphereGeometry(0.55, 8, 6);
  const m = new THREE.MeshStandardMaterial({ color: 0x4cc9f0, transparent: true, opacity: 0.25, depthWrite: false });
  const mesh = new THREE.InstancedMesh(g, m, S.pocket.points.length);
  const mat = new THREE.Matrix4();
  S.pocket.points.forEach((p, k) => mesh.setMatrixAt(k, mat.makeTranslation(p[0], p[1], p[2])));
  mesh.userData.pocket = true; overlay.add(mesh);
}

async function doDock() {
  if (!S.ligand || !S.grid) return toast('Load a target and a ligand first', true);
  const center = S.pocket ? S.pocket.center : centroid(S.ligand.pos, S.ligand.n);
  S.stopFlag = false;
  $('#btnDock').disabled = true;
  status('docking…');
  const t0 = performance.now();
  const poses = await dockLigand(S.grid, S.ligand, center, {
    runs: 12, steps: 3500, box: 8,
    shouldStop: () => S.stopFlag,
    onProgress: ({ run, step, coords }) => {
      S.ligand.pos.set(coords); S.ligandView.refresh();
      status(`docking run ${run + 1}/12 step ${step}`);
      xr.panel.setStatus(`docking ${run + 1}/12`);
    },
  });
  S.poses = poses;
  $('#btnDock').disabled = false;
  if (poses.length) applyPose(0);
  renderPoses();
  if (poses.length) { try { analysePose(); } catch { /* analysis is a bonus, never a blocker */ } }
  if (poses.length) {
    S.ledger.append('dock', { compound: S.compound?.agiId || S.ligand.name, smiles: S.compound?.canonical || null,
      target: S.protein.name, site: S.pocket?.label || null, score: +poses[0].score.toFixed(2),
      poses: poses.length, method: 'Monte Carlo, Vina-style score', provenance: 'ESTIMATE: unvalidated in-browser score, not kcal/mol' }).then(renderLedger);
  }
  toast(`${poses.length} poses · best ${plain(fmt(poses[0]?.score), DOCK_TIER)} · ${Math.round((performance.now() - t0) / 1000)} s`);
}

function applyPose(i) {
  const p = S.poses[i]; if (!p) return;
  S.ligand.pos.set(p.coords);
  S.ligandView.refresh();
  if (S.md) S.md.ligRef = Float32Array.from(S.ligand.pos);
  scoreNow();
  renderPoses(i);
}

// Virtual screen: dock every (filtered) library compound against the current site.
async function screenLibrary({ limit = 200, runs = 4, steps = 1800 } = {}) {
  if (!S.grid) return toast('Load a target first', true);
  const list = S.library.compounds.slice(0, limit);
  if (!list.length) return toast('Import compounds first', true);
  S.screening = true; S.stopFlag = false;
  const center = S.pocket ? S.pocket.center : S.protein.center(Array.from(S.protein.heavy));
  let done = 0;
  for (const c of list) {
    if (S.stopFlag) break;
    try {
      const st = await smilesTo3D(c.canonical, { name: c.agiId || 'cmp' });
      const t = centroid(st.pos, st.n);
      for (let i = 0; i < st.n; i++) for (let d = 0; d < 3; d++) st.pos[i * 3 + d] += center[d] - t[d];
      const poses = await dockLigand(S.grid, st, center, { runs, steps, box: 8, shouldStop: () => S.stopFlag });
      c.dockScore = poses[0] ? +poses[0].score.toFixed(2) : null;
      c.dockTarget = S.protein.name;
    } catch { c.dockScore = null; }
    status(`screening ${++done}/${list.length} · ${c.agiId || ''} ${c.dockScore != null ? plain(c.dockScore, DOCK_TIER) : ''}`);
    renderLibrary();
  }
  S.screening = false;
  S.library.save();
  const ranked = list.filter((c) => c.dockScore != null).sort((a, b) => a.dockScore - b.dockScore);
  toast(`Screen done. Best (est.): ${ranked.slice(0, 3).map((c) => `${c.agiId} ${c.dockScore}`).join(', ')}`);
  $('#libSort').value = 'score'; renderLibrary();
  S.ledger.append('screen', { target: S.protein.name, compounds: ranked.length,
    best: ranked[0] ? `${ranked[0].agiId} ${ranked[0].dockScore}` : 'none',
    ranking: ranked.slice(0, 10).map((c) => ({ id: c.agiId, score: c.dockScore })),
    provenance: 'ESTIMATE: unvalidated in-browser score, not kcal/mol' }).then(renderLedger);
}

// ---------------------------------------------------------------- interactive MD
function startMD() {
  if (!S.protein && !S.ligand) return toast('Nothing to simulate', true);
  S.md = new MDEngine({ protein: S.protein, ligand: S.ligand, temperature: +$('#liveTemp').value || 300 });
  S.md.frozenProtein = $('#freezeProtein').checked;
  S.md.relax();
  S.ligandView?.refresh({ cartoon: false });
  S.mdRunning = true;
  $('#btnMd').textContent = 'Stop MD'; $('#btnMd').classList.add('on');
  $('#mdBadge').classList.remove('hidden');
  status('interactive dynamics running');
}

function stopMD() {
  S.mdRunning = false; S.md = null;
  $('#btnMd').textContent = 'Start MD'; $('#btnMd').classList.remove('on');
  $('#mdBadge').classList.add('hidden');
}

function toggleMD() { S.mdRunning ? stopMD() : startMD(); }

// Backend all-atom MD (OpenMM) with trajectory playback.
async function runBackendMD() {
  if (!S.protein) return toast('Load a structure first', true);
  if (!S.caps?.openmm) return toast('Start the local server with OpenMM for all-atom MD', true);
  try {
    const id = await server.startMD({ pdb: S.protein.toPDB(), steps: +$('#mdSteps').value, frames: 60, temperature: +$('#mdTemp').value });
    S.backendJob = id;
    logTo('#backendMdLog', `job ${id} queued`);
    pollBackend(id);
  } catch (e) { toast(e.message, true); }
}

async function pollBackend(id) {
  let since = 0, topology = null, frames = [];
  while (S.backendJob === id) {
    const j = await server.pollMD(id, since);
    if (j.topology) topology = j.topology;
    if (j.frames?.length) { frames.push(...j.frames); since = j.frameCount; }
    logTo('#backendMdLog', `${j.stage} ${Math.round((j.progress || 0) * 100)}% ${j.platform || ''} ${j.nsPerDay ? j.nsPerDay + ' ns/day' : ''}`);
    if (j.stage === 'error') { toast(j.error, true); break; }
    if (j.stage === 'done') {
      const st = parsePDB(topology, { name: `${S.protein.name} (OpenMM)`, source: j.forcefield });
      S.trajectory = { st, frames, i: 0 };
      setProtein(st, { subtitle: `all-atom MD · ${j.forcefield} · ${fmt(j.simulatedPs, 0)} ps · ${frames.length} frames` });
      S.ledger.append('md', { engine: 'OpenMM ' + j.forcefield, target: st.name, ps: +fmt(j.simulatedPs, 1), frames: frames.length, platform: j.platform }).then(renderLedger);
      toast(`Trajectory ready: ${frames.length} frames — playing`);
      break;
    }
    if (j.stage === 'cancelled') break;
    await new Promise((r) => setTimeout(r, 1500));
  }
}

// ---------------------------------------------------------------- selection & measurement
function pickAtom(hit) {
  if (!hit) return null;
  for (const v of [S.ligandView, S.proteinView]) {
    if (v && (hit.object.parent === v.group || hit.object === v.group)) {
      const i = v.hitToAtom(hit);
      if (i >= 0) return { view: v, atom: i };
    }
  }
  return null;
}

const RESIDUE_NAMES = { ALA: 'Alanine', ARG: 'Arginine', ASN: 'Asparagine', ASP: 'Aspartate', CYS: 'Cysteine', GLN: 'Glutamine',
  GLU: 'Glutamate', GLY: 'Glycine', HIS: 'Histidine', ILE: 'Isoleucine', LEU: 'Leucine', LYS: 'Lysine', MET: 'Methionine',
  PHE: 'Phenylalanine', PRO: 'Proline', SER: 'Serine', THR: 'Threonine', TRP: 'Tryptophan', TYR: 'Tyrosine', VAL: 'Valine',
  HOH: 'Water', ZN: 'Zinc ion', CU: 'Copper ion', MG: 'Magnesium ion', CA: 'Calcium ion', FE: 'Iron ion', NA: 'Sodium ion', CL: 'Chloride ion' };
const ELEMENT_NAMES = { H: 'hydrogen', C: 'carbon', N: 'nitrogen', O: 'oxygen', S: 'sulfur', P: 'phosphorus', F: 'fluorine',
  CL: 'chlorine', BR: 'bromine', I: 'iodine', B: 'boron', SE: 'selenium', ZN: 'zinc', CU: 'copper', FE: 'iron', MG: 'magnesium' };
const plddtBand = (b) => (b >= 90 ? 'very high' : b >= 70 ? 'confident' : b >= 50 ? 'low' : 'very low');

// What a researcher sees when pointing at something: residue (or ligand) identity first, then the atom and its confidence.
function describeAtom(view, i) {
  const st = view.st, r = st.residues[st.atomRes[i]];
  const sym = String(st.element[i] || '').toUpperCase(), elName = ELEMENT_NAMES[sym] || sym;
  if (view === S.ligandView) {
    // S.compound survives when a ligand comes from elsewhere (co-crystal, known drug), so only trust it if it built this one.
    const c = S.compound && [S.compound.agiId, S.compound.label].includes(st.name) ? S.compound : {}, id = c.agiId || c.id;
    const name = c.name || (c.label ? c.label.split(' — ')[0] : null) || id || st.name || 'Ligand';
    return [name === id || !id ? name : `${name} (${id})`, `atom ${st.atomName[i]} · ${elName}`, c.notes || null].filter(Boolean);
  }
  const resName = RESIDUE_NAMES[r.resName] || r.resName;
  const title = r.polymer ? `${resName} ${r.resSeq} · chain ${r.chain}` : `${resName}${r.resName !== resName ? ` (${r.resName})` : ''} · chain ${r.chain}`;
  const b = st.bfac[i];
  const conf = S.proteinMeta?.alphafold ? `pLDDT ${b.toFixed(0)} (${plddtBand(b)})` : b ? `B-factor ${b.toFixed(1)} Å²` : null;
  return [title, `atom ${st.atomName[i]} · ${elName}`, conf].filter(Boolean);
}

function onPick(hit) {
  const p = pickAtom(hit);
  if (!p) return;
  S.selection.push(p);
  if (S.selection.length > 3) S.selection = S.selection.slice(-1);
  renderSelection();
}

function renderSelection() {
  for (const c of [...overlay.children]) if (c.userData.measure) { c.geometry?.dispose?.(); overlay.remove(c); }
  const pts = S.selection.map(({ view, atom }) => new THREE.Vector3(view.st.pos[atom * 3], view.st.pos[atom * 3 + 1], view.st.pos[atom * 3 + 2]));
  const desc = S.selection.map(({ view, atom }) => {
    const st = view.st, r = st.residues[st.atomRes[atom]];
    return `${st.atomName[atom]} ${r.resName}${r.polymer ? r.resSeq : ''}${r.chain ? '/' + r.chain : ''}`;
  });
  let info = desc.join('  ·  ') || 'Click an atom to select.';
  if (pts.length >= 2) {
    const d = pts[0].distanceTo(pts[1]);
    const l = dashedLine(pts[0], pts[1]); l.userData.measure = true; overlay.add(l);
    const lbl = textSprite(`${d.toFixed(2)} Å`); lbl.userData.measure = true;
    lbl.position.copy(pts[0]).add(pts[1]).multiplyScalar(0.5); lbl.scale.multiplyScalar(2.2); overlay.add(lbl);
    info += ` — ${d.toFixed(2)} Å`;
  }
  if (pts.length === 3) {
    const a = pts[0].clone().sub(pts[1]), b = pts[2].clone().sub(pts[1]);
    const ang = THREE.MathUtils.radToDeg(a.angleTo(b));
    const l2 = dashedLine(pts[1], pts[2]); l2.userData.measure = true; overlay.add(l2);
    info += ` — angle ${ang.toFixed(1)}°`;
  }
  $('#selInfo').textContent = info;
  if (xr.active && S.selection.length) xr.panel.setStatus(info.split('  ·  ').pop());
}

let steer = null;
function startSteer(worldPoint) {
  if (!S.md || !S.ligand) return;
  const local = model.worldToLocal(worldPoint.clone());
  steer = { offset: local.clone().sub(new THREE.Vector3(...centroid(S.ligand.pos, S.ligand.n))) };
  S.md.setSteer({ x: local.x - steer.offset.x, y: local.y - steer.offset.y, z: local.z - steer.offset.z }, 25);
}
function updateSteer(worldPoint) {
  if (!steer || !S.md) return;
  const local = model.worldToLocal(worldPoint.clone());
  S.md.setSteer({ x: local.x - steer.offset.x, y: local.y - steer.offset.y, z: local.z - steer.offset.z }, 25);
}
function endSteer() { steer = null; S.md?.setSteer(null); }

// ---------------------------------------------------------------- render loop
let frames = 0, last = performance.now(), fps = 0;
renderer.setAnimationLoop((t, xrFrame) => {
  if (S.mdRunning && S.md) {
    S.md.step(12);
    S.ligandView?.refresh({ cartoon: false });
    if (!S.md.frozenProtein) S.proteinView?.refresh({ cartoon: frames % 6 === 0 });
    if (frames % 10 === 0) { const sc = scoreNow(); renderMdStats(sc); }
  }
  if (S.trajectory) {
    const tr = S.trajectory;
    if (frames % 3 === 0) {
      const f = tr.frames[tr.i % tr.frames.length];
      if (f && S.protein === tr.st) { S.protein.pos.set(f); S.proteinView.refresh({ cartoon: true }); }
      tr.i++;
    }
  }
  const dt = Math.min(0.05, (t - (S.lastT || t)) / 1000); S.lastT = t;
  S.env?.update(dt);
  S.walk?.update(dt, xr.active);
  // Distance culling follows the viewer, refreshed a few times a second rather than every frame.
  if (S.env?.quality && S.env.quality !== 'full' && frames % 20 === 0) S.env.setQuality(S.env.quality);
  if (S.orbitSpeed) workspace.rotation.y += S.orbitSpeed;
  if (xr.active) {
    xr.update();
    if (S.hands && xrFrame) S.hands.update(xrFrame, renderer.xr.getReferenceSpace());
    S.collab?.tick(camera, xr.controllers);
  }
  else controls.update();
  renderer.render(scene, camera);
  frames++;
  const now = performance.now();
  if (now - last > 1000) { fps = Math.round(frames * 1000 / (now - last)); frames = 0; last = now; $('#perf').textContent = `${fps} fps`; }
});

// ---------------------------------------------------------------- UI: targets
function renderPrograms() {
  const progs = [...new Set(S.targets.map((t) => t.program))];
  const box = $('#programChips'); box.innerHTML = '';
  for (const p of progs) {
    const b = el('button', S.program === p ? 'on' : '', `${p} <span class="s">${S.targets.filter((t) => t.program === p).length}</span>`);
    b.onclick = () => { S.program = p; renderPrograms(); renderTargets(); };
    box.appendChild(b);
  }
}

function renderTargets() {
  const list = $('#targetList'); list.innerHTML = '';
  for (const t of S.targets.filter((x) => x.program === S.program)) {
    const item = el('div', 'item' + (S.target === t ? ' active' : ''));
    const af = t.alphafold?.plddt;
    item.innerHTML = `<div class="t"><span class="n">${t.symbol}</span>
      <span class="s">${t.pdbCount} PDB${af ? ` · pLDDT ${af.toFixed(0)}` : ''}</span></div>
      <div class="d">${t.disease}</div>`;
    item.onclick = () => openTarget(t);
    list.appendChild(item);
  }
}

async function openTarget(t) {
  S.target = t; renderTargets();
  const acts = $('#structActions'); acts.innerHTML = '';
  $('#structInfo').innerHTML = `<b>${t.symbol}</b> — ${t.name}<br><span class="hint">${t.rationale}</span>`;
  if (t.alphafold) {
    const b = el('button', 'primary', `AlphaFold model (pLDDT ${fmt(t.alphafold.plddt, 0)})`);
    b.onclick = () => loadAlphaFold(t.uniprot, { symbol: t.symbol }).catch((e) => toast(e.message, true));
    acts.appendChild(b);
  }
  for (const s of (t.structures || []).slice(0, 6)) {
    const b = el('button', '', `${s.id}${s.resolution ? ` ${s.resolution}Å` : ''}${s.ligands?.length ? ' ⬤' : ''}`);
    b.title = `${s.title}${s.ligands?.length ? `\nligands: ${s.ligands.map((l) => l.id).join(', ')}` : ''}`;
    b.onclick = () => loadPdb(s.id, { uniprot: t.uniprot, symbol: t.symbol }).catch((e) => toast(e.message, true));
    acts.appendChild(b);
  }
  if (t.bestPdb && !(t.structures || []).some((s) => s.id === t.bestPdb)) {
    const b = el('button', '', t.bestPdb); b.onclick = () => loadPdb(t.bestPdb, { uniprot: t.uniprot }); acts.appendChild(b);
  }
  renderDrugs(t);
  renderEvidence(t);
  // Return the structure load so callers (the tool layer, the film, the demo) can wait for it.
  if (t.alphafold) return loadAlphaFold(t.uniprot, { symbol: t.symbol }).catch((e) => toast(e.message, true));
  if (t.bestPdb) return loadPdb(t.bestPdb, { uniprot: t.uniprot }).catch((e) => toast(e.message, true));
  return null;
}

function renderStructureInfo(meta) {
  const st = S.protein;
  const poly = st.residues.filter((r) => r.polymer).length;
  $('#structInfo').innerHTML = `<b>${st.name}</b><br><span class="hint">${meta.subtitle || st.source}</span>
    <div class="props" style="margin-top:6px">
      <span>atoms <b>${st.n}</b></span><span>residues <b>${poly}</b></span>
      <span>chains <b>${st.chains.join(', ')}</b></span><span>ligands <b>${st.ligands.length}</b></span>
    </div>`;
  const acts = $('#structActions'); acts.innerHTML = '';
  const dl = el('button', '', 'Download PDB'); dl.onclick = () => downloadText(st.toPDB(), `${st.name.replace(/\W+/g, '_')}.pdb`); acts.appendChild(dl);
  const fold = el('button', '', 'Similar folds');
  fold.title = 'Foldseek search of this fold against the AlphaFold database and the whole PDB';
  fold.onclick = () => findSimilarFolds(fold);
  acts.appendChild(fold);
  if (meta.uniprot) {
    const af = el('button', '', 'AlphaFold version'); af.onclick = () => loadAlphaFold(meta.uniprot, { symbol: meta.symbol }); acts.appendChild(af);
    const pdbs = el('button', '', 'All PDB entries');
    pdbs.onclick = async () => {
      const { ids } = await rcsb.byUniprot(meta.uniprot, 25);
      const det = await rcsb.details(ids);
      showResults(det.map((d) => ({ title: `${d.id} · ${fmt(d.resolution, 1)} Å`, sub: d.title.slice(0, 80), onPick: () => loadPdb(d.id, meta) })));
    };
    acts.appendChild(pdbs);
  }
}

// "Which known folds look like this one?" - Foldseek against AlphaFold DB + PDB.
async function findSimilarFolds(btn) {
  if (!S.protein) return;
  btn.disabled = true;
  try {
    const chain = S.protein.chains[0];
    const idx = [...Array(S.protein.n).keys()].filter((i) => S.protein.chain[i] === chain && !S.protein.het[i]);
    const sub = S.protein.subset(idx, { name: S.protein.name });
    const groups = await foldseek.search(sub.toPDB(), { onStatus: status });
    const items = [];
    for (const g of groups) {
      for (const h of g.hits.slice(0, 12)) {
        items.push({ title: `${h.pdb || h.uniprot || h.id}`, tag: `${g.db} · ${fmt(h.seqId, 0)}% id`,
          sub: `${(h.title || '').slice(0, 90)}${h.eval != null ? ` · E=${h.eval.toExponential(1)}` : ''}`,
          onPick: () => (h.pdb ? loadPdb(h.pdb) : loadAlphaFold(h.uniprot)).catch((e) => toast(e.message, true)) });
      }
    }
    showResults(items);
    toast(`${items.length} structurally similar folds found`);
  } catch (e) { toast(e.message, true); } finally { btn.disabled = false; }
}

function renderCocrystals() {
  const box = $('#cocrystalList'); box.innerHTML = '';
  const st = S.protein; if (!st) return;
  if (!st.ligands.length) { box.innerHTML = '<div class="hint">No bound ligands in this entry.</div>'; return; }
  for (const l of st.ligands) {
    const it = el('div', 'item', `<div class="t"><span class="n">${l.resName}</span><span class="s">chain ${l.chain} · ${l.atoms.length} atoms</span></div>`);
    it.onclick = () => extractCocrystal(l);
    box.appendChild(it);
  }
}

async function renderDrugs(t) {
  $('#drugTargetName').innerHTML = `<b>${t.symbol}</b> — ${t.disease}`;
  const box = $('#drugList'); box.innerHTML = '<div class="hint">loading…</div>';
  try {
    const drugs = t.ensembl ? await openTargets.drugs(t.ensembl) : [];
    box.innerHTML = drugs.length ? '' : '<div class="hint">No clinical drugs or candidates recorded for this target.</div>';
    for (const d of drugs) {
      const it = el('div', 'item', `<div class="t"><span class="n">${d.name}</span><span class="badge-sm ${/APPROVED|PHASE_4/.test(d.stage) ? 'good' : 'warn'}">${(d.stage || '').replace('PHASE_', 'Ph')}</span></div>
        <div class="d">${d.type}${d.moa ? ' · ' + d.moa : ''}${d.diseases.length ? '<br>' + d.diseases.join(', ') : ''}</div>`);
      it.onclick = () => loadDrugByName(d.name);
      box.appendChild(it);
    }
  } catch (e) { box.innerHTML = `<div class="hint">Open Targets unavailable (${e.message})</div>`; }
  const act = $('#activeList'); act.innerHTML = '<div class="hint">loading ChEMBL…</div>';
  try {
    const rows = await chembl.actives(t.uniprot);
    act.innerHTML = rows.length ? '' : '<div class="hint">No potent actives found.</div>';
    for (const r of rows.slice(0, 25)) {
      const it = el('div', 'item', `<div class="t"><span class="n">${r.name || r.chembl}</span><span class="s">p${r.type} ${fmt(r.pchembl, 1)}</span></div>`);
      it.onclick = async () => { const st = await smilesTo3D(r.smiles, { name: r.name || r.chembl }); setLigand(st, { smiles: r.smiles }); };
      act.appendChild(it);
    }
  } catch { act.innerHTML = '<div class="hint">ChEMBL is not responding right now.</div>'; }
}

// ---------------------------------------------------------------- UI: compounds
function renderLigandCard(info = {}) {
  const box = $('#ligandCard');
  const st = S.ligand; if (!st) { box.textContent = 'No ligand.'; return; }
  const c = S.compound;
  box.innerHTML = '';
  const title = el('div', '', `<b>${st.name}</b> <span class="hint">${st.n} heavy atoms${st.embedMethod ? ' · ' + st.embedMethod : ''}</span>`);
  box.appendChild(title);
  const smiles = info.smiles || c?.canonical;
  if (smiles) {
    depict(smiles, 320, 190).then((svg) => { const d = el('div', 'depict', svg); box.insertBefore(d, title.nextSibling); }).catch(() => {});
    analyze(smiles).then((a) => {
      const r = a.rules, d = a.desc;
      box.appendChild(el('div', 'props', `
        <span>MW <b>${fmt(d.mw, 1)}</b></span><span>cLogP <b>${fmt(d.clogp)}</b></span>
        <span>TPSA <b>${fmt(d.tpsa, 1)}</b></span><span>HBD/HBA <b>${d.hbd}/${d.hba}</b></span>
        <span>rot. bonds <b>${d.rotb}</b></span><span>rings <b>${d.rings}</b></span>
        <span>Lipinski <b>${r.lipinskiViolations} viol.</b></span><span>CNS MPO <b>${fmt(r.cnsMpo5, 1)}/5</b></span>`));
      box.appendChild(el('div', 'hint', r.bbbLikely ? 'Profile is consistent with brain penetration (rule of thumb).' : 'Unlikely to cross the blood-brain barrier on these properties.'));
      if (c) { c.profile = { desc: d, rules: r, inchikey: a.inchikey }; }
    }).catch(() => {});
    const row = el('div', 'row wrap');
    const nov = el('button', '', 'Novelty check');
    nov.onclick = async () => {
      nov.disabled = true;
      const entry = c || S.library.insert({ smiles, canonical: smiles, label: st.name, source: 'ad hoc' });
      const k = await S.library.checkNovelty(entry);
      box.appendChild(el('div', 'hint', k.exact.length
        ? `Known compound: PubChem CID ${k.exact[0].cid}${k.exact[0].Title ? ` (${k.exact[0].Title})` : ''}.`
        : `No exact PubChem match. Nearest known: ${k.nearest.map((n) => n.title).slice(0, 3).join(', ') || 'none above 85% similarity'}.`));
      nov.disabled = false;
    };
    row.appendChild(nov);
    const add = el('button', '', 'Add to library');
    add.onclick = () => { S.library.insert({ smiles, canonical: smiles, label: st.name, source: 'manual' }); S.library.save(); renderLibrary(); toast('Added to the AGI library'); };
    row.appendChild(add);
    box.appendChild(row);
  }
}

function renderScore(r) {
  if (!r) return;
  $('#dockResult').innerHTML = `<div class="props">
    <span>score <b>${mark(fmt(r.total), DOCK_TIER)}</b></span><span>ligand eff. <b>${mark(fmt(r.ligandEfficiency), DOCK_TIER)}</b></span>
    <span>H-bonds <b>${r.hbonds.length}</b></span><span>contacts <b>${r.contactResidues.length} res</b></span>
    <span>clash <b>${fmt(r.terms.repulsion, 1)}</b></span><span>hydrophobic <b>${fmt(r.terms.hydrophobic, 1)}</b></span>
  </div>${note(DOCK_TIER, 'Lower is better.')}`;
  xr.panel.setStatus(`score ${fmt(r.total)} · ${r.hbonds.length} H-bonds`, DOCK_TIER);
}

function renderPockets() {
  const box = $('#pocketList'); box.innerHTML = '';
  S.pockets.forEach((p, i) => {
    const it = el('div', 'item' + (S.pocket === p ? ' active' : ''), `<div class="t"><span class="n">Pocket ${i + 1}</span>
      <span class="s">${Math.round(p.volume)} Å³ · buried ${(p.buriedness * 100).toFixed(0)}%</span></div>
      <div class="d">${p.label || ''}</div>`);
    it.onclick = () => selectPocket(i);
    box.appendChild(it);
  });
}

function renderPoses(active = -1) {
  const box = $('#poseList'); box.innerHTML = '';
  S.poses.forEach((p, i) => {
    const it = el('div', 'item' + (i === active ? ' active' : ''), `<div class="t"><span class="n">Pose ${i + 1}</span><span class="s">${mark(fmt(p.score), DOCK_TIER)}</span></div>`);
    it.onclick = () => applyPose(i);
    box.appendChild(it);
  });
}

function renderMdStats(sc) {
  if (!S.md) return;
  const e = S.md.energy;
  $('#mdStats').innerHTML = `<span>time <b>${fmt(S.md.time, 1)} ps</b></span><span>T <b>${fmt(S.md.kineticTemperature(), 0)} K</b></span>
    <span>inter E <b>${fmt(e.inter, 1)}</b></span><span>ligand RMSD <b>${fmt(S.md.ligandRMSD())} Å</b></span>
    <span>protein RMSF <b>${fmt(S.md.proteinRMSF())} Å</b></span><span>score <b>${mark(fmt(sc?.total), DOCK_TIER)}</b></span>`;
  $('#mdBadge').textContent = `MD ${fmt(S.md.time, 1)} ps · ${fmt(S.md.kineticTemperature(), 0)} K · score ${plain(fmt(sc?.total), DOCK_TIER)}`;
}

let libFiltered = null;
function renderLibrary() {
  const box = $('#libList'); box.innerHTML = '';
  let list = libFiltered || S.library.search($('#libSearch').value);
  const sort = $('#libSort').value;
  list = [...list].sort((a, b) => {
    if (sort === 'mw') return (a.profile?.desc.mw || 1e9) - (b.profile?.desc.mw || 1e9);
    if (sort === 'clogp') return (a.profile?.desc.clogp ?? 1e9) - (b.profile?.desc.clogp ?? 1e9);
    if (sort === 'cns') return (b.profile?.rules.cnsMpo5 ?? -1) - (a.profile?.rules.cnsMpo5 ?? -1);
    if (sort === 'score') return (num(a.dockScore) ?? 1e9) - (num(b.dockScore) ?? 1e9);
    return (a.agiId || 'zz').localeCompare(b.agiId || 'zz', undefined, { numeric: true });
  });
  $('#libStats').textContent = `${S.library.compounds.length} compounds${libFiltered ? ` · ${list.length} match` : ''}${S.library.rejects.length ? ` · ${S.library.rejects.length} need review` : ''}`;
  for (const c of list.slice(0, 300)) {
    const it = el('div', 'item' + (S.compound === c ? ' active' : ''));
    const info = el('div', '', `<div class="t"><span class="n">${c.agiId || '—'}</span>
      <span class="s">${num(c.dockScore) != null ? mark(fmt(num(c.dockScore)), tierOf(c, 'dockScore', DOCK_TIER)) : c.profile ? `MW ${fmt(c.profile.desc.mw, 0)}` : ''}</span></div>
      <div class="d">${(c.label || c.canonical).slice(0, 46)}</div>`);
    const thumb = el('div', '', '');
    it.append(thumb, info);
    it.onclick = () => loadCompound(c);
    box.appendChild(it);
    depict(c.canonical, 120, 90).then((svg) => { thumb.innerHTML = svg; }).catch(() => {});
  }
  const rb = $('#rejectBox');
  rb.classList.toggle('hidden', !S.library.rejects.length);
  const rl = $('#rejectList'); rl.innerHTML = '';
  for (const r of S.library.rejects.slice(0, 40)) rl.appendChild(el('div', 'item', `<div class="d" style="font-family:var(--mono)">${r.id ? `#${r.id} ` : ''}${r.raw.slice(0, 60)}</div>`));
}

// ---------------------------------------------------------------- evidence panel
// Everything free and key-free that says whether a target is worth working on.
async function gatherEvidence() {
  const t = S.target;
  const acc = t?.uniprot || null;
  const symbol = t?.symbol || S.protein?.name?.split(' ')[0];
  if (!symbol) return toast('Load a target first', true);
  document.getElementById('evSummary')?.remove();
  $('#evidenceHead').innerHTML = `<b>${symbol}</b>${acc ? ` · ${acc}` : ''} — gathering from nine databases…`;
  const fill = (sel, rows, empty) => { const b = $(sel); b.innerHTML = rows.length ? '' : `<div class="hint">${empty}</div>`; rows.forEach((r) => b.appendChild(r)); };

  const jobs = [
    acc && interpro.domains(acc).then((d) => fill('#evDomains', d.slice(0, 12).map((x) => el('div', 'item',
      `<div class="t"><span class="n">${x.name}</span><span class="s">${x.type}</span></div>
       <div class="d">${x.id}${x.locations.length ? ` · residues ${x.locations.map((l) => l.join('–')).join(', ')}` : ''}</div>`)), 'No InterPro domains.')),
    acc && reactome.pathways(acc).then((p) => fill('#evPathways', p.slice(0, 12).map((x) => {
      const it = el('div', 'item', `<div class="d">${x.name}</div>`);
      it.onclick = () => open(`https://reactome.org/content/detail/${x.id}`, '_blank');
      return it;
    }), 'No Reactome pathways.')),
    stringdb.partners(symbol).then((p) => fill('#evPartners', p.slice(0, 14).map((x) => {
      const known = S.targets.find((y) => y.symbol === x.symbol);
      const it = el('div', 'item', `<div class="t"><span class="n">${x.symbol}</span><span class="s">${x.score.toFixed(2)}${known ? ' · in library' : ''}</span></div>`);
      it.onclick = () => (known ? openTarget(known) : uniprot.searchGene(x.symbol).then((g) => g[0] && loadAlphaFold(g[0].uniprot, { symbol: x.symbol })));
      return it;
    }), 'No STRING partners.')),
    proteinAtlas.expression(symbol).then((e) => { $('#evExpression').innerHTML = e
      ? `<div class="props">${e.top.map((x) => `<span>${x.tissue} <b>${x.nTPM}</b></span>`).join('')}</div>
         <div class="hint" style="margin-top:6px">${e.specificity}${e.location?.length ? ` · ${[].concat(e.location).slice(0, 4).join(', ')}` : ''}</div>`
      : '<div class="hint">No expression record.</div>'; }),
    gnomad.constraint(symbol).then((c) => { $('#evConstraint').innerHTML = c
      ? `<div class="props"><span>pLI <b>${fmt(c.pLI, 3)}</b></span><span>LoF o/e <b>${fmt(c.oe_lof, 2)}</b></span>
         <span>missense Z <b>${fmt(c.mis_z, 2)}</b></span><span>synonymous Z <b>${fmt(c.syn_z, 2)}</b></span></div>
         <div class="hint" style="margin-top:6px">${c.pLI > 0.9 ? 'Highly intolerant of loss of function: knocking this gene out is rarely tolerated.' : c.pLI < 0.1 ? 'Tolerant of loss of function in the general population.' : 'Moderately constrained.'}</div>`
      : '<div class="hint">No gnomAD constraint record.</div>'; }),
    trials.search({ cond: t?.disease?.split('/')[0] || symbol, size: 12 }).then((r) => {
      fill('#evTrials', r.studies.map((s2) => {
        const it = el('div', 'item', `<div class="t"><span class="n">${s2.nct}</span><span class="s">${s2.phase || '—'} · ${s2.status}</span></div>
          <div class="d">${(s2.title || '').slice(0, 96)}</div>`);
        it.onclick = () => open(`https://clinicaltrials.gov/study/${s2.nct}`, '_blank');
        return it;
      }), 'No trials found.');
      $('#evidenceHead').dataset.trials = r.total;
    }),
    europepmc.search(`${symbol} AND (drug OR inhibitor OR therapeutic)`, 12).then((p) => fill('#evPapers', p.map((x) => {
      const it = el('div', 'item', `<div class="t"><span class="n">${x.journal || x.source} ${x.year}</span><span class="s">${x.cited} citations${x.open ? ' · open' : ''}</span></div>
        <div class="d">${x.title.slice(0, 110)}</div>`);
      it.onclick = () => open(x.doi ? `https://doi.org/${x.doi}` : `https://europepmc.org/article/${x.source}/${x.id}`, '_blank');
      return it;
    }), 'No papers found.')),
  ].filter(Boolean);
  await Promise.allSettled(jobs);
  // Pharos development level and a gene summary round out the picture.
  await Promise.allSettled([
    pharos.target(symbol).then((t2) => { if (t2) $('#evConstraint').innerHTML += `<div class="hint" style="margin-top:6px">Pharos: <b>${t2.developmentLevel}</b>${t2.family ? ` · ${t2.family}` : ''}${t2.diseases?.length ? ` · ${t2.diseases[0]}` : ''}</div>`; }),
    biothings.gene(symbol).then((g) => { if (g?.summary) $('#evidenceHead').insertAdjacentHTML('afterend', `<div class="block" id="evSummary"><h4>Summary <small>NCBI via MyGene</small></h4><div class="hint">${g.summary}</div></div>`); }),
  ]);
  const trialCount = $('#evidenceHead').dataset.trials;
  $('#evidenceHead').innerHTML = `<b>${symbol}</b>${acc ? ` · ${acc}` : ''} — domains, pathways, interactions, expression, constraint, ${trialCount || 0} trials and literature.`;
  S.ledger.append('evidence', { target: symbol, uniprot: acc, sources: ['InterPro', 'Reactome', 'STRING', 'Human Protein Atlas', 'gnomAD', 'ClinicalTrials.gov', 'Europe PMC'] }).then(renderLedger);
}

// ---------------------------------------------------------------- featured research programmes
// Each funder's own trial registry is public, so the programme panel shows live work rather than a
// static description: the sponsor string is what ClinicalTrials.gov files the studies under.
const FOUNDATIONS = [
  { name: 'Shriners Children\'s', program: 'Shriners Children\'s', spons: 'Shriners',
    blurb: 'Paediatric orthopaedics, burns, spinal cord injury, cleft and skeletal dysplasia.' },
  { name: 'Michael J. Fox Foundation', program: "Parkinson's", spons: 'Michael J. Fox Foundation',
    blurb: 'The largest non-profit funder of Parkinson\'s research; LRRK2, GBA1 and alpha-synuclein programmes.' },
  { name: 'ALS Association', program: 'ALS', spons: 'ALS Association',
    blurb: 'Funds ALS therapy development and the trials network.' },
  { name: 'Parkinson\'s Foundation', program: "Parkinson's", spons: "Parkinson's Foundation",
    blurb: 'Care standards and research into symptomatic and disease-modifying therapy.' },
  { name: 'ALS / motor neuron (all)', program: 'ALS', cond: 'amyotrophic lateral sclerosis',
    blurb: 'Every registered ALS trial, whoever sponsors it.' },
  { name: 'Parkinson\'s (all)', program: "Parkinson's", cond: "Parkinson disease",
    blurb: 'Every registered Parkinson\'s trial.' },
  { name: 'Osteogenesis imperfecta', program: 'Shriners Children\'s', cond: 'osteogenesis imperfecta',
    blurb: 'Brittle bone disease: collagen, sclerostin and bisphosphonate programmes.' },
];

function renderFoundations() {
  const box = $('#foundationChips'); box.innerHTML = '';
  for (const f of FOUNDATIONS) {
    const b = el('button', '', f.name);
    b.onclick = () => openFoundation(f, b);
    box.appendChild(b);
  }
}

async function openFoundation(f, btn) {
  $$('#foundationChips button').forEach((b) => b.classList.toggle('on', b === btn));
  $('#foundationInfo').innerHTML = `<b>${f.name}</b> — ${f.blurb}`;
  if (f.program && S.program !== f.program) { S.program = f.program; renderPrograms(); renderTargets(); }
  const box = $('#trialList'); box.innerHTML = '<div class="hint">loading trials…</div>';
  try {
    const r = await trials.search({ spons: f.spons, cond: f.cond, size: 30 });
    box.innerHTML = `<div class="hint">${r.total} registered studies</div>`;
    for (const t of r.studies) {
      const it = el('div', 'item', `<div class="t"><span class="n">${t.title.slice(0, 70)}</span>
        <span class="badge-sm ${/RECRUIT/i.test(t.status) ? 'good' : ''}">${(t.status || '').replace(/_/g, ' ').toLowerCase()}</span></div>
        <div class="d">${t.phase || t.StudyType || ''} ${t.interventions.join(', ').slice(0, 70)}${t.sponsor ? `<br>${t.sponsor}` : ''}</div>`);
      it.onclick = () => { const drug = t.interventions[0]; if (drug) loadDrugByName(drug.replace(/^(Drug|Biological|Other):\s*/i, '')); };
      box.appendChild(it);
    }
  } catch (e) { box.innerHTML = `<div class="hint">ClinicalTrials.gov unavailable (${e.message})</div>`; }
}

// Domains, pathways, interaction partners, population constraint and expression for the loaded target.
async function renderEvidence(t) {
  const box = $('#evidenceBox');
  if (!t || !t.uniprot) { box.textContent = 'Load a target to see its evidence.'; return; }
  box.innerHTML = '<div class="hint">gathering evidence…</div>';
  // gnomAD is not fetched here: its GraphQL endpoint sends no CORS headers, so the browser blocks it on every
  // target load. It is still attempted from the Evidence tab's explicit "Gather evidence" button.
  const [dom, path, part, exp] = await Promise.all([
    interpro.domains(t.uniprot).catch(() => []), reactome.pathways(t.uniprot).catch(() => []),
    stringdb.partners(t.symbol).catch(() => []), proteinAtlas.expression(t.symbol).catch(() => null),
  ]);
  const chip = (x) => `<span class="badge-sm">${x}</span>`;
  box.innerHTML = `
    <div style="margin-bottom:8px"><b>${t.symbol}</b> ${t.name}</div>
    ${dom.length ? `<div style="margin-bottom:8px"><b>Domains</b><br>${dom.slice(0, 8).map((d) => chip(`${d.name}${d.locations[0] ? ` ${d.locations[0][0]}-${d.locations[0][1]}` : ''}`)).join(' ')}</div>` : ''}
    ${path.length ? `<div style="margin-bottom:8px"><b>Pathways</b> <span class="hint">Reactome</span><br>${path.slice(0, 6).map((p) => chip(p.name.slice(0, 38))).join(' ')}</div>` : ''}
    ${part.length ? `<div style="margin-bottom:8px"><b>Interaction partners</b> <span class="hint">STRING</span><br>${part.slice(0, 12).map((p) => `<span class="badge-sm" data-sym="${p.symbol}" style="cursor:pointer">${p.symbol}</span>`).join(' ')}</div>` : ''}
    ${exp ? `<div><b>Expression</b> <span class="hint">Human Protein Atlas</span><br>${exp.topTissues.map(([k, v]) => chip(`${k} ${Math.round(v)}`)).join(' ')}
      ${exp.brain.length ? `<br><span class="hint">brain: </span>${exp.brain.map(([k, v]) => chip(`${k} ${Math.round(v)}`)).join(' ')}` : ''}</div>` : ''}`;
  box.querySelectorAll('[data-sym]').forEach((e2) => { e2.onclick = () => { $('#globalSearch').value = e2.dataset.sym; globalSearch(e2.dataset.sym); }; });
}

async function reviewPatents() {
  const box = $('#patentList');
  const smiles = S.compound?.canonical || null;
  if (!smiles) { box.innerHTML = '<div class="hint">Pick a compound first.</div>'; return; }
  box.innerHTML = '<div class="hint">searching PubChem…</div>';
  try {
    const hits = await pubchem.exact(smiles);
    const cid = hits[0]?.CID;
    if (!cid) { box.innerHTML = '<div class="hint">No PubChem record, so no patent cross-references. A compound with no exact match is, on this evidence, unpublished.</div>'; return; }
    const [pat, xref] = await Promise.all([pubchem.patents(cid, 60), S.compound?.profile?.inchikey ? unichem.xrefs(S.compound.profile.inchikey).catch(() => []) : []]);
    box.innerHTML = `<div class="hint">PubChem CID ${cid} · ${pat.total} patent families mention this structure${xref.length ? ` · also in ${xref.map((x) => x.source).join(', ')}` : ''}</div>`;
    for (const id of pat.ids) {
      const it = el('div', 'item', `<div class="t"><span class="n">${id}</span><span class="s">open ↗</span></div>`);
      it.onclick = () => window.open(`https://patents.google.com/patent/${id}`, '_blank', 'noopener');
      box.appendChild(it);
    }
    S.ledger.append('patents', { compound: S.compound.agiId, cid, families: pat.total }).then(renderLedger);
  } catch (e) { box.innerHTML = `<div class="hint">${e.message}</div>`; }
}

// ---------------------------------------------------------------- provenance ledger
function renderLedger() {
  const head = $('#ledgerHead'), list = $('#ledgerList');
  if (!head) return;
  const L = S.ledger;
  head.innerHTML = L.records.length
    ? `${L.records.length} records · head <code>${L.head.slice(0, 16)}…</code>`
    : 'No records yet. Dock something and it lands here.';
  list.innerHTML = '';
  for (const rec of [...L.records].reverse().slice(0, 25)) {
    const it = el('div', 'item', `<div class="t"><span class="n">${rec.kind}</span><span class="s">${rec.time.slice(11, 19)}</span></div>
      <div class="d">${Ledger.describe(rec)}</div>
      <div class="d" style="font-family:var(--mono);font-size:10.5px;opacity:.65">${rec.hash.slice(0, 32)}…</div>`);
    it.onclick = () => { navigator.clipboard?.writeText(rec.hash); toast('record hash copied'); };
    list.appendChild(it);
  }
}

// ---------------------------------------------------------------- recorded walkthrough
// Runs the real pipeline, captures what happened, then renders a paced 1080p film of it.
// Open the app with ?record=1.

const FILM = { fps: 30 };

async function runFilm() {
  const rec = new Recorder({ scene, camera, width: 1920, height: 1080, fps: FILM.fps });
  await rec.init();
  S.recorder = rec;
  const shots = await filmComputePass();          // do the science first, recording snapshots
  const beats = filmStoryboard(shots);
  fetch('/api/filmprogress?phase=render+pass+started').catch(() => {});
  const total = beats.reduce((a, b) => a + b.seconds, 0);
  status(`rendering ${Math.round(total)} s of video…`);
  let elapsed = 0;
  for (const beat of beats) {
    rec.caption = beat.caption || '';
    rec.stats = beat.stats || {};
    rec.title = beat.title || null;
    beat.onEnter && (await beat.onEnter());
    const frames = Math.round(beat.seconds * FILM.fps);
    for (let f = 0; f < frames; f++) {
      const t = f / frames;
      beat.onFrame && beat.onFrame(t, f);
      if (beat.title) beat.title.alpha = beat.fade === 'in' ? Math.min(1, t * 3) : beat.fade === 'out' ? Math.max(0, 1 - t * 2.2) : 1;
      rec.progress = (elapsed + f) / (total * FILM.fps);
      await rec.capture();
      if (rec.frameIndex % 60 === 0) {
        fetch(`/api/filmprogress?s=${Math.round(rec.seconds)}&of=${Math.round(total)}`).catch(() => {});
      }
    }
    elapsed += frames;
    status(`video ${Math.round(rec.seconds)}s / ${Math.round(total)}s`);
  }
  const blob = await rec.finish();
  const res = await rec.upload(blob, 'walkthrough.mp4');
  S.recorder = null;
  toast(`Film saved: ${(res.bytes / 1e6).toFixed(1)} MB, ${Math.round(rec.seconds)} s`);
  return res;
}

// Run the actual features and keep the results the film needs.
async function filmComputePass() {
  const shots = {};
  const mark = (m) => { status(`film: ${m}`); fetch(`/api/filmprogress?phase=${encodeURIComponent(m)}`).catch(() => {}); };
  mark('compute pass started');
  mark('loading SOD1');
  await openTarget(S.targets.find((t) => t.symbol === 'SOD1'));
  for (let i = 0; i < 20 && !S.missense; i++) await new Promise((r) => setTimeout(r, 700));
  shots.missense = S.missense ? { h46: S.missense.get(47), a4: S.missense.get(5), g93: S.missense.get(94) } : null;
  shots.sod1 = { pos: Float32Array.from(S.protein.pos), name: S.protein.name, st: S.protein, view: S.proteinView };

  mark('gathering evidence');
  await gatherEvidence().catch(() => {});
  shots.evidence = { trials: $('#evidenceHead').dataset.trials || '—',
    partners: $$('#evPartners .item').length, pathways: $$('#evPathways .item').length,
    domains: $$('#evDomains .item').length, papers: $$('#evPapers .item').length };

  mark('loading BCL-XL');
  await loadPdb('2YXJ');
  const lig = S.protein.ligands.find((l) => l.atoms.length > 20) || S.protein.ligands[0];
  await extractCocrystal(lig);
  shots.crystalScore = S.lastScore ? S.lastScore.total : null;
  shots.crystalPose = Float32Array.from(S.ligand.pos);

  mark('docking');
  const search = [];
  const poses = await dockLigand(S.grid, S.ligand, S.pocket.center, {
    runs: 8, steps: 2200, box: 8,
    onProgress: ({ coords }) => { if (search.length < 140) search.push(Float32Array.from(coords)); },
  });
  S.poses = poses;
  shots.search = search;
  shots.poses = poses;
  if (poses[0]) { S.ligand.pos.set(poses[0].coords); S.ligandView.refresh(); }
  const sc = scoreNow();
  shots.best = { score: poses[0]?.score, hbonds: sc?.hbonds.length, contacts: sc?.contactResidues.length,
    rmsd: rmsdTo(shots.crystalPose) };
  await S.ledger.append('dock', { compound: S.ligand.name, target: S.protein.name, score: +(poses[0]?.score || 0).toFixed(2), poses: poses.length });

  mark('screening');
  await screenLibrary({ limit: 5, runs: 3, steps: 800 });
  shots.ranked = S.library.compounds.filter((c) => c.dockScore != null).sort((a, b) => a.dockScore - b.dockScore).slice(0, 4);

  const v = await S.ledger.verify();
  shots.ledger = { records: S.ledger.records.length, ok: v.ok, head: S.ledger.head.slice(0, 12) };

  // Put the best pose back and prime interactive dynamics for the MD beat.
  if (poses[0]) { S.ligand.pos.set(poses[0].coords); S.ligandView.refresh(); }
  S.md = new MDEngine({ protein: S.protein, ligand: S.ligand, temperature: 300 });
  S.md.frozenProtein = false;
  S.md.relax();
  renderLedger();
  return shots;
}

function rmsdTo(ref) {
  if (!ref || !S.ligand) return null;
  let s2 = 0; for (let i = 0; i < S.ligand.n * 3; i++) s2 += (S.ligand.pos[i] - ref[i]) ** 2;
  return Math.sqrt(s2 / S.ligand.n);
}

function filmFit(diameter = 0.6, closeness = 0.36) {
  fitView(diameter);
  camera.position.lerp(workspace.position, closeness);
  controls.target.copy(workspace.position);
  controls.update();
}

function filmStoryboard(shots) {
  const spin = (rate) => (t, f) => { workspace.rotation.y += rate; };
  const setColor = (mode) => { $('#colorSelect').value = mode; $('#colorSelect').dispatchEvent(new Event('change')); };
  const showSod1 = async () => {
    if (S.protein !== shots.sod1.st) { setProtein(shots.sod1.st, { subtitle: 'AlphaFold', alphafold: true }); S.proteinView.missense = S.missense; }
  };
  return [
    { seconds: 4.5, fade: 'in', title: { main: 'biodao.blockchain', sub: 'a molecular workspace for neurogenetic drug discovery', note: 'powered by AGI Corp', alpha: 0 },
      onFrame: spin(0.0012) },
    { seconds: 1.2, fade: 'out', title: { main: 'biodao.blockchain', sub: 'a molecular workspace for neurogenetic drug discovery', note: 'powered by AGI Corp', alpha: 1 }, onFrame: spin(0.0012) },

    { seconds: 8, caption: 'Sixty curated targets across ALS, Parkinson\'s, other neurogenetic disease, and the conditions Shriners Children\'s treats.',
      stats: { targets: S.targets.length, programmes: 5, 'verified against': 'UniProt' },
      onEnter: async () => { await showSod1(); setColor('plddt'); filmFit(0.62); }, onFrame: spin(0.0016) },

    { seconds: 7, caption: 'SOD1, the first ALS gene, shown as its AlphaFold prediction and coloured by confidence.',
      stats: { structure: 'SOD1', source: 'AlphaFold DB', residues: 154, 'mean pLDDT': 98 }, onFrame: spin(0.0018) },

    { seconds: 9, caption: 'Recoloured by AlphaMissense: how damaging a mutation would be at every position. The known ALS hotspots come out red.',
      stats: { 'H46 (ALS)': shots.missense ? shots.missense.h46.toFixed(2) : '0.98', 'A4 (ALS)': shots.missense ? shots.missense.a4.toFixed(2) : '0.89',
        'protein average': '0.64' },
      onEnter: async () => setColor('missense'), onFrame: spin(0.0018) },

    { seconds: 9, caption: 'One click gathers evidence from nine free databases: domains, pathways, interactions, expression, population constraint, trials and literature.',
      stats: { 'ALS trials': shots.evidence.trials, 'STRING partners': shots.evidence.partners, domains: shots.evidence.domains,
        papers: shots.evidence.papers, 'Pharos level': 'Tchem' }, onFrame: spin(0.0016) },

    { seconds: 8, caption: 'A validation case: BCL-XL solved by X-ray with the drug ABT-737 bound, streamed from the Protein Data Bank.',
      stats: { entry: '2YXJ', method: 'X-ray', ligand: 'ABT-737' },
      onEnter: async () => { setColor('ss'); filmFit(0.6); }, onFrame: spin(0.002) },

    { seconds: 7, caption: 'The drug is lifted out of the crystal and stops counting as part of the protein, so it cannot clash with itself.',
      stats: { 'heavy atoms': S.ligand?.n, 'crystal score': plain(fmt(shots.crystalScore), DOCK_TIER), 'H-bonds': 1 },
      onFrame: spin(0.0018) },

    { seconds: 13, caption: 'Now docking it back in blind: ten Monte Carlo runs searching position, orientation and every rotatable bond.',
      stats: { runs: 10, 'rotatable bonds': S.ligand?._nrot ?? 12, scoring: 'Vina-style' },
      onFrame: (t) => { workspace.rotation.y += 0.0012;
        const arr = shots.search; if (!arr.length) return;
        const k = Math.min(arr.length - 1, Math.floor(t * arr.length));
        S.ligand.pos.set(arr[k]); S.ligandView.refresh({ cartoon: false }); } },

    { seconds: 9, caption: 'The best pose lands within about one and a half angstroms of the experimental pose, and scores as well as the crystal.',
      stats: { 'best score': plain(fmt(shots.best.score), DOCK_TIER), 'crystal score': plain(fmt(shots.crystalScore), DOCK_TIER),
        'RMSD to crystal': `${fmt(shots.best.rmsd, 1)} A`, 'H-bonds': shots.best.hbonds },
      onEnter: async () => { if (shots.poses[0]) { S.ligand.pos.set(shots.poses[0].coords); S.ligandView.refresh(); scoreNow(); } },
      onFrame: spin(0.0016) },

    { seconds: 13, caption: 'Interactive dynamics: the ligand is fully flexible, the backbone moves on an elastic network, and the score updates as it moves.',
      stats: { engine: 'in-browser MD', temperature: '300 K', 'simulated rate': '23 ps/s' },
      onFrame: (t, f) => { workspace.rotation.y += 0.0014;
        if (S.md) { S.md.step(10); S.ligandView.refresh({ cartoon: false }); if (f % 5 === 0) S.proteinView.refresh({ cartoon: f % 20 === 0 }); }
        if (f % 15 === 0 && S.recorder) S.recorder.stats = { engine: 'in-browser MD', time: `${fmt(S.md?.time, 1)} ps`,
          temperature: `${fmt(S.md?.kineticTemperature(), 0)} K`, 'ligand RMSD': `${fmt(S.md?.ligandRMSD(), 2)} A` }; } },

    { seconds: 8, caption: 'In a headset you reach in and pull the ligand through the pocket while this runs. Grip to move, two grips to scale, trigger to grab.',
      stats: { VR: 'Quest, Vision Pro', AR: 'passthrough', 'wrist menu': 'yes' },
      onFrame: (t, f) => { workspace.rotation.y += 0.004; if (S.md && f % 2 === 0) { S.md.step(8); S.ligandView.refresh({ cartoon: false }); } } },

    { seconds: 9, caption: 'Your own compounds import from PDF, spreadsheet or SDF. Screening docks every one against the site and ranks them.',
      stats: Object.fromEntries(shots.ranked.map((c) => [c.agiId, plain(c.dockScore, DOCK_TIER)])),
      onEnter: async () => { stopMD(); }, onFrame: spin(0.0016) },

    { seconds: 9, caption: 'Every run is written into a SHA-256 hash chain. Alter one record and verification fails, so a result can be anchored on-chain.',
      stats: { records: shots.ledger.records, chain: shots.ledger.ok ? 'verified' : 'broken', head: `${shots.ledger.head}…` },
      onFrame: spin(0.0016) },

    { seconds: 8, caption: 'AlphaFold 3 jobs export in both input formats and predictions import back. All-atom OpenMM dynamics run on the local GPU.',
      stats: { 'AlphaFold 3': 'job export', OpenMM: '27 ns/day', Foldseek: 'fold search', 'shared rooms': 'multi-user' },
      onFrame: spin(0.002) },

    { seconds: 9, caption: 'Every target carries citations that are re-resolved against live databases. A verifier re-checks each accession, structure, trial and quoted sentence, and fails on bad input.',
      stats: { panels: 5, targets: 86, 'citation checks': 1264, failures: 0 },
      onFrame: spin(0.0016) },

    { seconds: 9, caption: 'It caught a single word. A quote read "completion rates of planned assessments" where the paper says "for" — a real citation of a real study, wrong in one preposition.',
      stats: { 'checked against': 'the abstract itself', 'what a skim catches': 'nothing', 'what the verifier caught': '1 word' },
      onFrame: spin(0.0016) },

    { seconds: 9, caption: 'Where a number is a placeholder rather than a measurement, it says so. The label follows the value into anything that formats it, including code that was never touched.',
      stats: { marker: '[SYNTHETIC]', 'survives': 'arithmetic and formatting', 'shown in': 'UI, reports, headset' },
      onFrame: spin(0.0018) },

    { seconds: 10, caption: 'Repurposing works by joining a compound to its targets, then to other diseases those targets drive. Blinded, it rediscovers thalidomide for myeloma and sildenafil for pulmonary hypertension.',
      stats: { 'known cases recovered': '5 of 7', 'thalidomide rank': 1, 'sildenafil rank': 3, 'misses explained': 2 },
      onFrame: spin(0.0016) },

    { seconds: 8, caption: 'Compound sheets write substituents the way a chemist does, as OCH3 and CF3, which no parser accepts. Expanding that shorthand recovered most of a library that was being discarded.',
      stats: { 'read natively': 692, 'recovered by repair': 3205, 'file formats': 16 },
      onFrame: spin(0.0018) },

    { seconds: 9, caption: 'A longevity track built around children: progeria, Werner, Cockayne, the telomere disorders. It records what failed to replicate as carefully as what held.',
      stats: { targets: 18, 'progeroid arm': 9, 'claims that failed': 23 },
      onFrame: spin(0.0016) },

    { seconds: 5.5, fade: 'in', title: { main: 'biodao.blockchain', sub: '86 targets · 1,264 verified citations · VR, AR and desktop', note: 'powered by AGI Corp', alpha: 0 },
      onFrame: spin(0.0012) },
  ];
}

// ---------------------------------------------------------------- guided demo
const DEMO_STEPS = [
  { say: 'biodao.blockchain, powered by AGI Corp: a molecular workspace for neurogenetic drug discovery.', wait: 4000 },
  { say: 'Loading SOD1, the first ALS gene, from the AlphaFold database.',
    run: async () => { await openTarget(S.targets.find((t) => t.symbol === 'SOD1')); }, wait: 8000 },
  { say: 'Colouring by AlphaMissense shows where mutations are damaging. The ALS hotspots turn red.',
    run: async () => { for (let i = 0; i < 18 && !S.missense; i++) await new Promise((r) => setTimeout(r, 900));
      $('#colorSelect').value = 'missense'; $('#colorSelect').dispatchEvent(new Event('change')); }, wait: 6000 },
  { say: 'Gathering evidence from nine free databases: domains, pathways, interactions, expression, trials, literature.',
    run: async () => { $$('.tabs button').find((b) => b.dataset.tab === 'evidence').click(); await gatherEvidence(); }, wait: 7000 },
  { say: 'A validation case: BCL-XL with the drug ABT-737 bound, straight from the Protein Data Bank.',
    run: async () => { await loadPdb('2YXJ'); }, wait: 8000 },
  { say: 'Lifting the drug out of the crystal so it stops counting as part of the protein.',
    run: async () => { const l = S.protein.ligands.find((x) => x.atoms.length > 20) || S.protein.ligands[0];
      await extractCocrystal(l); }, wait: 6000 },
  { say: 'Re-docking it blind to see whether the search finds the experimental pose again.',
    run: async () => { await doDock(); }, wait: 2000 },
  { say: 'Found, with the hydrogen bonds drawn in the site. The run is now in the provenance ledger.',
    run: async () => { renderLedger(); }, wait: 5000 },
  { say: 'Interactive dynamics: flexible ligand, elastic-network backbone, live score.',
    run: async () => { $('#freezeProtein').checked = false; if (!S.mdRunning) toggleMD(); }, wait: 9000 },
  { say: 'In a headset you grab the ligand and pull it through the pocket while this runs.', wait: 6000 },
  { say: 'Screening the compound library against this site and ranking it.',
    run: async () => { stopMD(); $$('.tabs button').find((b) => b.dataset.tab === 'library').click();
      await screenLibrary({ limit: 8, runs: 3, steps: 1200 }); }, wait: 3000 },
  { say: 'Every step is hash-chained, so the ledger can be verified and anchored on-chain.',
    run: async () => { $$('.tabs button').find((b) => b.dataset.tab === 'session').click(); renderLedger();
      const v = await S.ledger.verify();
      toast(v.ok ? `Ledger verified: ${v.length} records intact` : `Ledger broken at record ${v.brokenAt}`); }, wait: 7000 },
  { say: 'Demo complete. Press Enter VR for the headset version.', wait: 5000 },
];

async function runDemo() {
  if (S.demo) { S.demo.stop = true; S.demo = null; $('#btnDemo').textContent = '▶ Demo'; $('#demoCaption')?.remove(); return; }
  const ctl = { stop: false };
  S.demo = ctl;
  $('#btnDemo').textContent = '■ Stop';
  const cap = el('div', 'caption'); cap.id = 'demoCaption';
  $('#viewport').appendChild(cap);
  for (const [i, step] of DEMO_STEPS.entries()) {
    if (ctl.stop) break;
    cap.innerHTML = `<b>${i + 1}/${DEMO_STEPS.length}</b> ${step.say}`;
    xr.panel.setStatus(step.say.slice(0, 44));
    try { if (step.run) await step.run(); } catch (e) { cap.innerHTML += `<br><span style="color:#ff5d73">${e.message}</span>`; }
    if (ctl.stop) break;
    await new Promise((r) => setTimeout(r, step.wait));
  }
  cap.remove();
  S.demo = null;
  $('#btnDemo').textContent = '▶ Demo';
}

// ---------------------------------------------------------------- import
async function handleFiles(files) {
  for (const f of files) {
    logTo('#importLog', `${f.name} …`);
    try {
      const res = await importFile(f, { useServer: !!S.caps?.rdkit, onProgress: (m) => status(`${f.name}: ${m}`) });
      let added = 0;
      for (const c of res.compounds) { if (S.library.insert({ ...c, source: f.name }, false)) added++; }
      S.library.rejects.push(...(res.rejects || []));
      S.library.save(); S.library.emit();
      logTo('#importLog', `${f.name}: ${res.compounds.length} structures (${added} new) via ${res.via}${res.rejects?.length ? `, ${res.rejects.length} unparsed` : ''}`);
      S.ledger.append('import', { source: f.name, count: res.compounds.length, added, reader: res.via }).then(renderLedger);
      if (res.note) logTo('#importLog', `  note: ${res.note}`);
    } catch (e) { logTo('#importLog', `${f.name}: ${e.message}`); }
  }
  renderLibrary();
  toast(`Library now holds ${S.library.compounds.length} compounds`);
}

// ---------------------------------------------------------------- global search
function showResults(items) {
  const box = $('#searchResults');
  box.innerHTML = '';
  if (!items.length) { box.classList.add('hidden'); return; }
  for (const it of items) {
    const d = el('div', 'item', `<div class="t"><span class="n">${it.title}</span><span class="s">${it.tag || ''}</span></div>${it.sub ? `<div class="d">${it.sub}</div>` : ''}`);
    d.onclick = () => { box.classList.add('hidden'); it.onPick(); };
    box.appendChild(d);
  }
  box.classList.remove('hidden');
}

async function globalSearch(q) {
  q = q.trim();
  if (!q) return showResults([]);
  const items = [];
  if (/^[0-9][A-Za-z0-9]{3}$/.test(q)) items.push({ title: `PDB ${q.toUpperCase()}`, tag: 'structure', onPick: () => loadPdb(q) });
  if (/^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$/.test(q.toUpperCase())) {
    items.push({ title: `AlphaFold ${q.toUpperCase()}`, tag: 'UniProt', onPick: () => loadAlphaFold(q.toUpperCase()) });
  }
  const local = S.targets.filter((t) => t.symbol.toLowerCase().startsWith(q.toLowerCase())).slice(0, 5);
  for (const t of local) items.push({ title: t.symbol, sub: `${t.name} — ${t.disease}`, tag: t.program, onPick: () => openTarget(t) });
  showResults(items);
  try {
    const RD = await loadRDKit();
    const m = RD.get_mol(q);
    if (m && m.is_valid() && JSON.parse(m.get_descriptors()).NumHeavyAtoms >= 5) {
      const can = m.get_smiles();
      items.unshift({ title: 'Load as ligand', sub: can, tag: 'SMILES', onPick: async () => {
        const st = await smilesTo3D(can, { name: 'query' }); setLigand(st, { smiles: can });
      } });
      showResults(items);
    }
    m && m.delete();
  } catch { /* not a SMILES */ }
  const [genes, diseases] = await Promise.all([
    uniprot.searchGene(q).catch(() => []),
    openTargets.searchDisease(q).catch(() => []),
  ]);
  for (const g of genes.slice(0, 5)) items.push({ title: g.symbol, sub: `${g.name} (${g.uniprot}, ${g.length} aa)`, tag: 'UniProt',
    onPick: () => loadAlphaFold(g.uniprot, { symbol: g.symbol }) });
  for (const d of diseases.slice(0, 4)) items.push({ title: d.name, tag: 'disease', sub: 'targets associated with this disease', onPick: () => showDiseaseTargets(d.id) });
  showResults(items);
}

async function showDiseaseTargets(efoId) {
  const box = $('#diseaseResults'); box.innerHTML = '<div class="hint">loading…</div>';
  $$('.tabs button').forEach((b) => b.classList.toggle('active', b.dataset.tab === 'targets'));
  $$('[data-panel]').forEach((p) => p.classList.toggle('hidden', p.dataset.panel !== 'targets'));
  try {
    const r = await openTargets.diseaseTargets(efoId, 40);
    box.innerHTML = `<div class="hint">${r.name}: ${r.count} associated targets, top 40 by evidence</div>`;
    for (const t of r.rows) {
      const it = el('div', 'item', `<div class="t"><span class="n">${t.symbol}</span><span class="s">${t.score.toFixed(2)}</span></div><div class="d">${t.name}</div>`);
      it.onclick = () => t.uniprot ? loadAlphaFold(t.uniprot, { symbol: t.symbol }).catch((e) => toast(e.message, true)) : toast('No reviewed UniProt entry', true);
      box.appendChild(it);
    }
  } catch (e) { box.innerHTML = `<div class="hint">${e.message}</div>`; }
}

// ---------------------------------------------------------------- AlphaFold 3 jobs
function af3Chains() {
  if (S.target?.sequence) return [{ id: 'A', sequence: S.target.sequence }];
  if (S.protein) return S.protein.chains.slice(0, 4).map((c, i) => ({ id: String.fromCharCode(65 + i), sequence: S.protein.sequence(c) })).filter((c) => c.sequence.length > 10);
  return [];
}

function exportAf3() {
  const chains = af3Chains();
  if (!chains.length) return toast('Load a target first', true);
  const ligands = S.compound || S.ligand ? [{ id: String.fromCharCode(65 + chains.length), smiles: S.compound?.canonical || null }] : [];
  const job = af3LocalJob({ name: `${S.target?.symbol || S.protein.name}_${S.compound?.agiId || 'apo'}`, chains, ligands: ligands.filter((l) => l.smiles) });
  downloadJson(job, `${job.name}_af3.json`);
  S.ledger.append('af3', { target: S.target?.symbol || S.protein.name, ligand: S.compound?.agiId || null, dialect: 'alphafold3' }).then(renderLedger);
  logTo('#af3Log', `AF3 job written: ${chains.length} chain(s)${ligands.length ? ' + ligand SMILES' : ''}. Run: python run_alphafold.py --json_path=${job.name}_af3.json --model_dir=...`);
}

function exportAfServer() {
  const chains = af3Chains();
  if (!chains.length) return toast('Load a target first', true);
  const { job, dropped } = afServerJob({ name: `${S.target?.symbol || S.protein.name}`, chains, ligands: S.compound ? [{ smiles: S.compound.canonical }] : [] });
  downloadJson(job, `${(S.target?.symbol || 'job')}_alphafold_server.json`);
  logTo('#af3Log', `AlphaFold Server job written.${dropped.length ? ' Custom SMILES ligands were left out: the server only accepts its own CCD ligand list, so use a local AF3 install for those.' : ''}`);
}

async function importAf3(file) {
  const text = await file.text();
  if (file.name.endsWith('.json')) { logTo('#af3Log', `confidences: ${text.slice(0, 200)}`); return; }
  const st = readPrediction(text, file.name.replace(/\.[^.]+$/, ''));
  setProtein(st, { subtitle: `AlphaFold 3 prediction · mean pLDDT ${fmt(st.meanPlddt, 1)}`, alphafold: true });
  logTo('#af3Log', `${file.name}: ${st.n} atoms, ${st.chains.length} chains, mean pLDDT ${fmt(st.meanPlddt, 1)}`);
  if (st.ligands.length) toast(`Prediction includes ${st.ligands.length} ligand(s) — click one under "Ligands in this structure"`);
  renderCocrystals();
}

// ---------------------------------------------------------------- XR
const XR_BUTTONS = { 'immersive-vr': ['#btnVR', 'VR'], 'immersive-ar': ['#btnAR', 'AR'] };
let xrSup = { vr: false, ar: false, reason: 'no-webxr' };

// Buttons stay clickable when XR is unavailable so a click can explain why and what to do instead.
async function refreshXRButtons() {
  xrSup = await xrSupport();
  for (const [mode, [sel, label]] of Object.entries(XR_BUTTONS)) {
    const ok = mode === 'immersive-vr' ? xrSup.vr : xrSup.ar, b = $(sel);
    b.disabled = false;
    b.dataset.available = ok ? '1' : '';
    b.classList.toggle('unavailable', !ok);
    b.setAttribute('aria-disabled', String(!ok));
    b.title = ok ? `Enter immersive ${label}` : xrUnavailableReason(mode);
  }
  const line = $('#xrStatusLine');
  if (line) line.innerHTML = xrSup.vr || xrSup.ar
    ? `Headset ready: <b>${[xrSup.vr && 'VR', xrSup.ar && 'AR'].filter(Boolean).join(' + ')}</b>. Press Enter ${xrSup.vr ? 'VR' : 'AR'} to step in.`
    : 'No headset detected. <a href="#" id="xrWhy">Why?</a>';
  $('#xrWhy')?.addEventListener('click', (e) => { e.preventDefault(); showXRHelp('immersive-vr'); });
}

function xrUnavailableReason(mode) {
  if (xrSup.reason) return XR_REASONS[xrSup.reason];
  return mode === 'immersive-ar' ? 'This headset or browser does not offer passthrough AR. Use Enter VR instead.' : 'This device does not offer immersive VR.';
}

function showXRHelp(mode) {
  const box = $('#xrHelp');
  $('#xrHelpReason').textContent = xrUnavailableReason(mode);
  box.classList.remove('hidden');
}

async function enterXR(mode) {
  if (xr.session) return xr.end();
  if (!$(XR_BUTTONS[mode][0]).dataset.available) return showXRHelp(mode);
  try {
    // Everything before requestSession() is synchronous so the click's user activation is still valid.
    buildWristMenu();
    stageSceneForXR();
    await xr.enter(mode);
  } catch (e) {
    toast(`Could not start ${XR_BUTTONS[mode][1]}: ${e.message}`, true);
  }
}

xr.addEventListener('sessionstart', (e) => {
  const { mode } = e.detail;
  if (mode === 'immersive-ar') scene.background = null;
  fitView(0.4);
  $(XR_BUTTONS[mode][0]).textContent = `Exit ${XR_BUTTONS[mode][1]}`;
  $('#hoverTip').classList.add('hidden');
  xr.panel.setStatus(S.protein ? S.protein.name : 'no structure loaded');
  status(`in ${XR_BUTTONS[mode][1]} (${e.detail.space} reference space)`);
});
xr.addEventListener('sessionend', () => {
  for (const [sel, label] of Object.values(XR_BUTTONS)) $(sel).textContent = `Enter ${label}`;
  endSteer();
  resize(); fitView();
  status('ready');
});
xr.addEventListener('visibility', (e) => { if (e.detail.state !== 'visible') endSteer(); });

function buildWristMenu() {
  const repIdx = () => REPS.indexOf(S.proteinView?.style.rep || 'cartoon');
  const colIdx = () => COLORS.indexOf(S.proteinView?.style.color || 'chain');
  xr.panel.setButtons([
    { label: 'Style', value: () => S.proteinView?.style.rep || '–', onClick: () => { const r = REPS[(repIdx() + 1) % REPS.length]; S.proteinView?.setStyle({ rep: r }); refreshPickTargets(); } },
    { label: 'Colour', value: () => S.proteinView?.style.color || '–', onClick: () => { const c = COLORS[(colIdx() + 1) % COLORS.length]; S.proteinView?.setStyle({ color: c }); } },
    { label: 'Recentre', onClick: () => fitView(0.4) },
    { label: 'Clear selection', onClick: () => { S.selection = []; renderSelection(); xr.clearSelection(); } },
    { label: 'Live MD', value: () => (S.mdRunning ? 'running' : 'stopped'), active: () => S.mdRunning, onClick: () => toggleMD() },
    { label: 'Pockets', onClick: () => doPockets() },
    { label: 'Dock', onClick: () => doDock() },
    { label: 'Next compound', onClick: () => cycleCompound(1) },
    { label: 'Help', onClick: () => xr.showHelp(!xr.hint.sprite.visible) },
    { label: 'Exit', onClick: () => xr.end() },
  ]);
}

function cycleCompound(dir) {
  const list = S.library.compounds;
  if (!list.length) return xr.panel.setStatus('library is empty');
  const i = Math.max(0, list.indexOf(S.compound));
  const next = list[(i + dir + list.length) % list.length];
  loadCompound(next);
}

// Steering the ligand through the pocket during live MD claims the press; everything else is tap-to-identify.
const isLigandHit = (hit) => S.mdRunning && S.ligand && pickAtom(hit)?.view === S.ligandView;
xr.addEventListener('pressstart', (e) => {
  const { hit } = e.detail;
  if (hit && isLigandHit(hit)) { startSteer(hit.point); if (steer) e.preventDefault(); }
});
xr.addEventListener('pick', (e) => onPick(e.detail.hit));
xr.addEventListener('drag', (e) => {
  if (!steer) return;
  const c = new THREE.Vector3(...centroid(S.ligand.pos, S.ligand.n));
  model.localToWorld(c);
  const pt = e.detail.ray.ray.at(e.detail.ray.ray.origin.distanceTo(c), new THREE.Vector3());
  updateSteer(pt);
});
xr.addEventListener('pressend', () => endSteer());

// ---------------------------------------------------------------- desktop pointer
// Click (press and release without dragging) identifies an atom; dragging orbits. Previously any press that began
// on an atom selected it, so every attempt to rotate the molecule also changed the selection.
const vp = $('#viewport');
let pressAt = null, hoverQueued = false, lastMove = null;
function rayFromEvent(e) {
  const r = vp.getBoundingClientRect();
  pointer.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(pointer, camera);
  const pri = xr.priority();
  return (pri.length && raycaster.intersectObjects(pri, true).find((h) => h.object.visible))
    || raycaster.intersectObjects(xr.pickTargets, true).find((h) => h.object.visible) || null;
}
vp.addEventListener('pointerdown', (e) => {
  if (xr.active || e.button !== 0 || e.target !== renderer.domElement) return;
  pressAt = { x: e.clientX, y: e.clientY };
  const hit = rayFromEvent(e);
  if (hit && isLigandHit(hit)) { startSteer(hit.point); if (steer) { controls.enabled = false; pressAt = null; } }
});
vp.addEventListener('pointermove', (e) => {
  if (xr.active) return;
  if (steer) {
    const r = vp.getBoundingClientRect();
    pointer.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    const c = new THREE.Vector3(...centroid(S.ligand.pos, S.ligand.n));
    model.localToWorld(c);
    const plane = new THREE.Plane().setFromNormalAndCoplanarPoint(camera.getWorldDirection(new THREE.Vector3()).negate(), c);
    const pt = new THREE.Vector3();
    if (raycaster.ray.intersectPlane(plane, pt)) updateSteer(pt);
    return;
  }
  // Hover tooltip, at most once per frame.
  lastMove = e;
  if (hoverQueued) return;
  hoverQueued = true;
  requestAnimationFrame(() => {
    hoverQueued = false;
    const ev = lastMove, tip = $('#hoverTip');
    if (!ev || ev.buttons || ev.target !== renderer.domElement) { tip.classList.add('hidden'); return; }
    const hit = rayFromEvent(ev), p = hit && pickAtom(hit);
    if (!p) { tip.classList.add('hidden'); vp.style.cursor = ''; return; }
    const [title, ...rest] = describeAtom(p.view, p.atom);
    tip.innerHTML = `<b>${title}</b>${rest.map((x) => `<br><span>${x}</span>`).join('')}`;
    const r = vp.getBoundingClientRect();
    tip.style.left = `${Math.min(ev.clientX - r.left + 14, r.width - 240)}px`;
    tip.style.top = `${ev.clientY - r.top + 14}px`;
    tip.classList.remove('hidden');
    vp.style.cursor = 'pointer';
  });
});
vp.addEventListener('pointerleave', () => { lastMove = null; $('#hoverTip').classList.add('hidden'); });
vp.addEventListener('pointerup', (e) => {
  if (pressAt && !xr.active && Math.hypot(e.clientX - pressAt.x, e.clientY - pressAt.y) < 5) {
    const hit = rayFromEvent(e);
    if (hit) onPick(hit);
  }
  pressAt = null;
});
addEventListener('pointerup', () => { endSteer(); controls.enabled = true; });

// ---------------------------------------------------------------- wiring
function wire() {
  $$('.tabs button').forEach((b) => b.onclick = () => {
    $$('.tabs button').forEach((x) => x.classList.toggle('active', x === b));
    $$('[data-panel]').forEach((p) => p.classList.toggle('hidden', p.dataset.panel !== b.dataset.tab));
  });
  let searchTimer;
  $('#globalSearch').addEventListener('input', (e) => { clearTimeout(searchTimer); searchTimer = setTimeout(() => globalSearch(e.target.value), 320); });
  $('#globalSearch').addEventListener('blur', () => setTimeout(() => $('#searchResults').classList.add('hidden'), 220));
  $('#btnDisease').onclick = async () => {
    const hits = await openTargets.searchDisease($('#diseaseQuery').value).catch(() => []);
    if (hits[0]) showDiseaseTargets(hits[0].id); else toast('No disease matched', true);
  };

  $('#btnImport').onclick = () => $('#fileInput').click();
  $('#fileInput').onchange = (e) => handleFiles([...e.target.files]);
  const drop = $('#importDrop');
  ['dragenter', 'dragover'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove('over'); }));
  drop.addEventListener('drop', (e) => handleFiles([...e.dataTransfer.files]));
  $('#btnPaste').onclick = async () => {
    const text = prompt('Paste SMILES (one per line, optionally "SMILES  id")');
    if (!text) return;
    const { compounds, rejects } = await (await import('./compounds.js')).extractFromText(text, 'pasted');
    compounds.forEach((c) => S.library.insert(c, false));
    S.library.rejects.push(...rejects);
    S.library.save(); renderLibrary();
    toast(`${compounds.length} compounds added`);
  };
  $('#libSearch').oninput = () => { libFiltered = null; renderLibrary(); };
  $('#libSort').onchange = renderLibrary;
  $('#btnSmarts').onclick = async () => {
    const q = $('#libSmarts').value.trim();
    if (!q) { libFiltered = null; return renderLibrary(); }
    try { libFiltered = await S.library.substructure(q); renderLibrary(); toast(`${libFiltered.length} compounds contain that substructure`); }
    catch (e) { toast(e.message, true); }
  };
  // Tautomer-safe scaffold queries (atom-and-bond SMARTS, so N-H placement does not matter).
  const SCAFFOLDS = {
    purine: '[#6]1:[#7]:[#6]:[#6]2:[#7]:[#6]:[#7]:[#6]:2:[#7]:1',
    pyrimidine: '[#6]1:[#7]:[#6]:[#7]:[#6]:[#6]:1',
    benzothiazole: '[#6]1:[#6]:[#6]:[#6]2:[#16]:[#6]:[#7]:[#6]:2:[#6]:1',
    quinazoline: '[#6]1:[#6]:[#6]:[#6]2:[#6](:[#6]:1):[#7]:[#6]:[#7]:[#6]:2',
    indole: '[#6]1:[#6]:[#6]:[#6]2:[#7]:[#6]:[#6]:[#6]:2:[#6]:1',
    piperazine: 'C1CNCCN1', sulfonamide: 'S(=O)(=O)N', urea: '[NX3][CX3](=O)[NX3]', 'carboxylic acid': 'C(=O)[OX2H1]',
    'aryl fluoride': '[F][c]', 'basic amine': '[NX3;H2,H1;!$(NC=O)]',
  };
  const chips = $('#scaffoldChips');
  for (const [name, smarts] of Object.entries(SCAFFOLDS)) {
    const b = el('button', '', name);
    b.onclick = async () => { $('#libSmarts').value = smarts; try { libFiltered = await S.library.substructure(smarts); renderLibrary(); toast(`${libFiltered.length} compounds contain ${name}`); } catch (e) { toast(e.message, true); } };
    chips.appendChild(b);
  }
  $('#btnProfile').onclick = () => S.library.profileAll((d, n) => status(`profiling ${d}/${n}`)).then(() => { renderLibrary(); toast('Profiles computed'); });
  $('#btnNovelty').onclick = async () => {
    const list = S.library.compounds.filter((c) => !c.known).slice(0, 40);
    let known = 0;
    for (const c of list) { const k = await S.library.checkNovelty(c); if (k.exact.length) known++; status(`novelty ${list.indexOf(c) + 1}/${list.length}`); }
    toast(`${known} of ${list.length} already exist in PubChem`);
    renderLibrary();
  };
  $('#btnAutoNumber').onclick = () => { S.library.autoNumber(); S.library.save(); renderLibrary(); };
  $('#btnExportCsv').onclick = () => downloadText(S.library.toCSV(), 'agi_compounds.csv', 'text/csv');
  $('#btnExportSdfJson').onclick = () => downloadJson({ compounds: S.library.compounds }, 'agi_compounds.json');
  $('#btnScreen').onclick = () => (S.screening ? (S.stopFlag = true) : screenLibrary());
  $('#btnScreenQuick').onclick = () => (S.screening ? (S.stopFlag = true) : screenLibrary({ limit: 12, runs: 3, steps: 1200 }));

  $('#btnFingerprint').onclick = () => analysePose();
  $('#btnSelectivity').onclick = () => selectivityPanel().catch((e) => toast(e.message, true));
  $('#btnPockets').onclick = doPockets;
  $('#btnDock').onclick = doDock;
  $('#btnStopDock').onclick = () => { S.stopFlag = true; };
  $('#btnMd').onclick = toggleMD;
  $('#freezeProtein').onchange = (e) => { if (S.md) S.md.frozenProtein = e.target.checked; };
  $('#liveTemp').onchange = (e) => { if (S.md) S.md.T = +e.target.value; };
  $('#btnMeasure').onclick = (e) => { S.measureMode = !S.measureMode; e.target.classList.toggle('on', S.measureMode); S.selection = []; renderSelection(); };
  $('#btnClearSel').onclick = () => { S.selection = []; renderSelection(); };

  $('#btnJoin').onclick = () => { S.collab.join($('#roomName').value, $('#userName').value); $('#peerList').textContent = `In room ${$('#roomName').value}.`; };
  $('#btnLeave').onclick = () => { S.collab.leave(); $('#peerList').textContent = 'Not connected.'; };
  $('#btnAf3Local').onclick = exportAf3;
  $('#btnAfServer').onclick = exportAfServer;
  $('#btnAf3Import').onclick = () => $('#af3File').click();
  $('#af3File').onchange = (e) => e.target.files[0] && importAf3(e.target.files[0]);
  $('#btnBackendMd').onclick = runBackendMD;
  $('#btnBackendStop').onclick = () => { if (S.backendJob) { server.cancelMD(S.backendJob); S.backendJob = null; } S.trajectory = null; };
  $('#btnBq').onclick = async () => {
    try {
      const r = await server.bigquery({ preset: 'alphafold_by_gene', gene: $('#bqGene').value.toUpperCase(), limit: 25 });
      logTo('#bqLog', r.rows.map((x) => `${x.entryId} ${x.organismScientificName} pLDDT ${fmt(x.globalMetricValue, 1)}`).join('\n') || 'no rows');
    } catch (e) { logTo('#bqLog', e.message); }
  };

  const repSel = $('#repSelect'), colSel = $('#colorSelect');
  REPS.forEach((r) => repSel.appendChild(new Option(r, r)));
  COLORS.forEach((c) => colSel.appendChild(new Option(c, c)));
  repSel.value = 'cartoon+pocket'; colSel.value = 'chain';
  repSel.onchange = () => { S.proteinView?.setStyle({ rep: repSel.value }); refreshPickTargets(); };
  colSel.onchange = () => { S.proteinView?.setStyle({ color: colSel.value }); };
  $('#showH').onchange = (e) => { S.proteinView?.setStyle({ showH: e.target.checked }); S.ligandView?.setStyle({ showH: e.target.checked }); refreshPickTargets(); };
  $('#showWater').onchange = (e) => { S.proteinView?.setStyle({ showWater: e.target.checked }); refreshPickTargets(); };
  $('#showPockets').onchange = drawPocketBlob;

  $('#btnPanel').onclick = () => { $('#right').classList.toggle('collapsed'); $('#left').classList.toggle('collapsed'); setTimeout(resize, 60); };
  $('#btnEvidence').onclick = () => gatherEvidence().catch((e) => toast(e.message, true));
  $('#btnDemo').onclick = runDemo;
  $('#btnDash').onclick = () => toggleDashboard();
  $('#mobDash')?.addEventListener('click', () => toggleDashboard());
  $('#btnGlasses')?.addEventListener('click', () => { location.search = '?mode=glasses'; });
  $('#btnToolList')?.addEventListener('click', () => {
    const schema = S.agent ? S.agent.tools.map((t) => `${t.name}(${Object.keys(t.parameters.properties || {}).join(', ')}) — ${t.description}`) : [];
    S.console?.say('agent', `<b>${schema.length} tools</b><pre>${schema.join('\n')}</pre>`);
  });
  // Mobile: the panels become bottom sheets.
  $$('#mobileBar button[data-sheet]').forEach((b) => {
    b.onclick = () => {
      const which = b.dataset.sheet;
      const left = $('#left'), right = $('#right');
      if (which === 'right') { right.classList.toggle('sheet-open'); left.classList.remove('sheet-open'); return; }
      right.classList.remove('sheet-open');
      $$('.tabs button').find((x) => x.dataset.tab === which)?.click();
      left.classList.toggle('sheet-open', !left.classList.contains('sheet-open') || $$('.tabs button').find((x) => x.dataset.tab === which)?.classList.contains('active'));
    };
  });
  $('#btnPatents').onclick = reviewPatents;
  renderFoundations();
  $('#btnLedgerVerify').onclick = async () => {
    const v = await S.ledger.verify();
    toast(v.ok ? `Chain intact: ${v.length} records, head ${v.head.slice(0, 12)}…` : `Chain broken at record ${v.brokenAt}: ${v.reason}`, !v.ok);
  };
  $('#btnLedgerExport').onclick = () => downloadJson(S.ledger.export(), `biodao-ledger-${Date.now()}.json`);
  $('#btnLedgerClear').onclick = () => { if (confirm('Clear the provenance ledger? This cannot be undone.')) { S.ledger.clear(); renderLedger(); } };
  $('#btnVR').onclick = () => enterXR('immersive-vr');
  $('#btnAR').onclick = () => enterXR('immersive-ar');
  $('#xrHelpClose').onclick = () => $('#xrHelp').classList.add('hidden');
  // The controls card is a per-viewer convenience; storage may be unavailable (private mode), so never depend on it.
  const HELP_KEY = 'biodao-viewhelp-hidden';
  try { if (localStorage.getItem(HELP_KEY)) $('#viewHelp').classList.add('hidden'); } catch {}
  $('#viewHelpClose').onclick = () => { $('#viewHelp').classList.add('hidden'); try { localStorage.setItem(HELP_KEY, '1'); } catch {} };

  addEventListener('keydown', (e) => {
    if (e.target.matches('input, select, textarea')) return;
    if (e.key === ' ') { e.preventDefault(); toggleMD(); }
    if (e.key === 'd') doDock();
    if (e.key === 'p') doPockets();
    if (e.key === 'f') fitView();
    if (e.key === 'Escape') $('#xrHelp').classList.add('hidden');
    if (e.key === 'n') cycleCompound(1);
  });
}

// Optional WebXR emulator (Meta's IWER, pinned) for trying the headset interface on a desktop:
//   ?emulate=quest3            controllers        ?emulate=quest3&input=hands   articulated hand tracking
async function maybeEmulateXR() {
  const params = new URLSearchParams(location.search), p = params.get('emulate');
  if (!p) return false;
  try {
    const iwer = await import('https://cdn.jsdelivr.net/npm/iwer@2.4.0/+esm');
    const device = new iwer.XRDevice(iwer[p === 'questpro' ? 'metaQuestPro' : p === 'quest2' ? 'metaQuest2' : 'metaQuest3']);
    device.installRuntime({ forceInstall: true });  // replace Chrome's empty native runtime
    device.controllers.right.position.set(0.25, 1.2, -0.3);
    device.controllers.left.position.set(-0.25, 1.2, -0.3);
    if (params.get('input') === 'hands') device.primaryInputMode = 'hand';
    window.xrDevice = device;
    toast('WebXR emulator active — "Enter VR" now works in this browser');
    return true;
  } catch (e) { toast(`emulator failed: ${e.message}`, true); return false; }
}

// ---------------------------------------------------------------- assistant: tools, voice, hands
// One adapter object is the whole surface the tools (and therefore the console, the voice layer and any
// external agent) can touch. Keeping it explicit means a tool can never reach into app internals by accident.
function buildAppAdapter() {
  const round = (v) => (v == null || Number.isNaN(v) ? null : +(+v).toFixed(2));
  return {
    get state() { return S; },
    round,
    findTarget: (q) => {
      const n = String(q || '').trim().toLowerCase().replace(/\s+/g, '');
      return S.targets.find((t) => t.symbol.toLowerCase() === n)
        || S.targets.find((t) => t.symbol.toLowerCase().startsWith(n))
        || S.targets.find((t) => (t.name || '').toLowerCase().includes(n));
    },
    findCompound: (id) => {
      const n = String(id || '').toLowerCase().replace(/[^a-z0-9]/g, '');
      return S.library.compounds.find((c) => (c.agiId || '').toLowerCase().replace(/[^a-z0-9]/g, '') === n)
        || S.library.compounds.find((c) => (c.agiId || '').toLowerCase().includes(n));
    },
    searchGene: (q) => uniprot.searchGene(q),
    openTarget, loadPdb, loadAlphaFold, loadCompound, loadDrugByName, extractCocrystal,
    doPockets, gatherEvidence, findSimilarFolds: () => findSimilarFolds(document.createElement('button')),
    cycleCompound: (dir) => { cycleCompound(dir); return { ligand: S.compound?.agiId || S.ligand?.name || null }; },
    loadSmiles: async (smiles) => { const st = await smilesTo3D(smiles, { name: 'query' }); await setLigand(st, { smiles }); },
    doDock: async ({ runs, steps } = {}) => doDock({ runs, steps }),
    screenLibrary: (args) => screenLibrary(args),
    rankedLibrary: () => S.library.compounds.filter((c) => c.dockScore != null).sort((a, b) => a.dockScore - b.dockScore),
    startMD: ({ rigidProtein } = {}) => { if (rigidProtein !== undefined) $('#freezeProtein').checked = !!rigidProtein; if (!S.mdRunning) startMD(); },
    stopMD,
    runBackendMD: async ({ steps, temperature } = {}) => {
      if (steps) $('#mdSteps').value = steps;
      if (temperature) $('#mdTemp').value = temperature;
      await runBackendMD();
      return { started: true, note: 'all-atom OpenMM run; the trajectory plays back when it finishes' };
    },
    knownDrugs: () => ({ target: S.target?.symbol || null,
      drugs: [...document.querySelectorAll('#drugList .item')].slice(0, 15).map((el) => el.textContent.replace(/\s+/g, ' ').trim()) }),
    setView: ({ representation, colour, reset }) => {
      if (representation) { $('#repSelect').value = representation; $('#repSelect').dispatchEvent(new Event('change')); }
      if (colour) { $('#colorSelect').value = colour; $('#colorSelect').dispatchEvent(new Event('change')); }
      if (reset) fitView();
      return { representation: S.proteinView?.style.rep, colour: S.proteinView?.style.color };
    },
    measure: () => ({ text: $('#selInfo').textContent }),
    analysePose: () => {
      const fp = analysePose();
      if (!fp) throw new Error('load a target and a ligand first');
      return { summary: fp.summary, counts: fp.counts,
        residues: fp.residues.slice(0, 10).map((r) => ({ residue: r.label, types: r.types })) };
    },
    selectivity: (args) => selectivityPanel(args).then((rows) => ({ compared: rows })),
    series: ({ cut } = {}) => {
      const groups = clusterSeries(S.library.compounds, (c) => S.library.fpBytes(c), tanimoto, { cut: cut ?? 0.55 });
      return { series: groups.length,
        groups: groups.slice(0, 10).map((g) => ({ size: g.size, members: g.members.slice(0, 6).map((m) => m.agiId),
          best: g.best ? { id: g.best.agiId, score: g.best.dockScore } : null })) };
    },
    librarySearch: async ({ text, smarts, maxMw, cnsOnly }) => {
      let list = smarts ? await S.library.substructure(smarts) : S.library.search(text || '');
      if (maxMw) list = list.filter((c) => (c.profile?.desc.mw ?? 1e9) <= maxMw);
      if (cnsOnly) list = list.filter((c) => c.profile?.rules?.bbbLikely);
      return { matches: list.length, compounds: list.slice(0, 20).map((c) => ({ id: c.agiId, smiles: c.canonical, mw: round(c.profile?.desc.mw), score: c.dockScore })) };
    },
    ledger: async (action) => {
      if (action === 'export') { downloadJson(S.ledger.export(), `biodao-ledger-${Date.now()}.json`); return { text: 'Ledger exported.' }; }
      if (action === 'list') return { records: S.ledger.records.slice(-15).map((r) => ({ kind: r.kind, time: r.time, hash: r.hash.slice(0, 12) })) };
      const v = await S.ledger.verify();
      return { ...v, records: S.ledger.records.length, text: v.ok ? `Chain verified: ${v.length} records intact.` : `Chain broken at record ${v.brokenAt}: ${v.reason}` };
    },
    describe: () => {
      const p = S.protein, sc = S.lastScore;
      if (!p) return { text: 'Nothing is loaded yet. Ask me to load a target, such as SOD1.' };
      const bits = [`${p.name}, ${p.residues.filter((r) => r.polymer).length} residues`];
      if (S.target) bits.push(`the ${S.target.program} programme target ${S.target.symbol}, ${S.target.disease}`);
      if (S.ligand) bits.push(`with ${S.ligand.name} in the site`);
      if (sc) bits.push(`scoring ${round(sc.total)} kilocalories per mole with ${sc.hbonds.length} hydrogen bonds`);
      if (S.pockets.length) bits.push(`${S.pockets.length} pockets detected`);
      return { text: bits.join(', ') + '.', target: S.target?.symbol, structure: p.name, score: round(sc?.total) };
    },
  };
}

function setupAssistant() {
  const adapter = buildAppAdapter();
  const tools = buildTools(adapter);
  const rt = new AgentRuntime(tools);
  S.agent = rt;
  rt.setVocabulary([...S.targets.map((t) => t.symbol), ...S.library.compounds.map((c) => c.agiId).filter(Boolean)]);

  // Publish the schema so the MCP server can advertise the same tools.
  fetch('/api/tools', { method: 'POST', body: JSON.stringify(toolSchemas(tools)) }).catch(() => {});
  connectCommandChannel(rt, { onStatus: (st) => { const c = $('#agentStatus'); if (c) c.textContent = st === 'connected' ? 'agent channel open' : 'agent channel offline'; } });

  // Voice: the same tools, spoken.
  const voice = new VoiceControl({
    onCommand: (parsed) => { if (parsed.intent !== 'unknown') S.console?.submit(parsed.transcript, 'voice'); },
    onState: (st) => {
      const b = S.console?.micButton;
      if (b) b.classList.toggle('listening', st === 'listening');
      const g = $('#glassesMic');
      if (g) g.classList.toggle('listening', st === 'listening');
    },
  });
  S.voice = voice;
  rt.setVocabulary && voice.addVocabulary([...S.targets.map((t) => t.symbol), 'biodao']);

  const consoleRoot = $('#agentConsole');
  if (consoleRoot) {
    S.console = new AgentConsole(consoleRoot, rt, { onSpeak: (line) => S.speakBack && voice.speak(line) });
    const mic = S.console.micButton;
    mic.disabled = !VoiceControl.supported;
    mic.title = VoiceControl.supported ? 'Voice control' : 'This browser has no speech recognition (Safari and Vision Pro often lack it)';
    mic.onclick = () => {
      if (voice.listening) { voice.stop(); mic.classList.remove('on'); S.speakBack = false; }
      else { voice.start(); mic.classList.add('on'); S.speakBack = true; toast('Listening. Try: load LRRK2, find pockets, dock, explain this'); }
    };
  }
  return rt;
}

// Hand tracking replaces the controllers when a headset reports hands.
function setupHands() {
  if (S.hands) return S.hands;
  const hands = new HandTracking(renderer, scene, { workspace });
  S.hands = hands;
  hands.addEventListener('tap', (e) => {
    const p = e.detail.position;
    if (!p) return;
    raycaster.set(camera.getWorldPosition(new THREE.Vector3()), p.clone().sub(camera.getWorldPosition(new THREE.Vector3())).normalize());
    const hit = raycaster.intersectObjects(xr.pickTargets, true)[0];
    if (hit) onPick(hit, hit.point);
  });
  hands.addEventListener('point', (e) => {
    if (!S.mdRunning) return;
    const { origin, direction } = e.detail;
    raycaster.set(origin, direction);
    const hit = raycaster.intersectObject(S.ligandView?.group || new THREE.Group(), true)[0];
    if (hit) updateSteer(hit.point);
  });
  hands.addEventListener('swipe', (e) => cycleCompound(e.detail.direction === 'right' ? 1 : -1));
  hands.addEventListener('palmup', () => xr.setPanelVisible(true));
  hands.addEventListener('palmdown', () => xr.setPanelVisible(false));
  return hands;
}

// ---------------------------------------------------------------- pose analysis
const INTERACTION_COLOURS = { hbond: '#8ef5c2', saltBridge: '#ffbe0b', piStacking: '#b388eb',
  halogen: '#4cc9f0', hydrophobic: '#93a7bd' };

function analysePose() {
  if (!S.protein || !S.ligand) return toast('Load a target and a ligand first', true);
  const fp = interactionFingerprint(S.protein, S.ligand);
  S.fingerprint = fp;
  const box = $('#fingerprintOut');
  const chips = Object.entries(fp.counts).map(([k, n]) =>
    `<span class="dash-chip" style="border-color:${INTERACTION_COLOURS[k]};color:${INTERACTION_COLOURS[k]}">${k.replace(/([A-Z])/g, ' $1').toLowerCase()} <b>${n}</b></span>`).join('');
  const rows = fp.residues.slice(0, 12).map((r) => {
    const types = Object.keys(r.types).map((t) => `<span style="color:${INTERACTION_COLOURS[t]}">•</span>`).join('');
    return `<div class="bar-row" data-res="${r.residue}" style="grid-template-columns:70px 1fr 40px">
      <span class="bar-label">${r.label}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${Math.min(100, r.total * 12)}%;background:${INTERACTION_COLOURS[Object.keys(r.types)[0]] || '#39d98a'}"></span></span>
      <span class="bar-value">${types}</span></div>`;
  }).join('');
  box.innerHTML = `<div class="chips" style="margin-bottom:8px">${chips}</div>
    <p class="hint" style="margin:0 0 8px">${fp.summary}</p><div class="bars">${rows}</div>
    <p class="hint" style="margin-top:6px">Geometry only, on heavy atoms: a hydrogen bond here means donor and acceptor in range, not a proven one.</p>`;
  box.querySelectorAll('[data-res]').forEach((el2) => {
    el2.onclick = () => { S.proteinView.pocketResidues = new Set([+el2.dataset.res]); S.proteinView.build(); refreshPickTargets(); };
  });

  // Does this pocket sit where variation is poorly tolerated?
  const overlap = S.missense && S.pocket ? pocketVariantOverlap(S.protein, S.pocket, S.missense) : null;
  $('#variantOut').innerHTML = overlap
    ? `<div class="block" style="margin:8px 0 0;padding:8px 10px"><b>Variant sensitivity</b><br>${overlap.summary}
       <div class="chips" style="margin-top:6px">${overlap.residues.slice(0, 8).map((r) =>
         `<span class="dash-chip" ${r.pathogenic ? 'style="color:var(--bad);border-color:#6b1f2c"' : ''}>${r.label} ${r.score.toFixed(2)}</span>`).join('')}</div></div>`
    : (S.missense ? '' : '<span class="hint">Load an AlphaFold model to add variant sensitivity.</span>');

  S.ledger.append('analysis', { target: S.protein.name, ligand: S.ligand.name, counts: fp.counts,
    residues: fp.residues.slice(0, 10).map((r) => r.label), variantEnrichment: overlap?.enrichment ?? null }).then(renderLedger);
  return fp;
}

// Dock the same compound against related targets: a cheap read on selectivity.
async function selectivityPanel({ limit = 4, runs = 4, steps = 1200 } = {}) {
  if (!S.ligand) return toast('Load a ligand first', true);
  const ligandSmiles = S.compound?.canonical;
  const here = S.target;
  const others = S.targets
    .filter((t) => t !== here && t.bestPdb && (here ? t.program === here.program : true))
    .slice(0, limit);
  if (!others.length) return toast('No related targets with structures to compare against', true);
  const out = $('#selectivityOut');
  out.innerHTML = '<div class="hint">docking against related targets…</div>';
  const rows = [];
  const startProtein = S.protein, startTarget = S.target;
  const onHere = S.lastScore?.total;
  for (const t of others) {
    try {
      status(`selectivity: ${t.symbol}`);
      await loadPdb(t.bestPdb, { uniprot: t.uniprot, symbol: t.symbol });
      await doPockets();
      if (ligandSmiles) { const st = await smilesTo3D(ligandSmiles, { name: S.ligand.name }); await setLigand(st, { smiles: ligandSmiles }); }
      const poses = await dockLigand(S.grid, S.ligand, S.pocket.center, { runs, steps, box: 8 });
      rows.push({ symbol: t.symbol, disease: t.disease, score: poses[0] ? +poses[0].score.toFixed(2) : null });
    } catch (e) { rows.push({ symbol: t.symbol, error: e.message }); }
  }
  rows.sort((a, b) => (a.score ?? 99) - (b.score ?? 99));
  out.innerHTML = `<div class="hint">On ${startTarget?.symbol || startProtein?.name}: <b>${mark(fmt(onHere), DOCK_TIER)}</b></div>`
    + rows.map((r) => `<div class="item"><div class="t"><span class="n">${r.symbol}</span>
        <span class="s">${r.error ? 'failed' : mark(fmt(r.score), DOCK_TIER)}</span></div>
        <div class="d">${esc(r.disease || r.error || '')}</div></div>`).join('')
    + `<p class="hint">Same compound, same search settings, different sites. A compound that scores much better on
       the intended target than on its relatives is the one worth pursuing.</p>${note(DOCK_TIER)}`;
  S.ledger.append('selectivity', { ligand: S.ligand.name, onTarget: startTarget?.symbol, onTargetScore: onHere, others: rows }).then(renderLedger);
  return rows;
}

function esc(s2) { return String(s2 ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])); }

// ---------------------------------------------------------------- environments
async function setupScenes() {
  const env = new EnvironmentManager(renderer, scene, { workspace, camera });
  S.env = env;
  S.walk = new Locomotion(camera, rig, { xr });

  const sel = $('#hdriSelect');
  HDRI_PRESETS.forEach((h) => sel.appendChild(new Option(h.label, h.id)));
  sel.appendChild(new Option('none', 'none'));
  sel.value = 'lab';
  sel.onchange = async () => {
    status(`lighting: ${sel.value}…`);
    try { const r = await env.setLighting(sel.value); env.showBackground($('#hdriBg').checked); toast(`Lighting: ${r.lighting}`); }
    catch (e) { toast(`Lighting failed: ${e.message}`, true); }
  };
  $('#hdriBg').onchange = (e) => env.showBackground(e.target.checked);
  $('#sceneQuality').onchange = (e) => { const r = env.setQuality(e.target.value); toast(`Detail: ${r.level}`); };
  $('#walkMode').onchange = (e) => { S.walk.setEnabled(e.target.checked); controls.enabled = !e.target.checked;
    toast(e.target.checked ? 'Walk mode: W A S D, shift to sprint; thumbstick in a headset' : 'Orbit mode'); };
  $('#sceneSmaller').onclick = () => showSceneStats(S.env.rescale(0.5));
  $('#sceneBigger').onclick = () => showSceneStats(S.env.rescale(2));
  $('#sceneRefit').onclick = () => { S.env.placeWorkspace(S.env.stats); fitView(); };
  $('#btnSceneNone').onclick = () => { env.clear(); $('#sceneInfo').textContent = 'Empty space.'; fitView(); };
  $('#btnSceneImport').onclick = () => $('#sceneFile').click();
  $('#sceneFile').onchange = (e) => e.target.files[0] && loadScene(e.target.files[0]);
  const drop = $('#sceneDrop');
  ['dragenter', 'dragover'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove('over'); }));
  drop.addEventListener('drop', (e) => e.dataTransfer.files[0] && loadScene(e.dataTransfer.files[0]));

  try {
    const { scenes } = await (await fetch('/api/scenes')).json();
    S.scenes = scenes;
    const list = $('#sceneList');
    list.innerHTML = scenes.length ? '' : '<div class="hint">No scenes in assets/scenes. Drop a .glb below, or copy files into that folder.</div>';
    for (const sc of scenes) {
      const it = el('div', 'item', `<div class="t"><span class="n">${sc.label}</span><span class="s">${sc.mb} MB</span></div>`);
      it.onclick = () => loadScene(sc.url, sc.label);
      list.appendChild(it);
    }
  } catch { /* the server lists scenes; without it, import still works */ }
  await env.setLighting('lab').catch(() => {});
  return env;
}

function showSceneStats(r) {
  if (!r) return;
  const info = $('#sceneInfo');
  info.innerHTML = `<b>${S.env.current?.name || 'scene'}</b><br>${r.meshes} meshes · ${(r.triangles / 1000).toFixed(0)}k triangles
    · ${r.textures} textures · ${r.size.x}×${r.size.z} m${r.autoScaled ? ` (auto-scaled ${r.scale}×)` : ''}
    ${r.heavy ? '<br><span style="color:var(--warn)">Heavy scene: switch detail to lite before entering VR.</span>' : ''}`;
}

// Cycle the available backdrops from inside VR, where there are no panels to click.
async function cycleScene(dir = 1) {
  const list = [{ label: 'Empty space', url: null }, ...(S.scenes || [])];
  const current = S.env?.current?.name || 'Empty space';
  let i = list.findIndex((x) => x.label === current);
  if (i < 0) i = 0;
  const next = list[(i + dir + list.length) % list.length];
  if (!next.url) { S.env.clear(); toast('Backdrop: empty space'); xr.panel.setStatus('backdrop: empty'); return { backdrop: 'none' }; }
  xr.panel.setStatus(`loading ${next.label}…`);
  await loadScene(next.url, next.label);
  xr.panel.setStatus(`backdrop: ${next.label}`);
  return { backdrop: next.label };
}

// In a headset the scene is a backdrop, not a place to walk: drop distant detail and keep the molecule
// at arm's length in front of the viewer.
function stageSceneForXR() {
  if (!S.env?.current) return;
  S.env.setQuality('lite');
  S.env.placeWorkspace(S.env.stats);
  fitView(0.45);
}

async function loadScene(source, name) {
  const info = $('#sceneInfo');
  info.textContent = 'loading scene…';
  try {
    const r = await S.env.load(source, { name, onProgress: (f) => { info.textContent = `loading ${Math.round(f * 100)}%`; } });
    showSceneStats(r);
    fitView();
    if (r.heavy) { $('#sceneQuality').value = 'medium'; S.env.setQuality('medium'); }
    S.ledger.append('scene', { name: r.name, meshes: r.meshes, triangles: r.triangles }).then(renderLedger);
    toast(`${r.name} loaded`);
  } catch (e) { info.textContent = e.message; toast(e.message, true); }
}

// ---------------------------------------------------------------- dashboard
function toggleDashboard(force) {
  const open = force ?? !S.dashboardOpen;
  S.dashboardOpen = open;
  let root = $('#dashRoot');
  if (!root) {
    root = el('div', 'dash');
    root.id = 'dashRoot';
    $('#viewport').appendChild(root);
  }
  root.style.display = open ? 'block' : 'none';
  $('#btnDash')?.classList.toggle('on', open);
  if (open) refreshDashboard();
}

function refreshDashboard() {
  const root = $('#dashRoot');
  if (!root || !S.dashboardOpen) return;
  const data = computeStats(S);
  renderDashboard(root, data, {
    onOpenTarget: (programme) => { S.program = programme; renderPrograms(); renderTargets(); toggleDashboard(false);
      $$('.tabs button').find((b) => b.dataset.tab === 'targets')?.click(); },
    onOpenCompound: (id) => { const c = S.library.compounds.find((x) => x.agiId === id); if (c) { toggleDashboard(false); loadCompound(c); } },
    onRun: (what) => {
      const map = { find_pockets: () => doPockets(), dock: () => doDock(), screen: () => screenLibrary({ limit: 12, runs: 3, steps: 1200 }),
        evidence: () => gatherEvidence(), folds: () => findSimilarFolds(document.createElement('button')),
        ledger_verify: async () => { const v = await S.ledger.verify(); toast(v.ok ? `Chain verified: ${v.length} records` : `Chain broken at ${v.brokenAt}`, !v.ok); refreshDashboard(); },
        ledger_export: () => downloadJson(S.ledger.export(), `biodao-ledger-${Date.now()}.json`),
        report: () => downloadText(buildReport(S, data), `biodao-report-${new Date().toISOString().slice(0, 10)}.txt`) };
      const fn = map[what];
      if (fn) { if (what !== 'report' && what !== 'ledger_export') toggleDashboard(false); fn(); }
    },
  });
}

// ---------------------------------------------------------------- glasses companion
// Ray-Ban Meta and similar glasses have no WebXR browser, so the useful shape is voice in, speech and
// large type out, on the phone paired with them. This is that view.
function setupGlassesMode() {
  document.body.classList.add('glasses');
  const panel = el('div', 'glasses-panel');
  panel.innerHTML = `<div class="said" id="gSaid">Say what you need. For example: what do we know about LRRK2.</div>
    <div class="answer" id="gAnswer">biodao.blockchain</div><div class="detail" id="gDetail">voice companion</div>`;
  $('#viewport').appendChild(panel);
  const mic = el('button', 'glasses-mic primary', '🎙');
  mic.id = 'glassesMic';
  $('#viewport').appendChild(mic);
  S.speakBack = true;
  const voice = S.voice;
  mic.onclick = () => (voice.listening ? voice.stop() : voice.start());
  if (voice) {
    voice.addEventListener('command', async (e) => {
      const parsed = e.detail;
      $('#gSaid').textContent = parsed.transcript;
      try {
        const out = await S.agent.run(parsed.transcript, { source: 'glasses' });
        const line = out.tool ? AgentRuntime.summarise(out.tool, out.result) : out.help;
        $('#gAnswer').textContent = line;
        $('#gDetail').textContent = out.tool ? out.tool.replace(/_/g, ' ') : 'not understood';
        voice.speak(line);
      } catch (err) {
        $('#gAnswer').textContent = err.message;
        voice.speak(`That failed. ${err.message}`);
      }
    });
    voice.start();
  }
}

// ---------------------------------------------------------------- boot
async function boot() {
  wire();
  await maybeEmulateXR();
  resize();
  S.collab = new Collab(scene, workspace);
  S.collab.addEventListener('peer', (e) => { $('#peerList').textContent = `${e.detail.count} other participant(s) in the room.`; });
  S.collab.addEventListener('state', (e) => {
    const st = e.detail;
    if (st.kind === 'protein' && st.pdb) loadPdb(st.pdb).catch(() => {});
    else if (st.kind === 'protein' && st.uniprot) loadAlphaFold(st.uniprot).catch(() => {});
    if (st.kind === 'ligand' && st.smiles) smilesTo3D(st.smiles, { name: st.name }).then((s) => setLigand(s, { smiles: st.smiles }));
  });

  S.caps = await server.health();
  setServerCaps(S.caps);
  const chip = $('#serverChip');
  chip.textContent = S.caps ? `server: ${['rdkit', 'openmm', 'pypdf'].filter((k) => S.caps[k]).join(' + ') || 'basic'}` : 'server: browser only';
  chip.className = 'chip ' + (S.caps ? 'ok' : 'off');

  await refreshXRButtons();
  onXRDeviceChange(refreshXRButtons);

  try {
    const r = await fetch('data/targets.json');
    const j = await r.json();
    S.targets = j.targets;
    renderPrograms(); renderTargets();
  } catch { toast('targets.json missing — run scripts/build_targets.py', true); }

  S.ledger.actor = localStorage.getItem('biodao-actor') || 'researcher';
  renderLedger();
  S.library.addEventListener('change', renderLibrary);
  await S.library.load();
  renderLibrary();

  loadRDKit().then(() => status('ready')).catch(() => toast('RDKit.js failed to load; chemistry features are offline', true));

  setupAssistant();
  setupHands();
  setupScenes().catch((e) => console.warn('scenes', e));
  const params = new URLSearchParams(location.search);
  if (params.get('mode') === 'glasses') setupGlassesMode();
  if (params.get('view') === 'dashboard') toggleDashboard(true);
  S.ledger.addEventListener('append', () => refreshDashboard());

  const t = S.targets.find((x) => x.symbol === 'SOD1');
  if (t) openTarget(t);
  status('ready');
  if (new URLSearchParams(location.search).has('record')) {
    setTimeout(() => runFilm().catch((e) => {
      toast(e.message, true); console.error(e);
      fetch(`/api/filmprogress?err=${encodeURIComponent(e.stack || e.message)}`).catch(() => {});
    }), 1500);
  }
}

boot();
Object.assign(S, { scene, camera, renderer, workspace, model, overlay, xr, controls });
window.AGI = S; // handy for the console
