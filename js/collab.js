// Shared sessions: several people (headset or desktop) in the same molecular workspace.
// Transport is the local server: POST state, receive everyone else's over server-sent events.
// Avatars are a head and two hands; the room also syncs what is loaded and where the ligand sits.
import * as THREE from 'three';

const COLORS = [0x39d98a, 0x4cc9f0, 0xf72585, 0xffbe0b, 0xb388eb, 0xff7f51];

export class Collab extends EventTarget {
  constructor(scene, workspace) {
    super();
    this.scene = scene; this.workspace = workspace;
    this.room = null; this.client = Math.random().toString(36).slice(2, 9);
    this.peers = new Map(); this.es = null; this.lastSend = 0;
    this.group = new THREE.Group(); this.group.name = 'avatars';
    scene.add(this.group);

    // Who currently holds what, as last heard from the server. The server is
    // the authority; this is a cache so the UI can grey out an object without
    // a round trip, and it is corrected by every grab message that arrives.
    this.holders = new Map();       // objectId -> { client, name }
    this.held = new Set();          // objects this client holds
    this.lastRefresh = 0;
    this.camera = null;
  }

  get connected() { return !!this.es; }

  /** Is this object free for me to move right now? */
  canMove(objectId) {
    const holder = this.holders.get(objectId);
    return !holder || holder.client === this.client;
  }

  holderOf(objectId) { return this.holders.get(objectId) || null; }

  join(room, name) {
    this.leave();
    this.room = room; this.name = name || 'researcher';
    this.es = new EventSource(`/api/room/${encodeURIComponent(room)}/events`);
    this.es.onmessage = (e) => {
      const p = JSON.parse(e.data);
      if (p.kind === 'grab') { this.onGrab(p); return; }   // including our own
      if (p.client === this.client) return;
      this.onPeer(p);
    };
    this.es.onerror = () => this.dispatchEvent(new CustomEvent('error', { detail: 'lost connection to the room' }));
    this.dispatchEvent(new CustomEvent('joined', { detail: { room } }));
  }

  leave() {
    // Release anything we are holding before dropping the connection, so the
    // room does not have to wait out the lease on an object nobody is touching.
    for (const objectId of [...this.held]) this.release(objectId);
    if (this.es) { this.es.close(); this.es = null; }
    for (const [, p] of this.peers) this.group.remove(p.obj);
    this.peers.clear(); this.holders.clear(); this.held.clear(); this.room = null;
  }

  /**
   * Ask the server for exclusive hold of an object.
   *
   * The server decides, not us: two people reaching at once each believe they
   * were first, because neither has heard from the other yet. Resolves to true
   * only if the hold was actually granted -- a caller that assumes success will
   * fight the real holder and produce exactly the jitter this prevents.
   */
  async claim(objectId, { refresh = false } = {}) {
    if (!this.es) return false;
    if (refresh && this.held.has(objectId)) {
      const now = performance.now();
      if (now - this.lastRefresh < 1000) return true;   // lease is 5s; 1Hz is ample
      this.lastRefresh = now;
    }
    try {
      const res = await fetch(`/api/room/${encodeURIComponent(this.room)}/grab`, {
        method: 'POST',
        body: JSON.stringify({ client: this.client, name: this.name,
                               object: objectId, action: 'claim' }),
      });
      const out = await res.json();
      if (out.granted) {
        this.held.add(objectId);
        this.holders.set(objectId, { client: this.client, name: this.name });
      } else {
        this.held.delete(objectId);
        if (out.holder) this.holders.set(objectId, { client: out.holder, name: out.holder_name });
        this.dispatchEvent(new CustomEvent('refused', {
          detail: { object: objectId, holder: out.holder_name || 'someone else' } }));
      }
      return Boolean(out.granted);
    } catch {
      return false;    // offline: do not pretend we hold it
    }
  }

  release(objectId) {
    this.held.delete(objectId);
    this.holders.delete(objectId);
    if (!this.es) return;
    fetch(`/api/room/${encodeURIComponent(this.room)}/grab`, {
      method: 'POST',
      body: JSON.stringify({ client: this.client, object: objectId, action: 'release' }),
    }).catch(() => {});
  }

  onGrab(msg) {
    if (msg.holder) this.holders.set(msg.object, { client: msg.holder, name: msg.holder_name });
    else this.holders.delete(msg.object);

    // The server may have given it to someone else while we thought we had it
    // -- after a stall long enough for our lease to lapse. Believe the server.
    if (msg.holder && msg.holder !== this.client) this.held.delete(msg.object);

    this.dispatchEvent(new CustomEvent('grab', {
      detail: { object: msg.object, holder: msg.holder,
                name: msg.holder_name, mine: msg.holder === this.client } }));
  }

  onPeer(p) {
    let peer = this.peers.get(p.client);
    if (!peer) {
      const color = COLORS[this.peers.size % COLORS.length];
      const obj = new THREE.Group();
      const head = new THREE.Mesh(new THREE.SphereGeometry(0.11, 16, 12), new THREE.MeshStandardMaterial({ color, roughness: 0.4 }));
      const nose = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.12, 12), new THREE.MeshStandardMaterial({ color }));
      nose.rotation.x = -Math.PI / 2; nose.position.z = -0.1; head.add(nose);
      const hands = [0, 1].map(() => new THREE.Mesh(new THREE.OctahedronGeometry(0.045), new THREE.MeshStandardMaterial({ color, roughness: 0.3 })));
      obj.add(head, ...hands);
      this.group.add(obj);
      peer = { obj, head, hands, color };
      this.peers.set(p.client, peer);
      this.dispatchEvent(new CustomEvent('peer', { detail: { name: p.name, count: this.peers.size } }));
    }
    if (p.head) { peer.head.position.fromArray(p.head.p); peer.head.quaternion.fromArray(p.head.q); }
    (p.hands || []).forEach((h, i) => peer.hands[i] && peer.hands[i].position.fromArray(h));
    peer.last = performance.now();
    if (p.state) this.dispatchEvent(new CustomEvent('state', { detail: p.state }));
  }

  // Called each frame; throttled to ~12 Hz.
  tick(camera, controllers, state = null) {
    if (!this.es) return;
    this.camera = camera;          // share() needs a real camera; see below
    const now = performance.now();
    this.sweepPeers(now);
    if (now - this.lastSend < 80 && !state) return;
    this.lastSend = now;
    const payload = { client: this.client, name: this.name,
      head: { p: camera.getWorldPosition(new THREE.Vector3()).toArray(), q: camera.getWorldQuaternion(new THREE.Quaternion()).toArray() },
      hands: controllers.map((c) => c.getWorldPosition(new THREE.Vector3()).toArray()), state };
    fetch(`/api/room/${encodeURIComponent(this.room)}`, { method: 'POST', body: JSON.stringify(payload) }).catch(() => {});
  }

  /**
   * Drop peers we have stopped hearing from.
   *
   * Without this an avatar left by a closed tab stands in the room forever.
   * Worse than untidy: people talk to it, and the peer count stays wrong, so
   * "three of us are in here" keeps being true after everyone has gone.
   */
  sweepPeers(now = performance.now(), timeout = 8000) {
    for (const [id, peer] of this.peers) {
      if (peer.last && now - peer.last > timeout) {
        this.group.remove(peer.obj);
        peer.obj.traverse?.((o) => { o.geometry?.dispose?.(); o.material?.dispose?.(); });
        this.peers.delete(id);
        this.dispatchEvent(new CustomEvent('left', {
          detail: { name: peer.name, count: this.peers.size } }));
      }
    }
  }

  // Push a discrete change (loaded target, compound, pose) to everyone.
  //
  // This used to read `this._cam`, which was never assigned anywhere, so the
  // fallback ran every time and every share() reported a head position of
  // (0,0,0). Loading a target teleported your avatar to the world origin in
  // front of everyone, then the next tick snapped it back -- which read as the
  // room being glitchy rather than as a bug with a cause.
  share(state) {
    if (!this.es) return;
    if (this.camera) { this.tick(this.camera, [], state); return; }
    // Genuinely no camera yet (sharing before the first frame). Send the state
    // without a pose rather than inventing one at the origin.
    fetch(`/api/room/${encodeURIComponent(this.room)}`, {
      method: 'POST',
      body: JSON.stringify({ client: this.client, name: this.name, state }),
    }).catch(() => {});
  }
}
