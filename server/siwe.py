"""Sign-In with Ethereum (EIP-4361): MetaMask login, without a password.

A wallet login is a signature, not a secret. The user signs a structured
message; the server recovers which address produced it. Nothing secret crosses
the wire, and this server never sees, stores or asks for a private key.

For a DeSci record that is the point: the address that signs a research run is
the same kind of identity that anchors its Merkle root on-chain, so authorship
and provenance are one claim rather than two.

THE THREE WAYS THIS GOES WRONG, and what stops each:

  Replay -- a signature is a bearer token forever unless the nonce it covers is
  single-use. consume_nonce() removes it, so a captured signature authenticates
  exactly once. This is the failure that turns a login into a permanent skeleton
  key, and it is why nonces are issued by the server, never accepted from the
  client.

  Phishing -- a message signed for evil.example is a valid signature. It just is
  not a valid login *here*. The domain and URI are checked against what this
  server expects, not against what the message claims for itself.

  Staleness -- a signature with no expiry is good indefinitely. Expiration Time
  and Not Before are enforced when present, and issued_at is bounded by
  MAX_AGE_SECONDS regardless.

verify() returns a result object rather than raising or returning a bare bool,
because "why did this fail" is the part an operator needs at 3am, and a bool
throws it away.

NOT EXERCISED: no live MetaMask signature has been verified in this environment.
The recovery path is checked against signatures this repo generates and against
a published private-key/address pair, which proves the mathematics but not
interoperability with a real wallet's exact byte layout. Confirm with a real
sign-in before trusting it in production; verify() reports this as
`interop_verified: False`.
"""
import datetime as _dt
import os
import re
import secrets
import threading

import keccak
import secp256k1

SCHEMA_VERSION = "1.0"

#: An issued-at older than this is refused even when the message sets no
#: explicit expiry, so an unbounded signature cannot exist.
MAX_AGE_SECONDS = 600

#: How long an unused nonce stays valid before it is swept.
NONCE_TTL_SECONDS = 900

_NONCES = {}
_NONCE_LOCK = threading.Lock()


# --------------------------------------------------------------------------- addresses

def address_from_public_key(public_key) -> str:
    """Ethereum address: last 20 bytes of keccak256 over the 64-byte key."""
    digest = keccak.keccak256(secp256k1.public_key_bytes(public_key))
    return keccak.to_checksum_address("0x" + digest[-20:].hex())


def eip191_hash(message: str) -> bytes:
    """The personal_sign digest MetaMask actually signs.

    The 0x19 prefix and length are what stop a signed login being replayable as
    a signed transaction: a real transaction can never begin with this preamble.
    """
    body = message.encode()
    preamble = b"\x19Ethereum Signed Message:\n" + str(len(body)).encode()
    return keccak.keccak256(preamble + body)


def split_signature(signature):
    """65-byte hex signature -> (r, s, recovery_id).

    MetaMask sends v as 27/28; EIP-155 and some wallets send 0/1. Both are
    accepted, because rejecting a wallet's convention looks to the user like
    their account is broken.
    """
    raw = str(signature).lower().removeprefix("0x")
    if len(raw) != 130 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError("a signature must be 65 bytes of hex (130 characters)")

    data = bytes.fromhex(raw)
    r = int.from_bytes(data[0:32], "big")
    s = int.from_bytes(data[32:64], "big")
    v = data[64]

    if v >= 27:
        v -= 27
    if v not in (0, 1):
        raise ValueError(f"unsupported signature v byte: {data[64]}")

    # Reject the malleable high-s form: for every valid (r, s) there is an
    # equally valid (r, n-s), and accepting both gives one signature two
    # encodings -- enough to defeat any store keyed on the signature bytes.
    if s > secp256k1.N // 2:
        raise ValueError("non-canonical signature (high s); expected low-s form")

    return r, s, v


def recover_signer(message: str, signature) -> str:
    """Which address signed this message? Raises ValueError if none did."""
    r, s, v = split_signature(signature)
    public_key = secp256k1.recover_public_key(eip191_hash(message), r, s, v)
    if public_key is None:
        raise ValueError("signature does not recover to a valid public key")
    return address_from_public_key(public_key)


# --------------------------------------------------------------------------- nonces

def issue_nonce(ttl=NONCE_TTL_SECONDS) -> str:
    """Mint a single-use nonce. The server issues these; clients never pick them."""
    nonce = secrets.token_hex(16)
    expires = _now() + _dt.timedelta(seconds=ttl)
    with _NONCE_LOCK:
        _sweep_locked()
        _NONCES[nonce] = expires
    return nonce


def consume_nonce(nonce: str) -> bool:
    """Spend a nonce. True once, False every time after -- that is the point."""
    with _NONCE_LOCK:
        _sweep_locked()
        expires = _NONCES.pop(nonce, None)
    return expires is not None and expires > _now()


def _sweep_locked():
    now = _now()
    for key in [k for k, exp in _NONCES.items() if exp <= now]:
        _NONCES.pop(key, None)


def _now():
    return _dt.datetime.now(_dt.timezone.utc)


def reset_nonces():
    """Drop every outstanding nonce. For tests and for revoking in anger."""
    with _NONCE_LOCK:
        _NONCES.clear()


# --------------------------------------------------------------------------- the message

DEFAULT_STATEMENT = (
    "Sign in to verify authorship of research records. This signature proves you "
    "control this address. It is not a transaction, moves no funds, and grants no "
    "spending permission.")

_FIELD = re.compile(r"^([A-Za-z ]+): (.*)$")


def build_message(domain, address, uri, chain_id, nonce, statement=DEFAULT_STATEMENT,
                  issued_at=None, expiration_time=None, resources=()):
    """Render an EIP-4361 message for a wallet to display and sign."""
    address = keccak.to_checksum_address(address)
    issued_at = issued_at or _now().isoformat(timespec="seconds").replace("+00:00", "Z")

    lines = [f"{domain} wants you to sign in with your Ethereum account:", address, ""]
    if statement:
        lines += [statement, ""]
    lines += [f"URI: {uri}", "Version: 1", f"Chain ID: {chain_id}",
              f"Nonce: {nonce}", f"Issued At: {issued_at}"]
    if expiration_time:
        lines.append(f"Expiration Time: {expiration_time}")
    if resources:
        lines.append("Resources:")
        lines += [f"- {r}" for r in resources]
    return "\n".join(lines)


def parse_message(message: str) -> dict:
    """Pull the fields back out of an EIP-4361 message.

    Deliberately strict about the first two lines: they carry the domain and the
    address, and a parser that shrugs at a malformed preamble is a parser that
    can be fed something the wallet displayed differently from what it signed.
    """
    lines = message.split("\n")
    if len(lines) < 2 or "wants you to sign in with your Ethereum account:" not in lines[0]:
        raise ValueError("not an EIP-4361 message: bad first line")

    out = {"domain": lines[0].split(" wants you to sign in")[0].strip(),
           "address": lines[1].strip(), "resources": []}

    in_resources = False
    for line in lines[2:]:
        if line.strip() == "Resources:":
            in_resources = True
            continue
        if in_resources and line.startswith("- "):
            out["resources"].append(line[2:].strip())
            continue
        match = _FIELD.match(line)
        if match:
            key, value = match.group(1).strip().lower().replace(" ", "_"), match.group(2).strip()
            out[key] = value
    return out


# --------------------------------------------------------------------------- verification

def _result(ok, reason=None, **extra):
    return {"schema_version": SCHEMA_VERSION, "ok": ok, "reason": reason,
            "interop_verified": False, **extra}


def verify(message, signature, expected_domain=None, expected_chain_id=None,
           expected_uri=None, now=None):
    """Verify a sign-in. Returns a result dict; never raises on bad input.

    A failure says which check failed, because "invalid signature" and "you
    signed for the wrong site" are different problems for whoever is debugging.
    """
    now = now or _now()

    try:
        fields = parse_message(message)
    except ValueError as exc:
        return _result(False, f"malformed message: {exc}")

    try:
        signer = recover_signer(message, signature)
    except ValueError as exc:
        return _result(False, f"bad signature: {exc}")

    claimed = fields.get("address", "")
    try:
        claimed_checksum = keccak.to_checksum_address(claimed)
    except ValueError:
        return _result(False, f"message address is not an address: {claimed!r}",
                       signer=signer)

    # The signature is valid for *some* address; this asks whether it is the one
    # the message names. A mismatch means the message was rewritten after signing.
    if claimed_checksum != signer:
        return _result(False, "signature does not match the address in the message",
                       signer=signer, claimed=claimed_checksum)

    if expected_domain is not None and fields.get("domain") != expected_domain:
        return _result(False,
                       f"wrong domain: signed for {fields.get('domain')!r}, "
                       f"this server is {expected_domain!r}", signer=signer)

    if expected_uri is not None and fields.get("uri") != expected_uri:
        return _result(False, f"wrong URI: signed for {fields.get('uri')!r}", signer=signer)

    if expected_chain_id is not None and str(fields.get("chain_id")) != str(expected_chain_id):
        return _result(False,
                       f"wrong chain: signed for chain {fields.get('chain_id')}, "
                       f"expected {expected_chain_id}", signer=signer)

    expiry = _parse_time(fields.get("expiration_time"))
    if expiry and now >= expiry:
        return _result(False, "signature has expired", signer=signer)

    not_before = _parse_time(fields.get("not_before"))
    if not_before and now < not_before:
        return _result(False, "signature is not valid yet", signer=signer)

    issued_at = _parse_time(fields.get("issued_at"))
    if issued_at is None:
        return _result(False, "message has no usable Issued At", signer=signer)
    age = (now - issued_at).total_seconds()
    if age > MAX_AGE_SECONDS:
        return _result(False, f"message is {int(age)}s old; limit is {MAX_AGE_SECONDS}s",
                       signer=signer)
    if age < -60:
        return _result(False, "message is issued in the future", signer=signer)

    # Last, because it is the only check with a side effect: a nonce must not be
    # burned by a request that was going to fail anyway.
    nonce = fields.get("nonce")
    if not nonce:
        return _result(False, "message carries no nonce", signer=signer)
    if not consume_nonce(nonce):
        return _result(False, "nonce is unknown, expired, or already used",
                       signer=signer)

    return _result(True, None, signer=signer, domain=fields.get("domain"),
                   chain_id=fields.get("chain_id"), nonce=nonce,
                   issued_at=fields.get("issued_at"),
                   resources=fields.get("resources", []))


def _parse_time(text):
    if not text:
        return None
    try:
        parsed = _dt.datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=_dt.timezone.utc)
