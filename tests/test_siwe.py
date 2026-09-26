"""Wallet login: the signature must mean what the server thinks it means.

A password login fails closed -- a wrong password is simply wrong. A signature
login fails *open* in three specific ways, because a valid signature is always
valid for something:

  A captured signature replays forever unless its nonce is spent.
  A signature for another site is genuine; it is just not a login here.
  A signature with no expiry authenticates indefinitely.

Each has a test below, written as the attack rather than as the feature, since
the feature passes trivially and the attack is what the code is actually for.

The signer lives in this file, not in server/. secp256k1.py deliberately has no
signing function -- it is non-constant-time Python that must never touch a
secret -- so the only way to produce a test signature is to write one here,
where it cannot be imported by the server.
"""
import datetime as _dt

import pytest

import keccak
import secp256k1 as C
import siwe


# --------------------------------------------------------------------------- a signer, for tests only

def sign(msg_hash: bytes, private_key: int, k: int = None):
    """ECDSA over secp256k1, returning a 65-byte Ethereum signature.

    NOT FOR PRODUCTION USE and not importable from server/: `k` is caller-
    supplied or drawn from a test-grade source, and a repeated k leaks the key.
    """
    import secrets
    e = int.from_bytes(msg_hash, "big")
    while True:
        k = k or secrets.randbelow(C.N - 1) + 1
        R = C.point_mul(k, C.G)
        r = R[0] % C.N
        if r == 0:
            k = None
            continue
        s = (pow(k, C.N - 2, C.N) * (e + r * private_key)) % C.N
        if s == 0:
            k = None
            continue

        recovery_id = (R[1] & 1) | (2 if R[0] >= C.N else 0)
        if s > C.N // 2:                       # canonical low-s form
            s = C.N - s
            recovery_id ^= 1
        return (r.to_bytes(32, "big") + s.to_bytes(32, "big")
                + bytes([recovery_id + 27]))


#: The private key from the EIP-155 specification, whose address is published.
PRIVATE_KEY = 0x4646464646464646464646464646464646464646464646464646464646464646
ADDRESS = "0x9d8A62f656a8d1615C1294fd71e9CFb3E4855A4F"

DOMAIN = "biodao.blockchain"
URI = "https://biodao.blockchain/login"
CHAIN_ID = 10143            # Monad testnet, matching chain_anchor's default


@pytest.fixture(autouse=True)
def _clean_nonces():
    siwe.reset_nonces()
    yield
    siwe.reset_nonces()


def _signed(**overrides):
    """A valid, freshly-nonced sign-in, unless a test overrides part of it."""
    params = {"domain": DOMAIN, "address": ADDRESS, "uri": URI,
              "chain_id": CHAIN_ID, "nonce": siwe.issue_nonce()}
    params.update(overrides)
    message = siwe.build_message(**params)
    return message, "0x" + sign(siwe.eip191_hash(message), PRIVATE_KEY).hex()


# --------------------------------------------------------------------------- the maths

def test_address_derivation_matches_the_published_vector():
    """Pins point_mul -> key encoding -> keccak -> EIP-55 against an external source."""
    assert siwe.address_from_public_key(C.point_mul(PRIVATE_KEY, C.G)) == ADDRESS


def test_a_signature_recovers_to_the_signing_address():
    message, signature = _signed()
    assert siwe.recover_signer(message, signature) == ADDRESS


def test_recovery_survives_many_different_nonces():
    """Different k each time exercises both recovery ids, not just the lucky one."""
    seen = set()
    for _ in range(12):
        message, signature = _signed()
        assert siwe.recover_signer(message, signature) == ADDRESS
        seen.add(bytes.fromhex(signature[2:])[64])
    assert len(seen) == 2, f"only recovery id(s) {seen} exercised; expected both"


def test_the_eip191_prefix_is_applied():
    """Without the 0x19 preamble a login signature could be replayed as a tx."""
    body = b"hello"
    expected = keccak.keccak256(b"\x19Ethereum Signed Message:\n5" + body)
    assert siwe.eip191_hash("hello") == expected


@pytest.mark.parametrize("bad", ["0x", "0xdeadbeef", "0x" + "zz" * 65, "not hex"])
def test_a_malformed_signature_is_refused_not_guessed(bad):
    with pytest.raises(ValueError):
        siwe.split_signature(bad)


def test_high_s_signatures_are_refused_as_non_canonical():
    """Malleability: (r, s) and (r, n-s) are both valid over the same message.

    Accepting both gives one authorisation two distinct encodings, which defeats
    any replay store keyed on the signature bytes.
    """
    message, signature = _signed()
    raw = bytearray.fromhex(signature[2:])
    s = int.from_bytes(raw[32:64], "big")
    raw[32:64] = (C.N - s).to_bytes(32, "big")

    with pytest.raises(ValueError, match="high s"):
        siwe.split_signature("0x" + raw.hex())


@pytest.mark.parametrize("v_byte", [27, 28, 0, 1])
def test_both_wallet_conventions_for_v_are_accepted(v_byte):
    """MetaMask sends 27/28; others send 0/1. Rejecting one looks like a broken account."""
    r, s, recovery = siwe.split_signature("0x" + "11" * 32 + "22" * 32 + bytes([v_byte]).hex())
    assert recovery in (0, 1)


# --------------------------------------------------------------------------- replay

def test_a_signature_authenticates_exactly_once():
    """The attack: capture a valid sign-in and present it again."""
    message, signature = _signed()

    first = siwe.verify(message, signature, expected_domain=DOMAIN)
    assert first["ok"] is True
    assert first["signer"] == ADDRESS

    replay = siwe.verify(message, signature, expected_domain=DOMAIN)
    assert replay["ok"] is False
    assert "already used" in replay["reason"]


def test_a_client_chosen_nonce_is_not_accepted():
    """Nonces are issued by the server; one the client invented is unknown."""
    message, signature = _signed(nonce="a-nonce-i-made-up")
    out = siwe.verify(message, signature, expected_domain=DOMAIN)

    assert out["ok"] is False
    assert "unknown" in out["reason"]


def test_a_failed_login_does_not_burn_the_nonce():
    """Otherwise one bad request from anywhere denies the real user their login."""
    nonce = siwe.issue_nonce()
    message, signature = _signed(nonce=nonce, domain="evil.example")

    rejected = siwe.verify(message, signature, expected_domain=DOMAIN)
    assert rejected["ok"] is False

    # The nonce must still be spendable by a legitimate attempt.
    good_message = siwe.build_message(domain=DOMAIN, address=ADDRESS, uri=URI,
                                      chain_id=CHAIN_ID, nonce=nonce)
    good_sig = "0x" + sign(siwe.eip191_hash(good_message), PRIVATE_KEY).hex()
    assert siwe.verify(good_message, good_sig, expected_domain=DOMAIN)["ok"] is True


def test_an_expired_nonce_cannot_be_spent():
    nonce = siwe.issue_nonce(ttl=-1)
    assert siwe.consume_nonce(nonce) is False


# --------------------------------------------------------------------------- phishing

def test_a_signature_for_another_domain_is_rejected_here():
    """The attack: a valid signature, collected on a site the user was tricked into."""
    message, signature = _signed(domain="evil.example")
    out = siwe.verify(message, signature, expected_domain=DOMAIN)

    assert out["ok"] is False
    assert "wrong domain" in out["reason"]
    assert out["signer"] == ADDRESS        # genuinely signed -- just not for us


def test_a_signature_for_another_chain_is_rejected():
    message, signature = _signed(chain_id=1)
    out = siwe.verify(message, signature, expected_domain=DOMAIN,
                      expected_chain_id=CHAIN_ID)
    assert out["ok"] is False
    assert "wrong chain" in out["reason"]


def test_a_signature_for_another_uri_is_rejected():
    message, signature = _signed(uri="https://evil.example/login")
    out = siwe.verify(message, signature, expected_domain=DOMAIN, expected_uri=URI)
    assert out["ok"] is False
    assert "wrong URI" in out["reason"]


def test_rewriting_the_message_after_signing_is_detected():
    """The attack: swap the address so someone else's signature logs you in."""
    message, signature = _signed()
    tampered = message.replace(ADDRESS, "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed")

    out = siwe.verify(tampered, signature, expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "does not match the address" in out["reason"]


def test_changing_any_byte_of_the_statement_invalidates_it():
    """The signature covers the whole message, including what the wallet displayed."""
    message, signature = _signed()
    tampered = message.replace("moves no funds", "moves your funds")
    assert siwe.verify(tampered, signature, expected_domain=DOMAIN)["ok"] is False


# --------------------------------------------------------------------------- staleness

def test_an_expired_message_is_rejected():
    past = (siwe._now() - _dt.timedelta(minutes=5)).isoformat(timespec="seconds")
    message, signature = _signed(expiration_time=past)

    out = siwe.verify(message, signature, expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "expired" in out["reason"]


def test_an_old_message_is_rejected_even_with_no_explicit_expiry():
    """An unbounded signature must not exist, whatever the message omitted."""
    stale = (siwe._now() - _dt.timedelta(seconds=siwe.MAX_AGE_SECONDS + 60))
    message, signature = _signed(issued_at=stale.isoformat(timespec="seconds"))

    out = siwe.verify(message, signature, expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "old" in out["reason"]


def test_a_message_from_the_future_is_rejected():
    ahead = (siwe._now() + _dt.timedelta(minutes=10)).isoformat(timespec="seconds")
    message, signature = _signed(issued_at=ahead)

    out = siwe.verify(message, signature, expected_domain=DOMAIN)
    assert out["ok"] is False
    assert "future" in out["reason"]


# --------------------------------------------------------------------------- the message itself

def test_the_message_round_trips_through_the_parser():
    nonce = siwe.issue_nonce()
    message = siwe.build_message(domain=DOMAIN, address=ADDRESS, uri=URI,
                                 chain_id=CHAIN_ID, nonce=nonce,
                                 resources=["ipfs://abc", "https://example/run/1"])
    fields = siwe.parse_message(message)

    assert fields["domain"] == DOMAIN
    assert fields["address"] == ADDRESS
    assert fields["uri"] == URI
    assert fields["chain_id"] == str(CHAIN_ID)
    assert fields["nonce"] == nonce
    assert fields["resources"] == ["ipfs://abc", "https://example/run/1"]


def test_the_statement_tells_the_user_this_is_not_a_transaction():
    """What the wallet shows is the only thing most users will read."""
    assert "not a transaction" in siwe.DEFAULT_STATEMENT
    assert "moves no funds" in siwe.DEFAULT_STATEMENT
    assert "no spending permission" in siwe.DEFAULT_STATEMENT


def test_a_non_siwe_string_is_refused():
    with pytest.raises(ValueError):
        siwe.parse_message("hello please log me in")


def test_verification_never_raises_on_hostile_input():
    """An endpoint that 500s on malformed input is a denial-of-service lever."""
    for message, signature in [("", "0x"), ("garbage", "0x" + "11" * 65),
                               ("x" * 5000, "nope")]:
        out = siwe.verify(message, signature, expected_domain=DOMAIN)
        assert out["ok"] is False
        assert out["reason"]


def test_verification_admits_it_has_not_met_a_real_wallet():
    """No live MetaMask signature has been verified here; the result says so."""
    message, signature = _signed()
    assert siwe.verify(message, signature, expected_domain=DOMAIN)["interop_verified"] is False


# --------------------------------------------------------------------------- binding to an account

@pytest.fixture
def _clean_users():
    import auth
    saved = dict(auth.USERS_DB)
    auth.USERS_DB.clear()
    yield auth
    auth.USERS_DB.clear()
    auth.USERS_DB.update(saved)


def test_first_sign_in_registers_the_account(_clean_users):
    """Control of the key is the credential, so there is no separate sign-up."""
    auth = _clean_users
    token = auth.authenticate_wallet(ADDRESS)

    assert token
    claims = auth.AuthToken.verify(token)
    assert claims["role"] == "researcher"

    user = auth.get_user_by_wallet(ADDRESS)
    assert user is not None
    assert user.wallet_address == ADDRESS


def test_signing_in_twice_does_not_create_a_second_account(_clean_users):
    """Otherwise a researcher's authorship forks across duplicate identities."""
    auth = _clean_users
    auth.authenticate_wallet(ADDRESS)
    auth.authenticate_wallet(ADDRESS)
    assert len(auth.USERS_DB) == 1


def test_address_case_does_not_fork_the_identity(_clean_users):
    """EIP-55 checksumming is presentational; two spellings are one account."""
    auth = _clean_users
    auth.authenticate_wallet(ADDRESS)
    auth.authenticate_wallet(ADDRESS.lower())
    auth.authenticate_wallet(ADDRESS.upper().replace("0X", "0x"))
    assert len(auth.USERS_DB) == 1


def test_a_wallet_account_has_no_password_to_attack(_clean_users):
    """The key is the only way in: password login must fail closed for it."""
    auth = _clean_users
    auth.authenticate_wallet(ADDRESS)
    user = auth.get_user_by_wallet(ADDRESS)

    assert user.password_hash is None
    assert auth.authenticate_user(user.email, "") is None
    assert auth.authenticate_user(user.email, "password") is None


def test_a_new_wallet_never_inherits_an_elevated_role(_clean_users):
    """Self-registration must not be a path to admin."""
    auth = _clean_users
    auth.create_user(email="boss@lab", name="Boss", role="admin")
    auth.authenticate_wallet(ADDRESS)

    assert auth.get_user_by_wallet(ADDRESS).role == "researcher"


def test_end_to_end_nonce_sign_verify_token(_clean_users):
    """The whole flow, as the browser performs it."""
    auth = _clean_users

    nonce = siwe.issue_nonce()
    message = siwe.build_message(domain=DOMAIN, address=ADDRESS, uri=URI,
                                 chain_id=CHAIN_ID, nonce=nonce)
    signature = "0x" + sign(siwe.eip191_hash(message), PRIVATE_KEY).hex()

    result = siwe.verify(message, signature, expected_domain=DOMAIN,
                         expected_chain_id=CHAIN_ID)
    assert result["ok"] is True

    token = auth.authenticate_wallet(result["signer"])
    claims = auth.AuthToken.verify(token)
    assert claims is not None
    assert claims["email"].startswith(ADDRESS.lower())
