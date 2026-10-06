"""A synthetic value must never leave the pipeline unlabelled.

These tests are written to FAIL if a placeholder number can reach a caller, a
JSON payload or a printed report without announcing itself. They do not check
that the numbers are good — they are not numbers at all in the scientific
sense; they check that nobody can mistake them for computed ones.

The walk below is deliberately generic: it discovers synthetic leaves anywhere
in a record and demands a provenance marker at or above them, so a NEW field
added to any of these records is covered without anyone remembering to.
"""
import dataclasses
import json
import subprocess
import sys

import pytest

from conftest import REPO_ROOT, SOURCE_DIRS

import molecular_research_pipeline as mrp
import pyrene_apoptotic_discovery as pad
import pyrene_validation_framework as pvf
from synthetic_provenance import MARKER, SyntheticValue, is_synthetic

# Real inputs/derived counts that legitimately are NOT synthetic: they are echoes
# of what the caller asked for, or genuinely computed. Anything else that is a
# float and not marked is a leak.
ALLOWED_PLAIN_NUMERIC = {
    "duration_ns",        # the requested duration, echoed back
    "frames_analyzed", "equilibration_frames", "production_frames",
    "compounds_simulated", "compounds_analyzed", "panel_size",
    "rotatable_bonds",    # real: RDKit
    "grid_size", "temperature", "pressure", "timestep",
    "pose_number",        # an index, not a measurement
    "duration_hours", "volume_per_dose", "timeline_months",
    "expected_selectivity_ratio",  # a stated design target, not a prediction
}


def to_plain(obj):
    """Serialize a record the way a consumer would: dataclass -> dict -> JSON."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    return obj


def walk(node, path="", provenanced=False):
    """Yield (path, value, covered_by_provenance) for every leaf."""
    if isinstance(node, dict):
        covered = provenanced or (MARKER in str(node.get("provenance", "")))
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else str(k), covered)
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]", provenanced)
    else:
        yield path, node, provenanced


# --------------------------------------------------------------------------
# Every result-producing entry point, constructed for real.
# --------------------------------------------------------------------------


def _records():
    """(name, record) for every public result type in the three stub modules."""
    out = []

    dock = mrp.MolecularDockingEngine()
    d = dock.dock("AGI-1", "BCL2")
    out.append(("DockingResult", d))
    out.append(("prepare_ligand", dock.prepare_ligand("AGI-1", "CC(C)Cc1ccc(cc1)C(C)C(=O)O")))
    out.append(("prepare_receptor", dock.prepare_receptor("BCL2", "/tmp/4O1J.pdb")))
    out.append(("docking_history", dock.docking_history[0]))

    md = mrp.MolecularDynamicsEngine()
    out.append(("setup_simulation", md.setup_simulation("AGI-1", "BCL2")))
    sim = md.run_simulation("AGI-1", "BCL2", duration_ns=0.01)
    out.append(("MDSimulation", sim))
    out.append(("analyze_trajectory", md.analyze_trajectory("AGI-1")))

    out.append(("ADMETProperties",
                mrp.ADMETPredictor().predict_admet("AGI-1", 350.0, 2.0, 5, 2)))

    out.append(("score_compound", mrp.CompoundScoringEngine().score_compound({
        'id': 'AGI-1',
        'binding_energy': d.binding_energy,
        'admet': dataclasses.asdict(mrp.ADMETPredictor().predict_admet("AGI-1", 350.0, 2.0, 5, 2)),
    })))

    rep = mrp.DrugRepurposingEngine()
    cands = rep.find_repurposing_candidates("BCL2", "pediatric_lymphoma")
    if cands:
        out.append(("repurposing_candidate", cands[0]))
    out.append(("off_target_effects", rep.analyze_off_target_effects("Aspirin", ["BCL2", "XIAP"])))

    out.append(("analyze_sar", mrp.StructureActivityRelationship().analyze_sar([{}], "binding")))

    gen = pad.PyreneSeries3Generator()
    compound = gen.generate_series3_compounds("BCL2", "pediatric_lymphoma", num_compounds=1)[0]
    out.append(("PyreneCompound", compound))
    out.append(("compound_summary", gen.get_compound_summary(compound)))
    out.append(("batch_molecular_dynamics",
                gen.batch_molecular_dynamics([compound], "4O1J", duration_ns=5)))

    val = pvf.PyrenePediatricValidator()
    assays = val.design_biochemical_validation(compound.compound_id, "BCL2",
                                               compound.predicted_potency)
    out.append(("BiochemicalAssay", assays[0]))
    cells = val.design_cell_assays(compound.compound_id, "INTRINSIC", "BCL2")
    out.append(("CellAssay", cells[0]))
    screen = val.design_selectivity_panel(compound.compound_id, "BCL2", "INTRINSIC")
    formulation = val.design_pediatric_formulation(compound.compound_id, "child",
                                                   compound.predicted_potency)
    out.append(("FormulationStrategy", formulation))
    out.append(("validation_report", val.create_validation_report(
        compound.compound_id, assays, cells, screen, formulation)))

    return out


RECORDS = _records()
RECORD_IDS = [name for name, _ in RECORDS]


@pytest.mark.parametrize("name,record", RECORDS, ids=RECORD_IDS)
def test_synthetic_values_are_covered_by_provenance(name, record):
    """No synthetic leaf may sit outside a record that declares provenance."""
    plain = to_plain(record)
    leaks = [p for p, v, covered in walk(plain) if isinstance(v, SyntheticValue) and not covered]
    assert not leaks, (
        f"{name}: synthetic values with no provenance marker at or above them: {leaks}"
    )


@pytest.mark.parametrize("name,record", RECORDS, ids=RECORD_IDS)
def test_marker_survives_json_serialization(name, record):
    """The thing a recipient actually sees is JSON. The marker must be in it."""
    payload = json.dumps(to_plain(record), default=str)
    assert MARKER in payload, f"{name}: serialized record carries no {MARKER} marker:\n{payload}"


@pytest.mark.parametrize("name,record", RECORDS, ids=RECORD_IDS)
def test_no_unmarked_floating_point_result(name, record):
    """Any float leaf is either synthetic-marked or an allowlisted real input.

    This is the test that catches a NEW placeholder field: add one and it fails
    until it is either marked or justified in ALLOWED_PLAIN_NUMERIC.
    """
    unmarked = []
    for path, value, _covered in walk(to_plain(record)):
        if isinstance(value, bool) or not isinstance(value, float):
            continue
        if isinstance(value, SyntheticValue):
            continue
        leaf = path.split(".")[-1].split("[")[0]
        if leaf in ALLOWED_PLAIN_NUMERIC:
            continue
        unmarked.append(path)
    assert not unmarked, (
        f"{name}: unmarked float results {unmarked}. Wrap them in SyntheticValue "
        f"or, if genuinely computed/echoed, add the field to ALLOWED_PLAIN_NUMERIC."
    )


# --------------------------------------------------------------------------
# The marker must reach a human reading printed output, not just JSON.
# --------------------------------------------------------------------------


def test_str_and_format_carry_the_marker():
    v = SyntheticValue(-9.4)
    assert MARKER in str(v)
    assert MARKER in f"{v:.2f}"
    assert MARKER in f"{v:.1%}"
    assert MARKER in repr(v)
    assert MARKER in "{}".format(v)


def test_arithmetic_keeps_the_marker():
    """A synthetic number stays synthetic through the arithmetic consumers do."""
    v = SyntheticValue(-9.0)
    for derived in (v * 2, v + 1, 1 + v, v / 3, -v, abs(v), round(v, 1), v - 0.5, 0.5 - v):
        assert isinstance(derived, SyntheticValue), f"{derived!r} lost its marker"
    assert is_synthetic(sum([v, v]) / 2)


def test_float_conversion_is_the_only_documented_escape():
    """float(x) strips the marker. That is why records also carry provenance."""
    assert not isinstance(float(SyntheticValue(1.0)), SyntheticValue)


# --------------------------------------------------------------------------
# Specific claims the modules used to make.
# --------------------------------------------------------------------------


def test_docking_engine_does_not_claim_vina_integration():
    engine = mrp.MolecularDockingEngine()
    assert "Vina" not in engine.scoring_function or "not integrated" in engine.scoring_function
    assert "AutoDock Vina integration" not in (mrp.MolecularDockingEngine.__doc__ or "")
    assert "STUB" in (mrp.__doc__ or "")


def test_rotatable_bonds_uses_rdkit():
    """Real chemistry, not letter-counting: the old heuristic gave 2 for butane."""
    count = mrp.MolecularDockingEngine()._count_rotatable_bonds
    assert count("CCCC") == 1
    assert count("CC(C)Cc1ccc(cc1)C(C)C(=O)O") == 4  # ibuprofen
    assert count("c1ccccc1") == 0


def test_rotatable_bonds_rejects_unparseable_smiles():
    """A bad SMILES must raise, not silently return a number."""
    with pytest.raises(ValueError):
        mrp.MolecularDockingEngine()._count_rotatable_bonds("not_a_smiles(((")


def test_kd_conversion_marks_synthetic_input_but_not_real_input():
    """Kd inherits provenance through math.exp, which would otherwise drop it."""
    val = pvf.PyrenePediatricValidator()
    assert isinstance(val._convert_affinity_to_kd(SyntheticValue(-9.4)), SyntheticValue)
    assert not isinstance(val._convert_affinity_to_kd(-9.4), SyntheticValue)


def test_import_emits_one_runtime_warning_on_first_synthetic_value():
    """A caller who ignores docstrings still gets told once, at runtime."""
    code = (
        "import warnings\n"
        "warnings.simplefilter('always')\n"
        "import molecular_research_pipeline as m\n"
        "with warnings.catch_warnings(record=True) as w:\n"
        "    warnings.simplefilter('always')\n"
        "    e = m.MolecularDockingEngine()\n"
        "    e.dock('a', 'b'); e.dock('c', 'd')\n"
        "    from synthetic_provenance import SyntheticResultWarning\n"
        "    hits = [x for x in w if issubclass(x.category, SyntheticResultWarning)]\n"
        "print(len(hits))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT),
        env={"PYTHONPATH": ":".join(str(d) for d in SOURCE_DIRS),
             "PATH": "/usr/bin:/bin", "HOME": ""},
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    # Exactly one: the warning fires on first use, not once per value.
    assert result.stdout.strip() == "1", result.stdout
