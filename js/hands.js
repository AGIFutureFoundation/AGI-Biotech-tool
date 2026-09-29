// Controller-free hand interaction, written against the WebXR Hand Input module
// (https://www.w3.org/TR/webxr-hand-input-1/): XRInputSource.hand + XRFrame.getJointPose().
//
// Gestures, per hand, evaluated once per XR frame in update(frame, referenceSpace):
//   pinch      thumb-tip to index-finger-tip distance, with hysteresis (pinchThreshold / releaseThreshold)
//   tap        pinch held < 250 ms without moving: a click
//   grab       one-hand pinch held or moved: the workspace follows the hand (relative matrix kept from pinch start)
//   two hands  both pinching: scale + yaw the workspace about the point between the hands (suppresses grab)
//   point      index extended, middle and ring curled: a picking ray from the index finger
//   palm up    palm normal faces the head within 50 degrees: show a menu
//   swipe      fast horizontal wrist motion (> 0.6 m/s over ~150 ms, relative to the head): next / previous compound
//
// Poses are read in `referenceSpace`, which is assumed to coincide with three.js world space (no camera rig offset).
import * as THREE from 'three';

const ACCENT = new THREE.Color('#39d98a'), JOINT_COLOR = new THREE.Color('#cfd8e6');
const SCALE_MIN = 0.002, SCALE_MAX = 0.2;
const TAP_MS = 250, TAP_TRAVEL = 0.015;  // a pinch shorter and stiller than this is a tap; otherwise it becomes a grab
const SWIPE_SPEED = 0.6, SWIPE_WINDOW = 150, SWIPE_COOLDOWN = 600;
const PALM_COS = Math.cos(THREE.MathUtils.degToRad(50));
const POINT_RATIO = 1.35;                // index tip this much further from the wrist than middle/ring tips
const SMOOTH = 0.5;                      // exponential filter on pinch points
const RAY_LENGTH = 3, JOINTS = 25;

const _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _head = new THREE.Vector3(), _right = new THREE.Vector3();
const _m = new THREE.Matrix4(), _m2 = new THREE.Matrix4(), _s = new THREE.Vector3(), _q = new THREE.Quaternion();

// Yaw angle of a horizontal direction, so that rotating by θ about +Y adds θ.
const yawOf = (d) => Math.atan2(-d.z, d.x);

export class HandTracking extends EventTarget {
  constructor(renderer, scene, { workspace, pinchThreshold = 0.022, releaseThreshold = 0.035 } = {}) {
    super();
    this.renderer = renderer; this.scene = scene; this.workspace = workspace;
    this.pinchThreshold = pinchThreshold; this.releaseThreshold = Math.max(releaseThreshold, pinchThreshold);
    this.group = new THREE.Group(); this.group.name = 'hand-tracking';
    scene.add(this.group);
    this._state = { left: this._makeHand('left'), right: this._makeHand('right') };
    this.grab = null;       // { type: 'one', h, local } | { type: 'two', m0, s0, mid0, yaw0, d0 }
  }

  _makeHand(handedness) {
    const geo = new THREE.SphereGeometry(1, 10, 8);
    const mat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 });
    const mesh = new THREE.InstancedMesh(geo, mat, JOINTS);
    mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    mesh.frustumCulled = false; mesh.count = 0;
    for (let i = 0; i < JOINTS; i++) mesh.setColorAt(i, JOINT_COLOR);
    const lineGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(0, 0, -RAY_LENGTH)]);
    const ray = new THREE.Line(lineGeo, new THREE.LineBasicMaterial({ color: ACCENT, transparent: true, opacity: 0.7 }));
    ray.visible = false; ray.frustumCulled = false;
    this.group.add(mesh, ray);
    return {
      mesh, ray, tracked: false, joints: new Map(),
      public: { handedness, pinching: false, pinchPoint: new THREE.Vector3(), pointing: false, palmUp: false,
        rayOrigin: new THREE.Vector3(), rayDirection: new THREE.Vector3(0, 0, -1) },
      wristQuat: new THREE.Quaternion(), rawPinch: new THREE.Vector3(), smoothed: false,
      pinchStart: 0, pinchFrom: new THREE.Vector3(), pinchTravel: 0, startAnchor: null, grabbing: false,
      history: [], lastSwipe: 0,
    };
  }

  get hands() {
    const f = (h) => (h.tracked ? h.public : null);
    return { left: f(this._state.left), right: f(this._state.right) };
  }

  setVisible(v) { this.group.visible = !!v; }

  _emit(type, detail) { this.dispatchEvent(new CustomEvent(type, { detail })); }

  // ------------------------------------------------ per-frame
  update(frame, referenceSpace) {
    if (!frame || !referenceSpace) return;
    const now = performance.now();
    this.renderer.xr.getCamera().getWorldPosition(_head);
    const seen = new Set();
    for (const source of frame.session.inputSources) {
      if (!source.hand || (source.handedness !== 'left' && source.handedness !== 'right')) continue;
      const h = this._state[source.handedness];
      if (this._readJoints(h, source.hand, frame, referenceSpace)) { seen.add(source.handedness); this._gestures(h, now); }
    }
    for (const k of ['left', 'right']) if (!seen.has(k)) this._lost(this._state[k]);
    this._twoHand();
    this._applyGrab();
  }

  _readJoints(h, hand, frame, space) {
    const mesh = h.mesh; let i = 0;
    h.joints.clear();
    for (const [name, jointSpace] of hand.entries()) {
      const pose = frame.getJointPose(jointSpace, space);
      if (!pose) continue;
      const p = pose.transform.position, o = pose.transform.orientation, r = pose.radius || 0.008;
      h.joints.set(name, { p: new THREE.Vector3(p.x, p.y, p.z), r });
      if (name === 'wrist') h.wristQuat.set(o.x, o.y, o.z, o.w);
      if (i < JOINTS) {
        _m.compose(_v.set(p.x, p.y, p.z), _q.set(o.x, o.y, o.z, o.w), _s.setScalar(r));
        mesh.setMatrixAt(i, _m);
        const tip = name === 'thumb-tip' || name === 'index-finger-tip';
        mesh.setColorAt(i, tip && h.public.pinching ? ACCENT : JOINT_COLOR);
        i++;
      }
    }
    mesh.count = i; mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    const ok = ['wrist', 'thumb-tip', 'index-finger-tip', 'middle-finger-tip'].every((n) => h.joints.has(n));
    h.tracked = ok; mesh.visible = ok;
    return ok;
  }

  _gestures(h, now) {
    const J = (n) => h.joints.get(n)?.p, s = h.public, hd = s.handedness;
    const wrist = J('wrist'), thumb = J('thumb-tip'), index = J('index-finger-tip'), middle = J('middle-finger-tip');

    // Pinch with hysteresis; the pinch point is the smoothed midpoint of thumb and index tips.
    const gap = thumb.distanceTo(index);
    h.rawPinch.copy(thumb).add(index).multiplyScalar(0.5);
    if (!h.smoothed) { s.pinchPoint.copy(h.rawPinch); h.smoothed = true; } else s.pinchPoint.lerp(h.rawPinch, SMOOTH);
    if (!s.pinching && gap < this.pinchThreshold) {
      s.pinching = true; h.pinchStart = now; h.pinchFrom.copy(s.pinchPoint); h.pinchTravel = 0;
      h.startAnchor = this._anchor(h, new THREE.Matrix4());
      this._emit('pinchstart', { handedness: hd, position: s.pinchPoint.clone() });
    } else if (s.pinching && gap > this.releaseThreshold) {
      this._endPinch(h, now);
    } else if (s.pinching) {
      h.pinchTravel = Math.max(h.pinchTravel, s.pinchPoint.distanceTo(h.pinchFrom));
      this._emit('pinchmove', { handedness: hd, position: s.pinchPoint.clone() });
      if (!h.grabbing && (h.pinchTravel > TAP_TRAVEL || now - h.pinchStart > TAP_MS)) this._grabStart(h);
    }

    // Pointing: index extended while middle and ring are curled.
    const dI = index.distanceTo(wrist), ring = J('ring-finger-tip');
    const curled = dI > POINT_RATIO * middle.distanceTo(wrist) && (!ring || dI > POINT_RATIO * ring.distanceTo(wrist));
    const pointing = curled && !s.pinching;
    if (pointing) {
      const base = J('index-finger-phalanx-proximal') || J('index-finger-metacarpal') || wrist;
      s.rayOrigin.copy(index); s.rayDirection.copy(index).sub(base).normalize();
      h.ray.position.copy(index); h.ray.quaternion.setFromUnitVectors(_v.set(0, 0, -1), s.rayDirection);
      this._emit('point', { handedness: hd, origin: s.rayOrigin.clone(), direction: s.rayDirection.clone() });
    }
    s.pointing = pointing; h.ray.visible = pointing;

    // Palm up: palm normal (sign depends on handedness) points toward the head.
    const im = J('index-finger-metacarpal'), pm = J('pinky-finger-metacarpal');
    if (im && pm) {
      const a = _v.copy(im).sub(wrist), b = _v2.copy(pm).sub(wrist);
      const n = hd === 'right' ? a.cross(b) : b.cross(a).clone();
      n.normalize();
      const toHead = _v2.copy(_head).sub(wrist).normalize();
      const up = n.dot(toHead) > PALM_COS;
      if (up !== s.palmUp) { s.palmUp = up; this._emit(up ? 'palmup' : 'palmdown', { handedness: hd, position: wrist.clone() }); }
    }

    // Swipe: horizontal wrist velocity (along the head's right vector) over the last ~150 ms.
    h.history.push({ t: now, p: wrist.clone() });
    while (h.history.length > 2 && now - h.history[0].t > SWIPE_WINDOW) h.history.shift();
    const first = h.history[0], dt = (now - first.t) / 1000;
    if (!s.pinching && dt > 0.08 && now - h.lastSwipe > SWIPE_COOLDOWN) {
      this.renderer.xr.getCamera().getWorldDirection(_v);
      _right.set(-_v.z, 0, _v.x).normalize();          // horizontal right of the view direction
      const dx = _v2.copy(wrist).sub(first.p).dot(_right) / dt;
      if (Math.abs(dx) > SWIPE_SPEED) {
        h.lastSwipe = now; h.history.length = 0;
        this._emit('swipe', { handedness: hd, direction: dx > 0 ? 'right' : 'left', position: wrist.clone(), speed: Math.abs(dx) });
      }
    }
  }

  _endPinch(h, now = performance.now()) {
    const s = h.public;
    if (!s.pinching) return;
    s.pinching = false;
    const quick = now - h.pinchStart < TAP_MS && h.pinchTravel < TAP_TRAVEL;
    this._emit('pinchend', { handedness: s.handedness, position: s.pinchPoint.clone() });
    if (h.grabbing) this._grabEnd(h);
    else if (quick) this._emit('tap', { handedness: s.handedness, position: s.pinchPoint.clone() });
  }

  _lost(h) {
    if (h.public.pinching) this._endPinch(h, Infinity);   // Infinity: tracking loss is never a tap
    if (h.public.palmUp) { h.public.palmUp = false; this._emit('palmdown', { handedness: h.public.handedness }); }
    h.tracked = false; h.smoothed = false; h.public.pointing = false; h.history.length = 0;
    h.mesh.visible = false; h.ray.visible = false;
  }

  // ------------------------------------------------ workspace manipulation
  // Anchor pose for a one-hand grab: the smoothed pinch point, oriented like the wrist.
  _anchor(h, out) { return out.compose(h.public.pinchPoint, h.wristQuat, _s.set(1, 1, 1)); }

  _grabStart(h) {
    h.grabbing = true;
    if (this.grab && this.grab.type === 'two') return;     // two-hand gesture suppresses single-hand grab
    this._rebaseOne(h, h.startAnchor);
    this._emit('grabstart', { handedness: h.public.handedness, position: h.public.pinchPoint.clone() });
  }

  _grabEnd(h) {
    h.grabbing = false;
    if (this.grab && this.grab.type === 'one' && this.grab.h === h) {
      this.grab = null;
      this._emit('grabend', { handedness: h.public.handedness, position: h.public.pinchPoint.clone() });
    }
  }

  _rebaseOne(h, from) {
    if (!this.workspace) return;
    this.workspace.updateMatrixWorld();
    const a = from || this._anchor(h, new THREE.Matrix4());
    this.grab = { type: 'one', h, local: a.clone().invert().multiply(this.workspace.matrixWorld) };
    h.startAnchor = null;
  }

  _twoHand() {
    const L = this._state.left, R = this._state.right;
    const both = L.tracked && R.tracked && L.public.pinching && R.public.pinching;
    const active = this.grab && this.grab.type === 'two';
    if (both && !active) {
      if (this.grab && this.grab.type === 'one') {
        const g = this.grab.h; this.grab = null;
        this._emit('grabend', { handedness: g.public.handedness, position: g.public.pinchPoint.clone(), reason: 'twohand' });
      }
      if (!this.workspace) return;
      this.workspace.updateMatrixWorld();
      const a = L.public.pinchPoint, b = R.public.pinchPoint, d = _v.copy(b).sub(a);
      this.grab = { type: 'two', m0: this.workspace.matrixWorld.clone(), s0: this.workspace.getWorldScale(_s).x,
        mid0: a.clone().add(b).multiplyScalar(0.5), yaw0: yawOf(d), d0: Math.max(d.length(), 1e-3) };
      this._emit('twohandstart', { midpoint: this.grab.mid0.clone(), left: a.clone(), right: b.clone() });
    } else if (!both && active) {
      this.grab = null;
      this._emit('twohandend', {});
      // A hand still pinching picks the single-hand grab back up from where it is now: no jump.
      for (const h of [L, R]) if (h.grabbing && h.public.pinching) {
        this._rebaseOne(h);
        this._emit('grabstart', { handedness: h.public.handedness, position: h.public.pinchPoint.clone() });
        break;
      }
    }
  }

  _applyGrab() {
    const g = this.grab, ws = this.workspace;
    if (!g || !ws) return;
    if (g.type === 'one') {
      _m.multiplyMatrices(this._anchor(g.h, _m2), g.local);
      this._setWorld(_m);
      this._emit('grabmove', { handedness: g.h.public.handedness, position: g.h.public.pinchPoint.clone(),
        workspacePosition: ws.getWorldPosition(new THREE.Vector3()) });
      return;
    }
    const a = this._state.left.public.pinchPoint, b = this._state.right.public.pinchPoint, d = _v.copy(b).sub(a);
    const scale = THREE.MathUtils.clamp(g.s0 * d.length() / g.d0, SCALE_MIN, SCALE_MAX), ratio = scale / g.s0;
    const rotationY = yawOf(d) - g.yaw0;
    const mid = a.clone().add(b).multiplyScalar(0.5);
    // M = T(mid) · Ry · S(ratio) · T(-mid0) · M0 : scale and turn about the point between the hands.
    _m.makeTranslation(mid.x, mid.y, mid.z)
      .multiply(_m2.makeRotationY(rotationY))
      .multiply(_m2.makeScale(ratio, ratio, ratio))
      .multiply(_m2.makeTranslation(-g.mid0.x, -g.mid0.y, -g.mid0.z))
      .multiply(g.m0);
    this._setWorld(_m);
    this._emit('twohandmove', { scale, rotationY, midpoint: mid, left: a.clone(), right: b.clone() });
  }

  // Write a world matrix into the workspace's local transform (respects a non-identity parent).
  _setWorld(world) {
    const ws = this.workspace;
    if (ws.parent) { ws.parent.updateMatrixWorld(); world = _m2.copy(ws.parent.matrixWorld).invert().multiply(world); }
    world.decompose(ws.position, ws.quaternion, ws.scale);
    ws.updateMatrixWorld();
  }

  dispose() {
    for (const h of Object.values(this._state)) {
      if (h.public.pinching) this._endPinch(h, Infinity);
      h.mesh.geometry.dispose(); h.mesh.material.dispose(); h.mesh.dispose?.();
      h.ray.geometry.dispose(); h.ray.material.dispose();
    }
    this.grab = null;
    this.scene.remove(this.group);
  }
}
