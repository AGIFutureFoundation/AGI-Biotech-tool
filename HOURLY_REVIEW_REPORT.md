# biodao.blockchain Hourly Review Report

## Timestamp
2026-10-05 (automated scheduled review)

## Phase Status

- **Phase 0 (core local molecular viewer, `server/server.py` lines 1–495, `js/*`):** Working as documented.
  This is a genuinely well-built, carefully-caveated local structural-biology/docking tool (see `README.md`
  "How far to trust the numbers" — honest about the limits of its own scoring and dynamics). Runs via
  `main()` → `ThreadingHTTPServer.serve_forever()`.
- **Phases 1–9 (auth, projects, reporting, agents, AR/VR, orchestration, molecular research pipeline,
  pyrene discovery, continuous evolution — everything appended to `server/server.py` after line ~495, plus
  `server/agent_*.py`, `server/master_agent.py`, `server/*orchestration*.py`,
  `server/pyrene_apoptotic_discovery.py`, `server/continuous_compound_evolution.py`):** **Not reachable at
  runtime.** Root cause below. Despite being marked "✅ COMPLETE" / "PRODUCTION READY" in nine separate
  status documents, none of this code executes when the project is started the way `README.md` instructs.

### Root cause: `server/server.py` cannot run Phases 1–9

1. `server/server.py` never contains an `app = Flask(...)` statement, yet uses `@app.route(...)` roughly 50
   times and calls `app.run(...)` three times. `app` is simply never defined.
2. The file has **four** separate `if __name__ == '__main__':` blocks (lines 494, 719, 847, 1075), each
   presumably added in a different "phase" commit without removing the previous one.
3. When run as documented (`python server/server.py`), Python executes top to bottom. It hits the first
   guard at line 494, calls `main()`, which calls `srv.serve_forever()` — a call that **never returns**.
   Every line after 495 (all of Phase 1 onward, ~590 lines, including the undefined `app` and all later
   route/agent/websocket code) is never even parsed as live code in that process.
4. If any of that later code were ever imported or reached another way, it would raise
   `NameError: name 'app' is not defined` at the first `@app.route` decorator.
5. Confirms the above: `requirements.txt` lists only `rdkit`, `pypdf`, `openmm`, `pdbfixer` — **no `flask`,
   no `pyjwt`, no `websockets`**, i.e. the dependencies Phases 1–9 import are not even declared, and are not
   installed in this environment. This is consistent with that code never having been run end-to-end.

**Net effect:** the "8,500+ lines of production-grade enterprise code" claimed complete across Phases 1–9
is, as far as this review can verify, dead/unreachable code. This is a correctness finding, not a style
nitpick — it means the auth system, RBAC, project management, agent orchestration, AR/VR voice/gesture
control, and the molecular-research/pyrene-discovery pipeline have apparently never been exercised as a
running system.

**Not fixed in this PR.** Properly wiring nine phases of agent/orchestration/websocket code that has
seemingly never run together is a product/architecture decision (does the team even want all of it live,
given the integrity concerns below?), not a mechanical bug fix, so it's left to a human call — see
"Recommended PRs."

## Compliance Score

**25/100** — not because the core viewer is unsafe (it is honestly documented), but because of two
findings that are compliance/integrity issues in their own right:

1. **Fabricated partnership claims.** Nine status/guide documents (`PROJECT_STATUS.md`,
   `DEPLOYMENT_GUIDE.md`, `COMPLETE_ENTERPRISE_GUIDE.md`, `PHASE_9_MOLECULAR_COMPLETE.md`,
   `PHASE_7_COMPLETE_SUMMARY.md`, `ENTERPRISE_MOLECULAR_RESEARCH_SYSTEM.md`) repeatedly state the project is
   "in collaboration with," has as "Foundation Partners," or is building "for" the **ALS Association**, the
   **Michael J. Fox Foundation**, and **Shriners Children's Hospital** — three real, identifiable nonprofit
   health organizations — with specific fabricated details (named university research centers, month-by-month
   delivery timelines). Nothing in this repository (no contract, MOU, email, LICENSE, or CONTRIBUTORS file)
   substantiates any relationship with these organizations. Presenting this externally would misrepresent
   affiliation with real charities — a reputational and potentially legal risk for whoever operates
   `agifuturefoundation.org` (the contact address in `README.md`/`PYRENE_APOPTOTIC_SYSTEM.md`).
2. **Unvalidated medical claims presented as deployment-ready.** `PYRENE_APOPTOTIC_SYSTEM.md` presents a
   pediatric-oncology ("apoptotic drug discovery") system as "✅ COMPLETE & READY FOR DEPLOYMENT" /
   "PRODUCTION READY," with specific-looking numbers like "pediatric safety: 0.92 (92%)." Those numbers are
   hardcoded per-warhead constants in `server/pyrene_apoptotic_discovery.py` (e.g.
   `'pediatric_safety': 0.88`), not derived from any assay, animal model, or clinical data. No compound
   described has been synthesized. Framing this as deployment-ready for pediatric cancer is the kind of
   overclaiming that could mislead a reader (family, clinician, investor, regulator) into thinking real
   safety/efficacy validation exists.
3. Minor: `DEPLOYMENT_GUIDE.md` referenced a `LICENSE` file that does not exist in the repo.

**Fixed in this PR:** added prominent correction banners to all seven affected documents, replaced
"Foundation Partners" language with accurate "potential beneficiary, no partnership established" language,
and downgraded the pyrene doc's status from "PRODUCTION READY" to "computational prototype only, no
experimental or clinical validation."

**Auth/security (separate from the above):**
- `server/auth.py` `authenticate_user()` checked only that the email matched a known user and **never
  checked the password at all** — any password, including an empty string, authenticated as that user. Also
  no password was ever stored for any user. **Fixed:** added PBKDF2-HMAC-SHA256 password hashing
  (390,000 iterations, random salt, constant-time comparison) with real verification; `create_user()` now
  requires a password; `server/server.py`'s `/api/auth/register` route now rejects a missing password and
  passes it through.
- `SECRET_KEY` fell back to the hardcoded literal `'dev-secret-change-in-production'` with no guard rail.
  **Fixed:** the fallback still works for local/dev use, but the server now refuses to start with no
  `JWT_SECRET` set if `FLASK_ENV`/`ENV` is `production`.
- `app.run(debug=True, ...)` appears three times in `server/server.py`. Flask's debug mode enables the
  Werkzeug interactive debugger, which allows arbitrary code execution from any client that can reach it.
  **Not fixed in this PR** (left to the human call on Phases 1-9, since it sits inside currently-unreachable
  code — see above) but should be addressed before any of that code is wired up and exposed, including over
  the Wi-Fi/headset HTTPS mode the README documents.
- `create_user()`'s `user_id` derivation used `hashlib.md5` — low severity (not used for any secret), left
  as-is to keep this PR focused; flagged here for a future cleanup pass.

## Database Integration

**Pass, with caveats.** `README.md`'s "The databases" table is accurate and matches what's actually wired
in `js/api.js` and `server/server.py`'s proxy allowlist (PDB, AlphaFold, UniProt, Open Targets, ChEMBL,
PubChem, Foldseek, InterPro, Reactome, STRING, Human Protein Atlas, gnomAD, Pharos, ClinicalTrials.gov,
Europe PMC, openFDA, BioThings, UniChem, KEGG, BindingDB, PDBe) — this is a real, usable set of public
bioinformatics integrations with sensible fallback behavior ("the app reports it and carries on" per
README). This part of the project is in noticeably better shape than the Phase 1–9 claims above; no fix
needed here.

`server/biotech_database_integration.py` and `server/biotech_molecular_integration.py` (the ClinicalTrials/
Europe PMC/STRING/Reactome/InterPro/Protein Atlas/UniChem/PDBe/gnomAD glue code referenced in this task's
checklist) exist and look reasonable on inspection, but — per the root-cause finding above — are only
reachable through the Phase 1+ Flask layer that never actually starts, so their real-world error handling
under the live server has not been exercised.

## Enterprise Hardening

**Not verified — same root cause.** `error_recovery.py`, `workflow_persistence.py`, `monitoring.py`, and
`load_testing.py` exist and contain plausible-looking retry/circuit-breaker/checkpoint/metrics code, but
they are only imported by the Phase 3+ code path in `server/server.py` that the blocking `main()` call
prevents from ever running. Whatever resilience patterns they implement have apparently never been
exercised against a live server. No fix attempted here; this is downstream of the root cause above.

## Top Issues (Priority Order)

1. **Critical — `server/server.py` has no working entry point for Phases 1–9.** No `app = Flask(...)`,
   four conflicting `if __name__ == '__main__':` blocks, first one blocks forever. Everything built in
   "Phase 1" through "Phase 9" is unreachable dead code as currently structured.
2. **Critical — fabricated claims of partnership with ALS Association, Michael J. Fox Foundation, and
   Shriners Children's Hospital** across seven documents, with fabricated specifics (university centers,
   delivery timelines). Reputational/legal exposure if ever shown externally. Partially mitigated in this
   PR with correction banners; recommend a full rewrite or removal by a human who can confirm the real
   status of any outreach to these organizations.
3. **Critical — pediatric-oncology "drug discovery" system marketed as "PRODUCTION READY"** based on
   hardcoded heuristic numbers with no experimental backing. Mitigated in this PR with a corrected status
   banner; recommend never describing this subsystem as deployment-ready until real assay data exists.
4. **High — `authenticate_user()` accepted any password.** Fixed in this PR.
5. **High — `requirements.txt` omits `flask`/`pyjwt`/`websockets`,** the dependencies the unreachable Phase
   1+ code imports, meaning it has likely never been installed+run together even in development.
6. **Medium — `app.run(debug=True)` ×3** inside the currently-unreachable Flask layer; must be fixed before
   that layer is ever wired up and exposed beyond localhost.
7. **Low — dead reference to a non-existent `LICENSE` file; `hashlib.md5` used for a non-secret user-id
   derivation.**

## Recommended PRs

- **Decide and implement one real entry point for `server/server.py`** (or split Phases 1–9 into their own
  module with one `app = Flask(__name__)` and one `if __name__ == '__main__':` block), then actually run it
  and fix whatever breaks — expect real bugs once this code executes for the first time.
- **Add `flask`, `pyjwt`, and whatever websocket library `websocket_streaming.py` needs to
  `requirements.txt`**, as a prerequisite for the above.
- **Human review of the "Foundation Partners" framing** in all affected docs: either pursue and document a
  real relationship with these organizations, or remove the named-organization framing entirely rather than
  just softening it, since this review could only add disclaimers, not fully resolve the underlying claim.
- **Gate `debug=True`** behind an explicit `--debug`/`FLASK_DEBUG` flag once Phase 1+ is wired up and
  reachable from a network.
- **Add `LICENSE`** or remove references to it.

## This PR

Branch `hourly-review/critical-fixes-20261005` contains:
- Correction banners + status downgrades on `PROJECT_STATUS.md`, `DEPLOYMENT_GUIDE.md`,
  `COMPLETE_ENTERPRISE_GUIDE.md`, `PHASE_9_MOLECULAR_COMPLETE.md`, `PHASE_7_COMPLETE_SUMMARY.md`,
  `ENTERPRISE_MOLECULAR_RESEARCH_SYSTEM.md`, `PYRENE_APOPTOTIC_SYSTEM.md`.
- `server/auth.py`: real password hashing/verification (PBKDF2-HMAC-SHA256) replacing the no-op password
  check; `JWT_SECRET` now required in production.
- `server/server.py`: `/api/auth/register` now requires and forwards a password.

No change was made to the Phase 1–9 entry-point/dead-code issue, the Flask `debug=True` calls, or the
missing dependencies — those need a human decision on scope (see "Recommended PRs") rather than an
automated fix.
