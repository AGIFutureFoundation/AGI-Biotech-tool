"""Retrospective check: does the engine rediscover repurposings it was not told about?

This is the only evidence that server/repurposing_engine.py produces something
better than plausible-sounding noise. A ranked list looks equally convincing
whether or not it is right, so the question has to be asked against cases where
the answer is already known and independently documented.

How the blinding works, and why it is not circular
--------------------------------------------------
For each case the engine runs with:

  * exclude_self=True -- the compound and its entire salt family are removed from
    the precedent set. Sildenafil cannot be evidence for sildenafil. The
    hypothesis must be carried by *other* drugs on the same target.
  * blind_disease_ids -- the compound's own record for the known second
    indication is hidden, so it is not filtered out as "already approved". This
    reconstructs the state of knowledge before the repurposing was found.

What is supplied per case is the *question* (which compound, which indication to
look for in the output), never the answer path. No case tells the engine which
target, which precedent drug, or which join should produce the hit. A case is
recovered when the held-out indication appears in the ranked hypotheses; the rank
it appears at is reported, because appearing at position 300 is not a recovery in
any practical sense.

Run:  .venv/bin/python scripts/validate_repurposing_recall.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# server/ holds the modules below and imports its siblings by bare name, matching
# what tests/conftest.py does for the suite and the other scripts here.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "server"))

import disease_panels
import repurposing_engine as engine

# Each case: a documented repurposing, the compound's ChEMBL id, and substrings
# that identify the held-out indication in Open Targets' disease vocabulary.
# `original` records what the drug was first developed or approved for, which is
# what makes the second indication a repurposing rather than a line extension.
KNOWN_CASES = [
    {
        "compound": "sildenafil", "chembl_id": "CHEMBL192",
        "original": "angina pectoris (developed), erectile dysfunction (first approval, 1998)",
        "repurposed_to": "pulmonary arterial hypertension",
        "documented": "FDA approval of Revatio for PAH, 2005",
        "match": ["pulmonary hypertension", "pulmonary arterial hypertension"],
    },
    {
        "compound": "thalidomide", "chembl_id": "CHEMBL468",
        "original": "sedative / antiemetic (withdrawn 1961); erythema nodosum leprosum (1998)",
        "repurposed_to": "multiple myeloma",
        "documented": "FDA approval for newly diagnosed multiple myeloma, 2006",
        "match": ["plasma cell myeloma", "multiple myeloma"],
    },
    {
        "compound": "tretinoin", "chembl_id": "CHEMBL38",
        "original": "acne vulgaris and photoaging (topical retinoid)",
        "repurposed_to": "acute promyelocytic leukaemia",
        "documented": "oral ATRA differentiation therapy for APL; FDA approval 1995",
        "match": ["promyelocytic leukemia", "promyelocytic leukaemia"],
    },
    {
        "compound": "minoxidil", "chembl_id": "CHEMBL802",
        "original": "severe refractory hypertension (oral, 1979)",
        "repurposed_to": "androgenetic alopecia",
        "documented": "topical minoxidil for androgenetic alopecia; FDA approval 1988",
        "match": ["alopecia"],
    },
    {
        "compound": "raloxifene", "chembl_id": "CHEMBL81",
        "original": "postmenopausal osteoporosis",
        "repurposed_to": "breast cancer risk reduction",
        "documented": "FDA approval for reduction of invasive breast cancer risk, 2007",
        "match": ["breast carcinoma", "breast cancer", "breast neoplasm"],
    },
    {
        "compound": "metformin", "chembl_id": "CHEMBL1431",
        "original": "type 2 diabetes mellitus",
        "repurposed_to": "oncology (investigational)",
        "documented": "large investigational programme; not approved for any cancer",
        "match": ["breast carcinoma", "prostate carcinoma", "colorectal", "endometrial",
                  "pancreatic", "neoplasm", "cancer"],
    },
    {
        "compound": "dimethyl fumarate", "chembl_id": "CHEMBL2107333",
        "original": "psoriasis (Fumaderm, Germany, 1994)",
        "repurposed_to": "relapsing multiple sclerosis",
        "documented": "FDA approval of Tecfidera for relapsing MS, 2013",
        "match": ["multiple sclerosis"],
    },
]

# Negative controls. If these score like the positives, the scoring is broken --
# a ranked list where everything ranks high carries no information.
NEGATIVE_CONTROLS = [
    {
        "compound": "mannitol", "chembl_id": "CHEMBL689",
        "why": "an osmotic agent whose effect is colligative, not receptor-mediated; "
               "there is no target to repurpose through",
    },
    {
        "compound": "AGI inventory compound (no database identity)",
        "smiles": "FC(F)(F)c1ccc(-n2ccnc2-c2cccc3nccnc23)cc1",
        "why": "a structure extracted from the user's own documents with no ChEMBL "
               "record; the engine should decline rather than improvise",
    },
]

TOP_N = (10, 25)


def _match(text, patterns):
    low = (text or "").lower()
    return any(p.lower() in low for p in patterns)


def run_case(case, limit=250, verbose=True):
    """Run one blinded case. Returns the outcome record."""
    probe = engine.generate_hypotheses(chembl_id=case["chembl_id"], name=case["compound"],
                                       label=case["compound"], include_network=False, limit=1)
    if probe.get("error"):
        return {**case, "recovered": False, "rank": None, "failure": probe["error"]}

    held_out = [row["disease_id"] for row in probe["existing_indications"]
                if _match(row["disease"], case["match"])]

    report = engine.generate_hypotheses(
        chembl_id=case["chembl_id"], name=case["compound"], label=case["compound"],
        include_network=False, limit=limit, blind_disease_ids=held_out)

    hits = [(i + 1, h) for i, h in enumerate(report["hypotheses"])
            if _match(h["disease"], case["match"])]
    out = {
        "compound": case["compound"], "chembl_id": case["chembl_id"],
        "original_indication": case["original"], "repurposed_to": case["repurposed_to"],
        "documented": case["documented"],
        "targets": [t.get("symbol") for t in report.get("targets", [])],
        "candidates_considered": report["counts"]["candidate_diseases"],
        "held_out_disease_ids": held_out,
        "recovered": bool(hits),
        "rank": hits[0][0] if hits else None,
        "score": hits[0][1]["score"] if hits else None,
        "matched_disease": hits[0][1]["disease"] if hits else None,
        "supporting_terms": [t["statement"] for t in hits[0][1]["terms"]] if hits else [],
        "status_in_report": hits[0][1]["status"] if hits else None,
    }
    if not hits:
        out["failure"] = _diagnose(report, case)
    if verbose:
        _print_case(out)
    return out


def _diagnose(report, case):
    """Say why a case was missed, specifically. 'It failed' is not a finding."""
    if not report.get("targets"):
        mech = report.get("mechanisms") or []
        if not mech:
            return ("no ChEMBL mechanism-of-action annotation for this compound or its salt "
                    "family, so the mechanism join has no target to start from")
        return ("mechanism targets exist but none resolved to an Ensembl gene, so Open Targets "
                "could not be queried")
    failed = report["diagnostics"]["mechanism"].get("targets_failed") or []
    if failed:
        return f"Open Targets lookup failed for {[f['symbol'] for f in failed]}: {failed[0]['error']}"
    queried = report["diagnostics"]["mechanism"].get("targets_queried") or []
    empty = [q for q in queried if not q["precedent_drugs"]]
    if empty and len(empty) == len(queried):
        return (f"targets {[q['symbol'] for q in empty]} resolved, but no *other* drug has a "
                "clinical record against them; with the compound itself excluded there is no "
                "precedent to transfer")
    return (f"targets {[q['symbol'] for q in queried]} have precedent drugs, but none of them "
            f"has a registered clinical record in an indication matching {case['match']}; the "
            "second indication is not reachable from shared-target evidence")


def run_negative_control(control, verbose=True):
    report = engine.generate_hypotheses(
        chembl_id=control.get("chembl_id"), smiles=control.get("smiles"),
        name=control.get("compound") if control.get("chembl_id") else None,
        label=control["compound"], include_network=False, limit=10)
    top = report["hypotheses"][0]["score"] if report.get("hypotheses") else 0.0
    out = {"compound": control["compound"], "why": control["why"],
           "resolved": not report.get("error"), "error": report.get("error"),
           "targets": [t.get("symbol") for t in report.get("targets", [])],
           "hypotheses": len(report.get("hypotheses", [])),
           "top_score": top,
           "top_disease": report["hypotheses"][0]["disease"] if report.get("hypotheses") else None}
    if verbose:
        print(f"  {out['compound']:52s} hypotheses={out['hypotheses']:4d} "
              f"top_score={out['top_score']:.2f} "
              f"{'| ' + (out['error'] or '') if out.get('error') else ''}")
    return out


def _print_case(out):
    verdict = f"rank {out['rank']:>3} (score {out['score']:.2f})" if out["recovered"] else "MISSED"
    print(f"  {out['compound']:20s} -> {out['repurposed_to']:34s} {verdict:>24s}   "
          f"of {out['candidates_considered']} candidates, targets={out['targets']}")
    if not out["recovered"]:
        print(f"      why: {out['failure']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", help="write the full result set here")
    ap.add_argument("--limit", type=int, default=250,
                    help="how deep in the ranking a hit still counts (default 250)")
    args = ap.parse_args(argv)

    print("Known-case rediscovery (compound self-excluded from its own evidence, "
          "known second indication blinded)\n")
    cases = [run_case(c, limit=args.limit) for c in KNOWN_CASES]

    print("\nNegative controls (should not look like the positives)\n")
    controls = [run_negative_control(c) for c in NEGATIVE_CONTROLS]

    recovered = [c for c in cases if c["recovered"]]
    summary = {
        "cases": len(cases), "recovered": len(recovered),
        "recall_any_rank": round(len(recovered) / len(cases), 3),
        **{f"recall_top_{n}": round(sum(1 for c in recovered if c["rank"] <= n) / len(cases), 3)
           for n in TOP_N},
        "median_rank_of_recovered": (sorted(c["rank"] for c in recovered)[len(recovered) // 2]
                                     if recovered else None),
        "failures": [{"compound": c["compound"], "why": c["failure"]}
                     for c in cases if not c["recovered"]],
        "negative_control_top_score": max([c["top_score"] for c in controls] or [0.0]),
        "best_positive_score": max([c["score"] for c in recovered] or [0.0]),
    }
    print("\nSummary")
    print(f"  recovered at any rank : {summary['recovered']}/{summary['cases']} "
          f"({summary['recall_any_rank']:.0%})")
    for n in TOP_N:
        print(f"  recovered in top {n:<3}  : {summary[f'recall_top_{n}']:.0%}")
    print(f"  best positive score   : {summary['best_positive_score']:.2f}")
    print(f"  best control score    : {summary['negative_control_top_score']:.2f}")
    for f in summary["failures"]:
        print(f"  MISS {f['compound']}: {f['why']}")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"summary": summary, "cases": cases, "negative_controls": controls,
                       "scoring": engine.SCORING}, fh, indent=2)
        print(f"\n  wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
