# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-05, later run (automated hourly review)

## Summary
This run found no new critical/high issue beyond what's already covered by an open
PR from a prior run, except for one: PR #7 (unauthenticated arbitrary-SQL execution
on `/api/bigquery`), filed by the immediately preceding hourly run, which is new
since the last version of this report. No new PR was opened this run. The standing
procedural finding is now worse, not better: **7 open PRs, 0 merges, 8 days**, and
the backlog grew by two (#6, #7) since the last check rather than shrinking.

## Phase Status
- Phase 0 (Auth): `server/auth.py` — password-bypass bug fixed, unmerged (PR #2, 8 days open). JWT hardcoded-secret fallback fixed, unmerged (PR #5, 7 days open).
- Phase 1 (Projects/reporting): no new issues found this run.
- Phase 2 (AR/VR, Master Agent voice): not re-audited this run (no code changes since last pass).
- Phase 3 (Orchestrator/server wiring): dead-Flask-app import bug fixed, unmerged (PR #3, 8 days open). **New this run:** `/api/bigquery` on the live stdlib-`http.server` handler (the path actually used by the frontend, per `js/api.js`) accepted caller-supplied raw SQL with no authentication when no `preset` was given — unauthenticated arbitrary SQL execution / cost-abuse against the operator's GCP project. Fixed narrowly (allowlist-only presets), unmerged, draft (PR #7, filed today).
- Phase 4-5 (Hardening/scaling): `error_recovery.py`, `workflow_persistence.py`, `monitoring.py`, `load_testing.py` exist but, per PR #1's audit, are not consistently wired into the live request path in `server.py`. PR #1's larger hardening pass remains open and unmerged.
- Phase 9 (Molecular/biotech database integration): confirmed via PR #4 — all ~29 "integrated" databases (ClinicalTrials.gov, Europe PMC, STRING, Reactome, InterPro, Protein Atlas, UniChem, PDBe, gnomAD, etc.) return fabricated data; no real network calls exist anywhere in the codebase for this layer. PR #4 adds `synthetic: true` markers; real connectivity is still unimplemented. Unmerged.

## Compliance Score
40/100 — one more live, unauthenticated vulnerability (arbitrary SQL execution) was found and fixed since the last report, but the backlog of unmerged fixes grew instead of shrinking. `main` today still has: a forgeable JWT admin token (public hardcoded fallback secret), a login path that never checks passwords, a server entrypoint that fails to import, fabricated database results presented as real, and now a confirmed unauthenticated SQL-execution endpoint — all with fixes sitting open and unreviewed.

## Database Integration
**Fail** — unchanged from last run. 0 of the 10+ named external databases make a real network call; all results are hardcoded. See PR #4.

## Enterprise Hardening
**Fail** — unchanged from last run. Resilience modules exist as standalone classes but are not consistently invoked from live routes.

## Top Issues (Priority Order)
1. **Process issue, not code, and getting worse**: 7 open PRs (#1-#7), 0 merges, 8 days since #1 was opened. Two more PRs (#6 report-only, #7 a real live fix) were added since the last check with still nothing merged. Recommend a human triage/merge pass now, or pausing the hourly cadence until the existing backlog is cleared — repeated in the last two reports (see PR #6).
2. **Needs dedicated human review before merge**: PR #1 added an unrequested crypto-wallet/payment subsystem (`secp256k1.py`, `keccak.py`, `siwe.py`, `x402.py`, `agent_facts.py`) and rewrote its own branch's git history to drop a 210MB file. `origin/main` is unaffected, but the PR's scope is well beyond "fix what the review found."
3. **Live, unauthenticated, until #7 merges**: anyone who can reach the server can run arbitrary SQL against the operator's GCP project via `/api/bigquery` with no `preset` set — billing/cost abuse and potential data exposure. Fix is filed (PR #7, draft) but unmerged.
4. Auth bypass (#2), forgeable JWT admin tokens (#5), dead Flask app (#3), and fabricated-as-real database results (#4) remain real, already fixed in open PRs, and unmerged on `main`.

## Recommended PRs
- None opened this run — the one new issue found (unauthenticated SQL execution) was already filed as PR #7 by the prior run before this one started. Opening another report-only PR would add an 8th item to a backlog three prior runs have already flagged as unconsumed.
- Recommend: merge #2, #3, #4, #5, #7 (narrowly-scoped security/correctness fixes) now; give #1 explicit human sign-off on scope before any merge decision; decide whether hourly cadence should continue generating new findings while 7 sit unreviewed.
