# Build loop

One focused item per iteration, every 20 minutes, with what was verified and what stayed unproven.
Order of preference: offline unit tests, then scoring improvements testable on synthetic geometry,
then wiki content, then whitepaper refinements.

## Session constraints (2026-10-05)

The sandbox blocks binding local ports and outbound network to pypi.org and the structure databases.
So: no server, no browser, no live evals, no video render. Everything below is offline work. When the
sandbox is relaxed (`sandbox.network.allowLocalBinding: true`, plus network allowances), the first
item to run is `node evals/redock.mjs`, because the headline benchmark is the weakest claim.

## Queue

- [ ] Unit tests for js/analysis.js interaction geometry on synthetic coordinates
- [ ] Unit tests for js/voice.js parseCommand across the intent grammar
- [ ] Unit tests for js/agent.js intent-to-tool mapping and enum translation
- [ ] Docking: wider search budget and a rescoring pass, measured against the 4-case benchmark
- [ ] docs/wiki/ pages ready to paste into the GitHub wiki
- [ ] Ed25519 signing once `cryptography` can install

## Iterations

### 2026-10-05 · Iteration 1 — protocol layer under test

Done: `tests/test_agent_protocols.py`, 11 cases over the x402, NANDA and OML code paths.

Verified offline (`.venv/bin/python -m pytest tests/test_agent_protocols.py -q`, 11 passed):
- A result signature verifies, and both a tampered payload and a swapped signature are rejected.
- The identity is stable across instances: a second `Identity()` loads the stored key rather than minting one.
- AgentFacts is signed and carries the benchmark caveat inside the discovery document itself.
- The 402 challenge names price, asset, scheme and network, and says it settles nothing.
- Free tools are not metered; `describe_scene` has no price, `dock` does.
- A payment is refused without a facilitator; malformed and incomplete payloads are refused first.
- Test mode accepts once, reports `settled: false`, and refuses the same payload on replay.
- A fingerprint challenge never contains its own answer.

Still unproven: settlement (nothing is wired to a facilitator); Ed25519 signing (package unavailable
here, so the HMAC path is what ran); every HTTP route, since no port can be bound this session.
