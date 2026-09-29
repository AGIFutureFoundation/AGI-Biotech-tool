"""Contract tests for pyrene structure assembly.

The point of this module is that a compound is a molecule rather than a label,
so the tests assert exactly that: a real core, warheads actually bonded, and
descriptors computed from the structure instead of hand-set.
"""
import pytest
from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors

from pyrene_structures import WARHEAD_SMILES, assemble, conformer, core, profile

RDLogger.DisableLog("rdApp.*")


def test_pyrene_core_is_actually_pyrene():
    """Regression: the series shipped phenanthrene labelled as a pyrene core."""
    mol = core("pyrene")
    assert rdMolDescriptors.CalcMolFormula(mol) == "C16H10"
    assert rdMolDescriptors.CalcNumRings(mol) == 4


def test_declared_core_was_phenanthrene():
    """Pins what the generator actually had, so the bug cannot quietly return."""
    declared = Chem.MolFromSmiles("C1=CC=C2C(=C1)C=CC3=CC=CC=C32")
    phenanthrene = Chem.MolFromSmiles("c1ccc2ccc3ccccc3c2c1")

    assert Chem.MolToSmiles(declared) == Chem.MolToSmiles(phenanthrene)
    assert rdMolDescriptors.CalcMolFormula(declared) == "C14H10"
    assert rdMolDescriptors.CalcNumRings(declared) == 3
    assert Chem.MolToSmiles(declared) != Chem.MolToSmiles(core("pyrene"))


@pytest.mark.parametrize("warhead", sorted(WARHEAD_SMILES))
def test_every_warhead_fragment_is_valid_chemistry(warhead):
    """A typo in the fragment table would corrupt every compound using it."""
    assert Chem.MolFromSmiles(WARHEAD_SMILES[warhead]) is not None


@pytest.mark.parametrize("warhead", sorted(WARHEAD_SMILES))
def test_each_warhead_assembles_onto_the_core(warhead):
    mol = assemble(warhead)
    assert mol is not None, f"{warhead} failed to assemble"
    assert Chem.MolFromSmiles(Chem.MolToSmiles(mol)) is not None


def test_assembled_compound_is_larger_than_the_bare_core():
    """Proves the warhead is bonded on, not merely named beside the core."""
    bare = core("pyrene")
    built = assemble("acrylamide", "urea")

    assert built.GetNumHeavyAtoms() > bare.GetNumHeavyAtoms()
    assert rdMolDescriptors.CalcNumRings(built) == 4  # core survives intact


def test_different_warheads_give_different_molecules():
    """The generator used to emit identical compounds; structures must differ."""
    a = assemble("acrylamide", "urea")
    b = assemble("hydroxamate", "trifluoromethyl")
    assert Chem.MolToSmiles(a) != Chem.MolToSmiles(b)


def test_unknown_warhead_returns_none_rather_than_guessing():
    assert assemble("not-a-real-warhead") is None
    assert assemble("acrylamide", "also-not-real") is None


def test_profile_values_are_computed_not_constant():
    """Hand-set constants were the original problem; these must track structure."""
    small = profile(assemble("amide"))
    large = profile(assemble("vinylsulfonamide", "glucose"))

    assert large["mw"] > small["mw"]
    assert large["heavy_atoms"] > small["heavy_atoms"]
    assert small["formula"] != large["formula"]


def test_conformer_is_embeddable_for_docking():
    """Docking and MD need 3D coordinates, which labels could never provide."""
    mol = conformer(assemble("acrylamide", "urea"))

    assert mol is not None
    assert mol.GetNumConformers() == 1
    assert mol.GetNumAtoms() > assemble("acrylamide", "urea").GetNumAtoms()  # Hs added
