// Offline harness for js/assets.js.
//
// The catalogue functions that matter are pure -- search, categories, credit,
// formatBytes -- plus resolve(), which is the one that decides whether to pull
// 37 MB into a browser. fetch is stubbed here with recorded Poly Haven shapes
// so all of that runs with no network, and the test that drives this harness
// stays deterministic in CI.
//
// Prints one JSON object on stdout. Exits non-zero on an internal error.

const CATALOGUE = {
  venice_sunset: {
    type: 0, name: 'Venice Sunset',
    categories: ['outdoor', 'sunrise-sunset', 'natural light'],
    tags: ['sunset', 'water', 'city'],
    authors: { 'Greg Zaal': 'All' }, max_resolution: [16384, 8192],
    date_published: 1500000000,
  },
  studio_small_09: {
    type: 0, name: 'Studio Small 09',
    categories: ['indoor', 'studio', 'artificial light'],
    tags: ['clean', 'softbox'],
    authors: { 'Andreas Mischok': 'All' }, max_resolution: [8192, 4096],
    date_published: 1600000000,
  },
  lab_bench_02: {
    type: 0, name: 'Lab Bench 02',
    categories: ['indoor', 'studio'], tags: ['laboratory', 'clean', 'clinical'],
    authors: { 'Someone Else': 'All' }, max_resolution: [4096, 2048],
    date_published: 1650000000,
  },
};

const FILES = {
  venice_sunset: {
    hdri: {
      '1k': { hdr: { url: 'https://dl.polyhaven.org/venice_sunset_1k.hdr', size: 1440400 } },
      '4k': { hdr: { url: 'https://dl.polyhaven.org/venice_sunset_4k.hdr', size: 22000000 } },
    },
  },
  aerial_asphalt_01: {
    Diffuse: {
      '1k': { jpg: { url: 'https://dl.polyhaven.org/asphalt_diff_1k.jpg', size: 900000 } },
      '8k': { jpg: { url: 'https://dl.polyhaven.org/asphalt_diff_8k.jpg', size: 37506182 } },
    },
  },
};

globalThis.fetch = async (url) => {
  const ok = (body) => ({ ok: true, status: 200, json: async () => body });
  if (url.includes('/assets?type=hdris')) return ok(CATALOGUE);
  if (url.includes('/assets?type=')) return ok({});
  const match = url.match(/\/files\/(.+)$/);
  if (match) {
    const body = FILES[decodeURIComponent(match[1])];
    if (!body) return { ok: false, status: 404, json: async () => ({}) };
    return ok(body);
  }
  return { ok: false, status: 500, json: async () => ({}) };
};

const A = await import(new URL('../../js/assets.js', import.meta.url).href);

const got = await A.catalogue('hdris');
const assets = got.assets;

const out = {
  catalogue_ok: got.ok,
  count: assets.length,
  names: assets.map((a) => a.name),

  // search
  by_text_lab: A.search(assets, { text: 'laboratory' }).map((a) => a.slug),
  by_text_name: A.search(assets, { text: 'venice' }).map((a) => a.slug),
  by_category: A.search(assets, { category: 'studio' }).map((a) => a.slug),
  // 'clean' alone matches both studio environments; adding the text 'clinical'
  // narrows to one. Chosen so the test proves the two filters COMBINE rather
  // than that one of them happens to be a no-op.
  by_category_only: A.search(assets, { category: 'indoor' }).map((a) => a.slug),
  by_both: A.search(assets, { text: 'clinical', category: 'indoor' }).map((a) => a.slug),
  limited: A.search(assets, { limit: 2 }).length,
  no_match: A.search(assets, { text: 'zzzz' }).length,

  categories: A.categories(assets).slice(0, 3),
  credit: A.credit(assets.find((a) => a.slug === 'venice_sunset')),

  // resolve: the size gate is the point
  small: await A.resolve('venice_sunset', { map: 'hdri', resolution: '1k' }),
  large_blocked: await A.resolve('venice_sunset', { map: 'hdri', resolution: '4k' }),
  large_allowed: await A.resolve('venice_sunset',
    { map: 'hdri', resolution: '4k', allowLarge: true }),
  texture_8k_blocked: await A.resolve('aerial_asphalt_01',
    { map: 'Diffuse', resolution: '8k', format: 'jpg' }),
  missing: await A.resolve('does_not_exist', { map: 'hdri' }),

  bytes: [A.formatBytes(0), A.formatBytes(900000), A.formatBytes(37506182)],
  default_resolution: A.DEFAULT_RESOLUTION,
};

// Offline behaviour: the app must survive the catalogue being down.
globalThis.fetch = async () => { throw new Error('network down'); };
const offlineMod = await import(
  `${new URL('../../js/assets.js', import.meta.url).href}?offline=1`);
out.offline = await offlineMod.catalogue('hdris');

process.stdout.write(JSON.stringify(out));
