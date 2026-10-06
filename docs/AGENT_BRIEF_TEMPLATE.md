# Agent Brief Template (agi-bioxr)

For the orchestrator. Facts below were checked on 2026-09-21. Re-check the baseline before you quote it.

## 1. What is wrong with the current briefs

1. **"Verify by execution" is too vague to change behaviour.** An agent obeys it by running the happy path once and pasting the output. None of the real bugs here would have shown up that way: 20 identical molecules still print, and `int("30M")` still raises only if someone reads the metric. Each was caught by an **invariant**: unique count == requested count, one definition per name, the value's type and provenance. **Fix:** every brief names at least one falsifiable check, an observable that would show the claim is wrong. A generic "docs lie" paragraph mostly adds tokens. One concrete sentence ("the docstring says X; show me X") does more.

2. **"Real output" can still be performative, and this repo makes that easy.**
   - The system `python3` has neither rdkit nor pytest. Several modules catch `ImportError` and degrade quietly, so an agent that runs the wrong interpreter can exercise the fallback path and call it success. Pin `.venv/bin/python`.
   - `pytest` currently reports **12 failed / 182 passed**. Most of the passes are the parametrized "module imports" floor, and pytest also collects legacy `server/test_*.py` and `scripts/test_*.py` files, whose async tests fail without a plugin. "182 passed" sounds like coverage and mostly isn't.
   - **Fix:** require a before/after baseline with the exact command, and ask for the delta, not the total.

3. **You don't say whether "correct" means *it runs* or *it's true*.** `_calculate_binding_energy` is `-8.5` minus a hand-set lookup table, capped at `-11.5`. `_calculate_selectivity`'s docstring says "lower is better", but the code treats 1.0 as best. An agent told to "fix correctness" will make fabricated numbers run cleanly, which is worse than a crash because it removes the last visible sign that something is off. **Fix:** make every brief pick one of *run*, *true*, or *label as heuristic*, and never allow a heuristic to leave the function looking like a measurement.

4. **File ownership covers write collisions but not read contamination.** Right now `server/biotech_*.py` is mid-edit by another agent. Any agent that runs the full suite, or imports those modules, sees someone else's half-finished state and either "fixes" it or blames itself. **Fix:** say what the agent may *run* as well as what it may *write*. Failures outside its ownership are reported, not touched.

5. **Owning a file doesn't mean the file is live.** `index.html` loads only `js/main.js`. Six JS files (1,726 lines) are unreachable from it: `immersive-xr-enhanced.js`, `hand_gesture_control.js`, `advanced_voice_control.js`, `gesture_voice_integration.js`, `agent_training_interface.js` and `vr-data-consumer.js`. `immersive-xr.js` is reachable, through a late import at `main.js:1525`. An agent can polish dead code and report a feature fixed. **Fix:** make reachability part of the check.

6. **Minor.** The "pediatric oncology researcher" motivation reads well but doesn't steer anything. Replace it with *what decision the output feeds*. The rest of the structure (pre-verified findings, no commit or push, "what could you NOT fix", the length cap) is good. Keep it.

**Over-constraint?** Mostly no. The constraints are on scope and evidence, not method. The real risk runs the other way: an under-specified *definition of done* invites the agent to declare victory at the first green run.

---

## 2. Template

`[L]` means load-bearing: never cut it. `[T]` means trimmable when the task is small or the agent is already warm. Aim for 200–350 words once filled in.

```
TASK [L]: <one sentence, verb first, naming the deliverable>

FEEDS [T]: <who or what consumes this and what decision it drives — one line>

TARGET STATE [L]: <pick one>
  - RUNS: executes without error on the paths listed below.
  - TRUE: output is scientifically/semantically correct as defined by <reference>.
  - LABELLED: can't be made true now; mark outputs as heuristic in code + return value.

ALREADY VERIFIED — do not re-derive [L when present]:
  - <fact, with file:line or command that proved it>
  - <format internals / root cause you already know>

KNOWN FALSE CLAIMS in your area [T]:
  - <docstring/md claim> — actually <reality>

FALSIFIABLE CHECKS — your work is not done until these pass [L]:
  1. <invariant: e.g. len(set(canonical_smiles)) == n_requested>
  2. <reachability: e.g. called from main.js / server route X>
  3. <negative case: input that must fail loudly, not degrade silently>

ENVIRONMENT [L]:
  - Python: .venv/bin/python only (system python3 lacks rdkit/pytest; some
    modules degrade silently on ImportError — confirm the real path ran).
  - Baseline before you touch anything: <command>, expect <N failed / M passed>.
  - Browser: <how to serve + URL, e.g. server/server.py then :8000/?emulate=quest3>

OWNERSHIP [L]:
  - WRITE only: <paths>. New files only under: <path>, and list each one you create.
  - RUN only: <test paths/commands>. Do not run or import: <paths other agents own>.
  - If something outside WRITE is broken, report it; do not fix it.
  - No git commit / push / stash / checkout.

REPORT [L] (≤ <N> words, these headings):
  - Changed: file:line list.
  - Evidence: for each FALSIFIABLE CHECK, the exact command + raw output tail.
  - Baseline delta: before vs after, same command.
  - Not done / not verified: what you couldn't fix, and what you claim but didn't execute.
  - Surprises: anything in the docs you found false.
```

**What to cut first, in order:** FEEDS, then KNOWN FALSE CLAIMS (fold them into ALREADY VERIFIED), then the Surprises heading. Never cut FALSIFIABLE CHECKS, ENVIRONMENT, OWNERSHIP, or the "not verified" line. Those four did the work in every brief that produced a real finding.

---

## 3. Worked examples

### A. Frontend / WebXR

```
TASK: Make grab-and-move of the ligand work with Quest 3 controllers in the VR session.
TARGET STATE: RUNS.
ALREADY VERIFIED: index.html loads only js/main.js. The live XR path is xr.js (XRManager,
  startSession) plus immersive-xr.js (imported at main.js:1525). immersive-xr-enhanced.js
  and the gesture/voice modules are NOT reachable. Do not edit them or cite them as evidence.
FALSIFIABLE CHECKS:
  1. At :8000/?emulate=quest3, Enter VR, squeeze on the ligand, move 0.2 m: its centroid
     (log it from main.js) changes by ~0.2 m. Paste the console lines.
  2. Browser console has zero uncaught errors across load → enter VR → exit.
  3. On a page load without emulate and without navigator.xr, the Enter VR button is
     disabled, not throwing.
ENVIRONMENT: .venv/bin/python server/server.py; browser at http://localhost:8000.
OWNERSHIP: WRITE js/xr.js, js/immersive-xr.js. RUN the browser only; no pytest needed.
  main.js is owned by another agent — if it needs a change, describe the diff in your report.
REPORT ≤200 words, standard headings.
```

### B. Scientific correctness

```
TASK: Audit the pyrene Series-3 scoring functions and make each one either true or honestly labelled.
FEEDS: Whether Series-3 rankings can be shown to a researcher at all.
TARGET STATE: LABELLED by default. TRUE only where RDKit can compute the quantity
  (e.g. SA score, descriptors).
ALREADY VERIFIED: server/pyrene_apoptotic_discovery.py: _calculate_binding_energy is
  -8.5 minus hand-set 'potency_boost' constants, capped at -11.5 (not computed).
  _calculate_selectivity's docstring says "lower is better" but it returns 1.0 as best.
  tests/test_pyrene_discovery.py fails: series_3 lists 'isothiazole', which the
  warhead library lacks.
FALSIFIABLE CHECKS:
  1. For every numeric field in get_compound_summary(), state "computed by X" or
     "heuristic constant", and make the returned dict carry that provenance.
  2. Any function you call TRUE: show two different molecules getting different values,
     and one value checked against an independent RDKit call.
  3. The isothiazole test passes. Did you add the warhead or remove the claim? Say which, and why.
ENVIRONMENT: .venv/bin/python -m pytest tests/test_pyrene_discovery.py -q
  (baseline: 1 failure).
OWNERSHIP: WRITE server/pyrene_apoptotic_discovery.py, tests/test_pyrene_discovery.py.
  RUN only that test file plus tests/test_module_imports.py.
REPORT ≤250 words. List every number you could NOT ground.
```

### C. Data pipeline

```
TASK: Deduplicate data/agi_compounds.json and make scripts/extract_compounds.py refuse to emit duplicates.
TARGET STATE: TRUE: one record per unique canonical structure.
ALREADY VERIFIED: the catalog advertises 425 compounds but holds 12 unique structures.
  Two scripts write the same file: extract_compounds.py:32 and seed_demo_library.py:24.
  Find out which one produced the current file before changing either.
FALSIFIABLE CHECKS:
  1. len(records) == len({Chem.MolToSmiles(Chem.MolFromSmiles(s)) for s in smiles}), shown
     before and after with the one-liner you used.
  2. Records whose SMILES don't parse are counted and reported, never dropped silently.
  3. Re-running the extractor on its source reproduces the file byte-for-byte (idempotent).
  4. grep the repo for the old count (425) and list every doc/UI string that still claims it.
     Report them; do not edit files you don't own.
ENVIRONMENT: .venv/bin/python; confirm rdkit imports first and fail if it doesn't.
OWNERSHIP: WRITE data/agi_compounds.json, scripts/extract_compounds.py; keep a backup of the
  original under data/agi_compounds.orig.json and list it. RUN tests/test_chem_extract.py.
REPORT ≤200 words.
```

---

## 4. Pre-dispatch checklist

- [ ] TARGET STATE is one of RUNS / TRUE / LABELLED.
- [ ] At least one **falsifiable** check: an invariant or negative case, not "run it and show output".
- [ ] A reachability check, if the task touches JS or a server route.
- [ ] `.venv/bin/python` and a baseline command with its expected numbers.
- [ ] WRITE paths and RUN scope are both listed, and neither overlaps another live agent.
- [ ] Everything I already verified is in the brief, with file:line.
- [ ] The report asks for exact commands plus raw output, a baseline delta, and "claimed but not executed".
- [ ] No commit or push. Any new files must be listed.
- [ ] Under ~350 words. If longer, cut from the `[T]` sections.
