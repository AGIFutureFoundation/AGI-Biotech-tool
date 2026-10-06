# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-06T10:48 UTC

## Phase Status
- Phase 0-9: Present in `server/*.py` (auth, projects, AR/VR, orchestration, hardening,
  scaling, molecular research pipeline). No missing files vs. the phase plan.
- Hardening modules exist as named: `error_recovery.py`, `workflow_persistence.py`,
  `monitoring.py`, `load_testing.py`, `database_migration.py`, `scaling_infrastructure.py`.

## Compliance Score
35/100 — **Critical security issues confirmed still live on `main`**, despite fix PRs
already open for them:

- `server/auth.py:authenticate_user()` performs **no password check at all** — it looks
  up the user by email and issues a valid token regardless of the `password` argument.
  Any known/guessable email fully authenticates. Fix already proposed in PR #2 / #8 / #10
  but none are merged.
- `server/server.py:run_bigquery()` (`POST /api/bigquery`) executes attacker-supplied
  `body["sql"]` verbatim against BigQuery with **no authentication on the route and no
  query allowlisting** when `preset` is omitted — unauthenticated arbitrary SQL execution.
  Fix already proposed in PR #7, not merged.

## Database Integration
Pass (structurally) — connectors for the named sources (ClinicalTrials.gov, Europe PMC,
STRING, Reactome, InterPro, Protein Atlas, UniChem, PDBe, gnomAD, AlphaFold/BigQuery, etc.)
are present in `biotech_database_integration.py` / `biotech_molecular_integration.py`.
Not independently re-verified this run (no network calls made) — prior runs' findings
(e.g. PR #4: some results were fabricated/synthetic rather than real API responses)
should be treated as still open until confirmed fixed and merged.

## Enterprise Hardening
Pass (structurally) — `error_recovery.py`, `workflow_persistence.py`, `monitoring.py`,
`load_testing.py` all exist with the expected retry/checkpoint/metrics/concurrency
patterns per prior reviews. Not re-audited line-by-line this run; see PR #1 and PR #9
for the most recent detailed hardening findings.

## Top Issues (Priority Order)
1. **Process/backlog failure, not a code gap**: this hourly routine has now opened
   **10 PRs since 2026-09-28, and none have been merged or closed**. Several contain
   critical, independently-confirmed security fixes (unauthenticated arbitrary SQL
   execution, full auth bypass, hardcoded JWT secret) that are sitting unapplied on
   `main` right now. Running this review hourly without anyone merging the output means
   the vulnerabilities it finds stay exploitable indefinitely and the PR queue keeps
   growing. **This is the top priority item** — merging the backlog matters more than
   finding new issues.
2. Auth bypass live on `main` (`server/auth.py`) — see PR #2, #8, #10 (possible overlap
   between these three; worth consolidating into one before merge).
3. Unauthenticated arbitrary SQL execution live on `main` (`server/server.py` `/api/bigquery`)
   — see PR #7.
4. Hardcoded JWT secret fallback — see PR #5.
5. Fabricated/synthetic data returned as if it were real database results (research
   integrity issue, serious for a scientific tool) — see PR #4.

## Recommended PRs
- No new PR opened this run for the auth bypass or SQL-execution issues — both already
  have open, unmerged fixes (PR #10/#8/#2 and PR #7 respectively). Opening another would
  just add to the backlog; review and merge the existing ones instead.
- Recommend: pick one of PR #2/#8/#10 (they likely overlap) as canonical, close the
  others with a pointer to it, then merge.
- Recommend: set up branch protection / required review so merged-but-unreviewed security
  fixes don't continue to pile up as open PRs.
