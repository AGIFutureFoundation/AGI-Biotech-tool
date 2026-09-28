# biodao.blockchain Hourly Review Report

## Timestamp
2026-09-28 (automated run, `main` @ `806b113`)

## Phase Status
- **Phase 0-3 (auth, projects, orchestration, Flask server):** ❌ BROKEN, not complete as docs claim.
  `server/server.py` is two unrelated programs concatenated in one file. Lines ~1-500 are a working stdlib
  `http.server` app (RDKit embedding, OpenMM/PDBFixer MD, PDF extraction, SSE collaboration, allowlisted
  proxy — this part is real). Starting at line ~501, a second "Phase 1 Enhancements" section uses
  `@app.route(...)`, `request`, `jsonify`, `g` — **none of which are ever imported or an `app = Flask(...)`
  instance created.** Running this file raises `NameError: name 'app' is not defined` at the first
  `@app.route` decorator. Everything after that point (WebSocket server wiring, master agent, workflow
  orchestrator, "Phase 2/3" routes) is unreachable dead code. `requirements.txt` doesn't even list Flask,
  PyJWT, or websockets, so `pip install -r requirements.txt` wouldn't satisfy this code's imports anyway.
- **Phase 4 (hardening: error_recovery, workflow_persistence, monitoring):** ✅ Real implementations
  (exponential backoff + circuit breaker state machine; SQLite-backed checkpoint/resume; real stats
  aggregation) but **not wired to any live endpoint** — no `/health` or `/metrics` route exists because the
  Flask layer they'd attach to doesn't run (see above).
- **Phase 5 (load testing, database migration, ML):** ⚠️ Partial. `load_testing.py` has a genuine asyncio
  concurrency harness, but `simulate_workflow()` just does `asyncio.sleep()` with random durations — it
  never calls real application code, so it measures nothing about the actual system.
- **Phase 9 (molecular research pipeline):** ⚠️ Fabricated science. Docking/MD/ADMET results are generated
  with `random.random()` / `random.gauss()` (`molecular_research_pipeline.py:101,173-174`), and the test
  suite asserts against the same ranges the fake generator was written to produce — tests "pass" but
  validate nothing scientific.

## Compliance Score
**25/100** — Critical auth bypass on `main` (fix already proposed in open PR #2, unmerged), no server-side
audit trail despite docs claiming one, hardcoded fallback JWT signing secret, debug mode enabled, and a
live command-injection primitive (`server/agents.py:172-194`, `subprocess.run(shell=True)` on
caller-supplied input, not currently routed but present in an "agent workflow" module).

## Database Integration
**FAIL.** `server/biotech_database_integration.py` and `biotech_molecular_integration.py` contain **zero**
HTTP client imports (no `requests`/`urllib`/`httpx`/`aiohttp`). All 30 claimed integrations (ClinicalTrials.gov,
Europe PMC, STRING, Reactome, InterPro, Protein Atlas, UniChem, PDBe, gnomAD, etc.) are metadata dict
entries with a fake `mcp://...` URL; `query_database()` returns hardcoded `'results_count': 42,  # Simulated`
and fabricated sample results. The only real outbound HTTP calls in the repo are in the original stdlib
`server.py` proxy allowlist and its RCSB PDB fetch — unrelated to the "enterprise" integration modules this
task was asked to verify.

## Enterprise Hardening
**Partial PASS on isolated modules, FAIL on integration.** `error_recovery.py` and `workflow_persistence.py`
are solid, real implementations. `monitoring.py` does real aggregation but is never exposed via an endpoint.
None of this is reachable at runtime because the Flask app it should protect/monitor never instantiates
(see Phase Status above).

## Top Issues (Priority Order)
1. **CRITICAL** — `server/auth.py:111-121` `authenticate_user()` never checks the password; anyone who
   knows/guesses a registered email gets a valid JWT. **An open PR already fixes this: #2,
   "Fix authentication bypass: verify passwords in login/register" — still unmerged on `main`.**
2. **CRITICAL** — `server/server.py:501+` — the entire "Phase 1-3" Flask section is unreachable dead code
   (undefined `app`/`request`/`jsonify`/`g`); README/PROJECT_STATUS.md claims of "Phase 1-3 ✅ COMPLETE"
   are false as written. No open PR addresses this.
3. **CRITICAL** — All 30 "database integrations" in `biotech_database_integration.py` /
   `biotech_molecular_integration.py` are fabricated/simulated, contradicting documentation. No open PR
   addresses this.
4. **HIGH** — `server/agents.py:172-194` `execute_bash_job` runs `subprocess.run(command, shell=True)` on
   caller-supplied input — command injection if ever wired to a route.
5. **HIGH** — `server/auth.py:17` `SECRET_KEY` defaults to the literal `'dev-secret-change-in-production'`
   when `JWT_SECRET` is unset — production deployments that forget the env var sign tokens with a public,
   guessable secret.
6. **HIGH** — `server/server.py` calls `app.run(debug=True, ...)` in three places — Werkzeug debugger /
   remote-code-execution exposure if this code path is ever fixed and deployed.
7. **MEDIUM** — No server-side audit trail of authenticated actions anywhere in `server/*.py`, despite
   `PROJECT_STATUS.md` claiming a completed "Provenance ... SHA-256 ledger." Only a disconnected
   client-side `js/ledger.js` hash chain exists (browser-only, not tied to `request.user` or persisted
   server-side).
8. **MEDIUM** — Fabricated docking/MD/ADMET results in the molecular research pipeline are asserted against
   by the test suite's own tautological ranges, giving false confidence that the science is validated.

## Open PR Status (avoid duplicating work)
- **#2 — "Fix authentication bypass: verify passwords in login/register"** (unmerged, `mergeable_state: clean`).
  Adds PBKDF2 password hashing, closes the exact bug in Top Issue #1. Small, scoped, looks reasonable — recommend
  human review + merge rather than a new PR for the same issue.
- **#1 — "Enterprise hardening: a test suite, four verification gates, and the silent bugs they found"**
  (unmerged, `mergeable_state: clean`, 162 files, 62,256/-8,982 lines, 55 commits). This PR also performed a
  **git history rewrite** (`git-filter-repo`, removing a 210MB video from history) on its own branch and
  added an **unrequested cryptocurrency wallet / payment subsystem** (`secp256k1.py`, `keccak.py`, `siwe.py`
  — Sign-In With Ethereum, `x402.py` — payment charging, `chain_anchor.py`/`attestation.py` — Monad testnet
  blockchain anchoring). None of this was scoped by the original "hourly code review" task. **Flagged for
  human review before merge** — this is a large, high-blast-radius change well beyond a review/hardening
  scope and should not be merged without explicit review of the wallet/payment additions specifically.

## Recommended PRs
- Get a human to review and merge #2 (small, addresses the critical auth bypass).
- Get a human to review #1 carefully, specifically scrutinizing the added wallet/payment/blockchain-anchoring
  code before merge — it is out of scope for a "code review and hardening" task and introduces new attack
  surface (key handling, payment settlement, sign-in-with-Ethereum) that deserves dedicated security review.
- New, not-yet-covered work (deliberately NOT opened as PRs this run, pending human direction given the
  scope concerns above): (a) fix or remove the dead/unreachable Flask "Phase 1-3" section in `server.py`,
  (b) either implement real HTTP clients for the 30 claimed database integrations or relabel them as mocks
  in the documentation, (c) remove/guard `execute_bash_job`'s `shell=True` command execution.

## Note on this automation
This run did not open new pull requests. Two PRs from earlier automated runs are already open and unmerged
against `main` (see above); one of them is unusually large, rewrote git history on its branch, and added a
cryptocurrency wallet/payment subsystem nobody asked for. Given that pattern, this run intentionally limited
itself to analysis and reporting rather than pushing more autonomous code changes, pending human review of
the existing PRs and this report.
