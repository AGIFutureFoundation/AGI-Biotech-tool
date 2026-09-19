// WebXR: immersive VR and passthrough AR, controllers/hands, grab-scale-rotate, ligand steering,
// and an in-headset wrist menu so the whole tool works without the desktop panels.
import * as THREE from 'three';
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';

const _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _q = new THREE.Quaternion(), _m = new THREE.Matrix4();

export class WristPanel {
  constructor({ width = 0.26, height = 0.2, columns = 2 } = {}) {
    this.buttons = []; this.columns = columns;
    this.canvas = document.createElement('canvas');
    this.canvas.width = 512; this.canvas.height = Math.round(512 * height / width);
    this.tex = new THREE.CanvasTexture(this.canvas);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    this.mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, height),
      new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, depthTest: false }));
    this.mesh.renderOrder = 20;
    this.mesh.name = 'wrist-panel';
    this.mesh.visible = false;
    this.status = '';
  }

  setButtons(list) { this.buttons = list; this.draw(); }
  setStatus(s) { if (s !== this.status) { this.status = s; this.draw(); } }

  layout() {
    const rows = Math.ceil(this.buttons.length / this.columns);
    const w = this.canvas.width / this.columns, h = (this.canvas.height - 64) / Math.max(1, rows);
    return this.buttons.map((b, i) => ({ b, x: (i % this.columns) * w, y: 64 + Math.floor(i / this.columns) * h, w, h }));
  }

  draw() {
    const c = this.canvas, ctx = c.getContext('2d');
    ctx.clearRect(0, 0, c.width, c.height);
    ctx.fillStyle = 'rgba(10,15,24,0.92)'; ctx.fillRect(0, 0, c.width, c.height);
    ctx.fillStyle = '#39d98a'; ctx.font = '600 26px system-ui, sans-serif';
    ctx.fillText('biodao.blockchain', 16, 34);
    ctx.fillStyle = '#9fb3c8'; ctx.font = '20px system-ui, sans-serif';
    ctx.fillText(this.status.slice(0, 44), 16, 58);
    for (const { b, x, y, w, h } of this.layout()) {
      ctx.fillStyle = b.active ? 'rgba(57,217,138,0.28)' : 'rgba(255,255,255,0.06)';
      ctx.fillRect(x + 6, y + 5, w - 12, h - 10);
      ctx.strokeStyle = b.active ? '#39d98a' : 'rgba(255,255,255,0.16)'; ctx.lineWidth = 2;
      ctx.strokeRect(x + 6, y + 5, w - 12, h - 10);
      ctx.fillStyle = '#e8f1ff'; ctx.font = '600 22px system-ui, sans-serif';
      ctx.fillText(String(b.label).slice(0, 18), x + 18, y + h / 2 + 2);
      if (b.value !== undefined) { ctx.fillStyle = '#9fb3c8'; ctx.font = '18px system-ui, sans-serif'; ctx.fillText(String(b.value).slice(0, 20), x + 18, y + h / 2 + 26); }
    }
    this.tex.needsUpdate = true;
  }

  hit(uv) {
    const px = uv.x * this.canvas.width, py = (1 - uv.y) * this.canvas.height;
    for (const { b, x, y, w, h } of this.layout()) if (px >= x && px <= x + w && py >= y && py <= y + h) return b;
    return null;
  }
}

export class XRManager extends EventTarget {
  constructor(renderer, scene, workspace, camera) {
    super();
    this.renderer = renderer; this.scene = scene; this.workspace = workspace; this.camera = camera;
    this.controllers = []; this.grips = [];
    this.raycaster = new THREE.Raycaster();
    this.panel = new WristPanel();
    this.grabState = null;
    this.pickTargets = [];
    this.mode = 'inspect'; // 'inspect' | 'steer' | 'measure'
    this.setup();
  }

  setup() {
    const factory = new XRControllerModelFactory();
    for (let i = 0; i < 2; i++) {
      const c = this.renderer.xr.getController(i);
      c.userData.index = i;
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, -1)]),
        new THREE.LineBasicMaterial({ color: 0x39d98a, transparent: true, opacity: 0.7 }));
      line.scale.z = 5; line.name = 'ray';
      c.add(line);
      c.addEventListener('selectstart', (e) => this.onSelect(c, true, e));
      c.addEventListener('selectend', (e) => this.onSelect(c, false, e));
      c.addEventListener('squeezestart', () => this.onSqueeze(c, true));
      c.addEventListener('squeezeend', () => this.onSqueeze(c, false));
      c.addEventListener('connected', (e) => { c.userData.handedness = e.data.handedness; this.placePanel(); });
      this.scene.add(c);
      this.controllers.push(c);
      const g = this.renderer.xr.getControllerGrip(i);
      g.add(factory.createControllerModel(g));
      this.scene.add(g);
      this.grips.push(g);
    }
    this.placePanel();
  }

  placePanel() {
    const left = this.controllers.find((c) => c.userData.handedness === 'left') || this.controllers[0];
    if (this.panel.mesh.parent) this.panel.mesh.parent.remove(this.panel.mesh);
    left.add(this.panel.mesh);
    this.panel.mesh.position.set(0.0, 0.06, -0.08);
    this.panel.mesh.rotation.set(-Math.PI / 3.2, 0, 0);
  }

  get active() { return this.renderer.xr.isPresenting; }

  pointerRay(controller) {
    _m.identity().extractRotation(controller.matrixWorld);
    this.raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
    this.raycaster.ray.direction.set(0, 0, -1).applyMatrix4(_m);
    return this.raycaster;
  }

  onSelect(controller, down) {
    if (down) {
      const ray = this.pointerRay(controller);
      const other = this.controllers.find((c) => c !== controller);
      const panelHit = this.panel.mesh.visible ? ray.intersectObject(this.panel.mesh, false)[0] : null;
      if (panelHit && controller !== this.panel.mesh.parent) {
        const b = this.panel.hit(panelHit.uv);
        if (b) { b.onClick && b.onClick(b); this.panel.draw(); this.pulse(controller, 0.4, 20); return; }
      }
      const hits = ray.intersectObjects(this.pickTargets, true).filter((h) => h.object.visible);
      this.dispatchEvent(new CustomEvent('pick', { detail: { hit: hits[0], controller, ray } }));
      if (hits[0]) this.pulse(controller, 0.3, 15);
      controller.userData.selecting = true;
    } else {
      controller.userData.selecting = false;
      this.dispatchEvent(new CustomEvent('pickend', { detail: { controller } }));
    }
  }

  pulse(controller, intensity = 0.4, ms = 20) {
    const gp = controller.userData.gamepad || (this.renderer.xr.getSession()?.inputSources || [])[controller.userData.index]?.gamepad;
    const act = gp?.hapticActuators?.[0];
    act && act.pulse && act.pulse(intensity, ms);
  }

  onSqueeze(controller, down) {
    controller.userData.squeezing = down;
    const both = this.controllers.filter((c) => c.userData.squeezing);
    if (both.length === 2) {
      const d = both[0].position.distanceTo(both[1].position);
      this.grabState = { type: 'scale', d0: d, s0: this.workspace.scale.x,
        mid0: _v.copy(both[0].position).add(both[1].position).multiplyScalar(0.5).clone(), p0: this.workspace.position.clone(),
        yaw0: Math.atan2(both[1].position.x - both[0].position.x, both[1].position.z - both[0].position.z), rot0: this.workspace.rotation.y };
    } else if (both.length === 1 && down) {
      const c = both[0];
      this.grabState = { type: 'move', controller: c, inv: new THREE.Matrix4().copy(c.matrixWorld).invert(),
        local: this.workspace.matrixWorld.clone().premultiply(new THREE.Matrix4().copy(c.matrixWorld).invert()) };
    } else if (!both.length) this.grabState = null;
  }

  update() {
    // Grab-move / two-handed scale of the whole molecular workspace.
    const g = this.grabState;
    if (g && g.type === 'move' && g.controller.userData.squeezing) {
      const m = new THREE.Matrix4().multiplyMatrices(g.controller.matrixWorld, g.local);
      m.decompose(this.workspace.position, this.workspace.quaternion, this.workspace.scale);
    } else if (g && g.type === 'scale') {
      const [a, b] = this.controllers;
      if (a.userData.squeezing && b.userData.squeezing) {
        const d = a.position.distanceTo(b.position);
        const s = Math.max(0.02, Math.min(6, g.s0 * (d / Math.max(g.d0, 1e-3))));
        this.workspace.scale.setScalar(s);
        const mid = _v.copy(a.position).add(b.position).multiplyScalar(0.5);
        this.workspace.position.copy(g.p0).add(_v2.copy(mid).sub(g.mid0));
        const yaw = Math.atan2(b.position.x - a.position.x, b.position.z - a.position.z);
        this.workspace.rotation.y = g.rot0 + (yaw - g.yaw0);
      }
    }
    // Continuous pointer for steering / hover.
    for (const c of this.controllers) {
      if (!c.userData.selecting) continue;
      const ray = this.pointerRay(c);
      this.dispatchEvent(new CustomEvent('drag', { detail: { controller: c, ray } }));
    }
  }

  setPanelVisible(v) { this.panel.mesh.visible = v; }
}

export async function xrSupport() {
  if (!navigator.xr) return { vr: false, ar: false };
  const [vr, ar] = await Promise.all([
    navigator.xr.isSessionSupported('immersive-vr').catch(() => false),
    navigator.xr.isSessionSupported('immersive-ar').catch(() => false),
  ]);
  return { vr, ar };
}

export async function startSession(renderer, mode, onEnd) {
  const init = mode === 'immersive-ar'
    ? { optionalFeatures: ['local-floor', 'bounded-floor', 'hand-tracking', 'layers', 'plane-detection'] }
    : { optionalFeatures: ['local-floor', 'bounded-floor', 'hand-tracking', 'layers'] };
  const session = await navigator.xr.requestSession(mode, init);
  await renderer.xr.setSession(session);
  session.addEventListener('end', onEnd);
  return session;
}
