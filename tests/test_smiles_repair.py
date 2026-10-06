"""Contract tests for shorthand SMILES repair.

The safety properties matter more than the recovery rate here: this code
rewrites scientific structures, so it must never alter a molecule that already
parses, and must never emit something unparseable.
"""
import pytest
from rdkit import Chem, RDLogger

from smiles_repair import AMBIGUOUS, EXPANSIONS, repair, repair_many

RDLogger.DisableLog("rdApp.*")

# The AGI catalogue scaffold, substituent left as a format slot.
CORE = "C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(%s)C=C4"

SHORTHAND_THAT_MUST_REPAIR = ["OCH3", "OCF3", "CF3", "OCHF2", "NO2", "SO2NH2", "COOH"]


@pytest.mark.parametrize("token", SHORTHAND_THAT_MUST_REPAIR)
def test_shorthand_substituent_is_repaired(token):
    original = CORE % token
    assert Chem.MolFromSmiles(original) is None, "fixture must start invalid"

    fixed, notes = repair(original)

    assert fixed is not None, f"{token} should be repairable: {notes}"
    assert Chem.MolFromSmiles(fixed) is not None
    assert any(token in n for n in notes)


@pytest.mark.parametrize("token", ["Cl", "Br", "F", "I"])
def test_valid_halogen_substituent_is_left_alone(token):
    """Halogens are already SMILES atoms; touching them would be a regression."""
    assert repair(CORE % token)[0] is None


def test_already_valid_input_is_never_rewritten():
    """The core safety property: parseable chemistry is never altered."""
    for smiles in ["CCO", "c1ccccc1", "NC1=NC2=CC(OC(F)(F)F)=CC=C2S1"]:
        fixed, notes = repair(smiles)
        assert fixed is None
        assert notes[0].startswith("already valid")


def test_ambiguous_shorthand_is_flagged_not_repaired():
    """`CN` parses as C-N but usually means nitrile -- too risky to rewrite."""
    assert "CN" in AMBIGUOUS
    assert EXPANSIONS["CN"] is None

    fixed, notes = repair(CORE % "CN")
    assert fixed is None
    assert any("ambiguous" in n for n in notes)


def test_unfixable_input_reports_rather_than_guessing():
    """Riluzole-file strings stay broken after expansion; say so, don't invent."""
    fixed, notes = repair("CC1=NC(=C(C(=N1)F)S(=O)(=O)NC)C(tert-butyl)C251=NC=CN=C252")
    assert fixed is None
    assert notes


def test_repair_never_emits_unparseable_output():
    candidates = [CORE % t for t in list(EXPANSIONS) + ["Cl", "ZZZ"]]
    for s in candidates:
        fixed, _ = repair(s)
        if fixed is not None:
            assert Chem.MolFromSmiles(fixed) is not None


def test_every_expansion_entry_is_itself_valid_chemistry():
    """A typo in the expansion table would silently corrupt every repair."""
    for token, expansion in EXPANSIONS.items():
        if expansion is None:
            continue
        assert Chem.MolFromSmiles(CORE % expansion) is not None, f"{token} expands to bad SMILES"


def test_batch_stats_account_for_every_input():
    smiles = [CORE % t for t in ("OCH3", "CF3", "Cl", "CN")] + ["not-a-molecule-at-all"]
    results, stats = repair_many(smiles)

    assert len(results) == stats["repaired"]
    assert stats["repaired"] + stats["already_valid"] + stats["unfixable"] == len(smiles)


def test_repaired_output_is_canonical():
    """Canonical form lets the inventory dedupe across source documents."""
    fixed, _ = repair(CORE % "CF3")
    assert fixed == Chem.MolToSmiles(Chem.MolFromSmiles(fixed))
