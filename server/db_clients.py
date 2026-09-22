"""Live clients for public biomedical databases.

Every function here makes a real HTTPS call (or answers from the on-disk cache of one) and parses the
real response. Nothing is simulated. Each endpoint was exercised by hand before being added.

Shared behaviour:
  * per-host throttling (NCBI 3 req/s, or 10 with NCBI_API_KEY; STRING 1 req/s; CT.gov ~1 req/s),
  * a SQLite response cache (AGI_DB_CACHE, default ~/.cache/agi-bioxr/db_cache.sqlite; TTL AGI_DB_CACHE_TTL
    seconds, default 7 days; AGI_DB_CACHE=off disables it),
  * retries with backoff on 429/5xx, honouring Retry-After,
  * a per-host circuit breaker so an offline run fails fast instead of waiting out every timeout,
  * failures never raise: functions return {"error": ...} (plus empty result fields) and the run goes on.

Environment: NCBI_API_KEY (optional), NCBI_EMAIL (defaults to the project contact), AGI_DB_OFFLINE=1
to forbid network access entirely (cache only).
"""
import hashlib
import json
import os
import sqlite3
import tempfile
import threading
import time
import xml.etree.ElementTree as ET

try:
    import requests
except ImportError:  # degrade: every call reports the missing dependency
    requests = None

CONTACT = os.environ.get("NCBI_EMAIL", "x@agifuturefoundation.org")
USER_AGENT = f"agi-bioxr/1.0 (mailto:{CONTACT})"
TIMEOUT = float(os.environ.get("AGI_DB_TIMEOUT", "20"))

PUBCHEM = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"
UNIPROT = "https://rest.uniprot.org/uniprotkb"
RCSB_SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
RCSB_DATA = "https://data.rcsb.org/rest/v1/core/entry"
ALPHAFOLD = "https://alphafold.ebi.ac.uk/api/prediction"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"
REACTOME = "https://reactome.org/ContentService"
STRING = "https://string-db.org/api/json"
OPENTARGETS = "https://api.platform.opentargets.org/api/v4/graphql"


def _ncbi_interval():
    return 0.11 if os.environ.get("NCBI_API_KEY") else 0.34


# Minimum seconds between requests to one host (published limits, rounded conservatively).
MIN_INTERVAL = {
    "eutils.ncbi.nlm.nih.gov": _ncbi_interval,
    "pubchem.ncbi.nlm.nih.gov": lambda: 0.25,  # PubChem: max 5 req/s
    "string-db.org": lambda: 1.0,               # STRING asks for one call per second
    "clinicaltrials.gov": lambda: 1.2,          # CT.gov throttles around 50 req/min per IP
}
DEFAULT_INTERVAL = 0.2


class _Cache:
    def __init__(self):
        self.path, self.db, self.lock = None, None, threading.Lock()
        self.ttl = float(os.environ.get("AGI_DB_CACHE_TTL", 7 * 86400))

    def _open(self):
        if self.db is not None or self.path == "off":
            return self.db
        path = os.environ.get("AGI_DB_CACHE")
        if path == "off":
            self.path = "off"
            return None
        if not path:
            home = os.path.expanduser("~")
            base = os.path.join(home, ".cache") if home and home != "~" and os.path.isdir(home) else tempfile.gettempdir()
            path = os.path.join(base, "agi-bioxr", "db_cache.sqlite")
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.db = sqlite3.connect(path, check_same_thread=False, timeout=10)
            self.db.execute("CREATE TABLE IF NOT EXISTS r (k TEXT PRIMARY KEY, t REAL, status INT, body TEXT)")
            self.path = path
        except Exception:  # noqa: BLE001 - an unwritable cache must not stop research
            self.path, self.db = "off", None
        return self.db

    def get(self, key, stale_ok=False):
        with self.lock:
            db = self._open()
            if db is None:
                return None
            row = db.execute("SELECT t, status, body FROM r WHERE k=?", (key,)).fetchone()
        if row and (stale_ok or time.time() - row[0] < self.ttl):
            return row[1], row[2]
        return None

    def put(self, key, status, body):
        with self.lock:
            db = self._open()
            if db is not None:
                try:
                    db.execute("REPLACE INTO r VALUES (?,?,?,?)", (key, time.time(), status, body))
                    db.commit()
                except Exception:  # noqa: BLE001
                    pass


class Http:
    """Throttled, cached, fault-tolerant HTTP. get()/post() return (status, text) or (None, error)."""

    def __init__(self):
        self.cache = _Cache()
        self.last, self.down, self.fails = {}, {}, {}
        self.lock = threading.Lock()
        self.session = None
        self.stats = {"network": 0, "cache_hits": 0, "errors": 0}

    def _session(self):
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
        return self.session

    def _wait(self, host):
        gap = MIN_INTERVAL.get(host, lambda: DEFAULT_INTERVAL)()
        with self.lock:
            now = time.monotonic()
            slot = max(now, self.last.get(host, 0) + gap)
            self.last[host] = slot
        if slot > now:
            time.sleep(slot - now)

    def request(self, method, url, params=None, data=None, json_body=None, ttl=True):
        key = hashlib.sha256(json.dumps([method, url, params, data, json_body], sort_keys=True, default=str)
                             .encode()).hexdigest()
        if ttl:
            hit = self.cache.get(key)
            if hit:
                self.stats["cache_hits"] += 1
                return hit
        if requests is None:
            return None, "the 'requests' package is not installed"
        host = url.split("/")[2]
        if os.environ.get("AGI_DB_OFFLINE") == "1":
            stale = self.cache.get(key, stale_ok=True)
            return stale or (None, "offline mode (AGI_DB_OFFLINE=1) and no cached response")
        if max(self.down.get(host, 0), self.down.get("*", 0)) > time.monotonic():
            stale = self.cache.get(key, stale_ok=True)
            return stale or (None, f"{host} unreachable recently; skipping for now")
        err = None
        for attempt in range(3):
            self._wait(host)
            try:
                self.stats["network"] += 1
                r = self._session().request(method, url, params=params, data=data, json=json_body, timeout=TIMEOUT)
            except Exception as e:  # noqa: BLE001 - connection errors, timeouts, DNS
                # One failure benches the host for a minute; two benched hosts mean the network is
                # down, so bench every host and let the caller's loop finish fast instead of hanging.
                err = f"{type(e).__name__}: {e}"
                self.fails[host] = time.monotonic() + 60
                self.down[host] = time.monotonic() + 60
                if sum(t > time.monotonic() for t in self.fails.values()) >= 2:
                    self.down["*"] = time.monotonic() + 60
                break
            self.fails.pop(host, None)
            if r.status_code == 429 or r.status_code >= 500:
                err = f"HTTP {r.status_code} from {host}"
                wait = r.headers.get("Retry-After", "")
                time.sleep(min(float(wait), 30) if wait.replace(".", "").isdigit() else 1.5 * (attempt + 1))
                continue
            if r.status_code < 400 or r.status_code == 404:  # a 404 is a real "not found" answer
                self.cache.put(key, r.status_code, r.text)
            return r.status_code, r.text
        self.stats["errors"] += 1
        stale = self.cache.get(key, stale_ok=True)
        return stale or (None, err)

    def json(self, method, url, **kw):
        """(data, error). data is None on failure or 404."""
        status, text = self.request(method, url, **kw)
        if status is None:
            return None, text
        if status == 404:
            return None, None
        if status >= 400:
            return None, f"HTTP {status}: {text[:200]}"
        try:
            return json.loads(text), None
        except ValueError:
            return None, f"unparseable response from {url.split('/')[2]}"


HTTP = Http()


def _get(url, **params):
    return HTTP.json("GET", url, params=params or None)


def _ncbi(params):
    p = dict(params, tool="agi-bioxr", email=CONTACT)
    if os.environ.get("NCBI_API_KEY"):
        p["api_key"] = os.environ["NCBI_API_KEY"]
    return p


# --------------------------------------------------------------------------- PubChem (PUG-REST)

PC_PROPS = "Title,IUPACName,MolecularFormula,MolecularWeight,SMILES,InChIKey,XLogP"


def inchikey_of(smiles):
    """InChIKey computed locally with RDKit, or None."""
    try:
        from rdkit import Chem, RDLogger
        RDLogger.DisableLog("rdApp.*")
        m = Chem.MolFromSmiles(smiles)
        return Chem.MolToInchiKey(m) if m else None
    except Exception:  # noqa: BLE001
        return None


def pubchem_cids(smiles=None, inchikey=None, name=None):
    """{'cids': [...], 'error'?}. Exact identity lookup by InChIKey, SMILES or name."""
    if inchikey:
        d, e = _get(f"{PUBCHEM}/compound/inchikey/{inchikey}/cids/JSON")
    elif smiles:  # POST: SMILES with '/', '#' or '\\' are unsafe in a URL path
        d, e = HTTP.json("POST", f"{PUBCHEM}/compound/smiles/cids/JSON", data={"smiles": smiles})
    elif name:
        d, e = _get(f"{PUBCHEM}/compound/name/{requests.utils.quote(name) if requests else name}/cids/JSON")
    else:
        return {"cids": [], "error": "no identifier given"}
    cids = [c for c in ((d or {}).get("IdentifierList", {}).get("CID") or []) if c]
    return {"cids": cids, **({"error": e} if e else {})}


def pubchem_properties(cids):
    cids = [str(c) for c in cids][:100]
    if not cids:
        return []
    d, _ = HTTP.json("POST", f"{PUBCHEM}/compound/cid/property/{PC_PROPS}/JSON", data={"cid": ",".join(cids)})
    return (d or {}).get("PropertyTable", {}).get("Properties", [])


def pubchem_synonyms(cid, limit=15):
    d, _ = _get(f"{PUBCHEM}/compound/cid/{cid}/synonyms/JSON")
    info = (d or {}).get("InformationList", {}).get("Information") or [{}]
    return info[0].get("Synonym", [])[:limit]


def pubchem_active_aids(cid):
    """AIDs of PubChem BioAssays in which this compound was tested active."""
    d, e = _get(f"{PUBCHEM}/compound/cid/{cid}/aids/JSON", aids_type="active")
    info = (d or {}).get("InformationList", {}).get("Information") or [{}]
    return {"aids": info[0].get("AID", []), **({"error": e} if e else {})}


def pubchem_bioassays(cid, limit=25):
    """Active BioAssay outcomes with target and potency. The response is large (~1 MB for approved drugs)."""
    d, e = _get(f"{PUBCHEM}/compound/cid/{cid}/assaysummary/JSON")
    if not d:
        return {"rows": [], **({"error": e} if e else {})}
    cols = d["Table"]["Columns"]["Column"]
    rows = [dict(zip(cols, r["Cell"])) for r in d["Table"].get("Row", [])]
    active = [r for r in rows if r.get("Activity Outcome") == "Active"]
    active.sort(key=lambda r: float(r.get("Activity Value [uM]") or 1e9))
    keep = ("AID", "Target Accession", "Target GeneID", "Activity Value [uM]", "Activity Name", "Assay Name")
    return {"tested": len(rows), "active": len(active), "rows": [{k: r.get(k) for k in keep} for r in active[:limit]]}


def pubchem_similar(smiles, threshold=90, limit=5):
    d, e = HTTP.json("POST", f"{PUBCHEM}/compound/fastsimilarity_2d/smiles/cids/JSON",
                     data={"smiles": smiles}, params={"Threshold": threshold, "MaxRecords": limit})
    return {"cids": (d or {}).get("IdentifierList", {}).get("CID", []), **({"error": e} if e else {})}


def pubchem_identify(smiles=None, inchikey=None, name=None, synonyms=10, activity=True, similar=True):
    """Recover a structure's PubChem identity: CID, title, synonyms, active-assay count; nearest neighbours if new."""
    ik = inchikey or (inchikey_of(smiles) if smiles else None)
    out = {"query": {"smiles": smiles, "inchikey": ik, "name": name}, "match": None, "source": "PubChem"}
    look = pubchem_cids(inchikey=ik) if ik else {"cids": []}
    if not look["cids"] and smiles:
        look = pubchem_cids(smiles=smiles)
    if not look["cids"] and name:
        look = pubchem_cids(name=name)
    if look.get("error"):
        out["error"] = look["error"]
    if look["cids"]:
        cid = look["cids"][0]
        p = (pubchem_properties([cid]) or [{}])[0]
        out.update(match="exact", cid=cid, title=p.get("Title"), iupac=p.get("IUPACName"),
                   formula=p.get("MolecularFormula"), mw=float(p["MolecularWeight"]) if p.get("MolecularWeight") else None,
                   xlogp=p.get("XLogP"), smiles=p.get("SMILES"), inchikey=p.get("InChIKey"),
                   url=f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}")
        if synonyms:
            out["synonyms"] = pubchem_synonyms(cid, synonyms)
        if activity:
            out["active_assays"] = len(pubchem_active_aids(cid)["aids"])
    elif similar and smiles and "error" not in out:
        near = pubchem_similar(smiles)
        out["match"] = "none"
        out["nearest"] = [{"cid": p.get("CID"), "title": p.get("Title"), "smiles": p.get("SMILES")}
                          for p in pubchem_properties(near["cids"])]
    return out


# --------------------------------------------------------------------------- NCBI E-utilities

def pubmed_search(term, retmax=10, mindate=None, maxdate=None, sort="relevance"):
    """{'count', 'articles': [{pmid, title, authors, journal, pubdate, doi, url}]}."""
    p = {"db": "pubmed", "term": term, "retmode": "json", "retmax": retmax, "sort": sort}
    if mindate or maxdate:
        p.update(datetype="pdat", mindate=str(mindate or 1800), maxdate=str(maxdate or 3000))
    d, e = _get(f"{EUTILS}/esearch.fcgi", **_ncbi(p))
    if not d:
        return {"count": None, "articles": [], "error": e or "no response"}
    r = d.get("esearchresult", {})
    ids = r.get("idlist", [])
    return {"count": int(r.get("count", 0)), "articles": pubmed_summaries(ids), "source": "PubMed"}


def pubmed_summaries(pmids):
    if not pmids:
        return []
    d, _ = _get(f"{EUTILS}/esummary.fcgi", **_ncbi({"db": "pubmed", "id": ",".join(map(str, pmids)), "retmode": "json"}))
    res = (d or {}).get("result", {})
    out = []
    for pid in res.get("uids", []):
        a = res[pid]
        doi = next((x["value"] for x in a.get("articleids", []) if x.get("idtype") == "doi"), None)
        out.append({"pmid": pid, "title": a.get("title", ""), "authors": [x["name"] for x in a.get("authors", [])],
                    "journal": a.get("fulljournalname") or a.get("source"), "pubdate": a.get("pubdate", ""),
                    "doi": doi, "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
    return out


def pubmed_abstracts(pmids):
    """{pmid: abstract text} via efetch XML."""
    if not pmids:
        return {}
    status, text = HTTP.request("GET", f"{EUTILS}/efetch.fcgi",
                                params=_ncbi({"db": "pubmed", "id": ",".join(map(str, pmids)), "retmode": "xml"}))
    if status != 200:
        return {}
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return {}
    return {art.findtext(".//PMID"): " ".join("".join(t.itertext()) for t in art.findall(".//Abstract/AbstractText"))
            for art in root.findall(".//PubmedArticle")}


def clinvar_variants(gene, pathogenic_only=True, retmax=20):
    """ClinVar variants in a gene: {'count', 'variants': [{accession, title, significance, conditions}]}."""
    term = f"{gene}[gene]" + (" AND clinsig_pathogenic[filter]" if pathogenic_only else "")
    d, e = _get(f"{EUTILS}/esearch.fcgi", **_ncbi({"db": "clinvar", "term": term, "retmode": "json", "retmax": retmax}))
    if not d:
        return {"count": None, "variants": [], "error": e or "no response"}
    ids = d["esearchresult"].get("idlist", [])
    out = {"count": int(d["esearchresult"].get("count", 0)), "variants": [], "source": "ClinVar"}
    if ids:
        s, _ = _get(f"{EUTILS}/esummary.fcgi", **_ncbi({"db": "clinvar", "id": ",".join(ids), "retmode": "json"}))
        res = (s or {}).get("result", {})
        for uid in res.get("uids", []):
            v = res[uid]
            g = v.get("germline_classification") or v.get("clinical_significance") or {}
            out["variants"].append({
                "accession": v.get("accession"), "title": v.get("title"), "significance": g.get("description"),
                "conditions": [t.get("trait_name") for t in g.get("trait_set", [])][:5],
                "url": f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{uid}/"})
    return out


# --------------------------------------------------------------------------- ChEMBL

def _chembl_mol(m):
    p = m.get("molecule_properties") or {}
    s = m.get("molecule_structures") or {}
    return {"chembl_id": m.get("molecule_chembl_id"), "name": m.get("pref_name"), "max_phase": m.get("max_phase"),
            "first_approval": m.get("first_approval"), "smiles": s.get("canonical_smiles"),
            "inchikey": s.get("standard_inchi_key"), "mw": p.get("full_mwt"), "alogp": p.get("alogp"),
            "atc": m.get("atc_classifications", []),
            "url": f"https://www.ebi.ac.uk/chembl/explore/compound/{m.get('molecule_chembl_id')}"}


def chembl_molecule(inchikey=None, chembl_id=None):
    d, e = _get(f"{CHEMBL}/molecule/{inchikey or chembl_id}.json")
    return _chembl_mol(d) if d else ({"error": e} if e else None)


def chembl_search(query, limit=5):
    d, e = _get(f"{CHEMBL}/molecule/search.json", q=query, limit=limit)
    return {"molecules": [_chembl_mol(m) for m in (d or {}).get("molecules", [])], **({"error": e} if e else {})}


def chembl_similar(smiles, similarity=70, limit=5):
    d, e = _get(f"{CHEMBL}/similarity/{requests.utils.quote(smiles, safe='') if requests else smiles}/{similarity}.json",
                limit=limit)
    return {"molecules": [dict(_chembl_mol(m), similarity=m.get("similarity")) for m in (d or {}).get("molecules", [])],
            **({"error": e} if e else {})}


def chembl_activities(chembl_id, limit=20):
    """Measured potencies (pChEMBL set) for a molecule, strongest first."""
    d, e = _get(f"{CHEMBL}/activity.json", molecule_chembl_id=chembl_id, pchembl_value__isnull="false",
                order_by="-pchembl_value", limit=limit)
    keep = ("target_chembl_id", "target_pref_name", "target_organism", "standard_type", "standard_value",
            "standard_units", "pchembl_value", "assay_chembl_id", "document_chembl_id")
    return {"activities": [{k: a.get(k) for k in keep} for a in (d or {}).get("activities", [])],
            "total": (d or {}).get("page_meta", {}).get("total_count"), **({"error": e} if e else {})}


def chembl_mechanisms(chembl_id):
    d, e = _get(f"{CHEMBL}/mechanism.json", molecule_chembl_id=chembl_id)
    return [{"mechanism": m.get("mechanism_of_action"), "action": m.get("action_type"),
             "target_chembl_id": m.get("target_chembl_id"), "max_phase": m.get("max_phase")}
            for m in (d or {}).get("mechanisms", [])]


# --------------------------------------------------------------------------- proteins & structures

def uniprot_gene(gene, organism=9606, limit=3):
    """Reviewed UniProt entries for a gene symbol."""
    d, e = _get(f"{UNIPROT}/search", query=f"gene_exact:{gene} AND organism_id:{organism} AND reviewed:true",
                fields="accession,gene_names,protein_name,length,cc_function,xref_ensembl", format="json", size=limit)
    out = []
    for r in (d or {}).get("results", []):
        pd = r.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {})
        fn = next((c for c in r.get("comments", []) if c.get("commentType") == "FUNCTION"), {})
        out.append({"accession": r.get("primaryAccession"), "protein_name": pd.get("value"),
                    "genes": [g.get("geneName", {}).get("value") for g in r.get("genes", [])],
                    "length": r.get("sequence", {}).get("length"),
                    "function": " ".join(t.get("value", "") for t in fn.get("texts", []))[:600],
                    "ensembl_genes": sorted({p["value"].split(".")[0] for x in r.get("uniProtKBCrossReferences", [])
                                             if x.get("database") == "Ensembl"
                                             for p in x.get("properties", []) if p.get("key") == "GeneId"}),
                    "url": f"https://www.uniprot.org/uniprotkb/{r.get('primaryAccession')}"})
    return {"entries": out, **({"error": e} if e else {})}


def pdb_structures(uniprot, rows=10):
    """RCSB PDB entries containing this UniProt accession: {'count', 'ids'}."""
    q = {"query": {"type": "terminal", "service": "text", "parameters": {
        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
        "operator": "exact_match", "value": uniprot}},
        "return_type": "entry", "request_options": {"paginate": {"start": 0, "rows": rows},
                                                     "sort": [{"sort_by": "rcsb_accession_info.initial_release_date",
                                                               "direction": "desc"}]}}
    d, e = HTTP.json("POST", RCSB_SEARCH, json_body=q)
    if d is None:
        return {"count": 0 if e is None else None, "ids": [], **({"error": e} if e else {})}
    return {"count": d.get("total_count"), "ids": [x["identifier"] for x in d.get("result_set", [])]}


def pdb_entry(pdb_id):
    d, e = _get(f"{RCSB_DATA}/{pdb_id}")
    if not d:
        return {"pdb_id": pdb_id, **({"error": e} if e else {})}
    info = d.get("rcsb_entry_info", {})
    return {"pdb_id": pdb_id, "title": d.get("struct", {}).get("title"), "method": info.get("experimental_method"),
            "resolution": (info.get("resolution_combined") or [None])[0],
            "released": d.get("rcsb_accession_info", {}).get("initial_release_date", "")[:10],
            "url": f"https://www.rcsb.org/structure/{pdb_id}"}


def alphafold_model(uniprot):
    d, e = _get(f"{ALPHAFOLD}/{uniprot}")
    if not d:
        return {"uniprot": uniprot, "model": None, **({"error": e} if e else {})}
    m = d[0]
    return {"uniprot": uniprot, "model": m.get("modelEntityId") or m.get("entryId"), "mean_plddt": m.get("globalMetricValue"),
            "pdb_url": m.get("pdbUrl"), "cif_url": m.get("cifUrl"), "version": m.get("latestVersion"),
            "url": f"https://alphafold.ebi.ac.uk/entry/{uniprot}"}


# --------------------------------------------------------------------------- clinical, pathways, networks

def clinical_trials(condition=None, intervention=None, pediatric=False, status=None, limit=10,
                    sponsor=None, lead_sponsor=None):
    """ClinicalTrials.gov v2. status e.g. 'RECRUITING'; pediatric restricts to trials enrolling children.

    sponsor matches sponsor or collaborator; lead_sponsor matches only trials the
    organisation runs itself. The two differ materially -- for St. Jude, 490
    against 437 -- so use lead_sponsor to ask what an institution is running and
    sponsor to include what it takes part in.
    """
    p = {"pageSize": limit, "countTotal": "true",
         "fields": "NCTId,BriefTitle,OverallStatus,Phase,Condition,InterventionName,StdAge,StartDate,"
                   "LeadSponsorName"}
    if condition:
        p["query.cond"] = condition
    if intervention:
        p["query.intr"] = intervention
    if sponsor:
        p["query.spons"] = sponsor
    if lead_sponsor:
        p["query.lead"] = lead_sponsor
    if pediatric:
        p["filter.advanced"] = "AREA[StdAge]CHILD"
    if status:
        p["filter.overallStatus"] = status
    d, e = _get(CTGOV, **p)
    if not d:
        return {"count": None, "trials": [], "error": e or "no response"}
    out = []
    for s in d.get("studies", []):
        ps = s.get("protocolSection", {})
        nct = ps.get("identificationModule", {}).get("nctId")
        out.append({"nct_id": nct, "title": ps.get("identificationModule", {}).get("briefTitle"),
                    "lead_sponsor": ps.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name"),
                    "status": ps.get("statusModule", {}).get("overallStatus"),
                    "start": ps.get("statusModule", {}).get("startDateStruct", {}).get("date"),
                    "phases": ps.get("designModule", {}).get("phases", []),
                    "conditions": ps.get("conditionsModule", {}).get("conditions", []),
                    "interventions": [i.get("name") for i in ps.get("armsInterventionsModule", {}).get("interventions", [])],
                    "ages": ps.get("eligibilityModule", {}).get("stdAges", []),
                    "url": f"https://clinicaltrials.gov/study/{nct}"})
    return {"count": d.get("totalCount"), "trials": out, "source": "ClinicalTrials.gov"}


def reactome_pathways(uniprot, species=9606):
    d, e = _get(f"{REACTOME}/data/mapping/UniProt/{uniprot}/pathways", species=species)
    return {"pathways": [{"id": p.get("stId"), "name": p.get("displayName"), "disease": p.get("isInDisease"),
                          "url": f"https://reactome.org/content/detail/{p.get('stId')}"} for p in (d or [])],
            **({"error": e} if e else {})}


def string_partners(gene, species=9606, limit=10):
    d, e = _get(f"{STRING}/interaction_partners", identifiers=gene, species=species, limit=limit,
                caller_identity="agi-bioxr")
    return {"partners": [{"partner": x.get("preferredName_B"), "score": x.get("score")} for x in (d or [])],
            **({"error": e} if e else {})}


def opentargets_target_drugs(ensembl_id, limit=25):
    """Drugs and clinical candidates acting on a target (Open Targets Platform GraphQL)."""
    q = """query($id:String!){ target(ensemblId:$id){ approvedSymbol drugAndClinicalCandidates { count rows {
      maxClinicalStage drug { id name drugType mechanismsOfAction { rows { mechanismOfAction actionType } } }
      diseases { disease { id name } } } } } }"""
    d, e = HTTP.json("POST", OPENTARGETS, json_body={"query": q, "variables": {"id": ensembl_id}})
    t = ((d or {}).get("data") or {}).get("target")
    if not t:
        err = e or ((d or {}).get("errors") or [{}])[0].get("message")
        return {"count": None if err else 0, "drugs": [], **({"error": err} if err else {})}
    c = t["drugAndClinicalCandidates"]
    return {"symbol": t["approvedSymbol"], "count": c["count"], "drugs": [
        {"chembl_id": r["drug"]["id"], "name": r["drug"]["name"], "type": r["drug"]["drugType"],
         "stage": r["maxClinicalStage"],
         "mechanism": ((r["drug"].get("mechanismsOfAction") or {}).get("rows") or [{}])[0].get("mechanismOfAction"),
         "diseases": sorted({x["disease"]["name"] for x in r.get("diseases") or [] if x.get("disease")})[:6]}
        for r in c["rows"][:limit]]}


# --------------------------------------------------------------------------- compound inventory join

def identify_compounds(compounds, limit=None, chembl=False):
    """Look up extracted compounds ({canonical|smiles, id, ...} dicts from chem_extract / document_ingest) in PubChem.

    Returns one record per input: the original id/smiles plus the PubChem identity (and ChEMBL record if asked).
    """
    out = []
    for c in compounds[:limit] if limit else compounds:
        smi = c.get("canonical") or c.get("smiles")
        ik = (c.get("profile") or {}).get("inchikey") or c.get("inchikey")
        pc = pubchem_identify(smiles=smi, inchikey=ik, synonyms=5, similar=False)
        rec = {"id": c.get("id", c.get("agiId")), "smiles": smi, "source": c.get("source") or c.get("sources"),
               "pubchem": pc}
        if chembl and pc.get("inchikey"):
            rec["chembl"] = chembl_molecule(inchikey=pc["inchikey"])
        out.append(rec)
    return out


def status():
    """What this client layer has actually done in this process (measured, not estimated)."""
    return {"cache": HTTP.cache.path, **HTTP.stats}
