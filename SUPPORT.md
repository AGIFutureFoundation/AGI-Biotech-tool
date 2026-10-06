# Support

This is a small project. There is no support team, no chat channel, no forum and no service-level
agreement. What follows is an honest map of where to look and who to ask.

## Try these first

Most problems are already answered in the repository:

- **`README.md`** — setup, the headset paths (HTTPS and `adb reverse`), importing your compound
  collection, what every panel does, and the section "How far to trust the numbers", which is the
  first place to look when a result surprises you.
- **`docs/DEMO.md`** — the running order, if you are trying to reproduce the walkthrough.
- **`docs/SPEC.md`** — the working spec.
- **`CONTRIBUTING.md`** — how to run the checks, and the conventions behind them.

## Check that it is not your environment

Nearly every "it does not work" report here has one of three causes.

**The wrong interpreter.** The system `python3` has neither rdkit nor pytest, and several modules
degrade silently rather than crash when an import fails. Always run `.venv/bin/python`.

**The server is not running.** Without it the app still loads, but 3D embedding, all-atom dynamics,
server-side PDF reading, shared sessions and the CORS proxy all switch off. The server prints which
engines it found at startup — read that output. Start it with `make serve`.

**A public database is having a bad day.** ChEMBL in particular returns server errors for spells.
The app reports it and carries on. Nothing here has a hard dependency on any single source.

Then confirm the repository itself is healthy:

```bash
make verify
```

That runs the test suite, the import check and the JS reachability check. If it is green, the
problem is in your environment or in a remote service; if it is red, say so in your report and
paste the output.

## Opening an issue

Use the issue templates. Pick the right one — they route differently:

- **Bug report** — something errors, hangs or does not do what it says.
- **Suspect value** — a number looks wrong, implausible or too tidy. This is the most valuable
  report you can file here and you do not need to know why it is wrong. "This score is identical
  for twenty different molecules" is a complete report.
- **Data or citation problem** — a target, identifier, PDB count, structure or citation that does
  not match its source.
- **Feature request** — something the tool should do and does not.

In any of them, include the exact command you ran and its raw output. This project treats a claim
as unestablished until it has been executed, and that applies to bug reports as much as to fixes.

## Security

Do not open an issue. See `SECURITY.md` and email **x@agifuturefoundation.org**.

## Response times

Issues are read by the maintainer when time allows, which may be weeks. There is no triage rota and
no guarantee that anything will be fixed. A report with a reproduction has a far better chance than
one without — and a pull request that carries its own evidence has the best chance of all.

## Not supported

- Deployment as a multi-user or public service. The app is built to run locally; see `SECURITY.md`
  for why that is not a formality.
- Scientific interpretation of results. The docking scores, the interactive dynamics, pocket
  detection, the drug-likeness rules and the CNS score are heuristics, and the README says exactly
  how far each can be trusted. Nobody here can tell you whether your compound will work.
- The BigQuery panel beyond what the README documents. It needs your own Google Cloud project and
  is the one feature that has not been run end to end.
- Optical structure recognition from scanned PDFs. Those hold pictures rather than text; you need
  DECIMER or OSRA before anything can import them.
