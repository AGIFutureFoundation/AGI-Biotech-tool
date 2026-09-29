<!--
The evidence sections below are the review. CI runs `make verify`, but nothing automated can tell
whether a number you produced is true — that part is this body. See CONTRIBUTING.md.
-->

## What this changes

<!-- One or two sentences, and why. Link the issue if there is one. -->

## Files changed

<!-- file:line list, with a clause each. Say which files are new. -->

## Evidence

Exact commands and raw output, not summaries. "I read it and it looks right" is not evidence.

```console
$ .venv/bin/python -m pytest ...

```

## Baseline delta

Same command before and after, and the difference between them — not the totals.

| | Before | After |
| --- | --- | --- |
| `make test` | | |
| `make imports` | | |
| `make reachable` | | |
| `make citations` (if touched) | | |

<!-- The 2026-09-22 baseline on this branch was: 525 passed / 1 xfailed; 53 import checks;
     22 of 22 JS modules reachable; 263/263 citation checks. Re-take your own baseline before
     you start rather than quoting these. -->

## Checks that can fail

Every new check must be able to fail, or it is worthless. Seed the bug it guards, show it caught,
then put the thing back — and paste both runs.

```console
$ # with the defect seeded

$ # with the defect removed

```

<!-- Prior art for this in the repo:
     .venv/bin/python scripts/verify_panel_citations.py --seed-bad   -> exit 1
     .venv/bin/python scripts/verify_panel_citations.py              -> exit 0 -->

- [ ] Every new check has been shown failing as well as passing.
- [ ] `make verify` is green, and I ran it with `.venv/bin/python` (not the system python).
- [ ] If I touched JS: `make reachable` still reports every module reachable, and something
      actually imports anything I added.
- [ ] If I touched a disease panel or its citations: `make citations` passes.

## Scientific values

Fill this in if the change produces, changes or consumes a numeric result. Otherwise write "none".

- [ ] Every number this change emits is **computed**, with the engine or source named — or it is
      wrapped in `SyntheticValue` and carries a `provenance` field, or it is labelled a heuristic
      in both the code and the returned value.
- [ ] I invented nothing. Any value I could not ground is recorded as a gap rather than filled in,
      and is listed below.
- [ ] No `xfail` was turned green by supplying a value that is not sourced. (`isothiazole` in
      `tests/test_pyrene_discovery.py` is `strict=True` on purpose.)

Values I could not ground, and what is missing:

<!-- List them. An honest gap here is a good outcome; a plausible guess is the failure mode this
     project exists to prevent. Write "none" if there are none. -->

## Not verified

What you claim but did not execute, and what you could not fix. Be specific. An unverified claim
you flag costs a reviewer a minute; one you present as done costs the project a retraction.

## Outside my scope

Anything broken that you found but did not touch, including failures in files owned by someone
else. Report, do not fix.

---

- [ ] I have read `CONTRIBUTING.md`.
- [ ] This branch is not `main`.
