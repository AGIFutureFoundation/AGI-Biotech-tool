# Known Limits

What this tool cannot do, or cannot yet prove. On its own page, linked from the front page, because a
limits section buried at the bottom of a long document is a limits section nobody reads.

## The science

**The docking score is not an affinity.** It is unitless, Vina-shaped, and uncalibrated. Do not convert it
to kcal/mol, a ΔG or a K<sub>d</sub>, and do not compare scores across different targets. See
[Docking and Scoring](Docking-and-Scoring).

**Pose prediction works on half the benchmark.** 2 of 4 within 2 Å, median 2.54 Å. Compact ligands in deep
rigid pockets are placed well; long flexible ligands in shallow grooves are not. Four cases cannot
generalise, and re-docking is the easy version of the problem — cross-docking has not been measured.

**There is no internal-strain term.** The score sees protein-ligand contacts only. A conformer that folds
onto itself is not penalised, which is why refinement polishes a conformer rather than generating one.

**Nothing here has been validated in a wet lab.** Not one prediction from this workspace has been tested
against an assay. Every output is a hypothesis to prioritise experiments, not a result.

**Implicit solvent, short timescales.** The dynamics use GBn2 implicit solvent, which is fast and loses the
structured water that often decides whether a hydrogen bond matters. Trajectory lengths reachable
interactively are far below what a binding free energy calculation needs.

## Not measured in the current environment

These are blocked by the sandbox the recent work ran in, not by the code:

| Blocked | Needs |
| --- | --- |
| The re-docking benchmark | Outbound network to the RCSB |
| Every HTTP route, the browser workspace, the MCP round trip | A bindable local port |
| Ed25519 signing — the HMAC fallback ran instead | `pip install cryptography` |
| Narration on the walkthrough films | A speech service; the script is written and waiting |

Five Python tests fail for exactly one reason: they bind a port. See [Testing](Testing).

## Scaffolded on purpose

| Feature | Honest status |
| --- | --- |
| **x402 settlement** | The challenge is well-formed and replay-protected. Nothing is wired to a facilitator; no value moves |
| **The ledger** | A local single-writer hash chain. Tamper-evident, not a blockchain, not distributed. See [Provenance Ledger](Provenance-Ledger) |
| **OML fingerprinting** | Challenge-response pairs work and a challenge never contains its answer. Detection of an unauthorised copy depends on someone running the check |

## Hardware

**Ray-Ban Meta glasses cannot render this workspace.** No display, no WebXR runtime. The glasses path is a
voice companion — audio in, audio out — with the visual workspace elsewhere. See
[XR and Hand Tracking](XR-and-Hand-Tracking).

**XR is the largest untested surface in the product.** Hand tracking, the wrist panel, multi-user presence
and comfort need a headset. The emulator proves layout and logic, not comfort or frame timing.

## Commercial

No revenue and no signed customer yet. No published team credentials, valuation, or raise terms — those
belong to the people who would have to stand behind them, and inventing them for a pitch would be the one
failure this project is built to avoid.

## Why this page exists

A research tool that overstates its accuracy costs someone months of bench work. The specific risk here is
a docking score read as an affinity: it looks like a kcal/mol number, it has a minus sign, it sorts
sensibly, and it is none of those things. So the caveat is in the ledger record, in the discovery document
an agent reads, in the video, in the whitepaper, and here.

If you find a claim anywhere in this project that this page does not cover, that is a bug worth reporting:
<x@agifuturefoundation.org>
