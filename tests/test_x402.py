"""Charging for an API call, and the two ways that goes badly wrong.

The first is giving work away: treating a well-formed payment authorization as
proof that funds moved. They are different claims, and only one of them has been
checked here -- no facilitator is reachable from this environment. Every result
says settled=False for that reason, and several tests below exist purely to stop
someone "tidying" that into a True.

The second is the opposite failure: a library that can pay. This module charges
and never pays, and one test asserts that no payment-signing capability exists
at all, because that is a property worth failing a build over rather than
trusting to review.
"""
import base64
import datetime as _dt
import json

import pytest

import x402


PAY_TO = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
PAYER = "0x9d8A62f656a8d1615C1294fd71e9CFb3E4855A4F"
ASSET = "0x0000000000000000000000000000000000000001"


def _terms(amount="1000000"):
    return x402.payment_required(
        amount=amount, pay_to=PAY_TO, asset=ASSET,
        resource="/api/dock", description="One docking run")["accepts"][0]


def _authorization(terms, **overrides):
    now = int(_dt.datetime.now(_dt.timezone.utc).timestamp())
    auth = {
        "from": PAYER, "to": terms["payTo"],
        "value": terms["maxAmountRequired"],
        "validAfter": str(now - 60), "validBefore": str(now + 600),
        "nonce": "0x" + "ab" * 32,
    }
    auth.update(overrides)
    payload = {
        "x402Version": x402.X402_VERSION,
        "scheme": terms["scheme"], "network": terms["network"],
        "payload": {"signature": "0x" + "cd" * 65, "authorization": auth},
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()


# --------------------------------------------------------------------------- the terms

def test_the_402_carries_decodable_terms():
    out = x402.payment_required(amount="1000000", pay_to=PAY_TO, resource="/api/dock")

    assert out["status"] == 402
    assert out["header_name"] == "PAYMENT-REQUIRED"

    decoded = json.loads(base64.b64decode(out["header_value"]))
    assert decoded["accepts"][0]["payTo"] == PAY_TO
    assert decoded["accepts"][0]["maxAmountRequired"] == "1000000"


def test_the_price_must_be_an_exact_string_not_a_float():
    """0.1 + 0.2 is a bad property for money, so floats are refused outright."""
    for bad in [1000000, 0.1, None, "1.5", "1e6", " 100"]:
        with pytest.raises(ValueError, match="exact"):
            x402.payment_required(amount=bad, pay_to=PAY_TO, resource="/api/dock")


def test_charging_defaults_to_testnet():
    """Charging real money should be typed, not inherited from a default."""
    assert x402.DEFAULT_NETWORK == "monad-testnet"
    assert _terms()["network"] == "monad-testnet"


# --------------------------------------------------------------------------- settlement is not verified

def test_a_valid_authorization_is_still_not_settled():
    """The central caveat. Structural validity is not proof that funds moved."""
    terms = _terms()
    result = x402.verify_payment(_authorization(terms), terms)

    assert result["structurally_valid"] is True
    assert result["settled"] is False
    assert result["settlement"] == "not_attempted"
    assert "NOT SETTLED" in result["settlement_caveat"]


def test_no_code_path_reports_a_settled_payment():
    """Pins that settled=False is unconditional, across success and failure."""
    terms = _terms()
    cases = [
        _authorization(terms),                                   # good
        _authorization(terms, value="1"),                        # underpaid
        "not base64",                                            # junk
        _authorization(terms, validBefore="0"),                  # expired
    ]
    for header in cases:
        assert x402.verify_payment(header, terms)["settled"] is False


def test_the_response_header_never_claims_settlement():
    terms = _terms()
    result = x402.verify_payment(_authorization(terms), terms)
    decoded = json.loads(base64.b64decode(x402.payment_response_header(result)))

    assert decoded["settled"] is False
    assert "NOT SETTLED" in decoded["caveat"]


# --------------------------------------------------------------------------- it must not pay

def test_the_module_exposes_no_way_to_pay():
    """A library that can autonomously spend is one bug from spending unasked."""
    forbidden = ("pay", "sign_payment", "make_payment", "send_payment",
                 "authorize_payment", "sign", "private_key", "wallet")
    exported = {n for n in dir(x402) if not n.startswith("_")}

    for name in forbidden:
        assert name not in exported, f"x402 exposes {name!r}; this module must only charge"
    assert "never pays" in x402.PAYMENT_BOUNDARY


def test_reading_another_servers_price_is_not_paying_it():
    """Inspecting terms is allowed; it returns data, and nothing is authorized."""
    header = x402.payment_required(amount="5", pay_to=PAY_TO,
                                   resource="/x")["header_value"]
    accepts, err = x402.parse_requirements(header)

    assert err is None
    assert accepts[0]["maxAmountRequired"] == "5"


# --------------------------------------------------------------------------- rejecting bad payments

def test_an_underpayment_is_refused():
    terms = _terms(amount="1000000")
    result = x402.verify_payment(_authorization(terms, value="999999"), terms)

    assert result["structurally_valid"] is False
    assert "underpaid" in result["reason"]


def test_a_payment_addressed_elsewhere_is_refused():
    """The attack: a genuine payment to someone else, replayed here as proof."""
    terms = _terms()
    result = x402.verify_payment(
        _authorization(terms, to="0xdEADBEeF00000000000000000000000000000000"), terms)

    assert result["structurally_valid"] is False
    assert "addressed elsewhere" in result["reason"]


def test_an_expired_authorization_is_refused():
    terms = _terms()
    past = str(int(_dt.datetime.now(_dt.timezone.utc).timestamp()) - 10)
    result = x402.verify_payment(_authorization(terms, validBefore=past), terms)

    assert result["structurally_valid"] is False
    assert "expired" in result["reason"]


def test_an_authorization_with_no_expiry_is_refused():
    """No expiry means replayable forever; an absent field is not a default."""
    terms = _terms()
    result = x402.verify_payment(_authorization(terms, validBefore=None), terms)

    assert result["structurally_valid"] is False
    assert "validBefore" in result["reason"]


def test_an_authorization_not_yet_valid_is_refused():
    terms = _terms()
    future = str(int(_dt.datetime.now(_dt.timezone.utc).timestamp()) + 600)
    result = x402.verify_payment(_authorization(terms, validAfter=future), terms)

    assert result["structurally_valid"] is False
    assert "not valid yet" in result["reason"]


def test_a_payment_for_another_network_is_refused():
    """A testnet authorization must not buy anything on mainnet, or vice versa."""
    terms = _terms()
    payload = json.loads(base64.b64decode(_authorization(terms)))
    payload["network"] = "monad-mainnet"
    header = base64.b64encode(json.dumps(payload).encode()).decode()

    result = x402.verify_payment(header, terms)
    assert result["structurally_valid"] is False
    assert "wrong network" in result["reason"]


@pytest.mark.parametrize("value", ["1e9", " 100", "-5", "0x64", "", None, 100])
def test_a_non_exact_amount_is_refused_not_coerced(value):
    """'1e9' must not become a billion just because float() would accept it."""
    terms = _terms()
    result = x402.verify_payment(_authorization(terms, value=value), terms)
    assert result["structurally_valid"] is False


def test_an_unsigned_authorization_is_refused():
    terms = _terms()
    payload = json.loads(base64.b64decode(_authorization(terms)))
    payload["payload"].pop("signature")
    header = base64.b64encode(json.dumps(payload).encode()).decode()

    assert x402.verify_payment(header, terms)["structurally_valid"] is False


def test_a_missing_nonce_is_refused():
    terms = _terms()
    result = x402.verify_payment(_authorization(terms, nonce=""), terms)
    assert result["structurally_valid"] is False
    assert "nonce" in result["reason"]


# --------------------------------------------------------------------------- hostile input

@pytest.mark.parametrize("header", [
    "", None, "not base64!!", base64.b64encode(b"not json").decode(),
    base64.b64encode(b'"a string"').decode(), base64.b64encode(b"[1,2,3]").decode(),
])
def test_a_malformed_header_never_raises(header):
    """This endpoint faces strangers; a 500 on bad input is a DoS lever."""
    result = x402.verify_payment(header, _terms())
    assert result["structurally_valid"] is False
    assert result["reason"]


def test_an_unsupported_protocol_version_is_refused():
    terms = _terms()
    payload = json.loads(base64.b64decode(_authorization(terms)))
    payload["x402Version"] = 99
    header = base64.b64encode(json.dumps(payload).encode()).decode()

    result = x402.verify_payment(header, terms)
    assert result["structurally_valid"] is False
    assert "x402Version" in result["reason"]
