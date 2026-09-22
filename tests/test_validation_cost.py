"""Contract tests for validation-stage costing.

The risk in this module is not arithmetic, it is drift: a published price
quietly becoming an estimate, or a crypto amount silently converted to dollars.
The tests pin provenance as much as numbers.
"""
import pytest

import longevity_panel as lv
import validation_cost as vc


def test_every_stage_names_its_provider_and_source():
    """A cost with no attributable origin is the failure mode to prevent."""
    for stage in vc.stages():
        assert stage["provider"], f"{stage['stage']} has no provider"
        assert stage["cost"], f"{stage['stage']} has no cost"
    assert vc.SOURCE.startswith("https://")
    assert vc.READ_ON


def test_crypto_cost_is_never_converted_to_dollars():
    """A SOL figure would be wrong within the hour; it stays denominated."""
    worm = next(s for s in vc.stages() if s["stage"] == "worm")
    assert worm["cost_is_crypto"] is True
    assert "SOL" in worm["cost"]
    assert "$" not in worm["cost"]

    plan = vc.plan("no-therapeutic")
    assert worm["cost"] in plan["crypto_costs"]
    # The crypto stage must not have leaked into the cash subtotal.
    assert plan["cash_subtotal_usd"] == 1500 + 7000


def test_cash_subtotal_sums_only_the_selected_stages():
    assert vc.plan("model-organism-only")["cash_subtotal_usd"] == 25000
    assert vc.plan("human-rct")["cash_subtotal_usd"] == 0


@pytest.mark.parametrize("evidence_class", sorted(vc._NEXT))
def test_every_evidence_class_in_the_panel_is_plannable(evidence_class):
    plan = vc.plan(evidence_class)
    assert "error" not in plan
    assert plan["rationale"]


def test_panel_evidence_classes_are_all_covered():
    """A new class in the panel must not silently fall through to 'unknown'."""
    used = {e.get("evidence_class") for e in lv.LONGEVITY_EVIDENCE.values()}
    assert used <= set(vc._NEXT), f"panel uses classes this module cannot plan: {used - set(vc._NEXT)}"


def test_strong_evidence_buys_nothing_further():
    """These stages cannot produce randomised evidence, so they stop."""
    for strong in ("human-rct", "approved-for-this-indication"):
        assert vc.plan(strong)["stages"] == []


def test_human_stage_does_not_claim_to_buy_randomised_evidence():
    human = next(s for s in vc.stages() if s["stage"] == "human")
    assert human["buys"] == "human-uncontrolled"
    assert human["buys"] != "human-rct"


def test_unknown_evidence_class_reports_rather_than_guessing():
    out = vc.plan("not-a-real-class")
    assert "error" in out
    assert out["known"]


def test_plan_for_target_resolves_a_real_panel_symbol():
    out = vc.plan_for_target("LMNA")
    assert out and out["symbol"] == "LMNA"
    assert out["arm"]
    assert out["stages"], "LMNA has no therapeutic, so stages should be proposed"


def test_plan_for_unknown_symbol_returns_none():
    assert vc.plan_for_target("NOT_A_GENE") is None


def test_every_plan_carries_its_caveat():
    """List price for a stage is not a quote for a compound."""
    for evidence_class in vc._NEXT:
        assert "quote" in vc.plan(evidence_class)["caveat"]
