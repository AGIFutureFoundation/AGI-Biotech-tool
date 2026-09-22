# biodao.blockchain — working spec

This is the request rewritten as something a team can build against: what each item means, how you can tell
it is done, and where reality pushes back. It replaces a long prompt with a checklist.

## The product in one line

A molecular research workspace that several people can share, that runs on a desktop, a phone, and a
headset, that can be operated by voice or by an agent as well as by hand, and that records what was done
so the result can be trusted later.

## Scope, with acceptance tests

| # | Capability | Done when | State |
| --- | --- | --- | --- |
| 1 | Tool layer | Every panel action is also a named tool with a typed schema | done, 19 tools |
| 2 | Agent interface | A sentence in the console runs the right tool and reports the result | done |
| 3 | External control | An MCP client lists the tools and drives a live browser session | done |
| 4 | Voice | Speech runs the same tools and the answer is spoken back | done |
| 5 | Hand control | Pinch, two-hand scale, point, swipe, palm menu, no controllers | done, untested on hardware |
| 6 | Dashboard | One page answers: what is loaded, what was screened, what the evidence says | done |
| 7 | Mobile | Usable one-handed at 390 px: bottom sheets, touch targets, no horizontal scroll | done |
| 8 | Shared space | Several people see the same molecule, each other, and each other's changes | partial: avatars and state sync exist; no voice chat, no ownership rules |
| 9 | Environments | Load a real glTF scene, stand the molecule in it, keep frame rate | done |
| 10 | Databases | Public sources, no keys, failure of one never blocks the rest | done, 14 sources |
| 11 | Evals | Accuracy is measured and published, not asserted | done, see below |
| 12 | AR glasses | Runs on glasses people actually own | **see the honest limits** |

## Honest limits

**Ray-Ban Meta glasses cannot run this.** The first two generations have no display. The Display model has
a small heads-up panel and no third-party WebXR browser. Nothing renders a molecule there. What does work,
and what is built, is a voice companion: you speak, the answer is spoken back and shown in large type on the
paired phone. Glasses that do have real browsers — Quest 3, Vision Pro, Android XR — run the full workspace.

**Docking accuracy is mixed.** The re-docking benchmark is 2 of 4 within 2 Å (median 2.54 Å). It reproduces
the MAO-B and oestrogen receptor poses closely and misses on BCL-XL and thrombin. Treat scores as a ranking
to triage, not as a binding prediction, and re-run the benchmark whenever the scoring function changes.

**Interactive physics is coarse by design.** Harmonic terms, an elastic network backbone, no explicit water,
no electrostatics. It is for feel and triage. The OpenMM backend is the one to quote.

**A local hash chain is not a blockchain.** Nothing is broadcast and there is no consensus. It makes
tampering detectable and gives a head hash you can anchor elsewhere.

## Principles

1. Anything a person can do, an agent can do, through the same tool with the same schema.
2. No feature may require an account or an API key to demonstrate.
3. A source that fails degrades that panel only.
4. Numbers shown to a researcher carry their method and their uncertainty.
5. New capability arrives as a new file; shared files are edited by one owner at a time.

## Still open

- Hardware testing for hand tracking and voice on Quest 3 and Vision Pro.
- Shared space: object ownership so two people cannot drag one ligand, and voice chat.
- Eval coverage: more re-docking cases, and a scoring function that passes more of them.
- A Sketchfab account token would allow in-app environment search; without it, scenes are imported by file.
