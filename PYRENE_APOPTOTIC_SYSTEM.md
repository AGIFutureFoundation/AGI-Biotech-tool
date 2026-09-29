# Pyrene Apoptotic Compound Design System

**Last verified:** 2026-09-22
**Status of this subsystem:** a compound *generator* and scoring scaffold. It produces
candidate structures. It does not produce validated results of any kind.

---

## Read this first — please do not skip this section

This document previously described expected clinical benefits for children with cancer:
"40–60% improved response rates" for BCL2 in paediatric lymphoma, "50–70% improved
sensitization to chemo" for XIAP, "30–50% improved remission rates" for FAS. It described
the platform as "PRODUCTION READY" and "READY FOR SYNTHESIS & TESTING".

**All of that was invented.** No compound in this system has been synthesised. None has
been tested in a biochemical assay, a cell line, an animal or a human. There is no efficacy
data, and therefore no basis whatsoever for a statement about response rates, remission
rates or patient outcomes. Those claims have been removed, not adjusted.

The numbers this system reports are placeholders. `server/pyrene_apoptotic_discovery.py`
emits values as `SyntheticValue`, which print with a `[SYNTHETIC]` marker and sit in records
carrying a `provenance` field recording that no model ran
(`server/synthetic_provenance.py`). The binding affinities, pediatric safety scores and
selectivity figures it produces are drawn from random distributions and given units.

**Nothing in this document is medical, clinical or regulatory guidance.**

---

## What the system actually does

It enumerates candidate compound structures on a pyrene scaffold, scores them with a
weighted formula, and iterates. That is genuinely useful as a design-space exploration
tool. It is not a discovery result.

### Compound generation (`server/pyrene_apoptotic_discovery.py`)

A four-ring pyrene core combined with a warhead library, across five apoptotic mechanism
classes. Structures are generated and validated with RDKit (`server/pyrene_structures.py`).

**Warhead library**, grouped by chemistry:

| Class | Members |
|---|---|
| Electrophilic | acrylamide, vinylsulfonamide, cyanoketone |
| Metal chelating | hydroxamate, catechol |
| H-bond donating | amide, urea |
| Hydrophobic | trifluoromethyl, phenyl |
| Targeting | folate, glucose |

The per-warhead "+1.5 kcal/mol" style contributions and "95% pediatric safety" scores in
the source are **design heuristics written by hand**, not measured or predicted values.
They order the search space. They are not property predictions.

### Mechanism classes

Five apoptotic routes are modelled as target sets, with literature-grounded biology:

1. **Intrinsic** — BCL2, BCL-xL, MCL1; mitochondrial cytochrome c release.
2. **Extrinsic** — FAS, TNFR1, TRAIL receptors; DISC formation to caspase-8.
3. **IAP antagonism** — XIAP, cIAP1/2, survivin; SMAC mimetic approach.
4. **Granzyme B** — perforin-mediated granule release, bypassing BCL2 blockade.
5. **Direct caspase activation** — caspase-3/7/9, executioner phase.

The mechanism biology is real and citable. The "pediatric relevance: 95%" style scores
attached to each are hand-assigned weights, not epidemiological measurements.

### Scoring (`server/continuous_compound_evolution.py`)

```
Composite = 0.40 × binding affinity
          + 0.25 × pediatric safety
          + 0.20 × selectivity
          + 0.15 × synergy potential
```

A ten-cycle loop moves from broad exploration to focused optimisation to exploitation of
the best scaffolds.

**The weighting scheme is a reasonable design decision. The inputs it combines are
synthetic.** A composite score built from random numbers ranks nothing. The "expected
improvement: +10–15% per 10 cycles" figure previously quoted describes drift in a random
walk.

---

## Target rationale

These targets were selected because the underlying disease biology is real and the unmet
need is documented. That rationale stands on its own and does not depend on any claim about
this system's output.

| Target | Mechanism | Disease context |
|---|---|---|
| BCL2 / BCL-xL | Intrinsic apoptosis | B- and T-cell lymphomas |
| XIAP | SMAC mimetic | Neuroblastoma, hepatoblastoma, rhabdomyosarcoma |
| FAS | Extrinsic apoptosis | Acute leukaemias |
| Survivin | IAP suppression | Broadly over-expressed across paediatric cancers |
| Caspase-3/7 | Direct activation | Therapy-resistant tumours |

For each, the documented unmet need is genuine: resistance to standard chemotherapy,
toxicity burden in children, high relapse rates in poor-risk groups, and in several cases no
approved targeted agent. That is why these targets are interesting.

**What this system contributes is candidate structures to consider — nothing more.** The
"expected benefit" percentages previously listed against each target have been removed.

---

## Paediatric safety framing

The generator carries a notion of paediatric appropriateness — favouring H-bond-donating
warheads over electrophiles and metal chelators, and flagging organ systems that warrant
monitoring in children (hepatic immaturity, developing renal filtration, cardiac
conduction, blood-brain barrier formation, active growth plates).

**This is a design bias in a search heuristic. It is not a safety assessment.**

An earlier version of this document contained an age-scaled dosing table (neonatal 50% of
adult dose, infant 60%, and so on). That table has been removed. It was not derived from
pharmacokinetic data, it applies to compounds that do not exist, and presenting dosing
fractions for children in a document about unsynthesised molecules is not defensible in any
form.

Nothing here should inform a dosing decision.

---

## Computational cost

Roughly six minutes per generation-and-scoring cycle for 20 compounds on a development
laptop, so about an hour for a ten-cycle run. This measures structure enumeration, RDKit
validation and arithmetic — the only parts of the loop that do real work.

Previously claimed figures for parallel throughput ("500+ compounds/day", "20+ simultaneous
workflows", "4–5x GPU speedup") were not measured and have been removed.

---

## What would make this real

In order:

1. **Replace the synthetic scoring inputs.** Route binding estimates through the real
   docking path (`js/dock.js`) or a validated external tool, not
   `molecular_research_pipeline.py`, which is also placeholder-backed.
2. **Replace hand-assigned safety heuristics** with a real ADMET/toxicity model, or drop
   the safety term from the composite score until one exists.
3. **Benchmark the scoring function** against compounds with known activity against these
   targets — venetoclax for BCL2, birinapant for IAPs — and report the recall.
4. **Only then** consider synthesis of anything, and only through people qualified to
   assess it.

Steps 1–3 are computational and could be done in this repository. Nothing beyond that is a
software task.

---

## Verified state of the wider repository

As of 2026-09-22, run in CI on every push:

| Check | Result |
|---|---|
| `make test` | 708 passed, 1 xfailed |
| `make reachable` | 22 of 22 JS modules reachable |
| Panel citations | 910/910 across four panels |
| Repurposing recall | 5 of 7 documented cases, both misses explained |

The St Jude panel (15 paediatric oncology targets, 263/263 citation checks passing) is the
part of this repository with real, verified paediatric cancer content. The panel name
describes the disease area it covers.

---

## Research focus

This subsystem was built to serve research into paediatric oncology — the same goal pursued
by organisations working on childhood cancer.

**No partnership, agreement, sponsorship, collaboration or endorsement exists with any such
organisation.** There is no FDA or EMA engagement, no regulatory submission, no IND, no
manufacturing arrangement and no clinical programme. Earlier versions of this document
implied several of these.

---

**Contact:** see `SUPPORT.md`.
