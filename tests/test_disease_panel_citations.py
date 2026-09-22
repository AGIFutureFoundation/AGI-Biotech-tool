"""Structural guards for the cited Parkinsons and Shriners panels.

These tests are offline by design. The live re-resolution of every identifier is
scripts/verify_panel_citations.py; what is checked here is that the evidence records exist, are
shaped the way that script expects, and never let a claim into the panel without something to
re-resolve. A unit-test suite must not depend on the network, so nothing here makes a request.
"""
import re

import pytest

from disease_panels import DISEASE_PANELS, PARKINSONS_EVIDENCE, SHRINERS_EVIDENCE

EVIDENCE = {"Parkinsons": PARKINSONS_EVIDENCE, "Shriners": SHRINERS_EVIDENCE}
TARGET_KEYS = {"symbol", "name", "inheritance", "prevalence", "mechanism", "pdb_count", "alphafold"}
EVIDENCE_KEYS = ("indication", "pediatric_onset", "uniprot", "pdb_ids", "alphafold_model",
                 "chembl_target", "potent_ligands", "drugs", "trials", "claims",
                 "tractability", "unmet_need", "caveat")

UNIPROT_RE = re.compile(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]$|^[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$")
PDB_RE = re.compile(r"^[0-9A-Z]{4}$")
PMID_RE = re.compile(r"^\d{7,8}$")
NCT_RE = re.compile(r"^NCT\d{8}$")
CHEMBL_RE = re.compile(r"^CHEMBL\d+$")

PAIRS = [(panel, t) for panel in EVIDENCE for t in DISEASE_PANELS[panel]["targets"]]
IDS = [f"{p}-{t['symbol']}" for p, t in PAIRS]


@pytest.mark.parametrize("panel,target", PAIRS, ids=IDS)
def test_target_record_shape_is_unchanged(panel, target):
    """The panel records stay the shape the rest of the codebase reads; evidence lives beside them."""
    assert set(target) == TARGET_KEYS, f"{panel}/{target['symbol']} drifted from the panel record shape"
    assert isinstance(target["pdb_count"], int) and target["pdb_count"] >= 0
    assert isinstance(target["alphafold"], bool)


@pytest.mark.parametrize("panel,target", PAIRS, ids=IDS)
def test_every_target_has_an_evidence_record(panel, target):
    ev = EVIDENCE[panel].get(target["symbol"])
    assert ev is not None, f"{panel}/{target['symbol']} has no evidence record to re-resolve"
    missing = [k for k in EVIDENCE_KEYS if k not in ev]
    assert not missing, f"{panel}/{target['symbol']} evidence missing {missing}"


@pytest.mark.parametrize("panel,target", PAIRS, ids=IDS)
def test_evidence_identifier_formats(panel, target):
    ev = EVIDENCE[panel][target["symbol"]]
    assert UNIPROT_RE.match(ev["uniprot"]), f"bad UniProt accession {ev['uniprot']}"
    assert ev["alphafold_model"] == f"AF-{ev['uniprot']}-F1"
    for pdb in ev["pdb_ids"]:
        assert PDB_RE.match(pdb), f"bad PDB id {pdb}"
    for claim in ev["claims"]:
        assert PMID_RE.match(claim["pmid"]), f"bad PMID {claim['pmid']}"
        assert claim["quote"].strip(), "a claim needs a verbatim quote to check against the abstract"
    for trial in ev["trials"]:
        assert NCT_RE.match(trial["nct_id"]), f"bad NCT id {trial['nct_id']}"
    for drug in ev["drugs"]:
        assert CHEMBL_RE.match(drug["chembl_id"]), f"bad ChEMBL id {drug['chembl_id']}"
    if ev["chembl_target"] is not None:
        assert CHEMBL_RE.match(ev["chembl_target"])


@pytest.mark.parametrize("panel,target", PAIRS, ids=IDS)
def test_counts_do_not_overstate(panel, target):
    ev = EVIDENCE[panel][target["symbol"]]
    assert len(ev["pdb_ids"]) <= target["pdb_count"], "more example structures than the live count"
    if target["pdb_count"] == 0:
        assert ev["pdb_ids"] == [], "no structures, so no example ids"
    assert isinstance(ev["potent_ligands"], int) and ev["potent_ligands"] >= 0
    if ev["chembl_target"] is None:
        assert ev["potent_ligands"] == 0, "no ChEMBL target means no potent ligands to claim"


@pytest.mark.parametrize("panel,target", PAIRS, ids=IDS)
def test_every_target_carries_a_checkable_claim(panel, target):
    ev = EVIDENCE[panel][target["symbol"]]
    assert ev["claims"], f"{panel}/{target['symbol']} asserts a phenotype with no citation"


@pytest.mark.parametrize("panel,target", PAIRS, ids=IDS)
def test_pediatric_status_is_explicit_in_the_panel_itself(panel, target):
    """A reader of the panel must not have to open the evidence to learn who the target is for."""
    ev = EVIDENCE[panel][target["symbol"]]
    assert isinstance(ev["pediatric_onset"], bool)
    prevalence = target["prevalence"].upper()
    if ev["pediatric_onset"]:
        assert "PEDIATRIC" in prevalence
    else:
        assert "NOT PEDIATRIC" in prevalence and "ADULT" in ev["caveat"].upper()


def test_parkinsons_keeps_a_genuinely_pediatric_core():
    peds = {s for s, ev in PARKINSONS_EVIDENCE.items() if ev["pediatric_onset"]}
    assert {"PRKN", "PINK1", "PARK7", "ATP13A2", "TH", "DDC", "SLC6A3", "GCH1"} <= peds
    adult = {s for s, ev in PARKINSONS_EVIDENCE.items() if not ev["pediatric_onset"]}
    assert {"SNCA", "LRRK2", "VPS35", "MAOB", "COMT", "DRD2"} == adult


def test_gba1_is_not_sold_as_pediatric_parkinsons():
    caveat = PARKINSONS_EVIDENCE["GBA1"]["caveat"]
    assert "GAUCHER" in caveat.upper() and "not cause pediatric" in caveat


def test_shriners_scope_has_no_unsupported_wound_healing_targets():
    """TGFB1/VEGFA/MMP9/RHOA/RTN4 were removed: no pediatric, Shriners-scope evidence was found.
    Re-adding one means adding citations, which this guards."""
    symbols = {t["symbol"] for t in DISEASE_PANELS["Shriners"]["targets"]}
    assert not symbols & {"TGFB1", "VEGFA", "MMP9", "RHOA", "RTN4"}
    assert set(SHRINERS_EVIDENCE) == symbols
