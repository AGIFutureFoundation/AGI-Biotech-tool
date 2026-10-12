"""Exercise the seams where one module hands an object to another.

A bug shipped here that neither module's own tests could catch: the pyrene
generator read `result.smiles` from a `DockingResult` that had no such field,
so the integration worked only while nobody used it. Import-graph analysis
could not see the connection either, because the scorer is *injected* rather
than imported, and a static attribute checker written for this turned out to
produce fourteen findings of which none were real — two distinct classes share
the name `DockingResult`, which is exactly the ambiguity that defeats it.

So these are runtime tests, and they deliberately use **real objects rather
than mocks**. A mock supplies whatever attribute is asked of it, which would
have hidden the original bug perfectly.
"""
import inspect

import pytest


def test_generator_accepts_the_real_scorer_and_reads_only_fields_it_has():
    """The seam that broke. Contract, checked without paying for a docking run."""
    import pyrene_docking
    from pyrene_apoptotic_discovery import PyreneSeries3Generator

    generator = PyreneSeries3Generator(structural_scorer=pyrene_docking.PyreneVinaScorer())
    source = inspect.getsource(PyreneSeries3Generator._structural_score)

    fields = set(pyrene_docking.DockingResult.__dataclass_fields__)
    methods = {n for n, _ in inspect.getmembers(pyrene_docking.DockingResult, inspect.isfunction)}

    for attr in ("smiles", "vina_like_score", "as_record"):
        if f"result.{attr}" in source:
            assert attr in fields or attr in methods, (
                f"_structural_score reads result.{attr} but DockingResult has no such "
                f"field or method; fields are {sorted(fields)}")


def test_the_two_docking_result_classes_stay_distinguishable():
    """Two classes share this name. Conflating them is how the bug hid."""
    from molecular_research_pipeline import DockingResult as Stub
    from pyrene_docking import DockingResult as Real

    assert Stub is not Real
    assert "binding_energy" in Stub.__dataclass_fields__
    assert "vina_like_score" in Real.__dataclass_fields__
    # The real one must not grow a kcal/mol-shaped field name by accident.
    assert "binding_energy" not in Real.__dataclass_fields__


def test_scorer_exposes_what_the_generator_calls():
    import pyrene_docking
    from pyrene_apoptotic_discovery import PyreneSeries3Generator

    source = inspect.getsource(PyreneSeries3Generator._structural_score)
    scorer = pyrene_docking.PyreneVinaScorer()

    assert "scorer.score_warheads(" in source
    assert callable(getattr(scorer, "score_warheads", None))

    params = inspect.signature(scorer.score_warheads).parameters
    for expected in ("warhead_1", "warhead_2", "target", "name"):
        assert expected in params, f"generator passes {expected}= which scorer lacks"


def test_generator_without_a_scorer_marks_its_output_synthetic():
    """No scorer means the old constants, which must stay labelled."""
    from pyrene_apoptotic_discovery import PyreneSeries3Generator

    compound = PyreneSeries3Generator().generate_series3_compounds("BCL2", "ped", 1)[0]
    assert "SYNTHETIC" in f"{compound.predicted_potency}"


def test_evolution_accepts_real_team_agents():
    """Injected agents; a signature drift here is invisible to import analysis."""
    from continuous_compound_evolution import ContinuousCompoundEvolution
    from team_agent_orchestration import AgentRole, TeamAgentOrchestrator

    team = TeamAgentOrchestrator()
    evolution = ContinuousCompoundEvolution(team_agents={
        "optimizer": team.agents[AgentRole.OPTIMIZER],
        "analyst": team.agents[AgentRole.ANALYST],
        "orchestrator": team.agents[AgentRole.ORCHESTRATOR],
    })

    assert evolution.optimizer_agent is not None
    assert evolution.analyst_agent is not None
    assert evolution.orchestrator_agent is not None


def test_enrichment_engine_accepts_a_real_federator():
    from biotech_molecular_integration import (BiotechDatabaseFederator,
                                               MolecularEnrichmentEngine)

    engine = MolecularEnrichmentEngine(BiotechDatabaseFederator())

    stats = engine.federator.get_database_stats()
    assert isinstance(stats.get("total_databases"), int)
    assert "1.5B" not in str(stats), "the fabricated record total must not return"


def test_discovery_pipeline_reads_fields_its_sources_provide():
    """It joins four modules; each lazy import is a seam."""
    import discovery_pipeline as pipeline

    report = pipeline.investigate("LMNA", max_drugs=0, include_sourcing=False)

    for key in ("symbol", "panel", "precedent_drugs", "repurposing", "notes"):
        assert key in report, f"summarise() reads {key!r}"
    pipeline.summarise(report)  # must not raise on a real report


def test_validation_cost_reads_the_evidence_class_the_panel_writes():
    import longevity_panel as lv
    import validation_cost as vc

    used = {e.get("evidence_class") for e in lv.LONGEVITY_EVIDENCE.values()}
    assert used <= set(vc._NEXT), f"panel classes the planner cannot handle: {used - set(vc._NEXT)}"


def test_document_ingest_uses_chem_extract_as_it_is_defined():
    import chem_extract
    import document_ingest

    assert "extract" in inspect.getsource(document_ingest)
    params = inspect.signature(chem_extract.extract).parameters
    assert "rejects" in params, "callers pass rejects= to collect unparseable candidates"


@pytest.mark.parametrize("module_name", [
    "compound_sourcing", "repurposing_engine", "pyrene_docking", "vina_score",
    "content_store", "screening_economics", "discovery_pipeline",
])
def test_module_imports_and_exposes_something_public(module_name):
    """A module nothing can import is a seam that fails before it is reached."""
    module = __import__(module_name)
    public = [n for n in dir(module) if not n.startswith("_")]
    assert public, f"{module_name} exposes no public API"


# --------------------------------------------------------- the positive case

def test_a_scorer_actually_produces_a_computed_potency_not_a_constant():
    """The claim the platform rests on, asserted end to end rather than by shape.

    Everything above checks the seam by reading source and signatures. None of
    it would notice the regression that matters most: a `try/except` wrapped
    around the scorer call, falling back to `_calculate_binding_energy`. The
    attribute names would still match, the scorer would still expose
    `score_warheads`, and the no-scorer test would still see `[SYNTHETIC]` --
    all green, while the platform's strongest claim quietly reverted to a
    lookup table.

    So this runs the path and inspects the value: a real float, not a
    SyntheticValue, with the SMILES of the molecule it was computed on.
    """
    import synthetic_provenance as sp
    import pyrene_docking
    from pyrene_apoptotic_discovery import PyreneSeries3Generator

    generator = PyreneSeries3Generator(structural_scorer=pyrene_docking.PyreneVinaScorer())
    compounds = generator.generate_series3_compounds("BCL2", "pediatric_leukemia", 2)
    assert compounds, "the structural path produced nothing"

    for c in compounds:
        potency = c.predicted_potency
        assert not isinstance(potency, sp.SyntheticValue), (
            f"{c.compound_id} came back as {potency!r} -- a placeholder. The scorer was "
            "supplied, so this is either a silent fallback or a broken wire-up.")
        assert "SYNTHETIC" not in f"{potency}"
        assert isinstance(float(potency), float)

        # A score whose molecule cannot be identified is the untraceable number
        # this whole module exists to replace.
        assert c.smiles, f"{c.compound_id} carries a computed potency but no SMILES"
        assert "c" in c.smiles.lower(), f"{c.compound_id} SMILES has no carbon: {c.smiles!r}"


def test_the_computed_record_says_which_fields_are_still_placeholders():
    """Potency being real must not launder the fields that are not."""
    import pyrene_docking
    from pyrene_apoptotic_discovery import PyreneSeries3Generator

    generator = PyreneSeries3Generator(structural_scorer=pyrene_docking.PyreneVinaScorer())
    c = generator.generate_series3_compounds("BCL2", "pediatric_leukemia", 1)[0]

    assert "COMPUTED predicted_potency" in c.provenance
    for still_a_constant in ("pediatric_safety_score", "synthetic_accessibility",
                             "selectivity_score"):
        assert still_a_constant in c.provenance, (
            f"{still_a_constant} is still a hand-set constant but the provenance "
            "field no longer names it")


def test_a_failing_scorer_raises_rather_than_falling_back():
    """The documented contract: no scorer means constants, a broken one means stop."""
    import pyrene_docking
    from pyrene_apoptotic_discovery import PyreneSeries3Generator

    class Broken(pyrene_docking.PyreneVinaScorer):
        def score_warheads(self, *a, **kw):
            raise RuntimeError("receptor unavailable")

    generator = PyreneSeries3Generator(structural_scorer=Broken())
    with pytest.raises(RuntimeError, match="receptor unavailable"):
        generator.generate_series3_compounds("BCL2", "pediatric_leukemia", 1)
