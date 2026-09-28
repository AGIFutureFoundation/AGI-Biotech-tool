# biodao.blockchain Hourly Review Report

## Timestamp
2026-09-28 09:49 UTC

## Scope note
This is a confirmation pass, not a fresh deep review. `main` (HEAD `806b113`,
"Phase 9 Extended") has not moved since the previous hourly report
(`hourly-review-2026-09-28-0653`, 06:53 UTC, on branch
`hourly-review-2026-09-28-0653`). That report's findings were re-verified
against the current repo state and still hold in full; see that branch for
the detailed phase-by-phase / compliance / database-integration / hardening
write-up. This report only records what changed since then and re-states the
recommendation.

## What changed since the last run (06:53 → 09:49 UTC)
- `main`: **no change** (`806b113`, same HEAD).
- PR #1 (`enterprise-hardening-and-ingestion`): gained **one** commit since the
  last report ("Re-ask ClinicalTrials.gov whether the cited trials still say
  what we claim", landed 08:26 UTC), then went idle. Still open, still
  `mergeable_state: clean`, still zero CI checks configured on the repo
  (`get_status` returns 0 statuses), still only the one bot comment
  (`tenki-reviewer[bot]`) that explicitly reviewed no diff.
- No new PRs, no new issues, no other branch activity.

## Standing critical findings (unchanged, still on `main`)
1. **Auth bypass** — `auth.authenticate_user()` never checks the password;
   any known email logs in as that user, any role, including admin.
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

All seven are already addressed on PR #1's branch (verified by the previous
run reading `auth.py`, `health.py`, etc. on that branch directly), which is
exactly why this run is not opening a competing PR.

## Recommendation (repeated from last run — still stands)
**PR #1 needs a human review before merge.** It is not a normal-sized PR to
wave through on bot approval:
- 162 files changed, +62,256/-8,982, 55 commits.
- Performed a `git-filter-repo` history rewrite on its own branch to remove a
  210MB video (confirmed again this run: `origin/main` is unaffected, still
  `806b113` — the rewrite did not touch the shared branch).
- Adds a wallet/payment/blockchain surface that was **not requested by any
  user-facing task**: hand-rolled `secp256k1.py`/`keccak.py`, SIWE sign-in,
  an `x402.py` payment-charging module, and Monad chain-anchoring
  (`chain_anchor.py`, `attestation.py`). Described as opt-in/off-by-default
  with no server-held keys, but hand-rolled crypto and payment-charging code
  is exactly the kind of scope expansion that should get a security-focused
  human read, not a second bot pass, before it ships — regardless of test
  coverage.
- No CI is wired up on this repository at all, so every "tests pass" claim in
  the PR body is self-reported.

**This run is taking no further automated action on PR #1 or `main`** beyond
recording this confirmation, for the same reason as the last run: opening a
second PR would duplicate already-completed work, and merging or further
expanding a 62k-line, crypto-touching PR without a human decision is outside
what an hourly bot should do unilaterally.

## Outstanding gap not yet covered by PR #1
- 13 of the ~29 registered databases still have no implementation anywhere in
  either codepath: PubMed, ArXiv, GenBank, dbSNP, GEO, BioGRID, Gene Ontology,
  CrossRef, Google Scholar, SureChEMBL, GTEx, ClinVar, RefSeq.
