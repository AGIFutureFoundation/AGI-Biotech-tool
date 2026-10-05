# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-05 (automated review)

## Phase Status
- Phase 0-9 analysis: pending final agent pass (will be appended)

## Compliance Score
25/100 — two unauthenticated-reachable critical vulnerabilities in the live auth system, plus no audit trail at all.

## Database Integration
FAIL — the Python "integration" modules that claim 30+ live database connectors are entirely mocked.

## Enterprise Hardening
FAIL (mostly) — resilience modules exist as library code but are never wired into the running server.

## Top Issues (Priority Order)
1. **CRITICAL — Authentication bypass**: `authenticate_user()` in `server/auth.py` never checked the submitted password; anyone who knew a registered email got a valid signed session token. FIXED in this PR.
2. **CRITICAL — Privilege escalation via self-registration**: `/api/auth/register` passed the client-supplied `role` field straight into `create_user`, letting any anonymous caller mint an `admin` account. FIXED in this PR.
3. **HIGH — IDOR on project access**: `GET /api/projects/<id>` only checked that the caller was authenticated, not that they owned or were a member of the project; the existing `Permission.can_access_project` helper was defined but never called. FIXED in this PR.
4. **MEDIUM — Hardcoded JWT signing secret**: `auth.py` defaulted to the literal string `'dev-secret-change-in-production'` when `JWT_SECRET` was unset, letting anyone who read the source forge admin tokens. FIXED in this PR (random per-process secret instead of a known fallback, with a startup warning).
5. **HIGH — Database integrations are decorative**: `server/biotech_database_integration.py` and `server/biotech_molecular_integration.py` contain zero real HTTP calls to any of the 30+ databases they claim to federate (ClinicalTrials.gov, STRING, Reactome, etc.) — methods literally comment "Simulate query execution" and return hardcoded fake records. The real, working integrations live only in `js/api.js` (client-side) and a generic proxy in `server/server.py`. Not fixed in this PR — this is a larger, non-security-critical scope/architecture gap, flagged for a follow-up.
6. **MEDIUM — Enterprise hardening modules are unreachable dead code**: `error_recovery.py`, `workflow_persistence.py`, `monitoring.py`, `load_testing.py`, `performance_optimization.py`, and `scaling_infrastructure.py` are never imported by `server/server.py`. No `/health` or `/metrics` endpoint exists, workflow execution never checkpoints/resumes, and the circuit breaker's `is_available()` is computed but never consulted before a retry. Not fixed in this PR — wiring these in is a larger feature-level effort, flagged for follow-up.
7. **LOW — No audit trail**: no action anywhere logs who did what and when (logins, registrations, project mutations, role changes).
8. **LOW — User IDs derived from `MD5(email)`**: not a security control itself, but allows offline enumeration/correlation of user IDs from email addresses. Not fixed in this PR.

## Recommended PRs
- (this PR) Fix the auth bypass, registration privilege escalation, project IDOR, and hardcoded JWT fallback.
- Follow-up: wire `monitoring.py` into a real `/health`/`/metrics` endpoint, make `workflow_persistence.py` checkpoints actually resumable, and make the circuit breaker in `error_recovery.py` actually gate calls.
- Follow-up: either implement real HTTP calls in the Python `biotech_*_integration.py` modules or remove/relabel them as mocks so the code doesn't overstate what's live (the real integrations already work, but only in `js/api.js`).
- Follow-up: add structured audit logging (user_id, action, resource, timestamp) on auth and project-mutation endpoints.
