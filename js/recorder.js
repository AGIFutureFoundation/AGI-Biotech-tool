// Deterministic video recorder: renders the live scene at 1080p into a composite canvas, draws a branded
// overlay and captions, and encodes H.264 with WebCodecs at fixed timestamps.
//
// Frames are encoded on an explicit clock rather than in real time, so the finished film has exactly the
// intended pacing even when the browser is throttling a background tab. Output is a real .mp4.
import * as THREE from 'three';

// Yield to the event loop without a timer. setTimeout is clamped to once a second in a background tab,
// and spinning on microtasks starves the encoder's own callbacks, so neither works here.
function macrotask() {
  return new Promise((resolve) => {
    const ch = new MessageChannel();
    ch.port1.onmessage = () => { ch.port1.close(); resolve(); };
    ch.port2.postMessage(0);
  });
}

const MUXER = 'https://cdn.jsdelivr.net/npm/mp4-muxer@5.2.1/+esm';

export class Recorder {
  constructor({ scene, camera, width = 1920, height = 1080, fps = 30, bitrate = 10e6 }) {
    this.scene = scene; this.srcCamera = camera; this.w = width; this.h = height; this.fps = fps; this.bitrate = bitrate;
    this.canvas = document.createElement('canvas');
    this.canvas.width = width; this.canvas.height = height;
    this.ctx = this.canvas.getContext('2d', { alpha: false });
    this.gl = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.gl.setClearColor(0x000000, 0);
    this.gl.setPixelRatio(1);
    this.gl.setSize(width, height, false);
    this.gl.outputColorSpace = THREE.SRGBColorSpace;
    this.camera = new THREE.PerspectiveCamera(camera.fov, width / height, camera.near, camera.far);
    this.caption = ''; this.progress = 0; this.stats = {}; this.title = null; this.frameIndex = 0;
  }

  async init() {
    const { Muxer, ArrayBufferTarget } = await import(/* @vite-ignore */ MUXER);
    this.target = new ArrayBufferTarget();
    this.muxer = new Muxer({
      target: this.target,
      video: { codec: 'avc', width: this.w, height: this.h, frameRate: this.fps },
      fastStart: 'in-memory',
    });
    this.encoder = new VideoEncoder({
      output: (chunk, meta) => this.muxer.addVideoChunk(chunk, meta),
      error: (e) => console.error('encoder', e),
    });
    this.encoder.configure({ codec: 'avc1.640028', width: this.w, height: this.h, bitrate: this.bitrate, framerate: this.fps });
  }

  // Render one frame of the live scene plus overlay, then hand it to the encoder.
  async capture() {
    this.camera.position.copy(this.srcCamera.getWorldPosition(new THREE.Vector3()));
    this.camera.quaternion.copy(this.srcCamera.getWorldQuaternion(new THREE.Quaternion()));
    this.camera.updateProjectionMatrix();
    this.gl.render(this.scene, this.camera);
    const c = this.ctx;
    this.drawBackdrop(c);
    c.drawImage(this.gl.domElement, 0, 0, this.w, this.h);
    this.drawOverlay(c);
    const us = Math.round((this.frameIndex * 1e6) / this.fps);
    const frame = new VideoFrame(this.canvas, { timestamp: us, duration: Math.round(1e6 / this.fps) });
    this.encoder.encode(frame, { keyFrame: this.frameIndex % (this.fps * 2) === 0 });
    frame.close();
    this.frameIndex++;
    // Give the event loop a turn so the encoder can deliver chunks, then apply back-pressure.
    await macrotask();
    while (this.encoder.encodeQueueSize > 8) await macrotask();
  }

  async finish() {
    await this.encoder.flush();
    this.muxer.finalize();
    return new Blob([this.target.buffer], { type: 'video/mp4' });
  }

  get seconds() { return this.frameIndex / this.fps; }

  // The WebGL layer is transparent, so the film gets the same deep-space backdrop as the app.
  drawBackdrop(c) {
    if (!this.bg) {
      this.bg = c.createRadialGradient(this.w * 0.5, this.h * 0.42, 60, this.w * 0.5, this.h * 0.42, this.w * 0.72);
      this.bg.addColorStop(0, '#12202f');
      this.bg.addColorStop(0.55, '#0a121d');
      this.bg.addColorStop(1, '#04070c');
    }
    c.fillStyle = this.bg;
    c.fillRect(0, 0, this.w, this.h);
  }

  drawOverlay(c) {
    const W = this.w, H = this.h;
    c.save();
    c.shadowColor = 'rgba(0,0,0,0.85)'; c.shadowBlur = 14;
    c.beginPath(); c.arc(56, 58, 9, 0, 7); c.fillStyle = '#39d98a'; c.fill();
    c.font = '600 34px -apple-system, system-ui, sans-serif';
    c.fillStyle = '#e8f1ff'; c.fillText('biodao', 78, 70);
    const bw = c.measureText('biodao').width;
    c.fillStyle = '#39d98a'; c.fillText('.blockchain', 78 + bw, 70);
    c.font = '500 17px -apple-system, system-ui, sans-serif'; c.fillStyle = '#93a7bd';
    c.fillText('POWERED BY AGI CORP', 80, 96);
    c.restore();

    const rows = Object.entries(this.stats).filter(([, v]) => v != null && v !== '');
    if (rows.length) {
      c.save();
      c.font = '500 23px ui-monospace, SFMono-Regular, Menlo, monospace';
      const boxW = 440, boxH = rows.length * 36 + 28;
      const x = W - boxW - 52, y = 44;
      c.fillStyle = 'rgba(10,18,30,0.88)';
      this.roundRect(c, x, y, boxW, boxH, 12); c.fill();
      c.strokeStyle = 'rgba(57,217,138,0.4)'; c.lineWidth = 1.5; c.stroke();
      rows.forEach(([k, v], i) => {
        const ly = y + 38 + i * 36;
        c.fillStyle = '#93a7bd'; c.fillText(k, x + 20, ly);
        c.fillStyle = '#e8f1ff'; c.textAlign = 'right'; c.fillText(String(v), x + boxW - 20, ly); c.textAlign = 'left';
      });
      c.restore();
    }

    if (this.caption) {
      c.save();
      c.font = '500 33px -apple-system, system-ui, sans-serif';
      const lines = this.wrap(c, this.caption, W - 340);
      const boxH = lines.length * 46 + 46, by = H - boxH - 70;
      c.fillStyle = 'rgba(7,13,21,0.93)';
      this.roundRect(c, 120, by, W - 240, boxH, 14); c.fill();
      c.fillStyle = '#39d98a'; c.fillRect(120, by, 5, boxH);
      c.fillStyle = '#e8f1ff';
      lines.forEach((l, i) => c.fillText(l, 154, by + 46 + i * 46));
      c.restore();
      c.fillStyle = 'rgba(255,255,255,0.12)'; c.fillRect(120, H - 44, W - 240, 4);
      c.fillStyle = '#39d98a'; c.fillRect(120, H - 44, (W - 240) * Math.min(1, this.progress), 4);
    }

    if (this.title) {
      const t = this.title;
      c.save();
      c.globalAlpha = 1;
      c.fillStyle = `rgba(5,8,14,${t.alpha})`; c.fillRect(0, 0, W, H);
      c.globalAlpha = t.alpha;
      c.textAlign = 'center';
      c.fillStyle = '#e8f1ff'; c.font = '600 92px -apple-system, system-ui, sans-serif';
      c.fillText(t.main, W / 2, H / 2 - 18);
      c.fillStyle = '#39d98a'; c.font = '500 36px -apple-system, system-ui, sans-serif';
      c.fillText(t.sub, W / 2, H / 2 + 50);
      if (t.note) { c.fillStyle = '#93a7bd'; c.font = '400 25px -apple-system, system-ui, sans-serif'; c.fillText(t.note, W / 2, H / 2 + 104); }
      c.restore();
    }
  }

  wrap(c, text, max) {
    const out = []; let line = '';
    for (const w of text.split(' ')) {
      const t = line ? `${line} ${w}` : w;
      if (c.measureText(t).width > max && line) { out.push(line); line = w; } else line = t;
    }
    if (line) out.push(line);
    return out;
  }

  roundRect(c, x, y, w, h, r) {
    c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath();
  }

  async upload(blob, name = 'walkthrough.mp4') {
    const r = await fetch(`/api/recording?name=${encodeURIComponent(name)}`, { method: 'POST', body: blob });
    return r.json();
  }
}
