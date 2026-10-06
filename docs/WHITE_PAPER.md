# AGI BioXR — Technical White Paper

**Status: pre-clinical research tooling.** No compound described anywhere in
this repository has been synthesised, assayed or tested in any biological
system. Nothing here is a therapeutic claim.

Every quantitative statement in this document is followed by the command that
produced it, and Appendix A collects them in one table. All commands are run
with the repository's own interpreter, `.venv/bin/python`; the system Python has
neither RDKit nor pytest, and several modules degrade quietly when an import
fails, so the wrong interpreter produces a passing run that proves nothing.

---

## 1. The problem, and who has it

A computational drug-discovery platform produces numbers. A binding energy, a
PDB count, an ADMET profile, a repurposing score. The person who has to act on
those numbers — order a synthesis, write a grant, brief a clinician — cannot
tell by looking whether any given number came from a calculation over real
atomic coordinates, from a curated database record, or from a constant somebody
typed in eighteen months ago.

This is not a hypothetical failure mode. It is the failure mode this repository
was built out of. Days before this document was written, the same codebase
carried, simultaneously:

- an HTTP API described in its own documentation as production ready, which
  raised `NameError` on import and had therefore never executed once;
- a compound generator that returned twenty copies of one molecule when asked
  for twenty, so the optimiser it fed was searching a population of size one;
- docking, molecular dynamics and ADMET scores drawn from `random()` behind a
  label reading "AutoDock Vina integration", on a machine where Vina was not
  installed;
- a load-testing harness that measured how fast Python can sleep;
- a "pyrene" compound series built on phenanthrene, whose warheads were never
  chemically attached, so each compound was a label rather than a molecule;
- target panels carrying invented structure counts, including one gene credited
  with 45 PDB entries against 3 real ones and three genes credited with 8–15
  structures that had none at all;
- authentication that accepted any password, including the empty string, on
  servers bound to every network interface;
- and no test suite.

None of that was malicious. Each item is what happens when a plausible
placeholder is written to keep a pipeline moving and is never removed, and when
no mechanism exists that can tell a placeholder from a result.

**Who has this problem.** Anyone running a computational pipeline whose outputs
will be read by someone who did not write it: a translational research group
with a hypothesis worth triaging; a foundation deciding which of forty
paediatric genetic conditions has tractable chemical matter; a diligence reader
who needs to know which figures in a deck are measurements. The platform's
premise is that provenance is not documentation. It has to be enforced by the
code, at every exit, or it decays.

---

## 2. The stack, accurately

**Language and runtime.** Python 3 for the server, data layer and scientific
code (27,438 lines across `server/` and `scripts/`); JavaScript ES modules for
the browser and XR layer (30 modules; 28 reachable from `main.js`, and 2 staged —
imported by the test and eval suites while they wait to be wired into the app). RDKit for
cheminformatics. NumPy for the scoring arithmetic. The HTTP layer is the Python
standard library's `ThreadingHTTPServer` with a hand-written dispatch table —
Flask is not installed and is not a dependency.

**Data layer.** `server/db_clients.py` holds live clients for eleven public
biomedical services: PubChem, NCBI E-utilities, ChEMBL, UniProt, the RCSB
search and data APIs, AlphaFold, ClinicalTrials.gov, Reactome, STRING and Open
Targets. Every function makes a real HTTPS call or answers from the on-disk
SQLite cache of one, and parses the real response. Per-host throttling follows
each service's published limits. There is a circuit breaker so an offline run
fails fast rather than waiting out every timeout.

**Chemistry.** `server/pyrene_structures.py` assembles molecules from a pyrene
core and an eleven-member warhead library and profiles them from structure.
`server/smiles_repair.py` recovers condensed organic shorthand (`OCH3`, `CF3`,
`NO2`) that chemists write by hand and RDKit rejects.

**Scoring.** `server/vina_score.py` is a Python port of the AutoDock Vina
empirical functional form (Trott & Olson 2010) implemented in `js/dock.js`. It
is a port rather than a wrapper because Vina and Open Babel are not installed —
`which vina obabel` finds nothing — so before the port there was no Python
docking at all.

**Provenance.** `server/synthetic_provenance.py` provides `SyntheticValue`, a
float subclass whose every textual form carries a `[SYNTHETIC]` marker,
propagates through arithmetic, and raises a one-time runtime warning the first
time one is constructed. Records containing one carry a `provenance` field
naming the specific fields that are placeholders.

**Integrity.** `server/content_store.py` stores research artefacts under the
SHA-256 of their bytes, so the address is the integrity proof, and computes
Merkle roots and inclusion proofs over sets of them. Nothing is broadcast and
no consensus is involved; it produces a root you *could* anchor, and says so.

**Verification.** One entry point, so a person, an agent and CI all run the same
thing: `make test`, `make imports`, `make reachable`, `make citations`,
`make verify`.

---

## 3. Current capabilities, with evidence

### 3.1 The test suite exists and passes

Measured 6 October 2026. Two suites, both offline.

```
$ .venv/bin/python -m pytest tests/ -q
5 failed, 1469 passed, 55 skipped, 1 xfailed, 43 warnings in 48.37s

$ node --test tests/*.test.mjs
pass 227  fail 0
```

**The five failures are stated rather than filtered.** All five are in
`tests/test_server_lifecycle.py` and all five bind a local TCP port, which the
sandbox these runs were made in refuses. They are an environment limitation, not
a regression, and the honest figure is the one above and not a cleaner one. The
single `xfail` is deliberate and is described in §6.

10,629 lines of test code across 40 Python files and 15 JavaScript files. The
JavaScript suites did not exist when this document was first written; they cover
the modules the browser actually runs — structure parsing, pocket detection, the
docking search and its refinement, the dynamics force field, binding-mode
clustering, the voice grammar, the tool registry, the provenance ledger, and the
database layer's behaviour when a source fails. §3.1.1 lists what they found.

### 3.1.1 What the tests found, not just that they pass

A suite that only ever confirms what its author expected is weak evidence. These
are defects the tests located, each fixed in the commit that reported it:

| Defect | Found by |
|---|---|
| The sp2 planarity restraint held its plane normal fixed, so its force was ~19% off its own energy gradient at small pyramidalisation | a finite-difference gradient check |
| PDB insertion codes were dropped, merging residues 100 and 100A and leaving the merged residue with only one C-alpha | parser tests written from the format specification |
| A flat detail cap let hydrophobic contacts crowd out the single π-stacking record | interaction-geometry tests on planted hits |
| "load LRRK2" arrives from a speech recogniser as "load lark two" and matched nothing | voice grammar tests |
| The flexible-refinement loop seeded its running best at infinity and so could never terminate on its first pass | refinement tests |

Two limits were also documented that had been nowhere in the documentation: a
hash chain cannot detect records removed from its *end* without an external
anchor, and the database layer's proxy fallback retries on any failed GET rather
than only a CORS refusal, so one lookup can cost two requests.

`make imports` runs a parametrised import test over every module under
`server/` and `scripts/` — 86 modules, all importing cleanly. That one check
would have caught three of this repository's worst historical bugs: the API
layer that raised `NameError`, a module missing a `typing` import, and a
dependency that was never declared.

```
$ make reachable
entry points : main.js
reachable    : 28 of 30 modules
  STAGED      js/ledger-verify.js (exercised by tests/evals, not yet in the app)
  STAGED      js/rescore.js (exercised by tests/evals, not yet in the app)
```

A staged module is one nothing in the app imports but the test or eval suites do.
The check reports them separately from dead code and fails only on the latter:
conflating the two pushes whoever hits the gate toward wiring an unfinished
module into the live app to get a green tick, which is the opposite of what a
dead-code gate is for.

### 3.2 Every cited identifier re-resolves against the live source

This is the platform's central capability and the reason the rest of it is
worth anything.

`scripts/verify_panel_citations.py` walks all five disease panels — 84 target
records in total — and asks each
external source whether the record still exists and still says what the panel
claims it says. UniProt accessions must resolve and their gene names must
include the panel's symbol. Cited PDB entries must appear in the RCSB search
for that accession, and the panel's structure count must match the live count.
AlphaFold model ids must match — and where a panel asserts there is *no* model,
there must still be none. ChEMBL targets must carry the accession; potent
ligand counts are checked against live activities at pChEMBL ≥ 6, including
where the panel claims zero. Named drugs must still have a curated mechanism
pointing at that target. NCT numbers must still list `CHILD` in their standard
ages. And every PMID quotation must still be a verbatim substring of the live
abstract.

```
$ make citations
250/250 checks passed
354/354 checks passed
207/207 checks passed
190/190 checks passed
263/263 checks passed
checked 5 panels: ALS, Longevity, Parkinsons, Shriners, StJude
```

1,264 checks, zero failures.

> **A note on the panel names.** Two of the five panel identifiers in the source
> are the informal names of the disease areas they were assembled around —
> paediatric oncology and paediatric skeletal and orthopaedic conditions. They
> are internal labels for a set of genes, nothing more. **No agreement,
> partnership, sponsorship or affiliation exists with any named organisation**,
> and none is implied. Where these panels are discussed outside the source tree,
> the disease area is the correct way to refer to them.

**The check earns its keep two ways.** First, it can fail. Run it with
`--seed-bad` and it injects a control target whose every identifier is
deliberately wrong — including a real PMID paired with a sentence that is not in
its abstract — and the run produces 13 failures and a non-zero exit. A verifier
nobody has watched fail is not evidence.

Second, and more to the point, it *has* failed on real data. The longevity
panel quoted a senolytics trial as reporting "completion rates **of** planned
clinical assessments". The paper says "**for**". One preposition. The quote
check is a verbatim substring test against the live abstract, so it failed, and
the panel was corrected. That is the entire argument for this design: a
paraphrase-tolerant check would have passed a sentence that was not in the
paper, and a human reviewer reading for sense would have passed it too.

```
$ .venv/bin/python -c "...efetch PMID 30616998..."
'completion rates for planned clinical assessments' -> True
'completion rates of planned clinical assessments'  -> False
```

### 3.3 The Vina port is checked against the JavaScript term by term

A scoring function ported silently wrong is the dangerous case, because the
output is still a plausible number. So `tests/test_vina_score_port.py` does not
assert that the port is correct. It runs the JavaScript implementation and the
Python implementation over the *same* crystallographic receptor geometry (chain
A of PDB 6O0K, BCL-2 with venetoclax) and the *same* ligand molblock, and
compares every one of the five Vina terms, the atom typing behind each term, the
rotatable-bond count and the H-bond list, to an absolute tolerance of 1e-9.
Both sides hold coordinates as float32 and reduce in double precision, so the
only legitimate difference is summation order; anything larger is a real
divergence.

```
$ .venv/bin/python -m pytest tests/test_vina_score_port.py -q
13 passed in 0.23s
```

A silently-wrong port fails this test. That is the property being bought.

The resulting number is called `vina_like_score` and is deliberately not called
a binding energy. It is unitless — see §4.

### 3.4 The compounds are molecules

The declared core `C1=CC=C2C(=C1)C=CC3=CC=CC=C32`, commented "Pyrene core" with
`rings=4` and documented as a four-ring pyrene platform across eleven files, is
phenanthrene. The current core is pyrene. RDKit settles it:

```
old core (claimed pyrene)  C14H10 rings= 3
current core               C16H10 rings= 4
assembled acrylamide+urea: C20H14N2O2 MW=314.34 cLogP=4.44 rings= 4
smiles: C=CC(=O)c1cc2ccc3cccc4ccc(c1NC(N)=O)c2c34
warheads in library: 11
unknown warhead -> None
```

More fundamentally: previously the warheads were never attached. A compound was
a core plus two warhead *names*, which is why its binding energies were hand-set
constants — there was nothing to compute on. Compounds now assemble, and an
unknown warhead returns `None` rather than guessing.

Docking a real assembled compound into a real pocket:

```
$ .venv/bin/python -c "PyreneVinaScorer().score_warheads('acrylamide','urea','BCL2')"
vina_like_score = -5.507
terms = {'gauss1': -1.071, 'gauss2': -4.545, 'repulsion': 1.1836,
         'hydrophobic': -1.1207, 'hbond': -0.9204}
heavy_atoms= 24 rot= 3 hbonds= 2 poses_kept= 4
receptor = BCL2 / PDB 6O0K, site defined by co-crystallised venetoclax (LBM,
           chain A, excluded from the receptor), 1200 receptor atoms scored
```

### 3.5 Compound generation is no longer degenerate

The generator called a deterministic selector with identical arguments every
iteration. Asking for twenty compounds returned twenty copies of one molecule
under twenty different IDs, so the optimisation loop searched a population of
one. Both states are reproducible from the git history:

```
OLD: n= 20 unique (w1,w2)= 1  unique ids= 20
NOW: n= 20 unique (w1,w2)= 20 unique ids= 20
```

### 3.6 Drug repurposing, validated by blinded rediscovery

`server/repurposing_engine.py` produces ranked, attributable repurposing
hypotheses from live records in ChEMBL, Open Targets, Reactome, STRING and
ClinicalTrials.gov. The score is the sum of its listed terms after per-join
caps — no hidden model, no learned weight — and the whole scheme is emitted with
every report so a reader can disagree with a weight and re-add the terms by
hand. It is ordinal: a 6.0 is not "twice as likely" as a 3.0. Its only job is to
order a worklist.

Two boundaries are enforced in code rather than promised in prose. **No dose is
ever computed**: `documented_doses()` retrieves dose text verbatim from
ClinicalTrials.gov and attaches the NCT id it came from; nothing multiplies,
scales or allometrically converts a dose, and nothing infers a paediatric dose
from an adult one. **Combinations are flagged, never asserted**: `cotarget_flags()`
returns questions.

`scripts/validate_repurposing_recall.py` tests this the only honest way — by
blinding the engine to a known second indication, excluding the compound from
its own evidence, and asking whether it rediscovers it:

```
$ .venv/bin/python scripts/validate_repurposing_recall.py
  sildenafil         -> pulmonary arterial hypertension  rank  3 of 169
  thalidomide        -> multiple myeloma                 rank  1 of 163
  tretinoin          -> acute promyelocytic leukaemia    rank 48 of  91
  minoxidil          -> androgenetic alopecia            MISSED
  raloxifene         -> breast cancer risk reduction     rank  3 of  61
  metformin          -> oncology (investigational)       MISSED
  dimethyl fumarate  -> relapsing multiple sclerosis     rank  1 of  23

  recovered at any rank : 5/7 (71%)
  recovered in top 10   : 57%
  best positive score   : 6.30
  best control score    : 1.20
```

The misses are reported with reasons, not hidden. Minoxidil's targets have
precedent drugs but none with a registered clinical record in alopecia, so the
second indication is simply not reachable from shared-target evidence.
Metformin's resolved target has no *other* drug with a clinical record against
it, so with metformin excluded there is no precedent to transfer. Both are
honest statements about the method's reach.

Negative controls behave: mannitol yields three weak hypotheses topping out at
1.20, and an inventory compound with no database identity yields none at all.

### 3.7 Structures, not strings

`server/smiles_repair.py` recovers hand-written shorthand, under two rules that
make it safe on scientific data. A string that already parses is never touched —
`C(CN)` is valid SMILES meaning carbon-nitrogen even when the author probably
meant a nitrile, so rewriting it would silently change the molecule; those are
reported as ambiguous instead. And a repair is accepted only when the original
failed to parse *and* the result parses, with every substitution recorded.

Re-run over the stored inventory's as-written strings:

```
$ .venv/bin/python -c "repair_many(as_written for the inventory)"
re-run repair over 1336 as-written strings:
{'already_valid': 1180, 'repaired': 156, 'unfixable': 0, 'ambiguous': 23}
```

### 3.8 Security

Authentication took a password argument and never looked at it: any known email
returned a valid JWT carrying that user's role, and the empty string worked as
well as anything else. Passwords are now hashed with `hashlib.scrypt` — memory-
hard, standard library — with a per-user random salt and a constant-time
comparison. An account with no password set cannot authenticate at all, so a
half-built account fails closed, and an unknown email still pays the hashing
cost so it cannot be distinguished by timing. Both servers now default to
`127.0.0.1`; reaching a headset over Wi-Fi requires passing `--host 0.0.0.0`
deliberately.

---

## 4. What the platform explicitly does not do

This section is load-bearing. Anything not listed in §3 belongs here.

**It does not produce binding free energies.** `vina_like_score` is a relative
ranking computed from real coordinates using Vina's functional form and
published weights. Those weights were fitted against a complete Vina pipeline —
its own atom typing, desolvation handling, conformer treatment and optimiser.
Reusing the weights without that pipeline reproduces the functional form, not
the calibration. The number has **no units**. It is not kcal/mol, not a
dissociation constant, and not comparable across receptors. `js/dock.js` says of
itself that it is not a validated replacement for Vina or Glide, and the port
inherits that statement exactly.

**It does not run molecular dynamics.** The "MD" batch is a heuristic over
hand-set constants, emitted as `SyntheticValue`.

**It does not predict ADMET, safety, selectivity or synthetic accessibility.**
These remain heuristics over hand-set warhead constants. Every one is emitted as
`SyntheticValue`, prints with `[SYNTHETIC]`, and appears by name in its record's
`provenance` field.

**It does not compute doses, and specifically does not compute paediatric
doses.** No allometric scaling, no adult-to-child extrapolation, no weight-band
table. Dose text is retrieved verbatim with its NCT id or it is absent. Dose
selection needs PK/PD modelling the platform does not have.

**It does not assert drug combinations.** Two compounds hitting complementary
targets is a reason to run an experiment, not a synergy claim. Synergy,
antagonism and shared toxicity cannot be read off target annotations.

**It does not synthesise or test anything.** No compound in this repository has
been made. Synthetic accessibility scores are placeholders; substitution
regiochemistry is stated as a plausible enumeration, not a claim about synthetic
outcome.

**It does not run AutoDock Vina.** Vina and Open Babel are not installed; the
scoring is a port of the functional form.

**It does not anchor anything on a blockchain.** `content_store.py` computes a
Merkle root and inclusion proofs. Anchoring is a separate, deliberate act with a
cost, and the module does not do it or pretend to.

**It does not have a validated load or throughput benchmark.**
`server/load_testing.py` still simulates workflow steps with
`asyncio.sleep(random.uniform(...))`. Any throughput number it prints measures
how fast Python sleeps. It is not run by `make verify` and no figure from it
appears in this document. It should be treated as unbuilt.

**It does not claim efficacy of any kind, for any compound, in any disease.**

---

## 5. Roadmap

Ordered by what unblocks the most, not by what demonstrates best.

1. **Repair the structural-scoring wire-up.** `PyreneSeries3Generator` with a
   `structural_scorer` currently raises `AttributeError: 'DockingResult' object
   has no attribute 'smiles'` — `_structural_score` reads a field the dataclass
   does not define. The docking module itself works when called directly (§3.4);
   only the generator path is broken. Until it is fixed, generated compounds
   carry heuristic `[SYNTHETIC]` potency and no SMILES. This is the single
   highest-value fix in the repository.
2. **Put the structural path under test**, so the wire-up cannot break silently
   again — the failure above is exactly the class of bug `make imports` catches
   for imports and nothing currently catches for call paths.
3. **Replace or delete `load_testing.py`.** A harness that measures `sleep` is
   worse than no harness, because it produces a number.
4. **Broaden receptor coverage.** Structural scoring needs a curated receptor
   and pocket definition per target; today that curation is narrow, and the
   scorer raises rather than falling back when it is missing.
5. **Retire the remaining `SyntheticValue` fields** by attaching real models —
   ADMET, selectivity, synthetic accessibility — or by deleting the fields. Each
   retirement is independently verifiable: the field stops printing
   `[SYNTHETIC]`.
6. **Run `make citations` on a schedule.** Panel citations are verified against
   live sources, which means they can rot. A monthly scheduled run converts
   silent rot into a failing build.
7. **Independent replication of the port.** The Vina port is checked against
   `js/dock.js`; both could be wrong together. Comparison against a real Vina
   install on a standard benchmark set would close that.

---

## 6. Limitations

Read this section as the most reliable part of the document.

**The verifier checks resolvability, not correctness.** `make citations` proves
that every identifier still resolves and every quoted sentence is still in the
abstract. It cannot tell you that the paper is good, that the quote is
representative rather than cherry-picked, that the target is the right target,
or that the interpretation built on top of the quote is sound. It closes the gap
between the panel and the literature. It does not close the gap between the
literature and reality.

**Passing checks are cache-assisted.** The reported runs show `network: 0` and
993 cache hits: they were answered from a seven-day SQLite cache of earlier live
calls. That is a legitimate mode — it is how the check stays runnable in CI
without hammering public APIs — but a fully cold, fully live verification is
`--no-cache`, and any claim of "verified live today" should be made only after
one. The cache is stale-tolerant on failure by design (§"what happens when a
database is down"), which is the right behaviour for research continuity and the
wrong behaviour for proving freshness.

**A blinded-rediscovery recall of 5/7 is a small sample.** Seven positives and
two negative controls is enough to demonstrate that the method is not vacuous
and not obviously leaking. It is not enough to estimate precision, to
characterise the miss rate, or to support any statement of the form "the engine
finds N% of repurposing opportunities". Two of the seven were missed, and the
reasons given are structural limits of shared-target evidence, not tuning
problems. Expect the rate to fall on a larger, less famous set, because the
seven positives are textbook cases with dense annotation.

**The repurposing score is ordinal and unvalidated as a magnitude.** It is a sum
of hand-chosen weights. The weights are published and arguable, which is better
than a black box, but nothing calibrates them against outcomes. The separation
observed between the best positive (6.30) and the best control (1.20) is one
observation on nine compounds, not an operating characteristic.

**`vina_like_score` is uncalibrated, and the port shares its reference's
assumptions.** Even granted a term-exact port, both implementations could be
wrong in the same way — that is precisely what a self-consistency test cannot
detect. The scores have not been compared against a real Vina installation, nor
against experimental affinities for any compound. Treat them as a way to order
candidates within one receptor and nothing more.

**Docking uses a seeded Monte Carlo sampler with few runs.** The run reported in
§3.4 kept 4 poses. Pose sampling this shallow finds a reasonable pose, not the
global optimum, and results will move with the seed. Neither receptor
flexibility nor explicit solvent is modelled.

**The structural scoring path is currently broken end to end** (§5, item 1). The
platform's strongest claim — that potency can be computed rather than asserted —
is demonstrable today only by calling the docking module directly, not through
the generator that is supposed to use it. It fails loudly rather than falling
back to constants, which is the correct failure, but it fails.

**Most fields in a generated compound record are still placeholders.** Safety,
selectivity, synthetic accessibility and the MD batch are hand-set constants.
`SyntheticValue` makes them visible; it does not make them informative. A reader
skimming a record will see numbers, and only the `[SYNTHETIC]` suffix and the
`provenance` field distinguish them from results. That marker survives `str`,
`repr`, `format` and arithmetic — but `float(x)` and a bare `json.dumps` strip
it, which is exactly why records also carry `provenance`. A downstream consumer
that casts to `float` and drops the record loses the warning.

**The compound inventory's provenance is documents, not a registry.** 1,336
unique structures were extracted from 16 source PDFs, 156 of them recovered by
shorthand repair. Repair is conservative and records every substitution, but an
OCR-and-repair pipeline over hand-written chemistry has an error rate that has
not been measured here. 23 strings carry ambiguous shorthand and were
deliberately left alone. None of these structures has a database identity: the
validation run shows an inventory compound matching no ChEMBL molecule at all,
which is the honest result and also a hard limit on what can be said about them.

**Panel breadth is narrow.** Five panels, 84 target records. Each is
well-verified. That is a different thing from broad coverage of any disease
area.

**The content store is local.** Content addressing gives you tamper-evidence
against accidental modification and a citable hash. It is not a notarisation, it
proves nothing about *when* an artefact existed, and a party who can rewrite the
store can rewrite the addresses with it.

**This repository has been wrong before, recently and badly.** §1 is the list.
The correct posture toward the present document is the one it argues for: do not
trust it, run the commands. Every figure above is reproducible in under a minute
with the commands in Appendix A, and any that is not should be treated as
deleted.

---

## Appendix A — Every quantitative claim and the command behind it

Every figure in the table below was re-measured on 6 October 2026 **except the
rows that need network access** — the `make citations` result, the 84 target
records, the seeded-failure count, the offline-run row and the PMID quotation
check. Those reach ClinicalTrials.gov, the RCSB, ChEMBL, UniProt and NCBI, which
this environment cannot, so they carry their last measured values and are marked
in the table. Saying "every figure" while five of them were carried forward is
precisely the drift this appendix exists to prevent, and it had happened here.

A figure that does not reproduce should be treated as deleted — that rule applies
to this document as much as to anything it describes, and several rows below are
corrections to numbers that had drifted since it was written.

| Claim | Command |
|---|---|
| 5 failed, 1469 passed, 55 skipped, 1 xfailed | `.venv/bin/python -m pytest tests/ -q` |
| the 5 failures all bind a local port | `.venv/bin/python -m pytest tests/test_server_lifecycle.py -q` |
| 227 JavaScript tests pass, 0 fail | `node --test tests/*.test.mjs` |
| 10,629 lines of test code | `cat tests/*.py tests/*.mjs \| wc -l` |
| 40 Python and 15 JavaScript test files | `ls tests/*.py \| wc -l; ls tests/*.mjs \| wc -l` |
| 86 modules import cleanly | `make imports` |
| 28 of 30 JS modules reachable from the app; 2 staged, 0 dead | `make reachable` |
| 27,438 lines of Python | `cat server/*.py scripts/*.py \| wc -l` |
| 30 JS modules | `ls js/*.js \| wc -l` |
| 11 live database endpoints | `grep -n "^PUBCHEM\|^EUTILS\|..." server/db_clients.py \| wc -l` |
| 250/354/207/190/263 checks passed; 1,264 total, 0 failures; 5 panels | `make citations` *carried forward — needs the network* |
| 84 target records checked | `grep -cE "^[A-Z][A-Z0-9]* - " <citations output>` *carried forward — needs the network* |
| 13 deliberate failures, non-zero exit | `.venv/bin/python scripts/verify_panel_citations.py --seed-bad` *carried forward — needs the network* |
| 0/204 checks pass with no network and no cache; exit 1 | `AGI_DB_OFFLINE=1 AGI_DB_CACHE=<empty> .venv/bin/python scripts/verify_panel_citations.py ALS` *carried forward — needs the network* |
| "completion rates **for**" is in PMID 30616998; "**of**" is not | `.venv/bin/python` + NCBI efetch of PMID 30616998 *carried forward — needs the network* |
| 13 port tests pass, tolerance 1e-9 | `.venv/bin/python -m pytest tests/test_vina_score_port.py -q` |
| old core C14H10, 3 rings; current core C16H10, 4 rings | `.venv/bin/python -c` + RDKit `CalcMolFormula` / `CalcNumRings` |
| acrylamide+urea → C20H14N2O2, MW 314.34, cLogP 4.44, 4 rings | same |
| 11 warheads; unknown warhead → `None` | `len(pyrene_structures.WARHEAD_SMILES)`; `ps.assemble('nosuchwarhead', None)` |
| vina_like_score −5.507; 5 terms; 24 heavy atoms, 3 rotatable bonds, 2 H-bonds, 4 poses; receptor 6O0K, 1200 atoms | `.venv/bin/python -c "PyreneVinaScorer().score_warheads('acrylamide','urea','BCL2')"` |
| SOST: 45 claimed historically vs 3 now | `git show f5e9a74:server/disease_panels.py` vs `server/disease_panels.py:223`; the 3 is confirmed by `make citations` |
| OLD generator: 20 requested, 1 unique warhead pair. NOW: 20 unique | `PyreneSeries3Generator.generate_series3_compounds('BCL2','pediatric_leukemia',20)` at `16628dc^` and at HEAD |
| repurposing recall 5/7 (71%); top-10 57%; best positive 6.30; best control 1.20 | `.venv/bin/python scripts/validate_repurposing_recall.py` |
| 1,336 unique structures from 16 files; 1,180 already valid, 156 repaired, 0 unfixable, 23 ambiguous | `.venv/bin/python -c` + `smiles_repair.repair_many` over `data/extracted_compound_inventory.json` |
| Vina and Open Babel absent | `which vina obabel` |
| old `server.py`: 29 `@app.route` decorators, `app` never defined, Flask absent, `NameError` on import | `git show 16628dc^:server/server.py`; `.venv/bin/python -c "import flask"`; import of the archived tree |
| structural path raises `AttributeError: 'DockingResult' object has no attribute 'smiles'` | `PyreneSeries3Generator(structural_scorer=PyreneVinaScorer()).generate_series3_compounds(...)` |

**One figure was not reproduced and has therefore been omitted from this
document:** the historical "58 routes" count for the dead API layer. The archived
`server/server.py` at `16628dc^` carries 29 `@app.route` decorators and 29
route-method pairs. The other properties of that layer — that `app` was never
defined, that Flask was not installed, and that the module raised `NameError` on
import — were all reproduced directly. The route count as stated could not be,
so it is not stated.
