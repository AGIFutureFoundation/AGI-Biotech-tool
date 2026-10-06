"""Biotech database results feeding the molecular research pipeline.

History: this module used to return the same hardcoded aspirin SMILES for every compound query, a fake
PMID 12345678 by 'Smith J, Doe A' for every literature query, and an SOD1 structure for every target;
get_database_stats() reported a '1.5B+' record total summed from capacity strings. All of that is gone.
Everything below is backed by real requests in db_clients.py; when a service fails, the method returns
fewer (or no) results and records the error in self.errors rather than raising or inventing data.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import db_clients as dbc


def _now():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CompoundSource:
    """Compound record retrieved from a database."""
    database: str
    compound_id: str
    smiles: str
    chemical_name: str
    mw: float
    logp: Optional[float]
    source_url: str
    retrieved_date: str
    inchikey: Optional[str] = None
    max_phase: Optional[str] = None


@dataclass
class TargetSource:
    """Target record retrieved from a database."""
    database: str
    target_id: str
    protein_name: str
    pdb_id: Optional[str]
    uniprot_id: Optional[str]
    gene_name: str
    source_url: str
    retrieved_date: str
    extra: Dict = field(default_factory=dict)


@dataclass
class LiteratureResult:
    """Paper retrieved from a literature database."""
    database: str
    pubmed_id: Optional[str]
    title: str
    authors: List[str]
    abstract: str
    publication_date: str
    url: str
    relevance_score: float


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


class BiotechDatabaseFederator:
    """Federates live queries across the databases db_clients supports."""

    LIVE = {
        'pubmed': ('PubMed', 'literature'), 'clinvar': ('ClinVar', 'genomics'),
        'pubchem': ('PubChem', 'drug'), 'chembl': ('ChEMBL', 'drug'), 'open_targets': ('Open Targets', 'drug'),
        'uniprot': ('UniProt', 'protein'), 'pdb': ('RCSB PDB', 'protein'), 'alphafold': ('AlphaFold DB', 'protein'),
        'reactome': ('Reactome', 'pathway'), 'string': ('STRING', 'pathway'),
        'clinicaltrials': ('ClinicalTrials.gov', 'clinical'),
    }

    def __init__(self):
        self.databases = {k: {'name': n, 'category': c, 'live': True} for k, (n, c) in self.LIVE.items()}
        self.query_cache = {}
        self.result_history = []
        self.errors = []

    def _err(self, db, r):
        if isinstance(r, dict) and r.get('error'):
            self.errors.append({'database': db, 'error': r['error'], 'at': _now()})

    def _log(self, kind, query, results, key):
        self.query_cache[key] = results
        self.result_history.append({'query': query, 'type': kind, 'results': len(results), 'timestamp': _now()})

    def search_compounds(self, query: str, target: Optional[str] = None,
                         databases: Optional[List[str]] = None) -> List[CompoundSource]:
        """Compounds by name or SMILES from PubChem and ChEMBL."""
        databases = databases or ['pubchem', 'chembl']
        is_smiles = dbc.inchikey_of(query) is not None and not query.isalpha()
        results = []
        if 'pubchem' in databases:
            r = dbc.pubchem_identify(smiles=query if is_smiles else None, name=None if is_smiles else query,
                                     synonyms=0, activity=False, similar=False)
            self._err('PubChem', r)
            if r.get('match') == 'exact':
                results.append(CompoundSource('PubChem', f"CID{r['cid']}", r.get('smiles') or '', r.get('title') or query,
                                              r.get('mw') or 0.0, _f(r.get('xlogp')), r['url'], _now(), r.get('inchikey')))
        if 'chembl' in databases:
            r = dbc.chembl_similar(query, 80, 5) if is_smiles else dbc.chembl_search(query, 5)
            self._err('ChEMBL', r)
            for m in r['molecules']:
                results.append(CompoundSource('ChEMBL', m['chembl_id'], m.get('smiles') or '', m.get('name') or m['chembl_id'],
                                              _f(m.get('mw')) or 0.0, _f(m.get('alogp')), m['url'], _now(),
                                              m.get('inchikey'), m.get('max_phase')))
        self._log('compound', query, results, f"compounds:{query}:{target}")
        return results

    def search_targets(self, query: str, databases: Optional[List[str]] = None) -> List[TargetSource]:
        """Human gene -> UniProt entry, its PDB structures and AlphaFold model."""
        databases = databases or ['uniprot', 'pdb', 'alphafold']
        up = dbc.uniprot_gene(query, limit=1)
        self._err('UniProt', up)
        results = []
        for e in up['entries']:
            acc = e['accession']
            if 'uniprot' in databases:
                results.append(TargetSource('UniProt', acc, e['protein_name'] or '', None, acc, query, e['url'], _now(),
                                            {'function': e['function'], 'length': e['length'],
                                             'ensembl': e['ensembl_genes']}))
            if 'pdb' in databases:
                pdb = dbc.pdb_structures(acc, 5)
                self._err('RCSB PDB', pdb)
                for pid in pdb['ids']:
                    x = dbc.pdb_entry(pid)
                    results.append(TargetSource('RCSB PDB', pid, x.get('title') or '', pid, acc, query,
                                                f"https://www.rcsb.org/structure/{pid}", _now(),
                                                {'resolution': x.get('resolution'), 'method': x.get('method'),
                                                 'total_structures': pdb['count']}))
            if 'alphafold' in databases:
                af = dbc.alphafold_model(acc)
                self._err('AlphaFold DB', af)
                if af.get('model'):
                    results.append(TargetSource('AlphaFold DB', af['model'], e['protein_name'] or '', None, acc, query,
                                                af['url'], _now(), {'mean_plddt': af['mean_plddt'], 'pdb_url': af['pdb_url']}))
        self._log('target', query, results, f"targets:{query}")
        return results

    def search_literature(self, query: str, target: Optional[str] = None,
                          years: Optional[Tuple[int, int]] = None, limit: int = 10) -> List[LiteratureResult]:
        """PubMed search (the only literature source with a live client)."""
        term = f"({query}) AND {target}" if target else query
        r = dbc.pubmed_search(term, retmax=limit, mindate=years[0] if years else None,
                              maxdate=years[1] if years else None)
        self._err('PubMed', r)
        abstracts = dbc.pubmed_abstracts([a['pmid'] for a in r['articles']])
        results = []
        for a in r['articles']:
            paper = {'title': a['title'], 'abstract': abstracts.get(a['pmid'], ''), 'date': a['pubdate']}
            results.append(LiteratureResult('PubMed', a['pmid'], a['title'], a['authors'], paper['abstract'],
                                            a['pubdate'], a['url'], self._calculate_relevance(query, paper)))
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        self._log('literature', query, results, f"literature:{query}:{target}")
        return results

    def _calculate_relevance(self, query: str, paper: Dict) -> float:
        """Fraction of query words present in title (weight 0.6) and abstract (0.4)."""
        words = [w for w in query.lower().replace('(', ' ').replace(')', ' ').split() if w not in ('and', 'or', 'not')]
        if not words:
            return 0.0
        title, abstract = paper.get('title', '').lower(), paper.get('abstract', '').lower()
        return round(0.6 * sum(w in title for w in words) / len(words)
                     + 0.4 * sum(w in abstract for w in words) / len(words), 3)

    def get_database_stats(self) -> Dict:
        """Measured activity of this federator. Database sizes are not claimed."""
        by_cat = {}
        for d in self.databases.values():
            by_cat.setdefault(d['category'], []).append(d['name'])
        return {'total_databases': len(self.databases), 'by_category': by_cat,
                'cached_queries': len(self.query_cache), 'search_history': len(self.result_history),
                'errors': len(self.errors), 'http': dbc.status()}


class MolecularEnrichmentEngine:
    """Enriches molecular research with live database context."""

    def __init__(self, federator: BiotechDatabaseFederator):
        self.federator = federator

    def enrich_compound_analysis(self, compound_smiles: str, compound_name: str = '') -> Dict:
        """Identity (PubChem), bioactivity and mechanism (ChEMBL), literature (PubMed) for one structure."""
        pc = dbc.pubchem_identify(smiles=compound_smiles, name=compound_name or None, synonyms=10)
        self.federator._err('PubChem', pc)
        name = pc.get('title') or compound_name
        ch = dbc.chembl_molecule(inchikey=pc['inchikey']) if pc.get('inchikey') else None
        acts, mech = ({'activities': []}, [])
        if ch and ch.get('chembl_id'):
            acts, mech = dbc.chembl_activities(ch['chembl_id'], 10), dbc.chembl_mechanisms(ch['chembl_id'])
        literature = self.federator.search_literature(name, limit=5) if name else []
        trials = dbc.clinical_trials(intervention=name, limit=5) if pc.get('match') == 'exact' and name else {'trials': []}
        return {
            'compound_name': name, 'smiles': compound_smiles, 'pubchem': pc, 'chembl': ch,
            'mechanisms': mech, 'top_activities': acts['activities'], 'clinical_trials': trials['trials'],
            'database_sources': [{'database': 'PubChem', 'compound_id': pc.get('cid'), 'mw': pc.get('mw'),
                                  'logp': pc.get('xlogp'), 'url': pc.get('url')}] if pc.get('cid') else [],
            'related_literature': [{'title': x.title, 'database': x.database, 'relevance': x.relevance_score,
                                    'url': x.url} for x in literature],
        }

    def enrich_target_analysis(self, target_gene: str) -> Dict:
        """Protein, structures, pathways, interactors, known drugs, pathogenic variants and literature for a gene."""
        targets = self.federator.search_targets(target_gene)
        acc = next((t.uniprot_id for t in targets if t.database == 'UniProt'), None)
        ens = next((t.extra.get('ensembl') for t in targets if t.database == 'UniProt'), None) or []
        pathways = dbc.reactome_pathways(acc)['pathways'] if acc else []
        drugs = dbc.opentargets_target_drugs(ens[0]) if ens else {'drugs': []}
        lit = self.federator.search_literature(f"{target_gene} pathway", limit=5)
        return {
            'target': target_gene,
            'protein_sources': [{'database': t.database, 'protein_name': t.protein_name, 'pdb_id': t.pdb_id,
                                 'uniprot_id': t.uniprot_id, 'url': t.source_url} for t in targets],
            'pathways': pathways,
            'interaction_partners': dbc.string_partners(target_gene, limit=10)['partners'],
            'known_drugs': drugs['drugs'],
            'pathogenic_variants': dbc.clinvar_variants(target_gene, retmax=5),
            'pathway_studies': [{'title': x.title, 'database': x.database, 'relevance': x.relevance_score,
                                 'url': x.url} for x in lit],
        }
