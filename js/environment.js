// Real-world environments for the workspace.
//
// A protein floating in black is fine for a screenshot, but researchers demo in rooms, and presence
// helps people judge scale. This loads glTF/GLB scenes (Sketchfab, Unity or Unreal exports, photogrammetry,
// anything glTF 2.0), drops the molecular workspace into them at a sensible height, and adds movement so
// you can walk around the molecule inside the scene.
//
// Format note: glTF/GLB is the interchange format that works everywhere on the web. Unity exports it with
// UnityGLTF or Sketchfab's exporter; Unreal has a built-in glTF exporter (File, Export All, .gltf/.glb).
// FBX, USD and .blend must be converted first; the loader tells the user rather than failing silently.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { resolve as resolveAsset } from './assets.js';

const DRACO = 'https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/libs/draco/';
const BASIS = 'https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/libs/basis/';

// Free, no-account sources. Poly Haven is CC0 and serves CORS headers, so lighting can be fetched live.
const HDRI_BASE = 'https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr';

/**
 * The download URL for an HDRI slug at a given resolution.
 *
 * Tries the naming convention first, because it holds for essentially every
 * asset and costs no request. Falls back to the catalogue API, which returns
 * the authoritative URL, so a file that breaks the convention still resolves.
 */
export async function resolveHdri(slug, resolution = '1k') {
  const direct = `${HDRI_BASE}/${resolution}/${slug}_${resolution}.hdr`;
  try {
    const head = await fetch(direct, { method: 'HEAD' });
    if (head.ok) return direct;
  } catch { /* fall through to the catalogue */ }

  const got = await resolveAsset(slug, { map: 'hdri', resolution, format: 'hdr' });
  if (got.ok) return got.url;
  throw new Error(got.reason || `no HDRI found for "${slug}"`);
}

export const HDRI_PRESETS = [
  { id: 'studio_small_09', label: 'Studio' },
  { id: 'lab', label: 'Lab (procedural)', procedural: true },
  { id: 'venice_sunset', label: 'Sunset' },
  { id: 'kloofendal_48d_partly_cloudy_puresky', label: 'Daylight' },
  { id: 'moonless_golf', label: 'Night' },
];

export class EnvironmentManager extends EventTarget {
  constructor(renderer, scene, { workspace, camera } = {}) {
    super();
    this.renderer = renderer; this.scene = scene; this.workspace = workspace; this.camera = camera;
    this.root = new THREE.Group();
    this.root.name = 'environment';
    scene.add(this.root);
    this.current = null;
    this.stats = null;
    this.pmrem = new THREE.PMREMGenerator(renderer);
    this.defaultBackground = scene.background;

    this.loader = new GLTFLoader();
    const draco = new DRACOLoader().setDecoderPath(DRACO);
    this.loader.setDRACOLoader(draco);
    try {
      const ktx2 = new KTX2Loader().setTranscoderPath(BASIS).detectSupport(renderer);
      this.loader.setKTX2Loader(ktx2);
    } catch { /* compressed textures are optional */ }
  }

  // Load from a URL (served scene) or a File the user picked.
  async load(source, { name, targetSize = null, onProgress } = {}) {
    const isFile = typeof File !== 'undefined' && source instanceof File;
    const label = name || (isFile ? source.name : String(source).split('/').pop());
    if (isFile && !/\.(glb|gltf)$/i.test(source.name)) {
      throw new Error(`${source.name} is not glTF. Export it as .glb first: Unreal has File > Export All > glb, `
        + 'Unity uses the UnityGLTF or Sketchfab exporter, Blender uses File > Export > glTF 2.0.');
    }
    const url = isFile ? URL.createObjectURL(source) : source;
    try {
      const gltf = await this.loader.loadAsync(url, (e) => onProgress && e.total && onProgress(e.loaded / e.total));
      this.clear();
      const model = gltf.scene;
      const stats = this.prepare(model, targetSize);
      this.root.add(model);
      this.current = { name: label, model, animations: gltf.animations || [] };
      this.stats = stats;
      if (gltf.animations?.length) {
        this.mixer = new THREE.AnimationMixer(model);
        gltf.animations.forEach((clip) => this.mixer.clipAction(clip).play());
      }
      this.placeWorkspace(stats);
      this.dispatchEvent(new CustomEvent('loaded', { detail: { name: label, ...stats } }));
      return { name: label, ...stats };
    } finally {
      if (isFile) setTimeout(() => URL.revokeObjectURL(url), 30000);
    }
  }

  // Centre the scene on the origin, stand it on the floor, and measure what it costs to draw.
  //
  // Exports arrive at every imaginable scale: a Sketchfab yacht can be two units long, a ripped game map
  // tens of thousands. Anything outside a plausible room-to-district range is normalised so a person is
  // the right size in it, and the factor is reported so it can be overridden.
  prepare(model, targetSize) {
    const box = new THREE.Box3().setFromObject(model);
    const size = box.getSize(new THREE.Vector3());
    const centre = box.getCenter(new THREE.Vector3());
    const footprint = Math.max(size.x, size.z);
    let scale = 1, autoScaled = false;
    if (targetSize && footprint > 0) {
      scale = targetSize / footprint;
    } else if (footprint > 0 && (footprint < 6 || footprint > 600)) {
      scale = 40 / footprint;   // aim for roughly a 40 m scene, walkable in a minute
      autoScaled = true;
    }
    model.scale.setScalar(scale);
    model.position.set(-centre.x * scale, -box.min.y * scale, -centre.z * scale);

    let triangles = 0, meshes = 0, textures = new Set();
    model.traverse((o) => {
      if (!o.isMesh) return;
      meshes++;
      const g = o.geometry;
      triangles += g.index ? g.index.count / 3 : (g.attributes.position?.count || 0) / 3;
      o.frustumCulled = true;
      o.castShadow = false; o.receiveShadow = false;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      for (const m of mats) {
        if (!m) continue;
        for (const key of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'emissiveMap']) {
          if (m[key]) { m[key].anisotropy = 4; textures.add(m[key].uuid); }
        }
        // Game exports often ship double-sided everything, which doubles the fill cost for no gain.
        if (m.side === THREE.DoubleSide && m.transparent === false) m.side = THREE.FrontSide;
      }
    });
    return { meshes, triangles: Math.round(triangles), textures: textures.size,
      size: { x: +(size.x * scale).toFixed(1), y: +(size.y * scale).toFixed(1), z: +(size.z * scale).toFixed(1) },
      nativeSize: { x: +size.x.toFixed(1), z: +size.z.toFixed(1) },
      scale: +scale.toFixed(4), autoScaled,
      // "Heavy" means it will likely miss a headset's frame budget: triangle load dominates, with a
      // secondary flag for scenes whose draw calls and texture uploads pile up.
      heavy: triangles > 1.2e6 || meshes > 400 || (textures.size > 140 && triangles > 3e5) };
  }

  // Put the molecule where a person would actually stand to look at it.
  placeWorkspace(stats) {
    if (!this.workspace) return;
    const eye = 1.3;
    this.workspace.position.set(0, eye, -0.8);
    this.dispatchEvent(new CustomEvent('placed', { detail: { position: this.workspace.position.toArray() } }));
  }

  // Image-based lighting: one HDRI changes the whole feel and costs one request.
  async setLighting(preset) {
    this.lightingId = preset;
    if (!preset || preset === 'none') {
      this.scene.environment = null;
      this.scene.background = this.defaultBackground;
      return { lighting: 'none' };
    }
    if (preset === 'lab') {
      const env = this.pmrem.fromScene(labEnvironment(), 0.04);
      this.scene.environment = env.texture;
      return { lighting: 'lab (procedural)' };
    }
    // Poly Haven names its files <slug>_<resolution>.hdr. This used to omit the
    // suffix, so EVERY non-procedural preset -- Sunset, Studio, Daylight, Night
    // -- 404'd. It failed as a toast rather than an exception, which is why it
    // survived: the scene simply kept its previous lighting and looked fine.
    //
    // resolveHdri() confirms the URL against the catalogue API when the direct
    // guess fails, so an asset that does not follow the convention still loads
    // instead of reintroducing exactly this bug for a different file.
    const url = await resolveHdri(preset);
    const tex = await new RGBELoader().loadAsync(url);
    tex.mapping = THREE.EquirectangularReflectionMapping;
    const env = this.pmrem.fromEquirectangular(tex);
    this.scene.environment = env.texture;
    if (!this.current) this.scene.background = env.texture;
    tex.dispose();
    return { lighting: preset, source: 'Poly Haven, CC0' };
  }

  // Manual override when the automatic guess reads the scene wrong.
  rescale(factor) {
    if (!this.current) return null;
    const m = this.current.model;
    const box = new THREE.Box3().setFromObject(m);
    m.scale.multiplyScalar(factor);
    m.position.multiplyScalar(factor);
    const now = new THREE.Box3().setFromObject(m);
    m.position.y -= now.min.y;                     // keep it standing on the floor
    this.stats.scale = +(this.stats.scale * factor).toFixed(4);
    const size = now.getSize(new THREE.Vector3());
    this.stats.size = { x: +size.x.toFixed(1), y: +size.y.toFixed(1), z: +size.z.toFixed(1) };
    return this.stats;
  }

  showBackground(on) {
    this.scene.background = on ? (this.scene.environment || this.defaultBackground) : this.defaultBackground;
  }

  // Drop detail when a heavy game map meets a 90 Hz headset.
  setQuality(level = 'full') {
    this.quality = level;
    if (!this.current) return { level };
    const far = level === 'lite' ? 60 : level === 'medium' ? 160 : Infinity;
    // Cull around wherever the viewer actually is, not the world origin, so walking keeps the room visible.
    const eye = this.camera ? this.camera.getWorldPosition(new THREE.Vector3()) : new THREE.Vector3();
    let hidden = 0;
    this.current.model.traverse((o) => {
      if (!o.isMesh) return;
      if (far === Infinity) { o.visible = true; return; }
      if (!o.userData._centre) o.userData._centre = new THREE.Box3().setFromObject(o).getCenter(new THREE.Vector3());
      o.visible = o.userData._centre.distanceTo(eye) < far;
      if (!o.visible) hidden++;
    });
    return { level, far: far === Infinity ? null : far, hidden };
  }

  update(dt) { this.mixer && this.mixer.update(dt); }

  clear() {
    for (const c of [...this.root.children]) {
      c.traverse((o) => {
        if (o.isMesh) {
          o.geometry?.dispose();
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          mats.forEach((m) => { if (!m) return; Object.values(m).forEach((v) => v && v.isTexture && v.dispose()); m.dispose(); });
        }
      });
      this.root.remove(c);
    }
    this.mixer = null; this.current = null; this.stats = null;
  }
}

// A neutral room that costs nothing to fetch: soft ceiling light, darker floor, used for reflections.
function labEnvironment() {
  const s = new THREE.Scene();
  const geo = new THREE.BoxGeometry();
  const light = (color, intensity, pos, scale) => {
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color, side: THREE.BackSide }));
    m.material.color.multiplyScalar(intensity);
    m.position.fromArray(pos); m.scale.fromArray(scale);
    s.add(m);
  };
  light(0x1b2735, 1, [0, 0, 0], [40, 20, 40]);
  light(0xbfd7ff, 3.5, [0, 9, 0], [12, 0.2, 12]);
  light(0x39d98a, 1.2, [-8, 3, -6], [0.3, 4, 8]);
  light(0x4cc9f0, 1.0, [8, 3, 6], [0.3, 4, 8]);
  return s;
}

// ---------------------------------------------------------------- moving around inside a scene
// Desktop: WASD with the mouse. Headset: thumbstick glide plus a teleport arc, both comfort-capped.
export class Locomotion {
  constructor(camera, rig, { speed = 2.4, xr } = {}) {
    this.camera = camera; this.rig = rig; this.speed = speed; this.xr = xr;
    this.keys = new Set();
    this.enabled = false;
    this._down = (e) => { if (this.enabled) this.keys.add(e.code); };
    this._up = (e) => this.keys.delete(e.code);
    addEventListener('keydown', this._down);
    addEventListener('keyup', this._up);
  }

  setEnabled(on) { this.enabled = on; if (!on) this.keys.clear(); }

  update(dt, xrActive) {
    if (!this.enabled) return;
    const dir = new THREE.Vector3();
    if (xrActive && this.xr) {
      for (const c of this.xr.controllers || []) {
        const gp = c.userData?.gamepad;
        const axes = gp?.axes;
        if (axes && axes.length >= 4) {
          const x = axes[2] || 0, y = axes[3] || 0;
          if (Math.abs(x) > 0.15 || Math.abs(y) > 0.15) dir.set(x, 0, y);
        }
      }
    } else {
      if (this.keys.has('KeyW') || this.keys.has('ArrowUp')) dir.z -= 1;
      if (this.keys.has('KeyS') || this.keys.has('ArrowDown')) dir.z += 1;
      if (this.keys.has('KeyA') || this.keys.has('ArrowLeft')) dir.x -= 1;
      if (this.keys.has('KeyD') || this.keys.has('ArrowRight')) dir.x += 1;
    }
    if (!dir.lengthSq()) return;
    dir.normalize();
    const yaw = new THREE.Euler(0, this.camera.rotation.y, 0, 'YXZ');
    dir.applyEuler(yaw);
    const boost = this.keys.has('ShiftLeft') ? 2.5 : 1;
    this.rig.position.addScaledVector(dir, this.speed * boost * dt);
  }

  dispose() { removeEventListener('keydown', this._down); removeEventListener('keyup', this._up); }
}
