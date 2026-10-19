# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-19 (automated run)

## Top Finding: this job is spamming duplicate PRs instead of landing fixes

This recurring hourly-review job has opened 12 PRs against `main` since 2026-09-28 (see
`#2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #18, #19`). Most are still open and in **draft**
state — i.e. never completed or merged. Several duplicate each other:

- `/api/bigquery` unauthenticated arbitrary-SQL execution was proposed as a fix **twice**
  (#7 on 2026-10-05, #18 on 2026-10-12) — both still open, unmerged, and duplicates of
  each other.
- The login/registration auth-bypass fix was proposed **three times** (#2, #8, #10)
  across two weeks.
- PR #19, opened by this same job on 2026-10-12, already identified this exact problem
  and explicitly recommended "pausing new hourly-review fix PRs until the backlog
  clears, so this job stops rediscovering and duplicating work that's already been
  proposed." That recommendation was not acted on, and this run would otherwise have
  produced a 13th duplicate.

**This run is not opening a new PR.** Opening another one would add to the backlog
rather than fix anything. The backlog itself — 12 open PRs, several draft/unmerged,
some duplicating each other — needs a human to triage: pick the best fix for each
issue, merge it, and close the superseded duplicates. Until that happens, this job
will keep rediscovering the same bugs every run.

## Confirmed still-live on `main` right now

- **`/api/bigquery` executes unauthenticated, caller-supplied SQL.** In
  `server/server.py`, the `POST /api/bigquery` route (~line 910) calls `run_bigquery`
  directly with no auth check — unlike other routes in the file, which call the
  `@require_auth`-equivalent JWT check at line ~589. `run_bigquery` (~line 373) runs
  `body["sql"]` verbatim via `client.query(sql, ...)` when no `preset` is given, so any
  caller can execute arbitrary SQL against the project's BigQuery billing/data. Fixes
  already proposed in #7 and #18 — unmerged.
- Login does appear to call `verify_password` (`server/auth.py:150,198`), so the
  "no-op password auth" issue raised in #8 may already be addressed on `main` —
  recommend closing #8 if confirmed fixed, rather than leaving it open as a stale
  duplicate.

## Phase Status
Not re-audited this run — superseded by the finding above. Phase-by-phase review is
low value while known, already-diagnosed critical findings sit unmerged.

## Compliance Score
Not scored this run.

## Database Integration
Not re-audited this run.

## Enterprise Hardening
Not re-audited this run.

## Top Issues (Priority Order)
1. **Process**: 12 open agent-authored PRs, mostly draft/unmerged, with confirmed
   duplicates — needs human triage (merge best fix per issue, close the rest).
2. **Critical/live**: unauthenticated arbitrary SQL execution via `/api/bigquery` on
   `main` — fix already proposed in #7/#18, just needs review and merge.
3. Confirm whether #8 (no-op password auth) is actually fixed on `main` already, and
   close it if so.

## Recommended PRs
- None opened this run — see "Top Finding" above.
- Recommended next step is **pausing this hourly job** (or switching it to
  report-only) until a human clears the existing PR backlog, per #19's own
  recommendation.
