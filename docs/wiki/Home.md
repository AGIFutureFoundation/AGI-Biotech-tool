# biodao.blockchain

A molecular research workspace for neurogenetic drug discovery, built for a headset and usable without
one. Powered by AGI Corp.

It loads a target, finds its pockets, puts a compound in one, docks it, runs dynamics on it, classifies
every contact the pose makes, and writes what it did into a hash-chained ledger. You can drive the whole
thing by voice, by hand, or by letting an agent drive it for you.

One rule governs the project: **every number it shows is either traceable to the thing that produced it, or
marked in the output itself as an estimate.** That rule is why this page leads with the weakest result
rather than the strongest.

## The weakest result, first

Re-docking crystal ligands blind: pull each one out of its structure, dock it back, and measure RMSD to
where it really sat. `evals/redock.mjs` defines eleven cases.

**2–6 of 11 within 2 Å across ten seeds; mean 4.6.** Reachability 6–9 of 11 and median top-pose RMSD
1.75–4.27 Å are carried forward from the three earlier ad-hoc runs — the ensemble aggregates pass
fractions, not those.

Three runs, three different answers. The spread is not a detail — it is the result. At the current
search budget (12 Monte Carlo runs × 3000 steps) this benchmark **cannot resolve a one- or two-case effect**,
and a one- or two-case effect is the size of every scoring and search change in the roadmap.

| Run | Pass | Reachable | Median | Scoring / sampling failures |
| --- | --- | --- | --- | --- |
| Recorded earlier | 5 / 11 | 9 / 11 | — | 4 / 2 |
| 12 Oct, unseeded | 6 / 11 | 7 / 11 | 1.75 Å | 1 / 4 |
| 12 Oct, seeded 20261012 | 4 / 11 | 6 / 11 | 4.27 Å | 2 / 5 |

The scoring-versus-sampling split **inverts** between runs. The earlier figure said four of six failures were
ranking failures, which is what the roadmap has steered by since iteration 19 and what the rescoring work of
iteration 20 was aimed at. Today's runs say one of five, then two of seven. We do not know whether ranking or
search is the larger problem, and nothing here is evidence either way.

**So no single number is published as the benchmark result**, and no scoring or search improvement can be
validated against this benchmark as configured. Quoting one run — including the most flattering, which would
be 6 of 11 — would be reading noise as a result. The figure of record, with every run behind it, is
`evals/benchmark-runs.json`.

Reproduce the seeded run with `NODE_USE_ENV_PROXY=1 node evals/redock.mjs --seed 20261012`. The next step is
to raise the search budget until a repeat reproduces itself, then report a mean and spread over several
seeds.

![Re-docking benchmark: eleven cases, RMSD to the crystallographic pose](chart-redock.png)

Each row is one case. The green dot is the best pose the search produced; the amber dot is the pose the
scorer ranked first. Where the two are far apart the search did its job and the ranking did not — that gap
is the four scoring failures, and it is the whole argument for working on the energy terms next.

## Watch it run

[![A two-minute cut of the workspace](https://github.com/AGIFutureFoundation/AGI-Biotech-tool/blob/enterprise-hardening-and-ingestion/docs/media/frame-38s.jpg)](https://github.com/AGIFutureFoundation/AGI-Biotech-tool/blob/enterprise-hardening-and-ingestion/docs/pitch.mp4)

A two-minute silent cut, rendered offline from the same figures as the rest of this wiki — no narration,
nothing staged. GitHub does not play video inside a wiki page, so the image above is a link to the file in
the repository, where it plays. [More frames and the longer
walkthrough](https://github.com/AGIFutureFoundation/AGI-Biotech-tool/tree/enterprise-hardening-and-ingestion/docs) sit alongside it.

> **The film carries the current figures.** `docs/pitch.mp4` was re-rendered on 12 October 2026 and its benchmark slide shows the three runs recorded at the time. It predates the ten-seed ensemble of 19 October, so it shows 4–6 of 11 where the current figure is 2–6; it is re-rendered when the next render runs. `ffmpeg` on the build machine links `libx265.216.dylib` while the installed x265 provides `.217`; `brew reinstall ffmpeg` is the real repair, and until then `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/Cellar/x265/4.2/lib` in front of the render command works.


The cases that fail, across runs: GSK-3β (1Q41), BCL-X<sub>L</sub> (2YXJ), carbonic anhydrase II (1OQ5),
MetAP2 (1R58), β-II tryptase (2BM2), CDK5 (1UNL), thrombin (1OYT) and p38 (1YWR) each fail in at least one
of the three runs — which is itself the point: the set is not stable. Case-by-case detail for every run is
in `evals/benchmark-runs.json`. GSK-3β (1Q41) is the one case
that fails the same way in all three — a 0.33–0.36 Å pose found and ranked near 6.8 Å — and is the
only ranking failure that reproduces.

Treat a score from this tool as a filter for ranking, never as an affinity prediction, and never in units —
see [Docking and Scoring](Docking-and-Scoring).

Re-measured 12 October 2026, the first time in this build loop the benchmark could be run at all —
the sandbox's network restriction lifted. Before that date these pages carried a single figure
carried forward from an earlier run, and before iteration 19 a four-case figure that was superseded
outright. Both are now replaced by a range, because a range is what the measurement supports.
## What is in it

| | |
| --- | --- |
| **Structures** | PDB and mmCIF parsing, bond perception, atom typing, AlphaFold models with per-residue confidence |
| **Docking** | Monte Carlo search with a Vina-shaped empirical score, then rigid-body and torsional refinement |
| **Dynamics** | Interactive in-browser MD, plus all-atom OpenMM with implicit solvent on the local server |
| **Analysis** | Hydrogen bonds, salt bridges, π-stacking, hydrophobic contacts, residue by residue |
| **Data** | 21 public databases, listed in [Data Sources](Data-Sources) |
| **Control** | 19 voice intents, 22 agent tools, hand tracking, a wrist panel, and a mouse |
| **Agents** | x402 payment challenges, NANDA AgentFacts, OML 1.0 fingerprinting — see [Agent Protocols](Agent-Protocols) |
| **Provenance** | A local SHA-256 hash chain over every result — see [Provenance Ledger](Provenance-Ledger) |

## Where to go next

- **I want to run it** → [Getting Started](Getting-Started)
- **I want to know if the science holds** → [Docking and Scoring](Docking-and-Scoring), then
  [Known Limits](Known-Limits)
- **I want to drive it by voice or wire an agent to it** → [Voice and Agent Control](Voice-and-Agent-Control)
- **I want to know what it sends where** → [Data Sources](Data-Sources)
- **I want to check the claims myself** → [Testing](Testing)

Correction and review are both welcome, including on this page: <x@agifuturefoundation.org>
