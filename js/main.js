// AGI BioXR — application shell: scene, data loading, docking, dynamics, screening, XR and UI wiring.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { parsePDB, parseMmCIF, parseMolblock, parsePDBFrames } from './structure.js';
import { MolView, REPS, COLORS, textSprite, dashedLine } from './render.js';
import { MDEngine } from './md.js';
import { ProteinGrid, vinaScore, findPockets, dockLigand, centroid } from './dock.js';
import { analyze, smilesTo3D, loadRDKit, setServerCaps, depict, heavyAtomModel, fingerprint } from './chem.js';
import { CompoundLibrary, importFile } from './compounds.js';
import { rcsb, alphafold, uniprot, openTargets, pubchem, chembl, server, foldseek } from './api.js';
import { af3LocalJob, afServerJob, downloadJson, downloadText, readPrediction } from './af3.js';
import { Collab } from './collab.js';
import { XRManager, xrSupport, startSession } from './xr.js';

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
const fmt = (v, n = 2) => (v == null || Number.isNaN(v) ? '–' : (+v).toFixed(n));

const S = {
  targets: [], program: 'ALS', target: null, protein: null, proteinView: null, ligand: null, ligandView: null,
  grid: null, pockets: [], pocket: null, poses: [], md: null, mdRunning: false, caps: null,
  selection: [], measureMode: false, library: new CompoundLibrary(), compound: null, screening: false, stopFlag: false,
  backendJob: null, trajectory: null, missense: null, lastScore: null,
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

function resize() {
  const v = $('#viewport');
  renderer.setSize(v.clientWidth, v.clientHeight, false);
  camera.aspect = v.clientWidth / Math.max(1, v.clientHeight);
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);

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
  S.protein = st; S.missense = null; S.pockets = []; S.pocket = null; S.poses = []; clearOverlay();
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
  status(`${st.n} atoms loaded`);
}

// Frame the structure at a comfortable arm's-length size: about 60 cm across, 80 cm in front, at eye height.
function fitView(diameter = 0.6) {
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
  toast(`${poses.length} poses · best ${fmt(poses[0]?.score)} kcal/mol · ${Math.round((performance.now() - t0) / 1000)} s`);
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
async function screenLibrary() {
  if (!S.grid) return toast('Load a target first', true);
  const list = S.library.compounds.slice(0, 200);
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
      const poses = await dockLigand(S.grid, st, center, { runs: 4, steps: 1800, box: 8, shouldStop: () => S.stopFlag });
      c.dockScore = poses[0] ? +poses[0].score.toFixed(2) : null;
      c.dockTarget = S.protein.name;
    } catch { c.dockScore = null; }
    status(`screening ${++done}/${list.length} · ${c.agiId || ''} ${c.dockScore ?? ''}`);
    renderLibrary();
  }
  S.screening = false;
  S.library.save();
  const ranked = list.filter((c) => c.dockScore != null).sort((a, b) => a.dockScore - b.dockScore);
  toast(`Screen done. Best: ${ranked.slice(0, 3).map((c) => `${c.agiId} ${c.dockScore}`).join(', ')}`);
  $('#libSort').value = 'score'; renderLibrary();
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

function onPick(hit, worldPoint) {
  const p = pickAtom(hit);
  if (!p) return;
  if (S.mdRunning && p.view === S.ligandView) { startSteer(worldPoint); return; }
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
  if (xr.active) { xr.update(); S.collab?.tick(camera, xr.controllers); }
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
  if (t.alphafold) loadAlphaFold(t.uniprot, { symbol: t.symbol }).catch((e) => toast(e.message, true));
  else if (t.bestPdb) loadPdb(t.bestPdb, { uniprot: t.uniprot }).catch((e) => toast(e.message, true));
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
    <span>score <b>${fmt(r.total)} kcal/mol</b></span><span>ligand eff. <b>${fmt(r.ligandEfficiency)}</b></span>
    <span>H-bonds <b>${r.hbonds.length}</b></span><span>contacts <b>${r.contactResidues.length} res</b></span>
    <span>clash <b>${fmt(r.terms.repulsion, 1)}</b></span><span>hydrophobic <b>${fmt(r.terms.hydrophobic, 1)}</b></span>
  </div><div class="hint">Vina-style empirical score; lower is better. Approximate, for ranking.</div>`;
  xr.panel.setStatus(`score ${fmt(r.total)} · ${r.hbonds.length} H-bonds`);
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
    const it = el('div', 'item' + (i === active ? ' active' : ''), `<div class="t"><span class="n">Pose ${i + 1}</span><span class="s">${fmt(p.score)} kcal/mol</span></div>`);
    it.onclick = () => applyPose(i);
    box.appendChild(it);
  });
}

function renderMdStats(sc) {
  if (!S.md) return;
  const e = S.md.energy;
  $('#mdStats').innerHTML = `<span>time <b>${fmt(S.md.time, 1)} ps</b></span><span>T <b>${fmt(S.md.kineticTemperature(), 0)} K</b></span>
    <span>inter E <b>${fmt(e.inter, 1)}</b></span><span>ligand RMSD <b>${fmt(S.md.ligandRMSD())} Å</b></span>
    <span>protein RMSF <b>${fmt(S.md.proteinRMSF())} Å</b></span><span>score <b>${fmt(sc?.total)}</b></span>`;
  $('#mdBadge').textContent = `MD ${fmt(S.md.time, 1)} ps · ${fmt(S.md.kineticTemperature(), 0)} K · score ${fmt(sc?.total)}`;
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
    if (sort === 'score') return (a.dockScore ?? 1e9) - (b.dockScore ?? 1e9);
    return (a.agiId || 'zz').localeCompare(b.agiId || 'zz', undefined, { numeric: true });
  });
  $('#libStats').textContent = `${S.library.compounds.length} compounds${libFiltered ? ` · ${list.length} match` : ''}${S.library.rejects.length ? ` · ${S.library.rejects.length} need review` : ''}`;
  for (const c of list.slice(0, 300)) {
    const it = el('div', 'item' + (S.compound === c ? ' active' : ''));
    const info = el('div', '', `<div class="t"><span class="n">${c.agiId || '—'}</span>
      <span class="s">${c.dockScore != null ? `${c.dockScore} kcal/mol` : c.profile ? `MW ${fmt(c.profile.desc.mw, 0)}` : ''}</span></div>
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
async function enterXR(mode) {
  try {
    xr.setPanelVisible(true);
    await startSession(renderer, mode, () => { xr.setPanelVisible(false); scene.background = null; resize(); });
    if (mode === 'immersive-ar') scene.background = null;
    buildWristMenu();
    toast('In headset: grip to move, two grips to scale, trigger to pick.');
  } catch (e) { toast(`Could not start ${mode}: ${e.message}`, true); }
}

function buildWristMenu() {
  const repIdx = () => REPS.indexOf(S.proteinView?.style.rep || 'cartoon');
  const colIdx = () => COLORS.indexOf(S.proteinView?.style.color || 'chain');
  xr.panel.setButtons([
    { label: 'MD', value: () => (S.mdRunning ? 'running' : 'stopped'), active: S.mdRunning, onClick: (b) => { toggleMD(); b.active = S.mdRunning; } },
    { label: 'Dock', onClick: () => doDock() },
    { label: 'Pockets', onClick: () => doPockets() },
    { label: 'Style', onClick: () => { const r = REPS[(repIdx() + 1) % REPS.length]; S.proteinView?.setStyle({ rep: r }); refreshPickTargets(); xr.panel.setStatus(r); } },
    { label: 'Colour', onClick: () => { const c = COLORS[(colIdx() + 1) % COLORS.length]; S.proteinView?.setStyle({ color: c }); xr.panel.setStatus(c); } },
    { label: 'Next cmpd', onClick: () => cycleCompound(1) },
    { label: 'Prev cmpd', onClick: () => cycleCompound(-1) },
    { label: 'Recentre', onClick: () => fitView() },
  ]);
}

function cycleCompound(dir) {
  const list = S.library.compounds;
  if (!list.length) return xr.panel.setStatus('library is empty');
  const i = Math.max(0, list.indexOf(S.compound));
  const next = list[(i + dir + list.length) % list.length];
  loadCompound(next);
}

// ---------------------------------------------------------------- desktop pointer
const vp = $('#viewport');
vp.addEventListener('pointerdown', (e) => {
  if (xr.active || e.button !== 0) return;
  const r = vp.getBoundingClientRect();
  pointer.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(xr.pickTargets, true);
  if (hits[0]) { onPick(hits[0], hits[0].point); if (steer) controls.enabled = false; }
});
vp.addEventListener('pointermove', (e) => {
  if (!steer || xr.active) return;
  const r = vp.getBoundingClientRect();
  pointer.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(pointer, camera);
  const c = new THREE.Vector3(...centroid(S.ligand.pos, S.ligand.n));
  model.localToWorld(c);
  const plane = new THREE.Plane().setFromNormalAndCoplanarPoint(camera.getWorldDirection(new THREE.Vector3()).negate(), c);
  const pt = new THREE.Vector3();
  if (raycaster.ray.intersectPlane(plane, pt)) updateSteer(pt);
});
addEventListener('pointerup', () => { endSteer(); controls.enabled = true; });

xr.addEventListener('pick', (e) => {
  const { hit } = e.detail;
  if (hit) onPick(hit, hit.point);
});
xr.addEventListener('drag', (e) => {
  if (!steer) return;
  const c = new THREE.Vector3(...centroid(S.ligand.pos, S.ligand.n));
  model.localToWorld(c);
  const pt = e.detail.ray.ray.at(e.detail.ray.ray.origin.distanceTo(c), new THREE.Vector3());
  updateSteer(pt);
});
xr.addEventListener('pickend', () => endSteer());

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
  $('#btnVR').onclick = () => enterXR('immersive-vr');
  $('#btnAR').onclick = () => enterXR('immersive-ar');

  addEventListener('keydown', (e) => {
    if (e.target.matches('input, select, textarea')) return;
    if (e.key === ' ') { e.preventDefault(); toggleMD(); }
    if (e.key === 'd') doDock();
    if (e.key === 'p') doPockets();
    if (e.key === 'f') fitView();
    if (e.key === 'n') cycleCompound(1);
  });
}

// Optional WebXR emulator: open the page with ?emulate=quest3 to try the headset UI on a desktop.
async function maybeEmulateXR() {
  const p = new URLSearchParams(location.search).get('emulate');
  if (!p) return false;
  try {
    const iwer = await import('https://cdn.jsdelivr.net/npm/iwer@2.4.0/+esm');
    const device = new iwer.XRDevice(iwer[p === 'questpro' ? 'metaQuestPro' : p === 'quest2' ? 'metaQuest2' : 'metaQuest3']);
    device.installRuntime({ forceInstall: true });  // replace Chrome's empty native runtime
    device.controllers.right.position.set(0.25, 1.2, -0.3);
    device.controllers.left.position.set(-0.25, 1.2, -0.3);
    window.xrDevice = device;
    toast('WebXR emulator active — "Enter VR" now works in this browser');
    return true;
  } catch (e) { toast(`emulator failed: ${e.message}`, true); return false; }
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

  const sup = await xrSupport();
  $('#btnVR').disabled = !sup.vr; $('#btnAR').disabled = !sup.ar;
  if (!sup.vr) $('#btnVR').title = 'Open this page in a headset browser (Quest, Vision Pro) or a WebXR emulator.';

  try {
    const r = await fetch('data/targets.json');
    const j = await r.json();
    S.targets = j.targets;
    renderPrograms(); renderTargets();
  } catch { toast('targets.json missing — run scripts/build_targets.py', true); }

  S.library.addEventListener('change', renderLibrary);
  await S.library.load();
  renderLibrary();

  loadRDKit().then(() => status('ready')).catch(() => toast('RDKit.js failed to load; chemistry features are offline', true));

  const t = S.targets.find((x) => x.symbol === 'SOD1');
  if (t) openTarget(t);
  status('ready');
}

boot();
Object.assign(S, { scene, camera, renderer, workspace, model, overlay, xr, controls });
window.AGI = S; // handy for the console
