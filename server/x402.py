"""x402: charge for an API call over plain HTTP, using the 402 status code.

This repo's expensive endpoints -- docking, MD, screening -- currently cost the
operator money and earn nothing, which is the usual reason a public research API
quietly disappears. x402 is the smallest standard way to put a price on a call
without accounts, API keys or a billing integration: the server answers 402 with
its terms, the client retries carrying a signed payment authorization.

THIS MODULE ONLY EVER CHARGES. It never pays.

There is no client here, no key, and no function that signs a payment. That is a
deliberate asymmetry: a library that can autonomously spend is one bug away from
spending without being asked, and an agent framework that can pay its own bills
is exactly the thing that should not ship by accident. Paying belongs in a
person's wallet, the same boundary chain_anchor and compound_sourcing draw.

SETTLEMENT IS NOT IMPLEMENTED, and this is the important caveat. Verifying that
a payment authorization is well-formed and matches the advertised terms is done
here. Confirming that it actually moved funds on-chain requires a facilitator
this environment cannot reach. verify_payment() therefore returns
``settled: False`` with ``settlement: "not_attempted"`` ALWAYS, and a caller that
treats a structural pass as "they paid" has been warned in the return value
itself. Wire a facilitator before charging anyone real money.

Header names follow the x402 transport spec: PAYMENT-REQUIRED on the 402,
PAYMENT-SIGNATURE on the retry, PAYMENT-RESPONSE on the outcome. Each carries
base64-encoded JSON.
"""
import base64
import binascii
import datetime as _dt
import json

SCHEMA_VERSION = "1.0"
X402_VERSION = 1

HEADER_REQUIRED = "PAYMENT-REQUIRED"
HEADER_SIGNATURE = "PAYMENT-SIGNATURE"
HEADER_RESPONSE = "PAYMENT-RESPONSE"

#: Monad testnet, matching chain_anchor.NETWORKS and the SIWE chain id. Testnet
#: by default for the same reason: charging real money should be typed, not
#: inherited from a default nobody looked at.
DEFAULT_NETWORK = "monad-testnet"
DEFAULT_CHAIN_ID = 10143

SETTLEMENT_CAVEAT = (
    "NOT SETTLED. This server verified that the payment authorization is well-formed "
    "and matches the advertised terms. It has NOT confirmed that any funds moved: no "
    "facilitator is configured and no chain was consulted. Do not release anything "
    "valuable on the strength of this alone.")

PAYMENT_BOUNDARY = (
    "This software charges but never pays. It holds no key, signs no payment, and "
    "cannot initiate a transfer.")


def _b64(obj) -> str:
    return base64.b64encode(json.dumps(obj, separators=(",", ":")).encode()).decode()


def _unb64(header):
    """Decode a base64 JSON header. Returns (obj, error); never raises.

    A malformed header is a client mistake, not a server fault, and must not be
    able to 500 an endpoint that is by definition exposed to strangers.
    """
    if not header:
        return None, "header is empty"
    try:
        raw = base64.b64decode(str(header), validate=True)
    except (binascii.Error, ValueError) as exc:
        return None, f"header is not valid base64: {exc}"
    try:
        obj = json.loads(raw)
    except ValueError as exc:
        return None, f"header is not valid JSON: {exc}"
    if not isinstance(obj, dict):
        return None, "header must decode to a JSON object"
    return obj, None


# --------------------------------------------------------------------------- charging

def payment_required(amount, pay_to, resource, description="", asset=None,
                     network=DEFAULT_NETWORK, chain_id=DEFAULT_CHAIN_ID,
                     max_timeout_seconds=300, mime_type="application/json"):
    """Build the terms for a 402 response.

    `amount` is in the asset's smallest unit, as a STRING. Not a float: a price
    is exact, and 0.1 + 0.2 is a bad property for money. Not an int either,
    because token amounts routinely exceed what JSON consumers parse safely.
    """
    if not isinstance(amount, str) or not amount.isdigit():
        raise ValueError(
            f"amount must be a decimal string in the asset's smallest unit, got {amount!r}. "
            "Floats are refused here on purpose: prices must be exact.")

    requirements = {
        "x402Version": X402_VERSION,
        "scheme": "exact",
        "network": network,
        "chainId": chain_id,
        "maxAmountRequired": amount,
        "payTo": pay_to,
        "asset": asset,
        "resource": resource,
        "description": description,
        "mimeType": mime_type,
        "maxTimeoutSeconds": max_timeout_seconds,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": 402,
        "accepts": [requirements],
        "header_name": HEADER_REQUIRED,
        "header_value": _b64({"x402Version": X402_VERSION, "accepts": [requirements]}),
        "payment_boundary": PAYMENT_BOUNDARY,
    }


def verify_payment(signature_header, requirements, now=None):
    """Check a client's PAYMENT-SIGNATURE against what was advertised.

    Structural verification only -- see SETTLEMENT_CAVEAT and the module
    docstring. The return value always carries settled=False.
    """
    now = now or _dt.datetime.now(_dt.timezone.utc)

    payload, err = _unb64(signature_header)
    if err:
        return _payment_result(False, f"malformed {HEADER_SIGNATURE}: {err}")

    if payload.get("x402Version") != X402_VERSION:
        return _payment_result(
            False, f"unsupported x402Version {payload.get('x402Version')!r}; "
                   f"this server speaks {X402_VERSION}")

    scheme = payload.get("scheme")
    if scheme != requirements.get("scheme"):
        return _payment_result(
            False, f"scheme mismatch: client sent {scheme!r}, terms require "
                   f"{requirements.get('scheme')!r}")

    if payload.get("network") != requirements.get("network"):
        return _payment_result(
            False, f"wrong network: payment is for {payload.get('network')!r}, "
                   f"terms are {requirements.get('network')!r}")

    details = payload.get("payload")
    if not isinstance(details, dict):
        return _payment_result(False, "payment payload is missing or not an object")

    authorization = details.get("authorization")
    if not isinstance(authorization, dict):
        return _payment_result(False, "payment payload carries no authorization object")

    # Amount: compared as integers, but only after confirming both are digit
    # strings. A client sending "1e9" or " 100" must not be coerced into a
    # number that happens to be large enough.
    claimed = authorization.get("value")
    required = requirements.get("maxAmountRequired")
    if not (isinstance(claimed, str) and claimed.isdigit()):
        return _payment_result(False, f"authorization value must be a decimal string, "
                                      f"got {claimed!r}")
    if int(claimed) < int(required):
        return _payment_result(
            False, f"underpaid: authorized {claimed}, required {required}")

    if authorization.get("to") != requirements.get("payTo"):
        return _payment_result(
            False, "payment is addressed elsewhere: authorization pays "
                   f"{authorization.get('to')!r}, terms require {requirements.get('payTo')!r}")

    # Validity window. An authorization with no expiry is one that can be
    # replayed forever, so an absent validBefore is a refusal, not a default.
    valid_before = _as_epoch(authorization.get("validBefore"))
    if valid_before is None:
        return _payment_result(False, "authorization has no usable validBefore")
    if now.timestamp() >= valid_before:
        return _payment_result(False, "payment authorization has expired")

    valid_after = _as_epoch(authorization.get("validAfter"))
    if valid_after is not None and now.timestamp() < valid_after:
        return _payment_result(False, "payment authorization is not valid yet")

    if not authorization.get("nonce"):
        return _payment_result(False, "authorization carries no nonce")

    if not details.get("signature"):
        return _payment_result(False, "authorization is not signed")

    return _payment_result(
        True, None, payer=authorization.get("from"),
        amount=claimed, asset=requirements.get("asset"),
        network=requirements.get("network"), nonce=authorization.get("nonce"))


def _as_epoch(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _payment_result(structurally_valid, reason, **extra):
    return {
        "schema_version": SCHEMA_VERSION,
        "structurally_valid": structurally_valid,
        # Never True. Structural validity is not settlement, and conflating the
        # two is how an endpoint gives away work for an unfunded promise.
        "settled": False,
        "settlement": "not_attempted",
        "reason": reason,
        "settlement_caveat": SETTLEMENT_CAVEAT,
        "payment_boundary": PAYMENT_BOUNDARY,
        **extra,
    }


def payment_response_header(result):
    """The PAYMENT-RESPONSE header value describing the outcome."""
    return _b64({
        "x402Version": X402_VERSION,
        "success": bool(result.get("structurally_valid")),
        "settled": False,
        "settlement": result.get("settlement", "not_attempted"),
        "error": result.get("reason"),
        "payer": result.get("payer"),
        "caveat": SETTLEMENT_CAVEAT,
    })


def parse_requirements(required_header):
    """Decode a PAYMENT-REQUIRED header. For reading another server's terms.

    Provided so this repo can INSPECT what something else charges -- reporting a
    price to a person is not the same as paying it, and there is still no
    function here that pays.
    """
    obj, err = _unb64(required_header)
    if err:
        return None, err
    accepts = obj.get("accepts")
    if not isinstance(accepts, list) or not accepts:
        return None, "PAYMENT-REQUIRED carries no 'accepts' list"
    return accepts, None
