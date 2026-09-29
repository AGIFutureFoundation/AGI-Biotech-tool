// Do the environment presets actually load?
//
// An eval rather than a test, because it asks a question about the live world:
// whether Poly Haven still serves these files at these URLs. That can fail for
// reasons nobody in this repo controls, and a unit test that goes red when a
// CDN is slow trains people to ignore red.
//
// It exists because every non-procedural preset in the shipped app was 404ing
// -- Sunset, Studio, Daylight and Night had never worked. The URL omitted the
// resolution suffix Poly Haven puts on its filenames. Nothing caught it because
// the failure surfaced as a toast and the scene simply kept its old lighting,
// which looked entirely fine.
//
//   node evals/hdri_presets.mjs            the five built-in presets
//   node evals/hdri_presets.mjs --sample 25  plus 25 random catalogue entries
//
// Exits non-zero if any preset fails, so it works as a release gate.

const BASE = 'https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr';
const API = 'https://api.polyhaven.com';

// Mirrors HDRI_PRESETS in js/environment.js, minus the procedural entries,
// which resolve to no URL at all.
const PRESETS = [
  'studio_small_09',
  'venice_sunset',
  'kloofendal_48d_partly_cloudy_puresky',
  'moonless_golf',
];

const args = process.argv.slice(2);
const sampleSize = args.includes('--sample')
  ? Number(args[args.indexOf('--sample') + 1]) || 25
  : 0;

async function head(url) {
  try {
    const res = await fetch(url, { method: 'HEAD' });
    return res.status;
  } catch (err) {
    return `ERR ${err.message}`;
  }
}

async function check(slug, resolution = '1k') {
  const url = `${BASE}/${resolution}/${slug}_${resolution}.hdr`;
  const status = await head(url);
  return { slug, status, url, ok: status === 200 };
}

async function sample(n) {
  const res = await fetch(`${API}/assets?type=hdris`);
  const all = Object.keys(await res.json());
  const picked = [];
  for (let i = 0; i < n && all.length; i += 1) {
    picked.push(all.splice(Math.floor(Math.random() * all.length), 1)[0]);
  }
  return picked;
}

const results = [];
for (const slug of PRESETS) results.push(await check(slug));

let sampled = [];
if (sampleSize) {
  sampled = await Promise.all((await sample(sampleSize)).map((s) => check(s)));
}

const failed = results.filter((r) => !r.ok);
const sampleFailed = sampled.filter((r) => !r.ok);

console.log('built-in presets');
for (const r of results) console.log(`  ${r.ok ? 'ok  ' : 'FAIL'} ${r.status}  ${r.slug}`);

if (sampled.length) {
  console.log(`\ncatalogue sample (${sampled.length})`);
  console.log(`  ${sampled.length - sampleFailed.length}/${sampled.length} resolved`);
  for (const r of sampleFailed) console.log(`  FAIL ${r.status}  ${r.slug}`);
}

if (failed.length) {
  console.error(`\n${failed.length} built-in preset(s) do not resolve. `
    + 'The environment picker is advertising lighting the app cannot load.');
  process.exit(1);
}
// A couple of stragglers in a random sample is the CDN, not the code. A large
// fraction failing means the naming convention moved.
if (sampled.length && sampleFailed.length > sampled.length * 0.2) {
  console.error(`\n${sampleFailed.length}/${sampled.length} catalogue entries failed. `
    + 'That is too many to be incidental: the filename convention has likely changed.');
  process.exit(1);
}
console.log('\nall presets resolve');
