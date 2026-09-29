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
