# Inspiration Layer — Three Bio Patents

**Staging only — local file. Do NOT publish, push, deploy, email, or share.**
**Research date: 7 November 2026.**
**Purpose:** the inspiration layer for the bio research expansion program. Each section below is a
standalone merge block for one subpage brief. The coordinator merges each section into its target
brief after the parallel brief workers land. **Do not edit any brief file from here — merge only
via the coordinator.**

## Honesty frame (governs every line below)

- **Hypothesis + design + falsification test, nothing more.** Every inspired direction is a
  **proposal for an experiment that has not been run**. No direction below is a discovery, a
  treatment, a cure, a diagnosis, a medical device, or a result — ours or anyone else's.
- **"Inspired by [patent]" is a label, not a claim.** Each direction is labelled with the patent
  that suggested it. An inspired direction is **never** the patent's claim, **never** the patent's
  data, and **never** our result. Where a direction borrows a patent's reported number, the number
  is attributed to the patent and carries the patent's own caveats.
- **Patent vs paper, predicted vs demonstrated — absolute.** A patent is a legal document with
  patent-reported data, not a peer-reviewed paper and not clinical evidence. An application
  publication (MENA) is not a granted patent. A computational-model prediction is not a wet-lab
  result. Nothing in this file upgrades any of those.
- **Every direction is falsifiable.** Each carries an explicit falsification test: the result
  that would kill it. If a direction cannot state what would kill it, it is not in this file.
- **Legal status is NOT verified in this file.** No freedom-to-operate conclusion may be drawn
  from anything here. Counsel must check each patent's live register status before any use.

## Evidence grades used in this file

| Grade | Meaning |
|---|---|
| **A — patent-reported** | Stated in the source patent document itself. Still patent-reported, not independently verified, not clinical. |
| **B — published, verified** | Published peer-reviewed or regulatory source, independently checked in a prior brief. Cited with its verification note. |
| **C — hypothesis, no data** | A new research question or design proposed here. No data exists for it. Every inspired direction in this file is Grade C by construction. |

## Sources read for this file

| # | Source | What it supports |
|---|---|---|
| 1 | `~/workspace/user/files/A_new_therapeutic_approach_to_treat_Alzheimer_s_disease.pdf` — Pharnext JP6062995B2 (61 pp., Google Patents printout, machine-translated from Japanese) | Section 1 core mechanism + all Alzheimer's numbers |
| 2 | `~/workspace/your_files/bio-research-expansion/brief-alzheimers.md` (read-only, for context) | Section 1 framing, caveats, cross-checks (Tables 2–5 illegible; JP lapse unverified live; six-combo pattern) |
| 3 | `~/workspace/user/files/Toxicity_typing_using_liver_stem_cells.pdf` — Snodgrass US 8,512,957 B2 (28 pp., read in full from rendered pages) | Section 2 core mechanism + all toxicity-screening details |
| 4 | `~/workspace/user/files/frank_gerter.pdf` — Condeelis et al. US 2022/0251662 A1 (25 pp., text-extracted in full) | Section 3 core mechanism + all MENA numbers |
| 5 | `~/workspace/your_files/bio-research-expansion/brief-cancer-dao.md` (read-only, for context) | Section 3 framing: Cancer DAO is a proposed programme (world + focus domain only); BCL-2 / Akt-Bad / BH3 context; AGI-183 identity tension |
| 6 | `~/workspace/your_files/bio-research-expansion/brief-als.md` + `compound-agi183.md` (read-only, for grounding) | Library reality check (§2) and the AGI-183 / CRBN identity tension (§1) |

---

# Section 1 — Alzheimer's: the three-network combination idea

**MERGE TARGET: `brief-alzheimers.md` (add as an inspiration section; do not alter the brief's
existing sections).**
**Inspired by: Pharnext JP6062995B2 — "A new therapeutic approach to treat Alzheimer's disease"
(Cohen, Chumakov, Nabirotchkin; assignee Pharnext SA; granted 2017-01-18; printout status
"Expired-Fee Related", anticipated expiration 2030-10-29 — live JPO register status NOT verified,
see brief-alzheimers.md §1.2).**

## 1.0 Core mechanism (the idea, faithful to the source)

The patent's idea is **repurposed-drug combination therapy aimed at three functional networks at
once, at sub-therapeutic doses**. The inventors data-mined Alzheimer's cell biology, expression
profiling, and genetics, selected genes by proximity to familial-AD genes (APP, ApoE, presenilin,
tau), and organised the result into three networks: **(1) synaptic function** — postsynaptic
density proteins (DLG2/PSD95), presynaptic release machinery (voltage-gated calcium channels,
MaxiK/BK channels, PRKG kinases, vesicle proteins STX2, BIN1, RAB3B, UNC13C, RIMS1/2), and axon
guidance converging on small GTPases (RhoA, Rac1, Cdc42); **(2) angiogenesis** — VEGFR1, ErbB4,
Notch, DCC, CD44, ephrin receptors, the AMPK signalling network, and the phospholipid growth-factor
axis (PA, LPA, S1P); **(3) cellular stress response** — calcium homeostasis (IP3R/ITPR1, RYR3,
SERCA3/ATP2A3, ATP2B1), protein folding/aggregation (APBA1/2, PARK2, **GSK-3β**), and apoptosis,
presented as primarily **p53-dependent** (WWOX, MDM1, HIPK2, PML; netrin-1 receptors UNC5C/DCC).

From a list of **40 already-known drugs**, the patent tests pairs in human brain microvascular
endothelial cells (HBMEC) exposed to aggregated human Aβ1-42 (2.5 µM, 18 h, capillary-network
length endpoint). Its evidentiary core — **Grade A, patent-reported, one in vitro assay only** —
is that **six two-drug combinations significantly blocked the >40% Aβ1-42 damage at concentrations
where each component alone had no significant effect** (ANOVA + Dunnett's, p < 0.05; 3 cultures,
6 wells per condition): sulfisoxazole + levosimendan; sulfisoxazole + terbinafine; baclofen +
levosimendan; terbinafine + aminocaproic acid; aminocaproic acid + levosimendan; terbinafine +
levosimendan. The patent reports **no formal synergy index** (no Bliss or Loewe score), so the
accurate wording is "singles-no-effect / combo-works pattern in the HBMEC assay" — never "synergy
proven." The same drugs were protective as singles at other (generally higher) doses, which is the
whole low-dose-combination rationale — and exactly why independent dose–response replication is
required. The patent's dose philosophy (patent-proposed, NOT clinical guidance) is each compound
at 1%–50%, most preferably 1%–10%, of its usual therapeutic dose. Its mouse protocol (Example IX,
BRI-Aβ42 mice) has **no readable outcome** — Table 5 was not legible — so no in vivo efficacy may
be claimed from this document. The patent's related-diseases definition includes ALS, Parkinson's,
and MS, but that is **claim scope, not evidence**: no data in the patent concern any disease other
than Alzheimer's models.

**What this mechanism suggests for us:** the design bet is orthogonal-mechanism pairing at low
dose, and the apoptosis arm (p53 → BAX/BCL-2 family → mitochondrial permeabilisation) is the same
biology our ALS program already works on (AGI-183 + AAV6-hSyn-MCL1 paper; Akt/Bad phosphorylation
as a proposed biomarker). The three directions below are built on that bridge — and on nothing
else.

## 1.1 Inspired direction — CRBN-recruited degradation of a three-network node, paired with a repurposed network drug

**Inspired by Pharnext JP6062995B2 (three-network model + low-dose combination logic).**

- **Hypothesis (Grade C — no data):** A CRBN-recruiting targeted degrader that removes a
  cellular-stress-response node protein (candidate node: GSK-3β, named by the patent as central to
  protein misfolding; or a p53-pathway activator from the patent's WWOX/MDM1/HIPK2/PML set) will
  protect human neurons from Aβ1-42 toxicity at a low dose **only when paired** with a repurposed
  network drug from a different network (candidate partner: levosimendan or baclofen, both in the
  patent's six-combo set), reproducing the patent's singles-no-effect / combo-works pattern in a
  neuronal system. The combination logic is the patent's; the degrader handle is new.
- **Grounding note — read before designing:** the CRBN handle here is a **mechanism class**
  (CRBN E3-ligase recruitment for targeted protein degradation). It is **NOT** the catalog
  compound that happens to be named AGI-183: the `AGI_Compound_001.pdf` catalog entry describes a
  CRBN-binding FLIP inhibitor that is **pro-apoptotic** (promotes extrinsic apoptosis in
  FLIP-dependent cancers) — the opposite direction from neuroprotection — and its identifier is in
  unresolved tension with the ALS paper's AGI-183 (a BCL-XL stabiliser, anti-apoptotic). See
  `compound-agi183.md` §5. **Do not name any catalog compound as the degrader candidate until
  that identity tension is resolved in writing.** The direction is valid as a mechanism-class
  proposal; no specific molecule is proposed here.
- **Experimental design:** (a) iPSC-derived human neurons exposed to aggregated human Aβ1-42
  oligomers (dose and exposure set by pilot, pre-registered); (b) full dose–response matrix for the
  degrader alone, the repurposed partner alone, and the pair, at sub-therapeutic-equivalent
  concentrations; (c) endpoints: neuronal survival / neurite-network length (same family of
  readouts as the patent's MAP-2/LDH assays), plus the shared apoptosis-axis panel from §1.3
  (Akt/pBad phosphorylation, BH3 profiling of mitochondrial priming, GSK-3β/tau phosphorylation);
  (d) formal synergy quantification (Bliss independence **and** Loewe additivity) with confidence
  intervals — the quantification the patent never performed; (e) a non-degrading CRBN-binder
  control and a degrader-dead (ligase-binding-deficient) control, to attribute any effect to
  degradation rather than to CRBN occupancy.
- **Falsification test:** the direction is killed if (i) the pair shows **no Bliss excess and no
  Loewe synergy** over the best single agent at any tested dose (i.e. the patent's pattern does not
  reproduce for this pair in neurons), **or** (ii) the degrader degrades its node (confirmed by
  protein measurement) yet neuronal protection does not change versus the partner alone (the node
  is not rate-limiting for this toxicity), **or** (iii) the degrader-dead control protects as well
  as the active degrader (the effect is not degradation-mediated). Any one of these kills it.
- **Evidence grade: C.** No data exist for this combination in any system.

## 1.2 Inspired direction — Replicate the patent's six-combo pattern in a second, neuronal system

**Inspired by Pharnext JP6062995B2 (the six-combo singles-no-effect / combo-works pattern,
Examples III–VIII, Figs. 8–13).**

- **Hypothesis (Grade C — no data):** At least one of the patent's six two-drug combinations
  reproduces its singles-no-effect / combo-works pattern outside the HBMEC endothelial assay —
  specifically in iPSC-derived human neurons exposed to Aβ1-42 oligomers, the ALS program's own
  neuronal platform. The patent's pattern is currently a **one-assay, one-cell-type** observation
  (Grade A in HBMEC only); this direction tests whether it is a property of the combinations or of
  the assay.
- **Experimental design:** Pre-registered replication of all six pairs (sulfisoxazole +
  levosimendan; sulfisoxazole + terbinafine; baclofen + levosimendan; terbinafine + aminocaproic
  acid; aminocaproic acid + levosimendan; terbinafine + levosimendan) in iPSC-derived human
  neurons + Aβ1-42 oligomers, with: full dose–response matrices for each single and each pair
  (not one concentration); the patent's matched-concentration singles-vs-combo contrast as the
  primary comparison; Bliss and Loewe quantification; the patent's positive-control logic (a known
  protectant, e.g. BDNF as in the patent's cortical-neuron assay) and vehicle/Aβ controls;
  pre-set success criterion (e.g. Bliss excess with confidence interval excluding zero, not just
  p < 0.05 vs Aβ). Compounds sourced as the named drugs at patent-proposed sub-therapeutic
  concentrations; phenformin is **excluded** from any replication set (restricted/withdrawn status
  in some markets — see brief-alzheimers.md §7.7) and no pair in the six contains it.
- **Falsification test:** the direction is killed if **none** of the six pairs reproduces a
  singles-no-effect / combo-works pattern with a positive Bliss/Loewe signal in the neuronal
  system — that outcome means the HBMEC pattern is assay- or cell-type-specific, and the
  generalisation to neurons is dropped. It is also killed for any individual pair whose singles
  are already protective at the tested concentrations (no low-dose window exists for that pair).
  A partial result (some pairs reproduce, others do not) narrows the direction to the reproducing
  pairs only; it does not rescue the rest.
- **Evidence grade: C** for the neuronal replication (no neuronal data exist). The HBMEC pattern
  itself remains **Grade A, patent-reported, HBMEC only**.

## 1.3 Inspired direction — A shared apoptosis-axis biomarker panel across the Alzheimer's and ALS programs

**Inspired by Pharnext JP6062995B2 (CSR apoptosis arm: p53-dependent apoptosis, BAD/BAX/BCL2 in
the target-gene list) read against the ALS paper (`als_4_8.pdf`: Akt/Bad phosphorylation as a
proposed predictive biomarker; BCL-XL/MCL1 control of mitochondrial outer-membrane
permeabilisation, MOMP).**

- **Hypothesis (Grade C — no data):** A combined pharmacodynamic readout panel — **Akt/pBad
  phosphorylation + BH3 profiling (mitochondrial priming) + GSK-3β/tau phosphorylation** — moves
  concordantly when a three-network combination protects neurons, and does **not** move when the
  combination fails to protect. If true, the panel becomes a cross-program asset shared by the
  Alzheimer's and ALS programs (both converge on "keep the mitochondrion from permeabilising");
  if false, the overlap was thematic and should be dropped. Note the asymmetry: the ALS paper uses
  Akt status to *stratify* response to BCL-2 therapy (a proposed predictive biomarker, itself
  unvalidated in neurodegeneration); the patent merely *lists* AKT as a network gene. This
  direction tests whether the shared panel has pharmacodynamic value — it does not assume the
  ALS paper's biomarker claim.
- **Experimental design:** Measure the three panel components in the replication assays of §1.2
  (and in the ALS program's own iPSC-derived TDP-43 motor-neuron assays, as a parallel arm):
  phospho-Akt (Ser473) and phospho-Bad (Ser99/136) by quantitative immunoblot; BH3 profiling by
  mitochondrial depolarisation in response to BH3-domain peptides (EC50 as the priming metric,
  as in the ALS paper); phospho-GSK-3β and phospho-tau as the misfolding-arm readout. Pre-register
  the expected direction of each component under protection, and the concordance criterion (all
  three moving in the pre-registered direction in protected conditions, none moving in
  unprotected conditions), before seeing data.
- **Falsification test:** the direction is killed if the panel **moves without protection** (it
  is not specific to the protective effect) **or fails to move when protection occurs** (it is not
  sensitive to it) in either program's assay. Either outcome means the panel is not a usable
  pharmacodynamic readout, and the cross-program overlap is recorded as thematic only. A panel
  that works in one program and not the other is kept for that program alone — no cross-program
  claim is made from a one-sided result.
- **Evidence grade: C.** The shared nodes (BAD/BAX/BCL2, AKT) are document-level facts in both
  sources; the panel's utility is an untested hypothesis. The ALS paper's Akt/Bad biomarker
  itself is a **prediction, not a validated biomarker** (preclinical oncology evidence only for
  pAKT S473 — see brief-cancer-dao.md §2 Strand C), and must not be cited as validated anywhere
  this panel is described.

---

# Section 2 — Toxicity screening: the liver-stem-cell molecular-profile idea

**MERGE TARGET: `brief-toxicity-screening.md` (add as an inspiration section; the brief itself is
being written by a parallel worker — this section merges after it lands).**
**Inspired by: Snodgrass US 8,512,957 B2 — "Toxicity typing using liver stem cells" (inventor
H. Ralph Snodgrass; assignee Vistagen Therapeutics, Inc.; granted Aug. 20, 2013; 25 claims, 4
drawing sheets. Filed Feb. 21, 2012 as a division of application 11/445,733 (filed Jun. 1, 2006,
now US 8,143,009), continuation of 09/881,526 (filed Jun. 14, 2001), provisional 60/211,606
(Jun. 14, 2000). Term and current in-force status NOT independently verified — do not assume
expired or in force from the grant date; a USPTO register check is required before any use.)**

## 2.0 Core mechanism (the idea, faithful to the source)

The patent's idea is **toxicity typing by molecular profile in a differentiating liver progenitor
system**. Isolated mammalian **liver stem cells (LSCs)** — pluripotent progenitor cells, preferably
hepatoblasts isolated from the embryonic hepatic diverticulum of the foregut (also isolable from
adult liver as stem-like cells), capable of differentiating into hepatocytes, bile-duct cells,
liver endothelial cells, and Ito cells — are exposed to a chemical composition, and the resulting
**alterations in gene expression or protein expression, relative to control LSCs grown in medium
only, are recorded as that composition's "molecular profile."** The readouts are gene-expression
arrays and, preferably, **mass spectrometry of proteins** (the patent's Figures 1–4 are mass-spec
protein profiles: small/large nuclear proteins and cytoplasmic proteins, test compositions I and
II vs control, with the differences between test and control isolated by subtractive quantitation).
The method's second half is a **reference library**: molecular profiles are compiled for
compositions **with predetermined toxicities** — the patent's Table 1 lists known drugs and
compounds by the tissues/organs in which they exert toxicity (liver, developmental, cardiovascular,
CNS, blood), including thalidomide, methotrexate, valproic acid, acetaminophen, isoniazid,
troglitazone, rosiglitazone, trovafloxacin, clozapine, doxorubicin, and cyclophosphamide, plus
environmental compounds (carbon tetrachloride, cadmium, lead, benzo(a)pyrene, methylmercury,
dioxins, PCBs). A test composition is **typed by comparing its profile to the library**: compounds
with similar toxicities share common alterations — some genes/proteins similarly up-regulated,
others similarly down-regulated — and those shared features become surrogate markers for assessing
the toxicity of a new or untested composition, and for ranking it among known toxic compositions.
The patent also claims: LSCs in array format; integrated systems (array reader + database of
profiles + correlation program, capable of reading more than 500 labels in an hour); dose
bracketing (normal/medium concentration bracketed by twofold or fivefold increases and decreases);
staging the exposure at different points of LSC differentiation; and species-matched controls
(mouse/rat preferred for preclinical correlation, primate/human most preferred for human relevance).
Its stated advantages over single-reporter cell lines, embryonic stem cells, and animal testing are
that LSCs are relatively easy to isolate and expand, avoid some ES-cell ethical/sourcing problems,
model a multi-lineage differentiating system rather than one cell type, and — because LSCs can be
isolated from live individuals (needle or small wedge biopsy) — could in principle support
individual-patient toxicity profiling. The test compositions in the patent's own figures are
**unnamed** ("Test Composition I" / "Test Composition II"), so no compound-specific result can be
quoted from this document.

**What this mechanism suggests for us:** a **pre-animal safety gate** for every compound set we
work with — profile first, rank against known-toxicity references, and only then decide what
deserves scarce animal or human-facing attention. The three directions below build that gate for
our actual compound sets.

## 2.1 Inspired direction — A toxicity-signature screen for the 40 repurposed Alzheimer's drugs (and their pairs)

**Inspired by Snodgrass US 8,512,957 B2 (molecular-profile library + typing by comparison).**

- **Hypothesis (Grade C — no data):** Each of the 40 repurposed drugs in the Pharnext patent —
  and each of the six two-drug combinations in §1.2 — produces a distinct LSC molecular profile,
  and any profile that **clusters with the reference set of known hepatotoxic compounds** (e.g.
  troglitazone, acetaminophen, methotrexate, from the Snodgrass Table 1 category) flags a
  liver-liability candidate **before** any animal work, while profiles clustering with the
  non-toxic/control references clear the compound for the next gate. The screen's value is
  comparative (profile-vs-library), not absolute: a single compound's profile means nothing
  without the reference library beside it.
- **Grounding note — library reality check:** there is **no compound-library data file** in our
  program today. `brief-als.md` establishes that the AGI compound library exists only as ALS
  Researcher ACP job listings, an agent site, and staged articles — no molecule file, no screening
  data on disk — and that no library size or contents may be quoted. This direction is therefore
  designed against an **enumerated, finite set** (the 40 named Pharnext drugs + the 6 pairs), not
  against "every compound in the validated library." A library inventory file must exist before
  any screen can be described as screening "the library."
- **Experimental design:** (a) Build the reference library first: LSCs (species-matched, human
  preferred for human relevance per the patent; rodent as the preclinical bridge) exposed to a
  pre-registered reference panel — known hepatotoxic (troglitazone, acetaminophen), known
  non-hepatotoxic at therapeutic exposure, and vehicle controls — at bracketed doses (twofold /
  fivefold around the expected exposure, per the patent's dosing section); (b) profile by mass
  spectrometry (the patent's preferred readout) and/or gene-expression array; (c) expose LSCs to
  each of the 40 drugs alone and each of the 6 pairs, at the patent-proposed sub-therapeutic
  concentrations and at bracketed multiples; (d) type each test profile by similarity to the
  reference library (pre-registered similarity metric and clustering rule, with blinding); (e)
  include the patent's staging idea: expose at the undifferentiated stage and at a
  differentiation-committed stage, and record whether the profile differs by stage.
- **Falsification test:** the direction is killed if the **reference compounds do not separate**
  — i.e. known hepatotoxic and known non-hepatotoxic references produce profiles that are
  indistinguishable by the pre-registered metric (no clustering) — because then the method cannot
  type toxicity in our hands at all. It is also killed for the pairs if combination profiles are
  **not predictable from, and not distinguishable beyond, the sum of the singles' profiles** in a
  way the metric can resolve (the screen cannot type combinations, only singles). A reference
  library that separates cleanly but flags every test compound as hepatotoxic is a different
  failure — assay oversensitivity — and also kills the screen as designed (recalibration or a
  different readout is required, not a re-interpretation).
- **Evidence grade: C.** The patent's mechanism is Grade A (patent-reported); no LSC profile
  exists for any of our compounds.

## 2.2 Inspired direction — An LSC pre-screen as a safety gate for the ALS / BCL-2 program, using the MCL1-inhibitor failure history as the caution

**Inspired by Snodgrass US 8,512,957 B2 (typing by comparison against predetermined-toxicity
references, including cardiovascular-toxicity categories) read against the ALS paper's MCL1
failure history (brief-cancer-dao.md §2 Strand B).**

- **Hypothesis (Grade C — no data):** The ALS program's BCL-2-family compounds can be
  pre-screened in LSCs for a toxicity-associated signature **before** any in-vivo step, by
  comparing their LSC molecular profiles against reference profiles of compounds with known
  cardiovascular toxicity (the Snodgrass Table 1 cardiovascular category) — because the oncology
  history that motivates the ALS program's tissue-targeted design is a toxicity history: systemic
  MCL1 inhibition failed in cancer trials on on-target cardiotoxicity (AZD5991: high-sensitivity
  troponin T elevated in 54/65 (83%) patients after any dose in a post hoc analysis of stored
  samples vs 14/31 (45%) pre-dose; prospectively reported troponin elevations 8/78 (10.3%);
  response 3/78 (3.9%), all in MDS — corrected framing per verification 2026-11-07). A compound
  whose LSC profile clusters with known cardiotoxic references is deprioritised; one that clusters
  with non-toxic references advances. The LSC screen is a **liver-progenitor** system being asked a
  cardiovascular question — that cross-organ reach is exactly what this direction tests.
- **Experimental design:** (a) Reference panel: LSC profiles for compounds with predetermined
  cardiovascular toxicity and for matched non-cardiotoxic controls, from the Snodgrass Table 1
  categories and from the MCL1-inhibitor record where a compound is obtainable for in-vitro use;
  (b) test profiles for the ALS program's named therapeutic concepts (BCL-XL stabilisation as in
  the ALS paper's AGI-183; MCL1 gain-of-function as in the AAV6-hSyn-MCL1 arm) at bracketed
  doses, in the same LSC system and species as the references; (c) pre-registered similarity
  metric and a pre-set clustering threshold; (d) a positive control for the cross-organ question:
  a compound with known cardiovascular toxicity but no known liver toxicity, to test whether the
  LSC system detects it at all.
- **Falsification test:** the direction is killed if the positive control fails — i.e. LSC
  profiles of known cardiotoxic vs non-cardiotoxic reference compounds **do not separate** by the
  pre-registered metric — because that outcome shows the LSC system cannot serve as a
  cardiac-liability gate in our hands, whatever it can do for liver toxicity. It is also killed if
  the ALS test compounds' profiles are **indistinguishable from vehicle** at all bracketed doses
  while the same compounds are active in their neuronal assays (the LSC system is blind to this
  compound class, not evidence of safety). **A null LSC result is never reported as "safe"** —
  it is reported as "no signal in this system," and the compound still requires its own
  cardiac-specific assessment.
- **Evidence grade: C.** The MCL1 failure figures are **Grade B** (verified 2026-11-07, corrected
  framing); the LSC screen's ability to detect cardiotoxicity is an untested hypothesis. Do not
  present the AZD5991 figures as our data — they are oncology clinical history synthesised in the
  ALS paper.

## 2.3 Inspired direction — Donor-specific LSC toxicity profiles (individual sensitivity)

**Inspired by Snodgrass US 8,512,957 B2 (LSCs isolable from live individuals by needle or wedge
biopsy, "providing a means to enable the development of toxicity profiles for individual patients
or patient populations that have unique drug sensitivities").**

- **Hypothesis (Grade C — no data):** LSCs derived from different donors produce
  **donor-specific** molecular profiles for the same compound — i.e. inter-donor profile variance
  exceeds technical replicate variance — so that a compound's toxicity profile is partly a property
  of the donor, not only of the compound. If true, donor-stratified LSC profiling becomes a
  research tool for understanding variable drug sensitivity; if false, a single-donor LSC line is
  sufficient for screening and donor variation adds nothing.
- **Experimental design:** (a) A multi-donor LSC panel (minimum pre-registered donor count, with
  donor consent, ethics approval, and sourcing documented before any work — this direction may
  not proceed without those); (b) each donor's LSCs exposed to the same compound at the same
  bracketed doses, with technical replicates nested inside each donor; (c) mass-spec protein
  profiles (and/or gene-expression arrays) per the patent's readouts; (d) variance decomposition:
  inter-donor variance vs intra-donor technical variance, pre-registered, for a pre-registered
  compound set (start with two compounds of known, contrasting toxicity from the reference
  library in §2.1); (e) a same-donor, different-batch control to separate donor effects from
  batch effects.
- **Falsification test:** the direction is killed if **inter-donor variance is not greater than
  technical replicate variance** for any tested compound — there is no donor signal to exploit,
  and donor-stratified profiling is dropped. It is also killed if donor differences track
  **batch or passage number** rather than donor identity (the same-donor different-batch control
  separates these) — the signal was an artefact, not biology. Either outcome ends the direction;
  neither outcome licenses a claim about individual patient risk, which would require clinical
  correlation data that do not exist.
- **Evidence grade: C.** The patent's individual-profiling passage is a **proposal in a patent
  specification** (Grade A as patent text, not as evidence); no donor-stratified LSC data exist.
  Governance flag: human LSC sourcing, consent, and ethics approval are preconditions, not
  paperwork to be added later. No patient-facing claim may be made from this direction at any
  stage.

---

# Section 3 — Cancer DAO: the Mena isoform-switch idea

**MERGE TARGET: `brief-cancer-dao.md` (add as a MENA section, alongside the existing BCL-2 /
Akt-Bad / BH3 pillars; do not alter the brief's existing sections).**
**Inspired by: Condeelis et al. US 2022/0251662 A1 — "Metastasis specific splice variants of Mena
and uses thereof in diagnosis, prognosis and treatment of tumors" (applicants: Albert Einstein
College of Medicine; MIT; IFO–Regina Elena Cancer Institute; inventors John S. Condeelis, Sumanta
Goswami, Frank Gertler, Paola Nistico; application publication Aug. 11, 2022. Family includes
granted US 9,719,142 and US 8,603,738. THIS document is an application publication, NOT a granted
patent; its current status is NOT independently verified. Do not present it as a granted patent
and draw no freedom-to-operate conclusion from it.)**

## 3.0 Core mechanism (the idea, faithful to the source)

Mena is a cytoskeletal protein of the Ena/VASP family that controls cell movement, motility, and
shape by **preventing actin filaments from being capped by capping proteins at their barbed
ends** — an anti-capping activity proposed to amplify the barbed-end output of the cofilin and
Arp2/3 pathways and thereby increase metastatic potential. The application's idea is that
**alternative splicing of Mena, not total Mena level, marks the invasive cell**: in invasive tumor
cells isolated from live primary tumors by an in vivo invasion (microneedle chemotaxis) assay,
transcripts containing the **++ exon** (4 amino acids, FYLG; SEQ ID NO: 2) and the **+++ exon**
(19 amino acids, AQSKVTATQDSTNLRCIFC; SEQ ID NO: 4) are **up-regulated**, while transcripts
containing the **11a exon** (21 amino acids, RDSPRKNQIVFDNRSYDSLRHR; SEQ ID NO: 24) are
**down-regulated**, specifically in the invasive population compared with average primary tumor
cells (APTCs) — shown in both the MTLn3 rat allograft model and the PyMT mouse transgenic model
(Fig. 1A–1B; 3 biological × 3 technical repeats), with the ++ and +++ exons on **separate**
transcripts (RACE + cloning, ≥10 clones each). The switch is **stable**: ++/+++ up-regulation
persists in cells that have intravasated into blood and in cells growing as lung metastases, and
Mena 11a was not detected in lung metastases (≥8-fold down-regulation) (Fig. 2). The quantitative
anchors, all **Grade A, application-reported**: total Mena is up-regulated 3–4 fold in invasive
cells; in fine-needle aspiration (FNA) samples from PyMT mice, Mena +++ rose **7.5-fold** in
metastatic carcinomas vs adenomas/MIN while Mena 11a fell to **30%** (n = 9 + 9); in human FNA
samples, 3 of 4 invasive ductal carcinomas showed **3–37-fold** increased Mena +++ vs a
fibroadenoma, Mena 11a was exceedingly low or undetectable in all 4, and in the one IDC where +++
itself was decreased the **Mena +++/Mena 11a ratio was still 7.5 vs a control of 1** — the basis
for the application's ratiometric marker (++/11a or +++/11a ratio). Functionally, expressing the
+++ isoform **enhances** tumor-cell migration (Fig. 8), and **mislocalising** Mena with a molecule
("mito") that redirects it to the wrong place in the cell **inhibits** migration (Fig. 9). The
application claims methods and kits for diagnosis, prognosis, therapy-efficacy assessment, and
metastasis inhibition (antisense, ribozyme, RNAi, antibody, or aptamer reducing ++/+++ and/or
increasing 11a), plus a compound-screening method (a compound that reduces ++/+++ expression or
increases 11a is a candidate metastasis inhibitor), for secretory epithelial tumors including
breast, pancreas, prostate, colon, brain, liver, lung, and head and neck. Detection is by QRT-PCR
with isoform-specific primers, hybridisation probes, or antibodies/aptamers against the isoform
peptides, in blood, tissue, or tumor samples — including circulating tumor cells in blood, which
the application says makes a blood assay possible. Controls named for normalisation include the
80K/140K Mena isoforms and VASP.

**Naming note:** the application itself uses **++ / +++ / 11a** and does not use the name
"Mena^INV". In the published literature, the 19-amino-acid invasive isoform (the application's +++
exon) is known as **Mena^INV**, and the 21-amino-acid epithelial isoform is **Mena11a**. This file
uses the application's ++/+++ notation as primary and gives the Mena^INV correspondence as a
literature mapping, not as application wording. The ++ exon (4 amino acids) is a separate exon
from +++ and is not Mena^INV.

**What this mechanism suggests for us:** a **splice-isoform ratio** as a research readout for the
Cancer DAO — a ratiometric, blood-accessible, migration-linked marker that pairs naturally with
the DAO's existing BCL-2 / BH3-profiling stratification pillar (brief-cancer-dao.md §3 Item 3):
one pillar stratifies by apoptotic priming, the other by invasive isoform state. The three
directions below are research designs, not diagnostics — no direction below claims a diagnostic,
prognostic, or therapeutic use in humans.

## 3.1 Inspired direction — A Mena isoform-ratio panel as a Cancer DAO metastasis-biomarker research design

**Inspired by Condeelis et al. US 2022/0251662 A1 (the +++/11a ratiometric marker; FNA data in
mouse and human samples).**

- **Hypothesis (Grade C — no data):** The **Mena +++/Mena 11a expression ratio** (with Mena ++ /
  Mena 11a as a secondary ratio) distinguishes invasive from non-invasive breast-cancer cells in
  an **independent** cell-line panel and in FNA-style samples — i.e. the ratio reproduces outside
  the application's own models (MTLn3 rat allograft, PyMT mouse, 4 human IDCs vs 1 fibroadenoma).
  The ratio, not any single isoform's absolute level, is the candidate readout, because the
  application's own human data show the ratio staying elevated (7.5 vs control 1) even where +++
  alone fell.
- **Experimental design:** (a) Cell-line panel: MDA-MB-231 (highly invasive) vs T47D (less
  invasive) — the two human lines in the application's Fig. 3 — plus at least one additional
  independent invasive/non-invasive pair, to avoid a two-line result; (b) QRT-PCR with
  isoform-specific primers following the application's primer-design strategy (Table 2 of the
  application; ++-specific, +++-specific, and 11a-specific primers plus pan-Mena primers),
  normalised to pan-Mena and to the application's named unchanged controls (80K/140K Mena
  isoforms, VASP); (c) blinded sample handling and pre-registered ratio thresholds; (d) a
  migration assay (transwell / wound-healing) run in parallel on the same lines, so the ratio is
  always reported **next to** a functional invasion readout, never alone; (e) if cell-line results
  support the ratio, a second stage in FNA-style samples from a mouse mammary model, mirroring
  the application's mouse FNA design (early adenoma/MIN vs late invasive metastatic carcinoma),
  with pre-registered group sizes.
- **Falsification test:** the direction is killed if the ratio **does not separate** invasive
  from non-invasive lines (area under the ROC curve not better than chance, or the pre-registered
  threshold fails in the second line pair) — the ratio is not a portable marker. It is also
  killed if the ratio separates the lines but **does not track the migration assay** (ratio high
  where migration is low, or vice versa) — the ratio would then be a correlate of cell line, not
  of invasive behaviour. A ratio that works in cell lines but fails in FNA-style samples narrows
  the direction to cell-line research use only; it does not support any tissue or blood
  application.
- **Evidence grade: C.** The application's FNA numbers (7.5-fold +++, 11a to 30%, 3–37-fold in
  human IDC) are **Grade A, application-reported** — from n = 9 + 9 mice and **4 human IDCs vs 1
  fibroadenoma**, which is a small, application-reported dataset, not a validated biomarker study.
  No diagnostic, prognostic, or clinical claim may be made from this direction. The Cancer DAO
  has no assay, lab, or dataset today (brief-cancer-dao.md §1) — this direction is a design for a
  capability that does not yet exist.

## 3.2 Inspired direction — An isoform-switch compound screen for the Cancer DAO

**Inspired by Condeelis et al. US 2022/0251662 A1 (the compound-screening method: a compound that
reduces ++/+++ expression or increases 11a expression is a candidate metastasis inhibitor).**

- **Hypothesis (Grade C — no data):** A compound that **shifts Mena splicing or expression from
  +++ toward 11a** (or reduces +++ expression) in an invasive breast-cancer line will **reduce
  invasion in a migration assay** — i.e. the isoform ratio is not only a marker of the invasive
  state but a **screenable readout** whose movement predicts a functional change. This is the
  application's screening logic turned into a falsifiable screen design for our programs.
- **Experimental design:** (a) Screen in MDA-MB-231 cells (invasive, +++-expressing per the
  application's Fig. 3) with QRT-PCR readout of ++, +++, and 11a (same primer strategy as §3.1)
  after compound exposure at bracketed doses; (b) compound set: a **defined, enumerated** starting
  set — the application's own screening method names no compounds, so the set must be specified
  before screening (candidates: the repurposed drugs with known splicing or cytoskeletal activity
  from our existing compound work, or a small literature-anchored set; the set, its size, and its
  sourcing are pre-registered — no "library" may be invoked, because no compound-library data
  file exists, see §2.1); (c) every ratio hit is carried into a **migration assay** (Fig. 8/9
  style: area-based migration measurement) in the same cells, blinded; (d) map the screen onto
  the existing ALS Researcher compound-screening job concept (`compound_screening_pack`, $150 /
  72h, listed in Virtuals ACP — a job listing, not a capability; the agent is offline with 0 jobs
  completed as of 2026-11-06) only as a **product framing** for when a screen exists, never as
  evidence that screening has happened.
- **Falsification test:** the direction is killed if **ratio movement does not track migration**
  — i.e. compounds shift the +++/11a ratio but migration does not fall (or migration falls
  without any ratio shift). Either pattern means the ratio is a correlate, not a driver readout,
  and it is dropped as a screen endpoint (it may survive as a marker only under §3.1's separate
  test). It is also killed if **no compound in the starting set moves the ratio** beyond technical
  noise — the screen has no dynamic range for this compound class, and the set (not the concept)
  must change before any re-test. A hit that moves both ratio and migration is a **screen hit**,
  not a drug candidate: it earns a dose–response and a second cell line, nothing more.
- **Evidence grade: C.** The application's screening method is a **claimed method** (Grade A as
  application text); no compound has been shown by it to inhibit metastasis. No treatment or
  anti-metastasis claim may be made from any hit at this stage. Curable.X is named here only as
  a possible future home for a screening capability — it is a proposed program, and no screen,
  compound, or result is attributed to it.

## 3.3 Inspired direction — Mena mislocalisation as a separable mechanism probe

**Inspired by Condeelis et al. US 2022/0251662 A1 (Fig. 9: inhibiting metastatic tumor-cell
migration by redirecting Mena to the wrong place in the cell with a molecule called "mito";
Fig. 8: expressing the +++ isoform enhances migration).**

- **Hypothesis (Grade C — no data):** **Redirecting Mena away from the leading edge**
  (mislocalisation) reduces tumor-cell migration **independently of isoform expression levels** —
  i.e. where Mena is matters separately from which splice isoform is present and how much of it
  there is. If true, localisation is a second, separable handle on the invasive phenotype alongside
  the isoform ratio (§3.1) and the isoform-switch screen (§3.2); if false, the Fig. 9 result was
  an expression-level effect in disguise, and localisation adds nothing.
- **Experimental design:** (a) Replicate the application's Fig. 8/9 logic in MDA-MB-231 cells:
  a characterised Mena-mislocalising tool (the application's "mito" molecule is named but not
  structurally specified in the extracted text — the tool, its identity, and its sourcing must be
  established from the application or the literature before any work, and if it cannot be
  identified the direction uses a documented mislocalisation approach instead, with the
  substitution recorded); (b) measure three things in parallel in the same experiment: Mena
  localisation (imaging: leading-edge vs cytosolic distribution), isoform expression (QRT-PCR for
  ++, +++, 11a — to test whether expression changed), and migration (area-based assay as in
  Fig. 8/9); (c) controls: vehicle, a non-mislocalising analogue if available, and an
  isoform-expression control (a condition that changes expression without changing localisation,
  e.g. siRNA titration, to separate the two variables in the other direction).
- **Falsification test:** the direction is killed if migration falls **only when isoform
  expression also falls** — i.e. there is no condition in which localisation changes while
  expression stays constant and migration still falls. That outcome means the mislocalisation
  effect is not separable from an expression effect, and localisation is dropped as an independent
  mechanism. It is also killed if the mislocalising tool **cannot be identified or sourced** and
  no documented substitute exists — the direction is then unbuildable, not merely untested, and
  is recorded as blocked rather than pursued with an unspecified reagent.
- **Evidence grade: C.** The Fig. 8/9 results are **Grade A, application-reported** (figure-level
  results in an application publication, without numeric values in the extracted text). No
  therapeutic claim — mislocalisation as a mechanism probe is a research question about cell
  biology, not a treatment strategy, and must not be presented as one.

---

## What this file does NOT do

- It does not claim any discovery, treatment, cure, diagnosis, prognosis, or medical-device use
  for any compound, combination, ratio, or screen described here.
- It does not present any inspired direction as the patent's claim or the patent's data, and it
  does not present any patent's data as our result.
- It does not verify any patent's legal status, and it draws no freedom-to-operate conclusion.
  Each section's status line states what was **not** verified.
- It does not create, fund, or approve any program, series, entity, or raise. Alzheimer's has no
  W3 series number; the Cancer DAO has no series number; no series number is adopted or invented
  here. Filed fact (Foundation B20260196664, Fellowship B20260229217) stays apart from proposed
  plans.
- It does not quote a compound-library size, contents, or screening results — no library data file
  exists (see §2.1 grounding note). Every screen in this file is designed against an enumerated,
  finite compound set.
- It does not resolve the AGI-183 identity tension (ALS paper's BCL-XL stabiliser vs catalog's
  CRBN-binding FLIP inhibitor) — §1.1 flags it as a blocker for naming any CRBN compound.
- It does not touch the Feldman traffic patent (US 8,918,278 B2) or any payments-track patent:
  those are not bio patents and are out of scope for this file by design.

## Verification log (for the parent coordinator)

- **Read in full:** Pharnext JP6062995B2 via `brief-alzheimers.md` (read in full, 61-page patent
  as briefed; Tables 2–5 illegible per the brief — no number from those tables is used here);
  Snodgrass US 8,512,957 B2, 28 pages, read from rendered page images (title page, abstract,
  spec pp. 1–16, Figs. 1–4); Condeelis US 2022/0251662 A1, 25 pages, text-extracted in full
  (1,154 lines: abstract, summary, detailed description §§0029–0066, Table 1 sequences, Table 2
  primers, Table 3 patient data, Figs. 1–11 descriptions).
- **Confirmed against the Snodgrass document:** abstract wording (molecular profiles in isolated
  mammalian LSCs; correlation with toxicities); LSC definition (pluripotent progenitors,
  hepatoblasts preferred, ≥51%/75%/95% pluripotent populations); Table 1 reference compounds by
  toxicity category; mass-spec-preferred readout; >500 labels/hour integrated systems; dose
  bracketing; species-matched controls; individual-patient profiling passage; test compositions I
  and II unnamed in the figures.
- **Confirmed against the Condeelis document:** ++ (4 aa, FYLG) / +++ (19 aa,
  AQSKVTATQDSTNLRCIFC) / 11a (21 aa) sequences; 3–4 fold Mena up-regulation in invasive cells;
  7.5-fold +++ / 11a to 30% in mouse FNA (n = 9 + 9); 3–37-fold +++ in 3 of 4 human IDCs;
  +++/11a ratio 7.5 vs control 1 in patient 5609; ++/+++ on separate transcripts; +++ persistence
  in blood and lung metastases; Fig. 8 migration enhancement / Fig. 9 mislocalisation inhibition;
  tumor list (breast, pancreas, prostate, colon, brain, liver, lung, head and neck); family
  (granted US 9,719,142 and US 8,603,738; this document an application publication).
- **Corrected / adapted vs the task's example moves (deliberate, recorded):** (a) the CRBN
  direction is framed as a **mechanism class** (CRBN-recruited degradation of a network node),
  NOT as pairing the catalog's CRBN compound with a network drug — the catalog's CRBN compound
  is a pro-apoptotic FLIP inhibitor, the opposite direction from neuroprotection, and its
  AGI-183 identifier is in unresolved tension with the ALS paper's AGI-183; (b) the toxicity
  screen is designed against the **enumerated 40-drug set**, not "every compound in the validated
  library" — no library data file exists; (c) the Mena^INV name is given as a **literature
  mapping** of the application's 19-aa +++ exon, not as application wording; the 4-aa ++ exon is
  a separate exon, not Mena^INV.
- **NOT verified:** live legal status of any of the three patents (JP6062995B2 JPO register;
  US 8,512,957 B2 USPTO register/term; US 2022/0251662 A1 current prosecution status); the
  identity or structure of the application's "mito" mislocalisation molecule (§3.3); any
  compound-library inventory; any experimental result in this file (all Grade C by design).
