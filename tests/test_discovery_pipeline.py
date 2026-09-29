"""Contract tests for the target-first discovery pipeline.

These avoid the network: what is worth pinning is that the pipeline joins
verified records honestly and reports absence as absence, not whether an
external service answered today.
"""
import pytest

import discovery_pipeline as pipeline


def test_targets_span_every_panel():
    found = pipeline.targets()
    panels = {t["panel"] for t in found}

    assert {"ALS", "Parkinsons", "Shriners", "StJude", "Longevity"} <= panels
    assert len(found) > 80


def test_every_target_carries_its_panel_and_accession():
    for target in pipeline.targets():
        assert target["panel"]
        assert target["symbol"]
        assert target["uniprot"], f"{target['symbol']} has no UniProt accession"


def test_unknown_symbol_reports_rather_than_guessing():
    out = pipeline.investigate("NOT_A_GENE", include_sourcing=False)

    assert "error" in out
    assert out["available"]
    assert "repurposing" not in out


def test_target_without_precedent_explains_why_no_hypotheses(monkeypatch):
    """LMNA is the causal protein in progeria and nothing targets it directly.

    The honest output is no hypotheses plus the reason, rather than a weaker
    hypothesis dressed up to fill the field.
    """
    out = pipeline.investigate("LMNA", max_drugs=0, include_sourcing=False)

    assert out["precedent_drugs"] == []
    assert out["repurposing"] == []
    assert any("no precedent to transfer" in n for n in out["notes"])


def test_longevity_target_gets_a_costed_next_experiment():
    out = pipeline.investigate("LMNA", max_drugs=0, include_sourcing=False)
    plan = out["next_experiment"]

    assert plan is not None
    assert [s["stage"] for s in plan["stages"]] == ["worm", "fly", "mouse"]
    assert plan["cash_subtotal_usd"] == 8500
    assert plan["crypto_costs"] == ["3 SOL"]


def test_non_longevity_panel_says_why_costing_is_absent():
    """Silence would read as 'no cost'; the reason is the useful part."""
    out = pipeline.investigate("MEN1", max_drugs=0, include_sourcing=False)

    assert out["next_experiment"] is None
    assert any("evidence strength" in n for n in out["notes"])


def test_precedent_drugs_come_from_the_verified_record():
    """Re-querying would break the chain back to verify_panel_citations.py."""
    out = pipeline.investigate("MEN1", max_drugs=0, include_sourcing=False)

    names = [d["name"] for d in out["precedent_drugs"]]
    assert "revumenib" in names
    assert all(d.get("chembl_id") for d in out["precedent_drugs"])


def test_summary_of_an_error_is_the_error():
    assert pipeline.summarise({"error": "nope"}) == "nope"


def test_summary_states_absent_evidence_rather_than_omitting_it():
    out = pipeline.investigate("LMNA", max_drugs=0, include_sourcing=False)
    text = pipeline.summarise(out)

    assert "precedent    : none" in text
    assert "note" in text


def test_a_failing_upstream_does_not_lose_the_rest_of_the_report(monkeypatch):
    """One dead service must degrade that section, not the whole investigation."""
    import repurposing_engine

    def boom(*a, **kw):
        raise RuntimeError("upstream down")

    monkeypatch.setattr(repurposing_engine, "generate_hypotheses", boom)
    out = pipeline.investigate("BCL2L1", max_drugs=1, include_sourcing=False)

    assert out["symbol"] == "BCL2L1"
    assert out["precedent_drugs"], "evidence should survive a repurposing failure"
    assert any("repurposing failed" in n for n in out["notes"])
