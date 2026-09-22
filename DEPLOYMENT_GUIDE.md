# biodao.blockchain: Deployment Guide

**Last verified:** 2026-09-22

## What this is

An AR/VR molecular research workspace that runs locally. This guide covers running it on
your own machine and what would be involved in hosting it for others.

**It is not currently deployed anywhere.** There is no hosted instance, no cluster, no
managed database and no operational commitment. Nothing below describes a running
production system; the "hosting it for others" section describes work that has not been
done.

---

## Quick start

### 1. Build the environment

```bash
cd ~/Projects/agi-bioxr
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

### 2. Start the server

```bash
.venv/bin/python server/server.py
```

Or `make serve`. The app listens on <http://localhost:8000> and loads SOD1 so there is
something on screen immediately.

The server is a Python standard-library `ThreadingHTTPServer` — not Flask, and not behind
a WSGI container. Only the standard library is required to start it; RDKit, pypdf, OpenMM,
PDBFixer and google-cloud-bigquery each enable their own feature when importable. `GET
/api/health` reports which optional engines are present.

### 3. Try the headset interface

Without a headset, open <http://localhost:8000/?emulate=quest3> for the WebXR emulator.

With one, WebXR needs a secure origin:

```bash
# Over Wi-Fi, any headset — accept the self-signed certificate once
.venv/bin/python server/server.py --https --port 8443

# Over USB, Quest only, no certificate warning
adb reverse tcp:8000 tcp:8000
```

---

## API endpoints

These are the endpoints `server/server.py` actually serves:

```
GET  /api/health              which optional engines are installed
POST /api/embed               SMILES -> 3D conformer (RDKit ETKDGv3 + MMFF94)
POST /api/extract             PDF / text upload -> SMILES + compound IDs
POST /api/md                  start an all-atom OpenMM simulation (implicit solvent)
GET  /api/md/<job>            poll progress, fetch trajectory frames
POST /api/library             save the AGI compound library to data/
POST /api/room/<room>         publish collaboration state (pose, target, avatar)
GET  /api/room/<room>/events  server-sent events stream of other participants
POST /api/bigquery            Google BigQuery public-dataset query (needs gcloud auth)
```

Multi-user collaboration uses server-sent events, not WebSockets. `/api/md` returns HTTP
501 when `openmm` and `pdbfixer` are not installed, rather than returning a fabricated
trajectory.

---

## Verifying an install

```bash
make verify     # test + imports + reachable
```

On 2026-09-22 this produced:

| Check | Result |
|---|---|
| `make test` | 708 passed, 1 xfailed |
| `make imports` | passes |
| `make reachable` | 22 of 22 JS modules reachable from `main.js` |

Citation checks hit the network and are run separately, per panel:

```bash
.venv/bin/python scripts/verify_panel_citations.py ALS          # 250/250
.venv/bin/python scripts/verify_panel_citations.py Parkinsons   # 207/207
.venv/bin/python scripts/verify_panel_citations.py Shriners     # 190/190
.venv/bin/python scripts/verify_panel_citations.py StJude       # 263/263
```

Use the venv interpreter. The system `python3` has neither `requests` nor RDKit, and
several modules degrade quietly on a failed import, so the wrong interpreter produces a
passing run that proves nothing — which is exactly why the `Makefile` pins `.venv/bin/python`.

`--seed-bad` injects a deliberately broken control target; the run must then fail. Use it
if you want to confirm the checker can still detect a bad citation.

All of this runs in CI on every push — see `.github/workflows/ci.yml` and
`.github/workflows/citations.yml`.

The repository is under a proprietary licence, all rights reserved (`LICENSE`). Check it
before redistributing or hosting anything built from it.

---

## Data storage

SQLite, in `data/`. Workflow state, checkpoints and agent memory use the schema in
`server/workflow_persistence.py`; the database-response cache lives at
`~/.cache/agi-bioxr/db_cache.sqlite`.

`server/database_migration.py` contains a SQLite-to-PostgreSQL migration path. It has not
been run against a live PostgreSQL instance.

---

## Security posture

`server/auth.py` provides JWT issuance and role checks (admin, PI, researcher, viewer),
and a SHA-256 provenance ledger records operations.

Several real defects were found and fixed in September 2026: an authentication bypass that
accepted any password, a JWT signing key committed to the repository as a literal, and
both servers binding `0.0.0.0` by default. Both servers now default to `127.0.0.1`, and
`--host 0.0.0.0` has to be passed deliberately to reach a headset over Wi-Fi.

Be clear about what the remaining posture does and does not mean:

- The server is written for single-machine, single-operator use and has not been hardened
  for hosting. No penetration test or third-party security audit has been performed.
  Earlier revisions of this document claimed a completed security audit; none exists.
- `--https` uses a self-signed certificate intended for getting WebXR working in a
  headset, not for protecting traffic on an untrusted network.
- The collaboration room endpoints are unauthenticated.
- See `SECURITY.md` for how to report a vulnerability.

---

## If you wanted to host this

None of the following has been done. It is a sketch of the work, not a checklist that is
partly complete.

**Substantial gaps to close first:**

1. Put a real WSGI/ASGI server in front of, or in place of, the stdlib HTTP server.
2. Decide what `server/molecular_research_pipeline.py` should do. It currently returns
   `[SYNTHETIC]`-labelled placeholder values; those must not reach a user who might read
   them as results.
3. Benchmark whatever you intend to promise. There is no measured throughput, latency or
   uptime figure for this codebase, and nothing in the repository produces one.
4. Review `server/scaling_infrastructure.py` and `server/performance_optimization.py`.
   They are in-process Python objects describing load balancing and caching; they are not
   wired to any cluster, Redis or PostgreSQL.
5. Threat-model multi-user access. The collaboration room endpoints are unauthenticated.

**Then the ordinary work:** TLS from a real CA, a managed database, backups, log
aggregation, metrics, and an on-call arrangement if anyone is going to depend on it.

---

## Troubleshooting

**`/api/md` returns 501.** OpenMM and PDBFixer are not installed in the active
environment. `GET /api/health` lists what is present.

**Imports fail, or tests pass suspiciously fast.** You are probably on the system
`python3`. Use `.venv/bin/python`.

**Citation checks fail with "the 'requests' package is not installed".** Same cause — the
venv interpreter has `requests`, the system one does not. This is an environment problem,
not a bad citation.

**"Enter VR" is greyed out.** WebXR needs a secure origin. Use `--https`, or
`adb reverse` over USB, or the `?emulate=quest3` emulator on the desktop.

**A scanned PDF imports nothing.** It holds images of structures with no text layer.
Optical chemical structure recognition (DECIMER, OSRA) would be needed first; the app
reports this when it detects one.

---

## Research focus

The workspace is built to serve research into ALS, Parkinson's, and the skeletal,
neuromuscular and burn-injury conditions treated in paediatric hospitals, with curated
target panels assembled around those disease areas.

This reflects the project's design intent and nothing more. **No partnership, agreement,
sponsorship or endorsement exists with any organisation working in these areas**, and
nothing in this repository should be read as implying one.

---

**Contact:** see `SUPPORT.md`.
