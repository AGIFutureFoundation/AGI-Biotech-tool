# Contributing to biodao.blockchain

This is a scientific tool. Someone may look at a number it prints and decide which molecule to
make. That single fact sets every rule below.

There is no review rota and no release train. What exists is a set of checks you can run yourself
in one command, a CI workflow that runs those same checks, and a small number of conventions that
were learned the expensive way. Read this before your first change; it is short because it only
describes things that are actually true here.

---

## Set up

The interpreter is not optional. Use `.venv/bin/python`, always.

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

The system `python3` on this machine has neither rdkit nor pytest:

```
$ python3 -c "import rdkit"
ModuleNotFoundError: No module named 'rdkit'
$ python3 -c "import pytest"
ModuleNotFoundError: No module named 'pytest'
```

Several modules catch `ImportError` and degrade quietly, so the wrong interpreter does not crash —
it exercises a fallback path and reports success. A run under the system python proves nothing.
Every command in this file, and every command in the `Makefile`, is pinned to `.venv/bin/python`
for that reason.

## Run the checks

`make` is the single entry point, so an agent, a person and any future CI all run the same thing.

| Command | What it does | Current result |
| --- | --- | --- |
| `make test` | full pytest suite | 525 passed, 1 xfailed (~13 s) |
| `make imports` | every module under `server/` and `scripts/` imports | 53 passed |
| `make reachable` | no orphaned JS modules | 22 of 22 modules reachable |
| `make verify` | `test` + `imports` + `reachable` | exit 0 |
| `make citations` | re-resolves every disease-panel identifier against live services | 263/263 checks passed |
| `make serve` | runs the app on <http://localhost:8000> | serves `200` |

Those figures were observed on 2026-09-22 on `enterprise-hardening-and-ingestion`. Treat them as a
baseline to diff against, not as a constant: report the **delta** your change makes, not the total.

`make verify` is what to run before you hand work over. `make citations` reaches the network and is
slower (it caches responses under `~/.cache/agi-bioxr/`); run it whenever you touch
`server/disease_panels.py` or anything it cites.

Tests import production modules by bare name (`from smiles_repair import ...`) because
`server/` and `scripts/` are put on `sys.path` once, in `tests/conftest.py`. New modules dropped
into either directory are picked up by the import regression test automatically — nobody has to
remember to add them.

---

## The five rules

These are not style preferences. Each one exists because its absence produced a specific, shipped
falsehood in this repository.

### 1. Verify by execution, not by reading. A docstring is a claim.

An entire HTTP API layer in this repo raised `NameError` on import and had therefore never once
executed, while the documentation described it as production-ready. Nobody had run it; several
people had read it.

Before you assert that something works, run it and paste the output. "I read the code and it looks
right" is not evidence. Neither is running the happy path once — see rule 2.

### 2. Every check must be able to fail. Prove it.

A test that cannot fail is worse than no test, because it buys confidence without paying for it.
When you add one, break the thing it guards, show the check catching it, then put the thing back.
Include that output in your pull request.

The pattern is already in the repo. `scripts/verify_panel_citations.py` takes a `--seed-bad` flag
that injects a target whose every identifier is deliberately wrong:

```
$ .venv/bin/python scripts/verify_panel_citations.py            ; echo $?
263/263 checks passed ... every cited identifier re-resolved.
0
$ .venv/bin/python scripts/verify_panel_citations.py --seed-bad ; echo $?
  ZZZBAD   chembl-target  CHEMBL99999999   did not resolve (not found)
  ZZZBAD   nct            NCT99999999      did not resolve (not found)
1
```

That is what a falsifiable check looks like. Copy the shape.

Aim each check at an **invariant**, not at "it ran". A compound generator here returned 20
identical molecules when asked for 20, and every happy-path run of it looked fine. The check that
would have caught it is one line: `len({canonical_smiles}) == n_requested`. Other invariants worth
reaching for: one definition per name (a scoring method here was defined twice, with conflicting
weights), the type and provenance of a value (a "1.5B+ records" metric was produced by
`int("30M")`), and a negative case that must fail loudly rather than degrade silently.

### 3. Never fabricate a scientific value. A gap stays a gap.

Docking, MD and ADMET outputs in this repo were once `random()` behind an "AutoDock Vina
integration" label. A "pyrene" core was phenanthrene. PDB counts were invented across three target
panels. Every one of those ran cleanly. Running cleanly is exactly the problem: a fabricated number
that computes removes the last visible sign that something is wrong, which is worse than a crash.

If the data is missing, record the gap. Do not fill it.

The suite contains one deliberately `xfail`ed test, and it is there on purpose:

```python
@pytest.mark.xfail(
    strict=True,
    reason="Known data gap, not a code defect: series_3 advertises an 'isothiazole' "
           "warhead that the library has no entry for. Closing it means either dropping "
           "a documented warhead or inventing its potency_boost, pediatric_safety and "
           "selectivity_risk constants, and fabricating pediatric safety numbers is not "
           "acceptable. strict=True so this alerts if someone supplies real values.",
)
```

`strict=True` means the suite fails if that test ever starts passing. Do not make it green by
supplying numbers. If you can close it with a real, cited source, say where the source is in the
pull request.

### 4. A synthetic value must announce itself at every exit.

`server/synthetic_provenance.py` defines `SyntheticValue`, a float that no measurement or model
produced. It carries the marker through `str`, `repr` and `format`, the record it sits in carries a
`provenance` field, and the first one created in a process raises `SyntheticResultWarning`.

If your code emits a placeholder number, wrap it. If your code consumes one, do not strip the
marker. When a real engine lands, set `provenance` explicitly — the default is always
`"synthetic"`, so the failure mode of forgetting is a number that looks fake rather than a fake
number that looks real.

The same instinct governs data repair. `server/smiles_repair.py` will not touch a SMILES string
that already parses, because `C(CN)` is valid chemistry even when the author meant a nitrile, and
rewriting it would silently change the molecule. Ambiguous cases are reported, not fixed. A repair
is accepted only when the original failed to parse and the result parses, and every accepted repair
records the substitutions it applied.

Broadly: pick one of **runs**, **true**, or **labelled as heuristic**, and never let a heuristic
leave a function looking like a measurement.

### 5. Dead code is not fixed code.

`index.html` loads exactly one entry script, `js/main.js`; everything else arrives through import
chains. This repo once carried six JS files, 1,726 lines, that nothing could reach — including one
that was a syntax error and so could never have loaded at all. Work was done on them and reported
as feature fixes.

`make reachable` is a gate on that and exits non-zero when anything is orphaned. If you add a JS
module, make something import it in the same change.

---

## Making a change

1. Branch off `main`. Do not commit directly to it.
2. Take a baseline first: run `make verify` **before** you touch anything, and keep the numbers.
3. Make the change. Keep it to one concern.
4. Run `make verify` again and diff against your baseline. Add `make citations` if you touched a
   disease panel.
5. Open a pull request using the template. The exact commands and their raw output belong in the
   body — that is the part a reviewer actually reads.

State plainly what you did **not** verify. An unverified claim you flag costs a reviewer a minute;
an unverified claim you present as done costs the project a retraction.

CI (`.github/workflows/ci.yml`) runs `make verify` on pushes and pull requests, and the live
citation audit runs on its own schedule in `citations.yml` — the same `make` targets you ran
locally, so a green local run is the best predictor of a green build. What CI cannot check is
whether a number is *true*. That part is the evidence in your pull request body, and it is the only
check there is for it.

## Working alongside other agents and people

Several agents may be working in this tree at once, so **read scope is as real as write scope**.
If a check fails in a file you do not own, report the failure — do not fix it, and do not assume
you caused it. Running the full suite can surface someone else's half-finished state.

Owning a file also does not mean the file is live; check reachability before claiming a fix.

`docs/AGENT_BRIEF_TEMPLATE.md` is the brief format used to dispatch work here. It is worth reading
even if you are a human: it is the clearest statement of what this project counts as evidence.

## Style

There is no formatter or linter configured, so match the file you are editing. In practice that
means 4-space indentation in Python, double quotes, and module docstrings that say *why* rather
than *what* — `synthetic_provenance.py`, `smiles_repair.py` and `check_reachable.py` are the
house style.

New Python dependencies go in `requirements.txt`, one line each, with a trailing comment saying
which feature they switch on and whether the app degrades without them or fails outright.

## Licence

This repository does not currently carry a licence, which means default copyright applies and
contributors have no explicit grant to rely on. Until the maintainer chooses one, be aware that the
terms for reuse of your contribution are undefined. Raise it with the maintainer before sending
anything substantial.

## Reporting rather than fixing

A number that looks wrong is a first-class bug report here, and often more valuable than a patch —
use the "Suspect value" issue template. Security issues go through `SECURITY.md`, not the issue
tracker.
