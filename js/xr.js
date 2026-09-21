// WebXR for the molecular workspace, written against the W3C WebXR Device API
// (https://www.w3.org/TR/webxr/) and the WebXR Hand Input module (https://www.w3.org/TR/webxr-hand-input-1/).
//
// Standards used, and where:
//   navigator.xr.isSessionSupported()            xrSupport(), plus 'devicechange' re-detection
//   navigator.xr.requestSession() + features     XRManager.enter(), from a user gesture only
//   XRReferenceSpace 'local-floor' -> 'local'    picked from session.enabledFeatures before three.js requests it
//   XRSession.requestAnimationFrame              three.js WebXRManager drives renderer.setAnimationLoop from the
//                                                session while presenting, and from window only on the desktop
//   XRSession 'end' / 'visibilitychange'         clean teardown; input and grabs cancelled while blurred/hidden
//   XRInputSource 'select*' / 'squeeze*'         primary action (trigger, hand pinch, Vision Pro transient pointer)
//                                                and grip; targetRayMode and handedness read from the source
//   XRHand + XRFrame.getJointPose()              three.js reads joint poses each frame; the wrist joint is the
//                                                grab anchor for hands, so turning your hand turns the molecule
//
// Interaction model, identical for controllers and hands:
//   point + tap trigger/pinch  -> identify the atom or residue under the ray
//   pinch/trigger and move     -> grab: move and rotate the structure (controllers can also use the grip button)
//   both hands grabbing        -> scale and turn it around the point between your hands
//   during live MD, pressing on the ligand steers it instead
import * as THREE from 'three';
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';
import { XRHandModelFactory } from 'three/addons/webxr/XRHandModelFactory.js';

const SLOTS = 4;              // two hands plus up to two transient pointers (Vision Pro reports both when hands are tracked)
const GRAB_TRAVEL = 0.015;    // metres of travel that turns a held pinch/trigger from a tap into a grab
const SCALE_MIN = 0.001;      // 1 Å = 1 mm
const SCALE_MAX = 0.2;        // 1 Å = 20 cm, close enough to walk into a binding pocket
const RAY_LENGTH = 3;

const _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _q = new THREE.Quaternion(), _m = new THREE.Matrix4(), _m2 = new THREE.Matrix4();
const UP = new THREE.Vector3(0, 1, 0);

// ---------------------------------------------------------------- support detection
// Returns what can actually be entered and, if nothing, why - so the UI can tell the researcher what to do.
export async function xrSupport() {
  if (!window.isSecureContext) return { vr: false, ar: false, reason: 'insecure' };
  if (!('xr' in navigator) || !navigator.xr) return { vr: false, ar: false, reason: 'no-webxr' };
  const q = (mode) => navigator.xr.isSessionSupported(mode).catch(() => false);
  const [vr, ar] = await Promise.all([q('immersive-vr'), q('immersive-ar')]);
  return { vr, ar, reason: vr || ar ? null : 'no-device' };
}

export const XR_REASONS = {
  insecure: 'WebXR needs a secure origin. Serve the app over HTTPS or open it on localhost.',
  'no-webxr': 'This browser has no WebXR. Open the page in a headset browser (Meta Quest, Vision Pro, Pico) or a WebXR-capable desktop Chrome/Edge.',
  'no-device': 'WebXR is available but no headset is connected. Connect one, open the page in the headset browser, or add ?emulate=quest3 to the URL to try the headset interface here.',
};

// Headsets can be plugged in after load (PC VR); re-run detection when the UA says the device set changed.
export function onXRDeviceChange(cb) {
  if (navigator.xr && navigator.xr.addEventListener) navigator.xr.addEventListener('devicechange', cb);
}

// ---------------------------------------------------------------- world-space text
// One fixed-size canvas per label so updating text never reallocates the GPU texture.
class Label {
  constructor(widthM = 0.16, { lines = 3, bg = 'rgba(10,15,24,0.9)', px = 640 } = {}) {
    this.canvas = document.createElement('canvas');
    this.canvas.width = px; this.canvas.height = 40 + lines * 52;
    this.maxLines = lines; this.bg = bg;
    this.tex = new THREE.CanvasTexture(this.canvas); this.tex.colorSpace = THREE.SRGBColorSpace;
    this.sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.tex, depthTest: false, transparent: true }));
    this.sprite.renderOrder = 30;
    this.sprite.scale.set(widthM, widthM * this.canvas.height / this.canvas.width, 1);
    this.sprite.center.set(0.5, 0);           // anchor at bottom-centre so it sits above the point it describes
    this.sprite.visible = false;
    this.key = '';
  }

  set(lines) {
    const key = lines.join('\n');
    if (key === this.key) return;
    this.key = key;
    const c = this.canvas, ctx = c.getContext('2d');
    ctx.clearRect(0, 0, c.width, c.height);
    const shown = lines.slice(0, this.maxLines);
    const h = 28 + shown.length * 52;
    ctx.fillStyle = this.bg; roundRect(ctx, 0, c.height - h, c.width, h, 18); ctx.fill();
    ctx.strokeStyle = 'rgba(57,217,138,0.55)'; ctx.lineWidth = 3; roundRect(ctx, 1.5, c.height - h + 1.5, c.width - 3, h - 3, 17); ctx.stroke();
    shown.forEach((t, i) => {
      ctx.fillStyle = i === 0 ? '#e8f1ff' : '#a9bdd2';
      ctx.font = i === 0 ? '600 38px system-ui, sans-serif' : '32px system-ui, sans-serif';
      ctx.fillText(fit(ctx, String(t), c.width - 44), 22, c.height - h + 56 + i * 52);
    });
    this.tex.needsUpdate = true;
  }
}

function fit(ctx, s, w) {
  if (ctx.measureText(s).width <= w) return s;
  while (s.length > 1 && ctx.measureText(s + '…').width > w) s = s.slice(0, -1);
  return s + '…';
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}

// ---------------------------------------------------------------- in-world menu
// Docked in the world beside the molecule rather than on a wrist: that works for controllers, tracked hands and
// Vision Pro's transient (gaze-and-pinch) pointers alike, which have no persistent wrist to attach to.
export class WristPanel {
  constructor({ width = 0.26, height = 0.22, columns = 2 } = {}) {
    this.buttons = []; this.columns = columns;
    this.canvas = document.createElement('canvas');
    this.canvas.width = 512; this.canvas.height = Math.round(512 * height / width);
    this.tex = new THREE.CanvasTexture(this.canvas);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    this.mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, height),
      new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, depthTest: false, side: THREE.DoubleSide }));
    this.mesh.renderOrder = 20;
    this.mesh.name = 'xr-menu';
    this.mesh.visible = false;
    this.status = '';
    this.hover = null;
  }

  setButtons(list) { this.buttons = list; this.draw(); }
  setStatus(s) { if (s !== this.status) { this.status = s; this.draw(); } }
  setHover(b) { if (b !== this.hover) { this.hover = b; this.draw(); } }

  layout() {
    const rows = Math.ceil(this.buttons.length / this.columns);
    const w = this.canvas.width / this.columns, h = (this.canvas.height - 64) / Math.max(1, rows);
    return this.buttons.map((b, i) => ({ b, x: (i % this.columns) * w, y: 64 + Math.floor(i / this.columns) * h, w, h }));
  }

  draw() {
    const c = this.canvas, ctx = c.getContext('2d');
    ctx.clearRect(0, 0, c.width, c.height);
    ctx.fillStyle = 'rgba(10,15,24,0.92)'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.fillStyle = '#39d98a'; ctx.font = '600 24px system-ui, sans-serif';
    ctx.fillText('Menu', 16, 30);
    ctx.fillStyle = '#9fb3c8'; ctx.font = '19px system-ui, sans-serif';
    ctx.fillText(fit(ctx, this.status, c.width - 32), 16, 55);
    for (const { b, x, y, w, h } of this.layout()) {
      const active = typeof b.active === 'function' ? b.active() : b.active;
      ctx.fillStyle = active ? 'rgba(57,217,138,0.28)' : b === this.hover ? 'rgba(76,201,240,0.2)' : 'rgba(255,255,255,0.06)';
      ctx.fillRect(x + 6, y + 5, w - 12, h - 10);
      ctx.strokeStyle = active ? '#39d98a' : b === this.hover ? '#4cc9f0' : 'rgba(255,255,255,0.16)'; ctx.lineWidth = 2;
      ctx.strokeRect(x + 6, y + 5, w - 12, h - 10);
      ctx.fillStyle = '#e8f1ff'; ctx.font = '600 22px system-ui, sans-serif';
      const value = typeof b.value === 'function' ? b.value() : b.value;
      ctx.fillText(fit(ctx, String(b.label), w - 36), x + 18, y + h / 2 + (value !== undefined ? -4 : 8));
      if (value !== undefined) { ctx.fillStyle = '#9fb3c8'; ctx.font = '18px system-ui, sans-serif'; ctx.fillText(fit(ctx, String(value), w - 36), x + 18, y + h / 2 + 20); }
    }
    this.tex.needsUpdate = true;
  }

  hit(uv) {
    const px = uv.x * this.canvas.width, py = (1 - uv.y) * this.canvas.height;
    for (const { b, x, y, w, h } of this.layout()) if (px >= x && px <= x + w && py >= y && py <= y + h) return b;
    return null;
  }
}

// ---------------------------------------------------------------- session + input
export class XRManager extends EventTarget {
  constructor(renderer, scene, workspace, camera) {
    super();
    this.renderer = renderer; this.scene = scene; this.workspace = workspace; this.camera = camera;
    this.raycaster = new THREE.Raycaster();
    this.raycaster.params.Line.threshold = 0.004;
    this.pickTargets = [];
    this.describe = null;          // (hit) => string[] | null, supplied by the app: what is under the ray
    this.priority = null;          // () => Object3D[] picked ahead of pickTargets
    this.panel = new WristPanel();
    this.scene.add(this.panel.mesh);
    this.hint = new Label(0.5, { lines: 5, bg: 'rgba(8,14,22,0.94)', px: 1080 });
    this.selection = new Label(0.2, { lines: 4 });
    this.selectionLocal = null;    // workspace-local anchor so the card rides along when the molecule moves
    this.scene.add(this.hint.sprite, this.selection.sprite);
    this.session = null; this.mode = null; this.visible = true;
    this.grab = null; this.frame = 0; this.needsPlacement = false;
    this.hintSeen = { grab: false, tap: false }; this.hintUntil = 0;
    const ctrlFactory = new XRControllerModelFactory(), handFactory = new XRHandModelFactory();
    this.inputs = Array.from({ length: SLOTS }, (_, i) => this._makeInput(i, ctrlFactory, handFactory));
  }

  get active() { return this.renderer.xr.isPresenting; }
  // Used by the collaboration layer to broadcast hand positions.
  get controllers() { return this.inputs.slice(0, 2).map((s) => s.ray); }

  _makeInput(i, ctrlFactory, handFactory) {
    const xr = this.renderer.xr;
    const ray = xr.getController(i), grip = xr.getControllerGrip(i), hand = xr.getHand(i);
    grip.add(ctrlFactory.createControllerModel(grip));
    hand.add(handFactory.createHandModel(hand, 'spheres'));   // procedural joints, no model download
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, -1)]),
      new THREE.LineBasicMaterial({ color: 0x39d98a, transparent: true, opacity: 0.65 }));
    line.scale.z = RAY_LENGTH; line.name = 'ray';
    ray.add(line);
    const reticle = new THREE.Mesh(new THREE.SphereGeometry(0.006, 12, 8), new THREE.MeshBasicMaterial({ color: 0x4cc9f0, depthTest: false }));
    reticle.renderOrder = 25; reticle.visible = false;
    const label = new Label(0.15, { lines: 2 });
    this.scene.add(ray, grip, hand, reticle, label.sprite);
    const s = { i, ray, grip, hand, line, reticle, label, source: null, isHand: false, press: null, grabbing: false };
    ray.addEventListener('connected', (e) => {
      s.source = e.data; s.isHand = !!e.data.hand;
      // Transient pointers (gaze-and-pinch) only exist while pinching: no ray to draw.
      line.visible = e.data.targetRayMode === 'tracked-pointer';
      this._refreshHint();
    });
    ray.addEventListener('disconnected', () => { this._cancel(s); s.source = null; this._hideHover(s); });
    ray.addEventListener('selectstart', () => this._primaryDown(s));
    ray.addEventListener('selectend', () => this._primaryUp(s));
    ray.addEventListener('squeezestart', () => this._grabStart(s));
    ray.addEventListener('squeezeend', () => this._grabEnd(s));
    return s;
  }

  // ------------------------------------------------ lifecycle
  async enter(mode) {
    if (this.session) return this.session;
    if (!navigator.xr) throw new Error(XR_REASONS['no-webxr']);
    // Only ask for what is used: the floor-level space and articulated hands. Unused features cost permission prompts.
    const session = await navigator.xr.requestSession(mode, { optionalFeatures: ['local-floor', 'hand-tracking'] });
    let space = 'local-floor';
    try {
      // three.js requests one reference space and fails the whole session if it is refused, so choose it first.
      if (Array.isArray(session.enabledFeatures)) { if (!session.enabledFeatures.includes('local-floor')) space = 'local'; }
      else space = await session.requestReferenceSpace('local-floor').then(() => 'local-floor', () => 'local');
      this.renderer.xr.setReferenceSpaceType(space);
      await this.renderer.xr.setSession(session);
      this.referenceSpaceType = space;
    } catch (e) {
      session.end().catch(() => {});
      throw e;
    }
    this.session = session; this.mode = mode; this.visible = session.visibilityState !== 'hidden';
    this.frame = 0; this.needsPlacement = true;
    this.hintSeen = { grab: false, tap: false }; this.hintUntil = performance.now() + 25000;
    session.addEventListener('visibilitychange', () => this._onVisibility());
    session.addEventListener('end', () => this._onEnd(), { once: true });
    this.panel.mesh.visible = true;
    this._refreshHint();
    this.dispatchEvent(new CustomEvent('sessionstart', { detail: { mode, space } }));
    return session;
  }

  end() { return this.session ? this.session.end() : Promise.resolve(); }

  _onVisibility() {
    // 'visible-blurred': a system menu is over the app and input is withheld; 'hidden': nothing is shown.
    // Either way any drag in progress has lost its input stream, so drop it rather than leave it stuck.
    this.visible = this.session.visibilityState === 'visible';
    if (!this.visible) { for (const s of this.inputs) { this._cancel(s); this._hideHover(s); } }
    this.dispatchEvent(new CustomEvent('visibility', { detail: { state: this.session.visibilityState } }));
  }

  _onEnd() {
    for (const s of this.inputs) { this._cancel(s); this._hideHover(s); s.source = null; }
    this.grab = null; this.session = null; this.mode = null;
    this.panel.mesh.visible = false; this.hint.sprite.visible = false; this.clearSelection();
    this.dispatchEvent(new CustomEvent('sessionend'));
  }

  // Put the structure about 60 cm in front of the eyes and slightly low, facing the user, with the menu to its left.
  recentre() { this.needsPlacement = true; this.frame = Math.max(this.frame, 3); }

  _place() {
    const cam = this.renderer.xr.getCamera();
    const head = cam.getWorldPosition(new THREE.Vector3());
    const fwd = cam.getWorldDirection(new THREE.Vector3()); fwd.y = 0;
    if (fwd.lengthSq() < 1e-6) fwd.set(0, 0, -1); fwd.normalize();
    const yaw = Math.atan2(-fwd.x, -fwd.z);
    this.workspace.position.copy(head).addScaledVector(fwd, 0.6); this.workspace.position.y = head.y - 0.12;
    this.workspace.quaternion.setFromAxisAngle(UP, yaw);
    const left = _v.set(-fwd.z, 0, fwd.x).negate();   // perpendicular to forward, towards the user's left
    this.panel.mesh.position.copy(head).addScaledVector(fwd, 0.55).addScaledVector(left, 0.36); this.panel.mesh.position.y = head.y - 0.25;
    this.panel.mesh.lookAt(head);
    this.hint.sprite.position.copy(head).addScaledVector(fwd, 0.9); this.hint.sprite.position.y = head.y + 0.12;
    this.needsPlacement = false;
  }

  // ------------------------------------------------ primary action: tap to identify, hold and move to grab
  _ray(s) {
    _m.identity().extractRotation(s.ray.matrixWorld);
    this.raycaster.ray.origin.setFromMatrixPosition(s.ray.matrixWorld);
    this.raycaster.ray.direction.set(0, 0, -1).applyMatrix4(_m);
    return this.raycaster;
  }

  _pick(raycaster) {
    // Priority targets (the ligand during live MD) win even when partly buried in the protein, so they can be steered.
    const pri = this.priority ? this.priority() : [];
    const first = pri.length ? raycaster.intersectObjects(pri, true).find((h) => h.object.visible) : null;
    return first || raycaster.intersectObjects(this.pickTargets, true).find((h) => h.object.visible) || null;
  }

  _panelHit(raycaster) {
    return this.panel.mesh.visible ? raycaster.intersectObject(this.panel.mesh, false)[0] || null : null;
  }

  // The hand's own pose for grabbing: the wrist joint for tracked hands, the grip space for controllers.
  _anchor(s) {
    if (s.isHand) { const w = s.hand.joints && s.hand.joints.wrist; if (w && w.visible) return w; }
    return !s.isHand && s.grip.visible ? s.grip : s.ray;
  }

  _primaryDown(s) {
    if (!this.visible) return;
    const rc = this._ray(s);
    const ph = this._panelHit(rc);
    if (ph) {
      const b = this.panel.hit(ph.uv);
      if (b) { b.onClick && b.onClick(b); this.panel.draw(); this.pulse(s, 0.4, 20); }
      s.press = { panel: true };
      return;
    }
    const hit = this._pick(rc);
    // Let the app claim the press (e.g. steering the ligand during live dynamics) by calling preventDefault().
    const claim = new CustomEvent('pressstart', { detail: { hit, ray: rc, input: s }, cancelable: true });
    if (!this.dispatchEvent(claim)) { s.press = { steering: true }; this.pulse(s, 0.3, 15); return; }
    const a = this._anchor(s); a.updateMatrixWorld();
    // Remember the pose at press time so a grab that starts after GRAB_TRAVEL includes that first bit of movement.
    s.press = { hit, start: a.getWorldPosition(new THREE.Vector3()), startMatrix: a.matrixWorld.clone(), anchor: a };
  }

  _primaryUp(s) {
    const p = s.press; s.press = null;
    if (!p || p.panel) return;
    if (p.steering) { this.dispatchEvent(new CustomEvent('pressend', { detail: { input: s } })); return; }
    if (s.grabbing) { this._grabEnd(s); return; }
    // A tap: identify what was under the ray when the press began.
    if (p.hit) {
      this.hintSeen.tap = true; this._refreshHint();
      this.dispatchEvent(new CustomEvent('pick', { detail: { hit: p.hit } }));
      const lines = this.describe ? this.describe(p.hit) : null;
      if (lines) this.showSelection(lines, p.hit.point);
      this.pulse(s, 0.3, 15);
    }
  }

  _cancel(s) {
    if (s.press && s.press.steering) this.dispatchEvent(new CustomEvent('pressend', { detail: { input: s } }));
    s.press = null;
    if (s.grabbing) { s.grabbing = false; this._rebaseGrab(); }
  }

  showSelection(lines, worldPoint) {
    this.selection.set(lines);
    this.workspace.updateMatrixWorld();
    this.selectionLocal = this.workspace.worldToLocal(worldPoint.clone());
    this.selection.sprite.visible = this.active;
  }

  clearSelection() { this.selectionLocal = null; this.selection.sprite.visible = false; }

  // ------------------------------------------------ grabbing: one hand moves/rotates, two hands scale/turn
  _grabStart(s) {
    if (s.grabbing || !this.visible) return;
    if (s.press && s.press.steering) return;
    s.grabbing = true;
    this.hintSeen.grab = true; this._refreshHint();
    this._rebaseGrab();
    this.pulse(s, 0.25, 15);
  }

  _grabEnd(s) {
    if (!s.grabbing) return;
    s.grabbing = false;
    this._rebaseGrab();
  }

  _rebaseGrab() {
    const g = this.inputs.filter((x) => x.grabbing);
    this.workspace.updateMatrixWorld();
    if (g.length === 1) {
      const a = this._anchor(g[0]); a.updateMatrixWorld();
      const p = g[0].press, from = p && p.startMatrix && p.anchor === a ? p.startMatrix : a.matrixWorld;
      if (p) p.startMatrix = null;
      this.grab = { type: 'one', s: g[0], anchor: a, local: new THREE.Matrix4().copy(from).invert().multiply(this.workspace.matrixWorld) };
    } else if (g.length >= 2) {
      const pa = this._anchor(g[0]).getWorldPosition(new THREE.Vector3()), pb = this._anchor(g[1]).getWorldPosition(new THREE.Vector3());
      this.grab = { type: 'two', a: g[0], b: g[1], m0: this.workspace.matrixWorld.clone(), s0: this.workspace.scale.x,
        mid0: pa.clone().add(pb).multiplyScalar(0.5), dir0: pb.clone().sub(pa).normalize(), d0: Math.max(pa.distanceTo(pb), 1e-3) };
    } else this.grab = null;
  }

  _applyGrab() {
    const g = this.grab;
    if (!g) return;
    if (g.type === 'one') {
      if (this._anchor(g.s) !== g.anchor) return this._rebaseGrab();   // hand tracking dropped the wrist: re-anchor, no jump
      _m.multiplyMatrices(g.anchor.matrixWorld, g.local);
      _m.decompose(this.workspace.position, this.workspace.quaternion, this.workspace.scale);
      return;
    }
    const pa = this._anchor(g.a).getWorldPosition(_v), pb = this._anchor(g.b).getWorldPosition(_v2);
    const ratio = THREE.MathUtils.clamp(g.s0 * pa.distanceTo(pb) / g.d0, SCALE_MIN, SCALE_MAX) / g.s0;
    const mid = pa.clone().add(pb).multiplyScalar(0.5);
    _q.setFromUnitVectors(g.dir0, pb.clone().sub(pa).normalize());
    // M = T(mid) · R · S(ratio) · T(-mid0) · M0 : pivot about the point between the hands.
    _m.makeTranslation(mid.x, mid.y, mid.z)
      .multiply(_m2.makeRotationFromQuaternion(_q))
      .multiply(_m2.makeScale(ratio, ratio, ratio))
      .multiply(_m2.makeTranslation(-g.mid0.x, -g.mid0.y, -g.mid0.z))
      .multiply(g.m0);
    _m.decompose(this.workspace.position, this.workspace.quaternion, this.workspace.scale);
  }

  // ------------------------------------------------ per-frame (called from the XR animation loop)
  update() {
    this.frame++;
    if (this.needsPlacement && this.frame >= 3) this._place();   // wait for a real head pose
    if (!this.visible) return;

    for (const s of this.inputs) {
      if (!s.source) continue;
      // A held press that has travelled far enough becomes a grab.
      if (s.press && s.press.start && !s.grabbing) {
        if (this._anchor(s).getWorldPosition(_v).distanceTo(s.press.start) > GRAB_TRAVEL) this._grabStart(s);
      }
      if (s.press && s.press.steering) this.dispatchEvent(new CustomEvent('drag', { detail: { input: s, ray: this._ray(s) } }));
    }
    this._applyGrab();
    this.workspace.updateMatrixWorld();

    // Hover: what would a tap select? Raycast every other frame per input to keep large structures cheap.
    let panelHover = null;
    for (const s of this.inputs) {
      if (!s.source || s.grabbing || (s.press && s.press.steering) || s.source.targetRayMode !== 'tracked-pointer') { this._hideHover(s); continue; }
      if ((this.frame + s.i) % 2) continue;
      const rc = this._ray(s);
      const ph = this._panelHit(rc);
      if (ph) { panelHover = this.panel.hit(ph.uv) || panelHover; s.line.scale.z = ph.distance; s.reticle.visible = false; s.label.sprite.visible = false; continue; }
      const hit = this._pick(rc);
      if (!hit) { this._hideHover(s); continue; }
      s.line.scale.z = hit.distance;
      s.reticle.position.copy(hit.point); s.reticle.visible = true;
      const lines = this.describe ? this.describe(hit) : null;
      const onSelected = this.selection.sprite.visible && this.selectionLocal &&
        this.workspace.localToWorld(_v.copy(this.selectionLocal)).distanceTo(hit.point) < 0.012;
      if (lines && !onSelected) { s.label.set(lines.slice(0, 2)); s.label.sprite.position.copy(hit.point).y += 0.015; s.label.sprite.visible = true; }
      else s.label.sprite.visible = false;
    }
    this.panel.setHover(panelHover);

    if (this.selectionLocal) {
      this.selection.sprite.position.copy(this.selectionLocal); this.workspace.localToWorld(this.selection.sprite.position);
      this.selection.sprite.position.y += 0.03;
    }
    if (this.hint.sprite.visible && performance.now() > this.hintUntil) this.hint.sprite.visible = false;
  }

  _hideHover(s) { s.reticle.visible = false; s.label.sprite.visible = false; s.line.scale.z = RAY_LENGTH; }

  // ------------------------------------------------ first-use guidance, matched to the input actually in hand
  showHelp(on = true) { this.hintUntil = on ? performance.now() + 30000 : 0; this.hint.sprite.visible = on && this.active; if (on) this._refreshHint(true); }

  _refreshHint(force = false) {
    if (!this.session) return;
    if (!force && this.hintSeen.grab && this.hintSeen.tap) { this.hint.sprite.visible = false; return; }
    const hands = this.inputs.some((s) => s.source && s.isHand);
    const transient = this.inputs.some((s) => s.source && s.source.targetRayMode === 'transient-pointer');
    const tap = hands ? 'Point and pinch' : transient ? 'Look and pinch' : 'Point and pull the trigger';
    const hold = hands || transient ? 'Pinch and move your hand' : 'Hold the grip button (or trigger) and move';
    this.hint.set([
      'How to inspect this structure',
      `${this.hintSeen.tap ? '✓' : '•'} ${tap} on an atom to identify it`,
      `${this.hintSeen.grab ? '✓' : '•'} ${hold} to grab, turn and move it`,
      '• Grab with both hands and pull apart to zoom',
      '• Menu on your left: style, colour, recentre, exit',
    ]);
    this.hint.sprite.visible = this.active && performance.now() < this.hintUntil;
  }

  pulse(s, intensity = 0.4, ms = 20) {
    const act = s.source && s.source.gamepad && s.source.gamepad.hapticActuators && s.source.gamepad.hapticActuators[0];
    if (act && act.pulse) Promise.resolve(act.pulse(intensity, ms)).catch(() => {});
  }
}
