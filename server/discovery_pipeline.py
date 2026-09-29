"""Target-first discovery: from a verified target to candidates you can act on.

Every piece this needs already existed and none of them were connected, so a
researcher had to drive four modules by hand and join the results themselves.
Starting from a target rather than a compound matches how the work actually
begins -- you have a disease and a protein, not a molecule.

One pass over a panel target gives:

  evidence      the panel's own record, every identifier of which has been
                re-resolved against live databases by verify_panel_citations.py
  precedent     drugs already acting on the target, taken from that verified
                record rather than re-queried, so the chain stays checkable
  repurposing   for each precedent drug, where else its targets point, with the
                drug's own record excluded so nothing predicts its own label
  sourcing      whether a candidate can actually be bought, by exact identity
  cost          what the next experiment costs, from the target's evidence class

Nothing here scores a molecule or invents a number. It joins verified records
and reports what is missing as missing -- a target with no precedent drug yields
no hypotheses, which is the honest answer rather than a weaker one dressed up.
"""
from typing import Dict, List, Optional


def _panels():
    """Every panel's evidence map, across the modules that define them."""
    import disease_panels as dp

    found = {}
    for name in dp.list_panels():
        evidence = getattr(dp, f"{name.upper()}_EVIDENCE", {})
        for symbol, record in evidence.items():
            found[symbol] = (name, record)

    try:
        import longevity_panel as lv
    except ImportError:
        return found

    for symbol, record in lv.LONGEVITY_EVIDENCE.items():
        found.setdefault(symbol, ("Longevity", record))
    return found


def targets() -> List[Dict]:
    """Every target available to investigate, with its panel and precedent count."""
    return sorted(
        (
            {
                "symbol": symbol,
                "panel": panel,
                "uniprot": record.get("uniprot"),
                "precedent_drugs": len(record.get("drugs") or []),
                "indication": record.get("indication"),
            }
            for symbol, (panel, record) in _panels().items()
        ),
        key=lambda t: (t["panel"], t["symbol"]),
    )


def investigate(symbol: str, max_drugs: int = 3, hypotheses_per_drug: int = 10,
                source_top: int = 3, include_sourcing: bool = True) -> Dict:
    """Run the pipeline for one target. Network-bound; results are cached."""
    panels = _panels()
    if symbol not in panels:
        return {"error": f"no panel target named {symbol!r}",
                "available": [t["symbol"] for t in targets()]}

    panel, evidence = panels[symbol]
    report = {
        "symbol": symbol,
        "panel": panel,
        "uniprot": evidence.get("uniprot"),
        "indication": evidence.get("indication"),
        "unmet_need": evidence.get("unmet_need"),
        "tractability": evidence.get("tractability"),
        "structures": len(evidence.get("pdb_ids") or []),
        "chembl_target": evidence.get("chembl_target"),
        "precedent_drugs": list(evidence.get("drugs") or []),
        "repurposing": [],
        "sourcing": [],
        "next_experiment": None,
        "notes": [],
    }

    if not report["precedent_drugs"]:
        report["notes"].append(
            "No drug in the verified record acts on this target, so there is no "
            "precedent to transfer and no repurposing hypothesis can be formed. "
            "That is a statement about available evidence, not about the target.")

    report["next_experiment"] = _next_experiment(symbol, evidence, report["notes"])
    _add_repurposing(report, max_drugs, hypotheses_per_drug)

    if include_sourcing:
        _add_sourcing(report, source_top)

    return report


def _next_experiment(symbol: str, evidence: Dict, notes: List[str]) -> Optional[Dict]:
    try:
        import validation_cost as vc
    except ImportError:
        return None

    if "evidence_class" not in evidence:
        notes.append(
            "Validation costing applies to the longevity track, which classifies "
            "targets by evidence strength. This panel does not carry that field.")
        return None
    return vc.plan(evidence["evidence_class"])


def _add_repurposing(report: Dict, max_drugs: int, limit: int) -> None:
    try:
        import repurposing_engine as engine
    except ImportError:
        report["notes"].append("repurposing_engine unavailable")
        return

    for drug in report["precedent_drugs"][:max_drugs]:
        try:
            result = engine.generate_hypotheses(
                chembl_id=drug.get("chembl_id"), name=drug.get("name"),
                label=drug.get("name"), limit=limit)
        except Exception as exc:  # a dead upstream must not lose the rest
            report["notes"].append(f"repurposing failed for {drug.get('name')}: {exc}")
            continue

        report["repurposing"].append({
            "drug": drug.get("name"),
            "chembl_id": drug.get("chembl_id"),
            "hypotheses": (result or {}).get("hypotheses", [])[:limit],
        })


def _add_sourcing(report: Dict, top: int) -> None:
    try:
        import compound_sourcing as sourcing
    except ImportError:
        report["notes"].append("compound_sourcing unavailable")
        return

    for drug in report["precedent_drugs"][:top]:
        try:
            # Exact identity only. source_compound never substitutes a similar
            # molecule, which would be a serious defect in something a lab orders from.
            report["sourcing"].append(
                sourcing.source_compound(name=drug.get("name"), label=drug.get("name"),
                                         price=False))
        except Exception as exc:
            report["notes"].append(f"sourcing failed for {drug.get('name')}: {exc}")


def summarise(report: Dict) -> str:
    """One-screen summary. Absent evidence is stated, never filled in."""
    if "error" in report:
        return report["error"]

    lines = [
        f"{report['symbol']}  ({report['panel']})",
        f"  indication   : {report.get('indication') or 'not recorded'}",
        f"  unmet need   : {(report.get('unmet_need') or 'not recorded')[:88]}",
        f"  structures   : {report['structures']} PDB entries",
        f"  precedent    : {', '.join(d['name'] for d in report['precedent_drugs']) or 'none'}",
    ]

    for block in report["repurposing"]:
        top = block["hypotheses"][:3]
        # Carry the score and status: a hypothesis with no confidence attached
        # reads as a finding, which it is not.
        named = ", ".join(
            f"{h.get('disease', '?')} ({h.get('score', '?')}, {h.get('status', '?')})"
            for h in top)
        lines.append(f"  repurposing from {block['drug']}: {named or 'none found'}")

    for record in report["sourcing"]:
        vendors = len(record.get("vendors") or [])
        lines.append(f"  sourcing {record.get('label', '?')}: "
                     + (f"{vendors} vendors" if record.get("sourceable") else "not sourceable"))

    nxt = report.get("next_experiment")
    if nxt and nxt.get("stages"):
        stages = ", ".join(s["stage"] for s in nxt["stages"])
        lines.append(f"  next         : {stages} (${nxt['cash_subtotal_usd']:,}"
                     + (f" + {nxt['crypto_costs'][0]}" if nxt.get("crypto_costs") else "") + ")")

    lines.extend(f"  note         : {n}" for n in report["notes"])
    return "\n".join(lines)
