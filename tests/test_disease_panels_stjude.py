"""Structural tests for the StJude pediatric oncology panel and its citation checker.

These tests are offline on purpose: they guard the shape and internal consistency of the panel so
that a bad edit fails in CI in milliseconds. Whether the cited records still exist in the live
databases is the job of scripts/verify_panel_citations.py, which makes real calls.
"""
import re

import pytest

import disease_panels as panels
import verify_panel_citations as verifier

TARGET_FIELDS = {"symbol", "name", "inheritance", "prevalence", "mechanism", "pdb_count", "alphafold"}

UNIPROT = re.compile(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]$|^[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$")
PDB_ID = re.compile(r"^[0-9][A-Za-z0-9]{3}$")
NCT_ID = re.compile(r"^NCT[0-9]{8}$")
CHEMBL_ID = re.compile(r"^CHEMBL[0-9]+$")
PMID = re.compile(r"^[0-9]{1,8}$")

PANEL = panels.get_panel("StJude")
EVIDENCE = panels.STJUDE_EVIDENCE
SYMBOLS = [t["symbol"] for t in PANEL["targets"]]


def test_panel_is_registered_alongside_the_existing_ones():
    assert {"ALS", "Parkinsons", "Shriners", "StJude"} <= set(panels.list_panels())
    assert len(panels.get_panel("ALS")["targets"]) == 20, "existing ALS panel must not change"
    assert PANEL["programs"] and PANEL["description"]


def test_every_target_uses_the_established_record_shape():
    reference = set(panels.get_panel("ALS")["targets"][0])
    assert reference == TARGET_FIELDS
    for target in PANEL["targets"]:
        assert set(target) == TARGET_FIELDS, f"{target.get('symbol')} has extra or missing fields"
        assert isinstance(target["pdb_count"], int) and target["pdb_count"] >= 0
        assert isinstance(target["alphafold"], bool)
        for field in ("name", "inheritance", "prevalence", "mechanism"):
            assert target[field].strip(), f"{target['symbol']}.{field} is empty"


def test_symbols_are_unique():
    assert len(SYMBOLS) == len(set(SYMBOLS))


def test_every_target_has_an_evidence_record_and_vice_versa():
    assert set(SYMBOLS) == set(EVIDENCE), "panel targets and evidence records must correspond"
    for symbol in SYMBOLS:
        assert panels.get_target_evidence(symbol) is EVIDENCE[symbol]


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_identifiers_are_well_formed(symbol):
    ev = EVIDENCE[symbol]
    assert UNIPROT.match(ev["uniprot"]), ev["uniprot"]
    assert ev["pdb_ids"], "every target cites at least one experimental structure"
    for pdb_id in ev["pdb_ids"]:
        assert PDB_ID.match(pdb_id), pdb_id
    if ev["chembl_target"] is not None:
        assert CHEMBL_ID.match(ev["chembl_target"])
    for drug in ev["drugs"]:
        assert CHEMBL_ID.match(drug["chembl_id"]) and drug["name"].strip()
    for trial in ev["trials"]:
        assert NCT_ID.match(trial["nct_id"]) and trial["note"].strip()
    for claim in ev["claims"]:
        assert PMID.match(claim["pmid"]), claim["pmid"]
        assert len(claim["quote"]) >= 16, "a quote must be specific enough to be checkable"


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_evidence_matches_the_target_record(symbol):
    target = next(t for t in PANEL["targets"] if t["symbol"] == symbol)
    ev = EVIDENCE[symbol]
    assert target["alphafold"] is bool(ev["alphafold_model"])
    if ev["alphafold_model"]:
        assert ev["alphafold_model"] == f"AF-{ev['uniprot']}-F1"
    assert target["pdb_count"] >= len(ev["pdb_ids"])
    assert ev["claims"], f"{symbol} makes claims with no citation"
    for field in ("indication", "tractability", "unmet_need", "caveat"):
        assert ev[field].strip(), f"{symbol}.{field} is empty"


@pytest.mark.parametrize("symbol", SYMBOLS)
def test_undruggable_targets_claim_no_drug(symbol):
    """Honesty check: a target called undruggable must not also cite a drug against it."""
    ev = EVIDENCE[symbol]
    undruggable = "undruggable" in ev["tractability"] or "not a small-molecule" in ev["tractability"]
    if undruggable:
        assert ev["drugs"] == [], f"{symbol} is described as undruggable but cites a drug"
    if ev["chembl_target"] is None:
        assert ev["potent_ligands"] == 0 and ev["drugs"] == []


def test_the_panel_names_undruggable_targets_rather_than_omitting_them():
    hard = [s for s in SYMBOLS if "undruggable" in EVIDENCE[s]["tractability"]]
    assert {"MYCN", "FLI1", "PAX3", "H3-3A"} <= set(hard)


def test_evidence_is_scoped_to_this_panel():
    """A symbol may legitimately appear in another panel (ACVR1 is also a Shriners target);
    what must hold is that STJUDE_EVIDENCE describes exactly the StJude targets."""
    assert set(EVIDENCE) == set(SYMBOLS)
    assert panels.get_target_evidence("SOD1") is None


def test_checker_reports_failures_and_normalises_text():
    report = verifier.Report(verbose=False)
    assert report.check("X", "pmid", "1", True, "fine") is True
    assert report.check("X", "pmid", "2", False, "broken") is False
    assert [r[2] for r in report.failures] == ["2"]
    assert verifier.norm("  a\n b  ") == "a b"


def test_checker_seed_record_is_wired_to_fail():
    symbol, ev, target = verifier.BAD_SEED
    assert symbol not in EVIDENCE
    assert set(target) == TARGET_FIELDS
    assert ev["claims"][-1]["pmid"] in {c["pmid"] for c in EVIDENCE["ALK"]["claims"]}, \
        "the seed should include a real PMID with a false quote, to test quote checking"


def test_checker_rejects_an_unknown_panel_without_touching_the_network():
    assert verifier.main(["NoSuchPanel"]) == 2
