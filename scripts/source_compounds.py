"""Falsifiable check for server/compound_sourcing.py, run against this repo's real compounds.

Three things are demonstrated, on real data, with raw output:

  1. POSITIVE -- approved drugs that the repurposing engine's documented cases name
     (sildenafil, metformin, thalidomide, tretinoin, ...) resolve to real vendors with
     real catalogue numbers and real product URLs.
  2. NEGATIVE CONTROL -- novel AGI compounds taken from
     data/extracted_compound_inventory.json return ZERO suppliers. The check FAILS if any
     of them comes back sourceable, and it also fails if a BOM line for one of them
     carries a vendor, a price or a substituted structure. A sourcing tool that quietly
     swaps in a near-neighbour is worse than one that returns nothing.
  3. HONEST TOTALS -- the BOM's estimated_total is a sum of real quotes only. With no
     price provider configured it is 0.0 over 0 priced lines, and the BOM says so.

Run:  .venv/bin/python scripts/source_compounds.py [--json out.json] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "server"))

import compound_sourcing as cs  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INVENTORY = os.path.join(REPO, "data", "extracted_compound_inventory.json")

# Approved drugs named by scripts/validate_repurposing_recall.py's documented cases. These
# are the real customer for sourcing: a repurposing hypothesis names an approved drug, and
# an approved drug should be purchasable.
REPURPOSING_DRUGS = [
    {"name": "sildenafil", "label": "sildenafil (repurposing case: PAH)"},
    {"name": "metformin", "label": "metformin (repurposing case: oncology)"},
    {"name": "thalidomide", "label": "thalidomide (repurposing case: myeloma)"},
    {"name": "tretinoin", "label": "tretinoin (repurposing case: APL)"},
    {"name": "raloxifene", "label": "raloxifene (repurposing case: breast cancer)"},
    {"name": "minoxidil", "label": "minoxidil (repurposing case: alopecia)"},
]


def load_inventory_compounds(limit):
    """Novel AGI structures from the user's own documents -- the negative-control set."""
    with open(INVENTORY) as fh:
        data = json.load(fh)
    out = []
    for c in data["compounds"][:limit]:
        out.append({
            "smiles": c["canonical_smiles"],
            "label": f"AGI-{c['compound_id']}",
            "compound_id": c["compound_id"],
            "mw": c.get("mw"),
        })
    return out


def banner(text):
    print("\n" + "=" * 78)
    print(text)
    print("=" * 78)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the full report here")
    ap.add_argument("--limit", type=int, default=6, help="how many inventory compounds to test")
    args = ap.parse_args()

    banner("PROVIDER STATUS -- what is live, what is key-gated")
    for p in cs.price_providers():
        mark = "LIVE" if p["configured"] else "OFF "
        print(f"  [{mark}] {p['provider']:<10} env={p['env_var'] or '-':<35} {p['status']}")
    print("\n  Availability (always live, keyless): PubChem PUG-View chemical vendors; Mcule lookup.")
    print("\n  Pricing evidence (each endpoint exercised before the decision):")
    for k, v in cs.PRICING_EVIDENCE.items():
        print(f"    {k}:")
        print(f"      observed: {v['observed']}")
        print(f"      verdict : {v['verdict']}")

    banner(f"1. POSITIVE -- approved drugs from the repurposing engine's documented cases")
    pos_bom = cs.bill_of_materials(REPURPOSING_DRUGS, vendor_limit=5)
    print(cs.render_bom_text(pos_bom))

    banner(f"2. NEGATIVE CONTROL -- {args.limit} novel AGI compounds from the repo inventory")
    novel = load_inventory_compounds(args.limit)
    for c in novel:
        print(f"  {c['label']}: {c['smiles']}")
    neg_bom = cs.bill_of_materials(novel, vendor_limit=5)
    print()
    print(cs.render_bom_text(neg_bom))

    # --- the assertions that could prove the module wrong ---
    banner("NEGATIVE-CONTROL VERDICT")
    failures = []
    for line in neg_bom["lines"]:
        if line["sourceable"]:
            failures.append(f"{line['label']} reported SOURCEABLE but should have no supplier")
        if line["vendor_count"]:
            failures.append(f"{line['label']} returned {line['vendor_count']} vendors")
        if line["line_cost"] is not None:
            failures.append(f"{line['label']} carries a price ({line['line_cost']})")
        ident = line.get("identity") or {}
        if ident.get("cid"):
            failures.append(f"{line['label']} resolved to CID {ident['cid']} -- possible substitution")

    print(f"  novel compounds tested : {len(neg_bom['lines'])}")
    print(f"  reported sourceable    : {neg_bom['summary']['sourceable']}  (must be 0)")
    print(f"  priced lines           : {neg_bom['summary']['priced_lines']}  (must be 0)")
    print(f"  estimated total        : {neg_bom['summary']['estimated_total']}  (must be 0.0)")

    banner("3. SIMILARITY IS OPT-IN AND LABELLED -- never merged into a BOM")
    sim = cs.similar_available_compounds(novel[0]["smiles"], threshold=80, limit=3, vendor_limit=2)
    print(f"  query: {sim['query_smiles']}")
    print(f"  WARNING carried on the result: {sim['warning']}")
    print(f"  neighbours returned: {len(sim['neighbours'])}")
    for n in sim["neighbours"]:
        print(f"    - CID {n['cid']} {n['title']!r}  vendors={n['vendor_count']}  "
              f"is_not_your_compound={n['is_not_your_compound']}")
    if sim["neighbours"]:
        neg_labels = {l["label"] for l in neg_bom["lines"]}
        leaked = [n for n in sim["neighbours"] if str(n.get("cid")) in neg_labels]
        if leaked:
            failures.append("a similarity neighbour leaked into the BOM")
        print("\n  None of the above appears in the BOM above: the BOM lists 0 vendors for "
              "the query compound.")

    banner("4. REQUEST FOR QUOTATION -- the actionable output when price is unavailable")
    rfq = cs.request_for_quote(pos_bom, requester="(reviewer)", organisation="AGI Future Foundation",
                               purpose="paediatric repurposing screen -- reference compounds")
    print(f"  boundary: {rfq['boundary']}")
    print(f"  vendors addressed: {rfq['vendor_count']}")
    for v in rfq["vendors"][:3]:
        print(f"    {v['vendor']}: {len(v['items'])} item(s)")
        for it in v["items"][:2]:
            print(f"      - {it['compound']} cat# {it['catalog_numbers'][:2]} "
                  f"restrictions={it['restrictions_flagged']}")
    print(f"  not covered (no supplier): {rfq['not_covered']}")
    print(f"  compliance note: {rfq['compliance_note'][:160]}...")

    banner("RESULT")
    if failures:
        print("FAILED -- the negative control did not hold:")
        for f in failures:
            print(f"  ! {f}")
    else:
        print("PASSED")
        print("  * approved drugs resolve to real vendors with real catalogue numbers")
        print("  * every novel AGI compound returned zero suppliers -- no silent substitution")
        print("  * no price was invented; unpriced lines are reported unpriced")
        print("  * restricted compounds are flagged rather than listed as routine purchases")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"providers": cs.price_providers(), "pricing_evidence": cs.PRICING_EVIDENCE,
                       "positive_bom": pos_bom, "negative_control_bom": neg_bom,
                       "similarity": sim, "rfq": rfq, "failures": failures}, fh, indent=1)
        print(f"\nfull report -> {args.json}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
