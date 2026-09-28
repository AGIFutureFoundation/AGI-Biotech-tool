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
| 8 | Shared space | Several people see the same molecule, each other, and each other's changes | partial: avatars, state sync and server-arbitrated ownership exist; no voice chat |
| 9 | Environments | Load a real glTF scene, stand the molecule in it, keep frame rate | done |
| 10 | Databases | Public sources, no keys, failure of one never blocks the rest | done, 14 sources |
| 11 | Evals | Accuracy is measured and published, not asserted | done, see below |
| 12 | AR glasses | Runs on glasses people actually own | **see the honest limits** |

## Honest limits

**Ray-Ban Meta glasses cannot run this.** The first two generations have no display. The Display model has
a small heads-up panel and no third-party WebXR browser. Nothing renders a molecule there. What does work,
and what is built, is a voice companion: you speak, the answer is spoken back and shown in large type on the
paired phone. Glasses that do have real browsers — Quest 3, Vision Pro, Android XR — run the full workspace.

**Docking accuracy is mixed, and the honest number is worse than it was.** The benchmark ran four cases
until 2026-09-28; it now runs eleven, spanning kinase, protease, nuclear-receptor, metalloenzyme and
protein-protein-interface sites. On the four-case set it scored 3/4, 3/4, 3/4 and 2/4 within 2 A. On the
eleven-case set it scores **5/11 within 2 A, median 2.09 A**.

That drop is the point of widening it. With four cases each result was worth 25 points, so a good run
looked like a validation study; the four happened to suit a shape-and-hydrophobicity score.

The benchmark now separates the two ways a case fails, because they call for opposite work and one
success rate hides which you have. A **sampling** failure means no near-native pose was ever generated:
the fix is more runs, more steps, a better move set. A **scoring** failure means a near-native pose WAS
generated and the function ranked something wrong above it: more sampling cannot help.

The split is lopsided. Of six failures, **four are scoring and two are sampling**, and 9/11 cases are
*reachable* — a pose within 2 A was generated, ranked or not. Perfect ranking over the poses already
being produced would take the benchmark from 5/11 to 9/11.

| case | top (ranked) | best (found) | mode |
| --- | --- | --- | --- |
| 1UNL CDK5 | 6.00 A | 1.29 A | scoring |
| 1Q41 GSK-3 beta | 6.82 A | 0.54 A | scoring |
| 1OQ5 carbonic anhydrase | 7.50 A | 1.63 A | scoring |
| 2BM2 tryptase | 5.22 A | 1.60 A | scoring |
| 2YXJ BCL-XL | 4.59 A | 3.86 A | sampling |
| 1R58 MetAP2 | 3.25 A | 3.02 A | sampling |

So the next improvement belongs in the energy terms, not the search.

**The benchmark cannot yet detect a small change, and that is its most important limit.** Ranking was
found to be inconsistent with the search -- each run picked its pose under `vinaScore + intraClash +
boxPenalty` and then ranked it by `vinaScore` alone -- and fixing that was measured over three runs per
arm: baseline 3/11, 5/11, 6/11 (mean 4.67); fixed 6/11, 5/11, 4/11 (mean 5.00). The difference is 0.33
cases and the spread inside each arm is 3 cases, so the result is **inconclusive**: the fix is kept
because ranking by a different objective than you optimised is wrong on its own terms, not because this
measured an improvement.

Eleven cases at three runs resolves nothing below roughly a three-case swing. Detecting a real scoring
change needs seeded runs so before and after see identical random draws, more cases, or both. Until then,
treat this benchmark as a floor check, not an A/B instrument. Note also that 1OQ5 passed at
1.44 A on one run and failed at 7.50 A on the next: single runs are draws, and the per-case verdict is
as stochastic as the total.

Quote the range, not a run. Treat scores as a ranking to triage, not as a binding prediction, and re-run the
benchmark whenever the scoring function changes.

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
- Shared space: voice chat. Object ownership is done — the server arbitrates a lease
  per object, so two people cannot drag one ligand and the loser is told who holds it.
- Eval coverage: more re-docking cases, and a scoring function that passes more of them.
- Environment search is done, against the Poly Haven catalogue (997 environments, CC0,
  no account or token needed). Sketchfab would add models on top of that, not instead.
