# Independent verification + red-team report — Research Lab Loop 2, Worker B3 (Track B)

**Role:** independent verification / red team. The job was to try to break the loop's load-bearing claims. A claim that survives is worth carrying forward; a claim that falls is a successful result for this task, not a failure.
**Date:** 7–8 Nov 2026 (searches run 8 Nov 2026, ~03:15 UTC).
**Sources read first:** `research-lab-loop/dossier/pattern-deep-dive-01` through `-04`, `flagship-akt-bad-bcl2.md` §§1–8, `cross-disease-patterns.md`.
**Method:** `browser.search` (general web + PubMed/PMC-indexed results) and `browser.open`/`browser.find` on primary full texts (Nature Neuroscience article, PMC full texts, patent PDFs). Every verdict below cites the exact source found. No citation, statistic, or URL is invented. Where a search found nothing, the queries used are recorded verbatim.

---

## 1. Per-claim verdicts

### (a) GAP-FLAG-2 — the negative novelty claim: "no peer-reviewed study proposes Akt/Bad phosphorylation as a predictive biomarker in ALS or any neurodegenerative disease"

**Verdict: REFUTED in substance; the narrow "peer-reviewed" wording survives only as a technicality. The novelty claim (Discovery 5) falls and must be withdrawn as stated.**

**What was found — a prior public proposal of exactly this biomarker in ALS:**

- **Ovadia, Cohen, Herkel, Margalit & Pevsner-Fischer — "Use of Akt phosphorylation as a biomarker for prognosing neurodegenerative diseases and treating same."** Patent family with priority **23 May 2011**:
  - WO2012160563A2, filed 23 May 2012, published 29 Nov 2012.
  - **EP 3263127 B1, granted 21 Aug 2019.**
  - **US 10,288,622 B2, granted 14 May 2019, status Active** (assignees Yeda Research and Development Co. Ltd. / Universitätsklinikum Hamburg-Eppendorf).
  - Claims, quoted from the patent text: *"a method for prognosticating the progression of a neurodegenerative disease in a subject, comprising: (a) assessing the value of at least one marker selected from: pAkt and pAkt:tAkt ratio, in a bodily sample derived from the subject"*; *"a level of pAkt or pAkt:tAkt ratio significantly below a control value indicates a rapid disease"*; and a method *"for assessing responsiveness to treatment"* with the peptide of the invention using pAkt/pAkt:tAkt. The specification states: *"Akt phosphorylation and pAkt:tAkt ratio distinguish between fast progression to low progression of ALS"* and *"high levels of pAkt and high levels of pAkt:tAkt ratio (e.g. above 1) correlate with responsiveness to treatment of ALS."* Supporting data in the patent: pAkt correlates with disease state in SOD1 mice (P = 0.01); the Stressin-1 peptide (LPPLPYP) raises pAkt.
  - Source: https://patents.google.com/patent/US10288622B2/en ; https://patents.google.com/patent/EP2715350A2/en ; EP 3263127 B1 PDF at https://patentimages.storage.googleapis.com/7c/a6/41/99342978e1bcb5/EP3263127B1.pdf

**Qualifications that limit — but do not save — the novelty claim:**

1. It is a **patent, not a peer-reviewed study**. Across five search phrasings I found no peer-reviewed journal article by Ovadia et al. proposing pAkt as an ALS biomarker. The literal sentence "no *peer-reviewed study* proposes…" was therefore not directly falsified by a journal article. But a granted patent family is prior art, publicly disclosing the idea since 2012 — fourteen years before the flagship paper (Apr 2026). A novelty claim that survives only because the prior proposal was filed at a patent office rather than published in a journal is not a novelty claim worth carrying.
2. **Direction differs.** The patent says *high* pAkt correlates with responsiveness to its Akt-raising peptide; the flagship predicts *low* pAkt/pBad gains most from BCL-XL stabilisation. Different intervention, opposite direction of the prediction. The patent does not propose the flagship's specific mechanism.
3. **No BAD, no BCL-2.** The patent proposes pAkt only. It never mentions pBad, BAD phosphorylation, or BCL-2-family therapy. The *narrowest* reformulation — "no prior proposal of Akt/Bad phosphorylation status as a stratification biomarker specifically for BCL-2-family enhancement therapy in neurodegeneration" — was not falsified by anything I found, but it has not been established by a documented search either; it needs its own search, run and recorded, before it is asserted.
4. The descriptive foundation is peer-reviewed and old: Leger et al., *FASEB J* 2006;20(3):583–585 (lower phosphorylated Akt protein in ALS patient skeletal muscle vs controls) and Dewil et al., *Neuropathol Appl Neurobiol* 2007;33(5):499–509 (Akt pathway dysfunction in motor neurons of sporadic and familial ALS patients). Those papers describe Akt dysfunction; they do not propose a biomarker. They are cited inside the patent.
5. **Phospho-BAD as a predictive biomarker exists — in cancer, not neurodegeneration.** US 9,063,143 B2 (Moffitt Cancer Center; "BAD protein phosphorylation status … represents a biomarker that predicts platinum sensitivity") and the underlying work ("BAD phosphorylation determines ovarian cancer chemo-sensitivity and patient survival"; 47-gene BAD-pathway signature associated with survival in 838 patients with ovarian, breast, colon, and brain cancer). This does not touch the neurodegeneration claim, but it kills any broader phrasing such as "phospho-BAD has never been proposed as a predictive biomarker" without the neurodegeneration qualifier.
   Source: https://patents.google.com/patent/US9063143B2/en

**Searches run for (a) (verbatim queries):** "Akt Bad phosphorylation predictive biomarker ALS amyotrophic lateral sclerosis"; "pBad phospho-BAD biomarker neurodegeneration Alzheimer Parkinson stratification"; "Stressin-1 peptide Akt phosphorylation ALS Leger pAkt prognostic biomarker paper"; "Ovadia Herkel Cohen Akt phosphorylation ALS prognosis fast slow progression peer-reviewed study"; "Pevsner-Fischer Ovadia Akt phosphorylation SOD1 mice ALS skeletal muscle biomarker journal article"; "\"phospho-BAD\" OR \"phosphorylated BAD\" predictive biomarker treatment response".

**Consequences:**
- Discovery 5's novelty claim is withdrawn as stated. H-FLAG-1 itself is unaffected as a hypothesis — the hypothesis does not depend on being first — but the dossier must stop calling it novel.
- **New flag for counsel (not a legal conclusion):** US 10,288,622 B2 is active and claims methods of using pAkt/pAkt:tAkt to assess responsiveness to ALS treatment. Any future pAkt-stratified ALS work should be checked against it before commercial steps. No freedom-to-operate conclusion is asserted here.

### (b) Bye et al. 2026 (Nat Neurosci 29:40–52) — combination, panel, endpoint, synergy

**Verdict: VERIFIED on the facts. Formal synergy (Bliss excess with CI) was NOT demonstrated — only combination benefit. The dossier's own "partial" rating for rubric criterion 2 is correct.**

**Verified facts (primary source read in full):** Bye et al., "Large-scale drug screening in iPSC-derived motor neurons from sporadic ALS patients identifies a potential combinatorial therapy," *Nat Neurosci* 2026;29(1):40–52. DOI 10.1038/s41593-025-02118-7, PMID 41286450, published online 24 Nov 2025.
- iPSC library from **100 patients with sporadic ALS** (plus 11 suspected monogenic cases and 25 healthy controls).
- **107 drugs** previously tested in ALS clinical trials screened at 2.5 µM; **97% failed** to mitigate neurodegeneration; only **riluzole, baricitinib, and memantine** rescued motor-neuron survival.
- **Survival endpoint:** LD50 (time to 50% decline in neurite length) by longitudinal live-cell imaging; SALS motor neurons showed reduced survival and accelerated neurite degeneration correlating with donor survival.
- **Combination:** "Combinatorial testing of the three effective drugs (riluzole, memantine and baricitinib) demonstrated that combinations of these drugs significantly increased the survival of SALS motor neurons"; triple combination: **100% of donors responding, minimum rescue 16.5 days**; memantine + riluzole +12.5 days (P = 0.0109). A secondary review reports triple-combination LD50 extension of 30.3 days (p < 0.0001) — that figure comes from the review (Therapeutic frontiers in ALS, PMC13292465), not from text I read in the primary paper, so cite it as review-reported.
- Source: https://www.nature.com/articles/s41593-025-02118-7 ; https://pubmed.ncbi.nlm.nih.gov/41286450/

**Synergy check (full-text search of the Nature article):** zero occurrences of "Bliss"; zero combination-index analysis; the single "synerg*" hit in the entire article is a Discussion sentence using the word colloquially: *"With each drug acting through different mechanisms, the synergistic benefits afforded by combining the treatments strongly support the use of combinatorial therapies in ALS…"* — no formalism, no confidence interval, no test against an additivity null. The paper demonstrates **combination benefit** (combination > singles, statistically significant), not **synergy** in the Bliss/Loewe/ZIP sense the rubric demands.

**Precision correction:** the dossier's "100-donor iPSC panel" is the library size. The drug screen itself was run on motor neurons from **16 SALS donors**. The dossier should state the screen n (16) alongside the library n (100) wherever the Bye result is cited, and state the donor n for the combination validation rather than implying all 100 were combination-tested.

### (c) AZD5991 — Phase 1 troponin signal (54/65, 83.1%) and halted development

**Verdict: VERIFIED exactly, including the dossier's own caveats.**

Desai et al., "A Phase 1 First-in-Human Study of the MCL-1 Inhibitor AZD5991 in Patients with Relapsed/Refractory Hematologic Malignancies," *Clin Cancer Res* 2024;30(21):4844–4855. DOI 10.1158/1078-0432.CCR-24-0028, PMID 39167622, PMCID PMC11528199, NCT03218683.
- Post-hoc retrospective high-sensitivity troponin T analysis: **elevated troponin T in 14/31 (45.2%) patients before any AZD5991 dose and in 54/65 (83.1%) after any dose at/after Cycle 1.**
- Protocol-recorded adverse-event rate was far lower: asymptomatic troponin I/T elevation in **8/78 (10.3%)** patients. The 54/65 figure is a retrospective subset (patients with available samples), not all 78 enrolled — the dossier's V1 note already states this correctly.
- Halted development, quoted: *"Treatment with AZD5991 was associated with high incidence of laboratory troponin elevation and a low overall response rate… These issues precluded further clinical development of AZD5991."* The study was discontinued to evaluate the troponin elevations and assess therapeutic index.
- Response: 3 objective responses in 78 enrolled patients (3.8%), all in myelodysplastic syndrome — the dossier's "3.9%" rounding note is accurate (3/78 = 3.85%).
- Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC11528199/ ; https://pubmed.ncbi.nlm.nih.gov/39167622/

### (d) PHP.eB primate-transfer failure — Hordeaux 2018 / Matsuzaki 2018, Ly6a

**Verdict: VERIFIED in substance, with a PRECISION CORRECTION on the capsid named.**

- Hordeaux et al. 2018, *Mol Ther* 26(3):664–668 — "The neurotropic properties of AAV-PHP.B are limited to C57BL/6J mice": the BBB advantage of PHP.B over AAV9 did not translate to BALB/c mice or to a non-human primate model.
- Matsuzaki et al. 2018, *Neurosci Lett* 665:182–188 — "Intravenous administration of the adeno-associated virus-PHP.B capsid fails to upregulate transduction efficiency in the marmoset brain."
- Mechanism: Hordeaux et al. 2019, *Mol Ther* 27:912–921 — "The GPI-linked protein LY6A drives AAV-PHP.B transport across the blood-brain barrier" (also Huang et al. 2019). LY6A is a mouse-specific endothelial protein, absent from primate endothelium — which explains the transfer failure.
- Source (review corroborating all three): https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2021.679483/full ; commentary: https://pmc.ncbi.nlm.nih.gov/articles/PMC6520466/

**Correction:** the 2018 papers tested **AAV-PHP.B, not PHP.eB**. PHP.eB is a further-evolved PHP.B derivative (Chan et al. 2017) that shares the Ly6a dependence, but the dossier's citation "Hordeaux et al. 2018; Matsuzaki et al. 2018" attached to "PHP.eB" is a capsid mismatch. Fix: cite the 2018 papers for PHP.B and cite Chan et al. 2017 + Hordeaux et al. 2019 for PHP.eB inheriting the Ly6a mechanism. The conclusion (strain-specific, no primate transfer) is unchanged.

### (e) PXT864 current development status — after exploratory Phase 2 (PLEODIAL)

**Verdict: RESOLVED — worse than "UNVERIFIED". Development in Alzheimer's was STOPPED by Pharnext on 14 Feb 2023. No Phase 3 ever occurred.**

- Pharnext press release, 14 Feb 2023: *"the Company's Board of Directors has decided to stop the development of its drug candidate PXT864 in Alzheimer's disease. Although PXT864 has generated interesting and encouraging preclinical and clinical results, these remain insufficient for commercialization in the short or medium term."* Reason given: inability to sign an industrial partner to license and continue development; the company refocused all resources on PXT3003 (CMT1A). Pharnext said it would continue seeking a partner for PXT864 in Alzheimer's, and was considering development in ALS (in-licensing or internally after PXT3003 Phase 3).
- July 2023: Bpifrance waived a €7.95M loan tied to the PXT864/DIPPAL programme (24 Feb 2023 announcement referenced in the same release).
- Highest phase reached: **Phase 2** — PLEODIAL-I (NCT02361424) and PLEODIAL-II (NCT02361242), completed; drug databases list clinical status **Inactive**. No Phase 3.
- Preclinical leg verified: Chumakov et al. 2015, *Sci Rep* 5:7608, DOI 10.1038/srep07608, PMCID PMC5378993, PMID 25566747 — baclofen + acamprosate synergistically protected neurons and endothelial structures in vitro against Aβ oligomers and alleviated cognitive deficits in two rodent AD models.
- Phase 2 reporting verified: Pharnext CTAD 2016 — exploratory, single-blind, 45 treatment-naïve mild-AD patients, 36 weeks; well-tolerated; ADAS-Cog-11 declined less than **historical placebo** (no concurrent control arm).
- Sources: https://financialreports.eu/filings/pharnext/regulatory-filings/2023/2813829/ ; https://www.fiercebiotech.com/biotech/pharnext-ditches-alzheimers-plans-saying-more-development-would-be-too-costly ; https://pmc.ncbi.nlm.nih.gov/articles/PMC5378993/

**Consequences for the dossier:**
- Deep dives #2/#3 and cross-disease Pattern 2/3 must update "later development status UNVERIFIED" to "development in Alzheimer's stopped Feb 2023; no Phase 3; partner sought; ALS indication under consideration by Pharnext."
- The rubric's Instance 1 (PXT864) is now a **stopped programme**, not a live precedent. It remains a valid preclinical + exploratory Phase 2a case, but the dossier should record that it died for commercial reasons and that the Phase 2 efficacy signal rested on a historical-placebo comparison (no concurrent control). Edison's assessment ("Phase IIa completed but missed endpoint, seeking partner") should be checked against the CTAD data before either phrasing is quoted as fact.

### (f) AGI-183 — any public record as a BCL-XL stabilizer or ALS compound

**Verdict: CONFIRMED ABSENT. No public record exists. GAP-FLAG-4 stands, and the search is now independently re-run.**

**Searches run (verbatim):** `"AGI-183" BCL-XL stabilizer ALS compound`; `"AGI-183" compound`. (Plus the flagship's own 7 Nov 2026 public search, which also found nothing.)

**What the searches returned instead (all unrelated):**
- **AG-183 / Tyrphostin 51** (CAS 122520-90-5, C13H8N4O3, MW 268.2) — an EGFR kinase inhibitor, IC50 0.8 µM in A431 cells. Different identifier (AG-, not AGI-), different target, different compound.
- **E3 Ligase Ligand-Linker Conjugate 183** (CAS 3081572-35-9) — a PCSK9 autophagy-degrader conjugate. Unrelated.
- **RNF183** — a real Bcl-xL-related protein, but an E3 ubiquitin ligase that **degrades** Bcl-xL during prolonged ER stress (PNAS 2018;115(12):E2762–E2771, PMID 29507230). It is a protein, not a compound, and its pharmacology is the opposite direction to stabilisation.
- NSC 183, GPR183, K-183 (HDAC inhibitor), and assorted non-scientific hits. No structure, synthesis, vendor listing, patent, or publication for any "AGI-183" BCL-XL stabiliser or ALS compound.

**Additional red-team note:** no BCL-XL *stabiliser* class exists in the public record at all as far as these searches show. The entire known BCL-XL small-molecule pharmacology is inhibitory (navitoclax, A-1155463, A-1331852, WEHI-539). The nearest real biology to "BCL-XL stabilisation" is the *removal* of a degradation signal (RNF183), which is a different mechanism from a stabilising small molecule. Gate 0b (demonstrate enhancement of BCL-XL function) is therefore not a routine characterisation step — it is the invention of a new pharmacology, and it is the programme's hardest gate.

### (g) Navitoclax thrombocytopenia — 53.8% all-grade, 38.5% grade 3/4 (de Vos et al. 2021)

**Verdict: VERIFIED EXACTLY from the primary full text.**

de Vos et al., "Safety and efficacy of navitoclax, a BCL-2 and BCL-XL inhibitor, in patients with relapsed or refractory lymphoid malignancies: results from a phase 2a study," *Leuk Lymphoma* 2021;62(4):810–818. DOI 10.1080/10428194.2020.1845332, PMID 33236943, PMCID PMC9257998, NCT00406809, N = 26.
- Table 2 (treatment-emergent AEs related to navitoclax): **thrombocytopenia, all grades: 14/26 (53.8%)**; **grade 3/4 thrombocytopenia: 10/26 (38.5%)**. Abstract confirms grade 3/4 thrombocytopenia 38.5% and neutropenia 30.8% as the most common grade 3/4 TRAEs.
- Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC9257998/
- Note the small denominator: both percentages rest on 14 and 10 patients respectively. The figures are correct as cited; they should not be quoted without the N = 26 context in any external use.

---

## 2. Stress-test of the falsification batteries — weakest test per deep dive

### Deep dive #1 (BCL-2 / apoptosis axis) — weakest: F1, the treatment × stratum interaction test

**Why it is the weakest.** F1 as designed cannot discriminate between its own failure modes. The stratification variable is dichotomised by a median split from the pilot cohort, so a null interaction is as consistent with (i) a wrong cut-point, (ii) a noisy phospho assay, (iii) the wrong phospho site (S136 vs S112 vs S473), or (iv) a genuinely false hypothesis — and the test reports all four as the same outcome ("biomarker fails"). It also tests the interaction while the combination may work overall, so a real treatment effect plus a noisy biomarker reads as a biomarker failure. No minimum meaningful interaction effect is quantified anywhere in the dive (the flagship mentions a pre-specified minimum but never states the number). A null F1 would be argued about, not accepted.

**Stronger replacement.** Make the primary stratification analysis **continuous, not dichotomised**: treatment × continuous pBad (S136) interaction on the EC50 trajectory as the primary test, with the median-split analysis demoted to a sensitivity check. Pre-register a quantitative minimum meaningful interaction (e.g. a stated EC50 difference between the lowest and highest pBad quartiles). And add a **within-line mechanistic manipulation** that bypasses stratification noise entirely: a PI3K-inhibitor arm that pharmacologically lowers pAkt/pBad in the *same* donor lines — if lowering pAkt increases the stabiliser arm's benefit within the same cells, the Akt→Bad→BCL-XL chain is confirmed directly; if it does not, the chain is wrong regardless of what the between-line stratification shows. Require the interaction to replicate under a second stressor (oxidative stress, not only glutamate) before any biomarker language is used.

**Secondary weakness in the same dive:** the "stabiliser test" sets no quantitative bar for what counts as enhancement. Strengthen it: pre-specify fold-change thresholds (e.g. ≥1.5× BAX retrotranslocation rate and ≥20% BH3 EC50 shift at a stated concentration, with a dose–response) and require the effect to be abolished by BCL-XL knockdown as on-target proof. Binding without a pre-specified functional threshold is not a test.

### Deep dive #2 (Alzheimer's three-network model) — weakest: the Stage 1 network-mapping study as falsification

**Why it is the weakest.** Stage 1 is a literature review, not an experiment, and "no credible angiogenesis evidence in ALS" is a judgement call with no pre-specified evidence threshold, no inclusion criteria, and no independent rater. Two reviewers could reach opposite verdicts from the same literature and both be defensible — so the test cannot kill the transfer cleanly. Worse, the built-in response to a failed leg ("narrow to two networks") is goalpost-moving: the hypothesis was *three* networks; dropping a leg after the fact and declaring the remainder a success makes the framing effectively unfalsifiable.

**Stronger replacement.** (1) Pre-register the mapping protocol *before* it runs: explicit inclusion/exclusion criteria, a quantitative evidence bar (e.g. ≥2 independent in-vivo studies showing vascular dysfunction causally linked to neuronal loss in ALS, not merely correlated), and a second independent rater with disagreements resolved by a stated rule. If the angiogenesis leg fails the bar, the hypothesis is **re-stated as a two-network hypothesis with new predictions** and the three-network claim is recorded as falsified — not silently narrowed. (2) Add a direct experimental falsifier at Stage 2: test the three-network combination against the **same combination minus the angiogenesis drug**, head-to-head. If removing the angiogenesis drug changes nothing on survival or priming, the third leg contributes zero and the three-network claim fails *even if the combination works* — which is the discrimination the current design lacks.

### Deep dive #3 (repurposing + combination logic) — weakest: Test 1, retrospective validation of the rubric

**Why it is the weakest.** It is circular. The rubric's criteria were constructed from exactly these cases (PXT864, Bye) and the negative controls (computational-only candidates) were selected knowing they score 0 on criterion 1. Passing a test built from your own training examples proves the rubric can reproduce its authors' judgements, not that it can predict anything. With n = 5 hand-picked cases and no blinding, a pass is near-guaranteed and a fail would be more informative than a pass.

**Stronger replacement.** Pre-register the rubric (criteria, thresholds, scoring rules) and apply it **blind to a held-out set of ≥10 historical repurposing combinations** — successes and failures the rubric's authors did not use to build it — scored by an independent rater who does not know the outcomes. Require a pre-specified rank correlation with actual outcomes (e.g. Spearman ρ ≥ 0.6) before the rubric is used to choose experiments. Strengthen Test 2 the same way: test **all three** ranked combinations (top, middle, bottom) and require monotone rank-order correspondence on the primary endpoint (top > middle > bottom), not merely top > bottom — a top-vs-bottom-only comparison cannot detect a rubric that ranks noise.

### Deep dive #4 (AAV delivery) — weakest: the Stage 1 bake-off decision rule ("best neuron-to-cardiomyocyte selectivity ratio advances")

**Why it is the weakest.** Three defects. (1) It is **relative, not absolute**: if all three capsids are poor, the best of three still advances, so the rule can rank but cannot kill the gene-therapy arm — the kill condition stated elsewhere ("no capsid achieves an acceptable off-target profile") has no number attached to it here. (2) It tests **tropism, not delivery**: transducing iPSC cardiomyocyte-lineage cells in a dish says nothing about biodistribution after systemic or intrathecal dosing, and there is no blood–brain-barrier component in the assay at all — no endothelium, no BBB crossing measured. A capsid can win the dish ratio and still never reach a motor neuron in vivo. (3) The off-target sentinel (cardiomyocyte-lineage cells) is a cell line, not a tissue; MCL1 cardiac risk in vivo involves mitochondrial homeostasis in mature cardiomyocytes, which iPSC-derived cells approximate poorly.

**Stronger replacement.** Pre-specify an **absolute bar**: neuron-to-cardiomyocyte transduction ratio ≥10:1 **and** absolute motor-neuron transduction ≥50% at a stated MOI — if no capsid clears it, the gene-therapy arm stops; no "best of a bad lot" advance. Add a **BBB-transwell arm** (human brain-endothelial monolayer) as a delivery gate alongside the tropism assay, so the bake-off measures both reaching the CNS and entering the right cells. Include AAV9 with a clinically relevant route proxy in the comparison set, and state the route (intrathecal vs IV) the bake-off is meant to inform before it runs.

---

## 3. The two strongest objections

### Strongest objection to the BCL-2 programme as a whole

**There is no drug.** The programme's lead arm (AGI-183, a BCL-XL stabiliser) has no structure, no synthesis, no vendor, no publication, and no public record of any kind — and no BCL-XL stabiliser pharmacology is known to exist anywhere in the literature; the entire known BCL-XL small-molecule field is inhibitory, and the nearest real biology (RNF183) *degrades* Bcl-xL. The programme is therefore not a drug-development problem but a **drug-discovery problem**: it must invent a new pharmacology before it can test any of its hypotheses. Everything downstream — the Bliss synergy timecourse, the MOMP 0.764 → 0.040 prediction, the pAkt/pBad stratification — is conditional on that invention, and the model numbers themselves come from code that is unavailable and cannot be reproduced (GAP-FLAG-1). In a real lab meeting the question is: "You have no compound, no delivery (AAV6 unjustified, no route, no dose), and a payload (MCL1 overexpression) with a known oncogenic signal in mice — what exactly would you test first, and why would anyone fund the experiment before those three are solved?" The programme's correct answer is its Phase 0 gates, but as framed it leads with model predictions that are its least trustworthy element. **The programme as designed is currently untestable, not merely untested** — and that is the objection most likely to kill it in a room.

### Strongest objection to the repurposing rubric (deep dive #3)

**It measures how much testing has already been done, not how good the idea is.** Criteria 1 and 2 (phenotypic evidence, formal synergy) are defined so that any designed-but-unrun programme scores ~0 by construction, while any already-tested combination scores highly — so the rubric systematically penalises novelty and rewards incumbency, which is the opposite of what a discovery programme needs. Its flagship application (ranking the loop's own BCL-2 programme last) looks like rigour but is costless: the outcome was guaranteed by the scoring rules before any science was done. And its "validation" (Test 1) is circular, as detailed above. A second, internal contradiction sharpens the point: the rubric's own rationale states that a combination's risk is *dominated by interaction risk rather than single-drug risk* — yet none of its five criteria scores interaction risk. Safety is scored per drug, in isolation, which is precisely the quantity the rubric says does not dominate. A rubric that cannot distinguish "promising but untested" from "bad idea," and that never scores the risk it claims matters most, will mislead any experiment-selection decision it is used for.

---

## 4. Summary table — what survived vs what fell

| # | Claim | Verdict | One-line basis |
|---|---|---|---|
| (a) | GAP-FLAG-2: no prior proposal of Akt/Bad as predictive biomarker in ALS / neurodegeneration | **REFUTED (substance)** / narrow wording survives as technicality | Ovadia et al. patent family (priority 2011; EP 3263127 B1 granted 2019; US 10,288,622 B2 granted 2019, active) proposes pAkt/pAkt:tAkt as ALS prognostic + treatment-responsiveness biomarker. No peer-reviewed journal article found; patent is prior art regardless. Discovery 5 novelty claim must be withdrawn as stated. |
| (b) | Bye et al. 2026: riluzole + memantine + baricitinib; 100-donor panel; survival endpoint; formal synergy | **VERIFIED (facts); synergy NOT demonstrated** | Nat Neurosci 2026;29:40–52, PMID 41286450. 100-donor library, 107 drugs, 3 hits, LD50 survival endpoint, combination benefit confirmed. Full text contains no "Bliss" and no combination-index analysis; "synergistic" appears once, colloquially, in Discussion. Precision fix: screen used 16 donors, not 100. |
| (c) | AZD5991: troponin 54/65 (83.1%), development halted (Desai 2024) | **VERIFIED exactly** | Clin Cancer Res 2024;30:4844–4855, PMID 39167622, PMC11528199. Post-hoc hs-troponin T 54/65 (83.1%) after any dose; 14/31 pre-dose; "These issues precluded further clinical development." Dossier's caveats confirmed. |
| (d) | PHP.eB primate-transfer failure (Hordeaux / Matsuzaki 2018; Ly6a) | **VERIFIED in substance; citation correction needed** | Hordeaux 2018 Mol Ther 26:664–668; Matsuzaki 2018 Neurosci Lett 665:182–188; Ly6a mechanism Hordeaux 2019 Mol Ther 27:912–921. Correction: 2018 papers tested PHP.B, not PHP.eB; PHP.eB inherits Ly6a dependence (Chan 2017). |
| (e) | PXT864 status after PLEODIAL Phase 2 | **RESOLVED — development STOPPED 14 Feb 2023; no Phase 3** | Pharnext stopped PXT864 in Alzheimer's ("insufficient for commercial exploitation", no licensing partner); seeking partner; ALS under consideration. Highest phase: Phase 2 (NCT02361424 / NCT02361242). Chumakov 2015 Sci Rep 5:7608 verified. |
| (f) | AGI-183 as BCL-XL stabiliser / ALS compound — any public record | **CONFIRMED ABSENT** | Two independent search phrasings, zero relevant records. Nearest hits are unrelated (AG-183/Tyrphostin 51 EGFR inhibitor; RNF183, a Bcl-xL-degrading ligase). GAP-FLAG-4 stands. |
| (g) | Navitoclax thrombocytopenia 53.8% all-grade, 38.5% grade 3/4 (de Vos 2021) | **VERIFIED exactly** | Leuk Lymphoma 2021;62:810–818, PMID 33236943, PMC9257998, Table 2, N = 26: 14/26 (53.8%) all-grade, 10/26 (38.5%) grade 3/4. |
| — | Dive #1 weakest test: F1 interaction | **Replace** | Median-split interaction cannot discriminate cut-point/assay/site error from a false hypothesis. Replace with continuous-interaction primary test + within-line PI3K-inhibitor manipulation + second-stressor replication. |
| — | Dive #2 weakest test: Stage 1 network-mapping falsification | **Replace** | Literature-review judgement with no threshold; "narrow to two networks" is goalpost-moving. Replace with pre-registered mapping protocol + quantitative bar + minus-one-drug head-to-head experiment. |
| — | Dive #3 weakest test: Test 1 retrospective validation | **Replace** | Circular (rubric built from its own test cases, n = 5, unblinded). Replace with blinded held-out set ≥10 combinations, pre-specified rank correlation; require monotone top > middle > bottom in Test 2. |
| — | Dive #4 weakest test: bake-off "best ratio advances" | **Replace** | Relative rule cannot kill the arm; tests tropism, not delivery (no BBB component). Replace with absolute bar (≥10:1 selectivity, ≥50% motor-neuron transduction) + BBB-transwell gate. |

---

## 5. Corrections and follow-ups the coordinator should carry

1. **Withdraw Discovery 5's novelty claim** (flagship §4/§5, deep dive #1, cross-disease Pattern 6). Reframe, only after a documented search: "no prior proposal of Akt/Bad status as a stratification biomarker *specifically for BCL-2-family enhancement therapy* in neurodegeneration was found" — with the search strategy, databases, terms, and dates recorded. Note the Ovadia patent in the same passage, including its opposite direction (high pAkt → responsiveness to an Akt-raising peptide) and the active US patent (10,288,622 B2) as a counsel flag.
2. **Update PXT864 status everywhere** (deep dive #2, deep dive #3 Instance 1, cross-disease Patterns 2/3): development in Alzheimer's stopped 14 Feb 2023; no Phase 3; partner sought; ALS under consideration. Record that the Phase 2 efficacy signal used a historical-placebo comparison with no concurrent control, and check Edison's "missed endpoint" characterisation before quoting it.
3. **Fix the PHP.B / PHP.eB citation** (deep dive #4, cross-disease Pattern 4): 2018 papers are PHP.B; add Chan et al. 2017 and Hordeaux et al. 2019 for the PHP.eB Ly6a link.
4. **Fix the Bye donor-n precision** (deep dives #1/#3, cross-disease Pattern 3): library 100 SALS donors; screen 16 SALS donors; state the combination-validation donor n. Never describe the Bye combination as demonstrating formal synergy — combination benefit only.
5. **Adopt the four strengthened falsification tests** in §2 above, or record the reason for declining each one. In particular, the rubric's Test 1 should not be presented as validation in any form until a blinded held-out test exists.
6. **AGI-183 (GAP-FLAG-4) and model reproducibility (GAP-FLAG-1) remain the programme's critical path.** The red-team finding adds that BCL-XL stabilisation has no known precedent pharmacology at all, which raises the bar on Gate 0b from "characterise the compound" to "establish that this pharmacology exists."

**Scope note:** searches were run on the public web and PubMed/PMC-indexed sources on 8 Nov 2026. A negative result ("no record found") is bounded by the queries listed in each section; it is not a proof of non-existence in paywalled or non-indexed sources. The (a) refutation, by contrast, rests on a positive find (granted patent family) and does not depend on search completeness.
