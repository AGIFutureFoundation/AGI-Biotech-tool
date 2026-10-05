# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-05 (automated hourly review run)

## ⚠️ Standing backlog — read this first
8 pull requests from prior automated hourly runs are **open and unmerged**, several since
2026-09-28 (a week ago). Three of them fix *currently live* security vulnerabilities in `main`:

| PR | Opened | Fixes |
|----|--------|-------|
| #2 | 09-28 | Auth bypass — any password is accepted for any known email |
| #3 | 09-28 | Dead Flask route block in `server.py` (never executes) |
| #5 | 09-29 | Hardcoded JWT secret fallback |
| #4 | 09-29 | Fabricated/mock "database" results presented as real |
| #7 | 10-05 | Unauthenticated arbitrary-SQL execution on `/api/bigquery` |
| #8 | 10-05 | No-op password auth + fabricated partnership/readiness claims |
| #6 | 10-05 | Report-only backlog triage |
| #1 | 09-28 | Enterprise hardening test suite |

**None of these have been merged.** Every hourly run since 09-28 has re-confirmed the same
unfixed auth bypass and hardcoded secret because nobody has reviewed/merged the existing PRs.
This run does not open new PRs for already-covered issues (see "Recommended actions").

## Phase Status
- **Phase 1** (auth, projects, disease panels, reporting, agents): implemented but **not
  reachable** — see Phase 3 finding below. Also: `auth.py` never checks passwords (PR #2
  covers this); `disease_panels.py:152-154` sorts prevalence as raw strings, producing a
  meaningless ranking; `agents.py` optimization/analysis agents return hardcoded fake
  results regardless of input.
- **Phase 2** (AR/VR + master agent voice control): `master_agent.py:140-141` calls
  `_handle_paper_request(entities)` on a base class whose method takes no `entities` arg →
  `TypeError` on any "generate paper" voice command; `agent_orchestrator.py` executor is
  entirely simulated (`asyncio.sleep` + hardcoded `mock: True` results).
- **Phase 3** (orchestrator/streaming wiring) — **most severe code-quality finding this
  run**: `server/server.py` lines 501-1086 (all Flask routes for auth/projects/reporting/
  workflows/master-agent) reference `app`, `request`, `jsonify`, `g` — **Flask is never
  imported anywhere in the file and isn't in requirements.txt**. This code sits after the
  real entry point (`srv.serve_forever()` at line ~491, which blocks forever), so it is
  dead code that never executes when the server is run normally. Already tracked in open
  PR #3 ("fix dead Flask app in server.py"), unmerged for a week.
- **Phase 4** (hardening): genuinely solid. `error_recovery.py`'s retry/circuit-breaker
  logic is real, `workflow_persistence.py` checkpoint/resume actually round-trips state,
  `monitoring.py` collects real metrics. Caveat: `retry_with_backoff` is defined but never
  called anywhere in the codebase — dead code, not wired into the one real network path
  (`server.py`'s `proxy_get`).
- **Phase 5** (scaling/load testing/migration/ML): `load_testing.py`'s stress-test harness
  (concurrency, p95/p99) is real but exercises a fake `asyncio.sleep` workload, not the
  actual server/DB stack. `ml_enhanced_recognition.py`'s gesture model is `random.choice`
  dressed up as "ensemble accuracy 0.94". **Fixed this run**: `database_migration.py` used
  MySQL-only inline `INDEX` syntax inside `CREATE TABLE`, which would raise a syntax error
  against real PostgreSQL, and lacked transaction isolation between migrated rows;
  `scaling_infrastructure.py`'s `DistributedCache` never actually enforced TTL expiry and
  evicted the lexicographically-smallest key instead of the oldest-inserted one.

## Compliance Score
**25/100** — Critical, currently-live issues (tracked in open PRs, not yet merged):
- Authentication bypass: `auth.py:111-121` ignores the password argument entirely (PR #2).
- Hardcoded JWT secret fallback: `auth.py:17` (PR #5).
- Unauthenticated arbitrary SQL on `/api/bigquery` (PR #7).
- Flask `debug=True` in three `app.run()` calls in `server.py` (lines ~720, 848, 1086) —
  exposes the Werkzeug interactive debugger (RCE risk) and leaks stack traces to clients.
  Sits inside the same dead-code block as PR #3; **not yet in any open PR** — should be
  fixed as part of resolving #3, not a separate PR.
- No audit-trail logging anywhere: sensitive mutating routes (`POST /api/projects`,
  `/api/reports/*/generate`, `/api/workflows/execute`) log nothing with user identity —
  only unstructured `print()` statements. Not yet tracked in an open PR; recommend a
  follow-up PR adding structured `user_id + action + timestamp` logging.
- No hardcoded credentials found in source (checked).

## Database Integration
**FAIL** — Of the ~30 "integrated" databases claimed in `biotech_database_integration.py`
and `biotech_molecular_integration.py` (STRING, Reactome, ClinicalTrials.gov, UniChem, PDBe,
gnomAD, etc.), **none have real HTTP client code in those two files** — `connect_database()`
and `query_database()` return hardcoded fake results (comment: "Simulate query execution").
Worse: `biotech_molecular_integration.py`'s `BiotechDatabaseFederator` returns the same
hardcoded aspirin SMILES / PDB id `4O1J` for every query, and this fabricated output is fed
into the live research pipeline via `team_agent_orchestration.py` as if it were real
database enrichment — already tracked in open PR #4.

The only genuine network integration is a generic CORS-bypass proxy in `server.py`
(`proxy_get`, allowlisted hosts for ebi.ac.uk, europepmc.org, string-db.org, etc.) — this
part is real, has reasonable timeouts, and has SSRF protection via host allowlisting, but
has no retry logic (dead `retry_with_backoff` exists but is never called) and uses a
blanket `except Exception` with no differentiation between timeout/4xx/5xx/DNS failure.

## Enterprise Hardening
**PASS with gaps** — `error_recovery.py` (retry+backoff, circuit breaker) and
`workflow_persistence.py` (checkpoint/resume) are real, working implementations, not stubs.
Gaps: `retry_with_backoff` is never actually called anywhere; persistence methods swallow
exceptions via `print()` + falsy return with no re-raise, so callers can silently lose
checkpoints; `monitoring.py` collects real metrics but exposes no HTTP health-check route;
`load_testing.py`'s load simulation doesn't exercise the real server/DB/websocket stack.

## Top Issues (Priority Order)
1. **8 open PRs unmerged for up to a week**, three fixing live security vulnerabilities
   (auth bypass, hardcoded JWT secret, unauthenticated SQL execution). This is the
   single highest-priority item — merge/review the backlog before anything else.
2. Flask `debug=True` in `server.py`'s `app.run()` calls — RCE/stack-trace exposure risk,
   not yet in any open PR (fold into PR #3's fix).
3. Fabricated per-query "database enrichment" data is fed into the live research pipeline
   as if real (tracked in PR #4, unmerged).
4. No audit-trail logging of sensitive actions (new finding, no PR yet).
5. `retry_with_backoff` / circuit breaker exist but are never wired into the one real
   network path in the app.

## Fixed This Run
- `server/database_migration.py`: removed invalid MySQL-style inline `INDEX` clauses from
  `CREATE TABLE` statements (would have raised a syntax error against real PostgreSQL);
  moved index creation to separate `CREATE INDEX IF NOT EXISTS` statements; switched the
  migration connection to `autocommit=True` so one bad row no longer poisons every
  subsequent insert in the same transaction.
- `server/scaling_infrastructure.py`: `DistributedCache.set()` now actually computes
  `expires_at` as `now + ttl_seconds` (was previously just `now`, making every entry
  immediately "expired" with no code ever checking it); `get()` now enforces that expiry;
  eviction now removes the true oldest-inserted key (dict insertion order) instead of the
  lexicographically smallest key name.
- Verified both fixes with an ad-hoc test (TTL expiry, oldest-key eviction, 10k-entry cap).

## Recommended Actions (no new PRs opened for these — already covered)
- Review and merge/close the 8 existing open PRs, starting with #2, #5, #7 (live security
  fixes) and #3 (dead Flask block, which also houses the `debug=True` issue above).
- Once PR #3 lands and the Flask block becomes real/reachable code again, re-review
  Phase 1-3 bugs found this run (`master_agent.py` entity-handling bugs,
  `agent_orchestrator.py`'s fully-simulated executor) since they were previously unreachable
  dead code and may now matter.
