"""A directory entry that cannot be checked is worse than no directory.

AgentFacts exist so one agent can find another AND verify who described it. The
failure mode is not a crash; it is a document that looks verified while
asserting whatever its author wanted. Three ways that happens:

  the body is edited after signing and the signature still passes,
  somebody other than the named provider signs it,
  the document claims a verification level nobody granted it.

Each has a test. The last is the one that matters most, because it is the one
that degrades gracefully into uselessness: every directory that ever treated
self-assertion as endorsement ended up full of agents claiming excellence.
"""
import datetime as _dt

import pytest

import agent_facts as af
import siwe
from test_siwe import ADDRESS, PRIVATE_KEY, sign


@pytest.fixture(autouse=True)
def _clean_nonces():
    siwe.reset_nonces()
    yield
    siwe.reset_nonces()


TOOLS = [{"name": "dock", "description": "Dock a ligand"},
         {"name": "fetch_structure", "description": "Fetch a PDB entry"}]


def _built(**kw):
    return af.facts_for_this_node(
        provider_address=ADDRESS, base_url="https://biodao.blockchain",
        tools=TOOLS, **kw)


def _published(facts=None):
    facts = facts or _built()["facts"]
    signature = "0x" + sign(siwe.eip191_hash(af._message_for(facts)), PRIVATE_KEY).hex()
    return af.attach_signature(facts, signature)


# --------------------------------------------------------------------------- it works

def test_a_signed_document_verifies():
    out = af.verify_facts(_published())

    assert out["ok"] is True
    assert out["signer"] == ADDRESS
    assert out["name"] == "agi-bioxr"
    assert {c["name"] for c in out["capabilities"]} == {"dock", "fetch_structure"}


def test_verification_says_what_it_does_not_establish():
    out = af.verify_facts(_published())
    assert "does NOT establish that the agent can do what it claims" in out["means"]


# --------------------------------------------------------------------------- tampering

def test_editing_the_body_after_signing_is_detected():
    """The attack: sign a modest document, then publish a grander one."""
    published = _published()
    published["description"] = "Clinically validated drug discovery platform"

    out = af.verify_facts(published)
    assert out["ok"] is False
    assert "modified since it was signed" in out["reason"]


def test_adding_a_capability_after_signing_is_detected():
    published = _published()
    published["capabilities"].append({"name": "cure_cancer", "description": "yes"})

    assert af.verify_facts(published)["ok"] is False


def test_a_document_signed_by_someone_else_is_rejected():
    """A valid signature by the wrong key is the subtlest version of this."""
    facts = _built()["facts"]
    facts["provider"]["address"] = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
    signature = "0x" + sign(siwe.eip191_hash(af._message_for(facts)), PRIVATE_KEY).hex()

    out = af.verify_facts(af.attach_signature(facts, signature))
    assert out["ok"] is False
    assert "someone other than the named provider" in out["reason"]


def test_an_unsigned_document_is_not_verified():
    assert af.verify_facts(_built()["facts"])["ok"] is False


@pytest.mark.parametrize("junk", [None, "string", 42, [], {}, {"signature": {}}])
def test_hostile_input_never_raises(junk):
    out = af.verify_facts(junk)
    assert out["ok"] is False
    assert out["reason"]


# --------------------------------------------------------------------------- self-assertion

def test_a_freshly_built_document_is_unverified():
    """The weakest truthful value, always."""
    facts = _built()["facts"]
    assert facts["verification"]["status"] == "unverified"
    assert "SELF-ASSERTED" in facts["verification"]["caveat"]


def test_there_is_no_way_to_build_a_verified_document():
    """No parameter can raise the status, because such a parameter would be used."""
    import inspect
    params = inspect.signature(af.build_facts).parameters
    for name in params:
        assert "verif" not in name.lower(), f"build_facts exposes {name!r}"
    assert af.facts_for_this_node.__doc__


def test_claiming_third_party_attestation_with_no_attestor_is_rejected():
    """The loophole: assert the strongest level and name nobody."""
    facts = _built()["facts"]
    facts["verification"] = {"status": "third_party_attested", "attestedBy": [],
                             "caveat": ""}
    signature = "0x" + sign(siwe.eip191_hash(af._message_for(facts)), PRIVATE_KEY).hex()

    out = af.verify_facts(af.attach_signature(facts, signature))
    assert out["ok"] is False
    assert "names no attestor" in out["reason"]


def test_an_unknown_verification_status_is_rejected():
    facts = _built()["facts"]
    facts["verification"]["status"] = "gold_standard"
    signature = "0x" + sign(siwe.eip191_hash(af._message_for(facts)), PRIVATE_KEY).hex()

    out = af.verify_facts(af.attach_signature(facts, signature))
    assert out["ok"] is False
    assert "unknown verification status" in out["reason"]


def test_a_self_signed_document_still_carries_its_caveat():
    out = af.verify_facts(_published())
    assert "SELF-ASSERTED" in out["caveat"]


# --------------------------------------------------------------------------- freshness

def test_expired_facts_are_rejected():
    stale = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=2))
    built = af.build_facts(name="x", description="d", provider_address=ADDRESS,
                           endpoints=[], capabilities=[], ttl_seconds=60,
                           issued_at=stale.isoformat(timespec="seconds"))
    out = af.verify_facts(_published(built["facts"]))

    assert out["ok"] is False
    assert "expired" in out["reason"]


def test_facts_issued_in_the_future_are_rejected():
    ahead = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=1))
    built = af.build_facts(name="x", description="d", provider_address=ADDRESS,
                           endpoints=[], capabilities=[],
                           issued_at=ahead.isoformat(timespec="seconds"))
    assert af.verify_facts(_published(built["facts"]))["ok"] is False


# --------------------------------------------------------------------------- canonical form

def test_key_order_does_not_change_the_digest():
    """A re-serialised copy of a signed document must still verify."""
    facts = _built()["facts"]
    reordered = dict(reversed(list(facts.items())))
    assert af.facts_digest(facts) == af.facts_digest(reordered)


def test_the_signature_block_is_not_part_of_what_it_signs():
    """A signature cannot cover itself; excluding it must be explicit."""
    facts = _built()["facts"]
    before = af.facts_digest(facts)
    assert af.facts_digest(af.attach_signature(facts, "0x" + "11" * 65)) == before


# --------------------------------------------------------------------------- wiring

def test_capabilities_are_driven_by_the_live_tool_list():
    """A document cannot drift into advertising a tool that was removed."""
    out = af.facts_for_this_node(provider_address=ADDRESS, base_url="https://x",
                                 tools=[{"name": "only_one"}])
    assert [c["name"] for c in out["facts"]["capabilities"]] == ["only_one"]


def test_pricing_defaults_to_free_and_says_so():
    assert _built()["facts"]["pricing"]["model"] == "free"


def test_x402_pricing_is_carried_with_its_settlement_caveat():
    out = _built(price={"amount": "1000000", "asset": "0xabc",
                        "network": "monad-testnet", "payTo": ADDRESS})
    pricing = out["facts"]["pricing"]

    assert pricing["model"] == "x402"
    assert "Settlement is not confirmed" in pricing["note"]


def test_the_document_states_its_provenance_policy():
    """Downstream consumers are told not to strip the SYNTHETIC markers."""
    assert "[SYNTHETIC]" in _built()["facts"]["provenancePolicy"]


def test_build_returns_the_exact_bytes_to_sign_and_holds_no_key():
    out = _built()
    assert "UNSIGNED" in out["boundary"]
    assert out["digest"] == af.facts_digest(out["facts"])
    assert "not a transaction" in out["sign_this"]
