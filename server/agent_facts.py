"""NANDA AgentFacts: a verifiable description of what this node offers.

An agent that another agent can find, but cannot check, is worse than one it
cannot find: discovery without verification is a directory of unfalsifiable
claims. NANDA's answer is AgentFacts -- structured metadata naming an agent's
capabilities, endpoints, security requirements and verification status, signed
so a resolver can check who asserted it.

This module builds this node's facts and verifies anyone else's. It closes a
loop with the rest of the repo:

    mcp_server.py   what tools exist          -> capabilities
    x402.py         what they cost            -> pricing
    siwe.py         who is asserting this     -> signature
    chain_anchor.py what the results mean     -> provenance policy

The honesty rule here is `verification`. A facts document is a CLAIM by whoever
signed it. A valid signature proves the claim was made by a keyholder; it proves
nothing about whether the agent can do what it says. So `verification.status` is
never set to anything stronger than what was actually checked, and
build_facts() cannot be made to emit "verified" -- there is no parameter for it.
An agent asserting its own excellence is the default state of every directory
that has ever existed, and treating a self-signed claim as endorsement is how
they all became useless.

Signing follows the same boundary as everything else here: build_facts()
produces an unsigned document plus the exact bytes to sign, and a person or
their wallet signs it. This module holds no key.
"""
import datetime as _dt
import json

import keccak
import siwe

SCHEMA_VERSION = "1.0"
FACTS_VERSION = "0.3"          # NANDA AgentFacts draft this follows

#: What a verification status is allowed to say, weakest first. Anything
#: stronger than "self_asserted" must come from a party that is not the subject.
VERIFICATION_LEVELS = ("unverified", "self_asserted", "third_party_attested")

SELF_ASSERTION_CAVEAT = (
    "SELF-ASSERTED. These facts were signed by the agent's own operator. A valid "
    "signature proves who made the claim, not that the claim is true, and not that "
    "any capability listed here works. Treat as a directory entry, not an endorsement.")

PROVENANCE_POLICY = (
    "Results from this node carry a 'provenance' field and placeholder values print "
    "with a [SYNTHETIC] marker. A caller that strips those markers is misrepresenting "
    "this node's output, whatever this document says.")


def canonical(facts) -> bytes:
    """Canonical JSON bytes for hashing: sorted keys, no incidental whitespace.

    The signature covers this encoding, so two documents that differ only in key
    order or spacing must not produce two different digests -- otherwise a
    re-serialised copy of a signed document stops verifying for no reason.
    """
    return json.dumps(_without_signature(facts), sort_keys=True,
                      separators=(",", ":")).encode()


def _without_signature(facts):
    """Facts minus its own signature block, which cannot cover itself."""
    return {k: v for k, v in facts.items() if k != "signature"}


def facts_digest(facts) -> str:
    return keccak.keccak256_hex(canonical(facts))


def build_facts(name, description, provider_address, endpoints, capabilities,
                pricing=None, ttl_seconds=3600, issued_at=None, chain_id=None):
    """Describe this node. Returns the unsigned document and what to sign.

    `provider_address` is the address expected to sign. It is recorded in the
    document so verification has something to check the recovered signer
    against; a document that does not name its expected signer can be "verified"
    against whoever happens to have signed it, which verifies nothing.
    """
    issued = issued_at or _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")

    facts = {
        "schema_version": SCHEMA_VERSION,
        "agentFactsVersion": FACTS_VERSION,
        "name": name,
        "description": description,
        "provider": {"address": keccak.to_checksum_address(provider_address),
                     "chainId": chain_id},
        "endpoints": list(endpoints),
        "capabilities": list(capabilities),
        "pricing": pricing or {"model": "free",
                               "note": "No charge is advertised for these endpoints."},
        "issuedAt": issued,
        "ttlSeconds": int(ttl_seconds),
        # Always the weakest truthful value. There is deliberately no parameter
        # to raise it: an agent cannot verify itself, and a build-time flag to
        # say otherwise would be used.
        "verification": {"status": "unverified",
                         "caveat": SELF_ASSERTION_CAVEAT,
                         "attestedBy": []},
        "provenancePolicy": PROVENANCE_POLICY,
    }

    return {
        "facts": facts,
        "digest": facts_digest(facts),
        "sign_this": _message_for(facts),
        "boundary": ("This document is UNSIGNED. It holds no key and signs nothing. "
                     "Sign `sign_this` with the provider address to publish it."),
    }


def _message_for(facts) -> str:
    """The human-readable text a wallet displays when signing these facts."""
    return (
        f"Publish AgentFacts for \"{facts['name']}\".\n"
        f"Digest: {facts_digest(facts)}\n"
        f"Provider: {facts['provider']['address']}\n"
        f"Issued: {facts['issuedAt']}\n\n"
        "This signs a directory entry describing an agent. It is a signature, not a "
        "transaction: it moves no funds and grants no spending permission. It asserts "
        "these capabilities are offered; it does not prove they work.")


def sign_payload(facts):
    """The exact string to sign for a facts document, and its digest."""
    return {"message": _message_for(facts), "digest": facts_digest(facts)}


def attach_signature(facts, signature):
    """Return a published copy of `facts` carrying its signature."""
    published = dict(facts)
    published["signature"] = {
        "algorithm": "eip191-personal-sign",
        "value": signature,
        "digest": facts_digest(facts),
    }
    return published


def _result(ok, reason=None, **extra):
    return {"schema_version": SCHEMA_VERSION, "ok": ok, "reason": reason,
            "interop_verified": False, **extra}


def verify_facts(published, now=None):
    """Check a signed AgentFacts document. Returns a result dict; never raises.

    Success means: this document was signed by the address it names as its
    provider, and has not expired. It does NOT mean the agent works, and the
    result says so in `means` rather than leaving the caller to infer it.
    """
    now = now or _dt.datetime.now(_dt.timezone.utc)

    if not isinstance(published, dict):
        return _result(False, "facts must be a JSON object")

    signature_block = published.get("signature")
    if not isinstance(signature_block, dict) or not signature_block.get("value"):
        return _result(False, "facts carry no signature")

    facts = _without_signature(published)
    provider = (facts.get("provider") or {}).get("address")
    if not provider:
        return _result(False, "facts do not name a provider address to check against")

    # The digest recorded alongside the signature must match what the document
    # actually hashes to now. A mismatch means the body was edited after signing.
    digest = facts_digest(facts)
    if signature_block.get("digest") and signature_block["digest"] != digest:
        return _result(False, "document has been modified since it was signed",
                       expected_digest=signature_block["digest"], actual_digest=digest)

    try:
        signer = siwe.recover_signer(_message_for(facts), signature_block["value"])
    except ValueError as exc:
        return _result(False, f"bad signature: {exc}")

    try:
        expected = keccak.to_checksum_address(provider)
    except ValueError:
        return _result(False, f"provider address is not an address: {provider!r}")

    if signer != expected:
        return _result(False, "signed by someone other than the named provider",
                       signer=signer, provider=expected)

    issued = _parse_time(facts.get("issuedAt"))
    if issued is None:
        return _result(False, "facts have no usable issuedAt", signer=signer)

    ttl = facts.get("ttlSeconds") or 0
    age = (now - issued).total_seconds()
    if ttl and age > ttl:
        return _result(False, f"facts expired {int(age - ttl)}s ago (ttl {ttl}s)",
                       signer=signer)
    if age < -60:
        return _result(False, "facts are issued in the future", signer=signer)

    status = (facts.get("verification") or {}).get("status")
    if status not in VERIFICATION_LEVELS:
        return _result(False, f"unknown verification status {status!r}", signer=signer)

    # A document may not claim third-party attestation with nobody named.
    attested_by = (facts.get("verification") or {}).get("attestedBy") or []
    if status == "third_party_attested" and not attested_by:
        return _result(False, "claims third-party attestation but names no attestor",
                       signer=signer)

    return _result(
        True, None, signer=signer, name=facts.get("name"), digest=digest,
        capabilities=facts.get("capabilities", []),
        endpoints=facts.get("endpoints", []),
        verification_status=status, attested_by=attested_by,
        means=("This document was signed by the provider it names and has not expired. "
               "It does NOT establish that the agent can do what it claims."),
        caveat=SELF_ASSERTION_CAVEAT if status != "third_party_attested" else None)


def _parse_time(text):
    if not text:
        return None
    try:
        parsed = _dt.datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=_dt.timezone.utc)


# --------------------------------------------------------------------------- this node

def facts_for_this_node(provider_address, base_url, tools, price=None, chain_id=None):
    """AgentFacts describing this deployment, built from its live tool list.

    Data-driven on the tools the MCP server actually advertises, so a document
    cannot drift into describing capabilities that were removed -- the usual way
    a directory entry becomes a lie without anyone lying.
    """
    capabilities = [{"name": t.get("name"), "description": t.get("description", "")}
                    for t in tools if t.get("name")]

    pricing = {"model": "free", "note": "No charge is advertised for these endpoints."}
    if price:
        pricing = {"model": "x402", "scheme": "exact",
                   "amount": price.get("amount"), "asset": price.get("asset"),
                   "network": price.get("network"), "payTo": price.get("payTo"),
                   "note": "Priced per call over HTTP 402. Settlement is not "
                           "confirmed by this node; see server/x402.py."}

    return build_facts(
        name="agi-bioxr",
        description=("Molecular research workspace: structure retrieval, docking, MD, "
                     "ADMET and screening, with content-addressed provenance and "
                     "optional on-chain anchoring."),
        provider_address=provider_address,
        endpoints=[{"protocol": "mcp", "transport": "stdio"},
                   {"protocol": "http", "url": base_url}],
        capabilities=capabilities, pricing=pricing, chain_id=chain_id)
