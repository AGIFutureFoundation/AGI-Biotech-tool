// Public data sources (all CORS-enabled, no API keys):
//   RCSB PDB (experimental structures), AlphaFold DB (Google DeepMind / EMBL-EBI predicted structures,
//   AlphaMissense variant effects), UniProt, Open Targets Platform (target-disease evidence + drugs;
//   also published as a Google BigQuery dataset), PubChem (all known compounds, 3D conformers,
//   similarity search), ChEMBL (bioactivity; EBI availability varies).
const cache = new Map();

async function http(url, { json = true, body = null, headers = {}, timeout = 45000, method } = {}) {
  const key = url + (body ? JSON.stringify(body) : '');
  if (cache.has(key)) return cache.get(key);
  const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), timeout);
  const p = fetch(url, { method: method || (body ? 'POST' : 'GET'), body: body ? JSON.stringify(body) : undefined,
    headers: body ? { 'Content-Type': 'application/json', ...headers } : headers, signal: ctl.signal })
    .then(async (r) => {
      if (r.status === 204) return json ? null : '';
      if (!r.ok) throw new Error(`${new URL(url).host} ${r.status}`);
      return json ? r.json() : r.text();
    })
    .finally(() => clearTimeout(t));
  cache.set(key, p);
  p.catch(() => cache.delete(key));
  return p;
}

// ---------------------------------------------------------------- RCSB PDB
export const rcsb = {
  file: (id) => http(`https://files.rcsb.org/download/${id.toUpperCase()}.pdb`, { json: false })
    .catch(() => http(`https://files.rcsb.org/download/${id.toUpperCase()}.cif`, { json: false }).then((t) => ({ cif: t }))),
  entry: (id) => http(`https://data.rcsb.org/rest/v1/core/entry/${id.toUpperCase()}`),
  async byUniprot(acc, rows = 25) {
    const q = { query: { type: 'terminal', service: 'text', parameters: { attribute: 'rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession', operator: 'exact_match', value: acc } },
      return_type: 'entry', request_options: { sort: [{ sort_by: 'rcsb_entry_info.resolution_combined', direction: 'asc' }], paginate: { start: 0, rows } } };
    const r = await http('https://search.rcsb.org/rcsbsearch/v2/query', { body: q });
    return r ? { total: r.total_count, ids: r.result_set.map((x) => x.identifier) } : { total: 0, ids: [] };
  },
  async details(ids) {
    if (!ids.length) return [];
    const gql = `{ entries(entry_ids: ${JSON.stringify(ids)}) { rcsb_id struct { title } rcsb_entry_info { resolution_combined experimental_method }
      nonpolymer_entities { nonpolymer_comp { chem_comp { id name formula_weight } } } } }`;
    const r = await http('https://data.rcsb.org/graphql', { body: { query: gql } });
    return (r.data.entries || []).map((e) => ({ id: e.rcsb_id, title: e.struct.title, resolution: (e.rcsb_entry_info.resolution_combined || [])[0],
      method: e.rcsb_entry_info.experimental_method,
      ligands: (e.nonpolymer_entities || []).map((n) => n.nonpolymer_comp.chem_comp).filter((c) => c.formula_weight > 0.15).map((c) => ({ id: c.id, name: c.name })) }));
  },
  // Full-text search across the PDB (any protein, any organism).
  async text(q, rows = 20) {
    const body = { query: { type: 'terminal', service: 'full_text', parameters: { value: q } }, return_type: 'entry', request_options: { paginate: { start: 0, rows } } };
    const r = await http('https://search.rcsb.org/rcsbsearch/v2/query', { body });
    return r ? r.result_set.map((x) => x.identifier) : [];
  },
  ligandSdf: (pdbId, compId) => http(`https://models.rcsb.org/v1/${pdbId.toLowerCase()}/ligand?label_comp_id=${compId}&encoding=sdf`, { json: false }),
};

// ---------------------------------------------------------------- AlphaFold DB (+ AlphaMissense)
export const alphafold = {
  async prediction(acc) { const r = await http(`https://alphafold.ebi.ac.uk/api/prediction/${acc}`); return r && r[0]; },
  async structure(acc) { const p = await this.prediction(acc); if (!p) throw new Error(`No AlphaFold model for ${acc}`); return { meta: p, text: await http(p.pdbUrl, { json: false }) }; },
  // Mean AlphaMissense pathogenicity per residue position (average over the 19 substitutions).
  async missense(acc) {
    const p = await this.prediction(acc);
    if (!p || !p.amAnnotationsUrl) return null;
    const csv = await http(p.amAnnotationsUrl, { json: false });
    const sum = new Map(), cnt = new Map();
    for (const line of csv.split('\n').slice(1)) {
      const [v, score] = line.split(','); if (!v) continue;
      const pos = parseInt(v.slice(1, -1), 10);
      sum.set(pos, (sum.get(pos) || 0) + +score); cnt.set(pos, (cnt.get(pos) || 0) + 1);
    }
    const out = new Map(); for (const [k, s] of sum) out.set(k, s / cnt.get(k));
    return out;
  },
};

// ---------------------------------------------------------------- UniProt
export const uniprot = {
  entry: (acc) => http(`https://rest.uniprot.org/uniprotkb/${acc}?format=json&fields=accession,gene_names,protein_name,sequence,organism_name,cc_function,cc_disease,ft_variant`),
  async searchGene(q, organism = 9606) {
    const r = await http(`https://rest.uniprot.org/uniprotkb/search?query=${encodeURIComponent(`(gene:${q} OR protein_name:${q}) AND organism_id:${organism} AND reviewed:true`)}&fields=accession,gene_primary,protein_name,length&size=10&format=json`);
    return r.results.map((x) => ({ uniprot: x.primaryAccession, symbol: x.genes?.[0]?.geneName?.value || x.primaryAccession,
      name: x.proteinDescription?.recommendedName?.fullName?.value || '', length: x.sequence?.length }));
  },
};

// ---------------------------------------------------------------- Open Targets Platform (GraphQL)
const OT = 'https://api.platform.opentargets.org/api/v4/graphql';
export const openTargets = {
  async q(query, variables = {}) { const r = await http(OT, { body: { query, variables } }); if (r.errors) throw new Error(r.errors[0].message); return r.data; },
  async drugs(ensemblId) {
    const d = await this.q(`query($id:String!){ target(ensemblId:$id){ approvedSymbol drugAndClinicalCandidates { count rows { maxClinicalStage
      drug { id name drugType maximumClinicalStage description mechanismsOfAction { rows { mechanismOfAction actionType } } }
      diseases { disease { id name } } } } } }`, { id: ensemblId });
    const t = d.target; if (!t) return [];
    return t.drugAndClinicalCandidates.rows.map((r) => ({ chembl: r.drug.id, name: r.drug.name, type: r.drug.drugType, stage: r.maxClinicalStage,
      moa: r.drug.mechanismsOfAction?.rows?.[0]?.mechanismOfAction || '', action: r.drug.mechanismsOfAction?.rows?.[0]?.actionType || '',
      diseases: (r.diseases || []).map((x) => x.disease?.name).filter(Boolean).slice(0, 4) }));
  },
  async searchDisease(text) {
    const d = await this.q(`query($q:String!){ search(queryString:$q, entityNames:["disease"], page:{index:0,size:6}){ hits { id name description } } }`, { q: text });
    return d.search.hits;
  },
  async diseaseTargets(efoId, size = 40) {
    const d = await this.q(`query($id:String!,$n:Int!){ disease(efoId:$id){ name associatedTargets(page:{index:0,size:$n}){ count rows { score
      target { id approvedSymbol approvedName proteinIds { id source } } } } } }`, { id: efoId, n: size });
    return { name: d.disease.name, count: d.disease.associatedTargets.count, rows: d.disease.associatedTargets.rows.map((r) => ({
      score: r.score, ensembl: r.target.id, symbol: r.target.approvedSymbol, name: r.target.approvedName,
      uniprot: (r.target.proteinIds.find((p) => p.source === 'uniprot_swissprot') || {}).id })) };
  },
  async searchTarget(text) {
    const d = await this.q(`query($q:String!){ search(queryString:$q, entityNames:["target"], page:{index:0,size:5}){ hits { id name } } }`, { q: text });
    return d.search.hits;
  },
};

// ---------------------------------------------------------------- PubChem
const PC = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug';
const smilesOf = (p) => p.SMILES || p.IsomericSMILES || p.CanonicalSMILES || p.ConnectivitySMILES;
export const pubchem = {
  async byName(name) {
    const r = await http(`${PC}/compound/name/${encodeURIComponent(name)}/property/Title,SMILES,ConnectivitySMILES,MolecularWeight,XLogP,TPSA,InChIKey/JSON`);
    const p = r.PropertyTable.Properties[0]; return { cid: p.CID, title: p.Title, smiles: smilesOf(p), mw: +p.MolecularWeight, xlogp: p.XLogP, tpsa: p.TPSA, inchikey: p.InChIKey };
  },
  async byInchiKey(key) {
    const r = await http(`${PC}/compound/inchikey/${key}/property/Title,SMILES,ConnectivitySMILES/JSON`).catch(() => null);
    const p = r?.PropertyTable?.Properties?.[0]; return p ? { cid: p.CID, title: p.Title, smiles: smilesOf(p) } : null;
  },
  sdf3d: (cid) => http(`${PC}/compound/cid/${cid}/SDF?record_type=3d`, { json: false }),
  // 2D similarity against PubChem's 100M+ compounds.
  async similar(smiles, threshold = 85, max = 25) {
    const key = `pcsim:${smiles}:${threshold}:${max}`;
    if (!cache.has(key)) {
      const url = `${PC}/compound/fastsimilarity_2d/smiles/property/Title,SMILES,ConnectivitySMILES,MolecularWeight/JSON?Threshold=${threshold}&MaxRecords=${max}`;
      const p = fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: 'smiles=' + encodeURIComponent(smiles) })
        .then((r) => (r.ok ? r.json() : r.status === 404 ? null : Promise.reject(new Error(`PubChem ${r.status}`))));
      cache.set(key, p); p.catch(() => cache.delete(key));
    }
    const r = await cache.get(key);
    return (r?.PropertyTable?.Properties || []).map((p) => ({ cid: p.CID, title: p.Title, smiles: smilesOf(p), mw: +p.MolecularWeight }));
  },
  async exact(smiles) {
    const r = await http(`${PC}/compound/fastidentity/smiles/${encodeURIComponent(smiles)}/property/Title/JSON`).catch(() => null);
    return r?.PropertyTable?.Properties || [];
  },
};

// ---------------------------------------------------------------- ChEMBL (optional; EBI outages are common)
const CH = 'https://www.ebi.ac.uk/chembl/api/data';
export const chembl = {
  async targetId(acc) { const r = await http(`${CH}/target.json?target_components__accession=${acc}&target_type=SINGLE%20PROTEIN`, { timeout: 25000 }); return r.targets[0]?.target_chembl_id; },
  async actives(acc, pchembl = 7, limit = 40) {
    const t = await this.targetId(acc); if (!t) return [];
    const r = await http(`${CH}/activity.json?target_chembl_id=${t}&pchembl_value__gte=${pchembl}&limit=${limit}&order_by=-pchembl_value&only=molecule_chembl_id,molecule_pref_name,canonical_smiles,standard_type,standard_value,standard_units,pchembl_value`, { timeout: 30000 });
    return r.activities.map((a) => ({ chembl: a.molecule_chembl_id, name: a.molecule_pref_name, smiles: a.canonical_smiles, type: a.standard_type, value: a.standard_value, units: a.standard_units, pchembl: +a.pchembl_value }));
  },
  async similar(smiles, sim = 70) {
    const r = await http(`${CH}/similarity/${encodeURIComponent(smiles)}/${sim}.json?limit=20&only=molecule_chembl_id,pref_name,similarity,max_phase,molecule_structures`, { timeout: 30000 });
    return r.molecules.map((m) => ({ chembl: m.molecule_chembl_id, name: m.pref_name, similarity: +m.similarity, phase: m.max_phase, smiles: m.molecule_structures?.canonical_smiles }));
  },
};

// ---------------------------------------------------------------- Foldseek (structure similarity search)
// Searches a 3D fold against the whole AlphaFold DB and the PDB - "which known folds look like this one?"
const FS = 'https://search.foldseek.com/api';
export const foldseek = {
  async search(pdbText, { databases = ['afdb50', 'pdb100'], mode = '3diaa', onStatus } = {}) {
    const fd = new FormData();
    fd.append('q', new Blob([pdbText], { type: 'chemical/x-pdb' }), 'query.pdb');
    fd.append('mode', mode);
    databases.forEach((d) => fd.append('database[]', d));
    onStatus && onStatus('submitting structure');
    const ticket = await fetch(`${FS}/ticket`, { method: 'POST', body: fd }).then((r) => r.json());
    if (!ticket.id || ticket.status === 'ERROR') throw new Error('Foldseek rejected the query');
    for (let i = 0; i < 150; i++) {
      const st = await fetch(`${FS}/ticket/${ticket.id}`).then((r) => r.json());
      if (st.status === 'COMPLETE') break;
      if (st.status === 'ERROR') throw new Error('Foldseek search failed');
      onStatus && onStatus(`Foldseek: ${st.status.toLowerCase()} (${i * 2}s)`);
      await new Promise((r) => setTimeout(r, 2000));
    }
    const res = await fetch(`${FS}/result/${ticket.id}/0`).then((r) => r.json());
    return (res.results || []).map((db) => {
      const raw = Array.isArray(db.alignments?.[0]) ? db.alignments.flat() : (db.alignments || []);
      return { db: db.db, hits: raw.map((a) => {
        const [id, ...rest] = String(a.target).split(' ');
        const afMatch = id.match(/^AF-([A-Z0-9]+)-F\d+/i);
        const pdbMatch = id.match(/^([0-9][a-z0-9]{3})[-_.]/i);
        return { id, title: rest.join(' '), seqId: a.seqId, alnLength: a.alnLength, eval: a.eval, prob: a.prob,
          tm: a.alntmscore ?? a.qtmscore ?? null, uniprot: afMatch ? afMatch[1] : null, pdb: pdbMatch ? pdbMatch[1].toUpperCase() : null };
      }) };
    });
  },
};

// ---------------------------------------------------------------- local server
export const server = {
  async health() { try { const r = await fetch('/api/health', { cache: 'no-store' }); return r.ok ? r.json() : null; } catch { return null; } },
  async startMD(spec) { const r = await fetch('/api/md', { method: 'POST', body: JSON.stringify(spec) }); const j = await r.json(); if (!r.ok) throw new Error(j.error); return j.id; },
  async pollMD(id, since = 0) { const r = await fetch(`/api/md/${id}?since=${since}`); return r.json(); },
  async cancelMD(id) { return fetch(`/api/md/${id}/cancel`, { method: 'POST' }); },
  async extract(file) {
    const r = await fetch('/api/extract', { method: 'POST', headers: { 'X-Filename': file.name }, body: await file.arrayBuffer() });
    const j = await r.json(); if (!r.ok) throw new Error(j.error); return j;
  },
  async saveLibrary(lib) { const r = await fetch('/api/library', { method: 'POST', body: JSON.stringify(lib) }); return r.json(); },
  async bigquery(body) { const r = await fetch('/api/bigquery', { method: 'POST', body: JSON.stringify(body) }); const j = await r.json(); if (!r.ok) throw new Error(j.error); return j; },
};
