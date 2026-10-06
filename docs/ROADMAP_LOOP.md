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

### 2026-10-05 · Iteration 2 — pitch video and deck, offline

Done: `scripts/make_pitch_video.py` renders ten designed slides with Pillow, depicts public-record
reference drugs with RDKit, and assembles a 110.0 s H.264 cut with ffmpeg; no browser, no network.
`docs/pitchdeck.html` published as an artifact with the film attached as an asset, the benchmark table,
roadmap, limits and the ask. Loop rescoped to job c65e6f33 (every 20 min) with a one-shot stop 879b69ab
at 23:13; the new prompt checks `git status` first because another session commits here concurrently.

Verified: `ffprobe` reports 110.0 s, 1920×1080, H.264; two slides inspected as frames and a footer
collision fixed before shipping.

Still unproven / blocked: narration — the requested Higgsfield voice failed on "out of credits", and
macOS `say` is blocked by the sandbox (produced a silent 4 KB file, −91 dB), so the cut is silent and
`docs/pitch_narration.txt` waits for either path to open. Everything from iteration 1 remains blocked.

### 2026-10-05 · Iteration 3 — interaction analysis under test

Done: `tests/analysis.test.mjs`, seven cases on synthetic geometry: a five-residue protein and a probe
ligand placed so each interaction class has exactly one planted hit.

Verified offline (`node --test tests/analysis.test.mjs`, 7 passed):
- Parallel stacking with PHE at 3.7 Å, hydrogen bond to SER OG at 2.9 Å, salt bridge to ASP at 2.9 Å,
  hydrophobic contact with LEU at 3.8 Å; a residue 30 Å away never appears.
- Geometric ring detection accepts a flat unsaturated ring and rejects a puckered one and a saturated one.
- A ligand moved out of range yields an empty, honest summary.
- Pocket variant overlap: lining count, pathogenic count at the 0.564 cut-off, enrichment arithmetic.
- Series clustering: union by Tanimoto, best scorer per series, compounds without fingerprints left out.

Bug found and fixed by the tests: the per-residue detail list capped at 12 entries, so dozens of
hydrophobic ring contacts crowded out the single stacking record a chemist wants. Counts were right; the
detail was lost. Only hydrophobic details are capped now.

Still unproven: the same thresholds on real complexes (needs network); every HTTP route (needs a port).
