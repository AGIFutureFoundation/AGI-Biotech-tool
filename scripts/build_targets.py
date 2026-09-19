#!/usr/bin/env python3
"""Build data/targets.json from targets_seed.py using live public APIs.

For each seed row this script:
  1. Confirms the UniProt accession really belongs to the stated gene (drops mismatches).
  2. Stores the canonical sequence (used for AlphaFold 3 job export).
  3. Resolves the Ensembl gene ID through Open Targets (used for known-drug lookups).
  4. Records AlphaFold DB model availability and mean pLDDT.
  5. Counts experimental PDB entries and picks a ligand-bound structure.

Standard library only. Usage:  python3 scripts/build_targets.py
"""
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
from targets_seed import SEED, PREFERRED_PDB  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "targets.json")

# Crystallisation additives and ions that should not count as a "drug-like ligand".
ADDITIVES = set("""HOH GOL EDO SO4 PO4 ACT CL NA MG ZN CA K MN CU CU1 FE FE2 NI CO CD IOD BR PEG PGE
DMS MPD TRS EPE MES BME FMT NO3 IMD ACY PG4 1PE P6G 2PE NH4 SCN CIT TAR MLI BU3 ACE NAG MAN BMA FUC GAL
HEM FAD NAD NAP NDP ADP ATP ANP GDP GTP SAH SAM UNX UNL PE8 CXS LDA BOG HEZ PEG BTB""".split())


def get(url, data=None, headers=None, tries=5):
    hdrs = {"User-Agent": "agi-bioxr/1.0", "Accept": "application/json"}
    hdrs.update(headers or {})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                print(f"   ! {url[:90]} -> {e}", file=sys.stderr)
                return None
            time.sleep(1.5 * (i + 1))


def uniprot(acc):
    d = get(f"https://rest.uniprot.org/uniprotkb/{acc}?format=json&fields=gene_names,protein_name,sequence,organism_name")
    if not d:
        return None
    genes = []
    for g in d.get("genes", []):
        if "geneName" in g:
            genes.append(g["geneName"]["value"])
        genes += [s["value"] for s in g.get("synonyms", [])]
    pd = d.get("proteinDescription", {})
    name = (pd.get("recommendedName") or (pd.get("submissionNames") or [{}])[0]).get("fullName", {}).get("value", "")
    return {"genes": genes, "name": name, "sequence": d["sequence"]["value"], "organism": d.get("organism", {}).get("scientificName")}


def ensembl(symbol):
    q = {"query": '{ search(queryString:"%s", entityNames:["target"], page:{index:0,size:5}){ hits { id name } } }' % symbol}
    d = get("https://api.platform.opentargets.org/api/v4/graphql", json.dumps(q).encode(), {"Content-Type": "application/json"})
    for h in (d or {}).get("data", {}).get("search", {}).get("hits", []):
        if h["name"].upper() == symbol.upper():
            return h["id"]
    return None


def alphafold(acc):
    d = get(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}")
    if not d:
        return None
    m = d[0]
    return {"id": m.get("modelEntityId"), "plddt": m.get("globalMetricValue"), "pdbUrl": m.get("pdbUrl"),
            "cifUrl": m.get("cifUrl"), "missenseUrl": m.get("amAnnotationsUrl")}


def rcsb(acc):
    query = {
        "query": {"type": "terminal", "service": "text", "parameters": {
            "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
            "operator": "exact_match", "value": acc}},
        "return_type": "entry",
        "request_options": {"sort": [{"sort_by": "rcsb_entry_info.resolution_combined", "direction": "asc"}],
                            "paginate": {"start": 0, "rows": 40}},
    }
    d = get("https://search.rcsb.org/rcsbsearch/v2/query", json.dumps(query).encode(), {"Content-Type": "application/json"})
    if not d:
        return 0, []
    return d.get("total_count", 0), [r["identifier"] for r in d.get("result_set", [])]


def rcsb_details(ids):
    if not ids:
        return {}
    gql = """{ entries(entry_ids: %s) { rcsb_id struct { title } rcsb_entry_info { resolution_combined experimental_method }
      nonpolymer_entities { nonpolymer_comp { chem_comp { id name formula_weight } } } } }""" % json.dumps(ids)
    d = get("https://data.rcsb.org/graphql", json.dumps({"query": gql}).encode(), {"Content-Type": "application/json"})
    out = {}
    for e in (d or {}).get("data", {}).get("entries", []) or []:
        ligs = []
        for n in e.get("nonpolymer_entities") or []:
            cc = n["nonpolymer_comp"]["chem_comp"]
            if cc["id"] not in ADDITIVES and (cc.get("formula_weight") or 0) >= 0.2:  # kDa -> >= 200 Da
                ligs.append({"id": cc["id"], "name": cc["name"]})
        res = (e.get("rcsb_entry_info") or {}).get("resolution_combined") or [None]
        out[e["rcsb_id"]] = {"title": e["struct"]["title"], "resolution": res[0],
                             "method": e["rcsb_entry_info"]["experimental_method"], "ligands": ligs}
    return out


def build(row):
    symbol, acc, program, disease, why = row
    up = uniprot(acc)
    if not up:
        return None, f"{symbol}/{acc}: UniProt lookup failed"
    if symbol.upper() not in [g.upper() for g in up["genes"]]:
        return None, f"{symbol}/{acc}: accession belongs to {up['genes'][:3]} - dropped"
    total, ids = rcsb(acc)
    pref = PREFERRED_PDB.get(symbol)
    check_ids = ([pref] if pref and pref not in ids else []) + ids
    det = rcsb_details(check_ids[:40])
    structures = [dict(id=i, **det[i]) for i in check_ids if i in det]
    best = None
    if pref and pref in det:
        best = pref
    else:
        for s in structures:
            if s["ligands"]:
                best = s["id"]
                break
        if not best and structures:
            best = structures[0]["id"]
    return {
        "symbol": symbol, "uniprot": acc, "program": program, "disease": disease, "rationale": why,
        "name": up["name"], "length": len(up["sequence"]), "sequence": up["sequence"],
        "ensembl": ensembl(symbol), "alphafold": alphafold(acc),
        "pdbCount": total, "bestPdb": best,
        "structures": [s for s in structures if s["ligands"]][:8] or structures[:4],
    }, None


def main():
    with ThreadPoolExecutor(max_workers=2) as ex:
        results = list(ex.map(build, SEED))
    targets, problems = [], []
    for t, err in results:
        (problems.append(err) if err else targets.append(t))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"generated": time.strftime("%Y-%m-%d"), "targets": targets}, f, indent=1)
    print(f"wrote {len(targets)} targets -> {OUT}")
    for t in targets:
        af = t["alphafold"]
        print(f"  {t['symbol']:9} {t['uniprot']:7} len={t['length']:5} pdb={t['pdbCount']:4} best={t['bestPdb']} "
              f"AF={'%.0f' % af['plddt'] if af and af.get('plddt') else '-'} ens={t['ensembl']}")
    for p in problems:
        print("PROBLEM:", p)


if __name__ == "__main__":
    main()
