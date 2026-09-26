"""An authorship claim must stay welded to the record it was made about.

The only interesting attack on a signed attestation is detachment: take a
genuine claim someone made about record A and present it as a claim about
record B. Every other failure is a variant of that -- prose and metadata
disagreeing, two roots in one message, a claim bundled with a manifest it was
never about.

So most of this file is that attack, from several angles. The happy path gets
one test, because it is the part that would pass by accident.
"""
import pytest

import attestation as att
import siwe
from test_siwe import ADDRESS, CHAIN_ID, DOMAIN, PRIVATE_KEY, URI, sign

ROOT_A = "0x" + "aa" * 32
ROOT_B = "0x" + "bb" * 32


@pytest.fixture(autouse=True)
def _clean_nonces():
    siwe.reset_nonces()
    yield
    siwe.reset_nonces()


def _attest(root=ROOT_A, role="author", label=None, **overrides):
    message = att.build_attestation(
        root=root, address=ADDRESS, domain=DOMAIN, uri=URI, chain_id=CHAIN_ID,
        role=role, label=label, **overrides)
    return message, "0x" + sign(siwe.eip191_hash(message), PRIVATE_KEY).hex()


# --------------------------------------------------------------------------- it works

def test_a_signed_claim_verifies_against_its_own_record():
    message, signature = _attest()
    out = att.verify_attestation(message, signature, expected_root=ROOT_A,
                                 expected_domain=DOMAIN)

    assert out["ok"] is True
    assert out["signer"] == ADDRESS
    assert out["merkle_root"] == ROOT_A
    assert out["role"] == "author"
    assert ADDRESS in out["claim"] and ROOT_A in out["claim"]


# --------------------------------------------------------------------------- detachment

def test_a_claim_about_one_record_does_not_verify_against_another():
    """The attack: reuse a genuine attestation on a different record."""
    message, signature = _attest(root=ROOT_A)

    out = att.verify_attestation(message, signature, expected_root=ROOT_B,
                                 expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "different record" in out["reason"]
    assert out["signed_root"] == ROOT_A      # says what it WAS for


def test_swapping_the_root_in_the_message_breaks_the_signature():
    """Editing the record reference invalidates the whole thing, as it must."""
    message, signature = _attest(root=ROOT_A)
    tampered = message.replace(ROOT_A, ROOT_B)

    out = att.verify_attestation(tampered, signature, expected_root=ROOT_B,
                                 expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "does not match the address" in out["reason"] or "bad signature" in out["reason"]


def test_prose_and_metadata_must_agree_on_the_root():
    """A message that showed the human one root and the verifier another.

    Only the Resources line is rewritten here, so the statement the wallet
    displayed still names ROOT_A. Such a message is refused outright rather than
    resolved in favour of either field.
    """
    nonce = siwe.issue_nonce()
    message = att.build_attestation(root=ROOT_A, address=ADDRESS, domain=DOMAIN,
                                    uri=URI, chain_id=CHAIN_ID, nonce=nonce)
    forged = message.replace(f"- {att.ROOT_RESOURCE}{ROOT_A}",
                             f"- {att.ROOT_RESOURCE}{ROOT_B}")
    signature = "0x" + sign(siwe.eip191_hash(forged), PRIVATE_KEY).hex()

    out = att.verify_attestation(forged, signature, expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "does not appear in the signed statement" in out["reason"]


def test_two_roots_in_one_message_is_refused():
    """Ambiguity is not resolved by picking the first one."""
    nonce = siwe.issue_nonce()
    message = att.build_attestation(root=ROOT_A, address=ADDRESS, domain=DOMAIN,
                                    uri=URI, chain_id=CHAIN_ID, nonce=nonce)
    forged = message.replace(f"- {att.ROOT_RESOURCE}{ROOT_A}",
                             f"- {att.ROOT_RESOURCE}{ROOT_A}\n"
                             f"- {att.ROOT_RESOURCE}{ROOT_B}")
    signature = "0x" + sign(siwe.eip191_hash(forged), PRIVATE_KEY).hex()

    out = att.verify_attestation(forged, signature, expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "exactly one" in out["reason"]


# --------------------------------------------------------------------------- inherited protections

def test_an_attestation_replays_no_better_than_a_login():
    """It is built on siwe, so the nonce rule applies without being restated."""
    message, signature = _attest()
    assert att.verify_attestation(message, signature, expected_domain=DOMAIN)["ok"] is True

    replay = att.verify_attestation(message, signature, expected_domain=DOMAIN)
    assert replay["ok"] is False
    assert "already used" in replay["reason"]


def test_an_attestation_signed_for_another_domain_is_rejected():
    nonce = siwe.issue_nonce()
    message = att.build_attestation(root=ROOT_A, address=ADDRESS, domain="evil.example",
                                    uri=URI, chain_id=CHAIN_ID, nonce=nonce)
    signature = "0x" + sign(siwe.eip191_hash(message), PRIVATE_KEY).hex()

    out = att.verify_attestation(message, signature, expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "wrong domain" in out["reason"]


# --------------------------------------------------------------------------- roles and shape

@pytest.mark.parametrize("role", att.ROLES)
def test_every_declared_role_round_trips(role):
    message, signature = _attest(role=role)
    out = att.verify_attestation(message, signature, expected_root=ROOT_A,
                                 expected_domain=DOMAIN)
    assert out["ok"] is True
    assert out["role"] == role


def test_an_unknown_role_is_refused_at_build_time():
    """Fail where the mistake is, not three steps later at verification."""
    with pytest.raises(ValueError, match="unknown role"):
        att.build_attestation(root=ROOT_A, address=ADDRESS, domain=DOMAIN,
                              uri=URI, chain_id=CHAIN_ID, role="owner")


@pytest.mark.parametrize("bad", ["0x1234", "", "0x" + "zz" * 32, "0x" + "aa" * 31])
def test_a_malformed_root_is_refused(bad):
    with pytest.raises(ValueError):
        att.build_attestation(root=bad, address=ADDRESS, domain=DOMAIN,
                              uri=URI, chain_id=CHAIN_ID)


def test_the_statement_is_readable_and_disclaims_a_transaction():
    """What the wallet renders is the only thing most signers will read."""
    statement = att.statement_for(ROOT_A, "author", label="bcl2-run-1")

    assert "I claim the role of author" in statement
    assert ROOT_A in statement
    assert 'labelled "bcl2-run-1"' in statement
    assert "not a transaction" in statement
    assert "puts nothing on a chain" in statement


def test_a_result_never_claims_more_than_a_signature_can_prove():
    message, signature = _attest()
    out = att.verify_attestation(message, signature, expected_root=ROOT_A,
                                 expected_domain=DOMAIN)

    assert "not evidence that the claim is true" in out["role_caveat"]
    assert "does not replace anchoring" in out["relation_to_anchor"]
    assert out["interop_verified"] is False


# --------------------------------------------------------------------------- bundling

def test_only_claims_about_this_record_are_bundled(tmp_path, monkeypatch):
    """A bundle whose contents were not all checked is worse than none at all."""
    monkeypatch.setenv("AGI_CONTENT_STORE", str(tmp_path))
    import content_store

    manifest = content_store.manifest({"r.json": {"score": -9.4}}, label="run")
    root = "0x" + manifest["merkle_root"].removeprefix("0x")

    mine, sig = _attest(root=root)
    good = att.verify_attestation(mine, sig, expected_root=root, expected_domain=DOMAIN)

    other, other_sig = _attest(root=ROOT_B)
    elsewhere = att.verify_attestation(other, other_sig, expected_domain=DOMAIN)

    bundle = att.attach(manifest, [good, elsewhere])

    assert len(bundle["attestations"]) == 1
    assert bundle["attestations"][0]["signer"] == ADDRESS
    assert len(bundle["rejected"]) == 1
    assert "claims by keyholders, not verified facts" in bundle["note"]


def test_an_empty_bundle_says_so_rather_than_looking_endorsed():
    bundle = att.attach({"merkle_root": ROOT_A}, [])
    assert bundle["attestations"] == []
    assert "No attestation verified" in bundle["note"]


def test_bundling_requires_a_manifest_with_a_root():
    with pytest.raises(ValueError, match="no merkle_root"):
        att.attach({"label": "run"}, [])
