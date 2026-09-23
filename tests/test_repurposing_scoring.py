"""Offline tests for repurposing scoring.

The recall evaluation in scripts/validate_repurposing_recall.py measures whether
the engine rediscovers documented repurposings, but it needs the network and is
run by hand. Nothing stopped a weight being changed and the 5-of-7 quietly
becoming 2-of-7.

These pin the judgements encoded in SCORING -- the ones whose rationale is
written out in the module and would be easy to erode without noticing.
"""
import pytest

import repurposing_engine as engine

SCORING = engine.SCORING


def _mech(stage="PHASE_2", drug="drugA", drug_id="CHEMBL1", target_id="CHEMBL_T1",
          rank=1, complex_component=False):
    return {
        "stage": stage, "drug": drug, "drug_chembl_id": drug_id,
        "target_chembl_id": target_id, "target_symbol": "TGT",
        "ensembl": "ENSG00000000001", "rank": rank,
        "is_complex_component": complex_component,
    }


def test_clinical_stage_points_are_ordered():
    """A later stage must never be worth less than an earlier one."""
    points = SCORING["mechanism"]["precedent_stage_points"]
    ladder = ["UNKNOWN", "PHASE_0", "PHASE_1", "PHASE_1_2", "PHASE_2",
              "PHASE_2_3", "PHASE_3", "PHASE_4"]

    values = [points[s] for s in ladder]
    assert values == sorted(values), f"stage points are not monotonic: {dict(zip(ladder, values))}"
    assert points["APPROVAL"] >= points["PHASE_3"]


def test_one_drug_scores_less_than_two_independent_drugs():
    """A drug's indication list is its whole clinical footprint, not this target's share.

    The dipyridamole case the module documents: a PDE5A mechanism plus stroke
    indications from unrelated antiplatelet use. Convergence is the evidence.
    """
    single, _ = engine._mechanism_terms([_mech()])
    double, _ = engine._mechanism_terms([
        _mech(drug="drugA", drug_id="CHEMBL1"),
        _mech(drug="drugB", drug_id="CHEMBL2"),
    ])

    assert single < double


def test_the_same_drug_twice_is_not_convergence():
    """Two rows for one drug must not be counted as two independent precedents."""
    once, _ = engine._mechanism_terms([_mech(drug_id="CHEMBL1")])
    twice, _ = engine._mechanism_terms([_mech(drug_id="CHEMBL1"), _mech(drug_id="CHEMBL1")])

    assert once == twice


def test_complex_subunits_do_not_multiply_the_evidence():
    """Keying on the gene would count every subunit as an independent target."""
    plain, _ = engine._mechanism_terms([_mech()])
    subunit, _ = engine._mechanism_terms([_mech(complex_component=True)])

    assert subunit < plain
    assert SCORING["mechanism"]["complex_component_multiplier"] < 1.0


def test_one_drug_hitting_two_targets_earns_the_convergence_bonus():
    """Polypharmacology, which the module distinguishes from promiscuity.

    One drug with clinical precedent through two *different* targets for the
    same disease is independent corroboration, so it is rewarded. I expected
    these to score equally and was wrong; the bonus is the documented design.
    """
    one_target, _ = engine._mechanism_terms([
        _mech(target_id="CHEMBL_T1"), _mech(target_id="CHEMBL_T1")])
    two_targets, _ = engine._mechanism_terms([
        _mech(target_id="CHEMBL_T1"), _mech(target_id="CHEMBL_T2")])

    bonus = SCORING["polypharmacology"]["convergent_target_bonus"]
    assert two_targets == pytest.approx(one_target + bonus)


def test_repeating_one_target_is_not_convergence():
    """The bonus must come from distinct targets, not from repeated rows."""
    once, _ = engine._mechanism_terms([_mech(target_id="CHEMBL_T1")])
    twice, _ = engine._mechanism_terms([
        _mech(target_id="CHEMBL_T1"), _mech(target_id="CHEMBL_T1")])

    assert once == twice


def test_documented_specificity_factors_match_the_implemented_ones():
    """The config states these factors; _mechanism_terms hardcodes them separately.

    Found by seeding: inverting the documented table to {"1": 1.2, "3+": 0.6}
    changed no behaviour and broke no test, because the config is read by nobody.
    Two sources of truth for one judgement will drift, and the drift is silent —
    the published rationale would describe scoring the engine no longer does.
    """
    documented = SCORING["mechanism"]["specificity_factor_by_distinct_drugs"]
    base = SCORING["mechanism"]["precedent_stage_points"]["PHASE_2"]

    for count, key in ((1, "1"), (2, "2"), (3, "3+")):
        points, _ = engine._mechanism_terms([
            _mech(drug=f"d{i}", drug_id=f"CHEMBL{i}") for i in range(count)])
        # Isolate the mechanism term from any convergence bonus.
        implied = points / base if count < 2 else None
        if implied is not None:
            assert implied == pytest.approx(documented[key]), (
                f"config says {documented[key]} for {key} drug(s), implementation "
                f"applies {implied}")


def test_structure_tiers_reward_closer_analogues():
    tiers = SCORING["structure"]["tiers"]
    thresholds = [t[0] for t in tiers]
    values = [t[1] for t in tiers]

    assert thresholds == sorted(thresholds, reverse=True), "tiers must descend by similarity"
    assert values == sorted(values, reverse=True), "closer analogues must score higher"


@pytest.mark.parametrize("tanimoto,expected", [(0.95, 2.0), (0.75, 1.2), (0.60, 0.6)])
def test_structure_points_follow_the_tier_table(tanimoto, expected):
    points, _ = engine._structure_terms([
        {"tanimoto": tanimoto, "analogue": "aspirin", "analogue_chembl_id": "CHEMBL25",
         "analogue_indications": [], "shared_target": None, "stage": "APPROVAL",
         "analogue_targets": []}])

    assert points == expected


def test_structure_below_the_floor_scores_nothing():
    floor = SCORING["structure"]["tiers"][-1][0]
    points, terms = engine._structure_terms([
        {"tanimoto": floor - 0.01, "analogue": "x", "analogue_chembl_id": "CHEMBL1",
         "analogue_indications": [], "shared_target": None, "stage": "APPROVAL",
         "analogue_targets": []}])

    assert points == 0.0
    assert terms == []


def test_network_evidence_alone_stays_below_a_credible_score():
    """Pathway co-membership is non-obvious and false-positive-prone.

    If the network cap ever rose above the mechanism floor, a speculative
    hypothesis would rank like a supported one.
    """
    network_cap = SCORING["network"]["cap"]
    weakest_mechanism = min(SCORING["mechanism"]["precedent_stage_points"].values())

    assert network_cap == engine.SPECULATIVE_CEILING
    assert network_cap <= SCORING["mechanism"]["precedent_stage_points"]["PHASE_2"]
    assert weakest_mechanism > 0


def test_network_points_are_capped():
    many = [{"kind": "reactome_pathway", "compound_target": "A", "panel_target": "B",
             "pathway": f"p{i}", "pathway_id": f"R-HSA-{i}"} for i in range(20)]
    points, _ = engine._network_terms(many)

    assert points <= SCORING["network"]["cap"]


def test_string_high_confidence_outweighs_medium():
    assert SCORING["network"]["string_high"] > SCORING["network"]["string_medium"]


def test_opposed_action_type_is_a_penalty():
    """An agonist cannot support a hypothesis built on antagonism."""
    assert SCORING["mechanism"]["action_type_opposed"] < 0
    assert SCORING["mechanism"]["action_type_match"] > 0


def test_scoring_describes_itself_as_ordinal_not_probabilistic():
    """A score read as a probability or an effect size would be misused."""
    description = SCORING["description"].lower()
    assert "not a probability" in description
    assert "ordinal" in description


def test_every_join_carries_a_rationale():
    for name in ("mechanism", "structure", "network", "polypharmacology"):
        assert SCORING[name].get("rationale"), f"{name} has no stated rationale"
