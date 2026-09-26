"""Does the SYNTHETIC marker survive the trip from engine to human?

synthetic_provenance.SyntheticValue propagates through arithmetic, so most
aggregation keeps its marking for free. That is easy to rely on without
checking, which is how the two bugs this file pins got written.

The gap is COUNTING. `sum(1 for x in xs if x > t)` and `len([x for x in xs
if ...])` consume synthetic values and return a clean int, because the 1s being
summed were never tainted. The predicate carried the provenance; the tally
dropped it. The resulting number is the most quotable kind there is -- "47
compounds showed favourable binding" -- and it arrives with nothing to say it
came from placeholders.

That matters more now that chain_anchor.py can write a record to Monad
permanently. An unmarked count is exactly what gets anchored and cited.

The first test documents which operations are safe, so the next person can see
at a glance where re-tainting is required rather than rediscovering it.
"""
import warnings

import pytest

import synthetic_provenance as sp

S = sp.SyntheticValue


@pytest.fixture(autouse=True)
def _quiet():
    """The module warns once on first synthetic construction; that is its job."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", sp.SyntheticResultWarning)
        yield


# --------------------------------------------------------------------------- the contract

def test_arithmetic_preserves_the_marker():
    """Mean, sum, negation, rounding: all safe without help."""
    xs = [S(-9.4), S(-8.1), S(-7.7)]
    assert sp.is_synthetic(sum(xs))
    assert sp.is_synthetic(sum(xs) / len(xs))
    assert sp.is_synthetic(-xs[0])
    assert sp.is_synthetic(round(xs[0], 2))
    assert sp.is_synthetic(xs[0] * 2 + 1)


def test_selection_preserves_the_marker():
    """min/max/sorted return the element itself, so the taint rides along."""
    xs = [S(-9.4), S(-8.1)]
    assert sp.is_synthetic(min(xs))
    assert sp.is_synthetic(max(xs))
    assert sp.is_synthetic(sorted(xs))
    # Clamping against a plain bound is the documented exception: the bound wins.
    assert not sp.is_synthetic(max(S(-1.0), 0.0))


def test_formatting_preserves_the_marker():
    """Every textual form carries it, including f-strings with a format spec."""
    x = S(-9.4)
    assert sp.MARKER in f"{x:.2f}"
    assert sp.MARKER in f"{x}"
    assert sp.MARKER in str(x)
    assert sp.MARKER in repr(x)


def test_counting_is_the_one_operation_that_launders():
    """The gap, pinned. If this ever starts passing, the class of bug is gone."""
    xs = [S(-9.4), S(-8.1), S(-7.7)]

    laundered = sum(1 for x in xs if x < -8)
    assert laundered == 2
    assert not sp.is_synthetic(laundered), "counting now propagates; simplify the callers"

    # derive() is the remedy: re-taint from the inputs the count was taken over.
    assert sp.is_synthetic(sp.derive(laundered, *xs))


def test_derive_does_not_taint_a_clean_count():
    """Re-tainting must be conditional, or every number becomes suspect and none is."""
    reals = [-9.4, -8.1, -7.7]
    assert not sp.is_synthetic(sp.derive(sum(1 for x in reals if x < -8), *reals))


# --------------------------------------------------------------------------- regression: reporting

def test_screening_report_count_is_marked_when_scores_are_synthetic():
    """A 'publication-ready' summary must not state a clean tally of placeholders.

    Regression: the executive summary read "identified N compounds with
    favorable binding scores" where every score was a SyntheticValue but N was
    a bare int.
    """
    from reporting import generate_screening_report

    results = [{"compound_id": f"AGI-{i}", "score": S(-9.0 + i), "smiles": "CCO"}
               for i in range(5)]
    report = generate_screening_report("p1", "c1", "BCL2", results)

    summary = report.sections["executive_summary"]["content"]

    # Asserting the marker merely appears in the summary would pass with or
    # without the fix, because the top-5 list formats each score and each of
    # those carries it. The claim under test is specifically that the COUNT
    # between "identified" and "compounds" is marked, so the assertion reads
    # only that span.
    span = summary.split("identified", 1)[1].split("compounds", 1)[0]
    assert sp.MARKER in span, f"count of favourable compounds is unmarked: {span!r}"

    # And it must read as a whole number of compounds, not 2.0 of them.
    assert "2.0" not in span
    assert span.strip().startswith("2")


def test_screening_report_count_is_clean_for_measured_scores():
    """The marker must not appear when the numbers are real."""
    from reporting import generate_screening_report

    results = [{"compound_id": f"AGI-{i}", "score": -9.0 + i, "smiles": "CCO"}
               for i in range(5)]
    report = generate_screening_report("p1", "c1", "BCL2", results)

    assert sp.MARKER not in report.sections["executive_summary"]["content"]


# --------------------------------------------------------------------------- regression: VR panel

def test_lipinski_count_reaching_the_vr_panel_is_marked():
    """Regression: 'pass_lipinski' displayed as a clean int beside marked numbers.

    Exercised through the real ADMET predictor rather than a stand-in, because
    the bug was in how a genuine SyntheticValue survived a genuine count.
    """
    from molecular_research_pipeline import ADMETPredictor

    admet = [ADMETPredictor().predict_admet(compound_id=f"AGI-{i}", mol_weight=400,
                                            logp=3.0, hba=5, hbd=2)
             for i in range(3)]
    absorption = [a.absorption_score for a in admet]

    assert sp.is_synthetic(absorption[0]), "predictor no longer returns synthetic scores"

    # The expression the orchestrator now uses.
    count = sp.derive(sum(1 for s in absorption if s == 1.0), *absorption)
    assert sp.is_synthetic(count)
    assert sp.MARKER in f"{count}"


def test_the_orchestrator_retaints_its_admet_count():
    """The fix is present at the call site, not just available in the helper."""
    import inspect

    import team_agent_orchestration as tao

    source = inspect.getsource(tao.TeamAgentOrchestrator.coordinate_lead_optimization_workflow)
    assert "pass_lipinski" in source
    lipinski_line = next(l for l in source.splitlines() if "pass_lipinski" in l)
    block = source[source.index(lipinski_line):source.index(lipinski_line) + 220]
    assert "sp.derive" in block, "pass_lipinski is counted without re-tainting"


# --------------------------------------------------------------------------- the anchoring tie-in

def test_a_report_built_from_synthetic_scores_cannot_be_anchored_silently():
    """The two halves meet here: an unmarked count would slip past the anchor gate.

    chain_anchor refuses synthetic records by detecting the marker. If a count
    launders it away, a record of placeholders can look clean enough to anchor
    permanently. This is the end-to-end reason the re-tainting matters.
    """
    import chain_anchor as ca

    manifest = {
        "merkle_root": "0x" + "ab" * 32,
        "entries": {"favorable_count": sp.derive(sum(1 for _ in range(3)),
                                                 S(-9.4))},
    }
    out = ca.anchor_payload(manifest)

    assert out["refused"] is True
    assert out["unsigned_transaction"] is None
