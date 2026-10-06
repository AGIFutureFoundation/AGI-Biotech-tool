"""Contract tests for screening economics.

The danger in a cost model is a confident total resting on a borrowed number.
These tests pin that prices must be supplied, never inferred.
"""
import pytest

import screening_economics as se


def _compounds(smiles_list):
    return [{"canonical_smiles": s} for s in smiles_list]


def test_no_price_is_invented_when_none_is_given():
    """The whole point: an unpriced stage stays unpriced."""
    plan = se.cascade(100)

    assert plan["staged_cost_usd"] == 0
    assert set(plan["unpriced_stages"]) == {"worm", "fly", "mouse"}
    assert all(s["stage_cost_usd"] is None
               for s in plan["steps"] if s["stage"] in plan["unpriced_stages"])


def test_validation_cost_thresholds_are_not_borrowed_as_unit_prices():
    """A funding threshold is not a bulk screening rate; conflating them inflates totals."""
    import validation_cost as vc

    thresholds = {s["stage"]: s.get("threshold") for s in vc.stages()}
    assert thresholds["mouse"] == "$7,000"

    plan = se.cascade(10)
    mouse = next(s for s in plan["steps"] if s["stage"] == "mouse")
    assert mouse["unit_cost_usd"] is None, "mouse must not inherit the $7,000 threshold"


def test_supplied_prices_are_used():
    plan = se.cascade(100, unit_costs={"worm": 25})
    worm = next(s for s in plan["steps"] if s["stage"] == "worm")

    assert worm["unit_cost_usd"] == 25
    assert worm["stage_cost_usd"] == worm["entering"] * 25


def test_computational_stages_are_free_and_known():
    plan = se.cascade(50)
    for name in ("descriptor_filter", "docking"):
        step = next(s for s in plan["steps"] if s["stage"] == name)
        assert step["unit_cost_usd"] == 0
        assert name not in plan["unpriced_stages"]


def test_duplicates_collapse_by_structure_not_identifier():
    dedup = se.deduplicate(_compounds(["CCO", "CCO", "CCO", "c1ccccc1"]))

    assert dedup["submitted"] == 4
    assert dedup["unique"] == 2
    assert dedup["redundancy_fraction"] == 0.5


def test_no_duplicates_reports_zero_redundancy():
    dedup = se.deduplicate(_compounds(["CCO", "c1ccccc1", "CCN"]))

    assert dedup["redundant"] == 0
    assert dedup["duplicate_groups"] == {}


def test_empty_input_does_not_divide_by_zero():
    assert se.deduplicate([])["redundancy_fraction"] == 0.0


def test_staging_costs_less_than_running_everything_everywhere():
    plan = se.cascade(1000, unit_costs={"worm": 25, "fly": 300, "mouse": 7000})

    assert plan["staged_cost_usd"] < plan["unstaged_cost_usd"]
    assert plan["avoided_usd"] == plan["unstaged_cost_usd"] - plan["staged_cost_usd"]


def test_survival_assumptions_are_overridable():
    """They are the weakest input, so they must not be buried."""
    strict = se.cascade(1000, survival={"docking": 0.01},
                        unit_costs={"worm": 25, "fly": 300, "mouse": 7000})
    loose = se.cascade(1000, survival={"docking": 0.90},
                       unit_costs={"worm": 25, "fly": 300, "mouse": 7000})

    assert strict["staged_cost_usd"] < loose["staged_cost_usd"]


def test_analyse_separates_deduplication_saving_from_ordering_saving():
    compounds = _compounds(["CCO"] * 10 + ["c1ccccc1"] * 10)
    out = se.analyse(compounds, unit_costs={"worm": 25, "fly": 300, "mouse": 7000})

    assert out["deduplication"]["unique"] == 2
    assert out["duplication_cost_usd"] > 0


def test_recommendations_flag_high_redundancy():
    out = se.analyse(_compounds(["CCO"] * 9 + ["CCN"]))
    assert any("repeats of a structure" in r for r in out["recommendations"])


def test_every_plan_carries_its_caveat():
    assert "not " in se.cascade(10)["caveat"].lower()
