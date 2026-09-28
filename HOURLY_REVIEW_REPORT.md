# biodao.blockchain Hourly Review Report

## Timestamp
2026-09-28 06:53 UTC

## Scope note
This review evaluates the current `main` branch (HEAD `806b113`, "Phase 9 Extended"),
which is what is actually deployed/mergeable today. It also accounts for the open
PR #1 (`enterprise-hardening-and-ingestion`), which already fixes most of the
critical findings below but is **not yet merged**. See "Open PR #1" section.

## Phase Status
- **Phase 0-1 (Flask API layer, auth/projects/reporting endpoints, `server/server.py`
  lines ~497-1086)**: **Broken, not just incomplete.** `app` (a Flask instance) is
  never created anywhere in `server.py`, yet `@app.route(...)` decorators are used
  throughout this block. Importing this module outside of `if __name__ == "__main__"`
  raises `NameError` immediately. The block only "works" today because `main()`
  (the real, working stdlib `http.server` app on lines 1-495) blocks forever in
  `srv.serve_forever()`, so this dead code is never actually reached in normal
  operation. `requirements.txt` doesn't list `flask` or `PyJWT` either, so this
  layer isn't even installable as shipped.
- **Phase 2-3 (AR/VR, master agent, orchestrator, websocket streaming)**: Real,
  working chemistry (RDKit/OpenMM-based) coexists with a chain of agent/molecular
  modules that call each other with mismatched signatures (e.g.
  `agent_orchestrator.AgentOrchestrator.__init__` requires args that `server.py`
  never passes; `websocket_streaming.StreamingServer.broadcast()` only logs, never
  sends over a socket). These would raise `TypeError`s immediately if actually
  invoked — evidence this chain has never been integration-tested end-to-end.
- **"Science" layer (docking, MD, ADMET, gesture/voice ML)**: Presented with
  professional docstrings but largely backed by `random.random()`/`random.gauss()`
  or hardcoded constants dressed as results (`molecular_research_pipeline.py`,
  `agents.py`, `ml_enhanced_recognition.py`, `active_learning.py`,
  `agent_training_system.py`, `team_agent_orchestration.py`). A reader could
  reasonably mistake this for working computation.
- **Phase 4 (error recovery, persistence, monitoring)**: The modules
  (`error_recovery.py`, `workflow_persistence.py`, `monitoring.py`) contain real,
  working logic (genuine exponential backoff, a real circuit-breaker state
  machine, real SQLite-backed checkpoint/resume, real metrics collection) — but
  **none of it is imported or called from `server.py`**. It's orphaned; only
  standalone test scripts under `scripts/` exercise it.
- **Phase 5 (load testing, scaling, DB migration)**: `load_testing.py` does real
  concurrent execution via `asyncio`, but only against `asyncio.sleep()` stand-ins,
  not the real server. `database_migration.py`'s PostgreSQL schema uses inline
  MySQL-style `INDEX idx_x (col)` clauses inside `CREATE TABLE`, which is invalid
  Postgres syntax — the migration path has never successfully run against real
  Postgres.

## Compliance Score
**14/100** on current `main`. Not a "needs polish" number — this reflects a
complete authentication bypass, not merely gaps:
- **CRITICAL** — `auth.authenticate_user()` never checks the password argument
  at all (comment admits "stub for demo purposes"); any known email logs in as
  that user, including `admin`/`pi` roles.
- **CRITICAL** — passwords are accepted at registration but never hashed or
  stored anywhere.
- **CRITICAL** — `JWT_SECRET` falls back to the hardcoded literal
  `'dev-secret-change-in-production'`, letting anyone forge tokens for any role
  if the env var is unset.
- **HIGH** — IDOR: `Permission.can_access_project()` exists but is never called
  anywhere in the codebase; any authenticated user can read any other lab's
  project data.
- **HIGH** — `require_role` (RBAC decorator) is defined but never applied to any
  route.
- **MEDIUM** — CORS wildcard (`Access-Control-Allow-Origin: *`) on every response.
- **MEDIUM** — latent shell injection surface in `agents.py`'s
  `execute_bash_job` (`subprocess.run(..., shell=True)`), currently unreferenced
  but exported.
- **LOW** — no audit-trail logging of auth events exists, despite generated
  report text claiming "a tamper-evident SHA-256 hash chain ledger" (fabricated
  boilerplate, not implemented in code).
- No hardcoded API keys/secrets found (checked all server/*.py + requirements.txt).

## Database Integration
**FAIL** (on current `main`). `biotech_database_integration.py` and
`biotech_molecular_integration.py` — the files literally named as the
integration layer — contain **zero HTTP calls** for any of the 29-30 databases
they register (ClinicalTrials.gov, STRING, Reactome, InterPro, Protein Atlas,
UniChem, PDBe, gnomAD, etc. included). `query_database()` returns hardcoded
`results_count: 42`; searches return literal mock dicts.

A separate, genuinely working integration exists but isn't wired to those
"integration" modules: `server.py`'s CORS proxy (`proxy_get`) has an SSRF-safe
allowlist of 25 real hosts with real timeouts, and `js/api.js` (frontend) builds
correctly-formed requests to ClinicalTrials.gov v2, Europe PMC, STRING, Reactome,
InterPro, Protein Atlas, UniChem, PDBe SIFTS, and gnomAD GraphQL — all 9 of the
databases named in this review's own template are in fact live via that path,
just not through the Python files that claim to own the integration. No
retry/backoff on 429/5xx exists anywhere. `database_migration.py` has one
f-string table-name interpolation (currently fed only from a hardcoded list, so
not exploitable today, but injection-shaped).

## Enterprise Hardening
**FAIL — orphaned, not "missing."** `error_recovery.py` (retry + circuit
breaker), `workflow_persistence.py` (SQLite checkpoint/resume),
`monitoring.py` (metrics + health check), and `load_testing.py` (real
`asyncio`-based concurrency) are all real, working implementations — but none
is imported by `server.py`. They provide zero protection today. Additional
gaps: `HealthCheck` has no checks registered anywhere, so any health endpoint
built on it reports "healthy" unconditionally; the circuit breaker records
failures but `retry_with_backoff` never consults `is_available()` before
calling, so it can't actually stop cascading failures.

## Top Issues (Priority Order)
1. **Auth bypass on `main`**: any known email + any password (including empty)
   returns a valid token with that user's real role. This is the single most
   urgent item if this server is ever exposed beyond localhost.
2. **Phase 1-3 Flask API block in `server.py` is not executable code** — `app`
   is undefined. Needs a decision: finish wiring it (add Flask/PyJWT to
   requirements, define `app`, fix the import-style inconsistencies and
   duplicate `if __name__` blocks), or delete it. Leaving it as-is misrepresents
   what the deployed server can actually do.
3. **IDOR / RBAC are decorative** — access-control functions exist and are
   never called.
4. **"Science" outputs (docking scores, MD trajectories, ADMET, gesture/voice
   recognition) are largely `random.*` or hardcoded values behind authoritative
   docstrings.** This is a scientific-integrity risk, not just a code-quality
   one, given this tool is used for real drug-discovery decisions.
5. **Database integration files are 100% mocked** despite being the modules
   named as owning that responsibility; the real, working integration lives
   in an unrelated code path (`server.py` proxy + `js/api.js`).

## Open PR #1 — read before doing anything else
There is already an open pull request,
[**#1: "Enterprise hardening: a test suite, four verification gates, and the
silent bugs they found"**](https://github.com/AGIFutureFoundation/AGI-Biotech-tool/pull/1)
(branch `enterprise-hardening-and-ingestion`, 54 commits accumulated over
2026-09-26 through 2026-09-28, evidently from prior runs of this same review
task). It independently found and **already fixes** nearly everything in the
"Top Issues" list above:
- Auth bypass, plaintext-accepted passwords, and the hardcoded JWT secret are
  fixed with real scrypt password hashing, constant-time verification, and a
  random per-process signing-key fallback with a loud warning (verified by
  reading `auth.py` on that branch directly).
- A real `vina_score.py` and honest 3-state `health.py` appear to replace some
  of the fake-science / fake-health-check issues above.
- Adds an egress allowlist checker (`scripts/check_egress.py`), a 1,262-test
  suite, and a `make verify` gate — none of which exist on `main` today.

**This PR also needs a human's own review before merging, for reasons beyond
what an hourly bot should decide alone:**
- It rewrote the *branch's own* git history with `git-filter-repo` to strip a
  210MB video file that made the branch unpushable. I confirmed `origin/main`
  is **unaffected** (still `806b113`, matches this checkout) — the rewrite did
  not touch the shared `main` branch. But anyone who had already cloned this
  specific feature branch needs to re-clone it.
- It adds a wallet/payment/blockchain surface (hand-rolled pure-Python
  `secp256k1.py`/`keccak.py`, SIWE sign-in, an `x402.py` payment module, and
  Monad chain-anchoring) — consistent with the project's own "biodao.blockchain"
  branding and prior rebrand commit, and described as opt-in/off-by-default
  with no key ever held server-side, but hand-rolled crypto primitives
  specifically warrant a security-focused human read before this ships,
  regardless of how well-tested against vectors.
- It's enormous: 161 files, +62,050/-8,982 across 54 commits. No CI is
  configured on the repo (status check is "pending" with 0 runs), so the
  `make verify` / test-suite evidence in the PR body is self-reported, not
  independently re-run by GitHub.
- It also touches `data/agi_compounds.json` with unrelated dock-score data
  from a prior browser session — flagged by the PR author itself as "outside
  my scope" but included anyway.

**Recommendation: do not let this merge on auto-approval alone.** The one
existing review comment on the PR is from a bot (`tenki-reviewer[bot]`) that
only looked at the most recent (file-removal) commit and explicitly says
there was "no diff content to review" — it did not review the substantive
54-commit change set.

## Recommended Actions
- Prioritize a human review of PR #1 given its size and the crypto/history-
  rewrite items above; it appears to be high-quality, well-evidenced work but
  is too consequential for another automated pass to wave through.
- Once reviewed: decide the fate of the dead Flask block in `server.py`
  (finish it or delete it) — this wasn't clearly addressed in what I could
  verify from the PR branch's file listing.
- Add real API-key/network mocking + integration tests for the 13 databases
  that currently have **no implementation anywhere** (PubMed, ArXiv, GenBank,
  dbSNP, GEO, BioGRID, Gene Ontology, CrossRef, Google Scholar, SureChEMBL,
  GTEx, ClinVar, RefSeq), vs. the 9 that are genuinely wired via `js/api.js`.
- No new PR was opened by this run: the critical/high findings above are
  already addressed on PR #1's branch, and opening a second, competing PR
  would duplicate that work rather than add value.
