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

- [x] Unit tests for js/analysis.js interaction geometry on synthetic coordinates (iter 3)
- [x] Unit tests for js/voice.js parseCommand across the intent grammar (iter 4)
- [x] Unit tests for js/agent.js intent-to-tool mapping and enum translation (iter 6)
- [~] Docking: local rigid-body refinement built and unit-tested (iteration 7). The 4-case benchmark
      re-measurement still waits on the network, so the 2-of-4 / 2.54 A median figure stands unchanged.
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

### 2026-10-06 · Iteration 4 — the spoken-command parser under test

Done: `tests/voice.test.mjs`, fifteen cases over `parseCommand`, which is pure and needs no microphone.

Verified offline (`node --test tests/voice.test.mjs`, 15 passed):
- Thirteen plain commands reach the intent meant; a target loads with or without verb and articles.
- A four-character PDB code is read as a structure, not a gene.
- Colour and representation words map onto renderer modes; an unintelligible colour returns null
  rather than a guess, because a wrong colour is worse than none.
- "screen twelve compounds" carries limit 12, since spoken numbers arrive as words.
- Silence, "um" and unrelated speech all return unknown and never trigger an action.
- Every published example parses to the intent it is published under, so help text cannot go stale.

Bug found and fixed: gene symbols nearly all end in a digit, and a recogniser returns that digit as a
word, so "load LRRK2" arrives as "load lark two". Letter-by-letter matching never got close and the
command silently failed. A spelled-out trailing number is now also offered as a digit, both to the
vocabulary matcher and to the no-vocabulary path, so "sod one" resolves to SOD1.

Still unproven: real speech input (no microphone and no Web Speech API offline); every HTTP route.

### 2026-10-06 · Iteration 5 — investor brief, 120 s film, vertical social cut

Done: `scripts/make_investor_video.py` (new file, so it does not collide with the other session's
uncommitted edits to make_pitch_video.py) renders a nine-slide 120 s investor cut leading with what is
newly proven, plus a purpose-built 27.5 s vertical teaser. `docs/investor-brief.html` published as an
artifact with the film attached.

Verified offline:
- `ffprobe`: investor.mp4 is 120.0 s at 1920×1080; investor-vertical.mp4 is 27.5 s at 1080×1920.
- Two frames inspected. The proof slide reads correctly and a caption that touched its plate border was
  shortened before shipping.
- Shares the FIGURES table with the walkthrough film, so a number cannot differ between the two.

Discarded after inspection: letterboxing the 16:9 deck into 9:16 for social. The body text came out about
four millimetres tall on a phone, so the vertical cut was rebuilt natively at 1080×1920 with six large
cards instead.

Still unproven / blocked: narration (Higgsfield workspace out of credits, macOS speech blocked by the
sandbox, so all cuts are silent and docs/pitch_narration.txt still waits); the artifact store refused a
12.8 MB upload twice, so the page carries a 4 MB 720p copy while the 1080p master stays in the repo.
No revenue, no signed customer, and no team or raise figures: those are the user's to supply, not mine
to invent.

### 2026-10-06 · Iteration 6 — the tool registry and the voice-to-renderer seam under test

Done: `tests/agent.test.mjs`, seventeen cases over `js/agent.js` driven by a stub workspace that records
calls, so every tool runs with no browser, no structure and no network.

Verified offline (`node --test tests/agent.test.mjs`, 17 passed; all three JS suites together, 39 passed):
- Every registered tool has a snake_case name, a usable description, a valid object schema, and no
  required property it fails to declare. No duplicate names.
- The published schema carries exactly name, description and parameters, and never leaks the function.
- The seam that matters: "colour by confidence" reaches the renderer as `plddt`, and "show cartoon" as
  `cartoon+pocket`. A person says one word; the renderer answers to another.
- Seven spoken intents route to the tool meant; an unrecognised sentence offers help and executes nothing.
- An unknown tool name is refused; failures are recorded in history and re-thrown rather than swallowed;
  start and result events carry the calling source.
- load_target falls back to a gene search and says plainly when nothing matches; load_compound names the
  three ways to identify a molecule; extract_ligand refuses a structure with nothing bound.
- The four tools marked slow are the four that actually cost compute.

One test expectation of mine was wrong, not the code: another session had tightened the dock units string
from "approximate" to "unitless Vina-like score ... not kcal/mol", which is the better statement. The
assertion now checks that the field disclaims exactness rather than demanding one phrase.

Still unproven: the tools against a live workspace (needs a port and a browser); every HTTP route.

### 2026-10-06 · Iteration 7 — a pose that actually sits in its minimum

Done: `js/refine.js`, a local refinement pass over the six rigid-body degrees of freedom. The Monte Carlo
search in `dock.js` ends wherever its last accepted move happened to land, which is near a minimum rather
than in it; Vina follows every MC run with a quasi-Newton polish for exactly this reason. This is the cheap
equivalent — a pattern search with a shrinking step that only ever accepts a strict improvement, so a
refined pose cannot score worse than the one it started from. Rotations pivot on the ligand centroid, so a
rotation probe never also translates the molecule. Wired into the interactive dock path in `js/main.js`:
poses are refined and re-sorted before they are shown, and the ledger now records the refinement gain
alongside the score instead of the raw search output.

Verified offline (`node --test` over all four JS suites, 47 passed; `node --check js/main.js`;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed):
- On a synthetic carbon cup with a known seat, refinement from four different displacements never returns
  a worse score than its input, and the reported improvement is never negative.
- A pose displaced 1.8 A + 1.4 A off the seat comes back closer to it than it started.
- The input coordinate array is never mutated, so a caller can compare before and after.
- Deterministic: the same input gives a byte-identical output. No RNG in the refinement path.
- The evaluation budget is respected; a finer `minStep` never scores worse and always costs at least as much.
- `refineAll` re-sorts, because refinement can reorder a ranking, and every pose keeps its gain record.
- With translation disabled the centroid holds to within 1e-3 A, confirming the rotation pivot.

What this does not do, stated plainly: it does not change the scoring function and it does not move
torsions. A pose placed in the wrong pocket is still in the wrong pocket, and a tighter fit to an
unvalidated score is not a better prediction.

Still unproven / blocked: whether refinement improves the 4-case re-docking benchmark. That needs
structures from the RCSB and the network is blocked, so the published figure stays what it was measured at
— 2 of 4 within 2 A, median 2.54 A — and is not restated as improved. Five Python failures remain in
`tests/test_server_lifecycle.py`; all five need to bind a local port, which this sandbox refuses.
