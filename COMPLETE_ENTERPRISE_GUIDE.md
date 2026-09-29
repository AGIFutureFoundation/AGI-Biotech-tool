# biodao.blockchain: Platform Guide

**Last verified:** 2026-09-22
**Licence:** proprietary, all rights reserved (see `LICENSE`)

A full description of what the platform does, what it does not do, and how the pieces fit
together.

---

## Scope of this document

An earlier version of this file described a deployed enterprise product with service-level
commitments, a support rotation, an operating budget and institutional partners. None of
that existed. The document has been rewritten to describe the software that is actually in
this repository.

Specifically, this platform has: no hosted instance, no cluster, no Redis, no PostgreSQL
deployment, no support channel, no SLA, no on-call rotation, and no users. It runs locally,
for one person at a time.

---

## The platform at a glance

| Capability | State |
|---|---|
| AR/VR molecular workspace (WebXR) | Works — headset or desktop browser |
| Structure loading (PDB, mmCIF, AlphaFold) | Works |
| Docking — Vina-form empirical scoring | Works, unbenchmarked |
| Molecular dynamics — OpenMM | Works when OpenMM + PDBFixer installed |
| Document ingestion, 16 formats | Works |
| Live public database clients | Works — 11 databases |
| Curated disease target panels | Works — 4 panels, 68 targets, citations verified |
| Drug repurposing from clinical precedent | Works — 5 of 7 documented cases recovered |
| Python `molecular_research_pipeline.py` | **Placeholder values, labelled `[SYNTHETIC]`** |
| ML gesture/voice recognition | **Stub — returns random choices** |
| Scaling / load-balancing infrastructure | **Unexercised scaffolding, nothing deployed** |

---

## Research focus

The workspace was built to serve the same research goals as organisations working on
childhood and neurodegenerative disease: ALS, Parkinson's, paediatric oncology, and the
skeletal, neuromuscular and burn-injury conditions treated in paediatric hospitals. The
curated target panels are assembled around those disease areas.

That is a statement about design intent and scope. **No partnership, agreement,
sponsorship, collaboration or endorsement exists with any organisation working in these
areas, and none has ever existed.** Nothing in this repository should be read as implying
otherwise.

---

## Architecture

```
                    Browser or WebXR headset
                              │
              ┌───────────────┴────────────────┐
              │  Front end (js/, 22 modules)   │
              │  structure · dock · md · xr    │
              │  hands · voice · collab        │
              └───────────────┬────────────────┘
                              │  HTTP + server-sent events
              ┌───────────────┴────────────────┐
              │  server/server.py              │
              │  stdlib ThreadingHTTPServer    │
              │  /api/embed  /api/extract      │
              │  /api/md     /api/library      │
              │  /api/room   /api/bigquery     │
              └───────────────┬────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   RDKit (embed,        OpenMM + PDBFixer     db_clients.py
   extraction)          (dynamics)            11 live databases
                                              + local SQLite cache
```

The front end does the interactive molecular work — docking, rendering, pose manipulation.
The server does what a browser cannot: conformer generation, PDF extraction, all-atom
dynamics, and outbound database queries. Each optional engine switches its feature on when
importable; `GET /api/health` reports which are present.

---

## What works, in detail

### Docking (`js/dock.js`)

A real empirical scoring function in the form of AutoDock Vina, using the published term
set and weights (Trott & Olson, 2010): gauss1, gauss2, repulsion, hydrophobic, hydrogen
bonding, plus a rotatable-bond penalty. Grid-accelerated neighbour lookup, pocket
detection, and flexible Monte Carlo pose search.

The limit, stated in the module header and repeated here: this is a re-implementation for
interactive use, **not a validated replacement for Vina or Glide**. Scores are meaningful
as relative rankings within a session.

It has not been benchmarked against a redocking set, so there is no accuracy figure. An
earlier version of this document claimed "94% RMSD ≤ 2.0 Å"; that number was never
measured and has been removed rather than replaced.

### Molecular dynamics (`/api/md`)

Real all-atom OpenMM in implicit solvent. Requires `openmm` and `pdbfixer`; without them
the endpoint returns HTTP 501 rather than fabricating a trajectory. While dynamics run, the
ligand can be dragged through the pocket and the structure pushes back.

Simulation length is whatever the caller requests and the hardware sustains. The repository
contains no long-timescale production runs, so the "100–1000 ns" range claimed previously
has been removed.

### Document ingestion (`server/document_ingest.py`)

16 reader types across 25 extensions: PDF, DOCX, XLSX, HTML, XHTML, XML, JSON, CSV, TSV,
Markdown, plain text, Pages (detected and redirected), and the chemistry formats PDB, MOL,
MOL2, SDF and SMILES.

The awkward parts of exported compound sheets are handled: SMILES split across lines are
rejoined and revalidated, an index number glued to the front of a structure is read as the
compound number, and several AGI ID spellings are recognised. Every structure is validated
with RDKit; anything that looks like a SMILES but will not parse goes to a review list
rather than being silently dropped.

### Live databases (`server/db_clients.py`)

11 databases have working clients that make real requests:

PubMed · UniProt · RCSB PDB · AlphaFold DB · ChEMBL · PubChem · ClinVar · Open Targets ·
Reactome · STRING · ClinicalTrials.gov

Responses are cached in a local SQLite cache at `~/.cache/agi-bioxr/db_cache.sqlite`.

`server/biotech_database_integration.py` registers 29 databases in total. The other 18 have
no client and answer `status: 'no_client'`, querying nothing. Earlier documentation
described all 29 as connected, with "1.5B+ records" — that figure was a string literal in
the source code, not a count of anything, and the related "862.4M+" was produced by calling
`int()` on the string `"30M"`.

### Disease target panels (`server/disease_panels.py`)

Four curated panels, 68 targets:

| Panel | Targets | Citation checks |
|---|---|---|
| ALS | 20 | 250/250 pass |
| Parkinson's | 18 | 207/207 pass |
| Shriners (skeletal, neuromuscular, burn injury) | 15 | 190/190 pass |
| St Jude (paediatric oncology) | 15 | 263/263 pass |

Each target carries a mechanism, inheritance pattern, prevalence, AlphaFold model and PDB
count, plus literature evidence. `scripts/verify_panel_citations.py` re-resolves every
cited identifier — UniProt accessions, PDB entries, AlphaFold models, ChEMBL targets,
PubMed IDs and quoted sentences — against the live services. `--seed-bad` adds a
deliberately broken control target, and the run must then fail; that is how the checker is
kept honest.

Panel names refer to the disease areas the panels cover. They are descriptive labels for
scope, not claims of any relationship.

### Drug repurposing (`server/repurposing_engine.py`)

Generates repurposing hypotheses from shared-target clinical precedent. Validated against
seven documented real-world repurposing cases by
`scripts/validate_repurposing_recall.py`:

- **Recovered: 5 of 7** (71%), including dimethyl fumarate for relapsing MS at rank 1 and
  raloxifene for breast cancer risk reduction at rank 3.
- **Missed: 2**, each with a printed explanation rather than a silent failure. Minoxidil's
  alopecia indication is not reachable from shared-target evidence; metformin's only
  resolved target has no other drug with a clinical record against it.
- **Negative controls** score well below the positives — best positive 6.30, best control
  1.20 — so the signal is not an artefact of scoring everything highly.

Earlier documentation claimed repurposing delivers "12 months to market versus 10 years"
and "50% cost reduction". Those were invented; this engine produces ranked hypotheses for a
human to evaluate, and makes no claim about development timelines or cost.

---

## What does not work

### The Python molecular pipeline returns placeholders

`server/molecular_research_pipeline.py`, `server/pyrene_apoptotic_discovery.py` and
`server/repurposing_engine.py`'s legacy `DrugRepurposingEngine` do not compute binding
energies, MD trajectories or ADMET properties. They return `random()`-derived values.

These are labelled rather than removed: values are emitted as `SyntheticValue`, print with
a `[SYNTHETIC]` marker, sit in records carrying a `provenance` field, and raise
`SyntheticResultWarning` on first use (`server/synthetic_provenance.py`), with the labelling
covered by `tests/test_synthetic_provenance.py`.

**Do not report these numbers as results.** The real docking and dynamics are the
JavaScript `dock.js` path and the OpenMM `/api/md` endpoint.

### ML recognition is a stub

`server/ml_enhanced_recognition.py` returns `random.choice(gestures)` with a `random.gauss`
confidence. There is no trained model and no ensemble. The "94% gesture accuracy" and "89%
voice accuracy" in earlier documents measured nothing.

### Performance figures do not exist

`server/load_testing.py` awaits `asyncio.sleep(random.uniform(...))` in place of work. The
throughput, latency and uptime numbers that appeared throughout earlier documentation —
596 ops/second, p99 165ms, 99.5% uptime, 100 concurrent workflows at 100% success — were
produced by timing those sleeps. No load test has been run against the real system and no
benchmark exists in the repository.

### Scaling infrastructure is a sketch

`server/scaling_infrastructure.py` and `server/performance_optimization.py` define load
balancers, auto-scalers, connection pools and caches as in-process Python objects, with
Kubernetes manifests as text. Nothing is deployed behind them.

---

## Compliance and security

**Provenance.** A SHA-256 ledger records operations, with timestamps and parameter
versioning. FAIR-format export (JSON, CSV, LaTeX) is available.

**Access control.** `server/auth.py` provides JWT issuance and role checks (admin, PI,
researcher, viewer).

**Fixed defects.** Three real problems were found and fixed in September 2026: an
authentication bypass that accepted any password, a JWT signing key committed as a literal,
and both servers binding `0.0.0.0` by default. Both now default to `127.0.0.1`; reaching a
headset over Wi-Fi requires passing `--host 0.0.0.0` deliberately.

**Remaining posture.** The server is written for single-machine, single-operator use and
has not been hardened for hosting. No penetration test or third-party security audit has
been performed — an earlier version of this document claimed one was complete; none exists.
The collaboration room endpoints are unauthenticated. See `SECURITY.md` to report a
vulnerability.

**Data handling.** Everything runs locally. No data leaves the machine except public
database lookups the user triggers.

---

## Continuous integration

`.github/workflows/ci.yml` runs the test suite, import checks and JS reachability on every
push. `.github/workflows/citations.yml` re-resolves the panel citations against live
services. On 2026-09-22: 708 passed, 1 xfailed; 22 of 22 JS modules reachable; 910 citation
checks passing across the four panels.

---

## Getting started

```bash
cd ~/Projects/agi-bioxr
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python server/server.py
```

Open <http://localhost:8000>. See `README.md` for headset setup and compound import,
`DEPLOYMENT_GUIDE.md` for endpoints and what hosting would involve, and `PROJECT_STATUS.md`
for the verified state of each component.

Support is best-effort via the repository — see `SUPPORT.md`. There is no SLA, no response
commitment and no on-call rotation.
