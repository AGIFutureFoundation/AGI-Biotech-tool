"""Structural guards for the cited disease panels (Shriners, Parkinsons).

These tests are offline by design: they check that every target in the two curated panels carries
the identifiers a citation check needs, in the right shape, so that a live re-resolution run
(UniProt / PDB / PubMed / ChEMBL / ClinicalTrials.gov) has something to verify. The live run is a
separate script; a unit-test suite must not depend on the network.
"""
import re

import pytest

from disease_panels import DISEASE_PANELS

CITED_PANELS = ("Shriners", "Parkinsons")
REQUIRED_KEYS = ("symbol", "name", "inheritance", "prevalence", "mechanism", "pdb_count", "alphafold",
                 "uniprot", "pdb_ids", "chembl_target", "clinvar_pathogenic", "pediatric",
                 "pediatric_note", "pmids", "nct_ids", "verified")

UNIPROT_RE = re.compile(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]$|^[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$")
PDB_RE = re.compile(r"^[0-9A-Z]{4}$")
PMID_RE = re.compile(r"^\d{7,8}$")
NCT_RE = re.compile(r"^NCT\d{8}$")
CHEMBL_RE = re.compile(r"^CHEMBL\d+$")

TARGETS = [(panel, t) for panel in CITED_PANELS for t in DISEASE_PANELS[panel]["targets"]]


def ids(pair):
    return f"{pair[0]}-{pair[1]['symbol']}"


@pytest.mark.parametrize("panel,target", TARGETS, ids=[ids(p) for p in TARGETS])
def test_required_keys_present(panel, target):
    missing = [k for k in REQUIRED_KEYS if k not in target]
    assert not missing, f"{panel}/{target.get('symbol')} missing {missing}"


@pytest.mark.parametrize("panel,target", TARGETS, ids=[ids(p) for p in TARGETS])
def test_identifier_formats(panel, target):
    assert UNIPROT_RE.match(target["uniprot"]), f"bad UniProt accession {target['uniprot']}"
    for pdb in target["pdb_ids"]:
        assert PDB_RE.match(pdb), f"bad PDB id {pdb}"
    for pmid in target["pmids"]:
        assert PMID_RE.match(pmid), f"bad PMID {pmid}"
    for nct in target["nct_ids"]:
        assert NCT_RE.match(nct), f"bad NCT id {nct}"
    if target["chembl_target"] is not None:
        assert CHEMBL_RE.match(target["chembl_target"]), f"bad ChEMBL id {target['chembl_target']}"


@pytest.mark.parametrize("panel,target", TARGETS, ids=[ids(p) for p in TARGETS])
def test_counts_are_consistent(panel, target):
    """pdb_count is a live count, so it must be a non-negative int and cover the listed examples."""
    assert isinstance(target["pdb_count"], int) and target["pdb_count"] >= 0
    assert isinstance(target["clinvar_pathogenic"], int) and target["clinvar_pathogenic"] >= 0
    assert len(target["pdb_ids"]) <= target["pdb_count"], "listed PDB examples exceed the live count"
    if target["pdb_count"] == 0:
        assert target["pdb_ids"] == [], "no structures, so no example ids"


@pytest.mark.parametrize("panel,target", TARGETS, ids=[ids(p) for p in TARGETS])
def test_every_claim_has_at_least_one_citation(panel, target):
    cited = target["pmids"] + target["nct_ids"] + re.findall(r"NCT\d{8}", target["pediatric_note"])
    assert cited, f"{panel}/{target['symbol']} asserts a phenotype with no PMID or NCT citation"


@pytest.mark.parametrize("panel,target", TARGETS, ids=[ids(p) for p in TARGETS])
def test_pediatric_flag_is_explicit(panel, target):
    """The panels feed decisions about children: the adult/pediatric call must never be implicit."""
    assert isinstance(target["pediatric"], bool)
    assert target["pediatric_note"].strip(), "pediatric_note must say why"
    if not target["pediatric"]:
        assert "ADULT" in target["pediatric_note"], \
            "a non-pediatric target must say so in words, not only in the flag"


def test_parkinsons_keeps_a_genuinely_pediatric_core():
    peds = {t["symbol"] for t in DISEASE_PANELS["Parkinsons"]["targets"] if t["pediatric"]}
    assert {"PRKN", "PINK1", "PARK7", "ATP13A2", "TH", "DDC", "SLC6A3", "GCH1"} <= peds


def test_shriners_scope_has_no_unsupported_wound_healing_targets():
    """TGFB1/VEGFA/MMP9/RHOA were removed: generic wound-healing proteins with no pediatric,
    Shriners-scope evidence found. Re-adding one requires citations, which this guards."""
    symbols = {t["symbol"] for t in DISEASE_PANELS["Shriners"]["targets"]}
    assert not symbols & {"TGFB1", "VEGFA", "MMP9", "RHOA", "RTN4"}
