"""The port check: server/vina_score.py must agree with js/dock.js term by term.

A scoring function ported silently wrong is the failure mode that matters here,
because the output still looks like a plausible number. So this does not assert
that the port is correct -- it runs BOTH implementations over the SAME receptor
geometry and the SAME ligand geometry and compares every term, the atom typing
behind every term, the rotatable-bond count and the H-bond list.

Fixtures (tests/fixtures/, offline):
  bcl2_6o0k_pocket.pdb        real crystallographic geometry: chain A of PDB
                              6O0K (BCL-2 + venetoclax), every residue with an
                              atom within 12 A of the venetoclax ligand.
  pyrene_acrylamide_amide.mol a real assembled pyrene compound from
                              server/pyrene_structures.py, MMFF-optimised,
                              centred on the venetoclax centroid.
"""
import json
import math
import pathlib
import shutil
import subprocess

import pytest

from conftest import REPO_ROOT

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
RECEPTOR = FIXTURES / "bcl2_6o0k_pocket.pdb"
LIGAND = FIXTURES / "pyrene_acrylamide_amide.mol"
HARNESS = FIXTURES / "score_with_dock_js.mjs"

# Both sides hold coordinates as float32 and reduce in double precision, so the
# only legitimate difference is summation order. Anything larger is a real
# divergence, not noise.
ABS_TOL = 1e-9


def _js_result():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; cannot run the reference implementation")
    proc = subprocess.run(
        [node, str(HARNESS), str(RECEPTOR), str(LIGAND)],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120)
    assert proc.returncode == 0, f"js/dock.js harness failed:\n{proc.stderr}"
    return json.loads(proc.stdout)


def _py_result():
    from vina_score import (Ligand, ProteinGrid, parse_molblock, parse_pdb,
                            rotatable_bonds, vina_score)
    rec = parse_pdb(RECEPTOR.read_text())
    lig_st = parse_molblock(LIGAND.read_text())
    grid, lig = ProteinGrid(rec), Ligand(lig_st)
    out = vina_score(grid, lig, details=True)
    out["nrotBonds"] = len(rotatable_bonds(lig_st))
    out["ligHeavy"] = len(lig.heavy)
    out["recAtoms"] = len(grid.atoms)
    out["ligTypes"] = {"hydrophobic": int(lig.hydrophobic.sum()),
                       "donor": int(lig.donor.sum()),
                       "acceptor": int(lig.acceptor.sum())}
    out["recTypes"] = {"hydrophobic": int(grid.hydrophobic.sum()),
                       "donor": int(grid.donor.sum()),
                       "acceptor": int(grid.acceptor.sum())}
    return out


@pytest.fixture(scope="module")
def both():
    return _js_result(), _py_result()


def test_fixtures_exist():
    for f in (RECEPTOR, LIGAND, HARNESS):
        assert f.is_file(), f"missing fixture {f}"


def test_receptor_atom_selection_matches(both):
    """The scored receptor atom set must be identical: a different atom set
    would make every term comparison below meaningless."""
    js, py = both
    assert js["recAtoms"] == py["recAtoms"] > 0


def test_atom_typing_matches(both):
    """Hydrophobic / donor / acceptor typing drives three of the five terms.

    Two implementations can agree on a total while disagreeing about which atom
    is which, so the typing is compared on its own.
    """
    js, py = both
    assert js["ligTypes"] == py["ligTypes"]
    assert js["recTypes"] == py["recTypes"]
    assert sum(py["ligTypes"].values()) > 0


def test_rotatable_bond_count_matches(both):
    js, py = both
    assert js["nrotBonds"] == py["nrotBonds"] == js["nrot"] == py["nrot"]


@pytest.mark.parametrize("term", ["gauss1", "gauss2", "repulsion", "hydrophobic", "hbond"])
def test_each_weighted_term_matches(both, term):
    js, py = both
    a, b = js["terms"][term], py["terms"][term]
    assert math.isclose(a, b, rel_tol=0, abs_tol=ABS_TOL), (
        f"term {term} diverged: js={a!r} python={b!r} (delta {abs(a - b):.3e}). "
        "The port is wrong; do not tune until it looks close.")


def test_every_term_is_actually_exercised(both):
    """Guard the guard: a fixture where four terms are zero would let a broken
    port pass four comparisons vacuously."""
    _js, py = both
    for term, value in py["terms"].items():
        assert value != 0.0, f"term {term} is zero in this fixture; it proves nothing"


def test_total_and_ligand_efficiency_match(both):
    js, py = both
    assert math.isclose(js["total"], py["total"], rel_tol=0, abs_tol=ABS_TOL)
    assert math.isclose(js["inter"], py["inter"], rel_tol=0, abs_tol=ABS_TOL)
    assert math.isclose(js["ligandEfficiency"], py["ligandEfficiency"],
                        rel_tol=0, abs_tol=ABS_TOL)


def test_hbond_and_contact_lists_match(both):
    js, py = both
    assert sorted(js["contactResidues"]) == sorted(py["contactResidues"])
    js_hb = sorted((h["lig"], h["prot"], round(h["r"], 9)) for h in js["hbonds"])
    py_hb = sorted((h["lig"], h["prot"], round(h["r"], 9)) for h in py["hbonds"])
    assert js_hb == py_hb


def test_weights_are_vinas_published_values():
    """The weights are the one thing a port cannot derive; transcribe them right."""
    import vina_score as vs
    assert (vs.W_GAUSS1, vs.W_GAUSS2, vs.W_REPULSION, vs.W_HYDROPHOBIC,
            vs.W_HBOND, vs.W_ROT) == (-0.0356, -0.00516, 0.84, -0.0351, -0.587, 0.0585)
    assert vs.CUT == 8.0
