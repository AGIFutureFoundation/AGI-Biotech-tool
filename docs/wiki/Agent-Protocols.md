# Agent Protocols

Three protocols let an outside agent discover this workspace, pay it, and verify that a result came from
it: x402 for payment, NANDA for discovery, OML 1.0 for identity. All three are implemented in
`server/agent_protocols.py`.

This page says plainly which parts work and which parts are a scaffold, because the distinction matters
more here than anywhere else in the product.

## Identity

An Ed25519 keypair, generated once and stored. Every result the workspace returns can be stamped and
later verified.

**Caveat, and it is a real one:** Ed25519 requires the `cryptography` package, which cannot be installed in
the current environment. The code falls back to HMAC-SHA256 with a stored secret. That is a *symmetric*
scheme — a verifier must hold the same secret, so it cannot prove authorship to a third party the way a
signature can. The fallback is honest about itself in the stamp it produces, and switching to Ed25519 is a
dependency install, not a rewrite. Until then, treat stamps as integrity checks between parties that
already share a secret, not as public signatures.

## x402 — payment

HTTP 402 is in the standard and has never had a payload. x402 gives it one: a challenge naming the price,
the asset, the settlement scheme, and the network, so an agent can decide whether to pay without a human
in the loop.

```
HTTP/1.1 402 Payment Required
{
  "price": "...", "asset": "...", "scheme": "...", "network": "...",
  "settled": false
}
```

**Nothing is wired to a facilitator.** The challenge is well-formed, the test-mode payment path accepts a
payment once, reports `settled: false`, and refuses a replay of the same payment. No value moves, and the
challenge says so in the response rather than only in documentation. This is the protocol surface an agent
needs in order to integrate, with settlement left unimplemented on purpose until there is a counterparty.

## NANDA — discovery

A signed JSON-LD AgentFacts document at `/.well-known/agent-facts.json`, following MIT's NANDA work. An
agent fetches it, learns what this workspace can do and under what terms, and verifies the signature.

The document carries the capability list, the terms, and — deliberately — **the benchmark caveat**. An agent
that discovers this service is told in the discovery document itself that the docking benchmark is 5 of 11
within 2 Å, with 9 of 11 reachable. A capability claim that omits its own error rate is how an agent ends up
trusting a number it should not, and discovery is the only place the agent is guaranteed to look.

That field is also where a stale figure does the most damage, and it was stale. For ten iterations after
the eval was widened to eleven cases it served the superseded 2 of 4 figure, signed, to every agent that
asked for it.
`tests/test_agent_protocols.py` now reads the case count out of `evals/redock.mjs` and fails if the
served note disagrees, rather than checking it against a number written down a second time.

## OML 1.0 — fingerprinting

Sentient Foundation's Open Model Licence fingerprinting: secret challenge-response pairs embedded at
build time. Present a challenge, and only the genuine artefact answers correctly, which lets you detect a
copy running without authorisation.

**A fingerprint challenge never contains its own answer.** That is the one property the scheme cannot
survive losing, and it is asserted directly in the tests.

## What is tested, and what is not

`tests/test_agent_protocols.py`, eleven cases, all offline:

| Verified | |
| --- | --- |
| Result signatures verify; tampering is rejected | ✓ |
| A signature from another result is rejected | ✓ |
| Identity is stable — a second instance loads the stored key rather than minting one | ✓ |
| AgentFacts is signed and carries the benchmark caveat | ✓ |
| The 402 challenge names price, asset, scheme and network, and says it settles nothing | ✓ |
| Test-mode payment accepts once, reports `settled: false`, refuses a replay | ✓ |
| A fingerprint challenge does not contain its answer | ✓ |

| Not verified | Why |
| --- | --- |
| Settlement | Nothing is wired to a facilitator |
| Ed25519 signing | The package cannot install here; the HMAC path is what ran |
| Every HTTP route | No port can be bound in the current environment |

## Verifying this page

```bash
.venv/bin/python -m pytest tests/test_agent_protocols.py -q
```

See also [Known Limits](Known-Limits) and [Voice and Agent Control](Voice-and-Agent-Control) for the tool
registry an agent actually calls.
