# Parkinson's / Gaucher / Lysosomal Program Brief — Lysosomal Therapeutics US20190092789A1

**Published:** research brief in this repo's `research/` folder.
**Research date: 7 November 2026.**
**Source document (read in full): `~/workspace/user/files/US20190092789A1.pdf` (24 pages) — US Patent Application Publication US 2019/0092789 A1, "Heterocyclic Pyrimidinone Compounds and Their Use in the Treatment of Medical Disorders," Skerlj et al., applicant/assignee Lysosomal Therapeutics Inc. (Cambridge, MA). Text extracted in full with `pdftotext` (1,539 lines); chemical structures in the PDF are images and were not individually readable from text.**

## Honesty lines (read first — they govern every item)

- **This is an ABANDONED patent APPLICATION, not a granted patent and not a trial.** Everything below is patent-reported **biochemistry only** — one in vitro enzyme-activation assay. No cells, no animals, no patients. No treatment, cure, diagnosis, or medical-device claims anywhere.
- **Legal status IS independently verified (see §1.2).** Google Patents, checked 2026-11-07 (page crawled 2026-11-08 01:17 UTC): US application **Abandoned 2020-02-01** (failure to respond to an office action); the WO member **Ceased**; the EP member **Withdrawn**. No member of this family ever granted. That does **not** equal freedom-to-operate (§1.3).
- **The application's own efficacy language is patent-drafting language, not evidence.** The document claims methods of "treating" 15 disorders. The only data in it are binned enzyme-activation symbols from one biochemical assay (§4). Never repeat a "treatment" claim from this document as fact.
- **The GCase-activation hypothesis took a major clinical hit in June 2026.** The applicant's clinical candidate from this same program, LTI-291 / BIA 28-6156 (pariceract), **failed its Phase IIb ACTIVATE trial** in GBA-associated Parkinson's and Bial discontinued it (§6). Any program built on this mechanism starts from that fact, not from the 2019 application.
- **Parkinson's has NO verified W3 series number.** The 33-series list has no Parkinson's entry. The vr-spaces-loop `series.json` S34/S35 numbers are invented and must NOT be adopted. Parkinson's is a disease program, not a series.
- **Every number needs a source + date.** Where a figure could not be verified, this brief says so. Table 1 / Table 4 compound structures are images — their individual identities are unverified (see §4.5).
- **Filed fact vs proposed plan kept apart.** The application is a filed fact (published 2019, abandoned 2020). Any Parkinson's/Gaucher program built on it is a **proposal** — nothing is formed, funded, trialled, or offered. "33 named W3 sub-series in the April 2026 internal list" — never 35.

---

## 1. What the patent application is + legal status

### 1.1 Identity

| Field | Value | Source |
|---|---|---|
| Publication number | US 2019/0092789 A1 | Supplied PDF, title page |
| Title | "Heterocyclic Pyrimidinone Compounds and Their Use in the Treatment of Medical Disorders" | Supplied PDF |
| Applicant / assignee | Lysosomal Therapeutics Inc., Cambridge, MA (US) | Supplied PDF |
| Inventors | Renato T. Skerlj (West Newton, MA); Andrew C. Good (Wallingford, CT); Peter T. Lansbury (Brookline, MA) | Supplied PDF |
| Application No. | US 15/756,663 | Supplied PDF; Google Patents |
| PCT filed | 2016-09-02 (PCT/US2016/050026; §371(c) date 2018-03-01) | Supplied PDF |
| Priority | US Provisional 62/214,478, filed 2015-09-04 | Supplied PDF |
| Publication date | 2019-03-28 | Supplied PDF; Google Patents |
| Classifications | C07D 513/04; C07D 498/04; C07D 487/04 | Supplied PDF |
| What it claims, in one sentence | Heterobicyclic pyrimidinone compounds (Formula I and Formula II), pharmaceutical compositions and medical kits containing them, and methods of using them to treat medical disorders — principally Gaucher disease, Parkinson's disease, Lewy body disease, dementia, and multiple system atrophy — on the theory that the compounds activate glucocerebrosidase (GCase). | Supplied PDF, Abstract + [0006]–[0010] |

### 1.2 Legal status — VERIFIED against Google Patents, 2026-11-07

Source: `https://patents.google.com/patent/US20190092789A1/en`, read 2026-11-07 (page crawled 2026-11-08 01:17 UTC). Google Patents itself cautions that its legal-status display "is an assumption and is not a legal conclusion" — confirm against the USPTO Patent Center before any FTO use.

| Member | Status (Google Patents, 2026-11-07) |
|---|---|
| **US 15/756,663** (US20190092789A1) | **Abandoned.** Legal events: non-final office actions mailed 2019-02-07 and 2019-07-25; **2020-02-01 — "ABANDONED — FAILURE TO RESPOND TO AN OFFICE ACTION"** (code STCB). Never granted. |
| **WO PCT/US2016/050026** (WO2017040877A1, published 2017-03-09) | **Ceased.** |
| **EP 16843038.7** (EP3344632A1, published 2018-07-11; EP3344632A4, 2019-03-20) | **Withdrawn.** |

**Family:** a single family (Google Patents Family ID 58188435) with **one** family application — the US application above. No granted member exists in this family anywhere.

**Claims as published:** claims 1 (Formula I compounds) and 15 (Formula II compounds) are the independent compound claims; claims 16–32 are dependent claims; claim 33 is a pharmaceutical composition; claim 34 is a method of treating the 15-disorder list. **Claims 2–14 and 35–40 were canceled in the publication.** These are *application* claims — they were never examined to grant, because the application was abandoned.

**Later citing art:** cited by US11459325B2 (Takeda Pharmaceutical, published 2022-10-04, "Heterocyclic compound"). A "similar document" listed by Google Patents is US20190112316A1 (2019-04-18), "Thiazolo[3,2-a]pyrimidinone and other heterobicyclic pyrimidinone compounds for use in medical therapy" — apparently a sibling Lysosomal Therapeutics filing; **its status was not checked in this pass** (follow-up for §8).

### 1.3 Freedom-to-operate consequences — do not skip these

1. **Abandoned ≠ free to use.** This application never granted, so it confers no exclusionary rights itself. But abandonment of *this* application says nothing about the applicant's **sibling families**, several of which DID grant: e.g. US11400095B2 (substituted imidazo[1,5-a]pyrimidines, granted 2022-08-02), US11124516B2 (pyrrolo[1,2-a]pyrimidinyl carboxamides, granted 2021-09-21), US11932645B2 (substituted pyrazolo[1,5-a]pyrimidines, granted 2024-03-19), EP3215511B1 (granted 2024-04-17, now held by Bial-R&D Investments S.A.). Those are different scaffolds, but the same therapeutic area and the same applicant lineage (Lysosomal Therapeutics → Bial, §6). A use of any pyrimidinone GCase activator needs a sweep of those families, not just this one.
2. **Abandonment can in principle be revived** by petition in the US (unintentional delay), though after 6+ years and with the WO/EP members also dead, revival of this family is a question for counsel, not an assumption in either direction.
3. **The underlying idea is crowded prior art.** The family itself cites PL3366688T3, "Substituted pyrazolopyrimidines as glucocerebrosidase activators" (US Dept. of Health and Human Services), and the GCase-activator field now includes Bial's pariceract program, Gain Therapeutics' GT-02287, and academic NCGC compounds. The application's own compounds are old chemistry (priority 2015).
4. **No FTO conclusion may be drawn from this brief.** A written FTO opinion from counsel, after a USPTO Patent Center check and a sibling-family sweep, is a precondition for any use.

---

## 2. The compound class + exemplary compounds

### 2.1 The class: heterobicyclic pyrimidinones (Formula I and Formula II)

Two Markush families are defined ([0007]–[0008], [0104]–[0118]):

- **Formula I** — a heterobicyclic pyrimidinone core bearing substituents R¹ (independently each occurrence: hydrogen, C₁–C₆ alkyl, halogen, C₁–C₆ haloalkyl, C₃–C₆ cycloalkyl, 3–8 membered heterocyclyl, or 6-membered aryl), R² (hydrogen, C₁–C₆ alkyl, or C₃–C₆ cycloalkyl), R³ (phenyl, C₃–C₈ cycloalkyl, 3–8 membered heterocycloalkyl, heteroaryl, partially unsaturated 9–10 membered bicyclic carbocyclyl, or partially unsaturated 8–10 membered bicyclic heterocyclyl — each optionally substituted), R⁴ (hydrogen or C₁–C₆ alkyl), X (O or N(R⁴)), Y (a bond, C₁–C₆ alkylene, C₁–C₆ haloalkylene, C₃–C₆ cycloalkylene, or —C(O)—), and n = 1 or 2; with the proviso that X is N(H) when Y–R³ is C₁–C₆ alkylene-(6-membered aryl). Pharmaceutically acceptable salts included.
- **Formula II** — the same variable set in a second ring arrangement (the isomeric heterobicyclic core). Preferred embodiments narrow R³ to substituted phenyl (1–3 substituents from C₁–C₆ alkyl, halogen, C₁–C₆ haloalkyl, C₃–C₆ cycloalkyl, hydroxyl, C₁–C₆ alkoxy, C₂–C₄ alkynyl, —(C₂–C₄ alkynyl)-C₁–C₆ alkoxy, 5-membered heteroaryl, saturated 3–8 membered heterocyclyl) or to substituted C₃–C₈ cycloalkyl / partially unsaturated bicyclic carbocyclyl / heterocyclyl.

**The named exemplary scaffold** (Abstract; Example 1): **6-oxo-3,4-dihydro-2H,6H-pyrimido[2,1-b][1,3]thiazine-7-carboxamide compounds** — i.e. a fused pyrimidinone–thiazine bicyclic core with a carboxamide at the 7-position.

### 2.2 Exemplified compounds (what the document actually makes)

| Example | What was prepared | Table |
|---|---|---|
| **Example 1** | **N-(4-butylcyclohexyl)-6-oxo-3,4-dihydro-2H,6H-pyrimido[2,1-b][1,3]thiazine-7-carboxamide** — the single named exemplar of the title scaffold. Prepared from ethyl 2-mercapto-6-oxo-1,6-dihydropyrimidine-5-carboxylate + 1,3-dibromopropane (K₂CO₃, tetrabutylammonium bromide, toluene, 100 °C overnight), then amidation. | — |
| **Example 2** | **5-oxo-5H-oxazolo[3,2-a]pyrimidine-6-carboxamide compounds** (general procedure: amine + diethyl ethoxymethylenemalonate in 1,2,4-trichlorobenzene, 160 °C, 16 h) | Table 2 |
| **Example 3** | **5-oxo-1,5-dihydroimidazo[1,2-a]pyrimidine-6-carboxamide compounds** (carboxylic acid + amine, HATU/DIPEA in DMF, rt or 65 °C, 16 h). Individual entries carry ¹H/¹³C NMR and ESI-MS data in the text — e.g. compound **3A**: ESI-MS m/z 347 (M+Na); compound **3B**: ESI-MS m/z 309 (M−H). | Table 3 |

**Table 1** ([0076]) lists the "most preferred" exemplified compounds, numbered **I-1 through at least I-30** (I-1, I-2, I-8, I-30 are legible in the text extraction; the intervening entries are present but their structures are images). **The individual structures in Tables 1–4 are drawn as images in the PDF; their identities cannot be recovered from text extraction.** Do not attribute a named structure to a Table 1 number, and do not quote a compound count for Table 1 beyond "numbered I-1 through at least I-30."

**Open question — LTI-291:** the name **"LTI-291" (and "pariceract" / "BIA 28-6156") appears ZERO times in the extracted text of this application** (verified by text search, 2026-11-07). Whether the applicant's clinical candidate LTI-291 is a compound within Formula I/II of this application is **not established by this document** — its structure was not publicly reported in the early literature, and the application's structures are images. Do not claim this patent "is the LTI-291 patent" without a structure-level match confirmed against Bial's disclosures or the image structures. See §6.

---

## 3. Compositions, kits, methods + the disease list

### 3.1 Compositions ([0128]–[0164])

Pharmaceutical compositions comprising a Formula I or II compound plus a pharmaceutically acceptable carrier, formulated for oral, parenteral (subcutaneous, intramuscular, intravenous, epidural), topical, intravaginal/intrarectal, sublingual, ocular, transdermal, or nasal administration; unit dosage forms (tablets, drenches, boluses, powders, granules, sterile solutions/suspensions, sustained-release formulations). The stated dosing principle ([0165]) is only "the lowest dose effective to produce a therapeutic effect" — **no numeric human dose range is stated in the sections read**. Do not present any dose as the application's recommendation.

### 3.2 Kits ([0167])

A kit for treating a disorder, comprising (i) instructions for treating Gaucher disease, Parkinson's disease, Lewy body disease, dementia, or multiple system atrophy, and (ii) a Formula I or II compound, optionally in one or more unit dosage forms. That is the whole kit disclosure — no diagnostic, no biomarker, no companion test.

### 3.3 Methods of treatment ([0102]–[0127]) and the disease list

The method claim (claim 34 as published) covers administering a therapeutically effective amount to treat a disorder selected from:

> **Gaucher disease, Parkinson's disease, Lewy body disease, dementia, multiple system atrophy, epilepsy, bipolar disorder, schizophrenia, an anxiety disorder, major depression, polycystic kidney disease, type 2 diabetes, open angle glaucoma, multiple sclerosis, and multiple myeloma.**

Dementia is further specified ([0119]) as Alzheimer's disease, frontotemporal dementia, and a Lewy body variant of Alzheimer's disease. The stated mechanism ([0102]): "it is understood that heterobicyclic pyrimidinone compounds described herein **may activate glucocerebrosidase (GCase)**" — explicitly framed as "although not wishing to be bound by a particular theory."

**Critical scope note:** this 15-disorder list is a **definition of claim scope, not evidence**. The only data in the document are the biochemical GCase-activation results in §4. No data in the application concern any disease, any cell, or any animal. Inclusion of epilepsy, bipolar disorder, schizophrenia, type 2 diabetes, glaucoma, multiple sclerosis, or multiple myeloma proves nothing about efficacy in any of them.

### 3.4 Combination therapy ([0126]–[0127])

The application embraces co-administration with a second agent. Named second agents:

- **For Gaucher disease:** taliglucerase alfa, velaglucerase alfa, eliglustat, ibiglustat, miglustat.
- **For Parkinson's disease:** a glucosylceramide synthase inhibitor (e.g. ibiglustat), an acid ceramidase inhibitor (e.g. carmofur), an acid sphingomyelinase activator, levodopa, pramipexole, ropinirole, rotigotine, apomorphine (or salts thereof). Further glucosylceramide synthase inhibitors and acid ceramidase inhibitors are incorporated by reference (WO 2015/089067, WO 2014/151291, WO 2014/043068, WO 2008/150486, WO 2010/014554, WO 2012/129084, WO 2011/133915, WO 2010/091164; US 9,126,993; 8,961,959; 8,940,776; 8,729,075; 8,309,593; US 2014/0255381; US 2014/0336174). GCase assay methods are incorporated by reference from WO 2015/173168 and WO 2015/173169.

### 3.5 Background as stated by the applicant ([0003]–[0005])

- Gaucher disease is "a genetic disorder associated with a deficiency of the lysosomal enzyme, glucocerebrosidase," with an incidence of "approximately **1 in 20,000 live births** in the general population" (**patent-stated figure, not independently verified in this pass**) and "a common lysosomal storage disorder." Current treatments named: enzyme replacement therapy ("tends to be expensive"), analgesics for bone pain, blood and platelet transfusions, splenectomy, joint replacement for bone erosion.
- "Mutations in the gene encoding glucocerebrosidase are also a risk factor for Parkinson's disease and diffuse Lewy Body Disease." Parkinson's is described as a degenerative disorder of the CNS "associated with death of dopamine-containing cells in a region of the midbrain," afflicting "millions of people," incidence increasing with age; levodopa and dopamine agonists named with side effects (hallucinations, insomnia, nausea, constipation; tolerance; dyskinesia). Diffuse Lewy body disease is described as a dementia "sometimes confused with Alzheimer's disease."

---

## 4. The evidence (patent-reported, biochemical only)

**Read the whole section as:** "the patent reports…". There is exactly one experiment in this application: Example 4, a biochemical GCase-activation assay. No cell assay, no animal study, no human data.

### 4.1 Example 4 — GCase activation assay, Part I: procedure ([0189]–[0191])

- **Enzyme system:** 10 nM glucocerebrosidase (GCase) + 100 nM saposin C (Enzo ALX-201-262-C050) in a mixed-micelle preparation: phosphatidylserine (0.37 mol %) + Triton X-100 (0.32 mM) in 176 mM K₂HPO₄ / 50 mM citric acid, pH 4.7.
- **Substrate:** 4-methylumbelliferyl-β-D-glucopyranoside (4-MU-β-Glc), 2 mM — a fluorogenic artificial substrate, not the natural substrate glucosylceramide.
- **Protocol:** test compounds diluted from 10 mM DMSO stocks; 0.41 µL compound/DMSO added to 100 µL micellar solution containing GCase + saposin C; 30 min pre-incubation at room temperature; reaction initiated by combining 25 µL substrate solution with 25 µL compound/GCase/saposin mixture; 15 min at room temperature; stopped with 150 µL 1 M glycine, pH 12.5; endpoint fluorescence (excitation 365 nm, emission 440 nm) on a SpectraMax i3.
- **Screening concentrations:** 1.0 µM and 0.1 µM final. "Subsequent 8-point dose response curves were obtained using 3-fold dilutions from a maximum final concentration of 5 µM" — **but no dose–response curves, EC₅₀ values, or numeric activation percentages are reported in the extracted text.** Do not quote an EC₅₀ for any compound from this document.

### 4.2 Example 4 — Part II: results (Table 4, [0192])

Results are reported **only as binned symbols** (no numbers):

| Symbol | Meaning (per [0192]) |
|---|---|
| `+` | less than 5% GCase activation |
| `++` | 5% up to 10% GCase activation |
| `+++` | greater than 10% GCase activation |
| `N/A` | no data available |

Table 4 (pp. 20–22 of the publication) lists the exemplified compounds — structures as images — with cLogP, PSA, water solubility (µg/mL), and the activation symbol at 1 µM and at 0.1 µM. Legible rows show, for example, cLogP values ranging **0.5–2.8**, PSA **61.8–89.5**, and water solubility **0.3–58.0 µg/mL** (ranges observed across the legible Table 4 rows; the extraction interleaves columns, so these are ranges, not a per-compound table). Several compounds score `+++` (>10% activation) at 1 µM; at 0.1 µM most scored compounds fall to `+` (<5%) or `++` (5–10%). **The individual compound-to-row mapping is not recoverable from text extraction — do not attach a `+++` to a named compound.**

### 4.3 What the evidence is — and is not

- **It is:** a single-concentration-bin biochemical screen showing that some exemplified heterobicyclic pyrimidinones increase the activity of purified GCase against an artificial fluorogenic substrate, in a test tube, at 1 µM and 0.1 µM, by mostly <10% and in the best bin >10%.
- **It is not:** a cell result (no lysosomal activity in cells, no glucosylceramide clearance, no α-synuclein readout); not an animal result; not a human result; not a potency measurement (no EC₅₀); not a brain-penetration result; not a safety result. A >10% increase in test-tube GCase activity against 4-MU-β-Glc is a **screening signal**, and the application itself frames activation as a theory ("may activate"), not a demonstrated therapeutic mechanism.
- **No replication data, no statistics, no controls are reported** for Example 4 in the extracted text (no n, no error bars, no vehicle/DMSO control values, no positive-control activator). Treat the bins as the application's own reporting, not as independently verified measurements.

### 4.4 What could NOT be verified from the supplied document

- **Individual compound identities in Tables 1–4:** structures are images; only Example 1's compound is named in text, and only Table 3 entries 3A/3B carry text-readable analytical data (NMR/MS). Any structure-to-activity claim by anyone else must be re-checked against the image pages or the original USPTO publication.
- **Dose–response curves / EC₅₀ values:** mentioned as obtained ([0191]) but not reported in the extracted text.
- **The 1-in-20,000 Gaucher incidence figure:** patent-stated ([0003]); not independently verified in this pass.
- **Any numeric human dose:** none stated in the sections read ([0165] gives only the lowest-effective-dose principle).
- **Status of the sibling filing US20190112316A1:** not checked (see §1.2).
- **Whether LTI-291 falls within Formula I/II:** not established (§2.2).

---

## 5. The mechanism — literature-verified (separate from the application's claims)

This section is established science from the peer-reviewed and clinical literature, checked 2026-11-07. It is **not** the application's evidence — it is the reason the application's theory was plausible, and the context in which it must now be judged.

**The GBA1–GCase–Parkinson's link is real and well established.** *GBA1* encodes glucocerebrosidase (GCase), the lysosomal enzyme that hydrolyses glucosylceramide (GlcCer) and glucosylsphingosine (GlcSph). Biallelic loss-of-function *GBA1* variants cause Gaucher disease — deficient GCase activity with GlcCer/GlcSph accumulation, classically in tissue macrophages. Heterozygous *GBA1* variants are the **most common genetic risk factor for Parkinson's disease**, carried by roughly **5–20% of Parkinson's patients depending on ancestry** (5–15% in the 2026 ResearchSquare review of the field; 5–20% in the PMC review). The landmark multicentre study (Sidransky et al., 2009, as summarised in the 2026 review) showed heterozygous *GBA1* variants confer a **5–10-fold increased risk of Parkinson's**, often with earlier onset and more severe progression; in type 1 Gaucher disease itself, a 444-patient cohort followed 12 years found an adjusted lifetime Parkinson's risk ratio of **21.4 (95% CI 10.7–38.3)** versus the general population (Bultron et al.). Severe variants (e.g. L444P / p.Leu483Pro) carry earlier onset, faster progression, and more cognitive decline than mild ones; some variants (e.g. E326K) confer Parkinson's risk without causing Gaucher disease — E326K impairs GCase delivery to lysosomes via its receptor LIMP2, reducing lysosomal GCase activity. The mechanistic model: reduced GCase activity disrupts lysosomal homeostasis, impairs autophagy and α-synuclein turnover, and increases α-synuclein accumulation — a lysosomal-proteostasis route to Lewy pathology that also extends, in the literature, to dementia with Lewy bodies, frontotemporal dementia, and multiple system atrophy. **That mechanism is established science. It does not prove that any compound in this application treats any of those diseases.**

**GCase activation as a therapeutic strategy — the clinical record so far.** Small-molecule GCase activators (allosteric activators / pharmacological chaperones) aim to increase the activity of wild-type and mutant GCase. The field's lead from this applicant, LTI-291 / BIA 28-6156 (pariceract; see §6), reached the clinic: a Phase 1b trial in 40 GBA-PD participants (10, 30, or 60 mg daily × 28 days, randomised, double-blind, placebo-controlled; *Movement Disorders* 2023) was well tolerated and reached plasma and CSF concentrations "sufficient to at least double GCase activity." The follow-on Phase IIb ACTIVATE trial (NCT05819359) then **failed** — see §6. Other GCase activators remain in development (e.g. Gain Therapeutics' GT-02287, an allosteric "STAR" regulator), but as of 2026-11-07 none has demonstrated clinical efficacy in Parkinson's. **Target engagement (doubling GCase activity) is not clinical benefit** — that is the central lesson of ACTIVATE, and it governs every inspired direction in §10.

**Sources for this section:** (1) ResearchGate — Bultron et al., "The risk of Parkinson's disease in type 1 Gaucher disease" (444 GD1 patients, risk ratio 21.4, 95% CI 10.7–38.3); (2) Monarch Initiative Disease Mechanism page, Gaucher Disease (biallelic *GBA1* → deficient glucocerebrosidase; *GBA1* variants a major genetic risk factor for parkinsonism); (3) ResearchSquare preprint, "Beyond Parkinson's disease: expanding the neurodegenerative spectrum of GBA1-associated disorders" (posted 2026-08-25; Sidransky 2009 5–10× risk; 5–15% carrier frequency; L444P severity; E326K/LIMP2 — **preprint, not peer-reviewed**); (4) PMC12478413 (bioRxiv preprint 2025-09-02, E326K/LIMP2 mechanism; **preprint**); (5) PubMed 38843618 (GlcSph as a GBA-PD biomarker, 1,344 PD patients). All accessed via search 2026-11-07.

---

## 6. What the applicant actually did next — the LTI-291 / Bial story

This is the part of the record that matters most for any program decision, and it is **not** in the application — it is what happened after it.

- **LTI-291 (BIA 28-6156; INN pariceract; CAS 1919820-28-2)** is an oral small-molecule β-glucocerebrosidase activator / positive allosteric modulator originated by Lysosomal Therapeutics. First described in the literature by 2017; structure not publicly reported in the early literature.
- **Bial acquired the program in 2020**, buying Lysosomal Therapeutics' Parkinson's research programmes and forming Bial Biotech (Cambridge, MA) from former LTI executives and scientists. (European Biotechnology, 2026-06-09; Parkinson's News Today, 2026-06-15.)
- **Phase 1 / Phase 1b:** healthy-volunteer ascending-dose studies, then a Phase 1b in 40 GBA-associated Parkinson's participants (10/30/60 mg × 28 days) — well tolerated, no deaths or treatment-related serious adverse events, dose-proportional exposure, free CSF concentrations equal to the free fraction in plasma, and concentrations sufficient to **at least double GCase activity** (*Movement Disorders* 2023, via ResearchGate summary).
- **Phase IIb ACTIVATE (NCT05819359): 273 genetically confirmed GBA-PD patients, 85 clinical sites, 11 countries (Europe + North America).** Result, announced June 2026: the trial **did not meet its primary endpoint or key secondary efficacy endpoints** — pariceract "fail[ed] to demonstrate significant differentiation from placebo" on slowing progression. Generally well tolerated, no unexpected safety concerns. **Bial discontinued development of pariceract in this indication** and said it would share the data through scientific meetings and peer-reviewed publications. (European Biotechnology 2026-06-09; Parkinson's News Today 2026-06-15; AdisInsight, updated 2026-08-24, lists the program as Discontinued for Parkinson's disease, with an expanded-access programme completed 2026-08-10 and Phase I trial terminations in July 2026.)
- **What this means for us:** the GCase-activation hypothesis has now been tested at Phase 2b in the exact population (GBA-PD) and failed on efficacy despite demonstrated target engagement. That does not prove the mechanism is wrong — it proves that **doubling GCase activity, as pariceract did it, did not slow Parkinson's progression in that trial**. Any new direction must answer ACTIVATE explicitly: different molecule, different population, different endpoint, or a combination — with a pre-specified reason to expect a different outcome, not a hope. Do not present the 2019 application's screening bins as if ACTIVATE never happened.

---

## 7. Placement — Parkinson's / Gaucher / lysosomal program in the neurodegeneration track

**Placement:** this brief opens a **Parkinson's / Gaucher / lysosomal program section** in the neurodegeneration track, alongside the Alzheimer's brief (`brief-alzheimers.md`, Pharnext JP6062995B2) and the ALS briefs (`brief-als.md`, `brief-als-agi183.md`). The three programs are kept strictly separate — separate files, separate chats, separate repos — with cross-links only where a mechanism is genuinely shared (below).

**Portfolio overlap (verified):**

| Link | Status |
|---|---|
| **Parkinson's disease** | New disease program. Biota / Parkinson's interest already exists in the portfolio (per `brief-alzheimers.md` §5.2), but Biota has no series number either. **No W3 series number for Parkinson's — do not adopt S34/S35 from any `series.json`.** |
| **Gaucher disease** | New disease name for the portfolio. No existing program, no data beyond this application. A rare-disease program (lysosomal storage disorder) — different development logic from the common-disease Parkinson's program (small population, enzyme biology, existing ERT/SRT standards of care). Do not merge the two into one "program" without saying which disease is meant. |
| **Alzheimer's brief** | Genuine mechanistic touchpoints, thematic only: the Alzheimer's patent's protein-folding arm names **PARK2** (α-synuclein clearance) and **GSK-3β**; its related-diseases definition includes Parkinson's and Lewy body dementia — but that is claim scope, not evidence, and the Alzheimer's patent contributes no Parkinson's data. The shared biology is **proteostasis failure** (misfolded-protein accumulation) — lysosomal in this brief, proteasomal/aggregation in Alzheimer's. |
| **ALS briefs** | Thematic only: the ALS program's apoptosis axis (BCL-2 family, Akt/Bad, mitochondrial permeabilisation) and this brief's lysosomal axis are both organelle-quality-control biology, and both programs use iPSC-derived human neurons as a platform. No shared compound, no shared target, no shared data. A lysosomal-health readout panel (§10.1) is the one concrete bridge worth testing. |
| **Lewy body disease / dementia with Lewy bodies, multiple system atrophy** | Named in this application's disease list and supported by the *GBA1* literature (§5) as part of the *GBA1*-associated neurodegenerative spectrum. Names to track; no program, no data. |
| **Epilepsy, bipolar disorder, schizophrenia, major depression, anxiety, polycystic kidney disease, type 2 diabetes, open-angle glaucoma, multiple sclerosis, multiple myeloma** | Claim-scope list entries only (§3.3). No program, no data, no mechanistic colour in the application. Do not present them as pipeline indications. |

**Bottom line:** the application adds **Parkinson's and Gaucher** as new disease programs (lysosomal track), strengthens the **proteostasis** framing link to Alzheimer's, and adds Lewy body disease / multiple system atrophy as names to track — nothing more. Do not present the 15-disorder claim list as a pipeline.

---

## 8. What a real Parkinson's / Gaucher program would need next

Ordered; each step is a gate, not a formality. Nothing here is approved, funded, or started.

1. **Freedom-to-operate (gate 0).** USPTO Patent Center confirmation of the US abandonment (and whether any revival petition exists); sibling-family sweep — the granted Lysosomal Therapeutics / Bial families (US11400095B2, US11124516B2, US11932645B2, EP3215511B1) and the status of US20190112316A1; written FTO opinion from counsel. **No work that assumes FTO may start before this.**
2. **Recover the structures.** Read the image pages of the publication (Tables 1–4) and identify the exemplified compounds, including whether any of them is LTI-291 / BIA 28-6156 by structure. Until that is done, no compound from this application can be named, ordered, or screened.
3. **Read ACTIVATE.** Obtain Bial's ACTIVATE data as published (scientific meetings / peer-reviewed publication, promised June 2026) and the Phase 1b paper in full (*Movement Disorders* 2023). A real program starts from where Bial stopped: which endpoints, which doses, which subgroups, what biomarker movement, and what the authors themselves conclude about the mechanism.
4. **Independent replication of the screening signal (§4).** Pre-registered replication of the GCase-activation assay (4-MU-β-Glc, saposin C, pH 4.7) with full dose–response curves, EC₅₀ values, replicate counts, vehicle controls, and a positive-control activator — the quantification the application never reported. Success criterion set in advance (e.g. EC₅₀ with confidence interval, not a `+`/`++`/`+++` bin).
5. **Second-system replication — in cells.** The same compounds in a cellular lysosomal assay: GCase activity in patient-derived cells (Gaucher fibroblasts; GBA-PD iPSC-derived neurons), glucosylceramide / glucosylsphingosine clearance, and α-synuclein turnover. A test-tube signal that does not move cellular GlcCer/GlcSph is not a program.
6. **Brain penetration and safety review.** Every candidate needs measured blood–brain-barrier penetration (the Parkinson's indication requires CNS exposure — pariceract's CSF data are the benchmark), a per-compound safety review, and a drug–drug interaction screen before any animal work is designed.
7. **In vivo, properly — only after steps 2–6.** Pre-registered, blinded study in an established GBA model (e.g. GBA-mutant mouse with α-synuclein pathology), with GCase activity, GlcSph, α-synuclein load, and motor/cognitive endpoints — not a one-assay screen. The application contains no animal protocol at all; there is nothing to copy.
8. **Genotype stratification design (§10.3).** Any future GBA-PD work must be designed genotype-first (severe vs mild vs risk-only variants; L444P vs N370S vs E326K), with GCase activity and GlcSph as pre-specified pharmacodynamic gates, learning from ACTIVATE's broad GBA-PD enrollment.
9. **Company context check.** Bial (BIAL, Portugal) now holds the program; its 2020 acquisition of LTI's Parkinson's programmes and its June 2026 discontinuation of pariceract are the current state. Any partnership, licensing, or diligence conversation must start from Bial's current position, not from the 2019 application.
10. **Governance.** No series number, no entity, no raise, no public claim until gates 1–4 are passed and Mike approves the program in writing. Keep Parkinson's/Gaucher strictly separate from the ALS, Alzheimer's, Cancer, Biota, and Fellowship programs.

---

## 9. What NOT to claim

- **No treatment, cure, prevention, diagnosis, or medical-device claims.** Not for Parkinson's, Gaucher, Lewy body disease, dementia, multiple system atrophy, or any of the other 10 claim-list disorders. Not in articles, sites, decks, or social posts.
- **No clinical efficacy.** Nothing in this application is human evidence. Pariceract's Phase 1b target-engagement data (doubling GCase activity) are *Bial's* data — cite them as such, with the ACTIVATE failure attached in the same passage, never as our result and never without the failure.
- **No "GCase activation treats Parkinson's."** The application's theory is "may activate"; its data are test-tube bins; the only clinical test of the hypothesis (ACTIVATE) failed. The accurate sentence is: "Small molecules in this application increased purified GCase activity by up to >10% in a test-tube assay; the clinical candidate from the same program failed its Phase 2b efficacy trial in GBA-PD."
- **No "abandoned, therefore free to use."** Abandonment of this family ≠ FTO (§1.3). No FTO statement until counsel opines in writing.
- **No compound-level claims.** Do not name a compound from Tables 1–4 (structures are images), do not attach a `+++` to a named molecule, do not quote an EC₅₀ (none reported), do not present Example 1's N-(4-butylcyclohexyl) carboxamide as "the active compound" — it is the named exemplar of the scaffold, with no compound-level data attached to it in the text.
- **No "this is the LTI-291 patent."** The name appears zero times in the application; the structure match is unverified (§2.2).
- **No dose guidance.** No numeric dose is stated in the application ([0165] gives only the lowest-effective-dose principle). Never present a dose to a patient, clinician, or investor.
- **Do not present the 15-disorder claim list as a pipeline** (§3.3), the background incidence figure as verified (§3.5), or the `+`/`++`/`+++` bins as potency measurements (§4.2).
- **Do not sum, merge, or cross-attribute.** No family valuation, no combined "neurodegeneration platform" claim, no ALS/Alzheimer's numbers in Parkinson's copy, no Parkinson's numbers in ALS/Alzheimer's copy. Keep the programs apart.
- **Do not adopt S34/S35.** Parkinson's has no W3 series number; the vr-spaces-loop `series.json` numbers are invented.

---

## 10. INSPIRATION — directions inspired by this patent (hypotheses + designs, never the application's claims and never our results)

*Each direction is labeled "inspired by [patent]," carries an evidence grade, and has a confirm-or-kill test. Grade C = no data; a plausible mechanism plus a concrete test. Nothing below is a result.*

### 10.1 Inspired direction — A lysosomal-health readout panel for the neurodegeneration track

**Inspired by US20190092789A1 (Example 4 GCase-activation assay design: fluorogenic 4-MU substrate, saposin C co-factor, pH 4.7 lysosomal conditions).**

- **Hypothesis (Grade C — no data):** A compact lysosomal-health panel — GCase enzymatic activity (4-MU-β-Glc assay as in Example 4), glucosylsphingosine (GlcSph) level, and α-synuclein turnover — measured in iPSC-derived human neurons, will discriminate *GBA1*-variant lines from wild-type lines and will respond to a known tool GCase activator, giving the ALS and Alzheimer's programs a shared lysosomal readout they currently lack. The assay design is the application's; the cross-program panel is new.
- **Experimental design:** (a) iPSC-derived neurons from *GBA1*-variant donors (severe, mild, and risk-only variants) vs isogenic wild-type controls; (b) GCase activity by the Example 4 fluorogenic assay adapted to cell lysates, plus GlcSph by mass spectrometry and α-synuclein by immunoassay; (c) a tool activator arm (a published GCase activator, not a compound from this application) vs vehicle, dose–response, pre-registered; (d) the same panel run in the ALS program's iPSC motor neurons and the Alzheimer's program's iPSC cortical neurons, to test whether lysosomal dysfunction is a shared axis or a Parkinson's-only axis.
- **Falsification test (confirm-or-kill):** the direction is killed if (i) the panel **does not discriminate** *GBA1*-variant from wild-type lines on any of its three readouts, **or** (ii) the tool activator raises test-tube GCase activity but moves **no** cellular readout (GlcSph, α-synuclein) — reproducing the ACTIVATE lesson in vitro — **or** (iii) the panel moves in Parkinson's lines only and is flat in the ALS/Alzheimer's lines (then it is a Parkinson's assay, not a cross-program asset, and the cross-program claim is dropped).
- **ACTIVATE guardrail:** this direction is assay development, not a therapeutic bet. It must not be described as progress toward a treatment.

### 10.2 Inspired direction — GCase activation as a combination partner, not a monotherapy

**Inspired by US20190092789A1 (GCase-activation theory + the application's own combination-therapy section [0126]–[0127]) and by the Alzheimer's brief's low-dose orthogonal-combination logic.**

- **Hypothesis (Grade C — no data):** A tool GCase activator will protect human neurons from lysosomal/α-synuclein stress **only when paired** with an orthogonal mechanism from our existing programs — e.g. an apoptosis-axis modulator from the ALS program (BCL-2 family / Akt-Bad axis) — reproducing a singles-no-effect / combo-works pattern in a neuronal system. The combination logic is the Alzheimer's patent's and this application's §3.4; the lysosomal + mitochondrial pairing is new. The rationale for pairing rather than monotherapy is ACTIVATE: GCase activation alone, at clinically achieved exposures, did not slow Parkinson's progression — so the testable question is whether a second, orthogonal arm changes the outcome.
- **Experimental design:** (a) human iPSC-derived dopaminergic neurons under lysosomal stress (e.g. *GBA1*-variant background, or conduritol B epoxide GCase inhibition as a tool stressor — concentration set by pilot, pre-registered); (b) full dose–response matrix for the GCase activator alone, the apoptosis-axis partner alone, and the pair; (c) endpoints: neuronal survival / neurite-network length, plus the §10.1 lysosomal panel (GCase activity, GlcSph, α-synuclein) and the ALS program's apoptosis-axis panel (Akt/pBad phosphorylation, BH3 profiling of mitochondrial priming); (d) formal synergy quantification (Bliss independence **and** Loewe additivity) with confidence intervals — the quantification neither this application nor the Alzheimer's patent performed.
- **Falsification test (confirm-or-kill):** the direction is killed if (i) the pair shows **no Bliss excess and no Loewe synergy** over the best single agent at any tested dose, **or** (ii) the GCase activator raises GCase activity (target engagement) yet neuronal protection does not change versus the partner alone (target engagement without functional benefit — the ACTIVATE pattern), **or** (iii) the pair protects only at concentrations far above the tool activator's known brain-exposure range (not translatable). Any one of these kills it.
- **Compound rule:** no compound from this application's Tables 1–4 may be named as the activator until its structure is recovered (§8.2) and FTO is cleared (§8.1). Use a published tool activator with a disclosed structure.

### 10.3 Inspired direction — Genotype-stratified, biomarker-gated GBA-PD program design

**Inspired by US20190092789A1 (the GBA1–Parkinson's rationale in [0004]) and by the ACTIVATE trial's outcome (§6).**

- **Hypothesis (Grade C — no data, and a design proposal, not a molecule):** The reason to design any future GBA-PD work genotype-first — severe *GBA1* variants (e.g. L444P) vs mild (e.g. N370S) vs risk-only (e.g. E326K) — with GCase activity and GlcSph as pre-specified pharmacodynamic gates, is that ACTIVATE enrolled a broad, genetically confirmed GBA-PD population (273 patients) and failed overall; a stratified design tests whether the mechanism works in a defined subgroup rather than re-running a broad trial. The stratification idea is new; the variant severity gradient is literature (§5).
- **Experimental design:** (a) a retrospective-analysis question first: when Bial publishes ACTIVATE, test whether any subgroup (by variant severity, baseline GCase activity, or GlcSph) showed a target-engagement-to-outcome relationship; (b) only if a subgroup signal exists, design a prospective, pre-registered, biomarker-gated study in that subgroup, with GCase activity + GlcSph as go/no-go gates before any efficacy readout; (c) the design document must state in advance what subgroup signal would justify proceeding and what would kill the program.
- **Falsification test (confirm-or-kill):** the direction is killed if (i) published ACTIVATE data show **no** subgroup or biomarker signal of any kind (no target-engagement-to-outcome relationship anywhere), **or** (ii) the variant-severity gradient does not predict GCase activity or GlcSph in our own §10.1 panel (the stratification variable is not measuring what it claims to measure). Either kills the stratified-design rationale, and the program stops at assay development (§10.1).
- **Governance note:** this direction is a design document only. It authorises no trial, no enrollment, no patient contact, and no public claim.

---

## Sources

| # | Source | What it supports | Date / as-of |
|---|---|---|---|
| 1 | `~/workspace/user/files/US20190092789A1.pdf` (24 pp., US 2019/0092789 A1) | Everything in §§1.1, 2–4 unless otherwise noted: identity, compound class, exemplars, compositions/kits/methods, disease list, combination agents, Example 4 assay + binned results, claims as published | Published 2019-03-28; read in full (text extraction, 1,539 lines) 2026-11-07 |
| 2 | https://patents.google.com/patent/US20190092789A1/en | §1.2 legal status: US Abandoned 2020-02-01 (failure to respond; non-final actions 2019-02-07, 2019-07-25); WO Ceased; EP Withdrawn; single family application; cited by US11459325B2; sibling grants listed in §1.3 | Page crawled 2026-11-08 01:17 UTC; read 2026-11-07 |
| 3 | https://www.researchgate.net/publication/41533056_The_risk_of_Parkinson's_disease_in_type_1_Gaucher_disease | §5: 444 GD1 patients, 12-year follow-up, adjusted lifetime PD risk ratio 21.4 (95% CI 10.7–38.3) | Bultron et al.; found via search 2026-11-07 |
| 4 | https://dismech.monarchinitiative.org/pages/disorders/Gaucher_Disease.html | §5: biallelic *GBA1* → deficient glucocerebrosidase; *GBA1* variants a major genetic risk factor for parkinsonism | Accessed via search 2026-11-07 |
| 5 | https://www.researchsquare.com/article/rs-10567488/latest.pdf | §5: Sidransky 2009 5–10× PD risk; 5–15% of PD patients carry *GBA1* variants; L444P severity; E326K/LIMP2; *GBA1* spectrum incl. DLB, FTD, MSA | Preprint posted 2026-08-25; **not peer-reviewed**; found via search 2026-11-07 |
| 6 | https://pmc.ncbi.nlm.nih.gov/articles/PMC12478413/ | §5: E326K impairs LIMP2 interaction and lysosomal GCase delivery; 5–20% of PD patients carry a *GBA1* variant | bioRxiv preprint 2025-09-02; **not peer-reviewed**; found via search 2026-11-07 |
| 7 | https://pubmed.ncbi.nlm.nih.gov/38843618/ | §5: GlcSph elevated in GBA-PD; 1,344 PD patients, dried blood spot GCase activity + GlcSph + *GBA1* sequencing | 2024; found via search 2026-11-07 |
| 8 | https://european-biotechnology.com/latest-news/bial-drops-pariceract-after-phase-iib-failure-in-gba-associated-parkinsons/ | §6: Bial discontinued pariceract after Phase IIb failure; ACTIVATE 273 patients, 85 sites, 11 countries; 2020 acquisition of LTI Parkinson's programmes | Published 2026-06-09; found via search 2026-11-07 |
| 9 | https://parkinsonsnewstoday.com/news/bial-drops-parkinsons-therapy-fails-slow-disease-trial/ | §6: ACTIVATE (NCT05819359) missed primary + key secondary endpoints; Phase 1b (40 GBA-PD, 10/30/60 mg × 28 days) reached CSF levels sufficient to double GCase activity | Published 2026-06-15; found via search 2026-11-07 |
| 10 | https://adisinsight.springer.com/drugs/800040602 | §6: LTI-291 profile — originator Lysosomal Therapeutics, developer BIAL; Discontinued for Parkinson's disease; expanded-access programme completed 2026-08-10 | Latest update 2026-08-24; found via search 2026-11-07 |
| 11 | https://newdrugapprovals.org/2026/07/28/pariceract/ | §6: pariceract (INN), BIA 28-6156 / LTI-291, CAS 1919820-28-2, GCase activator, first described by 2017 | Found via search 2026-11-07 |
| 12 | `~/workspace/your_files/bio-research-expansion/brief-alzheimers.md` | Track framing + house rules applied here: no S34/S35 series numbers; every number sourced + dated; filed fact vs proposed plan apart; combination-logic and apoptosis-axis cross-links (§§7, 10.2) | Read 2026-11-07 |
| 13 | `~/workspace/your_files/bio-research-expansion/brief-als.md` | Track framing + house rules; ALS apoptosis-axis panel cross-link (§§7, 10.1–10.2) | Read 2026-11-07 (honesty lines + §§1–6) |

## Verification log (for the parent coordinator)

- **Read in full:** the 24-page application PDF via `pdftotext` (1,539 lines) — title page, background, summary, definitions (§§0012–0101, mostly boilerplate, skimmed), Formula I/II embodiments, therapeutic applications, compositions, kits, Examples 1–4, incorporation by reference, and claims 1, 15–34 (2–14 and 35–40 canceled as published).
- **Verified against the live register:** legal status via Google Patents (crawled 2026-11-08 01:17 UTC) — US Abandoned 2020-02-01 (failure to respond to an office action; non-final actions 2019-02-07 and 2019-07-25), WO Ceased, EP Withdrawn, single family application, no granted member. This is the one brief in the track whose legal status was verified live rather than left unverified.
- **Counted, not copied:** the 15-disorder method-claim list (counted from [0010]/[0103]/claim 34); Table 1 numbered I-1 through at least I-30 (I-1, I-2, I-8, I-30 legible; intervening structures are images); Table 3 entries 3A (ESI-MS m/z 347, M+Na) and 3B (m/z 309, M−H) with NMR data; Table 4 activation bins (+ <5%, ++ 5–10%, +++ >10%) at 1.0 and 0.1 µM, with legible cLogP 0.5–2.8, PSA 61.8–89.5, solubility 0.3–58.0 µg/mL ranges.
- **Confirmed against the document:** the "may activate glucocerebrosidase (GCase)" theory wording ([0102]); the GCase assay protocol in full ([0190]–[0191]: 10 nM GCase, 100 nM saposin C, 4-MU-β-Glc 2 mM, pH 4.7, 30 min pre-incubation, 15 min reaction, 365/440 nm); the 8-point dose–response curves mentioned but not reported ([0191]); the kit disclosure ([0167]); the combination second agents for Gaucher and Parkinson's ([0127]); the dementia subtypes ([0119]); the Gaucher background including the 1-in-20,000 figure ([0003]).
- **Confirmed absent:** "LTI-291" / "pariceract" / "BIA 28" appear zero times in the extracted text (text search, 2026-11-07). No EC₅₀, no numeric dose, no cell/animal/human data anywhere in the document.
- **Literature-verified (independent searches, 2026-11-07):** the GBA1–Gaucher–Parkinson's link (biallelic → Gaucher; heterozygous = most common PD genetic risk factor; Sidransky 2009 5–10×; GD1 risk ratio 21.4, 95% CI 10.7–38.3; 5–20% carrier frequency); the E326K/LIMP2 mechanism (preprint); and the LTI-291/Bial record — 2020 acquisition, Phase 1b target engagement (doubling GCase activity, 40 patients), Phase IIb ACTIVATE failure (273 patients, NCT05819359), discontinuation June 2026 (corroborated by two independent news sources + AdisInsight).
- **NOT verified (flagged in the brief):** individual compound structures in Tables 1–4 (images); Table 1's exact compound count; per-compound Table 4 rows; any EC₅₀ or dose–response numbers; the 1-in-20,000 Gaucher incidence figure; the status of sibling filing US20190112316A1; whether LTI-291 falls within Formula I/II; the full text of the Phase 1b *Movement Disorders* 2023 paper (summarised second-hand) and of the ACTIVATE publication (promised, not yet located).
