"""Priority 2: contract tests for server/chem_extract.py (SMILES extraction).

chem_extract's module docstring makes four specific claims about quirks it
handles. Each claim gets a test. A docstring that cannot be falsified is
marketing, not documentation.
"""
import pytest

import chem_extract


def canonicals(results):
    return {r["canonical"] for r in results}


def ids(results):
    return [r["id"] for r in results]


# --------------------------------------------------------------------------
# Known-good SMILES must be found and canonicalised.
# --------------------------------------------------------------------------

GOOD_SMILES = [
    # (input SMILES, expected RDKit canonical form)
    ("CC(=O)Oc1ccccc1C(=O)O", "CC(=O)Oc1ccccc1C(=O)O"),          # aspirin
    ("C1=CC2=C(C=C1OC(F)(F)F)SC(=N2)N", "Nc1nc2ccc(OC(F)(F)F)cc2s1"),  # riluzole
    ("CC1=NN(C(=O)C1)C2=CC=CC=C2", "CC1=NN(c2ccccc2)C(=O)C1"),   # edaravone
    ("CN1CCC(CC1)c1ccccc1", "CN1CCC(c2ccccc2)CC1"),
]


@pytest.mark.parametrize("smiles,expected_canonical", GOOD_SMILES)
def test_extracts_known_good_smiles(smiles, expected_canonical):
    found = chem_extract.extract(smiles, source="unit")
    assert expected_canonical in canonicals(found), (
        f"{smiles!r} was not extracted; got {canonicals(found)}"
    )


def test_canonicalisation_is_representation_independent():
    """The same molecule written two ways must collapse to one canonical entry."""
    kekule = chem_extract.extract("C1=CC=CC=C1C(=O)O")
    aromatic = chem_extract.extract("c1ccccc1C(=O)O")
    assert canonicals(kekule) == canonicals(aromatic) != set()


def test_deduplicates_repeated_molecule():
    text = "CC(=O)Oc1ccccc1C(=O)O\nCC(=O)Oc1ccccc1C(=O)O\nC1=CC=CC=C1C(=O)O"
    found = chem_extract.extract(text)
    assert len(found) == len(canonicals(found)), "duplicate canonical SMILES returned"


# --------------------------------------------------------------------------
# Known-bad input must yield nothing (no false positives).
# --------------------------------------------------------------------------

BAD_INPUTS = [
    "this is not a molecule at all",
    "",
    "    \n\n   ",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
    "1234567890",
    "The quick brown fox jumps over the lazy dog",
    "Compound Cmpd Cpd Synthetic",
]


@pytest.mark.parametrize("text", BAD_INPUTS)
def test_rejects_non_chemistry(text):
    assert chem_extract.extract(text) == [], f"false positive on {text!r}"


def test_prose_containing_chemistry_words_is_not_a_molecule():
    """Words like 'Compound' are letter-only tokens RDKit might parse as atoms."""
    found = chem_extract.extract("Compound was dissolved in Chloroform and Sodium")
    assert found == [], f"prose parsed as structures: {canonicals(found)}"


# --------------------------------------------------------------------------
# Docstring claim 1: SMILES wrapped across lines are re-joined and re-validated.
# --------------------------------------------------------------------------


def test_line_wrapped_smiles_is_rejoined():
    text = "AGI-Compound-12\nCC(=O)Oc1ccccc1C(=\nO)O"
    found = chem_extract.extract(text)
    assert "CC(=O)Oc1ccccc1C(=O)O" in canonicals(found), (
        f"line-wrapped SMILES not re-joined; got {canonicals(found)}"
    )


def test_line_wrapped_smiles_keeps_its_id():
    found = chem_extract.extract("AGI-Compound-12\nCC(=O)Oc1ccccc1C(=\nO)O")
    assert 12 in ids(found)


# --------------------------------------------------------------------------
# Docstring claim 2: an index number glued to the front ("150CN1CC2=..." -> #150).
# --------------------------------------------------------------------------


def test_glued_index_prefix_is_split_off():
    found = chem_extract.extract("150CN1CC2=CC=CC=C2C1")
    assert len(found) == 1, f"expected one compound, got {found}"
    assert found[0]["id"] == 150, f"glued index not recovered: id={found[0]['id']}"
    assert found[0]["canonical"] == "CN1Cc2ccccc2C1", (
        "the digits were not stripped before parsing; "
        f"canonical={found[0]['canonical']}"
    )


# --------------------------------------------------------------------------
# Docstring claim 3: IDs as "AGI 001", "AGI-Compound-12", "Compound #7", "001.".
# --------------------------------------------------------------------------

ID_CASES = [
    ("AGI 001  CC(=O)Oc1ccccc1C(=O)O", 1),
    ("AGI-Compound-12  CC(=O)Oc1ccccc1C(=O)O", 12),
    ("Compound #7: CN1CCC(CC1)c1ccccc1", 7),
    ("001. CC(=O)Oc1ccccc1C(=O)O", 1),
    ("AGI Synthetic Compound 42  CC(=O)Oc1ccccc1C(=O)O", 42),
    ("Cmpd-9  CC(=O)Oc1ccccc1C(=O)O", 9),
]


@pytest.mark.parametrize("text,expected_id", ID_CASES)
def test_compound_id_forms(text, expected_id):
    found = chem_extract.extract(text)
    assert found, f"nothing extracted from {text!r}"
    assert found[0]["id"] == expected_id, (
        f"{text!r} -> id {found[0]['id']}, expected {expected_id}"
    )


def test_id_is_read_from_the_header_line_above():
    """An ID on a line directly above the structure should still attach."""
    found = chem_extract.extract("AGI 077\nCC(=O)Oc1ccccc1C(=O)O")
    assert found and found[0]["id"] == 77


def test_id_is_none_when_absent_rather_than_invented():
    found = chem_extract.extract("CC(=O)Oc1ccccc1C(=O)O")
    assert found and found[0]["id"] is None


# --------------------------------------------------------------------------
# Docstring claim 4: nothing unparseable is kept, but SMILES-shaped failures are
# handed back via `rejects` instead of vanishing silently.
# --------------------------------------------------------------------------


def test_unparseable_but_smiles_shaped_goes_to_rejects():
    rejects = []
    found = chem_extract.extract("C1CC(=O)NNNN[Zz]1CCC", source="sheet.pdf", rejects=rejects)
    assert found == [], "an unparseable string was returned as a real compound"
    assert len(rejects) == 1, f"lost the unparseable candidate: {rejects}"
    assert rejects[0]["raw"] == "C1CC(=O)NNNN[Zz]1CCC"
    assert rejects[0]["source"] == "sheet.pdf"


def test_rejects_is_optional_and_extraction_still_works_without_it():
    assert chem_extract.extract("C1CC(=O)NNNN[Zz]1CCC") == []


def test_plain_prose_does_not_pollute_rejects():
    rejects = []
    chem_extract.extract("the meeting is at four o'clock on Tuesday", rejects=rejects)
    assert rejects == [], f"prose leaked into rejects: {rejects}"


# --------------------------------------------------------------------------
# Structural contract of the returned records.
# --------------------------------------------------------------------------

REQUIRED_KEYS = {"id", "smiles", "canonical", "label", "source"}


def test_result_records_have_the_documented_shape():
    found = chem_extract.extract("AGI 001  CC(=O)Oc1ccccc1C(=O)O", source="mysource")
    assert found
    for record in found:
        assert set(record) == REQUIRED_KEYS, f"unexpected record shape: {set(record)}"
        assert record["source"] == "mysource"
        assert isinstance(record["canonical"], str) and record["canonical"]
        assert record["id"] is None or isinstance(record["id"], int)


def test_multiple_compounds_across_a_document():
    text = (
        "AGI 001  CC(=O)Oc1ccccc1C(=O)O\n"
        "AGI 002  CC1=NN(C(=O)C1)C2=CC=CC=C2\n"
        "AGI 003  CN1CCC(CC1)c1ccccc1\n"
    )
    found = chem_extract.extract(text)
    assert len(found) == 3, f"expected 3 compounds, got {len(found)}: {canonicals(found)}"
    assert ids(found) == [1, 2, 3]
