"""Where screening money goes, and the cheapest order to spend it in.

Most of the cost of a screening campaign is spent on compounds that were never
going to work, and the order the work is done in decides how much of that is
avoidable. Three effects dominate, and only one of them is about chemistry:

  duplication   the same structure tested twice under two identifiers. Free to
                remove and worth more than any other single step here: the
                user's own extracted inventory carries 1,336 unique structures
                across 5,450 occurrences, so testing by identifier would pay
                four times over for one library.

  ordering      a filter that costs nothing should run before one that costs
                thousands. Reordering changes no science and no result; it only
                changes what the expensive stages are asked to look at.

  precedent     a compound with an approved clinical record arrives with
                toxicology and pharmacokinetics already done. That is the real
                economic argument for repurposing, and it is a saving in
                elapsed years rather than in assay fees.

This module estimates avoided spend, which is not a budget. It takes no assay
price by default and will not borrow one: the figures in validation_cost are
funding thresholds from a single protocol, not bulk screening rates, and using
them as per-compound costs inflates every total downstream. Supply your own
quotes through `unit_costs`, or read the structural result -- the redundancy
fraction and the shape of the cascade -- which holds whatever the prices are.
"""
from typing import Dict, Iterable, List, Optional

# Attrition assumptions are the weakest part of any such model, so they are
# named, defaulted conservatively, and overridable rather than buried.
DEFAULT_SURVIVAL = {
    "descriptor_filter": 0.95,  # drug-like libraries lose little here
    "docking": 0.30,            # ranking keeps roughly the top third
    "worm": 0.10,               # lifespan hits are rare
    "fly": 0.50,                # of worm hits, replication in a second organism
    "mouse": 0.30,              # the step where most longevity findings fail
}


def _stage_costs(unit_costs: Optional[Dict[str, int]] = None) -> Dict[str, Optional[int]]:
    """Cash cost per compound per stage. None means free or not priced.

    Only the two computational stages are free and known. Everything else must
    be supplied, because no per-compound assay price is available to this
    codebase and borrowing one would be wrong in a specific way worth naming:
    validation_cost carries funding *thresholds* from one protocol, which unlock
    a stage for a single compound inside that model. They are not bulk screening
    prices. Ora screens on the order of ten thousand compounds, which will not
    cost what one tokenised experiment costs, and treating a threshold as a unit
    price inflates every total that follows.
    """
    return {"descriptor_filter": 0, "docking": 0, **(unit_costs or {})}


def deduplicate(compounds: Iterable[Dict]) -> Dict:
    """Collapse to unique structures. The cheapest saving available."""
    by_structure: Dict[str, List[Dict]] = {}
    total = 0

    for compound in compounds:
        total += 1
        key = compound.get("canonical_smiles") or compound.get("smiles")
        if key:
            by_structure.setdefault(key, []).append(compound)

    unique = len(by_structure)
    return {
        "submitted": total,
        "unique": unique,
        "redundant": total - unique,
        "redundancy_fraction": round((total - unique) / total, 4) if total else 0.0,
        "duplicate_groups": {k: len(v) for k, v in by_structure.items() if len(v) > 1},
    }


def cascade(n_compounds: int, stages: Optional[List[str]] = None,
            survival: Optional[Dict[str, float]] = None,
            unit_costs: Optional[Dict[str, int]] = None) -> Dict:
    """Cost of running `n_compounds` through stages, cheapest first.

    Compares against running every compound through every stage, which is what
    a campaign costs when it is not staged at all.
    """
    order = stages or ["descriptor_filter", "docking", "worm", "fly", "mouse"]
    rates = {**DEFAULT_SURVIVAL, **(survival or {})}
    costs = _stage_costs(unit_costs)

    steps, remaining, staged_total, unpriced = [], n_compounds, 0, []

    for stage in order:
        unit = costs.get(stage)
        entering = remaining
        if unit is None:
            unpriced.append(stage)
            spend = None
        else:
            spend = entering * unit
            staged_total += spend

        remaining = round(entering * rates.get(stage, 1.0))
        steps.append({
            "stage": stage,
            "entering": entering,
            "unit_cost_usd": unit,
            "stage_cost_usd": spend,
            "survival_rate": rates.get(stage, 1.0),
            "surviving": remaining,
        })

    # The unstaged comparison: everything through everything.
    unstaged = sum(n_compounds * (costs.get(s) or 0) for s in order)

    return {
        "compounds": n_compounds,
        "steps": steps,
        "staged_cost_usd": staged_total,
        "unstaged_cost_usd": unstaged,
        "avoided_usd": unstaged - staged_total,
        "survivors": remaining,
        "unpriced_stages": unpriced,
        "caveat": "Estimated avoided spend under stated survival assumptions, not "
                  "a budget. Survival rates are assumptions and are the weakest "
                  "input; override them with your own attrition data.",
    }


def analyse(compounds: List[Dict], stages: Optional[List[str]] = None,
            survival: Optional[Dict[str, float]] = None,
            unit_costs: Optional[Dict[str, int]] = None) -> Dict:
    """Deduplicate, then cost the cascade on what is actually left."""
    dedup = deduplicate(compounds)
    plan = cascade(dedup["unique"], stages, survival, unit_costs)
    naive = cascade(dedup["submitted"], stages, survival, unit_costs)

    return {
        "deduplication": dedup,
        "cascade": plan,
        "duplication_cost_usd": naive["staged_cost_usd"] - plan["staged_cost_usd"],
        "total_avoided_usd": (naive["unstaged_cost_usd"] - plan["staged_cost_usd"]),
        "recommendations": _recommend(dedup, plan),
    }


def _recommend(dedup: Dict, plan: Dict) -> List[str]:
    out = []

    if dedup["redundancy_fraction"] > 0.1:
        out.append(
            f"{dedup['redundancy_fraction']:.0%} of submitted compounds are repeats of a "
            f"structure already in the set. Canonicalise before ordering anything: this "
            f"is free and is the largest single saving available.")

    priced = [s for s in plan["steps"] if s["stage_cost_usd"]]
    if priced:
        worst = max(priced, key=lambda s: s["stage_cost_usd"])
        out.append(
            f"{worst['stage']} dominates the spend at ${worst['stage_cost_usd']:,}. "
            f"Anything that reduces what reaches it is worth more than a discount on it.")

    if plan["unpriced_stages"]:
        out.append(
            f"No cash price is recorded for: {', '.join(plan['unpriced_stages'])}. "
            f"Those stages are excluded from the totals rather than estimated.")

    out.append(
        "A compound with an approved clinical record already has toxicology and "
        "pharmacokinetics. Where a repurposing candidate and a novel compound are "
        "otherwise comparable, the saving is in years rather than in assay fees.")
    return out
