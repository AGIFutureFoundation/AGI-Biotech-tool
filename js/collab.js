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
  }

  get connected() { return !!this.es; }

  join(room, name) {
    this.leave();
    this.room = room; this.name = name || 'researcher';
    this.es = new EventSource(`/api/room/${encodeURIComponent(room)}/events`);
    this.es.onmessage = (e) => {
      const p = JSON.parse(e.data);
      if (p.client === this.client) return;
      this.onPeer(p);
    };
    this.es.onerror = () => this.dispatchEvent(new CustomEvent('error', { detail: 'lost connection to the room' }));
    this.dispatchEvent(new CustomEvent('joined', { detail: { room } }));
  }

  leave() {
    if (this.es) { this.es.close(); this.es = null; }
    for (const [, p] of this.peers) this.group.remove(p.obj);
    this.peers.clear(); this.room = null;
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
    const now = performance.now();
    if (now - this.lastSend < 80 && !state) return;
    this.lastSend = now;
    const payload = { client: this.client, name: this.name,
      head: { p: camera.getWorldPosition(new THREE.Vector3()).toArray(), q: camera.getWorldQuaternion(new THREE.Quaternion()).toArray() },
      hands: controllers.map((c) => c.getWorldPosition(new THREE.Vector3()).toArray()), state };
    fetch(`/api/room/${encodeURIComponent(this.room)}`, { method: 'POST', body: JSON.stringify(payload) }).catch(() => {});
  }

  // Push a discrete change (loaded target, compound, pose) to everyone.
  share(state) { if (this.es) this.tick(this._cam || { getWorldPosition: () => new THREE.Vector3(), getWorldQuaternion: () => new THREE.Quaternion() }, [], state); }
}
