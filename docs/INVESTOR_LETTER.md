# A letter to prospective investors

AGI Corp / AGI Future Foundation
23 September 2026

---

Dear reader,

I want to start with the thing most letters like this leave out, because if you
are going to stop reading it should be now rather than three pages in.

**Nothing this platform has produced is a drug.** No compound in our repository
has been synthesised. None has been assayed, put into a cell, or given to an
animal or a person. This is pre-clinical research tooling — software that
triages hypotheses and checks whether claimed facts are still true. We make no
claim, and will make no claim, about the efficacy of any compound in any disease.

I am also not going to tell you the market is worth some number of billions. We
have not sourced a defensible figure for the segment we actually occupy, and the
large pharmaceutical-R&D totals that get quoted in decks are not a market we
address. **Our addressable market is, at present, unquantified.** If we cite a
number later, it will come with its source.

And I am not asking you for a specific amount in this letter. When there is a
figure, it will be a considered one attached to a plan, not a round number
chosen to sound serious.

What I have instead is a story about a week, and I think it is a better thing to
own than any of the above.

---

## What happened

Days before I wrote this, our own codebase was audited against its own
documentation. The audit was not kind, and it was not supposed to be. What it
found:

An HTTP API that our documentation called production ready raised `NameError` on
import. It had never executed, not once. A compound generator asked for twenty
molecules returned twenty copies of one, so the optimisation loop reading from
it had been searching a population of size one. Docking, molecular dynamics and
ADMET scores were `random()` sitting behind a label that read "AutoDock Vina
integration", on a machine where Vina had never been installed. A load-testing
harness benchmarked `asyncio.sleep` — its throughput figure measured how fast
Python sleeps. A compound series documented across eleven files as a four-ring
pyrene platform was built on phenanthrene, which has three rings and two fewer
carbons; and the warheads were never chemically attached, so every compound was
a label rather than a molecule. Target panels carried invented structure counts:
one gene credited with 45 protein structures had 3, and three genes credited
with 8 to 15 had none at all. Authentication accepted any password, including
the empty string, on servers bound to every network interface. And there was no
test suite of any kind.

Some of that material had been attached to claims — improved response rates,
dosing guidance — for compounds that did not have a molecular structure. That
material has been deleted. It is not being revised, softened or restated
somewhere else. It was wrong and it is gone.

I am telling you this because you would find it, and because the only version of
this company worth funding is the one that tells you first.

---

## What we did about it

We rebuilt, and we built the mechanism that makes the rebuild checkable.

The platform now runs 763 passing tests. Every module under `server/` and
`scripts/` — 66 of them — is checked for clean import on every push, which is
the single check that would have caught the dead API, a missing type import and
an undeclared dependency all at once.

More importantly, we built a verifier that re-resolves every factual claim in
our target panels against the live public databases they came from. For each of
84 target records it asks UniProt whether the accession still names that gene,
asks RCSB whether each cited structure exists and whether our structure count
matches theirs, asks AlphaFold whether the model id is right — and where we
claim there is no model, whether there is still none. It asks ChEMBL whether the
target carries the accession and whether our ligand counts hold at the stated
potency threshold, including where we claim zero. It asks ClinicalTrials.gov
whether each cited study still lists children among its eligible ages. And it
asks PubMed whether every sentence we quote is still, character for character, in
the abstract.

That is 1,264 checks. They pass. You can run them yourself in a few minutes;
the command is `make citations`.

Two details tell you more about how this works than the count does.

**The first.** Our longevity panel quoted a senolytics trial as reporting
"completion rates *of* planned clinical assessments". The paper says "*for*".
One preposition. The meaning was unchanged, and the quote was being used
correctly — to argue that the trial measured feasibility rather than efficacy,
which is the sceptical reading and the right one. The verifier does an exact
substring match against the live abstract, so it failed, and we fixed the panel.

I find that more reassuring than the 1,264. A check loose enough to forgive a
changed preposition is loose enough to forgive a changed number, and a human
reviewer reading for sense would have let it through. We would rather be
annoyed by a strict check than trusted by a lenient one.

**The second.** We have no AutoDock Vina installed, so rather than pretend, we
ported the Vina scoring function from our own reviewed JavaScript
implementation into Python. A scoring function ported silently wrong is the
worst kind of bug, because the output is still a plausible number that no amount
of inspection reveals as wrong. So the test does not assert that the port is
correct. It runs both implementations over the same crystallographic receptor
geometry and the same ligand, and compares every one of the five interaction
terms, the atom typing behind each term, the rotatable-bond count and the
hydrogen-bond list, to a tolerance of one part in a billion. A silently-wrong
port fails.

And we do not call the output a binding energy. We call it `vina_like_score`,
it has no units, it is not kcal/mol, and it is not comparable between receptors.
It orders candidates within one pocket. That is what it does, so that is what it
is called.

---

## The thing I would actually want you to look at

Anyone can write a document claiming rigour. What we built is a way for numbers
that have no computation behind them to announce themselves.

Placeholder values in this system are not comments saying "TODO". They are a
distinct type. A placeholder prints with a `[SYNTHETIC]` marker in every textual
form, the marker survives arithmetic, the first one constructed in a process
raises a warning, and the record containing it carries a field naming exactly
which of its values are placeholders. Safety scores, selectivity, synthetic
accessibility and our "molecular dynamics" outputs are all still placeholders
today, and every one of them says so on sight. To publish a fabricated figure
from this platform you would now have to strip the marker deliberately.

Where a real computation cannot be performed, the code raises rather than
substituting a constant. There is a broken call path in our repository right
now for precisely that reason — the structural scoring route from the compound
generator fails on a field-name mismatch. It is at the top of our roadmap and it
is documented in our white paper. I mention it here because a platform that
fails loudly will always have visible breakage, and a platform that falls back
quietly will look flawless. I know which one I would fund.

---

## What we are not claiming

Let me be exhaustive, because the alternative is being selective.

We do not produce binding free energies — the score is unitless and
uncalibrated. We do not run molecular dynamics. We do not predict ADMET, safety,
selectivity or synthetic accessibility; those are placeholders. We do not
compute doses of any kind, and specifically we do not compute paediatric doses:
there is no allometric scaling and no adult-to-child extrapolation anywhere in
the system, because dose selection needs pharmacokinetic modelling we do not
have. We do not assert drug combinations or synergy — the code returns them as
questions. We do not anchor anything on a blockchain. We have no validated
throughput or load benchmark, and any such figure from our own harness would be
measuring `sleep`. We have never synthesised or tested a compound. We make no
efficacy claim about anything, for any disease, now or in this letter's future.

Our validation of the repurposing engine recovered five of seven known cases
under blinding. Two were missed, and we report why: in both cases the second
indication simply is not reachable from shared-target evidence. Seven positives
is a small sample. It shows the method is not vacuous. It does not support a
percentage claim about real-world discovery, and we will not make one.

Our coverage is five disease panels and 84 target records. Each is
well-verified. That is not the same as breadth, and I do not want 1,264 passing
checks read as breadth.

**On the disease areas we work in:** the panels were assembled around
neurodegenerative disease, paediatric oncology, paediatric skeletal and
orthopaedic conditions, movement disorders and ageing biology. We have built
toward the same research goals that the foundations and hospitals in these
fields pursue. **We have no agreement, partnership, sponsorship or affiliation
with any such organisation, and nothing here should be read as implying one.**
Where an internal panel identifier in our source carries an institution's
informal name, it is a label for a set of genes and nothing more.

**On intellectual property:** our licence is proprietary — no rights are granted
except by separate written agreement. But it is a software licence, and it
covers software: code, documentation, data files, panels and research outputs.
It does not and cannot cover compound intellectual property. Rights in a
chemical entity are a patent matter, determined by filings and prior art. Any
diligence on compound IP has to be done as patent diligence, and we are not
representing otherwise.

---

## Why this is the better story

The version of this letter I could have written a fortnight ago would have had a
market size, a funding ask, a percentage improvement in response rates and a
paediatric dosing table. Every one of those numbers would have rested on
compounds that did not exist, with binding energies from a random number
generator. Some of it would also have been unlawful to send you.

What I have instead is a platform that found its own worst claims and deleted
them, and that now cannot easily reacquire them — because the placeholders
announce themselves, the citations re-resolve against live sources, the ported
physics is checked term by term against its reference, and the whole thing runs
from a single command that a stranger can execute.

That is a smaller story. It is also one where every sentence survives being
checked, which is the only property that compounds over time. A company whose
claims only ever shrink under scrutiny is worth less this quarter and more in
five years than one whose claims do not.

If you want to go further: read `docs/WHITE_PAPER.md`, which states every figure
alongside the command that produced it and devotes its longest section to the
platform's limitations. Read `docs/QA.md`, which answers the uncomfortable
questions directly, including why you should not take our word for any of this.
Then run `make test`, `make verify` and `make citations` yourself. They take
minutes. If anything fails to reproduce, that is a finding, and we would want it
from you.

Thank you for reading this far.

Sincerely,

AGI Corp / AGI Future Foundation

---

*This letter is provided for information only. It is not an offer to sell or a
solicitation of an offer to buy any security, and it contains no forward-looking
statement regarding the efficacy, safety, regulatory status or commercial
prospects of any compound or product. The platform described is pre-clinical
research software. No compound described in it has been synthesised or tested in
any biological system. Values marked `[SYNTHETIC]` are placeholders produced by
no measurement or model and must not be read as results. The software licence is
proprietary and does not convey rights in compound intellectual property, which
is governed by patent law.*
