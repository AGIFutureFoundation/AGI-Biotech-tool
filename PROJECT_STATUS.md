# biodao.blockchain: Project Status

**Last verified:** 2026-09-26
**Scope:** an AR/VR molecular workspace for drug discovery, built to serve the same
research goals as organisations working on ALS, Parkinson's and childhood disease.

This file describes what is in the repository and what has actually been run. Every
figure below is reproducible with the command given next to it. Where something is not
measured, this file says so rather than estimating.

---

## Executive summary

biodao.blockchain is a working molecular workspace: it loads real protein structures,
docks compounds with a real scoring function, runs real molecular dynamics, ingests
compound collections from 16 document formats, and queries live public biomedical
databases. Its four curated disease-target panels are backed by citations that
re-resolve against the source services on demand.

It is **not** a deployed product. There is no cluster, no hosted instance, no user base,
and no service-level commitment. It runs locally, for one person at a time, on the
machine that starts it.

The research areas it targets — ALS, Parkinson's, and the skeletal, neuromuscular and
burn-injury conditions treated in paediatric hospitals — reflect the project's design
intent. **No partnership, agreement, sponsorship or endorsement exists with any
organisation working in those areas.**

---

## What is verified

Each row is a command you can run. The figures are from a run on 2026-09-22.

| Check | Command | Result |
|---|---|---|
| Test suite | `make test` | 1116 passed, 1 xfailed |
| Module imports | `make imports` | passes |
| JS module reachability | `make reachable` | 24 of 24 modules reachable from `main.js` |
| Panel citations — ALS | `scripts/verify_panel_citations.py ALS` | 250/250 checks passed |
| Panel citations — Parkinson's | `scripts/verify_panel_citations.py Parkinsons` | 207/207 checks passed |
| Panel citations — Shriners | `scripts/verify_panel_citations.py Shriners` | 190/190 checks passed |
| Panel citations — St Jude | `scripts/verify_panel_citations.py StJude` | 263/263 checks passed |
| Repurposing recall | `scripts/validate_repurposing_recall.py` | 5 of 7 documented cases recovered; both misses explained |

These checks run in CI on every push (`.github/workflows/ci.yml` and `citations.yml`), so
a regression shows up without anyone remembering to run them.

The citation checks re-resolve every cited identifier — UniProt accessions, PDB entries,
AlphaFold models, ChEMBL targets, PubMed IDs and quoted sentences — against the live
services. `--seed-bad` adds a deliberately broken control target and the run must then
fail, which is how the checker itself is kept honest.

Run the citation checks with the venv interpreter (`.venv/bin/python`). The system
`python3` lacks `requests`, and the checks then fail for environmental reasons rather
than real ones.

---

## What works

**Structure and rendering.** Loads PDB and mmCIF, AlphaFold models by UniProt accession,
and local files. Cartoon, surface, stick and ball-and-stick representations.

**Docking (`js/dock.js`).** A real empirical scoring function in the form of AutoDock
Vina — the same term set and published weights (Trott & Olson, 2010): gauss1, gauss2,
repulsion, hydrophobic, hydrogen bonding, with a rotatable-bond penalty. Grid-accelerated
pocket detection and flexible Monte Carlo pose search.

The module's own header states the limit plainly, and so does this document: it is a
re-implementation for interactive use, **not a validated replacement for Vina or Glide**.
Scores are useful as relative rankings within a session. It HAS now been benchmarked:
`node evals/redock.mjs` re-docks four crystal ligands and measures RMSD against the
experimental pose. Four consecutive runs on 2026-09-27 gave 3/4, 3/4, 3/4 and 2/4 within
2 Å (per-run medians 1.25, 1.69, 1.47, 2.12 Å). The search is Monte Carlo, so that spread
is the result — a single run quoted as "the" accuracy would be a lucky sample dressed as a
measurement. Four cases is also a small set; it is a sanity check, not a validation study,
and it remains not a replacement for Vina or Glide.

**Molecular dynamics (`/api/md`).** Real all-atom OpenMM in implicit solvent, via
`server/server.py`. Requires `openmm` and `pdbfixer`; the endpoint returns HTTP 501 when
they are absent rather than faking a trajectory. Simulation length is whatever the caller
asks for and the hardware sustains — the repo contains no long-timescale production runs,
so no nanosecond figure is claimed.

**Document ingestion (`server/document_ingest.py`).** 16 reader types across 25 file
extensions: PDF, DOCX, XLSX, HTML, XML, JSON, CSV, TSV, Markdown, plain text, and the
chemistry formats PDB, MOL, MOL2, SDF and SMILES. SMILES broken across lines are rejoined
and revalidated with RDKit; anything that will not parse goes to a review list instead of
being silently dropped.

**Live database clients (`server/db_clients.py`).** 11 databases have working clients that
make real requests: PubMed, UniProt, RCSB PDB, AlphaFold DB, ChEMBL, PubChem, ClinVar,
Open Targets, Reactome, STRING and ClinicalTrials.gov. Responses are cached in a local
SQLite cache.

**Disease target panels (`server/disease_panels.py`).** Four curated panels, 68 targets
total — ALS (20), Parkinson's (18), Shriners (15), St Jude (15) — each target carrying a
mechanism, inheritance pattern, prevalence, AlphaFold model and PDB count, with literature
evidence that re-resolves against PubMed.

**Drug repurposing (`server/repurposing_engine.py`).** Builds repurposing hypotheses from
shared-target clinical precedent. Validated against seven documented real-world
repurposing cases: it recovers five, and `scripts/validate_repurposing_recall.py` prints a
specific reason for each of the two misses rather than hiding them — minoxidil's alopecia
indication is not reachable from shared-target evidence, and metformin's only resolved
target has no other drug with a clinical record against it. Negative controls score well
below the positives (best positive 6.30, best control 1.20).

**Provenance.** A SHA-256 ledger records operations, and FAIR-format export is available.

**Licensing.** The repository carries a proprietary licence, all rights reserved. See
`LICENSE`.

---

## What does not work, or is not what its name suggests

This section exists because earlier versions of this document claimed otherwise.

**The Python molecular pipeline returns placeholder values.**
`server/molecular_research_pipeline.py`, `server/pyrene_apoptotic_discovery.py` and
`server/repurposing_engine.py` do not compute binding energies, MD trajectories, ADMET
properties or repurposing scores. They return `random()`-derived placeholders.

These are now *labelled* rather than removed: values are emitted as `SyntheticValue`,
print with a `[SYNTHETIC]` marker, sit in records carrying a `provenance` field, and raise
`SyntheticResultWarning` on first use (`server/synthetic_provenance.py`). The labelling is
covered by `tests/test_synthetic_provenance.py`. **Do not report these numbers as
results.** The real docking and MD are the JavaScript `dock.js` path and the OpenMM
`/api/md` endpoint, not this pipeline.

**The database registry lists more than it can query.**
`server/biotech_database_integration.py` registers 29 databases; 11 have clients. The
other 18 return `status: 'no_client'` and query nothing. Earlier documentation described
all 29 as "connected" with "1.5B+ records" — that figure was a string literal in the
source, never a count of anything.

**The ML recognition module is a stub.**
`server/ml_enhanced_recognition.py` returns `random.choice(gestures)` with a
`random.gauss` confidence. The "94% gesture accuracy" and "89% voice accuracy" reported in
earlier documents were not measurements of anything. There is no trained model, no
ensemble, and no accuracy figure.

**The load-testing module measures itself.**
`server/load_testing.py` awaits `asyncio.sleep(random.uniform(...))` in place of work. The
throughput, latency and uptime numbers that appeared throughout earlier documentation
(596 ops/second, p99 165ms, 99.5% uptime) were produced by timing those sleeps. No load
test has been run against the real system, and there is no benchmark in the repository.

**The scaling and performance modules are unexercised scaffolding.**
`server/scaling_infrastructure.py` and `server/performance_optimization.py` define load
balancers, auto-scalers, connection pools and caches as in-process Python objects. Nothing
is deployed behind them: no Kubernetes cluster, no Redis, no PostgreSQL instance. Treat
them as a design sketch, not as infrastructure.

**There is no user base.** Earlier documents cited "50+ researchers". There are no users.

---

## Running it

```bash
cd ~/Projects/agi-bioxr && .venv/bin/python server/server.py
```

Then open <http://localhost:8000>. See `README.md` for headset setup, compound import and
the demo running order, and `DEPLOYMENT_GUIDE.md` for what deployment would actually
involve.

---

## Honest next steps

These are unstarted, and listing them here is not a commitment to a date.

1. **Benchmark the docking function.** Redock a standard set (PDBbind core, Astex) and
   publish a real RMSD success rate — or state that the scoring function is for
   interactive ranking only and stop implying accuracy.
2. **Replace or delete the synthetic pipeline.** Either route
   `molecular_research_pipeline.py` to the real docking and MD paths, or remove it so its
   placeholder values cannot be mistaken for results.
3. **Measure something before claiming performance.** If throughput matters, write a
   benchmark that exercises the real endpoints.
4. **Implement clients or trim the registry.** 18 databases are listed but unreachable.
5. **Expand panel coverage** beyond the current 68 targets, keeping every addition backed
   by an identifier that re-resolves.

---

*Historical session logs from September 2026 (`PHASE_7_COMPLETE_SUMMARY.md`,
`PHASE_9_MOLECULAR_COMPLETE.md`, `SESSION_SUMMARY.txt`, `EXTENDED_SYSTEM_SUMMARY.txt`,
`PHASE_7_FILES_SUMMARY.txt`) are retained as dated records and carry superseded-record
headers. Their figures are not measurements and should not be cited.*
