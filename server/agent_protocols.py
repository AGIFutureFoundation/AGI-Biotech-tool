"""Agent-to-agent protocol layer: x402 payments, NANDA discovery, OML-style fingerprinting.

Three separate problems arise when one agent calls another's tools:

  x402   - how does the caller pay for a metered tool without an account?
           (HTTP 402 challenge, signed payment payload, retry. x402.org / Coinbase.)
  NANDA  - how does the caller find this agent and learn what it can do?
           (A signed AgentFacts document at a well-known URL. MIT Project NANDA.)
  OML    - how does anyone later prove which agent produced a result?
           (Secret challenge/response fingerprints plus signatures over outputs. Sentient
            Foundation's OML 1.0 applies this to model weights; the same idea is applied
            here to this service and the artefacts it emits.)

WHAT IS AND IS NOT REAL HERE
  * The HTTP shapes are implemented: a caller gets a spec-shaped 402 challenge, an
    AgentFacts document, and a verifiable signature over every result.
  * Signing is real. Ed25519 when `cryptography` is installed, HMAC-SHA256 otherwise.
    Keys live in .keys/ and never leave the machine.
  * Settlement is NOT implemented. No wallet, no chain, no funds move. A payment counts as
    accepted only in test mode, and the response says so. Wiring a real x402 facilitator is
    a deliberate separate step - see verify_payment().
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYDIR = os.path.join(ROOT, ".keys")

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    HAVE_ED25519 = True
except Exception:  # noqa: BLE001
    HAVE_ED25519 = False


class Identity:
    """This service's signing key and stable agent id."""

    def __init__(self, name="biodao.blockchain"):
        self.name = name
        os.makedirs(KEYDIR, mode=0o700, exist_ok=True)
        self.alg = "ed25519" if HAVE_ED25519 else "hmac-sha256"
        self._load_or_create()

    def _read_key(self, path):
        with open(path) as f:
            data = json.load(f)
        self.secret = base64.b64decode(data["secret"])
        self.created = data["created"]

    def _load_or_create(self):
        """Load the signing key, or create it privately and exactly once.

        Two things the straightforward version got wrong:

        A plain open(path, "w") creates the file 0o666 & ~umask -- 0o644 under
        the usual 022 -- and the chmod to 0o600 lands afterwards. Between the
        two, any other local account can read the signing key. The fix is to
        never let it exist with wider permissions: os.open with O_EXCL and an
        explicit 0o600 mode.

        And `if not exists: write` is not a decision, it is a race. Two first
        starts both see no file and both write. The one that loses carries on
        with a secret that is not the one on disk, so it signs happily until it
        restarts, picks up the winner's key, and every signature it issued
        stops verifying. Creating through a temporary file and os.link makes
        publication atomic: link fails if the name is taken, and the loser
        adopts the winner's key instead of its own. Nothing ever observes a
        half-written key file either, which open(path, "w") also allowed.
        """
        path = os.path.join(KEYDIR, "agent_key.json")
        if os.path.exists(path):
            self._read_key(path)
        else:
            self.secret = secrets.token_bytes(32)
            self.created = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            tmp = os.path.join(KEYDIR, ".agent_key." + secrets.token_hex(16))
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(fd, "w") as f:
                    json.dump({"secret": base64.b64encode(self.secret).decode(), "created": self.created,
                               "note": "Local signing key. Not a wallet; holds no funds. Do not commit."},
                              f, indent=1)
                try:
                    os.link(tmp, path)
                except FileExistsError:
                    # Another process published first. Its key is the real one.
                    self._read_key(path)
            finally:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
        if HAVE_ED25519:
            self._key = Ed25519PrivateKey.from_private_bytes(self.secret)
            self.public = base64.b64encode(self._key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)).decode()
        else:
            # Without Ed25519 this "public key" is a commitment to the secret, not a true public key:
            # it lets a caller recognise a repeat signer, not verify without holding the secret.
            self.public = hashlib.sha256(self.secret).hexdigest()
        self.agent_id = "did:nanda:" + hashlib.sha256((self.name + self.public).encode()).hexdigest()[:32]

    def sign(self, payload: bytes) -> str:
        if HAVE_ED25519:
            return base64.b64encode(self._key.sign(payload)).decode()
        return base64.b64encode(hmac.new(self.secret, payload, hashlib.sha256).digest()).decode()

    def sign_json(self, obj) -> dict:
        body = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
        return {"alg": self.alg, "key": self.public, "signature": self.sign(body),
                "digest": "sha256:" + hashlib.sha256(body).hexdigest()}


IDENTITY = Identity()


def agent_facts(base_url, tools, pricing):
    """A signed description of this agent: who it is, what it does, how to reach it.

    Shaped after MIT Project NANDA's AgentFacts. Not registered with any public index;
    publishing it there is a separate action the operator takes deliberately.
    """
    facts = {
        "@context": ["https://www.w3.org/ns/did/v1", "https://nanda.media.mit.edu/agentfacts/v0"],
        "id": IDENTITY.agent_id,
        "name": "biodao.blockchain",
        "label": "molecular research workspace (AGI Corp)",
        "description": ("Operates a live molecular research workspace: loads protein structures, detects "
                        "pockets, docks compounds, classifies interactions, screens libraries, runs "
                        "molecular dynamics and gathers target evidence from public databases."),
        "provider": {"name": "AGI Future Foundation", "url": "https://agifuturefoundation.org",
                     "contact": "x@agifuturefoundation.org"},
        "version": "1.0.0",
        "created": IDENTITY.created,
        "endpoints": {
            "mcp": {"transport": "stdio", "command": "server/mcp_server.py"},
            "http": {"tools": f"{base_url}/api/tools", "invoke": f"{base_url}/api/command",
                     "facts": f"{base_url}/.well-known/agent-facts.json"},
        },
        "capabilities": [{"name": t.get("name"), "description": (t.get("description") or "")[:160]} for t in tools],
        "pricing": pricing,
        "verification": {"fingerprint": f"{base_url}/api/oml/challenge", "scheme": "oml-1.0-style"},
        "limits": {"note": "Docking scores are an unvalidated empirical estimate. Benchmark: 2 of 4 "
                           "re-docking cases within 2 A, median 2.54 A. Not a binding prediction."},
    }
    facts["proof"] = IDENTITY.sign_json(facts)
    return facts


# Tools that cost real compute are the ones worth metering. Everything else stays free.
PRICING = {
    "dock": {"amount": "0.05", "unit": "USDC", "why": "Monte Carlo search, tens of seconds of CPU"},
    "screen_library": {"amount": "0.50", "unit": "USDC", "why": "docks every compound in the library"},
    "run_backend_md": {"amount": "0.25", "unit": "USDC", "why": "GPU molecular dynamics"},
    "selectivity": {"amount": "0.20", "unit": "USDC", "why": "docks against several targets"},
}
PAYMENT_NETWORK = os.environ.get("BIODAO_X402_NETWORK", "base-sepolia")
PAY_TO = os.environ.get("BIODAO_X402_ADDRESS", "")
_SEEN_PAYMENTS = {}


def price_of(tool):
    return PRICING.get(tool)


def payment_required(tool, resource_url):
    """The 402 body: what is owed, to whom, on what network, and how to retry."""
    price = PRICING[tool]
    return {
        "x402Version": 1,
        "error": "payment required",
        "accepts": [{
            "scheme": "exact",
            "network": PAYMENT_NETWORK,
            "maxAmountRequired": price["amount"],
            "asset": price["unit"],
            "payTo": PAY_TO or "(unset: BIODAO_X402_ADDRESS)",
            "resource": resource_url,
            "description": f"{tool}: {price['why']}",
            "mimeType": "application/json",
            "maxTimeoutSeconds": 300,
        }],
        "note": ("Retry with an X-PAYMENT header carrying the signed payload. This deployment verifies "
                 "the header's shape and replay-protection only; it settles nothing on chain."),
    }


def verify_payment(header_value, tool, accept_test_payments=False):
    """Check an X-PAYMENT header. Returns (ok, detail).

    Real settlement means handing the payload to an x402 facilitator and confirming the transfer
    before returning the resource. That call is deliberately absent, so test mode is the only way a
    payment is accepted and every accepted payment says so.
    """
    if not header_value:
        return False, "no X-PAYMENT header"
    try:
        payload = json.loads(base64.b64decode(header_value).decode())
    except Exception:  # noqa: BLE001
        return False, "X-PAYMENT is not base64-encoded JSON"
    # json.loads returns whatever the JSON says, including a list, a string or a
    # number. The membership test below raises TypeError on an int, and a string
    # like "schemenetworkpayload" passes all three substring checks and then
    # raises on the index. /api/command calls this without a try, so either one
    # turned a priced request into an unhandled exception instead of a 402.
    if not isinstance(payload, dict):
        return False, "X-PAYMENT must decode to a JSON object"
    for field in ("scheme", "network", "payload"):
        if field not in payload:
            return False, f"payment payload is missing {field}"
    digest = hashlib.sha256(json.dumps(payload["payload"], sort_keys=True).encode()).hexdigest()
    if digest in _SEEN_PAYMENTS:
        return False, "this payment payload has already been used"
    if not accept_test_payments:
        return False, ("payment verification is not wired to a facilitator in this deployment; "
                       "set BIODAO_X402_TEST=1 for local development")
    _SEEN_PAYMENTS[digest] = time.time()
    return True, {"settled": False, "mode": "test", "tool": tool,
                  "warning": "accepted without settlement because BIODAO_X402_TEST is set"}


# Secret (challenge, response) pairs: anyone can ask this service a question only it can answer,
# which is how a later reader tells a genuine result from a copied one.
def _fingerprint_pairs(n=16):
    pairs = []
    for i in range(n):
        material = hashlib.sha256(IDENTITY.secret + f"fp{i}".encode()).hexdigest()
        pairs.append({"index": i, "challenge": material[:16], "response": material[16:48]})
    return pairs


def fingerprint_challenge():
    pair = secrets.choice(_fingerprint_pairs())
    return {"index": pair["index"], "challenge": pair["challenge"],
            "verify": "POST the index and response to /api/oml/verify",
            "scheme": "oml-1.0-style challenge/response over a service secret"}


def fingerprint_verify(index, response):
    pairs = _fingerprint_pairs()
    if not isinstance(index, int) or not 0 <= index < len(pairs):
        return {"ok": False, "reason": "unknown challenge index"}
    ok = hmac.compare_digest(pairs[index]["response"], str(response))
    return {"ok": ok, "agent": IDENTITY.agent_id,
            "reason": None if ok else "response does not match this agent's fingerprint"}


def stamp(result, tool=None):
    """Sign a result so its origin can be checked later. Applied to every tool call."""
    envelope = {"tool": tool, "issued": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "agent": IDENTITY.agent_id, "result": result}
    envelope["proof"] = IDENTITY.sign_json({k: v for k, v in envelope.items() if k != "proof"})
    return envelope


def verify_stamp(envelope):
    proof = envelope.get("proof") or {}
    body = {k: v for k, v in envelope.items() if k != "proof"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    if proof.get("digest") != digest:
        return {"ok": False, "reason": "the result does not match its digest: it was altered after signing"}
    # The key is OURS, never the envelope's. This used to verify against
    # proof["key"] -- the key the caller supplied alongside the signature -- so
    # anyone could generate a keypair, sign any body they liked, enclose their
    # own public key and have /api/verify answer {"ok": true}. That proves
    # somebody signed it, which is not a claim worth making; the question this
    # endpoint answers is whether THIS service signed it.
    #
    # An envelope naming a different key is rejected by name rather than left
    # to fail the signature check, so the reason is legible. Verifying envelopes
    # from other agents would need an explicit allowlist of known keys, not
    # whatever arrives in the request.
    if proof.get("key") != IDENTITY.public:
        return {"ok": False,
                "reason": "signed with a key that is not this service's; an envelope "
                          "carrying its own key proves nothing about who issued it"}
    if HAVE_ED25519:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            Ed25519PublicKey.from_public_bytes(base64.b64decode(IDENTITY.public)).verify(
                base64.b64decode(proof.get("signature", "")), raw)
            return {"ok": True, "agent": envelope.get("agent"), "alg": proof.get("alg")}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "reason": f"signature does not verify: {e}"}
    ok = hmac.compare_digest(IDENTITY.sign(raw), proof.get("signature", ""))
    return {"ok": ok, "agent": envelope.get("agent"), "alg": proof.get("alg"),
            "reason": None if ok else "signature does not verify"}
