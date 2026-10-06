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

Re-docking four complexes where the answer is known from the crystal structure:

| Case | Top-pose RMSD | Result |
| --- | --- | --- |
| MAO-B · safinamide | 1.20 Å | pass |
| Oestrogen receptor · 4-hydroxytamoxifen | 1.24 Å | pass |
| Thrombin · inhibitor | 3.83 Å | fail |
| BCL-X<sub>L</sub> · ABT-737 | 4.04 Å | fail |

**2 of 4 within 2 Å. Median 2.54 Å.** A compact, buried, mostly rigid ligand is placed well. A long
peptidomimetic in a shallow groove is not. Treat a score from this tool as a filter for ranking, never as
an affinity prediction, and never in units — see [Docking and Scoring](Docking-and-Scoring).

This figure is carried forward from the last run with network access. It is re-measured by
`node evals/redock.mjs`, which needs to fetch structures from the RCSB.

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
