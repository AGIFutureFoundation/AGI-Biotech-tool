# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-12 (automated run)

## Headline finding: the PR backlog problem solved itself the wrong way

Every prior hourly-review finding in this report is secondary to this: **`main`'s git history was
force-pushed between 2026-10-06 and 2026-10-12** (old tip `806b113`, current tip `a25a5ac`; `git fetch`
reports "forced update"). None of the ten PRs opened by hourly runs since 2026-09-28 (#2–#11) share a
merge-base with the new `main` any more — `git diff origin/main...origin/<branch>` fails with
"no merge base" for every one of them. They are not just stale, they are structurally unmergeable
through GitHub's normal merge button.

PR #11 (2026-10-06) had already flagged the then-10-PR backlog and explicitly recommended merging
#2/#8/#10 (auth bypass) and #7 (BigQuery unauthenticated SQL) instead of opening more PRs. That advice
was not followed through the PR mechanism — but by the time of this run, **the auth-bypass fix had
landed on `main` anyway**, almost certainly by someone applying the fix directly and then rewriting
history, rather than by merging #2/#8/#10. The BigQuery fix did not make the same trip and the
vulnerability PR #7 described is still live on current `main`.

Net effect: two weeks of hourly-review output (10 PRs, several with real, reviewed, correct fixes) is
now orphaned. Recommend someone with push access either (a) explains/confirms the history rewrite and
closes the now-unmergeable PRs #2–#11 with a note pointing at what actually landed, or (b) if the
rewrite was unintentional, recovers the pre-rewrite `main` (`806b113`) before anything reachable only
from it is garbage-collected.

## Phase status (server/*.py)

Read through the full `server/` tree (59 files). No incomplete/stubbed phase found this run beyond
what's noted below. Auth (`auth.py`), projects (`projects.py`), orchestration
(`agent_orchestrator.py`, `team_agent_orchestration.py`, `master_agent.py`), and the hardening modules
(`error_recovery.py`, `workflow_persistence.py`, `monitoring.py`) are all present and non-trivial.
VR/AR surfaces (`websocket_streaming.py`, the headset flow in `server.py`) are implemented, matching
the README's description of the product as a VR/AR molecular workspace, not a blockchain enterprise
platform in the sense the standing review prompt assumes — the prompt's framing ("Phase 1-5",
"biodao.blockchain platform", specific hardening file names) matches this repo closely enough that no
mismatch flag is needed.

## Compliance score

**62/100.** Breakdown:
- Password auth now verifies a scrypt hash with a constant-time comparison (`auth.py:150-203`) — this
  is a **real fix already on `main`**, contradicting `SECURITY.md`'s old claim that the password
  argument is ignored. Fixed in this PR: the doc.
- `JWT_SECRET` no longer has a published fallback constant; an unset variable now generates a random
  per-process key with a `RuntimeWarning` (`auth.py:20-44`). Also already on `main`; also a stale claim
  in `SECURITY.md`, fixed in this PR.
- **Still live: `POST /api/bigquery` executes attacker-supplied raw SQL with zero authentication** when
  the request omits `preset` (`server.py`, `run_bigquery()`). Confirmed by reading current `main`
  directly, not by trusting the PR titles. **Fixed in this PR** (see below).
- Most other API routes remain unauthenticated by design (documented in `SECURITY.md`, confirmed
  still true after the fix below: only project access and the BigQuery free-form-SQL branch call
  `self._user()`). This matches the project's own stated threat model (local-first, LAN-exposed for
  headsets) and is not something this run treats as a new finding.
- Audit trail: `chain_anchor.py`, `attestation.py`, and `synthetic_provenance.py` provide on-chain
  anchoring and synthetic-data marking; `test_provenance_integrity.py` and `test_synthetic_provenance.py`
  exercise them. No gap found this run.
- FAIR-principle / data-provenance markers (`[SYNTHETIC]` tagging, `provenance` fields) are present and
  tested (`test_chain_anchor.py::test_synthetic_records_are_refused_by_default`).

## Database integration

**Pass, with one caveat.** `biotech_database_integration.py` and `db_clients.py` wire up ClinicalTrials.gov,
Europe PMC, STRING, Reactome, InterPro/UniProt-adjacent lookups, Human Protein Atlas, UniChem-adjacent
compound sourcing, PDBe/RCSB, gnomAD, and more, all routed through the fixed-allowlist proxy
(`PROXY_HOSTS` in `server.py`) that `SECURITY.md` and `scripts/check_egress.py` both enforce at build
time (`make egress`). BigQuery (AlphaFold metadata) is the one integration that accepts free-form
query input, and it is also the one with an auth gap — fixed in this PR.

## Enterprise hardening

**Pass.** `error_recovery.py` implements retry/circuit-breaker logic; `workflow_persistence.py` provides
checkpoint/resume; `monitoring.py` exposes metrics and health-check primitives; `load_testing.py` /
`scaling_infrastructure.py` cover concurrent-workflow load. No missing-feature gap found this run.
(Not re-verified line-by-line this run — unchanged since no code in these files was touched — see
prior hourly-review history if a deeper pass is wanted.)

## Top issues (priority order)

1. **Orphaned PR backlog from a `main` history rewrite** — ten PRs (#2–#11) are no longer mergeable
   through GitHub; at least one still-unapplied critical fix (BigQuery) was lost in the process.
   Needs a human decision (see "Headline finding" above).
2. **`POST /api/bigquery` unauthenticated arbitrary SQL execution** — confirmed live on `main` as of
   this run. Fixed in the PR this report ships with.
3. **`SECURITY.md` described two vulnerabilities (auth bypass, hardcoded JWT fallback) that are
   already fixed on `main`**, which is itself a compliance/documentation-accuracy issue (stale security
   disclosure actively misleads a reader). Fixed in the same PR.

## Recommended PRs

- *(This PR)* — gate `POST /api/bigquery`'s free-form SQL path behind the existing bearer-token check,
  and correct `SECURITY.md`'s now-stale auth/JWT claims.
- Separately: someone with push access should triage PRs #2–#11 — confirm what already landed via the
  history rewrite, and close or rebase the rest. No new PR was opened for this; it is not a code change,
  it is a repository-hygiene decision for a human.
- Dependabot PRs #12–#17 are open and unreviewed; routine dependency-version bumps, not reviewed in
  depth this run.
