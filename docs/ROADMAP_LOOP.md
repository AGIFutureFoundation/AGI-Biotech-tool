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
- [~] Docking: local rigid-body refinement (iteration 7), torsional refinement (iteration 8) and binding-mode
      clustering with a discrimination check (iteration 10), all unit-tested on synthetic geometry. The
      four-case set is retired — it became four of the eleven when evals/redock.mjs was widened — and the
      standing figure is 5 of 11 within 2 A, 9 of 11 reachable. That eleven-case result has NOT been
      re-measured since the refinement work landed; it still waits on the network. So the refinement must
      not be restated as improving it. (Historical only: the retired four-case set read 2 of 4, median
      2.54 A.)
- [ ] Calibrate the discrimination margin in js/poses.js against the re-docking benchmark — how large a score
      gap must be before the better-scoring pose is reliably the closer one. Needs the network. Until then the
      default is a stated convention and says so in its own output.
- [~] **Scoring-side work.** `js/rescore.js` adds three terms vinaScore lacks — buried unsatisfied polar,
      metal coordination, internal clash — unit-tested on synthetic geometry including a corrected ranking
      inversion (iter 20). **Not yet wired into the dock path, and the weights are not calibrated.**
- [ ] Calibrate the rescoring weights in `js/rescore.js` against the eleven-case benchmark: how often does
      each term flip a ranking the right way, and what weight maximises that. Needs the network. Until then
      every result the module returns carries `WEIGHTS_ARE_UNCALIBRATED`.
- [ ] Wire `rerank` into `doDock` once the weights mean something. Rescoring with invented weights in the
      product would be worse than not rescoring at all; it belongs behind calibration, not in front of it.
- [x] docs/wiki/ pages ready to paste into the GitHub wiki (iter 9), guarded by tests/wiki.test.mjs
- [x] Pocket detection under test on synthetic geometry (iter 11) — the one untested stage of the chain
- [x] Dynamics force field under test, with a gradient check (iter 12)
- [x] Planarity term in `js/md.js` swapped for the exact-gradient one (iter 13). Measured impact on where
      minimisation lands: negligible — 0.002 to 0.006 A RMSD, energies agreeing to 0.001. The fix is correct
      and removes a latent hazard; it is not a result anyone would notice.
- [x] Structure parsers under test, and insertion codes fixed (iter 14)
- [x] Provenance ledger under test by actual tampering, plus a standalone export verifier (iter 15)
- [x] Database layer failure behaviour under test with a stubbed fetch (iter 16)
- [x] Whitepaper figures corrected and put under test (iter 17)
- [~] tests/claims.test.mjs extended to docs/investor-brief.html (iter 18). docs/pitchdeck.html is still
      held back: the other session has uncommitted changes to it, and a guard that fails on someone else's
      in-flight edit is a bad guard. Add it once that file is clean.
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

### 2026-10-06 · Iteration 8 — the torsions the search only sampled coarsely

Done: `js/torsion.js`. Iteration 7 tightened a pose as a rigid body; a ligand with rotatable bonds has more
freedom than that, and the Monte Carlo search samples those dihedrals coarsely. This searches them directly:
`rotateTorsion` turns the atoms on one side of a bond about that bond's own axis, `refineTorsions` runs a
pattern search over every rotatable bond with a shrinking angular step, and `refineFlexible` alternates
rigid-body and torsional passes until a full pass of both stops helping. Every stage accepts only strict
improvements. The interactive dock path in `js/main.js` now calls `refineAllFlexible`, and the ledger records
the method as rigid-body *and* torsional refinement rather than rigid-body alone.

Verified offline (`node --test` over all five JS suites, 61 passed; `node --check js/torsion.js js/main.js`;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed). The geometry checks are exact and make no reference to
the scoring function, which is the point of them:
- A torsion rotation preserves **every** bond length to 1e-4 A and every bond angle to 1e-4 rad. The hinge
  atoms and the whole fixed side do not move at all. A rotation followed by its inverse returns the input.
- It moves the dihedral spanning its own bond by exactly the angle asked for, and the two flanking dihedrals
  by nothing — so one call changes one degree of freedom, not several.
- A six-carbon sp3 zig-zag yields exactly the three rotatable bonds the geometry implies; the two terminal
  bonds are correctly excluded, and the smaller side is always the one that moves.
- A bond whose atoms have collapsed onto each other is skipped rather than normalised by zero; coordinates
  never become NaN.
- Search discipline: never worse than its input from four starting bends, bond lengths still 1.53 A after a
  full refinement, byte-identical determinism, input array never mutated, budget respected, a finer angular
  step never worse. A rigid ligand costs exactly one scoring call and is returned unchanged.
- `refineFlexible` is never worse than `refinePose` alone, and a pose already settled stops after one pass
  instead of burning the budget. `refineAllFlexible` re-sorts and keeps a gain record per pose.

One bug of mine, found by the test rather than by reading: `refineFlexible` seeded its running best at
Infinity, so the first pass always compared favourably and the loop could never stop on it. A settled pose
cost two passes where one would do. Now seeded from the pose's own starting score.

Still unproven / blocked: whether torsional refinement improves the 4-case re-docking benchmark. That needs
structures from the RCSB and the network is blocked; the published figure stays what was measured — 2 of 4
within 2 A, median 2.54 A — and is not restated. Nor does this add an internal-strain term: `vinaScore` sees
protein-ligand contacts only, so a torsion that folds the ligand onto itself costs nothing in this search,
which is why `refineFlexible` polishes a conformer rather than generating one. Five Python failures remain in
`tests/test_server_lifecycle.py`; all five need to bind a local port, which this sandbox refuses.

### 2026-10-06 · Iteration 9 — the wiki, with a test that reads it

Done: `docs/wiki/`, nine pages written as one file per GitHub wiki page — `Home`, `Getting-Started`,
`Data-Sources`, `Docking-and-Scoring`, `Voice-and-Agent-Control`, `Agent-Protocols`, `XR-and-Hand-Tracking`,
`Provenance-Ledger`, `Testing`, `Known-Limits` — plus `_Sidebar.md` for the navigation rail and a `README.md`
with the push-to-`.wiki.git` recipe. `docs/WIKI.md` is untouched: that stays the one long page for someone
reading the repository top to bottom, while these are short pages for someone who arrived from a search
result with one question.

Two editorial decisions worth recording. `Home` leads with the re-docking failure, not the feature list —
the 2-of-4 table is the first thing under the first heading. And `Known-Limits` is its own page linked from
the front page rather than a section at the bottom of a long document, because a limits section nobody
scrolls to is decoration.

Facts on the pages were read out of the code, not recalled: the 19 intents from `INTENTS` in `js/voice.js`,
the 22 tools and their six `slow` flags by instantiating `buildTools` against a proxy, and the 21 database
hosts by extracting every `https://` literal from `js/api.js`.

Done also: `tests/wiki.test.mjs`, thirteen cases, because prose is not compiled and so rots silently.

Verified offline (`node --test` over all six JS suites, 74 passed; `.venv/bin/python -m pytest tests/ -q`,
1438 passed):
- Every internal wiki link resolves to a page that exists; the sidebar and the page set agree in both
  directions; no page is orphaned from both Home and the sidebar; every page opens with exactly one H1.
- No page gives the docking score an energy unit except to disclaim it.
- The benchmark figure is checked, not trusted: any line claiming "3 of 4" or "4 of 4 within 2 A" fails, any
  median other than 2.54 A fails, and Home, the docking page and the testing page must each say the figure
  was carried forward rather than re-measured.
- `Known-Limits` must cover the wet lab, Ray-Ban, settlement, the blockchain claim, revenue and Ed25519;
  the ledger page must say in as many words that it is not a blockchain, and why.
- No line may assert narration, settlement or lab validation as done unless the line negates it.
- The intent count on the wiki is compared against `INTENTS.length` and every intent name must appear, so a
  new intent cannot ship undocumented. Every host listed on the data-sources page must be one `js/api.js`
  actually calls.

The guards were mutation-checked rather than assumed: changing Home's table to "4 of 4 within 2 A, median
1.20 A" fails the benchmark test, and misspelling one link target as `Docking-And-Scoring` fails the link
test. Both were reverted. Two of my first-draft checks were too crude and flagged their own disclaimers —
"it looks like a kcal/mol number" and "Nothing here has been validated in a wet lab" — so both now allow a
negated or warning line. That is the honest limit of a regex over prose: it catches a confident false
claim, not a carefully hedged one.

Still unproven / blocked: the pages are not pushed. That needs `git push` to `AGI-Biotech-tool.wiki.git`,
and the stored GitHub token is invalid, so publishing waits on the user running `gh auth refresh`. Two
figures on the wiki are marked carried-forward because they cannot be re-measured here: the re-docking
benchmark (2 of 4 within 2 A, median 2.54 A, needs the RCSB) and MD throughput (needs the server). Five
Python failures remain in `tests/test_server_lifecycle.py`; all five need to bind a local port.

### 2026-10-06 · Iteration 10 — saying out loud when the score did not choose

Checked first whether the obvious scoring-side gap was already closed, and it was: another session's
`tests/test_vina_score_port.py` already runs `js/dock.js` and `server/vina_score.py` over the same real
geometry and compares every term, the atom typing behind every term, the rotatable-bond count and the H-bond
list. So no duplicate was written.

Done instead: `js/poses.js`, which addresses the benchmark's *diagnosed* failure mode rather than its number.
The two complexes this tool gets wrong are a long flexible ligand in a shallow groove, where many placements
score within a hair of each other and the search returns whichever won by a rounding error. `dockLigand`
already thins poses to 1.5 A apart and returns them sorted, and a sorted table reads as a verdict. This
groups the survivors into binding modes by leader clustering in score order at a coarser cutoff, then
compares the top two modes and reports whether the gap between them clears a margin. When it does not, the
workspace says so: *the next-best sits N A away and only M behind, so this ranking is not a preference.* The
sentence goes into the toast and the numbers go into the provenance record next to the score —
`bindingModes`, `topModeGap`, `discriminates` — so the caveat travels with the result into any export.

The margin is a convention and is labelled one. Calibrating it means asking how large a score gap has to be
before the better-scoring pose is reliably closer to the crystal, which needs the benchmark, which needs the
network. So the default is a cautious round number, every caller can override it, and the exported constant
`MARGIN_IS_UNCALIBRATED` is appended to every verdict the module produces. A new queue item records the
calibration as owed work rather than letting the convention harden into a fact.

Verified offline (`node --test` over all seven JS suites, 88 passed; `node --check js/poses.js js/main.js`;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed):
- Three synthetic knots at known separations cluster into exactly three modes with populations 3, 2, 1;
  every pose lands in exactly one mode and no index is invented.
- Modes come out best-score-first and each is led by its own best-scoring member. `spread`, `best`, `worst`
  and `rmsdToBest` were checked against hand-computed values.
- A cutoff past every separation gives one mode; a cutoff under the intra-knot wobble gives one mode per
  pose. An empty or null list returns nothing rather than throwing.
- A 0.8 gap is reported as discriminating; a 0.1 gap is reported as not a preference, and the note carries
  how far away the rival pose actually is. A gap exactly at the margin counts as clearing it.
- **One mode returns `null`, not `true`**: the absence of a rival is not evidence that the score chose. Zero
  poses is reported, not guessed at.
- Every verdict that leans on the margin includes the uncalibrated disclaimer, and the disclaimer is itself
  asserted to actually disclaim rather than merely exist.
- Clustering does not mutate the poses it was given, including not re-sorting the caller's array in place.

Also updated `docs/wiki/Docking-and-Scoring.md` with a binding-modes section; `tests/wiki.test.mjs` still
passes, so the new prose did not break the link graph or smuggle in an uncalibrated claim.

Still unproven / blocked: the margin's value, as above. Whether surfacing modes changes the 4-case benchmark
outcome — it should not, since nothing about the score changed, but that is an expectation and not a
measurement, and the benchmark needs the RCSB. The published figure stays 2 of 4 within 2 A, median 2.54 A,
and is not restated. Five Python failures remain in `tests/test_server_lifecycle.py`; all five bind a local
port, which this sandbox refuses.

### 2026-10-06 · Iteration 11 — the one stage of the chain nobody was testing

Done: `tests/pockets.test.mjs`, twelve cases over `findPockets`. Both remaining queue items need the
network, so the pick came from the preference order: pocket detection was the only stage of the docking
chain with no JavaScript test at all. It matters more than its position suggests — if it ranks a surface
dent above a buried cavity, the search, the refinement, the scoring and the analysis all run correctly
against the wrong site, and nothing in the output says so. A wrong answer from a wrong pocket is
indistinguishable from a wrong answer from a wrong score.

Receptors built so the cavity is known by construction: Fibonacci-sphere shells whose interior free volume
follows from the radius and the 2.8 A occlusion margin, a solid ball on a 2.4 A lattice with no interior at
all, and a hemispherical dimple pressed into a plate.

**No defect found.** Every behaviour put to it was correct, which is the honest result and is why the value
of this iteration is the guard rather than a fix.

Verified offline (`node --test` over all eight JS suites, 100 passed; `.venv/bin/python -m pytest tests/ -q`,
1438 passed). Expected numbers were measured against the implementation first, then asserted with
tolerances tight enough to fail on a real change — a centre to 0.5 A, a buriedness to 0.02:
- A radius-9 shell gives exactly one pocket, centred within 0.5 A of the cavity centre, volume 900–1200 A^3
  against a predicted ~1000, buriedness above 0.95. The nearest wall atom is over 6 A from the centre and
  under 10, so the centre is demonstrably inside the cavity rather than on the wall or outside it.
- Internal consistency per pocket: volume equals point count times cell volume, buriedness in (0, 1],
  druggability in [0, 1], score finite and positive, centre finite.
- Two cavities at different radii are both found and the larger ranks first, with the right centres and
  the more druggable call going to the bigger one.
- A convex solid reports **no** pocket: lattice interstices are not cavities.
- A shallow dimple 25 A from a sealed cavity does not outrank it. In fact it does not register at all,
  which is the right answer — an open dimple is not a binding site.
- Excluding a contiguous cap of wall opens the pocket as it should: buriedness 0.986 to 0.837, score 995 to
  489, and the centre of the buried region retreats to x = −1.4, away from the opening.
- The answer is stable across grid spacings of 1.0, 1.25 and 1.5 — centre within 0.5 A, buriedness within
  0.004, volume spread under 15 percent.
- `maxPockets` caps the list without disturbing the ranking; a structure with no polymer atoms, and one with
  every atom excluded, both return an empty list rather than throwing.
- Every pocket names lining residues that are real indices into the structure, and carries a readable label.

One result worth recording because it surprised: removing every other atom from the shell halves its atom
count but leaves the survivors about 2.9 A apart, which still occludes a 2.8 A probe. The cavity stays
sealed and its volume grows slightly as the wall thins. That is physically right, not a bug, and it is now
asserted so a future change cannot quietly turn a sealed wall porous.

The suite was mutation-checked rather than assumed: loosening the buriedness threshold from 19 of 26
directions to 3 fails six of the twelve cases. `js/dock.js` was restored byte-for-byte afterwards, confirmed
by an empty `git diff`.

Also updated `docs/wiki/Testing.md` with the three newest suites and the 100-test count;
`tests/wiki.test.mjs` still passes.

Still unproven / blocked: pocket detection against real crystallographic cavities, which needs structures
from the RCSB. Synthetic shells prove the algorithm does what it claims; they do not prove its thresholds
are right for real protein surfaces, which are rougher and rarely sealed. The 4-case benchmark was not
re-measured — 2 of 4 within 2 A, median 2.54 A stands. Five Python failures remain in
`tests/test_server_lifecycle.py`; all five bind a local port.

### 2026-10-06 · Iteration 12 — the force must be the gradient, and in one place it was not

Both open queue items still need the network, so the pick came from the preference order again: the dynamics
engine was the last part of the chain with no JavaScript test. Done: `tests/md.test.mjs`, twenty-one cases
over `buildLigandFF`, `ligandForces`, `minimize` and `MDEngine`, and `js/planarity.js`, a replacement for one
term that the tests showed was wrong.

The centrepiece is a central finite-difference gradient check in double precision. A force field has one
property worth more than all the others — the force must be the negative gradient of the energy — and when
it fails nothing in the output says so; the molecule just behaves slightly oddly in a way that reads as
physics being hard. Running the check at three step sizes makes second-order convergence visible rather
than assumed: 3.18e-5 at h=1e-3, 3.18e-7 at 1e-4, 2.27e-9 at 1e-5. Bonds, angles and non-bonded repulsion
are exact.

**The finding: the planarity term in `js/md.js` is not the gradient of its own energy.** It computes the
plane normal from the three substituents and then treats it as fixed, so the force misses the normal's
dependence on where those substituents are. Measured against the finite difference, it is about 19 percent
off when the sp2 centre is pyramidalised by 0.3 A, falling to 0.9 percent by 1.6 A — worst at small
displacement, which is precisely the regime a minimiser spends its time in. The FIRE minimiser steers on the
sign of F·V together with the energy, so an inconsistent pair can make it shrink a timestep it should be
growing, and a force that is not a gradient does no definite work.

This was nearly missed. The first gradient check of the term returned 3e-10 and looked clean; that geometry
had the substituent plane distorted too, and the errors happened to cancel. Pyramidalising the centre alone,
holding the substituents still, is what exposed it.

`js/planarity.js` is the corrected term, differentiated properly through the normalised cross product, with
the fourth derivative taken as minus the sum of the other three so the forces sum to zero in floating point
as well as in algebra. It is a new file rather than an edit to `js/md.js` because another session is working
in that file; the swap is one line and is now a queue item.

Verified offline (`node --test tests/*.test.mjs`, 121 passed; `node --check js/planarity.js`;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed):
- One force-field term per piece of topology; non-bonded pairs are exactly the 1-4 and 1-5 pairs, so nothing
  is double-counted against a bond or angle term. Bond rest lengths shorten with order, triple < double <
  single, with a C-C single bond at 1.52 A. The 1-3 restraint distance matches the law of cosines at 109.5
  degrees to 1e-3 A.
- A bond at rest costs nothing; stretched by dr it costs exactly k·dr² to 1e-6. Repulsion is exactly zero at
  and beyond its cutoff, rises monotonically inside it, matches krep·(repel−r)² to 1e-6, and pushes the pair
  apart rather than together.
- Forces sum to zero to 1e-9 — Newton's third law, which a sign error in any term would break.
- Minimisation lowers the energy, returns every bond to within 0.1 A of its rest length, produces no NaN, and
  moves an already-settled geometry by under 0.05 A on a second pass.
- Dynamics over 400 steps: no NaN, both bonds still between 1.2 and 2.0 A so the molecule did not come apart,
  kinetic temperature physical for a 300 K bath, finite ligand RMSD. A second relaxation never raises the
  energy.
- A frozen protein does not move by a single float. The steric guard separates a real clash, shifts no atom
  further than its 0.25 A limit, reports the fix count, and leaves an exactly coincident pair alone instead
  of dividing by zero.
- The replacement restraint: zero at planarity, monotonically rising with displacement, gradient-exact to
  1e-7 at every pyramidalisation tested, momentum-conserving to 1e-12, and silent on degenerate collinear
  substituents where no plane exists.
- The md.js defect is asserted as a bounded fact in its own test, between 5 and 50 percent, so the number
  cannot drift unnoticed and whoever fixes the term is told to delete the test.

Two of my own test expectations were wrong rather than the code. The repulsion test first moved a bonded atom
and measured the bond term by mistake, which drowned the effect it was looking for; it now strips the bonded
terms and varies one pair. And `stericGuard` looked broken in a probe — it returned undefined and the ligand
did not move — until reading it showed it writes to the engine's own `lp` buffer, records its count in
`lastGuardFixes`, and deliberately skips coincident atoms. The code was right on all three counts.

Still unproven / blocked: whether fixing the planarity term changes any result a user sees. It should matter
most to conformer relaxation, but that is an expectation and not a measurement, and measuring it means
running the OpenMM comparison, which needs the server. The 4-case benchmark was not re-measured — 2 of 4
within 2 A, median 2.54 A stands. Implicit solvent and short timescales remain the honest limits of the
dynamics regardless of this fix. Five Python failures remain in `tests/test_server_lifecycle.py`; all five
bind a local port.

### 2026-10-06 · Iteration 13 — landing the fix, and measuring that it barely matters

Done: swapped the planarity term in `js/md.js` for `planarityForce` from `js/planarity.js`, removed the
superseded implementation rather than leaving it in place unused, and replaced the test that recorded the
defect with the test that proves the fix landed. `js/md.js` was last touched by an early commit of mine, is
clean in the working tree, and the other session is working in `scripts/make_pitch_video.py` and
`docs/pitchdeck.html`, so a one-line swap there was safe to make.

Verified offline (`node --test tests/*.test.mjs`, 123 passed; `node --check js/md.js`;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed; the JS-to-Python scoring cross-check, 13 passed):
- `ligandForces` as a whole — bonds, angles, 1-4 restraints, planarity and repulsion together — is now
  gradient-exact to under 1e-6 at every pyramidalisation tested, on a fixture that exercises both the
  planarity term and the 1-4 restraints. Before the swap the same check failed at 6.26e-2.
- The complete force field still conserves momentum to 1e-9 after the change.
- The superseded in-place implementation is asserted **gone**, not merely unused: a second implementation
  left behind is a second implementation someone calls by mistake.
- Mutation-checked: reinstating the old term inline fails the new gradient test at 6.26e-2 with z = 0.1 A.
  `js/md.js` was restored afterwards and `git diff --stat` confirmed only the intended 5-insertion,
  13-deletion swap remained.

**The honest part.** Last iteration left "whether the fix changes any result a user sees" unproven. Part of
that is measurable offline, so it was measured: minimise a conjugated fragment with two sp2 centres from
three different starting distortions, with the old term and the new one, and compare. The answer is that it
barely matters. Residual out-of-plane distance is at most 0.001 A either way, final energies agree to about
0.001, and the minimised geometries differ by 0.002 to 0.006 A RMSD. Both terms flatten an sp2 centre; they
only disagree about the force on the way there, and FIRE's line search absorbed the difference.

So the fix is correct, it removes a latent hazard — a force that is not a gradient does no definite work, and
the minimiser steers on the sign of F·V together with the energy — and on the evidence available it is not a
result anyone would notice. Both halves of that belong in the record. The original 19 percent figure was a
real defect in the force, and it is also true that it did not propagate to the geometry.

Still unproven / blocked: energy conservation over a long trajectory, where an inexact force would show up
most clearly. The Langevin thermostat dominates the energy budget at these timescales, so measuring
conservation means running without it and comparing against the OpenMM backend — which needs the server. The
4-case benchmark was not re-measured; 2 of 4 within 2 A, median 2.54 A stands. Implicit solvent and short
timescales remain the honest limits of the in-browser dynamics. Five Python failures remain in
`tests/test_server_lifecycle.py`; all five bind a local port.

### 2026-10-06 · Iteration 14 — the stage upstream of everything

Both open queue items still need the network or a package install, so the pick came from the preference
order: the structure parsers were the last untested stage, and the only one upstream of pocket detection.
A column misread there does not announce itself — it comes out the other end as a slightly wrong answer
that looks like a slightly wrong score.

Done: `tests/structure.test.mjs`, seventeen cases over `parsePDB`, `parsePDBFrames`, `parseMmCIF`,
`parseMolblock` and `parseAny`, with fixtures hand-written from the PDB format specification rather than
from the implementation's current behaviour, so the expectations come from the format and not from the code.

**The finding: PDB insertion codes were dropped.** `buildResidues` keyed residues on chain, sequence number
and residue name, with no insertion code, so ALA 100 and ALA 100A collapsed into one four-atom residue —
and because the C-alpha is assigned by scanning, the merged residue silently kept only the *second* C-alpha
it saw. Antibody CDR loops are numbered 100, 100A, 100B, so this is not an exotic case. The consequences are
concrete: the elastic network model in `js/md.js` anchors every atom of a residue on its C-alpha, so half an
inserted loop would ride on the wrong anchor; residue counts come out short; and pocket lining labels name
one residue where there are two.

Fixed in `js/structure.js`: the insertion code is read from column 27 in `parsePDB`, from
`pdbx_PDB_ins_code` in `parseMmCIF` so both formats group residues identically, stored per atom, included
in the residue key, and exposed on each residue as `iCode` plus a ready `label` of the form `ALA100A`. The
file was clean in the working tree and last touched by an early commit of mine; the other session is in
`scripts/make_pitch_video.py` and `docs/pitchdeck.html`.

Verified offline (`node --test tests/*.test.mjs`, 140 passed; `node --check js/structure.js`;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed; the JS-to-Python scoring cross-check on real
crystallographic geometry, 13 passed — so the residue-grouping change shifted no score):
- Every field of an ATOM record read out of its own columns: name, residue, chain, sequence number,
  coordinates, B-factor, element, and ATOM versus HETATM.
- **Coordinates packed with no separating space** — `-123.456-123.456 -99.999` — still parse as three
  numbers. This is the test that proves the parser is column-based and not splitting on whitespace.
- Element from columns 77-78 when present, inferred from the atom name when blank. An atom named `CA` is
  carbon in a residue and calcium as an ion, decided purely by which column the letters start in, which is
  the actual PDB convention. Two-letter elements FE, CL and ZN survive inference.
- Only one alternate conformer is kept, not both merged into the same residue.
- Insertion codes: three residues where there were two, each keeping its own C-alpha, with `ALA100A`
  labelled distinctly from `ALA100`, and every atom mapped to the residue it was written under. Asserted
  for mmCIF as well, where `?` correctly means no insertion code.
- A multi-model file reads the first model only unless `allModels` is passed; `parsePDBFrames` returns one
  frame per model with the right coordinate count.
- A standard residue written as HETATM is promoted back to polymer — otherwise a pocket detector would carve
  a hole in the protein surface where a selenomethionine sits — while an actual ligand stays a heteroatom.
  Waters and ions are classified apart from the chain.
- CONECT bonds two heteroatoms 2.4 A apart, which distance perception alone will not bond; removing the
  CONECT line leaves them unbonded, so the first assertion means something.
- Bond perception finds exactly the three bonds a backbone fragment implies and does not bond an atom 30 A
  away. A molblock is read from its counts line and its bond block rather than re-perceived. `parseAny`
  dispatches on content, not only on the file name. Blank and junk input parse to an empty structure instead
  of throwing.

Mutation-checked: reverting the residue key to its old form fails both insertion-code tests, in the PDB and
the mmCIF path. `js/structure.js` was restored and `git diff --stat` confirmed only the intended
11-insertion, 3-deletion change remained.

Still unproven / blocked: the parsers against real files from the RCSB, which is where the awkward cases
live — multi-character chain IDs, hybrid-36 serial numbers past 99999, and structures with more than 62
chains. Those need the network. The 4-case benchmark was not re-measured; 2 of 4 within 2 A, median 2.54 A
stands. Five Python failures remain in `tests/test_server_lifecycle.py`; all five bind a local port.

### 2026-10-06 · Iteration 15 — tamper detection that is actually tested

Both open queue items still need the network or a package install. The pick: `js/ledger.js` was untested,
and it is the project's central honesty mechanism. Every traceability claim rests on one property — if a
record is altered, verification fails — and the wiki asserted it, the whitepaper asserted it, and nothing
checked it. A tamper-evident log whose tamper detection is untested is decoration.

Done: `tests/ledger.test.mjs`, twenty-one cases that actually tamper, and `js/ledger-verify.js`, which fills
a gap the export format implied but never provided.

**The gap.** `js/ledger.js` promises an export "whose root hash you can anchor on-chain, in a DAO proposal,
or in a lab notebook, and later verify". There was nothing to verify it with: `Ledger.verify()` is a method
on a live Ledger that loads from localStorage, so checking a file someone emailed you meant reconstructing a
workspace around it. `verifyExport(doc, { expectedHead })` takes the document alone — no Ledger, no browser
storage, no network — and additionally checks two things the live method structurally cannot, because a live
Ledger computes them rather than reading them: that the claimed `head` is the hash the chain actually ends
on, and that the claimed `length` matches the records carried. A header disagreeing with its own body is the
first thing a careless forgery gets wrong.

**The honest limit, now stated rather than implied.** Removing records from the *end* of a chain leaves a
chain that verifies perfectly, because the remaining prefix is a valid chain in its own right. This is a
property of hash chains, not a defect, and it was nowhere in the documentation. It is now a row in the
detection table on the wiki — the only "no" in that table — and the sole remedy, an external head hash, is
a parameter that closes it. Called without one, every result the verifier returns says in as many words that
records removed from the end would not show. An "ok" that quietly means "ok except for the part I cannot
check" is worse than no check at all.

Verified offline (`node --test tests/*.test.mjs`, 161 passed; `node --check js/ledger-verify.js`;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed):
- Tampering caught, each at the right index with the right reason: editing a score; **deleting the
  "not kcal/mol" caveat**, which is detected like any other edit because the caveat is a hashed field and
  not a note on a page; reordering two records; splicing one out of the middle; renumbering an index;
  forging the header's head or length.
- The careful forger's move — editing a payload *and* re-hashing the record to cover it — still fails, at
  the **following** record, whose link now dangles. That is the chain doing the one job it exists for.
- Truncation verifies clean, asserted as a fact so nobody later writes documentation claiming otherwise;
  and against an anchored head the missing record shows, with the reason naming end-removal.
- An export survives a JSON round trip and still verifies. This matters more than it looks: the canonical
  string hashes the payload with `JSON.stringify`, so a round trip that reordered keys would make an
  untouched record fail. It does not, and that is now proven rather than assumed.
- The standalone verifier agrees with the live one on a real chain. `js/ledger.js` keeps `canonical()`
  private, so this is the cross-check: if the two disagreed about what string gets hashed, every hash would
  mismatch and the test would fail. It is the guard against the two drifting apart.
- Malformed documents — null, a number, a string, an empty object, a records field that is not an array, a
  record with no hash — are rejected with a stated reason rather than throwing.
- Every result reports its own limits, and the human summary distinguishes an anchored pass from an
  unanchored one instead of printing the same reassuring line for both.
- Empty ledger at genesis; clear returns to genesis; appending after a clear starts a fresh chain; append
  emits an event carrying the record so the UI cannot fall out of step.
- The UI line a person reads marks a dock score `(est.)` and carries no energy unit — the third place that
  has to agree the number is not kcal/mol, after the record and the wiki. An unknown record kind falls back
  to its name rather than rendering "undefined".

Mutation-checked: removing the re-hash comparison from `Ledger.verify()` fails two cases, including the one
that checks the estimate caveat cannot be stripped. `js/ledger.js` was restored, confirmed by an empty
`git diff`.

One observation worth recording rather than ignoring: one Python run reported 1435 passed where two
consecutive clean runs before and after reported 1438, with 1499 collected throughout. The other session was
mid-write in `scripts/make_pitch_video.py` — 90 lines changed in the working tree — during that reading, so
the dip was transient and in its area, not a regression from this work.

Still unproven / blocked: anchoring a head hash anywhere external, which is the only thing that makes
truncation detectable in practice. That needs a network and a counterparty, so the parameter exists and is
tested while the practice does not yet. The ledger also still proves provenance and not correctness — a
tamper-evident record of an unvalidated docking score is an unvalidated docking score. The 4-case benchmark
was not re-measured; 2 of 4 within 2 A, median 2.54 A stands. Five Python failures remain in
`tests/test_server_lifecycle.py`; all five bind a local port.

### 2026-10-06 · Iteration 16 — what happens when a source does not answer

Both open queue items still need the network or a package install. The pick: `js/api.js` was untested, and
the wiki's Data Sources page makes a specific claim about it — "a failed lookup is reported as a failed
lookup ... it does not fill the gap with a plausible number." That is the second published claim in two
iterations that nothing checked, and like the ledger's it is checkable offline, because the thing being
tested is how the module behaves when a request *fails*, and a stubbed `fetch` fails on demand far more
reliably than a real one.

Done: `tests/api.test.mjs`, eighteen cases. Every test installs its own `fetch` stub, records what was
requested, and asserts both the result and the requests made. Nothing reaches the network — the stub would
throw if anything tried.

The property worth the most here is not about data at all. The CORS fallback re-sends a failed request
through the local server's read-only proxy, and it must never do that to a POST: replaying a request body
because the first attempt looked like a CORS failure is a silent duplicate submission, invisible until it is
very much not. Two cases pin it down, one for a thrown failure and one for an HTTP status, and both assert
that nothing with a body ever reaches `/api/proxy`.

Verified offline (`node --test tests/*.test.mjs`, 179 passed; `.venv/bin/python -m pytest tests/ -q`,
1438 passed):
- A 404 and a 503 both throw, with the message naming the host that failed and the status it failed with, so
  a failure cannot be read as "this protein has no data" — a different and much worse statement.
- "No hits" and "could not ask" stay distinguishable: a search that genuinely returns nothing gives
  `{ total: 0, ids: [] }`, while a source that cannot be reached rejects. Both are representable and they do
  not look alike.
- A failed GET is retried exactly once through the proxy, for the URL originally wanted, decoded and
  compared — one retry, not a loop.
- A POST is never replayed, by either failure route. An aborted request is not retried, so a timeout is not
  served twice.
- A 204 reads as `null` rather than a parse error. A repeated lookup is served from cache and not
  re-requested. A failed lookup is evicted from the cache, so one flaky moment does not poison a source for
  the rest of the session.
- A structure file falls back from PDB format to mmCIF and tags the result as cif so the caller parses it
  correctly; with neither format available it fails rather than handing back empty text that would parse to
  a zero-atom structure.
- Asking about an empty identifier list makes no request at all. The failure contract is spot-checked across
  three further providers rather than assumed from one. Every provider URL is https or a local path.

Three of my own test expectations were wrong, not the code — two were guessed method names, and the third was
more interesting: a test meant to prove cache eviction passed its 502 through to a successful proxy retry and
so measured the wrong thing entirely. **The proxy fallback catches any failure of a GET, not only a CORS
refusal**, so a 502 from a source is retried through the proxy too. That is defensible, since the proxy may
be allowed where the browser is not, but it means one lookup can cost two requests, and it is not obvious
from the call site. It is now a test of its own and a note on the wiki page.

Mutation-checked: removing the `body ||` condition from the retry guard fails both POST cases. `js/api.js`
was restored, confirmed by an empty `git diff`.

Still unproven / blocked: the providers against the live services. These tests prove the module handles
failure honestly; they say nothing about whether any given endpoint still exists, still returns the shape
expected, or has changed its pagination — which is exactly what `make reachable` and a network would check.
Response-shape drift at a public API is the most likely way this layer breaks in practice and it cannot be
caught from here. The 4-case benchmark was not re-measured; 2 of 4 within 2 A, median 2.54 A stands. Five
Python failures remain in `tests/test_server_lifecycle.py`; all five bind a local port.

### 2026-10-06 · Iteration 17 — the whitepaper had stopped being true

Both open queue items still need the network or a package install, so the pick came from the preference
order, which puts whitepaper refinements next. The whitepaper had not been touched in sixteen iterations
while the repository moved underneath it.

`docs/WHITE_PAPER.md` carries an Appendix A listing every figure it states next to the command that produces
it, and says plainly: "do not trust it, run the commands ... any figure that is not reproducible should be
treated as deleted." That is the right rule, and it had quietly stopped holding. §3.1 claimed **763 passed,
775 collected, 2,034 lines of test code** against an actual **1,438 passed, ~1,496 collected, 9,374 lines**,
and the JavaScript suites — twelve files and 179 cases at the start of this iteration — were not mentioned
anywhere in the document. Nobody had lied. The document was written once and the repository kept moving,
which is exactly what prose cannot notice.

Done, in two halves.

**Corrected.** §3.1 now carries both suite results with the measurement date, and states the five Python
failures alongside the passes with the reason they fail, rather than quoting a cleaner number. Appendix A's
rows were re-measured: test line count, Python line count, JS module count, test file counts, and the
JavaScript test total, with the stale `make test` line replaced by the command that actually produces the
figure. A new §3.1.1 lists **what the tests found** rather than only that they pass — the planarity gradient
error, the dropped insertion codes, the stacking record crowded out by a detail cap, "load lark two", the
refinement loop that could not terminate — plus the two limits documented rather than fixed: that a hash
chain cannot detect records removed from its end without an external anchor, and that the database proxy
retries any failed GET and so can cost two requests per lookup. A suite that only confirms its author's
expectations is weak evidence, and a document reporting only a pass count is making that weak argument.

**Guarded.** `tests/claims.test.mjs`, eleven cases that re-measure the document's figures from the
filesystem and fail when claim and reality disagree. Verified offline (`node --test tests/*.test.mjs`, 190
passed; `.venv/bin/python -m pytest tests/ -q`, 1438 passed):
- Test line count, Python line count, JS module count and both test-file counts are measured with the same
  commands the appendix names, and compared against the figures printed beside them.
- The JavaScript test total is checked against the number of cases declared across the suites. It agrees
  exactly: 190 declared, 190 run.
- The Python line is required to carry its failures alongside its passes, and to say why those five fail, so
  the passing count can never appear on its own.
- The benchmark figure is scanned across five published surfaces for an overstated pass rate or a median
  other than 2.54 A, and no surface may give the docking score an energy unit without disclaiming it.
- Appendix A must pair every claim with a command, with no blank rows.
- The document must state when it measured, and must still contain the defect list.

Deliberately not asserted: the exact Python collection count. The other session commits here concurrently
and adds Python tests — the figure read 1,499 and 1,496 within the same hour — so pinning it would produce a
test that fails for reasons unrelated to the claim it guards. What is asserted instead is that the document
says when it measured, which is the project's own rule for a figure that cannot be pinned.

Four of the guard's first-draft assertions were wrong rather than the document. Two were arithmetic I had
created myself: adding `claims.test.mjs` changed the line count and test count it measures, so the figures
had to be re-measured with the guard in place, and the final line count is now read from the filesystem and
formatted in rather than typed. The third was a false positive of the same family as iteration 9's — the
progress report *quotes* the forbidden phrase "4 of 4 within 2 A" in order to describe this very check, so
the scan now skips a quoted phrase, since a quoted phrase is being discussed and not asserted. The fourth
was an appendix row reading `| ... | same |`, the table's way of pointing at the command above, which my
assertion mistook for a missing command.

Mutation-checked: reverting the JS module figure from 29 to its old 22 fails the guard with the measured
value named in the message. The whitepaper was restored afterwards.

Still unproven / blocked: `docs/pitchdeck.html` and `docs/investor-brief.html` are not yet under the guard.
pitchdeck.html has 27 lines of uncommitted changes from the other session in the working tree, and a guard
that fails on someone else's in-flight edit is a bad guard; it is a queue item instead. The citation and
database figures in the appendix — the `make citations` rows — were left as they stand because re-measuring
them needs the network, and they are marked with the date they were last measured rather than restated as
current. The 4-case benchmark was not re-measured; 2 of 4 within 2 A, median 2.54 A stands. Five Python
failures remain in `tests/test_server_lifecycle.py`; all five bind a local port.

### 2026-10-06 · Iteration 18 — the guard had a hole big enough to walk through

Of the three open items, two need the network or a package install. The third — extending the claims guard
to the deck and the investor brief — was half actionable: `docs/investor-brief.html` is clean in the working
tree, and only `docs/pitchdeck.html` is still held by the other session. Investor-facing claims are also
where an overstatement costs the most, so that was the half worth doing.

Auditing the brief turned up no dishonesty in it — it already said "Two of four within 2 Å, median 2.54 Å",
published the failing rows, and added that this is "not good enough to predict affinity". **It turned up a
hole in my own guard instead.** The brief spells its numbers out in words, and the benchmark check from
iteration 17 matched only digits, so "Three of four within 2 Å" would have passed unnoticed in the one
document where it matters most.

Closing that exposed a second, worse hole. The check has an exemption for a phrase inside quotation marks,
because the progress report quotes the forbidden wording in order to describe the check itself. The
exemption allowed a quote *anywhere earlier on the line* — and in an HTML file, every `style="…"` attribute
carries quotes, so the exemption applied to essentially every line of every HTML document under guard. The
check was close to vacuous on the surfaces that matter most, and it had been passing green the whole time.

A mutation test is what found it. Rewriting the brief's figure to "Three of four" did **not** fail the suite
on the first attempt. The exemption now requires the quote to sit immediately before the phrase, and there
is a test whose only job is to prove the exemption is too narrow to be used as a loophole — including the
exact HTML-attribute case that defeated it.

Done, in three parts:
- The benchmark check matches digits and words, both cases, and is itself proved against eight known-good
  and known-bad strings rather than trusted.
- A new check requires that any surface quoting the pass rate also names the two cases that fail. **It
  caught a real instance on its first run**: `docs/wiki/Testing.md` stated "2 of 4 within 2 Å" in its
  carried-forward table with no mention of Thrombin or BCL-X<sub>L</sub>. The pass rate is only meaningful
  next to the cases it excludes, and that page now names them, with their RMSDs and the reason both fail.
- `docs/investor-brief.html` joins the benchmark and energy-unit scans. Its one vague claim — "offline
  tests" with no figure — now reads 1,438 Python and 193 JavaScript tests, which the guard re-measures.

Verified offline (`node --test tests/*.test.mjs`, 193 passed; `tests/wiki.test.mjs`, 13 passed;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed). Mutation-checked twice: once before narrowing the
exemption, where the inflated claim slipped through, and once after, where it fails with the offending line
quoted in the message.

The line count and JavaScript test figures in the whitepaper and the brief are now written by reading the
filesystem and formatting the result in, not typed. Editing a test file changes the numbers that file's own
tests measure, and doing that by hand cost three rounds of correction across iterations 17 and 18.

Still unproven / blocked: `docs/pitchdeck.html`, which has uncommitted changes from the other session and
stays out of the guard until that file is clean. Three further published surfaces were not audited this
iteration — `docs/pitch.html`, `docs/whitepaper.html` and `docs/WIKI.md` — and the guard does not cover
them, so a stale claim could still be sitting in any of them; that is a known gap, not a clean bill of
health. The 4-case benchmark was not re-measured; 2 of 4 within 2 A, median 2.54 A stands. Five Python
failures remain in `tests/test_server_lifecycle.py`; all five bind a local port.

### 2026-10-06 · Iteration 19 — the figure I had been publishing was the wrong one

Both standing items still need the network or a package install, so this iteration took the gap I recorded
at the end of iteration 18: three published surfaces — `docs/WIKI.md`, `docs/whitepaper.html` and
`docs/pitch.html` — were neither audited nor guarded. Auditing them did not find a stale sentence. It found
that **I had been publishing the wrong benchmark for ten iterations.**

`evals/redock.mjs` defines **eleven** cases. Commit `5902c9a`, "Widen the re-docking benchmark to eleven
cases; the score drops to 5/11", landed before any of my work, and `docs/WIKI.md` and `docs/pitch.html` have
reported the eleven-case result all along. Meanwhile five surfaces I maintain — the wiki front page, the
docking page, the testing page, the investor brief and the progress report — went on citing a four-case set
at 2 of 4 within 2 A with a 2.54 A median. Those four cases are now four of the eleven. The figure was not
invented and it was not dishonest; it was simply superseded, and I never checked the number I was
propagating against the code that produces it. Verified offline: `CASES.length` is 11.

Worse than the stale number: in iterations 17 and 18 I built a guard that **enforced** it, and spent
iteration 18 sharpening that guard's precision against word forms and quotation marks. The guard was
rigorous about the wrong figure. Precision applied to an unverified premise is not care, it is the
appearance of care, and it is the exact failure this project is organised to avoid.

Worse again, the eleven-case record carries a diagnosis I had been working against. Nine of eleven cases are
**reachable** — the search generates a pose within 2 A — and four of the six failures are *scoring* failures
where the crystal pose was found and the ranking put something wrong above it, in the GSK-3 beta case
ranking a 0.54 A pose below a 6.82 A one. Perfect ranking over poses already being produced would take the
benchmark from 45 percent to 82 percent **with no change to the search at all**. Iterations 7, 8 and 10 went
into the search: rigid-body refinement, torsional refinement, binding-mode clustering. That work is correct
and iteration 10's discrimination check is squarely a ranking concern, so it is not wasted — but the
ordering was set by a four-case benchmark that had already been retired, and the repository was holding the
better answer the whole time. A queue item now points the next work at the energy terms.

Done:
- `docs/wiki/Home.md`, `docs/wiki/Docking-and-Scoring.md`, `docs/wiki/Testing.md` and
  `docs/investor-brief.html` now lead with 5 of 11 succeeding and 9 of 11 reachable, name all six failures,
  and separate the four scoring failures from the two sampling ones, because that distinction is the whole
  value of the measurement. The figures are cited as the last recorded run, attributed to the documents that
  recorded it, and explicitly not as something re-measured here.
- The four-case figure is **retired in public rather than quietly overwritten**: the docking page keeps a
  short section saying what it was, that it is superseded, and why a number that was shown to people should
  be withdrawn where it was shown. The investor brief carries a dated correction note for the same reason.
- `docs/progress-report.html`'s earlier entries are left exactly as they are. It is a dated log; its past
  entries record what was believed at the time, and a log that gets rewritten is not a log. The correction
  goes in the new entry.
- `tests/claims.test.mjs` no longer compares documents against a number written down beside them. It now
  imports `CASES` from `evals/redock.mjs` and fails any surface citing a different case count — the check
  that would have caught this in iteration 9 instead of iteration 19.

Verified offline (`node --test tests/*.test.mjs`, 195 passed; `tests/wiki.test.mjs`, 13 passed;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed). Mutation-checked in both directions: reverting the
front page to the four-case figure fails with the offending line quoted, and inflating the eleven-case pass
rate fails too.

Getting the second of those to fail took three attempts, and the reason is worth recording because it is the
same mistake twice. The reachability figure, nine of eleven, must not be read as a pass rate, so the check
exempts reachability claims. My first exemption was scoped to the whole **line**, and
`**8 of 11 succeed. 9 of 11 are reachable.**` passed: the inflated half was exempted by the honest half
sitting beside it. That is precisely iteration 18's quotation-mark hole in a new costume — a line is too
coarse a unit to decide what a phrase means. The second attempt used a thirty-character window and was wrong
in both directions, reaching into the adjacent clause while markdown emphasis, `*generates*`, broke the
keyword inside the match. The exemption is now scoped to the matched phrase alone, and the case that
defeated the first draft is a test.

Still unproven / blocked: the eleven-case result itself. I cannot re-measure it — the benchmark fetches
structures from the RCSB and the network is blocked — so 5 of 11 and 9 of 11 are cited as recorded by
another session's run, not as verified here, and the same goes for the 0.54 A and 6.82 A figures behind the
diagnosis. Whether the four-case set was 2 of 4 as my pages said or 3 of 4 as `docs/WIKI.md` says is now
moot and stays unresolved; the set is retired either way. `docs/pitchdeck.html` remains outside the guard
while the other session has uncommitted changes to it. `docs/pitch.html`, `docs/whitepaper.html` and
`docs/WIKI.md` are still not under the guard: they are the other session's documents, they already carry the
current figure, and adding them means reconciling their stale test counts too, which is a separate task.
Five Python failures remain in `tests/test_server_lifecycle.py`; all five bind a local port.

### 2026-10-06 · Iteration 20 — working on the bottleneck for the first time

The queue item iteration 19 wrote is now the top one, and it is the first time in this loop that the work
has been aimed at a bottleneck the measurements actually identify. The eleven-case benchmark records nine of
eleven cases as *reachable* and four of six failures as **ranking** failures: the search produced a pose
within 2 A and the scoring function put something wrong above it. So this is a rescoring pass, not a search
change.

Done: `js/rescore.js`, three terms `vinaScore` does not have, each chosen because it is a known blind spot
of this class of function *and* matches a recorded failure:

- **Buried unsatisfied polar.** Desolvating a donor or acceptor and giving it no partner costs real energy.
  vinaScore charges nothing: gauss1, gauss2 and hydrophobic all reward the packing, and the absent hydrogen
  bond merely fails to earn its bonus. A decoy that buries a polar group in a greasy sub-pocket therefore
  scores like a good pose — and CDK5 and GSK-3 beta, both recorded scoring failures, are kinase sites full
  of places to do that.
- **Metal coordination.** vinaScore has no metal term at all. Carbonic anhydrase II (1OQ5) is a recorded
  scoring failure and celecoxib binds it by putting a sulfonamide nitrogen on the catalytic zinc; a pose
  that makes that bond earns nothing for it. MetAP2 (1R58) is dinuclear and also fails.
- **Internal clash.** The gap iteration 8 noted and did not close: vinaScore sees protein-ligand pairs only,
  so a conformer folded through itself is free.

Verified offline (`node --test tests/*.test.mjs`, 208 passed; `node --check js/rescore.js`;
`.venv/bin/python -m pytest tests/ -q`, 1438 passed). Thirteen cases in `tests/rescore.test.mjs`:
- **A ranking inversion of the recorded shape is corrected.** The fixture builds two sub-pockets in one
  receptor: a tight all-carbon slot that packs the ligand well and offers its oxygen nothing, and a roomier
  site with a zinc at the floor. vinaScore prefers the greasy decoy at -1.684 over the zinc-coordinating
  native at -0.583 — the carbonic-anhydrase failure in miniature — and rescoring reverses it, -1.383 against
  -1.234. The test asserts the fixture *starts* inverted, so it cannot silently stop proving anything.
- A buried polar atom with a partner at 2.9 A is not penalised; the same atom at 4.0 A is. A
  solvent-exposed polar atom is not penalised at all, because it is not desolvated — the penalty is for
  burying a polar group, not for having one.
- A metal at 2.1 A is credited; at 4.0 A it is not; at 1.4 A it is a clash and not a bond. Only divalent and
  transition metals coordinate: rewarding a pose for sitting next to a chloride or a sodium would be wrong,
  so `COORDINATING_METALS` is deliberately narrower than `IONS`.
- Internal clashes counted for a folded chain and not an extended one, with pairs under four bonds apart
  excluded since the geometry holds those.
- **Zero weights reduce rescoring to vinaScore exactly** — the property a reviewer should check first: the
  rescoring can be turned off and shown to be off. Signs match roles. Deterministic, no mutation of input.
- `rerank` re-sorts and records each pose's old score, new score, terms and `rankChange`, because changing
  an order is the only thing it does and a caller who cannot see what moved cannot judge whether it helped.

One real bug in my own module, found by probing it before writing the tests: the satisfaction check accepted
a metal anywhere in the 5 A burial shell, so a zinc 4 A away excused a completely unsatisfied oxygen.
Coordination now requires coordination distance, and the case is a test with the bug named in it.

Mutation-checked: zeroing the metal weight breaks the inversion test, and reinstating the satisfaction bug
fails the case written for it. `js/rescore.js` was restored, confirmed by an empty `git diff`.

Still unproven / blocked, and this is the main thing:
- **The weights are not calibrated and the module says so on every call.** Fitting them means running the
  eleven-case benchmark, measuring how often each term flips a ranking the right way, and tuning against
  that. That needs the RCSB. The defaults are round numbers of the same order as the Vina terms beside them,
  nothing more, and `WEIGHTS_ARE_UNCALIBRATED` is returned with every result.
- **It is deliberately not wired into `doDock`.** Rescoring with invented weights in the product would be
  worse than not rescoring at all: it would move rankings for reasons nobody had checked. Two queue items
  now record calibration first, wiring second.
- Whether these three terms are the right three is unmeasured. The synthetic tests prove each does what it
  claims on geometry built to exercise it; they say nothing about how often any of them matters on real
  structures. The benchmark was not re-measured; 5 of 11 and 9 of 11 stand as recorded by another session's
  run. Five Python failures remain in `tests/test_server_lifecycle.py`; all five bind a local port.
