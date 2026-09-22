#!/usr/bin/env python3
"""Re-resolve every identifier the longevity track cites, against the live services.

This is the longevity track's own checker. It does not import, modify or depend on
scripts/verify_panel_citations.py -- that script belongs to the disease panels and a checker
edited to accommodate new data proves nothing about the data.

It is deliberately STRICTER than the disease-panel checker in three places, because the failure
modes of a longevity track are different:

  * quotes are checked on `failed_claims` as well as `claims`. The negative results are the most
    load-bearing citations in this track, so they get the same verbatim substring check. A real
    PMID attached to a claim its abstract does not make is the exact failure this field produces.
  * trial ages are checked in BOTH directions. Each trial declares `pediatric_enrollment`, and the
    run fails if CT.gov's stdAges disagree either way. Asserting only "enrols children" would let
    an adult-only trial be quietly relabelled; this track contains adult-only trials on purpose
    and has to be honest about which ones they are.
  * `alphafold_model: None` is a positive assertion that AlphaFold DB has no model, and is
    checked as such. ATM (Q13315) is the real case: 3056 residues, no model in the database.

Everything else mirrors the panel schema:

    UniProt accession  -> resolves, and its gene names or synonyms include the panel's symbol
    PDB ids            -> the RCSB search for that accession returns each cited entry, each entry
                          resolves, and pdb_count is not larger than the live count
    AlphaFold          -> the predicted model id matches, or no model exists where None is claimed
    ChEMBL target      -> resolves and its components carry the accession; where the record says
                          `chembl_target: None`, ChEMBL must still have no single-protein target
    potent ligands     -> live count at pChEMBL >= 6 is not below the claimed count
    ChEMBL drug        -> molecule resolves, preferred name matches, and its curated mechanism
                          still points at a target carrying this accession
    ClinVar            -> live pathogenic-variant count for the gene is not below the claim
    NCT number         -> study resolves and its stdAges match the declared pediatric_enrollment
    PubMed PMID        -> record resolves, and every quoted phrase is still in the abstract

A network error is a failure: a citation that could not be checked has not been verified.

    .venv/bin/python scripts/verify_longevity_citations.py               # cached responses ok
    .venv/bin/python scripts/verify_longevity_citations.py --no-cache    # force live calls
    .venv/bin/python scripts/verify_longevity_citations.py --seed-bad    # prove it can fail
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "server"))

# A control target whose every identifier is wrong. --seed-bad splices it in so a passing run can
# be distinguished from a checker that cannot fail. The last two claims are the important ones:
# real, resolvable PMIDs carrying sentences their abstracts do not contain -- once in `claims`
# and once in `failed_claims`, so both quote paths are proven to bite.
BAD_SEED_SYMBOL = "ZZZLONGEVITY"
BAD_SEED_EVIDENCE = {
    'arm': 'progeroid-pediatric', 'pediatric_onset': True,
    'indication': 'deliberately broken control record',
    'evidence_class': 'no-therapeutic',
    'uniprot': 'Q0Q0Q0', 'pdb_ids': ['9ZZZ'], 'alphafold_model': 'AF-Q0Q0Q0-F1',
    'chembl_target': 'CHEMBL99999999', 'potent_ligands': 10,
    'clinvar_pathogenic': 999999,
    'drugs': [{'chembl_id': 'CHEMBL99999998', 'name': 'notadrug'}],
    'trials': [{'nct_id': 'NCT99999999', 'pediatric_enrollment': True, 'note': 'no such study'},
               # a REAL adult-only study mislabelled as enrolling children
               {'nct_id': 'NCT03574597', 'pediatric_enrollment': True,
                'note': 'SELECT is adult-only; this mislabel must be caught'}],
    'claims': [{'pmid': '999999999', 'quote': 'no such record'},
               # a real PMID whose abstract does not contain this sentence
               {'pmid': '29710166', 'quote': 'lonafarnib cured every child in the cohort'}],
    'failed_claims': [{'claim': 'control', 'pmid': '19587680',
                       'quote': 'rapamycin extended human lifespan by 40%'}],
    'human_evidence': 'none', 'model_organism_evidence': 'none',
    'tractability': 'control record', 'unmet_need': 'control record', 'caveat': 'control record',
}
BAD_SEED_TARGET = {'symbol': BAD_SEED_SYMBOL, 'name': 'deliberately broken control',
                   'inheritance': 'N/A', 'prevalence': 'n/a', 'mechanism': 'control record',
                   'pdb_count': 5, 'alphafold': True}


def norm(text):
    return " ".join((text or "").split())


class Report:
    """Collects pass/fail lines and decides the exit code."""

    def __init__(self, verbose=True):
        self.rows, self.verbose = [], verbose

    def check(self, target, kind, identifier, ok, detail=""):
        self.rows.append((target, kind, identifier, bool(ok), detail))
        if self.verbose:
            print(f"  [{'PASS' if ok else 'FAIL'}] {kind:<16} {identifier:<22} {detail}", flush=True)
        return ok

    @property
    def failures(self):
        return [r for r in self.rows if not r[3]]


def check_protein(db, report, symbol, ev, target):
    acc = ev['uniprot']
    entry, err = db.HTTP.json("GET", f"{db.UNIPROT}/{acc}.json")
    genes = [g.get("geneName", {}).get("value") for g in (entry or {}).get("genes", [])]
    synonyms = [s.get("value") for g in (entry or {}).get("genes", [])
                for s in g.get("synonyms", [])]
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
            present = pdb_id in hits["ids"]
            report.check(symbol, "pdb", pdb_id, present,
                         f"in RCSB entries for {acc}" if present
                         else f"not among the {live} RCSB entries for {acc}")
            rec = db.pdb_entry(pdb_id)
            report.check(symbol, "pdb-entry", pdb_id, bool(rec.get("title")),
                         norm(rec.get("title"))[:58] or f"did not resolve ({rec.get('error')})")
        claimed = target.get('pdb_count')
        report.check(symbol, "pdb_count", str(claimed),
                     claimed is not None and claimed <= live,
                     f"record claims {claimed}, RCSB has {live}")

    model = db.alphafold_model(acc)
    claimed_model = ev.get('alphafold_model')
    if claimed_model is None:
        # A positive assertion that AlphaFold DB has no model for this accession.
        report.check(symbol, "alphafold-none", acc, model.get("model") is None,
                     "record claims no model; AlphaFold returned " + str(model.get("model")))
    else:
        report.check(symbol, "alphafold", claimed_model,
                     model.get("model") == claimed_model,
                     f"live model={model.get('model')} pLDDT={model.get('mean_plddt')}")
    # The panel-level boolean must agree with the evidence-level model id.
    report.check(symbol, "alphafold-flag", str(target.get('alphafold')),
                 bool(target.get('alphafold')) == (claimed_model is not None),
                 f"panel alphafold={target.get('alphafold')}, evidence model={claimed_model}")


def check_chemistry(db, report, symbol, ev):
    acc, tid = ev['uniprot'], ev.get('chembl_target')
    claimed = ev.get('potent_ligands')
    if tid is None:
        found, _ = db._get(f"{db.CHEMBL}/target.json", target_components__accession=acc,
                           target_type="SINGLE PROTEIN")
        ids = [t["target_chembl_id"] for t in (found or {}).get("targets", [])]
        ok = found is not None and not ids
        report.check(symbol, "chembl-target", "(none claimed)", ok,
                     f"ChEMBL has no single-protein target for {acc}" if ok
                     else f"ChEMBL now has {ids}")
    else:
        rec, err = db._get(f"{db.CHEMBL}/target/{tid}.json")
        comps = [c.get("accession") for c in (rec or {}).get("target_components", [])]
        report.check(symbol, "chembl-target", tid, bool(rec) and acc in comps,
                     f"{(rec or {}).get('target_type')} components={comps}" if rec
                     else f"did not resolve ({err or 'not found'})")
        acts, aerr = db._get(f"{db.CHEMBL}/activity.json", target_chembl_id=tid,
                             pchembl_value__gte=6, limit=1)
        live = (acts or {}).get("page_meta", {}).get("total_count")
        if live is None:
            report.check(symbol, "ligands", str(claimed), False, f"ChEMBL did not answer ({aerr})")
        elif claimed == 0:
            report.check(symbol, "ligands", "0", live == 0,
                         f"record claims no potent ligand; ChEMBL has {live}")
        else:
            report.check(symbol, "ligands", str(claimed), claimed <= live,
                         f"record claims {claimed}, ChEMBL has {live} at pChEMBL>=6")

    for drug in ev.get('drugs') or []:
        cid, name = drug['chembl_id'], drug['name']
        mol = db.chembl_molecule(chembl_id=cid) or {}
        pref = norm(mol.get("name"))
        report.check(symbol, "chembl-drug", cid,
                     bool(pref) and name.lower() in pref.lower(),
                     f"{pref or 'did not resolve'} (record says {name}), "
                     f"max_phase={mol.get('max_phase')}")
        targets = {m.get("target_chembl_id") for m in db.chembl_mechanisms(cid)}
        linked = []
        for mt in filter(None, targets):
            rec, _ = db._get(f"{db.CHEMBL}/target/{mt}.json")
            if acc in [c.get("accession") for c in (rec or {}).get("target_components", [])]:
                linked.append(mt)
        report.check(symbol, "drug-target", cid, bool(linked),
                     f"mechanism targets {sorted(filter(None, targets))} -> {acc}: "
                     + (", ".join(linked) if linked else "NO LINK"))


def check_clinvar(db, report, symbol, ev):
    claimed = ev.get('clinvar_pathogenic')
    if claimed is None:
        return
    res = db.clinvar_variants(symbol, pathogenic_only=True, retmax=1)
    live = res.get("count")
    if live is None:
        report.check(symbol, "clinvar", str(claimed), False,
                     f"ClinVar did not answer ({res.get('error')})")
    else:
        report.check(symbol, "clinvar", str(claimed), claimed <= live,
                     f"record claims {claimed} pathogenic, ClinVar has {live}")


def check_trials(db, report, symbol, ev):
    for trial in ev.get('trials') or []:
        nct = trial['nct_id']
        want_child = bool(trial.get('pediatric_enrollment'))
        rec, err = db._get(f"{db.CTGOV}/{nct}")
        protocol = (rec or {}).get("protocolSection", {})
        if not protocol:
            report.check(symbol, "nct", nct, False, f"did not resolve ({err or 'not found'})")
            continue
        ages = protocol.get("eligibilityModule", {}).get("stdAges", [])
        status = protocol.get("statusModule", {}).get("overallStatus")
        has_child = "CHILD" in ages
        report.check(symbol, "nct", nct, True, f"{status}, ages={ages}")
        # Both directions: the declared flag has to match the registry, either way round.
        report.check(symbol, "nct-pediatric", nct, has_child == want_child,
                     f"record says pediatric_enrollment={want_child}, CT.gov stdAges={ages}")


def check_claims(db, report, symbol, ev):
    """Quote-check `claims` and `failed_claims` together: both are load-bearing citations."""
    claims = [(c, "quote") for c in (ev.get('claims') or [])]
    claims += [(c, "quote-failed") for c in (ev.get('failed_claims') or [])]
    if not claims:
        return
    pmids = sorted({c['pmid'] for c, _ in claims})
    summaries = {s["pmid"]: s for s in db.pubmed_summaries(pmids)}
    abstracts = {k: norm(v) for k, v in db.pubmed_abstracts(pmids).items()}
    for pmid in pmids:
        summary = summaries.get(pmid)
        report.check(symbol, "pmid", pmid, bool(summary and summary.get("title")),
                     norm(summary.get("title"))[:58] if summary else "did not resolve in PubMed")
    for claim, kind in claims:
        quote = norm(claim['quote'])
        abstract = abstracts.get(claim['pmid'], "")
        ok = bool(quote) and quote in abstract
        report.check(symbol, kind, claim['pmid'], ok,
                     f'"{quote[:54]}"' + ("" if ok else "  NOT IN ABSTRACT"))


def check_narrative(report, symbol, ev):
    """Offline structural checks that the track's own honesty rules were not skipped."""
    import longevity_panel as panel
    report.check(symbol, "evidence-class", ev.get('evidence_class') or "-",
                 ev.get('evidence_class') in panel.EVIDENCE_CLASSES,
                 "declared tier of evidence")
    for field in ("human_evidence", "model_organism_evidence"):
        report.check(symbol, field.replace("_", "-"), field,
                     bool((ev.get(field) or "").strip()),
                     "stated separately" if (ev.get(field) or "").strip() else "EMPTY")


def verify(seed_bad=False, verbose=True):
    import longevity_panel as panel
    import db_clients as db

    p = panel.get_panel("Longevity")
    evidence = dict(panel.LONGEVITY_EVIDENCE)
    targets = list(p["targets"])
    if seed_bad:
        evidence[BAD_SEED_SYMBOL] = BAD_SEED_EVIDENCE
        targets = targets + [BAD_SEED_TARGET]
        print(f"!! --seed-bad: added the control target {BAD_SEED_SYMBOL}; this run MUST fail\n")

    report = Report(verbose)
    print(f"{p['name']}: {len(targets)} targets, checking citations against live services\n")
    for target in targets:
        symbol = target["symbol"]
        ev = evidence.get(symbol)
        arm = (ev or {}).get("arm", "?")
        print(f"{symbol} [{arm}] - {(ev or {}).get('indication', 'no evidence record')}")
        if not ev:
            report.check(symbol, "evidence", symbol, False,
                         "no evidence record: nothing to re-resolve")
            continue
        check_narrative(report, symbol, ev)
        check_protein(db, report, symbol, ev, target)
        check_chemistry(db, report, symbol, ev)
        check_clinvar(db, report, symbol, ev)
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
            print(f"  {symbol:<14} {kind:<16} {identifier:<22} {detail}")
        return 1
    print("every cited identifier re-resolved, and every quote is still in its abstract.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed-bad", action="store_true",
                    help="add a control target with bad identifiers; the run must then fail")
    ap.add_argument("--no-cache", action="store_true",
                    help="bypass the db_clients response cache and call every service live")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="only print failures and the summary")
    args = ap.parse_args(argv)
    if args.no_cache:
        os.environ["AGI_DB_CACHE"] = "off"
    return verify(seed_bad=args.seed_bad, verbose=not args.quiet)


if __name__ == "__main__":
    sys.exit(main())
