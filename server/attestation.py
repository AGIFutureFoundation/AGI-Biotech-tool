"""Signed authorship claims over a research record.

Two things already exist and do not touch each other. siwe.py proves who is at
the keyboard. chain_anchor.py proves a record existed and has not changed. That
leaves the claim nobody was making: *this person asserts authorship of that
record*.

An attestation is that claim, and it is deliberately off-chain. It costs
nothing, needs no gas, can be produced for every run rather than the few worth
a transaction, and can be revoked by simply not republishing it. The anchor is
the expensive, permanent half; this is the cheap, retractable half, and most
records only ever need this one.

The claim is bound to an exact Merkle root. Re-signing a different record
produces a different message and therefore a different signature, so an
attestation cannot be detached from what it was made about and re-attached to
something else -- which is the only interesting attack on a scheme like this.

WHAT A VALID ATTESTATION MEANS: the holder of this key said this sentence about
this root, at a time they stated.

WHAT IT DOES NOT MEAN: that the work is correct, that the signer did it, or that
they had the right to claim it. A key is not a person and authorship is not
truth. verify() returns the claim; believing it is a separate decision, and
ROLE_CAVEAT says so on every record.

Reuses siwe's message construction and signature recovery rather than defining
a second signing scheme, because a parallel scheme is a second place for the
replay and malleability rules to be got wrong.
"""
import datetime as _dt

import keccak
import siwe

SCHEMA_VERSION = "1.0"

#: Prefix for the resource line that carries the root, so a verifier can find
#: it without parsing prose.
ROOT_RESOURCE = "agibioxr:merkle-root:"

ROLES = ("author", "contributor", "reviewer", "custodian")

ROLE_CAVEAT = (
    "An attestation records that the holder of this key made this claim. It is not "
    "evidence that the claim is true, that the work is correct, or that the signer "
    "performed it. Authorship disputes are not resolved by signatures.")

RELATION_TO_ANCHOR = (
    "This is an off-chain claim. It costs nothing and can be withdrawn by not "
    "republishing it. It does NOT put anything on a chain and does not replace "
    "anchoring: the anchor timestamps the record, this says who claims it.")


def _normalise_root(root) -> str:
    raw = str(root).lower().removeprefix("0x")
    if len(raw) != 64 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError(
            f"a Merkle root must be 32 bytes of hex (64 chars); got {len(raw)}: {root!r}")
    return "0x" + raw


def statement_for(root, role, label=None):
    """The sentence the wallet shows. It has to be readable, because it is read."""
    what = f"the research record with Merkle root {_normalise_root(root)}"
    if label:
        what += f' (labelled "{label}")'
    return (f"I claim the role of {role} for {what}. "
            "This is a signature, not a transaction: it moves no funds, grants no "
            "spending permission, and puts nothing on a chain.")


def build_attestation(root, address, domain, uri, chain_id, nonce=None,
                      role="author", label=None, issued_at=None):
    """Render the message a wallet will display and sign.

    The root appears twice on purpose: in the statement, where a person reads
    it, and in Resources, where a verifier parses it. They are checked against
    each other at verification, so a message whose prose and machine-readable
    field disagree is refused rather than silently resolved in favour of one.
    """
    if role not in ROLES:
        raise ValueError(f"unknown role {role!r}; expected one of {ROLES}")

    root = _normalise_root(root)
    resources = [f"{ROOT_RESOURCE}{root}", f"agibioxr:role:{role}"]
    if label:
        resources.append(f"agibioxr:label:{label}")

    return siwe.build_message(
        domain=domain, address=address, uri=uri, chain_id=chain_id,
        nonce=nonce or siwe.issue_nonce(),
        statement=statement_for(root, role, label),
        issued_at=issued_at, resources=resources)


def _statement_of(message) -> str:
    """The prose block a wallet renders: after the address, before the fields.

    Isolated deliberately. Checking a claim against the whole message would
    match text the signer never saw as a sentence -- including the very
    Resources line the check exists to cross-examine.
    """
    lines = message.split("\n")
    body = []
    for line in lines[3:]:                 # domain line, address, blank
        if line.startswith("URI: "):
            break
        body.append(line)
    return "\n".join(body).strip()


def _result(ok, reason=None, **extra):
    return {"schema_version": SCHEMA_VERSION, "ok": ok, "reason": reason,
            "role_caveat": ROLE_CAVEAT, "relation_to_anchor": RELATION_TO_ANCHOR,
            "interop_verified": False, **extra}


def verify_attestation(message, signature, expected_root=None,
                       expected_domain=None, expected_chain_id=None, now=None):
    """Check an authorship claim. Returns a result dict; never raises.

    `expected_root` is what the CALLER is asking about. Leaving it out verifies
    that the message is internally consistent and correctly signed, but not that
    it concerns the record you have in your hand -- which is almost never what
    you want, so it is worth passing.
    """
    base = siwe.verify(message, signature, expected_domain=expected_domain,
                       expected_chain_id=expected_chain_id, now=now)
    if not base["ok"]:
        return _result(False, base["reason"], signer=base.get("signer"))

    resources = base.get("resources") or []
    roots = [r[len(ROOT_RESOURCE):] for r in resources if r.startswith(ROOT_RESOURCE)]
    if len(roots) != 1:
        return _result(False,
                       f"expected exactly one {ROOT_RESOURCE} resource, found {len(roots)}",
                       signer=base["signer"])

    try:
        signed_root = _normalise_root(roots[0])
    except ValueError as exc:
        return _result(False, f"malformed root in resources: {exc}", signer=base["signer"])

    # The prose and the machine-readable field must agree. A message where they
    # differ showed the human one thing and the verifier another.
    #
    # This must look at the STATEMENT, not the whole message: the Resources line
    # is itself part of the message, so `signed_root in message` is trivially
    # true for any root an attacker writes there and checks nothing at all.
    if signed_root not in _statement_of(message):
        return _result(False, "root in Resources does not appear in the signed statement",
                       signer=base["signer"])

    if expected_root is not None:
        try:
            wanted = _normalise_root(expected_root)
        except ValueError as exc:
            return _result(False, f"expected_root is not a root: {exc}", signer=base["signer"])
        if wanted != signed_root:
            return _result(False,
                           "attestation is for a different record "
                           f"({signed_root}), not {wanted}",
                           signer=base["signer"], signed_root=signed_root)

    roles = [r[len("agibioxr:role:"):] for r in resources
             if r.startswith("agibioxr:role:")]
    role = roles[0] if len(roles) == 1 else None
    if role not in ROLES:
        return _result(False, f"missing or unknown role: {roles}", signer=base["signer"])

    return _result(True, None, signer=base["signer"], merkle_root=signed_root,
                   role=role, domain=base.get("domain"), chain_id=base.get("chain_id"),
                   issued_at=base.get("issued_at"),
                   claim=f"{base['signer']} claims to be {role} of {signed_root}")


def attach(manifest, attestations):
    """Bundle verified attestations with the manifest they concern.

    Only claims that verified against THIS manifest's root are attached. An
    attestation for another record is dropped and named in `rejected`, never
    quietly included -- a bundle whose contents were not all checked is worse
    than no bundle, because it looks checked.
    """
    root = manifest.get("merkle_root")
    if not root:
        raise ValueError("manifest has no merkle_root")
    root = _normalise_root(root)

    kept, rejected = [], []
    for item in attestations:
        if item.get("ok") and item.get("merkle_root") == root:
            kept.append({"signer": item["signer"], "role": item["role"],
                         "issued_at": item.get("issued_at")})
        else:
            rejected.append({"signer": item.get("signer"),
                             "reason": item.get("reason") or "root mismatch"})

    return {
        "schema_version": SCHEMA_VERSION,
        "merkle_root": root,
        "bundled_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "attestations": kept,
        "rejected": rejected,
        "role_caveat": ROLE_CAVEAT,
        "relation_to_anchor": RELATION_TO_ANCHOR,
        "note": ("Attestations are claims by keyholders, not verified facts about "
                 "who did the work." if kept else
                 "No attestation verified against this record."),
    }
