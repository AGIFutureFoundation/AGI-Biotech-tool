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
      clustering with a discrimination check (iteration 10), all unit-tested on synthetic geometry. The 4-case
      benchmark re-measurement still waits on the network, so the 2-of-4 / 2.54 A median figure stands
      unchanged and must not be restated as improved.
- [ ] Calibrate the discrimination margin in js/poses.js against the re-docking benchmark — how large a score
      gap must be before the better-scoring pose is reliably the closer one. Needs the network. Until then the
      default is a stated convention and says so in its own output.
- [x] docs/wiki/ pages ready to paste into the GitHub wiki (iter 9), guarded by tests/wiki.test.mjs
- [x] Pocket detection under test on synthetic geometry (iter 11) — the one untested stage of the chain
- [x] Dynamics force field under test, with a gradient check (iter 12)
- [x] Planarity term in `js/md.js` swapped for the exact-gradient one (iter 13). Measured impact on where
      minimisation lands: negligible — 0.002 to 0.006 A RMSD, energies agreeing to 0.001. The fix is correct
      and removes a latent hazard; it is not a result anyone would notice.
- [x] Structure parsers under test, and insertion codes fixed (iter 14)
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
