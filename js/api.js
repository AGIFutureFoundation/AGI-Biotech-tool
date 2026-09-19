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
  const read = async (r) => {
    if (r.status === 204) return json ? null : '';
    if (!r.ok) throw new Error(`${new URL(url).host} ${r.status}`);
    return json ? r.json() : r.text();
  };
  const p = fetch(url, { method: method || (body ? 'POST' : 'GET'), body: body ? JSON.stringify(body) : undefined,
    headers: body ? { 'Content-Type': 'application/json', ...headers } : headers, signal: ctl.signal })
    .then(read)
    // Several public APIs send no CORS headers. When the browser refuses the direct call, retry through the
    // local server's allowlisted read-only proxy, which is the only way those sources are reachable here.
    .catch(async (e) => {
      if (body || method === 'POST' || /abort/i.test(e.name || '')) throw e;
      const r = await fetch(`/api/proxy?url=${encodeURIComponent(url)}`);
      return read(r);
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
  // Patent families that mention this compound (PubChem cross-references, free, no key).
  async patents(cid, limit = 40) {
    const r = await http(`${PC}/compound/cid/${cid}/xrefs/PatentID/JSON`).catch(() => null);
    const list = r?.InformationList?.Information?.[0]?.PatentID || [];
    return { total: list.length, ids: list.slice(0, limit) };
  },
  async exact(smiles) {
    const r = await http(`${PC}/compound/fastidentity/smiles/${encodeURIComponent(smiles)}/property/Title/JSON`).catch(() => null);
    return r?.PropertyTable?.Properties || [];
  },
};

// UniChem: the same molecule's id in every other chemical database.
export const unichem = {
  async xrefs(inchikey) {
    const r = await http(`https://www.ebi.ac.uk/unichem/rest/inchikey/${inchikey}`).catch(() => []);
    const SRC = { 1: 'ChEMBL', 2: 'DrugBank', 3: 'PDBe', 4: 'Guide to Pharmacology', 6: 'KEGG', 7: 'ChEBI',
      14: 'FDA SRS', 15: 'Selleck', 21: 'PubChem DOTF', 22: 'PubChem', 31: 'BindingDB', 34: 'DrugCentral', 41: 'SureChEMBL' };
    return (r || []).map((x) => ({ source: SRC[+x.src_id] || `source ${x.src_id}`, id: x.src_compound_id }));
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

// ---------------------------------------------------------------- ClinicalTrials.gov (v2, no key)
export const trials = {
  async search({ cond, spons, intr, status, size = 25 } = {}) {
    const q = new URLSearchParams({ pageSize: String(size), countTotal: 'true',
      fields: 'NCTId,BriefTitle,OverallStatus,Phase,LeadSponsorName,Condition,InterventionName,StartDate,StudyType' });
    if (cond) q.set('query.cond', cond);
    if (spons) q.set('query.spons', spons);
    if (intr) q.set('query.intr', intr);
    if (status) q.set('filter.overallStatus', status);
    const r = await http(`https://clinicaltrials.gov/api/v2/studies?${q}`);
    return { total: r.totalCount ?? (r.studies || []).length, studies: (r.studies || []).map((s) => {
      const ps = s.protocolSection || {};
      return { nct: ps.identificationModule?.nctId, title: ps.identificationModule?.briefTitle,
        status: ps.statusModule?.overallStatus, phase: (ps.designModule?.phases || []).join('/'),
        sponsor: ps.sponsorCollaboratorsModule?.leadSponsor?.name,
        conditions: ps.conditionsModule?.conditions || [],
        interventions: (ps.armsInterventionsModule?.interventions || []).map((i) => i.name).slice(0, 4),
        start: ps.statusModule?.startDateStruct?.date };
    }) };
  },
};

// ---------------------------------------------------------------- protein annotation (EBI, Reactome, STRING, gnomAD, HPA)
export const interpro = {
  async domains(acc) {
    const r = await http(`https://www.ebi.ac.uk/interpro/api/entry/InterPro/protein/uniprot/${acc}/?page_size=20`).catch(() => null);
    return ((r && r.results) || []).map((e) => ({ id: e.metadata.accession, name: e.metadata.name, type: e.metadata.type,
      locations: (e.proteins?.[0]?.entry_protein_locations || []).flatMap((l) => l.fragments.map((f) => [f.start, f.end])) }));
  },
};

export const reactome = {
  async pathways(acc) {
    const r = await http(`https://reactome.org/ContentService/data/mapping/UniProt/${acc}/pathways?species=9606`).catch(() => []);
    return (r || []).map((p) => ({ id: p.stId, name: p.displayName }));
  },
};

export const stringdb = {
  async partners(symbol, limit = 15) {
    const r = await http(`https://string-db.org/api/json/interaction_partners?identifiers=${encodeURIComponent(symbol)}&species=9606&limit=${limit}`).catch(() => []);
    return (r || []).map((x) => ({ symbol: x.preferredName_B, score: x.score }));
  },
};

export const gnomad = {
  async constraint(symbol) {
    const r = await http('https://gnomad.broadinstitute.org/api', { body: { query:
      `{ gene(gene_symbol: "${symbol}", reference_genome: GRCh38) { gene_id gnomad_constraint { pLI oe_lof oe_lof_upper mis_z syn_z } } }` } }).catch(() => null);
    const c = r?.data?.gene?.gnomad_constraint;
    return c ? { pLI: c.pLI, oeLof: c.oe_lof, loeuf: c.oe_lof_upper, misZ: c.mis_z } : null;
  },
};

export const proteinAtlas = {
  async expression(symbol) {
    const r = await http(`https://www.proteinatlas.org/api/search_download.php?search=${encodeURIComponent(symbol)}&format=json&columns=g,gs,rnatsm,rnabs,scl&compress=no`).catch(() => []);
    const row = (r || []).find((x) => (x.Gene || '').toUpperCase() === symbol.toUpperCase()) || (r || [])[0];
    if (!row) return null;
    const tissue = row['RNA tissue specific nTPM'] || {};
    const brain = row['RNA brain regional specific nTPM'] || {};
    const top = Object.entries(tissue).sort((a, b) => b[1] - a[1]).slice(0, 6);
    return { topTissues: top, brain: Object.entries(brain).sort((a, b) => b[1] - a[1]).slice(0, 5),
      location: row['Subcellular location'] || row.scl || null };
  },
};

// PDBe SIFTS: which UniProt residue each PDB residue is, so UniProt-numbered data (AlphaMissense,
// disease variants) can be painted onto an experimental structure.
export const pdbe = {
  async sifts(pdbId) {
    const r = await http(`https://www.ebi.ac.uk/pdbe/api/mappings/uniprot_segments/${pdbId.toLowerCase()}`).catch(() => null);
    const entry = r && r[pdbId.toLowerCase()];
    if (!entry) return null;
    const out = [];
    for (const [acc, data] of Object.entries(entry.UniProt || {})) {
      for (const m of data.mappings || []) {
        out.push({ uniprot: acc, chain: m.chain_id, pdbStart: m.start.author_residue_number,
          pdbEnd: m.end.author_residue_number, uniStart: m.unp_start, uniEnd: m.unp_end });
      }
    }
    return out;
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






// Europe PMC: open literature search, including preprints.
export const europepmc = {
  async search(query, limit = 15) {
    const r = await http(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=${encodeURIComponent(query)}&format=json&pageSize=${limit}&sort=CITED%20desc`).catch(() => null);
    return ((r && r.resultList?.result) || []).map((x) => ({ id: x.id, source: x.source, title: x.title, authors: x.authorString,
      journal: x.journalTitle, year: x.pubYear, cited: x.citedByCount, doi: x.doi, open: x.isOpenAccess === 'Y' }));
  },
};




// openFDA: adverse event reports and label text for an approved drug.
export const openfda = {
  async adverseEvents(drug, limit = 10) {
    const q = `https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:"${encodeURIComponent(drug)}"&count=patient.reaction.reactionmeddrapt.exact&limit=${limit}`;
    const r = await http(q).catch(() => null);
    return ((r && r.results) || []).map((x) => ({ reaction: x.term.toLowerCase(), reports: x.count }));
  },
  async label(drug) {
    const r = await http(`https://api.fda.gov/drug/label.json?search=openfda.generic_name:"${encodeURIComponent(drug)}"&limit=1`).catch(() => null);
    const l = r?.results?.[0];
    return l ? { indications: (l.indications_and_usage || [])[0]?.slice(0, 400), warnings: (l.warnings || l.boxed_warning || [])[0]?.slice(0, 300),
      route: (l.openfda?.route || []).join(', ') } : null;
  },
};

// Pharos / NCATS: how well studied and how druggable a target is (Tclin, Tchem, Tbio, Tdark).
export const pharos = {
  async target(symbol) {
    const q = { query: `query($q:String!){ target(q:{sym:$q}) { name sym tdl fam novelty
      ppiCount: ppiCounts { value } diseaseCounts { name value } } }`, variables: { q: symbol } };
    const r = await http('https://pharos-api.ncats.io/graphql', { body: q }).catch(() => null);
    const t = r?.data?.target;
    return t ? { name: t.name, symbol: t.sym, developmentLevel: t.tdl, family: t.fam, novelty: t.novelty,
      diseases: (t.diseaseCounts || []).slice(0, 6).map((d) => `${d.name} (${d.value})`) } : null;
  },
};

// BioThings (MyChem / MyGene): aggregated annotation across dozens of chemical and gene databases.
export const biothings = {
  async chem(inchikey) {
    const r = await http(`https://mychem.info/v1/chem/${inchikey}?fields=drugbank.name,drugbank.groups,drugbank.indication,chebi.name,chembl.max_phase,unii.unii,pharmgkb.name`).catch(() => null);
    if (!r) return null;
    return { drugbank: r.drugbank?.name, groups: [].concat(r.drugbank?.groups || []), indication: (r.drugbank?.indication || '').slice(0, 300),
      chebi: r.chebi?.name, maxPhase: r.chembl?.max_phase, unii: r.unii?.unii };
  },
  async gene(symbol) {
    const r = await http(`https://mygene.info/v3/query?q=symbol:${encodeURIComponent(symbol)}&species=human&fields=name,summary,entrezgene,genomic_pos,go.BP,pathway.kegg`).catch(() => null);
    const h = r?.hits?.[0];
    return h ? { name: h.name, summary: (h.summary || '').slice(0, 600), entrez: h.entrezgene,
      kegg: [].concat(h.pathway?.kegg || []).slice(0, 8).map((k) => k.name),
      processes: [].concat(h.go?.BP || []).slice(0, 8).map((g) => g.term) } : null;
  },
};

// KEGG: pathway membership, via the local proxy (KEGG sends no CORS headers).
export const kegg = {
  async pathways(entrezId) {
    const txt = await http(`https://rest.kegg.jp/link/pathway/hsa:${entrezId}`, { json: false }).catch(() => '');
    const ids = (txt || '').split('\n').map((l) => l.split('\t')[1]).filter(Boolean);
    if (!ids.length) return [];
    const names = await http(`https://rest.kegg.jp/list/${ids.slice(0, 12).join('+')}`, { json: false }).catch(() => '');
    return (names || '').split('\n').filter(Boolean).map((l) => { const [id, name] = l.split('\t'); return { id, name }; });
  },
};

// BindingDB: measured binding affinities for a target, via the proxy.
export const bindingdb = {
  async byUniprot(acc, cutoffNm = 1000) {
    const r = await http(`https://bindingdb.org/axis2/services/BDBService/getLigandsByUniprot?uniprot=${acc}&code=0&response=application/json&cutoff=${cutoffNm}`).catch(() => null);
    const hits = r?.getLigandsByUniprotResponse?.affinities || [];
    return [].concat(hits).slice(0, 40).map((h) => ({ smiles: h.smile, type: h.affinity_type, value: h.affinity, monomer: h.monomerid }));
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
