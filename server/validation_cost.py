"""What it would cost to move a longevity target to the next level of evidence.

The longevity panel classifies every target by how strong its evidence actually
is -- model-organism-only, human-uncontrolled, human-rct, and so on. The obvious
next question is what the next step costs, and that had no answer here because
the platform models molecules and not experiments.

The figures below are published prices from pump.science's documentation, which
routes each stage to a named contract research organisation. They are quoted as
published, with the stage they buy and who runs it, and nothing is interpolated
between them or adjusted for a particular compound. A real quote comes from the
lab, not from here.

The worm figure is denominated in SOL and is deliberately not converted: a
dollar equivalent would be wrong within the hour and inventing one would be the
same failure as the fabricated metrics this codebase has spent its history
removing.

Source: https://pumpscience.gitbook.io/pump.science, read 2026-09-22.
"""
from typing import Dict, List, Optional

SOURCE = "https://pumpscience.gitbook.io/pump.science"
READ_ON = "2026-09-22"

# Ordered weakest to strongest. `buys` is the evidence_class a stage can move a
# target toward, not a promise that it will.
STAGES = (
    {
        "stage": "worm",
        "organism": "C. elegans",
        "measures": "lifespan",
        "cost": "3 SOL",
        "cost_is_crypto": True,
        "provider": "Ora Biomedical",
        "buys": "model-organism-only",
        "note": "Ora states ~10,000 compounds screened and ~1,000,000 C. elegans "
                "observations on one platform under one protocol. That uniformity is "
                "the useful part: lifespan assays vary enormously with temperature, "
                "diet and strain, so single-protocol data is more comparable than "
                "most of the published literature.",
    },
    {
        "stage": "fly",
        "organism": "Drosophila",
        "measures": "longevity",
        "cost": "$1,500",
        "cost_is_crypto": False,
        "provider": "Juvion Health Sciences",
        "buys": "model-organism-only",
        "note": "A second invertebrate model. Agreement between worm and fly is "
                "worth more than either alone, since it argues against an artefact "
                "of one organism's biology.",
    },
    {
        "stage": "mouse",
        "organism": "Mus musculus",
        "measures": "longevity",
        "cost": "$7,000",
        "cost_is_crypto": False,
        "provider": "VivoArchitect",
        "buys": "model-organism-only",
        "note": "The step where most longevity findings fail. Nearly all the "
                "senolytic and NAD+ lifespan evidence in the panel lives in mice "
                "and has not transferred to humans.",
    },
    {
        "stage": "human",
        "organism": "Homo sapiens",
        "measures": "wearable-derived endpoints",
        "cost": "$25,000",
        "cost_is_crypto": False,
        "provider": "Reputable Health",
        "buys": "human-uncontrolled",
        "note": "Decentralised and wearable-based, so it does not buy randomised "
                "evidence. It cannot move a target to human-rct.",
    },
)

# Which stages are worth running given what is already known.
_NEXT = {
    "no-therapeutic": ["worm", "fly", "mouse"],
    "model-organism-only": ["human"],
    "human-uncontrolled": [],
    "human-rct": [],
    "approved-for-this-indication": [],
}


def stages() -> List[Dict]:
    return [dict(s) for s in STAGES]


def plan(evidence_class: str) -> Dict:
    """Stages worth running for a target at this evidence level, with costs."""
    if evidence_class not in _NEXT:
        return {"error": f"unknown evidence class {evidence_class!r}",
                "known": sorted(_NEXT)}

    wanted = _NEXT[evidence_class]
    chosen = [dict(s) for s in STAGES if s["stage"] in wanted]

    cash = sum(int(s["cost"].lstrip("$").replace(",", ""))
               for s in chosen if not s["cost_is_crypto"])
    crypto = [s["cost"] for s in chosen if s["cost_is_crypto"]]

    if not chosen:
        rationale = ("Already at or above the strongest evidence these stages can "
                     "buy. Anything further is a randomised trial, which is not "
                     "priced here.")
    else:
        rationale = f"From {evidence_class}, the next useful evidence comes from: " \
                    + ", ".join(s["stage"] for s in chosen)

    return {
        "evidence_class": evidence_class,
        "stages": chosen,
        "cash_subtotal_usd": cash,
        "crypto_costs": crypto,  # kept separate; not converted
        "rationale": rationale,
        "source": SOURCE,
        "read_on": READ_ON,
        "caveat": "Published list prices for the stage, not a quote for a specific "
                  "compound. Synthesis, shipping, controls, replication and analysis "
                  "are not included, and a lab will price the actual work itself.",
    }


def plan_for_target(symbol: str) -> Optional[Dict]:
    """Cost the next step for a symbol in the longevity panel."""
    try:
        import longevity_panel as lv
    except ImportError:
        return None

    evidence = lv.LONGEVITY_EVIDENCE.get(symbol)
    if not evidence:
        return None

    out = plan(evidence.get("evidence_class", ""))
    out["symbol"] = symbol
    out["arm"] = evidence.get("arm")
    out["indication"] = evidence.get("indication")
    return out
