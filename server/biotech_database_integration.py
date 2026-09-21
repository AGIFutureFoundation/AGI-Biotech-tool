"""Registry of biotech databases, and a query router over the ones with a real client.

History: this module used to "connect" 29 databases by writing {'status': 'connected'} into a dict and
answered every query with results_count=42 and 'Data from <name>'. No network call was ever made.
Now a database is marked live only when db_clients.py has a client for it that makes a real request;
the others are listed for planning but answer with status 'no_client' instead of invented results.
There are no MCP servers behind any of these; mcp_endpoint is kept only for backward compatibility.
"""

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

import db_clients as dbc


class DatabaseCategory(Enum):
    """Categories of biotech databases."""
    LITERATURE = "literature"
    PROTEIN = "protein"
    GENOMICS = "genomics"
    DRUG_CHEMICAL = "drug_chemical"
    PATHWAY_FUNCTIONAL = "pathway_functional"
    CLINICAL = "clinical"
    STRUCTURAL = "structural"


@dataclass
class DatabaseEndpoint:
    """A public database. live=True means db_clients has a working, exercised client for it."""
    name: str
    category: DatabaseCategory
    url: str
    mcp_endpoint: Optional[str]
    api_key_required: bool
    free_tier_available: bool
    description: str
    query_types: List[str]
    live: bool = False
    api: Optional[str] = None


def _db(name, cat, url, desc, query_types, api=None, key=False):
    return DatabaseEndpoint(name, cat, url, None, key, True, desc, query_types, live=api is not None, api=api)


C = DatabaseCategory


class BiotechDatabaseRegistry:
    """Known databases. Descriptions state content only; no record counts are claimed."""

    DATABASES = [
        _db("PubMed", C.LITERATURE, "https://pubmed.ncbi.nlm.nih.gov/", "Biomedical literature citations",
            ["keyword_search", "pmid_lookup"], dbc.EUTILS),
        _db("ArXiv", C.LITERATURE, "https://arxiv.org/", "Preprints", ["keyword_search"]),
        _db("bioRxiv", C.LITERATURE, "https://www.biorxiv.org/", "Biology preprints", ["keyword_search"]),
        _db("medRxiv", C.LITERATURE, "https://www.medrxiv.org/", "Clinical preprints", ["keyword_search"]),
        _db("Semantic Scholar", C.LITERATURE, "https://www.semanticscholar.org/", "Scholarly graph", ["keyword_search"]),
        _db("CrossRef", C.LITERATURE, "https://www.crossref.org/", "DOI metadata", ["doi_lookup"]),
        _db("Google Scholar", C.LITERATURE, "https://scholar.google.com/", "No public API; not integrable",
            ["keyword_search"]),
        _db("ClinicalTrials.gov", C.CLINICAL, "https://clinicaltrials.gov/", "Registered clinical studies",
            ["keyword_search", "condition_search", "intervention_search"], dbc.CTGOV),
        _db("ChEMBL", C.DRUG_CHEMICAL, "https://www.ebi.ac.uk/chembl/", "Bioactive molecules and measured potencies",
            ["keyword_search", "compound_search", "target_search", "similarity_search"], dbc.CHEMBL),
        _db("PubChem", C.DRUG_CHEMICAL, "https://pubchem.ncbi.nlm.nih.gov/", "Chemical structures, synonyms, bioassays",
            ["keyword_search", "compound_search", "structure_search", "similarity_search"], dbc.PUBCHEM),
        _db("Open Targets", C.DRUG_CHEMICAL, "https://platform.opentargets.org/", "Target-disease-drug evidence",
            ["target_search", "known_drugs"], dbc.OPENTARGETS),
        _db("OpenFDA", C.CLINICAL, "https://open.fda.gov/", "Drug labels and adverse events", ["drug_search"]),
        _db("SureChEMBL", C.DRUG_CHEMICAL, "https://www.surechembl.org/", "Chemistry in patents", ["compound_search"]),
        _db("UniProt", C.PROTEIN, "https://www.uniprot.org/", "Protein sequence and function",
            ["keyword_search", "accession_lookup", "gene_search"], dbc.UNIPROT),
        _db("RCSB PDB", C.STRUCTURAL, "https://www.rcsb.org/", "Experimental 3D structures",
            ["accession_lookup", "keyword_search"], dbc.RCSB_SEARCH),
        _db("AlphaFold DB", C.STRUCTURAL, "https://alphafold.ebi.ac.uk/", "Predicted protein structures",
            ["accession_lookup"], dbc.ALPHAFOLD),
        _db("InterPro", C.PROTEIN, "https://www.ebi.ac.uk/interpro/", "Protein families and domains", ["domain_search"]),
        _db("Ensembl", C.GENOMICS, "https://www.ensembl.org/", "Genome annotation", ["gene_search"]),
        _db("NCBI GenBank", C.GENOMICS, "https://www.ncbi.nlm.nih.gov/genbank/", "Nucleotide sequences", ["accession_lookup"]),
        _db("ClinVar", C.GENOMICS, "https://www.ncbi.nlm.nih.gov/clinvar/", "Clinically interpreted variants",
            ["keyword_search", "gene_search"], dbc.EUTILS),
        _db("dbSNP", C.GENOMICS, "https://www.ncbi.nlm.nih.gov/snp/", "Short genetic variants", ["variant_lookup"]),
        _db("GTEx", C.GENOMICS, "https://gtexportal.org/", "Tissue expression", ["gene_expression"]),
        _db("RefSeq", C.GENOMICS, "https://www.ncbi.nlm.nih.gov/refseq/", "Reference sequences", ["accession_lookup"]),
        _db("GEO", C.PATHWAY_FUNCTIONAL, "https://www.ncbi.nlm.nih.gov/geo/", "Expression datasets", ["dataset_search"]),
        _db("Reactome", C.PATHWAY_FUNCTIONAL, "https://reactome.org/", "Curated pathways",
            ["keyword_search", "pathway_lookup"], dbc.REACTOME),
        _db("KEGG", C.PATHWAY_FUNCTIONAL, "https://www.kegg.jp/", "Pathway maps (academic licence terms)", ["pathway_lookup"]),
        _db("STRING", C.PATHWAY_FUNCTIONAL, "https://string-db.org/", "Protein interaction networks",
            ["keyword_search", "interaction_search"], dbc.STRING),
        _db("BioGRID", C.PATHWAY_FUNCTIONAL, "https://thebiogrid.org/", "Interactions (API needs BIOGRID_ACCESS_KEY)",
            ["interaction_search"], key=True),
        _db("Gene Ontology", C.PATHWAY_FUNCTIONAL, "https://geneontology.org/", "Gene function terms", ["term_search"]),
    ]

    @classmethod
    def get_all_databases(cls) -> List[DatabaseEndpoint]:
        return cls.DATABASES

    @classmethod
    def get_live(cls) -> List[DatabaseEndpoint]:
        return [db for db in cls.DATABASES if db.live]

    @classmethod
    def get_by_category(cls, category: DatabaseCategory) -> List[DatabaseEndpoint]:
        return [db for db in cls.DATABASES if db.category == category]

    @classmethod
    def search_database(cls, name_query: str) -> List[DatabaseEndpoint]:
        q = name_query.lower()
        exact = [db for db in cls.DATABASES if db.name.lower() == q]
        return exact or [db for db in cls.DATABASES if q in db.name.lower()]


def _q(p: Dict) -> str:
    return p.get("query") or p.get("target") or p.get("gene") or p.get("name") or ""


def _uniprot(p: Dict):
    """(UniProt entry or None, error) for the gene named in the query params."""
    if p.get("uniprot"):
        return {"accession": p["uniprot"], "ensembl_genes": []}, None
    r = dbc.uniprot_gene(_q(p), limit=1)
    return (r["entries"] or [None])[0], r.get("error")


def _pubchem(t, p):
    if t == "similarity_search" and p.get("smiles"):
        r = dbc.pubchem_similar(p["smiles"])
        return dbc.pubchem_properties(r["cids"]), r.get("error")
    r = dbc.pubchem_identify(smiles=p.get("smiles"), inchikey=p.get("inchikey"),
                             name=None if p.get("smiles") else _q(p), similar=bool(p.get("smiles")))
    return ([r] if r.get("match") == "exact" else r.get("nearest", [])), r.get("error")


def _chembl(t, p):
    if t == "similarity_search" and p.get("smiles"):
        r = dbc.chembl_similar(p["smiles"])
        return r["molecules"], r.get("error")
    if t == "target_search":  # molecules with measured activity against the target's gene product
        up, e = _uniprot(p)
        if not up:
            return [], e
        acc = up["accession"]
        d, e = dbc._get(f"{dbc.CHEMBL}/target.json", target_components__accession=acc, limit=1)
        tid = ((d or {}).get("targets") or [{}])[0].get("target_chembl_id")
        if not tid:
            return [], e
        d, e = dbc._get(f"{dbc.CHEMBL}/activity.json", target_chembl_id=tid, pchembl_value__isnull="false",
                        order_by="-pchembl_value", limit=p.get("limit", 20))
        keep = ("molecule_chembl_id", "molecule_pref_name", "standard_type", "standard_value", "standard_units",
                "pchembl_value", "canonical_smiles")
        return [dict({k: a.get(k) for k in keep}, target_chembl_id=tid) for a in (d or {}).get("activities", [])], e
    r = dbc.chembl_search(_q(p), p.get("limit", 10))
    return r["molecules"], r.get("error")


def _opentargets(t, p):
    ens = p.get("ensembl")
    if not ens:
        up, e = _uniprot(p)
        ens = (up["ensembl_genes"] or [None])[0] if up else None
        if not ens:
            return [], e
    r = dbc.opentargets_target_drugs(ens)
    return r["drugs"], r.get("error")


def _pdb(t, p):
    up, e = _uniprot(p)
    if not up:
        return [], e
    r = dbc.pdb_structures(up["accession"], p.get("limit", 10))
    return [dbc.pdb_entry(i) for i in r["ids"][:5]], r.get("error")


def _alphafold(t, p):
    up, e = _uniprot(p)
    r = dbc.alphafold_model(up["accession"]) if up else {"error": e}
    return ([r] if r.get("model") else []), r.get("error")


def _reactome(t, p):
    up, e = _uniprot(p)
    r = dbc.reactome_pathways(up["accession"]) if up else {"pathways": [], "error": e}
    return r["pathways"], r.get("error")


def _lst(fn, key):
    def run(t, p):
        r = fn(p)
        return r[key], r.get("error")
    return run


HANDLERS = {
    "PubMed": _lst(lambda p: dbc.pubmed_search(_q(p), p.get("limit", 10)), "articles"),
    "ClinicalTrials.gov": _lst(lambda p: dbc.clinical_trials(p.get("condition") or _q(p), p.get("intervention"),
                                                             p.get("pediatric", False), p.get("status"),
                                                             p.get("limit", 10)), "trials"),
    "ChEMBL": _chembl,
    "PubChem": _pubchem,
    "Open Targets": _opentargets,
    "UniProt": _lst(lambda p: dbc.uniprot_gene(_q(p)), "entries"),
    "RCSB PDB": _pdb,
    "AlphaFold DB": _alphafold,
    "ClinVar": _lst(lambda p: dbc.clinvar_variants(_q(p), p.get("pathogenic_only", True), p.get("limit", 20)), "variants"),
    "Reactome": _reactome,
    "STRING": _lst(lambda p: dbc.string_partners(_q(p), limit=p.get("limit", 10)), "partners"),
}


class MCP_ServerManager:
    """Routes queries to live clients. (Name kept for compatibility; there is no MCP transport.)"""

    def __init__(self):
        self.active_connections = {}
        self.connection_stats = {'total_requests': 0, 'successful_queries': 0, 'failed_queries': 0,
                                 'databases_connected': 0}

    def connect_database(self, endpoint: DatabaseEndpoint) -> Dict:
        """Register a database for routing. No network is touched; 'live' means a real client exists."""
        live = endpoint.name in HANDLERS
        conn = {'database': endpoint.name, 'status': 'live' if live else 'no_client', 'api': endpoint.api,
                'registered_at': datetime.now(timezone.utc).isoformat(), 'capabilities': endpoint.query_types}
        self.active_connections[endpoint.name] = conn
        self.connection_stats['databases_connected'] = sum(c['status'] == 'live' for c in self.active_connections.values())
        return conn

    def connect_all_free(self) -> Dict:
        dbs = BiotechDatabaseRegistry.get_all_databases()
        conns = [self.connect_database(db) for db in dbs]
        live = [c['database'] for c in conns if c['status'] == 'live']
        return {'connected': [{'name': c['database'], 'status': c['status']} for c in conns if c['status'] == 'live'],
                'failed': [], 'no_client': [c['database'] for c in conns if c['status'] != 'live'],
                'summary': {'total_connected': len(live), 'categories_covered':
                            len({db.category for db in dbs if db.name in live}), 'databases_available': len(dbs)}}

    def query_database(self, database_name: str, query_type: str, query_params: Dict) -> Dict:
        """Run a real query. Never raises; failures come back as status 'error' with results_count 0."""
        matches = BiotechDatabaseRegistry.search_database(database_name)
        if not matches:
            return {'error': f'Database {database_name} not found', 'status': 'error', 'results_count': 0,
                    'query_time_ms': 0}
        db = matches[0]
        base = {'database': db.name, 'query_type': query_type, 'results': [], 'results_count': 0, 'query_time_ms': 0}
        if db.name not in HANDLERS:
            return dict(base, status='no_client', error=f'No client implemented for {db.name}; nothing was queried')
        self.connection_stats['total_requests'] += 1
        t = time.perf_counter()
        try:
            results, err = HANDLERS[db.name](query_type, query_params)
        except Exception as e:  # noqa: BLE001 - a malformed response must not end a research run
            results, err = [], f'{type(e).__name__}: {e}'
        out = dict(base, results=results, results_count=len(results),
                   query_time_ms=round((time.perf_counter() - t) * 1000))
        if err:
            self.connection_stats['failed_queries'] += 1
            return dict(out, status='error', error=err)
        self.connection_stats['successful_queries'] += 1
        return dict(out, status='success')

    def get_connection_health(self) -> Dict:
        return {'active_connections': self.connection_stats['databases_connected'], 'stats': self.connection_stats,
                'connections': list(self.active_connections.values()), 'http': dbc.status()}


class ResearchWorkflowWithDatabases:
    """Target-centred research workflow over the live databases."""

    def __init__(self):
        self.mcp_manager = MCP_ServerManager()
        self.research_context = {}

    def initialize_for_target(self, target_name: str) -> Dict:
        connections = self.mcp_manager.connect_all_free()
        workflow = {
            'target': target_name,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'databases_connected': connections['summary']['total_connected'],
            'research_phase': 'initialized',
            'research_plan': {
                'phase_1_literature': ['PubMed'],
                'phase_2_protein': ['UniProt', 'AlphaFold DB', 'RCSB PDB'],
                'phase_3_genomics': ['ClinVar'],
                'phase_4_compounds': ['ChEMBL', 'PubChem', 'Open Targets'],
                'phase_5_pathways': ['STRING', 'Reactome'],
                'phase_6_clinical': ['ClinicalTrials.gov'],
            },
        }
        self.research_context[target_name] = workflow
        return workflow

    def _phase(self, target, phase, key, dbs, qtype, params):
        return {'target': target, 'phase': phase,
                key: {d: self.mcp_manager.query_database(d, qtype, params) for d in dbs}}

    def search_literature_for_target(self, target: str) -> Dict:
        return self._phase(target, 'literature_search', 'sources', ['PubMed'], 'keyword_search',
                           {'query': target, 'limit': 20})

    def identify_drug_compounds(self, target: str) -> Dict:
        return self._phase(target, 'compound_identification', 'databases', ['ChEMBL', 'Open Targets'],
                           'target_search', {'target': target})

    def analyze_protein_structure(self, target: str) -> Dict:
        return self._phase(target, 'structure_analysis', 'sources', ['UniProt', 'RCSB PDB', 'AlphaFold DB'],
                           'accession_lookup', {'target': target})


def generate_database_integration_report() -> Dict:
    """What is integrated. Record volumes are not reported because they are not measured."""
    dbs = BiotechDatabaseRegistry.get_all_databases()
    live = [db.name for db in dbs if db.name in HANDLERS]
    return {
        'total_databases': len(dbs),
        'live_databases': live,
        'categories': {cat.value: len(BiotechDatabaseRegistry.get_by_category(cat)) for cat in DatabaseCategory},
        'databases_by_category': {
            cat.value: [{'name': db.name, 'description': db.description, 'live': db.name in HANDLERS}
                        for db in BiotechDatabaseRegistry.get_by_category(cat)] for cat in DatabaseCategory},
        'free_tier_coverage': f'{len(live)} of {len(dbs)} have live clients; all live ones are keyless',
        'mcp_ready': False,
        'estimated_data_access': 'not measured',
        'http': dbc.status(),
    }
