"""Priority 2: invariants for server/pyrene_apoptotic_discovery.py.

Compound generation is the kind of code where a wrong number is far more
expensive than a crash: nothing raises, a plausible-looking score comes out, and
it is wrong all the way to the bench. These tests pin the invariants that the
dataclass field comments and the method docstrings promise.
"""
import math

import pytest

from pyrene_apoptotic_discovery import (
    ApoptosisType,
    PyreneCompound,
    PyreneSeries3Generator,
    WarheadType,
)

# The mapping documented in _select_mechanism.
DOCUMENTED_MECHANISM_MAP = {
    "BCL2": ApoptosisType.INTRINSIC,
    "BCL-xL": ApoptosisType.INTRINSIC,
    "FAS": ApoptosisType.EXTRINSIC,
    "TNFR1": ApoptosisType.EXTRINSIC,
    "XIAP": ApoptosisType.ANTI_APOPTOTIC,
    "survivin": ApoptosisType.ANTI_APOPTOTIC,
    "caspase-3": ApoptosisType.HYBRID,
}

# The mapping documented in _select_warhead_for_target.
DOCUMENTED_WARHEAD_MAP = {
    "BCL2": ["acrylamide", "vinylsulfonamide"],
    "FAS": ["hydroxamate", "cyanoketone"],
    "XIAP": ["acrylamide", "amide"],
    "caspase-3": ["cyanoketone", "vinylsulfonamide"],
}

TARGETS = ["BCL2", "FAS", "XIAP", "caspase-3", "SOMETHING_UNMAPPED"]


@pytest.fixture(scope="module")
def generator():
    return PyreneSeries3Generator()


@pytest.fixture(scope="module")
def batches(generator):
    """One generated batch per target, reused across tests."""
    return {
        target: generator.generate_series3_compounds(
            target_protein=target,
            target_indication="pediatric_lymphoma",
            num_compounds=7,
        )
        for target in TARGETS
    }


# --------------------------------------------------------------------------
# Requested count is honoured.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("n", [1, 3, 20, 50])
def test_requested_compound_count_is_honoured(generator, n):
    compounds = generator.generate_series3_compounds("BCL2", "pediatric_lymphoma", num_compounds=n)
    assert len(compounds) == n


def test_zero_compounds_requested_yields_none(generator):
    assert generator.generate_series3_compounds("BCL2", "pediatric_lymphoma", num_compounds=0) == []


def test_compound_ids_are_unique_and_sequential(generator):
    compounds = generator.generate_series3_compounds("BCL2", "pediatric_lymphoma", num_compounds=5)
    ids = [c.compound_id for c in compounds]
    assert len(set(ids)) == len(ids), f"duplicate compound_ids: {ids}"
    assert ids[0] == "AGI-PYRENE3-0001"
    assert ids[-1] == "AGI-PYRENE3-0005"


# --------------------------------------------------------------------------
# Score bounds. The dataclass field comments state the ranges.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("target", TARGETS)
def test_pediatric_safety_score_within_0_1(batches, target):
    for c in batches[target]:
        assert 0.0 <= c.pediatric_safety_score <= 1.0, (
            f"{c.compound_id} ({target}) pediatric_safety_score="
            f"{c.pediatric_safety_score} outside documented 0-1"
        )


@pytest.mark.parametrize("target", TARGETS)
def test_predicted_potency_within_documented_window(batches, target):
    """PyreneCompound documents predicted_potency as -12 to -6 kcal/mol."""
    for c in batches[target]:
        assert -12.0 <= c.predicted_potency <= -6.0, (
            f"{c.compound_id} ({target}) predicted_potency="
            f"{c.predicted_potency} outside documented -12..-6 kcal/mol"
        )


@pytest.mark.parametrize("target", TARGETS)
def test_selectivity_score_within_0_1(batches, target):
    for c in batches[target]:
        assert 0.0 <= c.selectivity_score <= 1.0, (
            f"{c.compound_id} ({target}) selectivity_score={c.selectivity_score}"
        )


@pytest.mark.parametrize("target", TARGETS)
def test_synthetic_accessibility_within_0_1(batches, target):
    for c in batches[target]:
        assert 0.0 <= c.synthetic_accessibility <= 1.0, (
            f"{c.compound_id} ({target}) synthetic_accessibility={c.synthetic_accessibility}"
        )


@pytest.mark.parametrize("target", TARGETS)
def test_no_nan_or_infinity_in_any_numeric_field(batches, target):
    numeric_fields = (
        "pediatric_safety_score",
        "predicted_potency",
        "synthetic_accessibility",
        "selectivity_score",
    )
    for c in batches[target]:
        for field in numeric_fields:
            value = getattr(c, field)
            assert isinstance(value, float), f"{field} is {type(value).__name__}, not float"
            assert math.isfinite(value), f"{c.compound_id} {field}={value} is not finite"


def test_binding_energy_respects_its_own_cap(generator):
    """_calculate_binding_energy caps at -11.5; the strongest warhead pair must
    not punch through it."""
    energy = generator._calculate_binding_energy("hydroxamate", "hydroxamate", "BCL2")
    assert energy >= -11.5, f"binding energy {energy} broke the -11.5 cap"


# --------------------------------------------------------------------------
# Mechanism / warhead selection matches the documented mapping.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("target,expected", sorted(DOCUMENTED_MECHANISM_MAP.items()))
def test_mechanism_matches_documented_mapping(generator, target, expected):
    assert generator._select_mechanism(target) is expected


def test_unmapped_target_defaults_to_intrinsic(generator):
    assert generator._select_mechanism("NOT_A_REAL_TARGET") is ApoptosisType.INTRINSIC


@pytest.mark.parametrize("target,expected_warheads", sorted(DOCUMENTED_WARHEAD_MAP.items()))
def test_warhead_selection_matches_documented_mapping(generator, target, expected_warheads):
    assert generator._target_preferences(target) == list(expected_warheads)


@pytest.mark.parametrize("target,expected_warheads", sorted(DOCUMENTED_WARHEAD_MAP.items()))
def test_first_pair_is_the_documented_preference(generator, target, expected_warheads):
    """The highest-priority pair must be the documented preferred warheads."""
    assert generator._warhead_pairs(target, 1)[0] == tuple(expected_warheads)


@pytest.mark.parametrize("count", [5, 20, 60])
def test_warhead_pairs_are_distinct_until_space_exhausted(generator, count):
    """Regression: generation used to return the same pair for every compound."""
    pairs = generator._warhead_pairs("BCL2", count)
    assert len(pairs) == count
    expected_unique = min(count, len(generator.warhead_library) * (len(generator.warhead_library) - 1))
    assert len(set(pairs)) == expected_unique


def test_pair_offset_yields_unseen_chemistry(generator):
    """Successive evolution cycles must explore different regions."""
    first = generator._warhead_pairs("BCL2", 20, offset=0)
    second = generator._warhead_pairs("BCL2", 20, offset=20)
    assert not set(first) & set(second)


def test_prefer_biases_pairs_toward_requested_warheads(generator):
    """Exploitation passes `prefer` to re-enter the region around a top performer."""
    assert generator._warhead_pairs("BCL2", 1, prefer=["glucose", "urea"])[0] == ("glucose", "urea")


@pytest.mark.parametrize("target", sorted(DOCUMENTED_MECHANISM_MAP))
def test_generated_compound_mechanism_is_consistent_with_mapping(generator, target):
    compounds = generator.generate_series3_compounds(target, "pediatric_lymphoma", num_compounds=3)
    expected = DOCUMENTED_MECHANISM_MAP[target]
    for c in compounds:
        assert c.apoptotic_mechanism is expected, (
            f"{c.compound_id}: target {target} produced {c.apoptotic_mechanism}, "
            f"documented mapping says {expected}"
        )


def test_explicit_mechanism_argument_overrides_the_mapping(generator):
    compounds = generator.generate_series3_compounds(
        "BCL2", "pediatric_lymphoma", num_compounds=2,
        apoptotic_mechanism=ApoptosisType.GRANZYME,
    )
    assert all(c.apoptotic_mechanism is ApoptosisType.GRANZYME for c in compounds)


@pytest.mark.parametrize("target", TARGETS)
def test_warhead_types_agree_with_the_warhead_library(generator, batches, target):
    """warhead_types must be the library's type for the chosen warheads, not a
    separately-maintained list that can drift."""
    for c in batches[target]:
        assert len(c.warhead_types) == 2
        assert c.warhead_types[0] is generator.warhead_library[c.warhead_1]["type"]
        assert c.warhead_types[1] is generator.warhead_library[c.warhead_2]["type"]


@pytest.mark.parametrize("target", TARGETS)
def test_chosen_warheads_exist_in_the_library(generator, batches, target):
    for c in batches[target]:
        assert c.warhead_1 in generator.warhead_library
        assert c.warhead_2 in generator.warhead_library


# --------------------------------------------------------------------------
# Warhead library structural integrity.
# --------------------------------------------------------------------------

WARHEAD_REQUIRED_KEYS = {"type", "smarts", "targets", "potency_boost",
                         "selectivity_risk", "pediatric_safety"}


def test_warhead_library_records_are_complete(generator):
    for name, w in generator.warhead_library.items():
        missing = WARHEAD_REQUIRED_KEYS - set(w)
        assert not missing, f"warhead {name!r} missing keys {missing}"
        assert isinstance(w["type"], WarheadType)
        assert 0.0 <= w["pediatric_safety"] <= 1.0, f"{name} pediatric_safety={w['pediatric_safety']}"
        assert 0.0 <= w["selectivity_risk"] <= 1.0, f"{name} selectivity_risk={w['selectivity_risk']}"
        assert w["potency_boost"] > 0, f"{name} potency_boost={w['potency_boost']}"
        assert isinstance(w["targets"], list) and w["targets"]


def test_series_definitions_have_coherent_affinity_ranges(generator):
    for key, series in generator.series_definitions.items():
        low, high = series.binding_affinity_range
        assert low < high, f"{key} binding_affinity_range={series.binding_affinity_range} inverted"
        assert 0.0 <= series.pediatric_safety <= 1.0
        assert series.rings > 0
        assert series.warheads, f"{key} declares no warheads"


@pytest.mark.xfail(
    strict=True,
    reason="Known data gap, not a code defect: series_3 advertises an 'isothiazole' "
           "warhead that the library has no entry for. Closing it means either dropping "
           "a documented warhead or inventing its potency_boost, pediatric_safety and "
           "selectivity_risk constants, and fabricating pediatric safety numbers is not "
           "acceptable. strict=True so this alerts if someone supplies real values.",
)
def test_series_3_warheads_all_exist_in_the_library(generator):
    """series_3 advertises four warheads; every one must be resolvable."""
    series = generator.series_definitions["series_3"]
    unknown = [w for w in series.warheads if w not in generator.warhead_library]
    assert not unknown, f"series_3 advertises warheads absent from the library: {unknown}"


# --------------------------------------------------------------------------
# Downstream summary / MD helpers must not blow up on generated input.
# --------------------------------------------------------------------------


def test_compound_summary_is_serialisable(generator, batches):
    import json

    summary = generator.get_compound_summary(batches["BCL2"][0])
    json.dumps(summary)  # raises if a non-serialisable enum leaked through
    assert summary["compound_id"].startswith("AGI-PYRENE3-")
    assert summary["apoptotic_mechanism"] == ApoptosisType.INTRINSIC.value


def test_batch_md_reports_every_compound(generator, batches):
    compounds = batches["BCL2"]
    results = generator.batch_molecular_dynamics(compounds, target_structure="1XYZ", duration_ns=5)
    assert results["compounds_simulated"] == len(compounds)
    assert len(results["refined_compounds"]) == len(compounds)
    for r in results["refined_compounds"]:
        assert math.isfinite(r["refined_affinity"])
        assert 0.0 <= r["stability_score"] <= 1.0


def test_generated_compounds_accumulate_on_the_generator():
    """generate_* appends to self.generated_compounds; a fresh generator starts empty."""
    g = PyreneSeries3Generator()
    assert g.generated_compounds == []
    g.generate_series3_compounds("BCL2", "pediatric_lymphoma", num_compounds=4)
    assert len(g.generated_compounds) == 4
    g.generate_series3_compounds("FAS", "pediatric_lymphoma", num_compounds=3)
    assert len(g.generated_compounds) == 7


# --------------------------------------------------------------------------
# Documented behaviour of the batch: what does "generate N compounds" mean?
# --------------------------------------------------------------------------


def test_batch_is_deterministic_for_identical_inputs():
    """Two generators given the same request must agree — no hidden randomness."""
    a = PyreneSeries3Generator().generate_series3_compounds("BCL2", "pediatric_lymphoma", num_compounds=5)
    b = PyreneSeries3Generator().generate_series3_compounds("BCL2", "pediatric_lymphoma", num_compounds=5)
    assert [c.predicted_potency for c in a] == [c.predicted_potency for c in b]
    assert [c.warhead_1 for c in a] == [c.warhead_1 for c in b]


def test_batch_contains_more_than_one_distinct_design(batches):
    """A request for N compounds should explore N designs, not emit one design N
    times under N different IDs.

    This is the invariant a drug-discovery 'generator' exists to satisfy. It is
    asserted here rather than measured in the eval because a batch with a single
    distinct design makes every downstream ranking, top-3 selection and
    'evolution' step meaningless.
    """
    compounds = batches["BCL2"]
    designs = {
        (c.warhead_1, c.warhead_2, c.predicted_potency, c.pediatric_safety_score)
        for c in compounds
    }
    assert len(designs) > 1, (
        f"all {len(compounds)} generated compounds are the same design "
        f"({designs.pop()}) with only the ID differing"
    )
