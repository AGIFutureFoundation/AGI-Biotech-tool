# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-05 (automated hourly run)

## Summary
This run found no new critical/high issue that isn't already covered by an
open PR from a prior hourly run. No new PR was opened. The more pressing
finding from this run is procedural, not code: **the hourly cadence is
producing PRs faster than anyone is merging them**, and one of the existing
open PRs took on scope well beyond a review fix. Both are flagged below and
reported to the user directly.

## Phase Status
- Phase 0 (Auth): `server/auth.py` — password-bypass bug fixed, unmerged (PR #2, 7 days open).
- Phase 1 (Projects/reporting): no new issues found this run.
- Phase 2 (AR/VR, Master Agent voice): not re-audited this run (no code changes since last pass).
- Phase 3 (Orchestrator/server wiring): `server/server.py` dead-Flask-app (`NameError` at import) fixed, unmerged (PR #3, 7 days open).
- Phase 4-5 (Hardening/scaling): `error_recovery.py`, `workflow_persistence.py`, `monitoring.py`, `load_testing.py` exist and implement retry/circuit-breaker, checkpointing, basic metrics, and concurrent load simulation respectively — but per PR #1's own findings, several of these modules are not actually wired into the live request path (constructed but not consistently called from `server.py`). PR #1 proposes a much larger hardening pass; still open, unmerged.
- Phase 9 (Molecular/biotech database integration): confirmed via PR #4 — `BiotechDatabaseFederator` / `MCP_ServerManager` return fabricated data for all 29 "integrated" databases (ChEMBL, PubChem, UniProt, PDB, ClinicalTrials.gov, Europe PMC, STRING, Reactome, InterPro, Protein Atlas, UniChem, PDBe, gnomAD, etc.) with no real network calls anywhere in the codebase. PR #4 adds `synthetic: true` markers to the payloads; it does not add real connectivity (out of scope for a single fix). Unmerged.

## Compliance Score
45/100 — security and research-integrity bugs are identified and fixed in open PRs, but **none have been merged**, so the code on `main` today still has: a JWT secret that falls back to a public hardcoded string, an auth function that never checks passwords, a server entrypoint that fails to import, and biotech database results presented as real when they are 100% fabricated.

## Database Integration
**Fail** — 0 of the 10+ named external databases (ClinicalTrials.gov, Europe PMC, STRING, Reactome, InterPro, Protein Atlas, UniChem, PDBe, gnomAD, etc.) make a real network call. All results are hardcoded mock data returned regardless of query. See PR #4 for the synthetic-marker fix; real connectivity remains unimplemented.

## Enterprise Hardening
**Fail** — `error_recovery.py` (retry/circuit breaker) and `workflow_persistence.py` (checkpoint/resume) are implemented as standalone classes but, per PR #1's audit, are not consistently invoked from the live Flask routes in `server.py`. `monitoring.py` and `load_testing.py` exist but have no scheduled/automatic invocation (nothing calls them outside manual scripts).

## Top Issues (Priority Order)
1. **Process issue, not code**: 5 open PRs have accumulated from repeated hourly runs over the past 7 days (#1 created 2026-09-28, #5 most recent 2026-09-29) with zero merges. The hourly schedule is generating review output faster than it's being consumed — recommend a human triage/merge pass, or reducing the review cadence, before another run adds a 6th.
2. **Needs human review before merge**: PR #1 ("Enterprise hardening") grew from a documentation-only review into a 172-file, 63,000+ line changeset that added an unrequested crypto-wallet/payment subsystem (`secp256k1.py`, `keccak.py`, `siwe.py`, `x402.py`, `agent_facts.py`) and rewrote the git history of its own branch with `git-filter-repo` to drop a 210MB video file. Confirmed `origin/main` itself is untouched (still at `806b113`, unaffected by the rewrite). This PR's scope is well beyond "fix what the review found" and should get explicit human sign-off, not an automated merge.
3. Auth bypass (PR #2), hardcoded JWT secret (PR #5), dead Flask app (PR #3), and fabricated-as-real database results (PR #4) are all real, already fixed in open PRs, and still unmerged on `main`.

## Recommended PRs
- None opened this run — all currently-known critical/high issues already have an open, unmerged fix PR (#2, #3, #4, #5). Opening a 6th would add to the backlog described in issue #1 above rather than resolve anything.
- Recommend: merge #2, #3, #4, #5 (narrowly-scoped security/correctness fixes) soon; give #1 dedicated human review given its scope before any merge decision.
