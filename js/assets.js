// Poly Haven asset catalogue: ~2,400 CC0 environments, textures and models.
//
// The app already streamed its five HDRIs from dl.polyhaven.org rather than
// vendoring them. This generalises that: the same CDN hosts 997 HDRIs, 862
// textures and 521 models, and the catalogue is a public JSON API. So "more
// asset options" is a browse-and-resolve problem, not a storage one. Nothing
// here is committed to the repo and the checkout does not grow.
//
// TWO THINGS THIS MODULE IS CAREFUL ABOUT.
//
// Size. An 8k texture is a 37 MB JPEG; its PNG is 131 MB. A picker that hands
// those to a browser on a conference wifi has broken the session, and in an XR
// headset it will drop frames or crash the tab. Every resolve() reports the
// byte size it is about to pull, 1k is the default, and anything above
// LARGE_BYTES has to be asked for explicitly via `allowLarge`.
//
// Absence. The catalogue is a third-party service. When it is unreachable the
// app must still work, so every entry point falls back to the built-in presets
// and says which mode it is in. An environment picker that empties itself
// because someone else's API is down is worse than one that never had 997
// options.
//
// Licensing: everything on Poly Haven is CC0, so no attribution is legally
// required. Authors are carried anyway and shown in the UI, because taking
// someone's work without crediting it is a choice, not a default.

const API = 'https://api.polyhaven.com';

export const TYPES = ['hdris', 'textures', 'models'];

// Browser-sane default. 1k is ~1-2 MB and is what the existing HDRI loader
// already used; 4k+ is an opt-in for a desktop with a real GPU.
export const DEFAULT_RESOLUTION = '1k';

// Above this, resolve() refuses without an explicit allowLarge.
export const LARGE_BYTES = 12 * 1024 * 1024;

export const CATALOGUE_UNAVAILABLE =
  'Asset catalogue unavailable (Poly Haven did not respond). Falling back to the '
  + 'built-in presets. This is a network problem, not a missing feature.';

const cache = new Map();

async function getJSON(url, { timeout = 15000 } = {}) {
  if (cache.has(url)) return cache.get(url);
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), timeout);
  try {
    const res = await fetch(url, { signal: ctl.signal });
    if (!res.ok) throw new Error(`Poly Haven ${res.status}`);
    const data = await res.json();
    cache.set(url, data);
    return data;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * The catalogue for one asset type, as an array of records.
 *
 * Returns { ok, assets, error }. Never throws: a browse UI that explodes when
 * a third party is down takes the whole workspace with it.
 */
export async function catalogue(type = 'hdris') {
  if (!TYPES.includes(type)) throw new Error(`unknown asset type: ${type}`);
  try {
    const raw = await getJSON(`${API}/assets?type=${type}`);
    const assets = Object.entries(raw).map(([slug, meta]) => ({
      slug,
      type,
      name: meta.name || slug,
      categories: meta.categories || [],
      tags: meta.tags || [],
      authors: Object.keys(meta.authors || {}),
      maxResolution: meta.max_resolution || null,
      published: meta.date_published ? new Date(meta.date_published * 1000) : null,
    }));
    assets.sort((a, b) => a.name.localeCompare(b.name));
    return { ok: true, assets, error: null };
  } catch (err) {
    return { ok: false, assets: [], error: `${CATALOGUE_UNAVAILABLE} (${err.message})` };
  }
}

/** Every category present in a catalogue, with counts, for building a filter UI. */
export function categories(assets) {
  const counts = new Map();
  for (const asset of assets) {
    for (const category of asset.categories) {
      counts.set(category, (counts.get(category) || 0) + 1);
    }
  }
  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

/**
 * Filter a catalogue by free text and/or category.
 *
 * Text matches name, slug, categories and tags, so "lab", "clean" and
 * "fluorescent" all find something useful without the user knowing the
 * vocabulary Poly Haven happens to use.
 */
export function search(assets, { text = '', category = null, limit = 0 } = {}) {
  const needle = text.trim().toLowerCase();
  let out = assets;

  if (category) out = out.filter((a) => a.categories.includes(category));
  if (needle) {
    out = out.filter((a) => {
      const hay = `${a.name} ${a.slug} ${a.categories.join(' ')} ${a.tags.join(' ')}`;
      return hay.toLowerCase().includes(needle);
    });
  }
  return limit ? out.slice(0, limit) : out;
}

/** Which resolutions and formats a given asset actually offers. */
export async function variants(slug) {
  try {
    const files = await getJSON(`${API}/files/${encodeURIComponent(slug)}`);
    return { ok: true, files, error: null };
  } catch (err) {
    return { ok: false, files: null, error: err.message };
  }
}

function pickNode(files, { map, resolution, format }) {
  // HDRIs expose {hdr: {1k: {...}}}; textures expose named maps such as
  // Diffuse / nor_gl / Rough. Both bottom out at {resolution: {format: {url}}}.
  const branch = files[map] || files.hdri || files.hdr || null;
  if (!branch) return null;
  const byRes = branch[resolution] || branch[DEFAULT_RESOLUTION]
    || branch[Object.keys(branch)[0]];
  if (!byRes) return null;
  return byRes[format] || byRes.jpg || byRes.hdr || byRes[Object.keys(byRes)[0]] || null;
}

/**
 * Resolve one downloadable file, refusing to silently pull something huge.
 *
 * Returns { ok, url, bytes, tooLarge, reason }. `tooLarge` is not an error --
 * it is the caller's decision to make, with the number in front of them.
 */
export async function resolve(slug, {
  map = 'hdri', resolution = DEFAULT_RESOLUTION, format = null, allowLarge = false,
} = {}) {
  const got = await variants(slug);
  if (!got.ok) return { ok: false, url: null, bytes: 0, tooLarge: false, reason: got.error };

  const preferred = format || (map === 'hdri' ? 'hdr' : 'jpg');
  const node = pickNode(got.files, { map, resolution, format: preferred });
  if (!node || !node.url) {
    return { ok: false, url: null, bytes: 0, tooLarge: false,
             reason: `no ${map} map at ${resolution} for ${slug}` };
  }

  const bytes = node.size || 0;
  if (bytes > LARGE_BYTES && !allowLarge) {
    return {
      ok: false, url: node.url, bytes, tooLarge: true,
      reason: `${formatBytes(bytes)} is above the ${formatBytes(LARGE_BYTES)} limit. `
            + 'Choose a lower resolution, or pass allowLarge to fetch it anyway.',
    };
  }
  return { ok: true, url: node.url, bytes, tooLarge: false, reason: null };
}

export function formatBytes(bytes) {
  if (!bytes) return 'unknown size';
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Trailing debounce, for search-as-you-type.
 *
 * Here rather than in main.js because the reason it exists belongs to this
 * module: without it, every keystroke filters ~1,000 records and, on the first
 * one, starts a catalogue fetch.
 */
export function debounce(fn, ms = 250) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

/** Credit line for an asset. CC0 needs none; showing one is the decent default. */
export function credit(asset) {
  const who = asset.authors && asset.authors.length ? asset.authors.join(', ') : 'Poly Haven';
  return `${asset.name} — ${who} (CC0, Poly Haven)`;
}
