# biodao.blockchain Hourly Review Report

## Timestamp
2026-09-28 17:47 UTC

## Scope note
This is a confirmation pass, not a fresh deep review. `main` (HEAD `806b113`,
"Phase 9 Extended") has not moved since the previous hourly reports
(`hourly-review-2026-09-28-0653` at 06:53 UTC and `hourly-review-2026-09-28-0949`
at 09:49 UTC). Those reports' phase-by-phase / compliance / database-integration
/ hardening findings were re-verified against the current repo state and still
hold in full; see `hourly-review-2026-09-28-0653` for the detailed write-up.
This report only records what changed since 09:49 and re-states the
recommendation, which is now more urgent given the elapsed idle time below.

## What changed since the last run (09:49 -> 17:47 UTC)
- `main`: **no change** (`806b113`, same HEAD).
- PR #1 (`enterprise-hardening-and-ingestion`, 162 files, +62,256/-8,982, 55
  commits): **no new commits** since `558f060` (08:26 UTC). Still open,
  `mergeable_state: clean`, CI green (`make verify` and `node --check js/`
  both passing), bot-reviewed with no issues found. **Idle 9h20m** with no
  human action.
- PR #2 (`fix/auth-password-verification`, the scoped auth-bypass fix opened
  after the 09:49 report): created 13:51 UTC, review bot flagged 2
  high/1 medium findings (re-registration overwriting a password hash,
  self-assignable `admin` role on register, 500 on missing email), all three
  fixed in `7b1006f` and confirmed resolved on their threads by 13:55 UTC.
  No CI pipeline is configured on this repo beyond the review bot;
  `mergeable_state: clean`. **Idle 3h52m** with no human action since being
  marked ready.
- No new PRs opened, no new critical issues found, no other branch activity.

## Standing critical findings (unchanged, still live on `main`)
1. **Auth bypass** — `auth.authenticate_user()` never checks the password on
   `main`; any known email logs in as that user, any role, including admin.
   Fix is ready and waiting in PR #2.
2. **Hardcoded JWT fallback secret** (`dev-secret-change-in-production`) —
   forgeable tokens if the env var is unset.
3. **IDOR/RBAC decorative** — `can_access_project()` and `require_role` exist
   but are never called from any route.
4. **"Science" outputs are simulated** — docking/MD/ADMET/gesture-voice
   results in several modules are `random.*`/hardcoded, not computed, behind
   authoritative-looking docstrings. Scientific-integrity risk given this
   tool's stated purpose (real drug-discovery decisions).
5. **Database integration layer is 100% mocked** — `biotech_database_integration.py`
   / `biotech_molecular_integration.py` return hardcoded results for all ~29
   registered databases; the only genuinely working integration (9 real APIs:
   ClinicalTrials.gov, Europe PMC, STRING, Reactome, InterPro, Protein Atlas,
   UniChem, PDBe, gnomAD) lives in an unrelated code path (`server.py`'s proxy
   + `js/api.js`), not in the files that claim to own this responsibility.
6. **Phase 1 Flask block in `server.py` is dead/broken code** — `app` is
   never defined; would raise `NameError` if actually imported/reached.
7. **Phase 4 hardening modules are orphaned** — `error_recovery.py`,
   `workflow_persistence.py`, `monitoring.py` are real, working
   implementations, but nothing in `server.py` calls them. Zero runtime
   protection today despite existing.

Findings 1-7 are all addressed on PR #1's branch; finding 1 alone (the
in-production-exploitable one) also has the smaller, independently
reviewable PR #2.

## Compliance score
55/100 — real security work exists and is sitting in review (not a code
quality problem), but `main` itself still has an unauthenticated-login bypass
live in a public repo, which caps this score regardless of what's queued.

## Database integration audit
Fail, unchanged. 9/29 registered sources have working live calls
(ClinicalTrials.gov, Europe PMC, STRING, Reactome, InterPro, Protein Atlas,
UniChem, PDBe, gnomAD) via `server.py`/`js/api.js`; the two modules whose job
title is "database integration" mock all ~29. 13 registered databases
(PubMed, ArXiv, GenBank, dbSNP, GEO, BioGRID, Gene Ontology, CrossRef, Google
Scholar, SureChEMBL, GTEx, ClinVar, RefSeq) have no implementation in either
code path. Not addressed by PR #1.

## Enterprise hardening
Fail on `main`, addressed on PR #1. `error_recovery.py`, `workflow_persistence.py`,
`monitoring.py`, `load_testing.py` are real implementations but orphaned —
nothing in `server.py` wires them into the request path. PR #1 adds a test
suite (1,262 tests), import/reachability/egress gates, and fixes several
silent-failure bugs across these modules.

## Top issues (priority order)
1. **Merge or reject PR #2.** A working, reviewed, CI-green fix for a live
   auth bypass has been sitting for ~4 hours. This is the single highest-
   leverage action available right now.
2. **Give PR #1 a human security read.** 62k-line diff, hand-rolled
   secp256k1/keccak/SIWE/x402 payment code, and a `git-filter-repo` history
   rewrite on its own branch — too large and sensitive for another automated
   pass to wave through, and it's been idle for over 9 hours.
3. Wire the orphaned Phase 4 hardening modules into `server.py` (covered by
   PR #1, but flagging in case PR #1 is rejected/deferred and this should be
   cherry-picked separately).
4. Close the 13-database integration gap once the mocked layer is either
   replaced or explicitly relabeled as demo/simulated data.

## Recommended PRs
- No new PR opened this run. Opening a third PR would duplicate already-
  completed work (PR #1 covers findings 1-7; PR #2 covers finding 1 alone).
  The remaining recommended action is human review and merge/reject of the
  two existing PRs, not more automated changes.

## Standing recommendation
Unchanged from the last two runs, and now more urgent: **a human needs to
look at PR #2 (small, fast to review) and PR #1 (large, needs a real security
read) today.** This run took no further automated action on `main` or either
PR beyond recording this confirmation.
