# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-12 (automated run)

## Headline Finding: the backlog, not new bugs, is the critical issue

This review found that the automated review process itself has broken down. There are **16 open
PRs** against `main`, most never merged, including at least one confirmed duplicate pair:

- **#7** `fix/bigquery-unauth-raw-sql` (opened ~2026-10-05) and **#18**
  `fix/bigquery-unauth-sql-20261012` (opened today) both fix the *same* vulnerability —
  unauthenticated arbitrary SQL execution on `POST /api/bigquery`. Neither is merged.
- Verified directly against current `main` (`a25a5ac`): `server/server.py` routes `/api/bigquery`
  to `run_bigquery()` **before** any bearer-token check, and `run_bigquery` (server/server.py:373-390)
  executes `body["sql"]` verbatim via `client.query(sql, ...)` with no auth, no allowlist, no
  parameterization when `preset` is absent. **The vulnerability is still live on `main` right now**,
  a week after it was first flagged and fixed in a PR.
- Several other hourly-review PRs (#2, #3, #4, #5, #6, #8, #9, #10, #11) are similarly stale —
  opened against commits `main` has since moved past (`main` was force-updated from `806b113` to
  `a25a5ac` at some point, which likely contributed to PRs silently falling behind).
- One of those stale PRs, **#11**, is literally titled "unmerged PR backlog is leaving critical
  fixes unapplied on main" — a previous run of this same job already raised this exact alarm, and
  it was not acted on.
- Spot check: the hardcoded-JWT-secret issue PR **#5** claims to fix is *no longer present* on
  `main` (`server/auth.py` already derives the signing key from `$JWT_SECRET` with a random
  per-process fallback), so that PR is likely obsolete and safe to close — but closing other
  people's/other runs' PRs is outside what this run should do unilaterally.

**No new PR was opened this run for the bigquery issue** — #18 already covers it and is current
against `main`; opening a third PR would add to the duplication problem rather than fix it.

## Phase Status
Not re-audited line-by-line this run; prior runs (see PRs #2-#11) already covered Phases 0-5
implementation gaps. Given the backlog above, re-running that analysis before the existing findings
are triaged would only add more unmerged, unreviewed output.

## Compliance Score
**Not newly scored.** The one confirmed live issue is severe: unauthenticated arbitrary SQL
execution is a critical data-exposure / injection risk (CWE-89 / CWE-306). Until #18 (or an
equivalent) is merged, treat compliance as failing on this control regardless of any numeric score.

## Database Integration
Not re-verified this run — see above re: avoiding duplicate analysis work.

## Enterprise Hardening
Not re-verified this run.

## Top Issues (Priority Order)
1. **Critical — live now**: unauthenticated arbitrary SQL execution on `/api/bigquery`
   (server/server.py:373-390, routed at line 908-911, ahead of the auth-required branch at line 944).
   Fix already drafted in PR #18 and PR #7 (duplicates) — pick one, merge it, close the other.
2. **High — process**: 16 open PRs, most stale against current `main`, including duplicate security
   fixes. This is actively undermining the value of hourly automated review: findings are being
   re-discovered instead of fixed. Needs a human pass to merge/close/rebase the backlog before
   further automated runs add more unreviewed PRs on top.
3. **Medium**: `main` was force-updated (history rewritten) between `806b113` and `a25a5ac`, which
   is why several PRs now show a base sha that no longer exists in `main`'s ancestry. Worth
   confirming this was intentional.

## Recommended PRs
- None opened this run. Recommended human/maintainer action instead:
  - Merge PR #18 (or #7) to close the live `/api/bigquery` auth gap, then close the other as duplicate.
  - Triage and close/rebase the remaining stale hourly-review PRs (#2, #3, #4, #6, #8, #9, #10, #11)
    — several may already be obsolete (e.g. #5, see above) now that `main` has moved on.
  - Consider pausing new hourly-review PR creation until the existing backlog is cleared, so the
    job stops duplicating work.
