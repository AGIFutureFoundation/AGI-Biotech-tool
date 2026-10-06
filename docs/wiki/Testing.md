# Testing

Every number on this page says which command produced it and when. A number that cannot be re-measured
right now is marked as carried forward rather than restated as fresh.

## Measured 6 October 2026

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/ -q` | **1438 passed**, 55 skipped, 1 xfailed, **5 failed** |
| `node --test tests/*.test.mjs` | **121 passed**, 0 failed |

The five Python failures are all in `tests/test_server_lifecycle.py` and all need to bind a local port,
which the environment these were run in refuses. They are an environment limitation, not a regression, and
they are reported here rather than filtered out of the count.

## The JavaScript suites

All thirteen run with `node --test`, no browser, no network, no server.

| Suite | Cases | What it proves |
| --- | --- | --- |
| `tests/analysis.test.mjs` | 7 | Interaction geometry on a synthetic five-residue protein with one planted hit per interaction class |
| `tests/voice.test.mjs` | 15 | `parseCommand` across the intent grammar, spoken digits and letters, and that silence executes nothing |
| `tests/agent.test.mjs` | 17 | The tool registry, schema validity, and the voice-to-renderer enum seam |
| `tests/refine.test.mjs` | 8 | Rigid-body refinement on a synthetic receptor with a seat known by construction |
| `tests/torsion.test.mjs` | 14 | Torsion geometry exactly, plus the torsional search discipline |
| `tests/poses.test.mjs` | 14 | Binding-mode clustering, and whether the score discriminated between modes |
| `tests/pockets.test.mjs` | 12 | Pocket detection on hollow shells, a solid ball, and a surface dimple |
| `tests/structure.test.mjs` | 17 | The PDB and mmCIF parsers, column by column, and bond perception |
| `tests/ledger.test.mjs` | 21 | The provenance hash chain, by actually tampering with it |
| `tests/api.test.mjs` | 18 | How the database layer behaves when a source fails, with `fetch` stubbed |
| `tests/claims.test.mjs` | 13 | Re-measures the published figures, and guards the benchmark claim |
| `tests/md.test.mjs` | 21 | The dynamics force field, its gradient, the minimiser, and the engine's invariants |
| `tests/wiki.test.mjs` | 13 | These pages: link integrity, sidebar coverage, and the claims that must not drift |

### Why synthetic geometry

A real complex needs the network, and a test that cannot run offline is a test that stops being run. So
these suites build receptors and ligands where the right answer follows from the construction:

- **Interaction analysis** gets a protein with exactly one planted hit per class — stacking with PHE at
  3.7 Å, a hydrogen bond at 2.9 Å, a salt bridge at 2.9 Å, a hydrophobic contact at 3.8 Å — and a residue
  30 Å away that must never appear in the output.
- **Refinement** gets a carbon cup with one obvious seat, so "did it find the minimum" has an answer.
- **The force field** gets a central finite-difference gradient check in double precision at three step
  sizes, so second-order convergence is visible rather than assumed. The force must be the negative gradient
  of the energy; when it is not, a minimiser can be steered the wrong way and nothing in the output says so.
- **Pocket detection** gets hollow spheres whose interior free volume follows from the radius and the probe
  margin, a solid ball with no interior at all, and a shallow dimple pressed into a plate. The dimple must
  not outrank the sealed cavity — if pocket detection picks the wrong site, everything downstream runs
  correctly against the wrong answer and nothing in the output says so.
- **Torsions** are checked without reference to the scoring function at all: a rotation must preserve every
  bond length to 1e-4 Å and every bond angle to 1e-4 rad, move the dihedral spanning its own bond by
  exactly the angle requested, move the two flanking dihedrals by nothing, leave the hinge atoms and the
  entire fixed side untouched, and compose with its inverse to the identity.

That last group is the kind of test worth having: exact, fast, and it would catch a wrong rotation matrix
that an end-to-end docking run would quietly absorb.

## What the tests have actually caught

Not a hypothetical list. These were found by a test, not by use:

| Bug | Suite |
| --- | --- |
| A flat detail cap let hydrophobic contacts crowd out the one π-stacking record | `analysis` |
| "load LRRK2" arrives from a recogniser as "load lark two" and matched nothing | `voice` |
| The flexible-refinement pass loop seeded its running best at infinity, so it could never stop on the first pass | `torsion` |
| The planarity restraint in `js/md.js` holds its plane normal fixed, so its force is about 19% off its own energy gradient | `md` |
| PDB insertion codes were dropped, so residues 100 and 100A merged and the merged residue kept only one C-alpha | `structure` |

The whitepaper's Appendix A is now checked by `tests/claims.test.mjs`, which re-measures its figures
against the repository rather than trusting them. It had drifted badly: 763 tests passing claimed against
1,438 actual, 2,034 lines of test code against 9,374, and no mention of the JavaScript suites at all.
Nobody had lied — the document was written once and the repository kept moving, which is precisely what
prose cannot notice and a test can.

Pocket detection, by contrast, was found correct on every synthetic case put to it, including the one that
surprised: removing every other atom from a shell halves its atom count but leaves the survivors about
2.9 Å apart, which still occludes a 2.8 Å probe, so the cavity stays sealed and its volume grows slightly
as the wall thins. The suite asserts that, so a future change cannot quietly turn a sealed wall porous.

Three of my own test expectations were also wrong rather than the code — in each case the code was right
and the assertion was fixed. Worth recording, because a suite that only ever confirms what you expected is
not telling you much.

## The Python suite

1438 cases covering the server, the scoring port, the compound ingestion, the agent protocols and the
video rendering. Of note:

| Suite | What it proves |
| --- | --- |
| `test_vina_score_port.py` | The scoring function term by term against reference values |
| `test_dock_seeding.py` | Deterministic search seeding — the same seed gives the same poses |
| `test_agent_protocols.py` | x402, NANDA and OML signing, tamper detection, replay rejection |

## Carried forward, not re-measured

| Figure | Command | Status |
| --- | --- | --- |
| Re-docking: 2 of 4 within 2 Å, median 2.54 Å | `node evals/redock.mjs` | **Needs the network** |

The two that pass are MAO-B · safinamide at 1.20 Å and the oestrogen receptor · 4-OHT at 1.24 Å. **The two
that fail are Thrombin · inhibitor at 3.83 Å and BCL-X<sub>L</sub> · ABT-737 at 4.04 Å** — both large and
flexible ligands in shallow or groove-shaped sites. The pass rate is only meaningful next to the cases it
excludes, so `tests/claims.test.mjs` requires any page quoting the figure to name the failures too. That
check caught this page doing exactly that.
| MD throughput: approximately 27 ns/day on Apple GPU | OpenMM benchmark | Needs the server |

Whether the refinement added in the two most recent iterations improves the re-docking benchmark **has not
been measured**. See [Docking and Scoring](Docking-and-Scoring).

## The largest untested surface

XR. Hand tracking, the wrist panel, multi-user presence and comfort cannot be verified without a headset,
and the HTTP routes cannot be verified without a bound port. What is verified is everything the XR layer
calls into. See [XR and Hand Tracking](XR-and-Hand-Tracking) and [Known Limits](Known-Limits).
