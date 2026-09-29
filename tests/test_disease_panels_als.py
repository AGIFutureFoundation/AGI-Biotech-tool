"""Structural guards for the cited ALS panel.

Offline by design, like tests/test_disease_panel_citations.py: the live re-resolution of every
identifier is scripts/verify_panel_citations.py. What is guarded here is that the ALS evidence
records exist, are shaped the way that script expects, and -- specifically for this panel -- that
the two failure modes that produced the previous fabricated version cannot come back:

  * a pdb_count asserted without a live re-derivation behind it, and
  * a structure count standing in for tractability on a protein that has no druggable pocket.
"""
import re

import pytest

from disease_panels import ALS_EVIDENCE, DISEASE_PANELS

TARGETS = DISEASE_PANELS["ALS"]["targets"]
IDS = [t["symbol"] for t in TARGETS]
TARGET_KEYS = {"symbol", "name", "inheritance", "prevalence", "mechanism", "pdb_count", "alphafold"}
EVIDENCE_KEYS = ("indication", "uniprot", "pdb_ids", "alphafold_model", "chembl_target",
                 "potent_ligands", "drugs", "trials", "claims", "modality", "tractability",
                 "unmet_need", "caveat")

UNIPROT_RE = re.compile(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]$|^[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$")
PDB_RE = re.compile(r"^[0-9A-Z]{4}$")
PMID_RE = re.compile(r"^\d{7,8}$")
NCT_RE = re.compile(r"^NCT\d{8}$")
CHEMBL_RE = re.compile(r"^CHEMBL\d+$")

# Counts re-derived live against RCSB on 2026-09-22, against what the panel used to claim.
# Five of these were wrong by more than 3x, in both directions, and three claimed structures
# for accessions RCSB holds none for.
LIVE_PDB_COUNTS = {
    "SOD1": 156, "TARDBP": 44, "FUS": 23, "C9orf72": 4, "TBK1": 25, "OPTN": 14, "VCP": 144,
    "SQSTM1": 26, "UBQLN2": 4, "PFN1": 22, "KIF5A": 4, "NEK1": 2, "ATXN2": 1, "MATR3": 0,
    "HNRNPA1": 73, "CHCHD10": 5, "ANG": 56, "STMN2": 0, "UNC13A": 0, "SIGMAR1": 5,
}
FABRICATED_PDB_COUNTS = {
    "SOD1": 50, "TARDBP": 15, "FUS": 20, "C9orf72": 5, "TBK1": 30, "OPTN": 10, "VCP": 40,
    "SQSTM1": 15, "UBQLN2": 8, "PFN1": 25, "KIF5A": 10, "NEK1": 8, "ATXN2": 5, "MATR3": 3,
    "HNRNPA1": 20, "CHCHD10": 2, "ANG": 15, "STMN2": 2, "UNC13A": 5, "SIGMAR1": 8,
}
NO_STRUCTURE = {"MATR3", "STMN2", "UNC13A"}


@pytest.mark.parametrize("target", TARGETS, ids=IDS)
def test_target_record_shape_is_unchanged(target):
    """ALS panel records keep the shape the rest of the codebase reads."""
    assert set(target) == TARGET_KEYS, f"ALS/{target['symbol']} drifted from the panel record shape"
    assert isinstance(target["pdb_count"], int) and target["pdb_count"] >= 0
    assert isinstance(target["alphafold"], bool)


@pytest.mark.parametrize("target", TARGETS, ids=IDS)
def test_every_target_has_an_evidence_record(target):
    ev = ALS_EVIDENCE.get(target["symbol"])
    assert ev is not None, f"ALS/{target['symbol']} has no evidence record to re-resolve"
    missing = [k for k in EVIDENCE_KEYS if k not in ev]
    assert not missing, f"ALS/{target['symbol']} evidence missing {missing}"


def test_evidence_and_panel_cover_the_same_symbols():
    assert set(ALS_EVIDENCE) == {t["symbol"] for t in TARGETS}


@pytest.mark.parametrize("target", TARGETS, ids=IDS)
def test_evidence_identifier_formats(target):
    ev = ALS_EVIDENCE[target["symbol"]]
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


@pytest.mark.parametrize("target", TARGETS, ids=IDS)
def test_counts_do_not_overstate(target):
    ev = ALS_EVIDENCE[target["symbol"]]
    assert len(ev["pdb_ids"]) <= target["pdb_count"], "more example structures than the live count"
    if target["pdb_count"] == 0:
        assert ev["pdb_ids"] == [], "no structures, so no example ids"
    assert isinstance(ev["potent_ligands"], int) and ev["potent_ligands"] >= 0
    if ev["chembl_target"] is None:
        assert ev["potent_ligands"] == 0, "no ChEMBL target means no potent ligands to claim"


@pytest.mark.parametrize("target", TARGETS, ids=IDS)
def test_pdb_counts_match_the_live_rederivation(target):
    """The whole point of the rebuild: every count traces to an RCSB answer, not to a guess."""
    symbol = target["symbol"]
    assert target["pdb_count"] == LIVE_PDB_COUNTS[symbol], (
        f"{symbol} pdb_count {target['pdb_count']} is not the value re-derived from RCSB "
        f"({LIVE_PDB_COUNTS[symbol]}); re-run scripts/verify_panel_citations.py ALS"
    )


@pytest.mark.parametrize("target", TARGETS, ids=IDS)
def test_no_fabricated_count_survived(target):
    """Guards the specific numbers that were invented, so a revert is loud rather than quiet."""
    symbol = target["symbol"]
    if LIVE_PDB_COUNTS[symbol] != FABRICATED_PDB_COUNTS[symbol]:
        assert target["pdb_count"] != FABRICATED_PDB_COUNTS[symbol], (
            f"{symbol} is back to its fabricated pdb_count {FABRICATED_PDB_COUNTS[symbol]}"
        )


@pytest.mark.parametrize("symbol", sorted(NO_STRUCTURE))
def test_targets_with_no_structures_say_so(symbol):
    """RCSB genuinely holds nothing for these three; that is a finding, not an outage to paper over."""
    target = next(t for t in TARGETS if t["symbol"] == symbol)
    assert target["pdb_count"] == 0
    ev = ALS_EVIDENCE[symbol]
    assert ev["pdb_ids"] == []
    assert "none" in ev["tractability"].lower() or "zero" in ev["tractability"].lower()


@pytest.mark.parametrize("target", TARGETS, ids=IDS)
def test_every_target_carries_a_checkable_claim(target):
    ev = ALS_EVIDENCE[target["symbol"]]
    assert ev["claims"], f"ALS/{target['symbol']} asserts a phenotype with no citation"


@pytest.mark.parametrize("target", TARGETS, ids=IDS)
def test_modality_is_stated_for_every_target(target):
    """A structure count must never be left to imply small-molecule tractability on its own."""
    ev = ALS_EVIDENCE[target["symbol"]]
    assert ev["modality"].strip(), f"ALS/{target['symbol']} states no therapeutic modality"


@pytest.mark.parametrize("symbol", ["TARDBP", "FUS", "HNRNPA1", "MATR3", "ATXN2", "UBQLN2"])
def test_aggregation_prone_rna_binders_are_not_sold_as_druggable(symbol):
    """These carry structures that are fibrils or isolated domains; the record must say so."""
    ev = ALS_EVIDENCE[symbol]
    assert "poor" in ev["tractability"].lower() or "none" in ev["tractability"].lower(), (
        f"{symbol} is an aggregation-prone RNA-binding protein and must not be called tractable"
    )
    # The record has to engage with the docking question explicitly, whether it does so by
    # naming small molecules or by saying there is nothing to dock against.
    modality = ev["modality"].lower().replace("-", " ")
    assert "small molecule" in modality or "dock" in modality, (
        f"{symbol} modality does not say whether small-molecule work is appropriate"
    )


def test_antisense_is_named_as_the_working_modality_where_it_is():
    """Tofersen (SOD1) and jacifusen (FUS) are antisense; the panel must not imply small molecule."""
    for symbol in ("SOD1", "TARDBP", "FUS", "ATXN2"):
        assert "antisense" in ALS_EVIDENCE[symbol]["modality"].lower(), symbol


def test_tofersen_is_not_cited_as_a_sod1_protein_drug():
    """ChEMBL points tofersen at 'SOD1 mRNA' (a nucleic-acid target), not at P00441.

    Citing it as a drug against the protein accession would fail the verifier's drug-target check,
    and would misrepresent the modality. The record explains this instead.
    """
    ev = ALS_EVIDENCE["SOD1"]
    assert ev["drugs"] == [], "tofersen acts on the transcript; it is not a P00441 protein ligand"
    assert "mRNA" in ev["modality"] or "mRNA" in ev["caveat"]


def test_symbols_use_the_uniprot_gene_spelling():
    """The verifier matches the panel symbol against UniProt gene names exactly.

    'TDP43' is not a gene name (Q13148 is TARDBP) and C9orf72 is not spelled C9ORF72; both
    previously made the panel unverifiable.
    """
    symbols = {t["symbol"] for t in TARGETS}
    assert "TDP43" not in symbols and "TARDBP" in symbols
    assert "C9ORF72" not in symbols and "C9orf72" in symbols


def test_risk_genes_are_not_described_as_mendelian():
    """NEK1, ATXN2, UNC13A and STMN2 were all labelled 'AD' with a '<1% fALS' prevalence.

    None of them is a dominant Mendelian ALS gene: two are risk alleles, one is a GWAS
    polymorphism and one is a downstream consequence of TDP-43 loss.
    """
    for symbol in ("NEK1", "ATXN2", "UNC13A", "STMN2"):
        target = next(t for t in TARGETS if t["symbol"] == symbol)
        assert target["inheritance"] != "AD", f"{symbol} is not an autosomal dominant ALS gene"
        assert "risk" in target["inheritance"].lower() or "not a mendelian" in target["inheritance"].lower()


def test_loss_of_function_targets_are_flagged_against_inhibitor_chemistry():
    """TBK1, NEK1 and ANG carry real inhibitor chemistry but the disease is loss of function.

    An inhibitor is the wrong direction, and the record has to say so rather than letting the
    ligand count read as an opportunity.
    """
    for symbol in ("TBK1", "NEK1", "ANG"):
        ev = ALS_EVIDENCE[symbol]
        blob = (ev["modality"] + " " + ev["tractability"] + " " + ev["caveat"]).lower()
        assert "wrong direction" in blob or "inverted" in blob, symbol
