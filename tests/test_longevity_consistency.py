"""The panel must never claim stronger evidence than its own records support.

scripts/verify_longevity_citations.py already asks whether each citation still
resolves and still says what is quoted. That is the outward-facing check. This
is the inward one, and it catches a different and quieter failure: a record
whose evidence_class does not match the evidence in the same record.

That failure is invisible to a citation checker. Every PMID can resolve, every
quote can be verbatim, and the target can still be labelled
'approved-for-this-indication' with no approved drug attached to it — because
the label is a separate field a human typed. Downstream, a clinician or a
funder reads the label, not the twelve citations under it.

So these tests treat evidence_class as a claim to be checked against the record,
not as metadata. They are deliberately strict in one direction only: a record
may under-claim (carry more evidence than its class implies, which is merely
conservative) and may not over-claim.

The panel currently holds 18 targets; nothing here hardcodes that, so adding a
target means satisfying the rules rather than updating a number.
"""
import re

import pytest

import longevity_panel as lp


TARGETS = lp.LONGEVITY_PANEL["Longevity"]["targets"]
EVIDENCE = lp.LONGEVITY_EVIDENCE

#: Classes that assert a drug has been given to a human for this indication.
HUMAN_THERAPEUTIC = {"approved-for-this-indication", "human-rct", "human-uncontrolled"}


def _records():
    return sorted(EVIDENCE.items())


# --------------------------------------------------------------------------- the graph is whole

def test_every_panel_target_has_an_evidence_record():
    """A target on the panel with no evidence behind it is an assertion with no source."""
    missing = [t["symbol"] for t in TARGETS if t["symbol"] not in EVIDENCE]
    assert not missing, f"panel targets with no evidence record: {missing}"


def test_every_evidence_record_belongs_to_a_panel_target():
    """Orphan evidence is evidence nobody can reach, which rots unnoticed."""
    symbols = {t["symbol"] for t in TARGETS}
    orphans = [s for s in EVIDENCE if s not in symbols]
    assert not orphans, f"evidence records for targets not on the panel: {orphans}"


def test_the_two_arms_are_the_only_arms():
    """A typo'd arm silently drops a target out of every arm-filtered view."""
    arms = {ev["arm"] for ev in EVIDENCE.values()}
    assert arms == {"progeroid-pediatric", "geroscience-adult"}


# --------------------------------------------------------------------------- the class is earned

@pytest.mark.parametrize("symbol,ev", _records())
def test_evidence_class_is_one_of_the_declared_classes(symbol, ev):
    assert ev["evidence_class"] in lp.EVIDENCE_CLASSES, \
        f"{symbol} has an undeclared evidence class: {ev['evidence_class']!r}"


@pytest.mark.parametrize("symbol,ev", _records())
def test_an_approval_claim_is_traceable_to_what_was_approved(symbol, ev):
    """'approved-for-this-indication' is the strongest label available.

    A reader must be able to get from the label to the thing a regulator
    actually approved. Usually that is a drug in the same record. It can also be
    a registry record marked as the approval, which is how a disease gene can
    carry the label while the drug sits on its pharmacological target -- the
    ZMPSTE24 / FNTB pair here, where lonafarnib's label covers
    processing-deficient laminopathies and both records cite the same NCT.

    What it may not be is nothing at all.
    """
    if ev["evidence_class"] != "approved-for-this-indication":
        pytest.skip("not an approval claim")

    # Checked by naming, not by keyword. An earlier version of this looked for
    # the word "approved" in a trial note and failed ZMPSTE24, whose note says
    # "the lonafarnib marketing record explicitly covers ZMPSTE24 progeroid
    # laminopathies" -- traceable to a reader, invisible to the match. What
    # matters is that a drug the panel knows about is named somewhere reachable.
    known_drugs = {d["name"].lower()
                   for record in EVIDENCE.values()
                   for d in record.get("drugs") or []}

    named_here = {d["name"].lower() for d in ev.get("drugs") or []}
    named_in_a_trial_note = {
        drug for drug in known_drugs
        for t in ev.get("trials") or []
        if drug in (t.get("note") or "").lower()}

    assert named_here or named_in_a_trial_note, (
        f"{symbol} claims approval but no approved drug is named in the record or "
        "in any of its trial notes. A reader cannot tell what was approved.")


@pytest.mark.parametrize("symbol,ev", _records())
def test_a_human_therapeutic_claim_is_backed_by_a_trial_or_a_citation(symbol, ev):
    """Saying a drug reached humans requires a trial record or a quoted source."""
    if ev["evidence_class"] not in HUMAN_THERAPEUTIC:
        pytest.skip("no human therapeutic claim")
    assert ev.get("trials") or ev.get("claims"), \
        f"{symbol} claims human therapeutic evidence with neither a trial nor a citation"


@pytest.mark.parametrize("symbol,ev", _records())
def test_no_therapeutic_means_no_drug_is_listed(symbol, ev):
    """The one class that can be falsified by its own record.

    'no-therapeutic' says no drug has been given to a human for this target. A
    drug in the same record contradicts that outright — and under-claiming here
    is not conservative, it is wrong in the direction that hides existing
    treatment from someone reading the panel.
    """
    if ev["evidence_class"] != "no-therapeutic":
        pytest.skip("not a no-therapeutic record")
    assert not ev.get("drugs"), \
        f"{symbol} is labelled no-therapeutic but lists drugs: {ev.get('drugs')}"


@pytest.mark.parametrize("symbol,ev", _records())
def test_a_trial_under_model_organism_only_explains_why_it_does_not_count(symbol, ev):
    """A registered trial is not the same as human therapeutic evidence.

    My first version of this rule forbade trials here outright, and the data was
    right and the rule was wrong. These records list trials that exist and then
    say why each one does not support the longevity claim: navitoclax is
    oncology and "none is a senolytic aging trial"; the IGF1R trial is IGF-1
    REPLACEMENT, the opposite direction to the hypothesis; the WRN helicase
    inhibitor is for MSI-high cancer, not Werner syndrome.

    That distinction is the whole value of the field, so what is enforced is
    that it is drawn: a trial sitting under this class without a note is a
    contradiction nobody has resolved.
    """
    if ev["evidence_class"] != "model-organism-only":
        pytest.skip("not a model-organism-only record")

    for trial in ev.get("trials") or []:
        note = (trial.get("note") or "").strip()
        assert note, (
            f"{symbol} is model-organism-only and lists {trial.get('nct_id')} with no "
            "note. Either the trial is human evidence and the class is wrong, or it "
            "is not and the record must say why.")


# --------------------------------------------------------------------------- identifiers resolve in shape

PMID = re.compile(r"^\d{1,8}$")
NCT = re.compile(r"^NCT\d{8}$")
UNIPROT = re.compile(r"^[A-NR-Z][0-9][A-Z0-9]{3}[0-9]$|^[OPQ][0-9][A-Z0-9]{3}[0-9]$")
PDB = re.compile(r"^[0-9][A-Za-z0-9]{3}$")


@pytest.mark.parametrize("symbol,ev", _records())
def test_every_claim_has_a_pmid_and_a_verbatim_quote(symbol, ev):
    """A claim with no quote cannot be checked, which makes it an opinion."""
    for claim in ev.get("claims") or []:
        assert PMID.match(str(claim.get("pmid", ""))), \
            f"{symbol}: claim has a malformed PMID {claim.get('pmid')!r}"
        assert (claim.get("quote") or "").strip(), \
            f"{symbol}: claim on PMID {claim.get('pmid')} has no quote to check"


@pytest.mark.parametrize("symbol,ev", _records())
def test_failed_claims_are_also_quoted(symbol, ev):
    """The negative results carry the most weight, so they get the same bar."""
    for failed in ev.get("failed_claims") or []:
        assert PMID.match(str(failed.get("pmid", ""))), \
            f"{symbol}: failed_claim has a malformed PMID {failed.get('pmid')!r}"
        assert (failed.get("quote") or "").strip(), \
            f"{symbol}: a failed_claim carries no quote"


@pytest.mark.parametrize("symbol,ev", _records())
def test_trial_identifiers_are_well_formed(symbol, ev):
    for trial in ev.get("trials") or []:
        assert NCT.match(trial.get("nct_id", "")), \
            f"{symbol}: malformed NCT id {trial.get('nct_id')!r}"
        assert isinstance(trial.get("pediatric_enrollment"), bool), \
            f"{symbol}: {trial.get('nct_id')} does not state pediatric enrollment as a boolean"


@pytest.mark.parametrize("symbol,ev", _records())
def test_structure_identifiers_are_well_formed(symbol, ev):
    assert UNIPROT.match(ev["uniprot"]), f"{symbol}: malformed UniProt {ev['uniprot']!r}"
    for pdb in ev.get("pdb_ids") or []:
        assert PDB.match(pdb), f"{symbol}: malformed PDB id {pdb!r}"


@pytest.mark.parametrize("symbol,ev", _records())
def test_a_ligand_count_names_the_target_it_was_counted_against(symbol, ev):
    """Potency counts are meaningless without the ChEMBL target they came from.

    This record set documents a case where counting against the subunit rather
    than the complex understated tractability roughly 360-fold, which is exactly
    why the target id has to travel with the number.
    """
    if not ev.get("potent_ligands"):
        pytest.skip("no ligand count")
    assert ev.get("chembl_target"), \
        f"{symbol} reports {ev['potent_ligands']} potent ligands with no chembl_target"


# --------------------------------------------------------------------------- the summary is computed

def test_summary_counts_match_the_underlying_data():
    """summary() claims to be computed rather than asserted. Verify that."""
    got = lp.summary()

    assert got["targets"] == len(TARGETS)
    assert sum(got["by_arm"].values()) == len(EVIDENCE)
    assert sum(got["by_evidence_class"].values()) == len(EVIDENCE)
    assert got["trials"] == sum(len(ev["trials"]) for ev in EVIDENCE.values())
    assert got["claims"] == sum(len(ev["claims"]) for ev in EVIDENCE.values())
    assert got["failed_claims"] == len(lp.failed_claims())


def test_pediatric_counts_agree_with_the_records():
    got = lp.summary()
    expected = sum(1 for ev in EVIDENCE.values()
                   for t in ev["trials"] if t["pediatric_enrollment"])

    assert got["pediatric_trials"] == expected
    assert got["pediatric_onset"] == len(lp.pediatric_targets())


def test_failed_claims_are_surfaced_not_buried():
    """Recorded contradictions must reach the reporting path, or why record them."""
    failed = lp.failed_claims()
    assert failed, "no failed claims are surfaced; the negative results are the point"
    for item in failed:
        assert item["symbol"] in EVIDENCE
        assert item["arm"] in {"progeroid-pediatric", "geroscience-adult"}


def test_targets_with_human_evidence_does_not_include_weaker_classes():
    """The helper a caller trusts to filter must not leak model-organism data."""
    for symbol in lp.targets_with_human_evidence():
        assert EVIDENCE[symbol]["evidence_class"] in HUMAN_THERAPEUTIC, \
            f"{symbol} is reported as human evidence but is " \
            f"{EVIDENCE[symbol]['evidence_class']}"


def test_every_arm_filter_returns_only_that_arm():
    for arm in ("progeroid-pediatric", "geroscience-adult"):
        for target in lp.targets_by_arm(arm):
            assert EVIDENCE[target["symbol"]]["arm"] == arm
