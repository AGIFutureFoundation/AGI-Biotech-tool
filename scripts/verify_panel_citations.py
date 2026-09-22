#!/usr/bin/env python3
"""Re-resolve every identifier a disease panel cites, against the live services.

The panel in server/disease_panels.py is only worth as much as its citations. This script takes a
panel name, walks its evidence records and asks each source whether the record still exists and
still says what the panel claims it says:

    UniProt accession  -> exists, and its gene names include the panel's symbol
    PDB ids            -> the RCSB search for that accession returns the cited entry, and the
                          panel's pdb_count is not larger than the live count
    AlphaFold model    -> the predicted model id matches (or, when the panel says alphafold=False,
                          that no model exists)
    ChEMBL target      -> exists and its components carry the accession; when the panel asserts
                          `chembl_target: None`, ChEMBL must still have no single-protein target
    potent ligands     -> live count of activities at pChEMBL >= 6 is not below the claimed count
                          (and is still zero where the panel claims no chemical matter)
    ChEMBL drug        -> molecule exists, its preferred name matches the drug named, and its
                          curated mechanism still points at this target
    NCT number         -> study exists on ClinicalTrials.gov and still lists CHILD in its std ages
    PubMed PMID        -> record exists, and the verbatim phrase the panel quotes is still in the
                          abstract

Anything that fails to resolve is a failure, and any failure makes the script exit non-zero. A
network error is a failure too: a citation that cannot be checked has not been verified.

    .venv/bin/python scripts/verify_panel_citations.py                # StJude, cached responses ok
    .venv/bin/python scripts/verify_panel_citations.py --no-cache     # force live calls
    .venv/bin/python scripts/verify_panel_citations.py --seed-bad     # prove the checker can fail

--seed-bad adds one synthetic target whose every identifier is deliberately wrong, including a real
PMID with a quote that is not in its abstract. Use it to confirm the checker still fails when it
should before trusting a passing run.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "server"))

# A target that exists in no database, used by --seed-bad to prove the checks can fail.
BAD_SEED = ("ZZZBAD", {
    'indication': 'deliberately broken control record',
    'uniprot': 'Q0Q0Q0', 'pdb_ids': ['9ZZZ'], 'alphafold_model': 'AF-Q0Q0Q0-F1',
    'chembl_target': 'CHEMBL99999999', 'potent_ligands': 10,
    'drugs': [{'chembl_id': 'CHEMBL99999998', 'name': 'notadrug'}],
    'trials': [{'nct_id': 'NCT99999999', 'note': 'no such study'}],
    'claims': [{'pmid': '999999999', 'quote': 'no such record'},
               # a real PMID whose abstract does not contain this sentence
               {'pmid': '36807339', 'quote': 'ALK point mutations occurred in 99.9% of all cases'}],
}, {'symbol': 'ZZZBAD', 'name': 'deliberately broken control', 'inheritance': 'N/A',
    'prevalence': 'n/a', 'mechanism': 'control record', 'pdb_count': 5, 'alphafold': True})


def norm(text):
    return " ".join((text or "").split())


class Report:
    """Collects pass/fail lines and decides the exit code."""

    def __init__(self, verbose=True):
        self.rows, self.verbose = [], verbose

    def check(self, target, kind, identifier, ok, detail=""):
        self.rows.append((target, kind, identifier, bool(ok), detail))
        if self.verbose:
            print(f"  [{'PASS' if ok else 'FAIL'}] {kind:<14} {identifier:<22} {detail}", flush=True)
        return ok

    @property
    def failures(self):
        return [r for r in self.rows if not r[3]]


def check_protein(db, report, symbol, ev, target):
    acc = ev['uniprot']
    entry, err = db.HTTP.json("GET", f"{db.UNIPROT}/{acc}.json")
    genes = [g.get("geneName", {}).get("value") for g in (entry or {}).get("genes", [])]
    synonyms = [s.get("value") for g in (entry or {}).get("genes", []) for s in g.get("synonyms", [])]
    ok = bool(entry) and symbol in (genes + synonyms)
    report.check(symbol, "uniprot", acc, ok,
                 f"genes={genes}" if entry else f"did not resolve ({err or 'not found'})")

    want = ev.get('pdb_ids') or []
    rows = max(target.get('pdb_count') or 0, len(want), 1)
    hits = db.pdb_structures(acc, rows=rows)
    live = hits.get("count")
    if live is None:
        report.check(symbol, "pdb-search", acc, False, f"RCSB did not answer ({hits.get('error')})")
        for pdb_id in want:
            report.check(symbol, "pdb", pdb_id, False, f"unverified: no RCSB answer for {acc}")
    else:
        for pdb_id in want:
            report.check(symbol, "pdb", pdb_id, pdb_id in hits["ids"],
                         "in RCSB entries for " + acc if pdb_id in hits["ids"]
                         else f"not among the {live} RCSB entries for {acc}")
            entry_rec = db.pdb_entry(pdb_id)
            report.check(symbol, "pdb-entry", pdb_id, bool(entry_rec.get("title")),
                         norm(entry_rec.get("title"))[:60] or f"did not resolve ({entry_rec.get('error')})")
        claimed = target.get('pdb_count')
        report.check(symbol, "pdb_count", str(claimed), claimed is not None and claimed <= live,
                     f"panel claims {claimed}, RCSB has {live}")

    model = db.alphafold_model(acc)
    if target.get('alphafold'):
        report.check(symbol, "alphafold", ev.get('alphafold_model') or "-",
                     model.get("model") == ev.get('alphafold_model'),
                     f"live model={model.get('model')} pLDDT={model.get('mean_plddt')}")
    else:
        report.check(symbol, "alphafold", acc, model.get("model") is None,
                     "panel claims no model; AlphaFold returned " + str(model.get("model")))


def check_chemistry(db, report, symbol, ev):
    acc, tid = ev['uniprot'], ev.get('chembl_target')
    claimed = ev.get('potent_ligands')
    if tid is None:
        found, _ = db._get(f"{db.CHEMBL}/target.json", target_components__accession=acc,
                           target_type="SINGLE PROTEIN")
        ids = [t["target_chembl_id"] for t in (found or {}).get("targets", [])]
        report.check(symbol, "chembl-target", "(none claimed)", found is not None and not ids,
                     "ChEMBL has no single-protein target for " + acc if found is not None and not ids
                     else f"ChEMBL now has {ids}")
    else:
        rec, err = db._get(f"{db.CHEMBL}/target/{tid}.json")
        comps = [c.get("accession") for c in (rec or {}).get("target_components", [])]
        report.check(symbol, "chembl-target", tid, bool(rec) and acc in comps,
                     f"components={comps}" if rec else f"did not resolve ({err or 'not found'})")
        acts, aerr = db._get(f"{db.CHEMBL}/activity.json", target_chembl_id=tid,
                             pchembl_value__gte=6, limit=1)
        live = (acts or {}).get("page_meta", {}).get("total_count")
        if live is None:
            report.check(symbol, "ligands", str(claimed), False, f"ChEMBL did not answer ({aerr})")
        elif claimed == 0:
            report.check(symbol, "ligands", "0", live == 0,
                         f"panel claims no potent ligand; ChEMBL has {live}")
        else:
            report.check(symbol, "ligands", str(claimed), claimed <= live,
                         f"panel claims {claimed}, ChEMBL has {live} at pChEMBL>=6")

    for drug in ev.get('drugs') or []:
        cid, name = drug['chembl_id'], drug['name']
        mol = db.chembl_molecule(chembl_id=cid) or {}
        pref = norm(mol.get("name"))
        report.check(symbol, "chembl-drug", cid, bool(pref) and name.lower() in pref.lower(),
                     f"{pref or 'did not resolve'} (panel says {name}), max_phase={mol.get('max_phase')}")
        targets = {m.get("target_chembl_id") for m in db.chembl_mechanisms(cid)}
        linked = []
        for mt in filter(None, targets):
            rec, _ = db._get(f"{db.CHEMBL}/target/{mt}.json")
            if acc in [c.get("accession") for c in (rec or {}).get("target_components", [])]:
                linked.append(mt)
        report.check(symbol, "drug-target", cid, bool(linked),
                     f"mechanism targets {sorted(filter(None, targets))} -> {acc}: "
                     + (", ".join(linked) if linked else "no link"))


def check_trials(db, report, symbol, ev):
    for trial in ev.get('trials') or []:
        nct = trial['nct_id']
        rec, err = db._get(f"{db.CTGOV}/{nct}")
        protocol = (rec or {}).get("protocolSection", {})
        ages = protocol.get("eligibilityModule", {}).get("stdAges", [])
        status = protocol.get("statusModule", {}).get("overallStatus")
        report.check(symbol, "nct", nct, bool(protocol) and "CHILD" in ages,
                     f"{status}, ages={ages}" if protocol else f"did not resolve ({err or 'not found'})")


def check_claims(db, report, symbol, ev):
    claims = ev.get('claims') or []
    pmids = sorted({c['pmid'] for c in claims})
    if not pmids:
        return
    summaries = {s["pmid"]: s for s in db.pubmed_summaries(pmids)}
    abstracts = {k: norm(v) for k, v in db.pubmed_abstracts(pmids).items()}
    for pmid in pmids:
        summary = summaries.get(pmid)
        report.check(symbol, "pmid", pmid, bool(summary and summary.get("title")),
                     norm(summary.get("title"))[:60] if summary else "did not resolve in PubMed")
    for claim in claims:
        quote = norm(claim['quote'])
        report.check(symbol, "quote", claim['pmid'], quote in abstracts.get(claim['pmid'], ""),
                     f'"{quote[:58]}"')


def verify(panel_name, seed_bad=False, verbose=True):
    import disease_panels as panels
    import db_clients as db

    panel = panels.get_panel(panel_name)
    if not panel:
        print(f"no such panel: {panel_name}; have {panels.list_panels()}")
        return 2
    evidence = dict(getattr(panels, f"{panel_name.upper()}_EVIDENCE", {}))
    targets = list(panel["targets"])
    if seed_bad:
        symbol, ev, target = BAD_SEED
        evidence[symbol], targets = ev, targets + [target]
        print(f"!! --seed-bad: added the control target {symbol}; this run MUST fail\n")

    report = Report(verbose)
    print(f"{panel['name']}: {len(targets)} targets, checking citations against live services\n")
    for target in targets:
        symbol = target["symbol"]
        ev = evidence.get(symbol)
        print(f"{symbol} - {(ev or {}).get('indication', 'no evidence record')}")
        if not ev:
            report.check(symbol, "evidence", symbol, False, "no evidence record: nothing to re-resolve")
            continue
        check_protein(db, report, symbol, ev, target)
        check_chemistry(db, report, symbol, ev)
        check_trials(db, report, symbol, ev)
        check_claims(db, report, symbol, ev)
        print()

    failures = report.failures
    print("-" * 78)
    print(f"{len(report.rows) - len(failures)}/{len(report.rows)} checks passed; "
          f"database activity: {db.status()}")
    if failures:
        print(f"\n{len(failures)} FAILED:")
        for symbol, kind, identifier, _, detail in failures:
            print(f"  {symbol:<8} {kind:<14} {identifier:<22} {detail}")
        return 1
    print("every cited identifier re-resolved.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("panel", nargs="?", default="StJude", help="panel key in DISEASE_PANELS")
    ap.add_argument("--seed-bad", action="store_true",
                    help="add a control target with bad identifiers; the run must then fail")
    ap.add_argument("--no-cache", action="store_true",
                    help="bypass the db_clients response cache and call every service live")
    ap.add_argument("-q", "--quiet", action="store_true", help="only print failures and the summary")
    args = ap.parse_args(argv)
    if args.no_cache:
        os.environ["AGI_DB_CACHE"] = "off"
    return verify(args.panel, seed_bad=args.seed_bad, verbose=not args.quiet)


if __name__ == "__main__":
    sys.exit(main())
