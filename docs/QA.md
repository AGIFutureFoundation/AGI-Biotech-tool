# AGI BioXR — Questions and Answers

For sceptical scientists and technical due-diligence readers. The companion to
`docs/WHITE_PAPER.md`; where a figure appears here, that document's Appendix A
names the command that produced it.

Throughout: this is **pre-clinical research tooling**. No compound has been
synthesised or tested in any biological system, and nothing here is a
therapeutic claim.

---

## About trusting the platform at all

### Your own documentation was wrong last week. Why should I believe this?

You shouldn't, on my say-so. That is the honest answer and it is also the design
principle.

Here is what was wrong, days ago, in this repository: an HTTP API documented as
production ready that raised `NameError` on import and had never executed; a
compound generator returning twenty copies of one molecule when asked for
twenty; docking, MD and ADMET drawn from `random()` behind an "AutoDock Vina
integration" label on a machine with no Vina; a load-test harness that measured
`asyncio.sleep`; a "pyrene" series built on phenanthrene with warheads never
chemically attached; target panels with invented structure counts, one gene
credited with 45 PDB entries against 3 real ones; authentication that accepted
the empty string as a password; and no test suite.

That list is not a confession appended for candour. It is the specification for
what changed. Each item now has a check that fails if it returns:

| What was wrong | What catches it now |
|---|---|
| API never executed | `make imports` — 66 modules, parametrised import test |
| 20 identical molecules | uniqueness assertions in `tests/test_pyrene_discovery.py` |
| `random()` behind a Vina label | `SyntheticValue` — every placeholder prints `[SYNTHETIC]` |
| Invented PDB counts | `make citations` — 1,264 live re-resolutions |
| Phenanthrene labelled pyrene | RDKit tests pinning C16H10 / 4 rings, *and* pinning that the old core was phenanthrene so the bug cannot return quietly |
| Empty password accepted | scrypt with per-user salt, constant-time compare, fail-closed |
| No test suite | 763 passing tests |

The right posture is to run the commands. `make test` takes eighteen seconds.
`make citations` takes a few minutes and hits the live databases. If a figure in
our documents does not reproduce, it is wrong and we want to know.

One thing I would add: notice which direction the corrections went. Every one
made a claim *smaller*. SOST went from 45 structures to 3. "Binding energy in
kcal/mol" became "unitless relative ranking". A documented throughput number was
withdrawn entirely rather than re-measured. A platform that only ever revises
upward is telling you something about its process.

### What stops this from happening again in six months?

Three things, in descending order of how much I trust them.

**Machine checks that run without anyone remembering to run them.** `make
verify` (tests + imports + JS reachability) runs on every push in CI, offline
and deterministic. `make citations` runs weekly on a schedule against the live
databases — deliberately *not* on every push, because a single run is roughly
210 HTTPS requests against services that throttle unauthenticated clients, and
because an upstream 503 reddening an unrelated pull request produces a build
everyone learns to ignore.

**Provenance enforced at the type level.** A placeholder is not a comment
saying "TODO". It is a `SyntheticValue`, a float subclass whose `str`, `repr` and
`format` all carry a `[SYNTHETIC]` suffix, which propagates through arithmetic,
which raises a runtime warning the first time one is constructed in a process,
and which causes the record containing it to carry a `provenance` field naming
the specific placeholder fields. To publish a fabricated number you now have to
strip the marker on purpose.

**Failing loudly rather than falling back.** Where a real computation cannot be
performed, the code raises. The structural scorer will not substitute a constant
for a docking score, because a silent fallback is indistinguishable from a
result. There is a broken call path in the repository right now for exactly this
reason (see below) — it raises instead of quietly producing numbers, which is
the failure mode I want.

That third one is a discipline, not a mechanism, and disciplines erode. The
roadmap's second item is putting the structural path under test so it doesn't
have to be a discipline.

---

## About the data

### How do I know your target data is right?

Run `make citations`. It re-resolves every identifier in all five disease panels
against the live source and fails on anything that doesn't check out.

Specifically, for each of 84 target records it asserts: the UniProt accession
resolves and its gene names include the panel's symbol; each cited PDB entry
appears in the RCSB search for that accession, and the panel's structure count
equals the live count; the AlphaFold model id matches — and where the panel says
there is no model, there must still be none; the ChEMBL target exists and its
components carry the accession, and where the panel asserts no single-protein
target, ChEMBL must still have none; the count of potent ligands at pChEMBL ≥ 6
is not below the claim, including where the claim is zero; each named drug still
has a curated mechanism pointing at that target; each NCT number still lists
`CHILD` in its standard ages; and every quoted sentence is still a verbatim
substring of the live PubMed abstract.

Current state: 1,264 checks across five panels, zero failures.

Note the two-sided assertions. Checking that a claimed 45 structures is not
*more* than the live count is what would have caught the historical SOST bug.
Checking that a claimed *zero* is still zero is what catches the opposite error —
a panel that says "no chemical matter here" when chemical matter has since
appeared.

### A passing verifier proves nothing if it can't fail. Can it?

Yes, and you can watch it:

```
$ .venv/bin/python scripts/verify_panel_citations.py --seed-bad
```

This injects a control target whose every identifier is deliberately wrong,
including a real PMID paired with a sentence that is not in its abstract. It
produces 13 failures and exits non-zero. Run it before trusting a passing run.

More persuasively, it has failed on real data. The longevity panel quoted a
senolytics trial as reporting "completion rates **of** planned clinical
assessments". The paper says "**for**". One preposition, in a sentence whose
meaning was entirely unchanged, in a quote that was being used *correctly* — to
argue that the trial's primary endpoints were feasibility, not efficacy. The
verbatim substring check failed and the panel was corrected.

I keep returning to this because it is the whole argument in one incident. A
paraphrase-tolerant check passes that sentence. A careful human reviewer reading
for sense passes it. Only an exact-match check against the live abstract fails
it. And if the check is loose enough to accept a changed preposition, it is
loose enough to accept a changed number.

### What happens when a database is down?

Two different things, on purpose, depending on what you are doing.

**In research paths** (`server/db_clients.py`), failures never raise. A function
returns `{"error": ...}` alongside empty result fields and the run continues.
There is a per-host circuit breaker so an offline run fails fast rather than
waiting out every timeout, retries with backoff on 429 and 5xx honouring
`Retry-After`, and a seven-day SQLite response cache. On failure the cache is
consulted *stale-tolerantly* — a week-old answer beats no answer when you are
triaging a hypothesis.

**In the verifier**, the opposite. A network error is a failure. The script says
so in its own docstring: a citation that cannot be checked has not been verified.
Prove it yourself by pointing it at an empty cache with the network forbidden:

```
$ AGI_DB_OFFLINE=1 AGI_DB_CACHE=/tmp/empty.sqlite \
  .venv/bin/python scripts/verify_panel_citations.py ALS
0/204 checks passed
204 FAILED
exit 1
```

Zero passes. Not "204 skipped", not "assumed valid". The output distinguishes
`did not resolve` from `unverified: no RCSB answer`, so you can tell a wrong
citation from an unreachable one, and both are failures.

### Is `make citations` hitting the network or the cache?

Honest answer: the runs reported in our documents show `network: 0` and 993
cache hits. They were answered from the seven-day cache of earlier live calls.
That is legitimate for routine verification and it is how the check stays
runnable without hammering public APIs — but it is not proof of freshness.

For a cold, fully live run, pass `--no-cache`. Any claim of the form "verified
live today" should be made only after one, and we try to say which we mean.

### Where do the compounds come from, and can I trust the structures?

1,336 unique structures extracted from 16 source PDFs. 1,180 parsed as written;
156 were recovered by shorthand repair; 0 were unfixable; 23 carry ambiguous
shorthand and were deliberately left alone.

Repair is deliberately conservative, under two rules. A string that already
parses is never touched — `C(CN)` is valid SMILES meaning carbon-nitrogen even
when the author almost certainly meant a nitrile, so rewriting it would silently
change the molecule; those are reported as ambiguous. And a repair is accepted
only when the original failed to parse *and* the result parses, with every
substitution recorded in the compound's record.

What I cannot tell you: the error rate of an OCR-and-repair pipeline over
hand-written chemistry has not been measured here. And none of these structures
has a database identity — the repurposing validation run includes an inventory
compound as a negative control precisely because it matches no ChEMBL molecule
at all. That is the honest result and it is a hard limit on what can be said
about them.

---

## About the science

### Is `vina_like_score` a binding affinity?

No, and the naming is deliberate.

It is a relative ranking computed from real 3D coordinates using the AutoDock
Vina functional form (Trott & Olson 2010) with Vina's published weights. Those
weights were fitted against a complete Vina pipeline — its own atom typing,
desolvation handling, conformer treatment and optimiser. Reusing the weights
without that pipeline reproduces the functional form, not the calibration.

So: **no units**. Not kcal/mol. Not a *K*d. Not comparable across receptors. It
orders candidates within one pocket. `js/dock.js`, the reference implementation,
says of itself that it is not a validated replacement for Vina or Glide, and the
Python port inherits that statement verbatim.

If you see "kcal/mol" anywhere near one of these numbers, it is a bug and we
want the report.

### You ported a scoring function. How do I know the port is correct?

You know it agrees with its reference to 1e-9, and you know nothing beyond that.

`tests/test_vina_score_port.py` does not assert that the port is correct — an
assertion against hand-computed expected values would just encode someone's
arithmetic. It runs the JavaScript implementation and the Python implementation
over the *same* crystallographic receptor geometry (chain A of PDB 6O0K, BCL-2
with venetoclax) and the *same* ligand molblock, and compares every one of the
five Vina terms, the atom typing behind each term, the rotatable-bond count and
the H-bond list. Both sides hold coordinates as float32 and reduce in double
precision, so the only legitimate difference is summation order; the tolerance
is 1e-9 and anything larger is a real divergence, not noise.

This is the right test because the dangerous failure is a port that is silently
wrong — the output is still a plausible number, and no amount of staring at it
reveals the problem. A term-by-term comparison catches a transposed weight, a
wrong cutoff, a mistyped atom.

What it explicitly does not catch: both implementations being wrong in the same
way. That is the structural limit of any self-consistency test. Comparison
against a real Vina installation on a standard benchmark set is on the roadmap
and has not been done.

### Why not just install AutoDock Vina?

Fair question, and the answer is a trade-off rather than a principle. Vina and
Open Babel are not installed — `which vina obabel` finds nothing — and before
the port there was no Python docking at all, only the browser implementation.
Porting keeps one source of truth for the terms and weights and adds no system
dependency, at the cost of the calibration question above. Installing Vina would
give a calibrated score and an independent check on the port. It should happen.

### Have any of these compounds been made or tested?

No. None. Not one compound in this repository has been synthesised, assayed, or
put into any biological system.

Substitution regiochemistry is stated as a plausible enumeration, not a claim
about synthetic outcome. Synthetic accessibility scores are placeholders —
literally `SyntheticValue` constants that print `[SYNTHETIC]`. The compounds are
now genuine molecules in the sense that they have structures RDKit will accept
and conformers a docking routine will score. They are not molecules in the sense
that anyone has held one.

### What is actually computed versus placeholder?

Computed from real data: target panel facts (re-resolved against live
databases); repurposing hypotheses and scores (traced to ChEMBL, Open Targets,
Reactome, STRING, ClinicalTrials.gov records); molecular structures and
descriptors (RDKit over assembled molecules); `vina_like_score` and its five
terms (from coordinates); content hashes and Merkle roots.

Placeholder, emitted as `SyntheticValue`: predicted potency in the default
heuristic mode; paediatric safety score; selectivity score; synthetic
accessibility; the entire "MD" batch.

The way to tell them apart is not to consult a table. It is to look at the
value. A placeholder prints `[SYNTHETIC]`, and its record's `provenance` field
names it. The one gap: `float(x)` and a bare `json.dumps` of a naked value strip
the marker, which is exactly why records also carry `provenance`. A downstream
consumer that casts to float and discards the record loses the warning — worth
knowing if you are integrating.

### Your repurposing engine recovered 5 of 7. Isn't that weak?

It is a small sample and I would not build a claim on it. Seven positives and
two negative controls is enough to show the method is not vacuous and not
obviously leaking its answer; it is not enough to estimate precision or to
support any statement of the form "finds N% of repurposing opportunities".
Expect the rate to fall on a larger, less famous set — these seven are textbook
cases with unusually dense annotation.

What I would point at instead is the *shape* of the result. The validation
blinds the engine to the known second indication and excludes the compound from
its own evidence. Thalidomide and dimethyl fumarate come back rank 1;
sildenafil and raloxifene rank 3 of 169 and 61. Negative controls separate:
mannitol tops out at 1.20 against a best positive of 6.30, and an inventory
compound with no database identity yields nothing at all.

And the two misses are reported with mechanistic reasons rather than buried.
Minoxidil's targets have precedent drugs, but none with a registered clinical
record in alopecia — so that indication is simply not reachable from
shared-target evidence. Metformin's resolved target has no *other* drug with a
clinical record against it, so with metformin excluded there is no precedent to
transfer. Those are statements about the reach of the method, which is more
useful to you than the headline number.

### What does the repurposing score mean numerically?

Ordinal, nothing more. It is the sum of its listed terms after per-join caps.
There is no hidden model and no learned weight; the entire scheme is emitted
with every report so you can disagree with a weight and re-add the terms by
hand. It is not a probability and not an effect size, and a 6.0 is not "twice as
likely" as a 3.0. Its only job is to order a worklist.

Nothing calibrates the weights against outcomes. The separation between best
positive and best control is one observation on nine compounds, not an operating
characteristic.

### Does the platform calculate doses?

No, and this is enforced in code rather than promised in prose. Nothing
multiplies, scales, extrapolates or allometrically converts a dose. Nothing
infers a paediatric dose from an adult one. `documented_doses()` retrieves dose
text verbatim from ClinicalTrials.gov records and attaches the NCT id it came
from — retrieval, not calculation.

Dose selection needs PK/PD modelling this platform does not have. An age-scaled
paediatric dosing table for unsynthesised compounds is precisely the kind of
artefact this codebase spent its history removing.

### Does it assert drug combinations or synergy?

No. `cotarget_flags()` returns questions and says so in every record it emits.
Two compounds hitting complementary targets is a reason to run an experiment.
Synergy, antagonism and shared toxicity cannot be read off target annotations.

---

## About the engineering

### One of your tests is marked xfail. What's broken?

Nothing, in the code. `series_3` advertises an `isothiazole` warhead that the
warhead library has no entry for. Closing that gap means either dropping a
documented warhead or inventing its potency, paediatric-safety and
selectivity-risk constants — and fabricating paediatric safety numbers is not
acceptable. So the test stays failing, marked `strict=True`, which means it will
alert if someone ever supplies real values and the gap closes.

It is a data gap held open deliberately, in public, rather than papered over
with plausible constants. That is the same decision as everything else here.

### Is anything currently broken?

Yes, and it is in the white paper's roadmap as the highest-value fix.

`PyreneSeries3Generator` constructed with a `structural_scorer` raises
`AttributeError: 'DockingResult' object has no attribute 'smiles'` —
`_structural_score` reads a field the dataclass does not define. The docking
module works correctly when called directly; only the generator's wire-up is
broken. Until it is fixed, generated compounds carry heuristic `[SYNTHETIC]`
potency and no SMILES.

I would rather you heard this from us. Two observations. It fails loudly instead
of falling back to constants — which is the correct failure, and was an explicit
design choice in that function, with a comment saying so. And it is exactly the
class of bug that `make imports` catches for imports and that nothing currently
catches for call paths, which is why "put the structural path under test" sits
directly beneath "fix it" on the roadmap.

### How do you handle secrets and authentication?

Authentication previously took a password argument and never looked at it: any
known email returned a valid JWT carrying that user's role, and the empty string
worked as well as anything else. Verified before fixing — `'correct-horse'`,
`'wrong'` and `''` all issued a token.

Now: `hashlib.scrypt` (memory-hard, standard library, since bcrypt and argon2
are not installed and this project stays with the stdlib where it can), a
per-user random salt, constant-time comparison. An account with no password set
cannot authenticate at all, so a half-built account fails closed. An unknown
email still pays the hashing cost, so it cannot be distinguished from a wrong
password by timing.

A JWT signing key was previously committed to the repository; it was removed.
`JWT_SECRET` now comes from the environment, and if it is unset the process
generates a random key and warns that tokens will not survive a restart or
validate across workers.

Both servers default to binding `127.0.0.1`. Reaching a headset over Wi-Fi
requires passing `--host 0.0.0.0` deliberately.

### Do you have a throughput or load benchmark?

No, and please do not accept one from us.

`server/load_testing.py` simulates workflow steps with
`asyncio.sleep(random.uniform(...))`. Any operations-per-second figure it prints
measures how fast Python sleeps, which is why a historical "596 ops/second"
appears in no current document. The module is not run by `make verify` and its
output should be treated as unbuilt. Replacing or deleting it is on the roadmap —
a harness that measures `sleep` is worse than no harness, because it produces a
number and numbers get quoted.

### What does the content-addressed store actually give me?

Tamper-evidence and a citable reference. An artefact is stored under the
SHA-256 of its bytes, so the address *is* the integrity proof: asking for a hash
can only return content that hashes to it. A Merkle root reduces a whole run to
32 bytes, and an inclusion proof shows a given artefact was under that root.

What it is not: nothing is broadcast, no consensus is involved, and nothing is
anchored anywhere. It produces a root you *could* anchor on-chain; anchoring is
a separate, deliberate act with a cost, and the module does not do it or pretend
to. It proves nothing about *when* an artefact existed, and a party who can
rewrite the store can rewrite the addresses with it.

### Why is CI split into two workflows?

`ci.yml` is the merge gate: `make verify` — pytest, the per-module import test,
the JS reachability check. Everything in it is offline and deterministic, Python
3.12 only, deliberately no version matrix.

`citations.yml` runs the live check weekly, on Mondays at 06:17 UTC (off the
hour on purpose; scheduled runs cluster at :00 and get delayed under load). It
is separate because a single run is roughly 210 HTTPS requests against services
that ask you not to do that from one IP, and because the script treats a network
error as a failure — correct for a weekly audit, wrong for a merge gate. A red
build that everyone learns to ignore is worse than no build. The structural half
of the citation check — that evidence records exist and are shaped correctly —
runs offline on every push as part of `make verify`.

### Why does everything insist on `.venv/bin/python`?

Because the system Python has neither RDKit nor pytest, and several modules
degrade quietly when an import fails. Running a check with the wrong interpreter
produces a passing run that proves nothing — which is a compact description of
this repository's entire historical failure mode. The Makefile hardcodes
`PY := .venv/bin/python` and CI builds that exact path rather than using the
runner's bare Python.

---

## About scope and licensing

### What is the licence?

Proprietary. No licence, express or implied, is granted except under a separate
written agreement. Viewing the repository, or a hosting platform making it
accessible, grants nothing.

Important scope note: the licence covers the *software* — code, documentation,
data files, target panels and research outputs. It does not and cannot cover
compound intellectual property. Rights in a chemical entity are a patent matter,
governed by filings and prior art, not by a software licence.

### Is this a product?

It is pre-clinical research tooling. It triages hypotheses, verifies that
claimed facts still hold against live public databases, assembles and scores
molecules for relative ranking, and refuses to generate the numbers it cannot
compute. It does not make, test, dose or treat anything.

### How narrow is the coverage, really?

Five disease panels, 84 target records. Each is well-verified; that is a
different thing from broad coverage of any disease area, and I would not want
"1,264 passing checks" to be read as breadth. Structural scoring additionally
needs a curated receptor and pocket definition per target, and today that
curation is narrower still — the scorer raises rather than falling back when it
is missing.

### What would change your mind about this platform?

A cold `--no-cache` citation run that fails on something substantive. A
comparison against a real Vina installation showing the port's ranking does not
track. A larger repurposing validation set where recall collapses. Any of those
would be findings we would publish, because a platform whose argument is "run
the commands" does not get to be selective about which runs it reports.
