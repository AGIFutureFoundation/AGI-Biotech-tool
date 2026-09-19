// The AGI compound library: import (PDF / CSV / SMI / SDF / JSON), de-duplicate, profile, search, export.
// PDFs are read in the browser with pdf.js, or handed to the local server when it has RDKit + pypdf
// (more reliable). macOS privacy settings never get in the way because you pick the files yourself.
import { analyze, canonical, loadRDKit, tanimoto, substructFilter } from './chem.js';
import { server, pubchem } from './api.js';

const PDFJS = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.min.mjs';
const LS_KEY = 'agi-bioxr-library-v1';

const TOKEN = /[A-Za-z0-9@+\-\[\]()=#$/\\%.]{5,}/g;
const ID_PATTERNS = [
  /\bAGI[\s\-_#:]*(?:Synthetic\s+)?(?:Compound|Cmpd|Cpd)?[\s\-_#:]*(\d{1,4})\b/i,
  /\b(?:Compound|Cmpd|Cpd)[\s\-_#:]*(\d{1,4})\b/i,
  /^\s*(\d{1,4})[.):\-\s]/,
];

let pdfjsLib = null;
async function pdfjs() {
  if (!pdfjsLib) {
    pdfjsLib = await import(/* @vite-ignore */ PDFJS);
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.min.mjs';
  }
  return pdfjsLib;
}

export async function pdfToText(file, onPage) {
  const lib = await pdfjs();
  const doc = await lib.getDocument({ data: await file.arrayBuffer() }).promise;
  const out = [];
  for (let p = 1; p <= doc.numPages; p++) {
    const page = await doc.getPage(p);
    const tc = await page.getTextContent();
    // Group items into visual lines by y position so wrapped SMILES can be re-joined.
    const lines = new Map();
    for (const it of tc.items) {
      const y = Math.round(it.transform[5] / 3);
      (lines.get(y) || lines.set(y, []).get(y)).push(it);
    }
    const sorted = [...lines.entries()].sort((a, b) => b[0] - a[0])
      .map(([, items]) => items.sort((a, b) => a.transform[4] - b.transform[4]).map((i) => i.str).join(' ').replace(/\s{2,}/g, ' ').trim());
    out.push(...sorted);
    onPage && onPage(p, doc.numPages);
  }
  return out.join('\n');
}

// Browser mirror of server/chem_extract.py.
export async function extractFromText(text, source = '') {
  const RD = await loadRDKit();
  const lines = text.replace(/\r/g, '\n').split('\n').map((l) => l.trimEnd());
  const found = [], rejects = [], seen = new Set();
  const parse = (s) => {
    if (s.length < 5 || !/[CcNnOo]/.test(s)) return null;
    const m = RD.get_mol(s);
    if (!m) return null;
    if (!m.is_valid()) { m.delete(); return null; }
    const d = JSON.parse(m.get_descriptors());
    const can = m.get_smiles(); m.delete();
    return d.NumHeavyAtoms >= 6 ? can : null;
  };
  const looksSmilesLine = (l) => !!l && [...l.matchAll(TOKEN)].some((t) => parse(t[0]));
  const findId = (i, prefix) => {
    if (prefix) return +prefix;
    for (const p of ID_PATTERNS) { const m = lines[i].match(p); if (m) return +m[1]; }
    for (let j = i - 1; j >= Math.max(0, i - 2); j--) {
      if (looksSmilesLine(lines[j])) break;
      for (const p of ID_PATTERNS) { const m = lines[j].match(p); if (m) return +m[1]; }
    }
    return null;
  };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const tm of line.matchAll(TOKEN)) {
      let tok = tm[0].replace(/[.,;]+$/, '');
      let prefix = '';
      const lead = tok.match(/^(\d{1,4})(?=[A-Z[])/);
      if (lead) { prefix = lead[1]; tok = tok.slice(lead[1].length); }
      let can = parse(tok), cand = tok, k = i;
      while ((!can || tm.index + tm[0].length >= line.length - 1) && k + 1 < lines.length && k - i < 3) {
        const nxt = (lines[k + 1].trim().split(' ')[0] || '');
        if (!nxt || /[^A-Za-z0-9@+\-[\]()=#$/\\%.]/.test(nxt)) break;
        const joined = parse(cand + nxt);
        if (!joined && can) break;
        if (joined) { can = joined; cand += nxt; } else cand += nxt;
        k++;
      }
      if (!can) {
        if (/[=([]/.test(tok) && (tok.match(/[CNOSc]/g) || []).length >= 4 && tok.length >= 8) rejects.push({ id: findId(i, prefix), raw: tok, source });
        continue;
      }
      if (seen.has(can)) continue;
      seen.add(can);
      found.push({ id: findId(i, prefix), smiles: cand, canonical: can, label: line.slice(0, tm.index).replace(/[:\-\s]+$/, '').slice(0, 80), source });
    }
  }
  return { compounds: found, rejects };
}

export async function parseSdfText(text, source) {
  const RD = await loadRDKit();
  const out = [];
  for (const block of text.split(/\$\$\$\$\s*/)) {
    if (!block.trim()) continue;
    const m = RD.get_mol(block);
    if (m && m.is_valid()) {
      const name = (block.split('\n')[0] || '').trim();
      out.push({ id: (name.match(/(\d{1,4})/) || [])[1] ? +name.match(/(\d{1,4})/)[1] : null, smiles: m.get_smiles(), canonical: m.get_smiles(), label: name, source, molblock: block });
    }
    m && m.delete();
  }
  return { compounds: out, rejects: [] };
}

export async function parseTable(text, source) {
  const RD = await loadRDKit();
  const rows = text.split(/\r?\n/).filter((l) => l.trim());
  const out = [], rejects = [];
  for (const row of rows) {
    const cells = row.split(/[\t,;|]/).map((c) => c.trim().replace(/^"|"$/g, ''));
    let smiles = null, rest = [];
    for (const c of cells) {
      if (!smiles) { const m = RD.get_mol(c); if (m && m.is_valid() && JSON.parse(m.get_descriptors()).NumHeavyAtoms >= 6) { smiles = m.get_smiles(); m.delete(); continue; } m && m.delete(); }
      rest.push(c);
    }
    if (!smiles) { if (cells.length > 1 && /[=([]/.test(row)) rejects.push({ raw: row.slice(0, 120), source }); continue; }
    const idCell = rest.find((c) => /\d/.test(c)) || '';
    out.push({ id: (idCell.match(/(\d{1,4})/) || [])[1] ? +idCell.match(/(\d{1,4})/)[1] : null, smiles, canonical: smiles, label: rest.join(' ').slice(0, 80), source });
  }
  return { compounds: out, rejects };
}

// ---------------------------------------------------------------- library
export class CompoundLibrary extends EventTarget {
  constructor() { super(); this.compounds = []; this.byCanonical = new Map(); this.rejects = []; }

  async load() {
    let data = null;
    try { const r = await fetch('data/agi_compounds.json', { cache: 'no-store' }); if (r.ok) data = await r.json(); } catch { /* optional file */ }
    let local = null;
    try { local = JSON.parse(localStorage.getItem(LS_KEY) || 'null'); } catch { /* ignore */ }
    const merged = [...(data?.compounds || []), ...(local?.compounds || [])];
    for (const c of merged) this.insert(c, false);
    this.rejects = [...(data?.rejects || []), ...(local?.rejects || [])];
    this.emit();
    return this.compounds.length;
  }

  emit() { this.dispatchEvent(new CustomEvent('change', { detail: { n: this.compounds.length } })); }

  insert(c, emit = true) {
    const key = c.canonical || c.smiles;
    if (!key) return null;
    const prev = this.byCanonical.get(key);
    if (prev) {
      prev.sources = [...new Set([...(prev.sources || []), ...(c.sources || [c.source]).filter(Boolean)])];
      if (!prev.agiId && c.agiId) prev.agiId = c.agiId;
      return prev;
    }
    const entry = {
      agiId: c.agiId || (c.id != null ? `AGI-${String(c.id).padStart(3, '0')}` : null),
      smiles: c.smiles, canonical: key, label: c.label || '', sources: c.sources || (c.source ? [c.source] : []),
      tags: c.tags || [], notes: c.notes || '', added: c.added || new Date().toISOString().slice(0, 10),
      profile: c.profile || null, fp: c.fp || null, known: c.known || null,
    };
    this.compounds.push(entry); this.byCanonical.set(key, entry);
    if (emit) this.emit();
    return entry;
  }

  // Number unlabelled compounds in sequence, filling gaps after the highest existing AGI id.
  autoNumber(prefix = 'AGI') {
    let max = 0;
    for (const c of this.compounds) { const m = (c.agiId || '').match(/(\d+)/); if (m) max = Math.max(max, +m[1]); }
    for (const c of this.compounds) if (!c.agiId) c.agiId = `${prefix}-${String(++max).padStart(3, '0')}`;
    this.emit();
  }

  async profileAll(onProgress) {
    let done = 0;
    for (const c of this.compounds) {
      if (!c.profile) {
        try {
          const a = await analyze(c.canonical);
          c.profile = { desc: a.desc, rules: a.rules, inchikey: a.inchikey };
          c.fp = btoa(String.fromCharCode(...a.fp));
        } catch { c.profile = { error: true }; }
      }
      onProgress && onProgress(++done, this.compounds.length);
      if (done % 20 === 0) await new Promise((r) => setTimeout(r, 0));
    }
    this.save(); this.emit();
  }

  fpBytes(c) { return c.fp ? Uint8Array.from(atob(c.fp), (ch) => ch.charCodeAt(0)) : null; }

  similarTo(fp, { limit = 20, exclude = null } = {}) {
    return this.compounds.filter((c) => c.fp && c !== exclude)
      .map((c) => ({ c, sim: tanimoto(fp, this.fpBytes(c)) }))
      .sort((a, b) => b.sim - a.sim).slice(0, limit);
  }

  async substructure(query) {
    const flags = await substructFilter(query, this.compounds.map((c) => c.canonical));
    return this.compounds.filter((_, i) => flags[i]);
  }

  // "Is this already a known compound?" — exact match against PubChem, then nearest known neighbours.
  async checkNovelty(entry) {
    const exact = await pubchem.exact(entry.canonical).catch(() => []);
    const sim = await pubchem.similar(entry.canonical, 85, 10).catch(() => []);
    entry.known = { exact: exact.map((e) => ({ cid: e.CID, title: e.Title })), nearest: sim.slice(0, 5), checked: new Date().toISOString().slice(0, 10) };
    this.save();
    return entry.known;
  }

  search(q) {
    const s = q.trim().toLowerCase();
    if (!s) return this.compounds;
    return this.compounds.filter((c) => (c.agiId || '').toLowerCase().includes(s) || c.label.toLowerCase().includes(s)
      || c.canonical.toLowerCase().includes(s) || c.tags.some((t) => t.toLowerCase().includes(s)));
  }

  filter({ mwMax, clogpMax, cnsOnly, lipinskiClean }) {
    return this.compounds.filter((c) => {
      const d = c.profile?.desc, r = c.profile?.rules;
      if (!d) return false;
      if (mwMax && d.mw > mwMax) return false;
      if (clogpMax && d.clogp > clogpMax) return false;
      if (cnsOnly && !r.bbbLikely) return false;
      if (lipinskiClean && r.lipinskiViolations > 0) return false;
      return true;
    });
  }

  save() {
    const payload = { saved: new Date().toISOString(), compounds: this.compounds, rejects: this.rejects };
    try { localStorage.setItem(LS_KEY, JSON.stringify(payload)); } catch { /* quota */ }
    server.saveLibrary(payload).catch(() => {}); // persists to data/agi_compounds.json when the server runs
  }

  toCSV() {
    const head = 'agi_id,smiles,label,mw,clogp,tpsa,hbd,hba,rotb,cns_mpo5,lipinski_violations,sources\n';
    return head + this.compounds.map((c) => {
      const d = c.profile?.desc || {}, r = c.profile?.rules || {};
      return [c.agiId, c.canonical, JSON.stringify(c.label || ''), d.mw?.toFixed(1), d.clogp?.toFixed(2), d.tpsa?.toFixed(1), d.hbd, d.hba, d.rotb,
        r.cnsMpo5, r.lipinskiViolations, JSON.stringify((c.sources || []).join('; '))].join(',');
    }).join('\n');
  }

  toSmi() { return this.compounds.map((c) => `${c.canonical}\t${c.agiId || ''}`).join('\n'); }
}

// Dispatch an imported file to the right reader.
export async function importFile(file, { useServer = false, onProgress } = {}) {
  const name = file.name.toLowerCase();
  if (name.endsWith('.pages') || name.endsWith('.numbers') || name.endsWith('.key')) {
    throw new Error(`${file.name} is an Apple iWork file. In Pages choose File > Export To > PDF, then import the PDF.`);
  }
  if (name.endsWith('.pdf')) {
    if (useServer) {
      try {
        const r = await server.extract(file);
        return { compounds: r.compounds, rejects: r.rejects, note: r.note, via: 'server (pypdf + RDKit)' };
      } catch (e) { onProgress && onProgress(`server extraction failed (${e.message}); using in-browser reader`); }
    }
    const text = await pdfToText(file, (p, n) => onProgress && onProgress(`reading page ${p}/${n}`));
    const r = await extractFromText(text, file.name);
    return { ...r, via: 'browser (pdf.js + RDKit.js)', note: text.trim() ? null : 'No text layer found: this PDF holds scanned images, so structures need optical recognition first.' };
  }
  const text = await file.text();
  if (name.endsWith('.json')) {
    const j = JSON.parse(text);
    const list = Array.isArray(j) ? j : j.compounds || [];
    return { compounds: await Promise.all(list.map(async (c) => ({ ...c, canonical: c.canonical || await canonical(c.smiles) }))), rejects: [], via: 'json' };
  }
  if (name.endsWith('.sdf') || name.endsWith('.mol')) return { ...(await parseSdfText(text, file.name)), via: 'sdf' };
  if (name.endsWith('.csv') || name.endsWith('.tsv') || name.endsWith('.smi') || name.endsWith('.txt')) return { ...(await parseTable(text, file.name)), via: 'table' };
  return { ...(await extractFromText(text, file.name)), via: 'text' };
}
