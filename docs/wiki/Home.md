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

**5 of 11 succeed. 9 of 11 are reachable.**

"Reachable" is the more useful number: in nine of eleven cases the search *generates* a pose within 2 Å. Of
the six failures, **four are scoring failures** — the crystal pose was found and the scoring function ranked
something wrong above it, in one case ranking a 0.54 Å pose below a 6.82 Å one. Only two are sampling
failures. Perfect ranking over poses already being produced would take the benchmark from 45% to 82% with no
change to the search at all.

That is a diagnosis, not just a score: **the next work belongs in the energy terms, not the search.**

![Re-docking benchmark: eleven cases, RMSD to the crystallographic pose](chart-redock.png)

Each row is one case. The green dot is the best pose the search produced; the amber dot is the pose the
scorer ranked first. Where the two are far apart the search did its job and the ranking did not — that gap
is the four scoring failures, and it is the whole argument for working on the energy terms next.

## Watch it run

[![A 110-second cut of the workspace](https://github.com/AGIFutureFoundation/AGI-Biotech-tool/blob/enterprise-hardening-and-ingestion/docs/media/frame-38s.jpg)](https://github.com/AGIFutureFoundation/AGI-Biotech-tool/blob/enterprise-hardening-and-ingestion/docs/pitch.mp4)

A 110-second silent cut, rendered offline from the same figures as the rest of this wiki — no narration,
nothing staged. GitHub does not play video inside a wiki page, so the image above is a link to the file in
the repository, where it plays. [More frames and the longer
walkthrough](https://github.com/AGIFutureFoundation/AGI-Biotech-tool/tree/enterprise-hardening-and-ingestion/docs) sit alongside it.

The six failures, named: CDK5 (1UNL), GSK-3β (1Q41), carbonic anhydrase II (1OQ5) and β-II tryptase (2BM2)
are **scoring** failures — a good pose was found and ranked below a bad one. BCL-X<sub>L</sub> (2YXJ) and
MetAP2 (1R58) are **sampling** failures, where no good pose was generated at all.

Treat a score from this tool as a filter for ranking, never as an affinity prediction, and never in units —
see [Docking and Scoring](Docking-and-Scoring).

These figures are carried forward from the last run with network access and are re-measured by
`node evals/redock.mjs`, which fetches structures from the RCSB. The four-case table published here until iteration 19 is **superseded**. `evals/redock.mjs` now defines eleven cases, and the figure above is the last recorded run of it, published in `docs/WIKI.md` and `docs/pitch.html`. Neither set can be re-measured here, because the benchmark fetches structures from the RCSB and the network is blocked.

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
