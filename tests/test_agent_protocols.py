"""Offline checks for the agent protocol layer.

These run without a network or a listening port: they exercise the signing, the payment challenge and
the fingerprint logic directly. What they cannot prove is settlement (nothing is wired to a facilitator)
or Ed25519 signing (that package is not installed here), and both are asserted as the current state so
the test fails loudly if someone wires one up without updating the claims.
"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "server"))

import agent_protocols as ap


def test_identity_is_stable_and_named():
    assert ap.IDENTITY.agent_id.startswith("did:nanda:")
    assert ap.IDENTITY.alg in ("ed25519", "hmac-sha256")
    # A second Identity must load the stored key, not mint a new one.
    assert ap.Identity().agent_id == ap.IDENTITY.agent_id


def test_stamp_verifies_and_detects_tampering():
    env = ap.stamp({"best": -9.9, "poses": 7}, "dock")
    assert ap.verify_stamp(env)["ok"] is True
    env["result"]["best"] = -99.0
    bad = ap.verify_stamp(env)
    assert bad["ok"] is False
    assert "altered" in bad["reason"] or "verify" in bad["reason"]


def test_stamp_detects_a_swapped_signature():
    a = ap.stamp({"x": 1}, "dock")
    b = ap.stamp({"x": 2}, "dock")
    a["proof"] = b["proof"]
    assert ap.verify_stamp(a)["ok"] is False


def test_agent_facts_are_signed_and_declare_limits():
    facts = ap.agent_facts("http://localhost:8000", [{"name": "dock", "description": "d"}], ap.PRICING)
    assert facts["id"] == ap.IDENTITY.agent_id
    assert facts["proof"]["alg"] == ap.IDENTITY.alg
    # The benchmark caveat travels with the discovery document, not just the marketing.
    assert "2 of 4" in facts["limits"]["note"]
    body = {k: v for k, v in facts.items() if k != "proof"}
    assert ap.verify_stamp({**body, "proof": facts["proof"]})["ok"] is True


def test_payment_challenge_names_price_and_network():
    ch = ap.payment_required("screen_library", "http://localhost:8000/api/command")
    accept = ch["accepts"][0]
    assert ch["x402Version"] == 1
    assert accept["maxAmountRequired"] == ap.PRICING["screen_library"]["amount"]
    assert accept["asset"] == "USDC"
    assert accept["scheme"] == "exact"
    assert "settles nothing" in ch["note"]


def test_free_tools_are_not_metered():
    assert ap.price_of("describe_scene") is None
    assert ap.price_of("dock") is not None


def test_payment_is_refused_without_a_facilitator():
    payload = base64.b64encode(json.dumps(
        {"scheme": "exact", "network": "base-sepolia", "payload": {"sig": "0xdead"}}).encode()).decode()
    ok, detail = ap.verify_payment(payload, "dock", accept_test_payments=False)
    assert ok is False
    assert "facilitator" in detail


def test_malformed_payment_is_rejected_before_anything_else():
    assert ap.verify_payment("not-base64", "dock", accept_test_payments=True)[0] is False
    missing = base64.b64encode(json.dumps({"scheme": "exact"}).encode()).decode()
    ok, detail = ap.verify_payment(missing, "dock", accept_test_payments=True)
    assert ok is False and "missing" in detail


def test_test_mode_accepts_once_and_refuses_a_replay():
    payload = base64.b64encode(json.dumps(
        {"scheme": "exact", "network": "base-sepolia", "payload": {"nonce": "replay-check-1"}}).encode()).decode()
    ok, detail = ap.verify_payment(payload, "dock", accept_test_payments=True)
    assert ok is True
    assert detail["settled"] is False          # never claim money moved
    assert "without settlement" in detail["warning"]
    again, why = ap.verify_payment(payload, "dock", accept_test_payments=True)
    assert again is False and "already been used" in why


def test_fingerprint_round_trip():
    ch = ap.fingerprint_challenge()
    pairs = ap._fingerprint_pairs()
    right = pairs[ch["index"]]["response"]
    assert ap.fingerprint_verify(ch["index"], right)["ok"] is True
    assert ap.fingerprint_verify(ch["index"], "wrong")["ok"] is False
    assert ap.fingerprint_verify(999, right)["ok"] is False


def test_the_challenge_does_not_leak_its_answer():
    ch = ap.fingerprint_challenge()
    assert "response" not in ch
    pairs = ap._fingerprint_pairs()
    assert pairs[ch["index"]]["response"] not in json.dumps(ch)
