# Molecular Research System

**Last verified:** 2026-09-22
**Scope:** the docking, dynamics, scoring and repurposing components of biodao.blockchain

---

## Read this first

This document previously described a complete drug-discovery R&D platform with validated
docking accuracy, long-timescale dynamics and 29 connected databases. Much of that was not
true, and the corrections are noted inline below.

The single most important thing to understand about this subsystem is that **it has two
separate implementations, and only one of them computes anything.**

| Path | Implementation | Status |
|---|---|---|
| `js/dock.js` | Vina-form empirical scoring, Monte Carlo search | **Real** |
| `/api/md` → OpenMM | All-atom dynamics, implicit solvent | **Real** |
| `server/molecular_research_pipeline.py` | Docking, MD, ADMET, scoring, SAR | **Placeholder values** |

The Python pipeline's engines — `MolecularDockingEngine`, `MolecularDynamicsEngine`,
`ADMETPredictor`, `DrugRepurposingEngine` — return `random()`-derived numbers. They are
labelled as such at runtime, but they are not simulations and their output is not a result.

---

## The real docking path: `js/dock.js`

### Scoring function

A re-implementation of the AutoDock Vina empirical scoring function, using the published
term set and weights (Trott & Olson, 2010):

| Term | Weight | Role |
|---|---|---|
| gauss1 | −0.0356 | short-range steric attraction |
| gauss2 | −0.00516 | broader steric attraction |
| repulsion | 0.840 | close-contact penalty |
| hydrophobic | −0.0351 | nonpolar surface contact |
| hydrogen bond | −0.587 | directional polar contact |
| rotatable bonds | 0.0585 | conformational entropy penalty |

Interaction cutoff 8 Å, with XS radii per element. The grid (`ProteinGrid`) buckets heavy
atoms into 4 Å cells for neighbour lookup, excluding water and masked atoms.

### Search

Pocket detection followed by flexible Monte Carlo pose search — rigid-body moves plus
torsion perturbation, with local refinement of accepted poses.

### What this is not

The module header says it plainly and so does this document: **a re-implementation for
interactive use, not a validated replacement for Vina or Glide.** Scores are useful as
relative rankings within a session.

It has not been benchmarked against a redocking set. There is therefore no accuracy figure
for this code. Earlier versions of this document claimed "94% RMSD ≤ 2.0 Å" and "docking
validation RMSD ≤ 2.0 Å" as quality assurance — neither was ever measured, and both have
been removed rather than replaced with a different number. Benchmarking against PDBbind
core or Astex would produce a real figure; nobody has done it.

---

## The real dynamics path: `/api/md`

All-atom OpenMM in implicit solvent, served by `server/server.py`:

```
POST /api/md         start a simulation
GET  /api/md/<job>   poll progress, fetch trajectory frames
```

Requires `openmm` and `pdbfixer`. When either is missing the endpoint returns HTTP 501 with
`{"error": "server needs openmm and pdbfixer"}` — it does not fabricate a trajectory.
`GET /api/health` reports which engines are installed.

Structures are prepared with PDBFixer before simulation. While dynamics run, the front end
streams frames and the ligand can be dragged through the pocket interactively, with the
structure responding.

**Simulation length** is whatever the caller requests and the hardware sustains. The
repository contains no long-timescale production runs. Earlier versions of this document
claimed "100–1000 ns production runs", "50,000 frames per simulation" and "100 ns in 24
hours"; none of those runs happened, and the figures have been removed.

---

## The placeholder path: `molecular_research_pipeline.py`

### What it actually does

The module's own docstring is accurate: values are emitted as `SyntheticValue`, print with
`[SYNTHETIC]`, and sit in records whose `provenance` field records that no model ran.
`server/synthetic_provenance.py` raises `SyntheticResultWarning` the first time a synthetic
value is generated:

> Synthetic placeholder values are being generated: no docking, MD, ADMET or assay model
> has run. Every such number prints with '[SYNTHETIC]' and every record carries a
> 'provenance' field. Do not report them as results.

This labelling is enforced by `tests/test_synthetic_provenance.py`.

### Why it still exists

It defines the shape of a pipeline — the stages, the record types, the scoring weights —
that real engines could be wired into. The composite scoring weights
(30% binding affinity, 25% ADMET, 20% stability, 15% synthesis feasibility, 10% novelty)
and the priority tiers (Lead ≥ 0.80, Candidate ≥ 0.60, Hit ≥ 0.40, Inactive below) are
design decisions worth keeping.

But the inputs those weights combine are currently random numbers. A composite score built
from `random()` is not a ranking of anything.

### Claims removed from this section

- "Dock 100+ compounds/day" — no batch docking has been run at any rate.
- "Binding energy −10 to −6 kcal/mol range" — the range of a random distribution.
- "Accuracy: 94% RMSD ≤ 2.0 Å" — never measured.
- "100–1000 ns simulations" — never run.
- "Ranking accuracy: validated against experimental data" — no experimental comparison
  exists.
- "Hit rate 0.1–0.2% (industry standard)" — quoting an industry figure as though it were
  this system's measured output.
- "12 months to market vs 10 years", "50% cost reduction" — invented development-timeline
  and cost claims.
- "Patent search (novelty confirmation)" — no patent search is implemented.

---

## Drug repurposing: `server/repurposing_engine.py`

This one is real and measured. It builds repurposing hypotheses from shared-target clinical
precedent — if drugs against a target have registered clinical records in an indication,
that indication becomes a hypothesis for a new compound hitting the same target.

`scripts/validate_repurposing_recall.py` tests it against seven documented real-world
repurposing cases:

```
recovered at any rank : 5/7 (71%)
recovered in top 10   : 57%
best positive score   : 6.30
best control score    : 1.20
```

Dimethyl fumarate for relapsing MS comes back at rank 1; raloxifene for breast cancer risk
reduction at rank 3. The two misses print explanations rather than failing silently:

- **minoxidil → androgenetic alopecia:** KCNJ11 and ABCC9 have precedent drugs, but none
  with a registered clinical record matching alopecia. A second indication is not reachable
  from shared-target evidence.
- **metformin → oncology:** GPD2 resolves, but no *other* drug has a clinical record
  against it, so with the compound itself excluded there is no precedent to transfer.

Negative controls — mannitol, and an AGI inventory compound with no database identity —
score 1.20 and 0.00 respectively, well below the positives.

---

## Data sources

11 databases have working clients making real requests: PubMed, UniProt, RCSB PDB,
AlphaFold DB, ChEMBL, PubChem, ClinVar, Open Targets, Reactome, STRING and
ClinicalTrials.gov. Responses cache to `~/.cache/agi-bioxr/db_cache.sqlite`.

`server/biotech_database_integration.py` registers 29 databases. The remaining 18 have no
client and return `status: 'no_client'`, querying nothing. Its module docstring records the
history honestly:

> this module used to "connect" 29 databases by writing `{'status': 'connected'}` into a
> dict and answered every query with `results_count=42`. No network call was ever made.

Earlier versions of this document listed "29 Databases" as input data sources with record
counts totalling "1.5B+". That total was a string literal in the source, not a count. There
are also no MCP servers behind any of these; `mcp_endpoint` is retained only for backward
compatibility.

---

## Disease target panels

Four curated panels, 68 targets, each backed by identifiers that re-resolve against live
services:

| Panel | Targets | Checks |
|---|---|---|
| ALS | 20 | 250/250 |
| Parkinson's | 18 | 207/207 |
| Shriners — skeletal, neuromuscular, burn injury | 15 | 190/190 |
| St Jude — paediatric oncology | 15 | 263/263 |

Run `.venv/bin/python scripts/verify_panel_citations.py <panel>` to re-check. Use the venv
interpreter; the system `python3` lacks `requests` and the run fails for environmental
reasons rather than real ones.

Panel names describe the disease areas covered. They are scope labels, not claims of any
relationship with any organisation.

---

## Research focus

This subsystem was built to serve research into ALS, Parkinson's, paediatric oncology and
paediatric skeletal and neuromuscular conditions — the same goals pursued by organisations
working on childhood and neurodegenerative disease.

**No partnership, agreement, sponsorship or endorsement exists with any such organisation.**
An earlier version of this document ended with "Ready for deployment to ALS Association,
MJF, Shriners"; that line was false and has been removed.

---

## Honest next steps

1. **Benchmark the docking function** against a standard redocking set, or state
   permanently that it is for interactive ranking only.
2. **Wire the pipeline to the real engines, or delete it.** Placeholder values that look
   like results are the most dangerous thing in this subsystem, and labelling is a
   mitigation rather than a fix.
3. **Implement clients for the remaining databases, or trim the registry** so the count
   reflects what can be queried.
4. **Run a real MD production simulation** and report its actual length and wall time.
