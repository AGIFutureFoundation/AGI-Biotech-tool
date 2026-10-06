"""Identifier bridge: ChEMBL target <-> UniProt accession <-> Ensembl gene <-> gene symbol.

The repurposing joins need this because the three sources key on three different
things. ChEMBL annotates a mechanism against a *target* (which may be a protein
complex with four components), Open Targets keys on a *single Ensembl gene*, and
Reactome/STRING key on a UniProt accession or a gene symbol. Nothing in
db_clients crosses those boundaries, so this module does it and nothing else.

Every call goes through db_clients.HTTP, so the per-host throttle, the SQLite
response cache and the circuit breaker all apply unchanged. Failures return
empty results with an "error" key; nothing here raises.
"""
from __future__ import annotations

import threading

import db_clients as db

# Process-local memo on top of the on-disk cache: the joins hit the same handful
# of targets hundreds of times per run and even a cache hit costs a SQLite read.
_MEMO: dict = {}
_MEMO_LOCK = threading.Lock()


def _memo(key, fn):
    """Cache successful lookups for the process. Never cache a failure.

    Every fetcher here returns an error dict rather than raising, and this used
    to store whatever came back. db.HTTP fails fast when its circuit breaker is
    open or another host failed recently, so one network blip produced an error
    dict that was then served for the life of the process: genes_for_chembl_target
    returned no genes for that target forever after, and repurposing_joins
    silently dropped every hypothesis depending on it.

    The on-disk cache already retries correctly. Only this in-process memo kept
    the failure, so only this needed fixing.
    """
    with _MEMO_LOCK:
        if key in _MEMO:
            return _MEMO[key]
    value = fn()
    if isinstance(value, dict) and value.get("error"):
        return value              # transient: answer now, retry next time
    with _MEMO_LOCK:
        _MEMO[key] = value
    return value


def chembl_target(target_chembl_id):
    """A ChEMBL target: {chembl_id, name, target_type, organism, accessions[]}.

    target_type matters: SINGLE PROTEIN is a clean join, PROTEIN COMPLEX means the
    mechanism is annotated against an assembly and every component is a candidate
    gene (thalidomide's CRL4(CRBN) ligase has four). Callers should say which.
    """
    def fetch():
        d, e = db._get(f"{db.CHEMBL}/target/{target_chembl_id}.json")
        if not d:
            return {"chembl_id": target_chembl_id, "accessions": [], "error": e or "no response"}
        comps = d.get("target_components") or []
        return {
            "chembl_id": target_chembl_id,
            "name": d.get("pref_name"),
            "target_type": d.get("target_type"),
            "organism": d.get("organism"),
            "accessions": [c["accession"] for c in comps
                           if c.get("accession") and c.get("component_type") == "PROTEIN"],
            "url": f"https://www.ebi.ac.uk/chembl/explore/target/{target_chembl_id}",
        }
    return _memo(("chembl_target", target_chembl_id), fetch)


def uniprot_accession(accession):
    """{accession, symbol, protein_name, ensembl_genes[]} for one UniProt accession.

    db_clients.uniprot_gene searches by gene *symbol*; ChEMBL hands us an
    accession, so this is the reverse direction.
    """
    def fetch():
        d, e = db._get(f"{db.UNIPROT}/search",
                       query=f"accession:{accession}",
                       fields="accession,gene_names,protein_name,xref_ensembl",
                       format="json", size=1)
        rows = (d or {}).get("results") or []
        if not rows:
            return {"accession": accession, "symbol": None, "ensembl_genes": [],
                    "error": e or "no UniProt entry"}
        r = rows[0]
        genes = [g.get("geneName", {}).get("value") for g in r.get("genes", [])]
        ens = sorted({p["value"].split(".")[0]
                      for x in r.get("uniProtKBCrossReferences", [])
                      if x.get("database") == "Ensembl"
                      for p in x.get("properties", []) if p.get("key") == "GeneId"})
        return {
            "accession": r.get("primaryAccession", accession),
            "symbol": next((g for g in genes if g), None),
            "protein_name": r.get("proteinDescription", {})
                             .get("recommendedName", {}).get("fullName", {}).get("value"),
            "ensembl_genes": ens,
            "url": f"https://www.uniprot.org/uniprotkb/{accession}",
        }
    return _memo(("uniprot", accession), fetch)


def genes_for_chembl_target(target_chembl_id):
    """ChEMBL target -> [{accession, symbol, ensembl, protein_name}], one per component gene.

    'ensembl' is the single Ensembl gene id Open Targets is queried with. Where
    UniProt cross-references several, the first (lowest-sorted, stable) is used
    and the rest are dropped: Open Targets is one-row-per-gene and a second id
    for the same protein would double-count the same evidence.
    """
    t = chembl_target(target_chembl_id)
    out = []
    for acc in t.get("accessions", []):
        u = uniprot_accession(acc)
        if not u.get("ensembl_genes"):
            continue
        out.append({"accession": u["accession"], "symbol": u.get("symbol"),
                    "protein_name": u.get("protein_name"), "ensembl": u["ensembl_genes"][0]})
    return {"target": t, "genes": out}


def ensembl_for_symbol(symbol):
    """Gene symbol -> {symbol, accession, ensembl} via the reviewed human UniProt entry.

    Used for disease-panel targets, which carry a symbol (and usually an accession
    in their evidence record) rather than an Ensembl id.
    """
    def fetch():
        r = db.uniprot_gene(symbol, limit=1)
        entries = r.get("entries") or []
        if not entries:
            return {"symbol": symbol, "accession": None, "ensembl": None,
                    "error": r.get("error") or "no reviewed UniProt entry"}
        e = entries[0]
        ens = e.get("ensembl_genes") or []
        return {"symbol": symbol, "accession": e.get("accession"),
                "ensembl": ens[0] if ens else None,
                "protein_name": e.get("protein_name")}
    return _memo(("symbol", symbol), fetch)
