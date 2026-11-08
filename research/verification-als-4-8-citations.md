# Citation Verification — ALS Paper `als_4_8.pdf`

**Paper verified:** "Synergistic Neuroprotection in ALS: Akt/Bad Phosphorylation as a Predictive Biomarker for BCL-2 Family Therapy", authors x@agicorp.network and Bios (bios@bio.xyz). File: `~/workspace/user/files/als_4_8.pdf` (1,053,308 B, created 2026-04-08).

**Verification date:** 2026-11-07 (all sources accessed 2026-11-07 PST / 2026-11-08 ~00:48 UTC). Methods: Firecrawl scrape of PMC full texts, NCBI E-utilities summaries, PubMed/JCI/Reactome/Haematologica page reads, and targeted web searches.

**Scope note:** This paper is a research proposal plus computational-model predictions (Bliss excess, BH3 EC50 trajectories, 42-day MOMP probabilities are model outputs, not wet-lab results). Nothing here is a proven therapy, cure, treatment, or diagnosis. This verification covers only whether the cited external sources exist and say what the paper claims they say.

**Headline findings:**
- The AZD5991 numbers (54/65 = 83% troponin; 3/78 = 3.9% response) are arithmetically correct but framed misleadingly — see §4.
- The seven-inhibitor list is real; "none beyond Phase I/II" holds, but the cardiotoxicity claim has a documented exception (PRT1419) — see §5.
- The "no studies in neurodegeneration" claim was NOT falsified in its narrow form, but its cited anchor is invalid and a 2012 patent plus 2006/2007 peer-reviewed papers already proposed pAkt as an ALS biomarker — see §9.
- The reference list contains two duplicate citations: refs [10] = [11] and refs [6] = [7] are each the same paper cited twice — see §7, §10.

---

## 1. PubMed 39167622 — AZD5991 cardiotoxicity story

**VERDICT: Confirmed.**

**What the source actually says:** Desai P et al., "A Phase 1 First-in-Human Study of the MCL-1 Inhibitor AZD5991 in Patients with Relapsed/Refractory Hematologic Malignancies", *Clinical Cancer Research* 2024;30(21):4844–4855 (NCT03218683). The abstract states: "Asymptomatic elevations of troponin I or T were observed in eight (10.3%) patients. Post hoc retrospective analysis revealed elevated troponin T in 14/31 patients before any AZD5991 dose and in 54/65 patients after any AZD5991 dose at or after Cycle 1. No associations were found between elevated troponin and cardiovascular risk factors." Conclusion: "Treatment with AZD5991 was associated with high incidence of laboratory troponin elevation and a low overall response rate."

**Caveat (carries into §4):** the 54/65 figure comes from a *post hoc* retrospective high-sensitivity troponin T analysis of stored samples, not from adverse events reported during the trial (those were 8/78, 10.3%). And 14/31 patients already had elevated troponin *before* any dose.

**Source:** https://pubmed.ncbi.nlm.nih.gov/39167622/ — as of 2026-11-07.

---

## 2. PMC11528199 — disappointing AZD5991 efficacy

**VERDICT: Confirmed.**

**What the source actually says:** This is the full text of the same Desai et al. 2024 paper (§1). Efficacy section: "Three of the five patients with MDS achieved an objective response… None of the patients who showed ORR had prior venetoclax exposure… No objective responses were observed in patients with MM or other histologies." Table 3: ORR 0 in AML (n=38), 3 (60%) in MDS (n=5), 0 in others (n=35). Discussion: "Limited clinical activity was observed with AZD5991 monotherapy and in combination with venetoclax across different hematologic malignancies." The trial was terminated early and the MTD was not determined; a grade 3 troponin I increase led to an FDA clinical hold.

**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11528199/ — as of 2026-11-07. (Verified via Firecrawl full-text scrape.)

---

## 3. PMC7731749 — MCL1 expression in cardiac tissue / fundamental challenge

**VERDICT: Confirmed.**

**What the source actually says:** This is NOT the mouse knockout study — it is a review: "MCL-1 inhibitors, fast-lane development of a new class of anti-cancer agents", *Journal of Hematology & Oncology* 2020. It states: "A first alert concerning on-target/off-tumor toxicity came from the AMG-397 trial that was put on hold because of cardiac side effects. Because MCL-1 is implicated in normal cardiac myocyte functioning, these side effects are probably directly related to the on-target activity of these compounds and may limit the therapeutic window of MCL-1 inhibitors." It also notes conditional-knockout studies showing "an essential role for MCL-1 in hematopoietic stem cells, hepatocytes, neutrophils, cardiomyocytes and during neuronal development."

**Note:** The paper's claim is supported by this review. The underlying primary evidence for MCL1's cardiac role is Thomas et al., *Genes & Development* 2013 ("Loss of MCL-1 leads to impaired autophagy and rapid development of heart failure", PMID 23788623): cardiomyocyte-specific Mcl-1 ablation caused rapid cardiomyopathy and death, with MCL-1 "highly expressed in myocardium". The paper would be stronger citing that primary study directly, but ref [3] as cited does support the point.

**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC7731749/ — as of 2026-11-07. (Verified via Firecrawl full-text scrape; primary study: https://pubmed.ncbi.nlm.nih.gov/23788623/.)

---

## 4. THE AZD5991 NUMBERS — troponin 83% (54/65) and response 3.9% (3/78)

**VERDICT: Partially confirmed — numbers are arithmetically correct; the framing is misleading in three specific ways.**

**What the source actually says (Desai et al. 2024, PMC11528199 full text):**

- **54/65 (83.1%) troponin elevation — real, but:** it is from a *post hoc* retrospective analysis using a high-sensitivity troponin T assay on stored plasma samples, in the subset of patients with available samples — not "83% of treated patients". The trial's prospectively reported adverse-event rate was **8/78 (10.3%)** asymptomatic troponin I/T elevations. More importantly, **14/31 (45.2%) patients already had elevated troponin T before any AZD5991 dose**, so a large share of the 83% reflects pre-existing elevation in a heavily pretreated, relapsed/refractory population, not drug-attributable injury. The paper's phrasing ("troponin elevation in 83% of treated patients") omits all of this. The correct statement: "In a post hoc analysis of stored samples, high-sensitivity troponin T was elevated in 54/65 (83%) patients after any AZD5991 dose, versus 14/31 (45%) before any dose; prospectively reported troponin elevations were 8/78 (10.3%)."
- **3/78 (3.9%) objective response rate — arithmetically correct, but not a number the trial paper states.** The paper reports ORR by subgroup only: MDS 3/5 (60%), AML 0/38, others 0/35; total treated 78, so 3/78 = 3.85% ≈ 3.9% is a valid derived overall figure. But presenting "3.9%" without the subgroup breakdown understates the drug's activity: **all three responders were MDS patients, a 60% ORR in that subgroup** (1 marrow CR without hematologic improvement, 1 PR on monotherapy, 1 marrow CR on combination). The honest framing is "3/78 overall (3.9%), all in MDS (3/5, 60%); no responses in AML, myeloma, or other histologies."
- The trial was terminated early for the unfavorable risk/benefit ratio and the MTD was never determined — that part of the paper's framing is accurate.

**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11528199/ — as of 2026-11-07.

---

## 5. THE SEVEN INHIBITORS CLAIM — ABBV-467, AMG 176, AMG 397, AZD5991, GS-9716, MIK665, PRT1419; none beyond Phase I/II; cardiotoxicity predominant dose-limiting factor

**VERDICT: Partially confirmed — the list is real and "none beyond Phase I/II" holds, but the cardiotoxicity claim is not universal across the class.**

**What the sources actually say:** A 2025 review (*International Journal of Molecular Sciences*, "Targeting the BCL2 Family: Advances and Challenges in BH3 Mimetic-Based Therapies") tabulates all seven: MIK665 (S64315) — Phase I, majority of trials completed; PRT1419 — Phase I, some completed; AMG-176 (tapotoclax) — clinical trial terminated; AMG-397 — clinical trial terminated; GS-9716 — listed trial but not recruiting; AZD5991 — clinical trial terminated due to cardiac toxicity concerns; ABBV-467 — clinical trial terminated. The same review states cardiotoxicity was "the most frequently reported and concerning adverse effect" and that the FDA placed holds on AMG-397, AMG-176, and AZD5991 trials. A second 2026 review states the programs were mostly discontinued by 2020–2021 and that "no Mcl1 inhibitor has received FDA approval, largely due to concerns regarding dose-limiting cardiotoxicity."

**Exceptions that must be disclosed:**
- **PRT1419 remains in active development as of late 2025** and "demonstrated acceptable safety and tolerability in patients with advanced or metastatic solid tumors… notably without cardiac toxicity." So "cardiotoxicity the predominant dose-limiting factor" is true for most of the class but false as a universal claim — PRT1419 is the counterexample. (Some later PRT1419 combination studies were terminated, NCT05107856.)
- **GS-9716's status is unclear** ("listed trial but not recruiting") — its failure mode is not documented as cardiotoxicity in the sources found.
- "None advanced beyond Phase I/II" is accurate as of 2026-11-07: no MCL1 inhibitor has reached Phase III or approval. But the claim should be dated — PRT1419 is still active in Phase I, so "uniformly failed" overstates the current state.

**Sources:** https://www.mdpi.com/1422-0067/26/20/9859 (IJMS 2025 review); https://www.mdpi.com/2218-273X/16/5/694 (2026 review) — as of 2026-11-07.

---

## 6. PubMed 9346240 — Akt/Bad phosphorylation biology

**VERDICT: Confirmed.**

**What the source actually says:** Datta SR et al., "Akt phosphorylation of BAD couples survival signals to the cell-intrinsic death machinery", *Cell* 1997;91(2):231–241. Abstract: "Growth factor activation of the PI3′K/Akt signaling pathway culminates in the phosphorylation of the BCL-2 family member BAD, thereby suppressing apoptosis and promoting cell survival. Akt phosphorylates BAD in vitro and in vivo, and blocks the BAD-induced death of primary neurons in a site-specific manner." The paper shows Akt phosphorylates BAD at Ser-136 (mouse numbering). This is the foundational paper for the Akt→Bad mechanism and it even used primary neurons — directly relevant.

**Source:** https://pubmed.ncbi.nlm.nih.gov/9346240/ — as of 2026-11-07.

---

## 7. PubMed 31150457 — Akt phosphorylation as validated predictive biomarker in oncology

**VERDICT: Partially confirmed — the paper exists and supports a weaker claim; "validated" is an overstatement, and it is a duplicate of ref [11].**

**What the source actually says:** PMID 31150457 is Rice SJ et al., "EGFR mutations and AKT phosphorylation are markers for sensitivity to combined MCL-1 and BCL-2/xL inhibition in non-small cell lung cancer", *PLOS ONE* 2019;14(5):e0217657. Abstract: "a high level of phosphorylated AKT (S473) was identified as a marker for sensitivity to the combination treatment" — in a panel of lung cancer **cell lines** treated with maritoclax (MCL-1 inhibitor) ± a BCL-2/xL inhibitor.

**Problems:**
1. **"Validated as a predictive biomarker" is overstated.** This is a preclinical, in-vitro cell-line study. It identifies pAKT (S473) as a *marker for sensitivity* in cell lines and states the data "support the design of a clinical trial" — it does not clinically validate any biomarker in patients.
2. **It is about pAKT (S473), not Akt/Bad phosphorylation.** The study does not measure Bad phosphorylation as the predictive marker.
3. **Duplicate citation:** PMID 31150457 (ref [10]) and DOI 10.1371/journal.pone.0217657 (ref [11]) are the **same paper cited twice** under different identifiers. Ref [11]'s description ("Akt phosphorylation of Bad at serine 99/136") does not match this paper at all — that Ser99/136 biology is established by Datta 1997 [8] and Reactome R-HSA-198347 [14], not by Rice 2019.

**Source:** https://pubmed.ncbi.nlm.nih.gov/31150457/ — as of 2026-11-07.

---

## 8. JCI article 170169 — anchor for the "no peer-reviewed studies" claim (ref [9])

**VERDICT: Contradicted as support for the claim (the article exists; it does not support what it is cited for).**

**What the source actually says:** Chong SJF et al., "Hyperphosphorylation of BCL-2 family proteins underlies functional resistance to venetoclax in lymphoid malignancies", *Journal of Clinical Investigation* 2023;133(22):e170169. Using BH3 profiling and kinase-activity mapping, the authors found that hyperphosphorylation of BCL-2 family proteins — including MCL-1, BCL-2, **BAD**, and BAX — underlies intrinsic and acquired resistance to venetoclax in CLL and DLBCL, and that targeting phosphorylation with phosphatase-activating drugs restored venetoclax sensitivity.

**Why it fails as an anchor:** The paper's ref [9] is cited for the sentence "no peer-reviewed studies were identified that specifically propose or validate Akt/Bad phosphorylation as a [predictive biomarker in neurodegeneration]". The JCI paper (a) is an oncology study, (b) contains no systematic literature search, and (c) says nothing about neurodegeneration or about the absence of studies. A single oncology paper cannot evidence a negative search result. Ironically, it *strengthens* the oncology-side biology (BAD phosphorylation status genuinely modulates BCL-2 therapy response) while contributing nothing to the neurodegeneration novelty claim.

**Source:** https://www.jci.org/articles/view/170169 — as of 2026-11-07.

---

## 9. THE "NO STUDIES IN NEURODEGENERATION" CLAIM — systematic search found NO peer-reviewed studies proposing/validating Akt/Bad phosphorylation as a predictive biomarker for BCL-2 family therapies in ALS or any neurodegenerative disease

**VERDICT: Partially confirmed — the narrow claim was not falsified, but the novelty framing is overstated and the cited anchor is invalid (see §8).**

**Searches run (2026-11-07):**
1. "Akt Bad phosphorylation biomarker amyotrophic lateral sclerosis ALS patient stratification"
2. "BAD phosphorylation phospho-BAD biomarker Parkinson Alzheimer Huntington neurodegeneration"
3. "BH3 profiling mitochondrial priming neurodegeneration ALS Parkinson Alzheimer longitudinal study"
4. "Leger 2006 FASEB Journal Akt phosphorylation reduced ALS patients skeletal muscle"

**What I found — no direct counterexample:** No peer-reviewed study was found that proposes or validates Akt/Bad phosphorylation as a *predictive biomarker for BCL-2 family therapy* in ALS, Parkinson's, Alzheimer's, or Huntington's. The narrow claim, as worded, survived these searches. Adjacent work exists (e.g., 14-3-3 phosphorylation as a proposed Parkinson's biomarker — Slone et al., Michael J. Fox Foundation-funded; 14-3-3 is the scaffold that binds phospho-BAD — but that work does not concern BCL-2 family therapy stratification), and no longitudinal BH3 profiling study in a neurodegenerative model surfaced, consistent with the paper's related gap claim.

**Closest prior art — this materially narrows the novelty claim:**
1. **A granted patent proposed pAkt as an ALS biomarker in 2012.** "Use of Akt phosphorylation as a biomarker for prognosing neurodegenerative diseases and treating same" (WO2012160563; CA2836503; EP3263127B1, granted 2019): claims pAkt and pAkt:tAkt ratio as biomarkers for ALS progression prognosis and for assessing responsiveness to treatment. It is a patent, not a peer-reviewed study; it is about pAkt (not pBad) as a *prognostic* marker (not predictive for BCL-2 family therapy). It therefore does not strictly falsify the narrow claim — but it does mean "pAkt as a stratification biomarker in ALS" was proposed 14 years ago, and the paper's Discovery 5 language ("completely novel", "never been proposed") is overstated. Source: https://patents.google.com/patent/CA2836503A1/en
2. **Peer-reviewed evidence of pAkt dysregulation in ALS patients since 2006.** Léger B et al., "Human skeletal muscle atrophy in amyotrophic lateral sclerosis reveals a reduction in Akt and an increase in atrogin-1", *FASEB Journal* 2006;20(3):583–585 (doi:10.1096/fj.05-5249fje): ALS patients have significantly lower phosphorylated Akt protein than controls. Dewil M et al., *Neuropathology and Applied Neurobiology* 2007;33(5):499–509: Akt pathway dysfunction in motor neurons of sporadic and familial ALS patients. These establish pAkt as a disease-associated measure in ALS — again prognostic/disease biology, not predictive for BCL-2 therapy, but they undercut any suggestion that Akt phosphorylation in ALS is unexplored territory.
3. The paper's own systematic-search methodology is not described anywhere in the PDF (no search strings, databases, dates, or inclusion criteria), so the negative claim is not reproducible as stated. A negative claim of this kind needs a documented search strategy; ref [9] (JCI 170169) is not one.

**Bottom line:** the specific combination — Akt/Bad phosphorylation *as a predictive biomarker for BCL-2 family therapy* in neurodegeneration — appears genuinely unproposed. But the paper should claim exactly that narrow novelty, cite the 2012 patent and the Léger/Dewil papers as the boundary of prior art, and replace ref [9] with a real systematic-review methods note. As written, Discovery 5 overclaims.

---

## 10. Spot-checks of additional references (one line each)

- **PLOS ONE 10.1371/journal.pone.0217657 (Rice et al. 2019)** — Exists; supports pAKT (S473) as a sensitivity marker for combined MCL-1 + BCL-2/xL inhibition in NSCLC cell lines, but does **not** support ref [11]'s description ("Akt phosphorylation of Bad at Ser99/136") and is a duplicate of ref [10]. Partially confirmed. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0217657
- **PMC3770266** — Exists; "BH3 profiling — measuring integrated function of the mitochondrial apoptotic pathway to predict cell fate decisions" (*Cancer Letters* 2013). Supports the BH3 profiling description. Confirmed. https://pmc.ncbi.nlm.nih.gov/articles/PMC3770266/
- **PMC8316436** — Exists; "Dynamic BH3 profiling identifies active BH3 mimetic combinations in non-small cell lung cancer" (*Cell Death & Disease* 2021). Supports BH3 profiling utility. Confirmed. https://pmc.ncbi.nlm.nih.gov/articles/PMC8316436/
- **PMC9257998** — Exists; "Safety and efficacy of navitoclax, a BCL-2 and BCL-X(L) inhibitor, in patients with relapsed or refractory lymphoma" (*Leukemia & Lymphoma* 2021). Supports the thrombocytopenia (BCL-XL) half of the toxicity framing; the cardiotoxicity (MCL1) half rests on refs [1]–[3]. Confirmed with that split. https://pmc.ncbi.nlm.nih.gov/articles/PMC9257998/
- **PMC3221787** — Exists; "A unified model of mammalian BCL-2 protein family interactions at the mitochondria" (*Molecular Cell* 2011). Supports MCL1/BCL-XL orthogonal sequestration of BAK/BAX. Confirmed. https://pmc.ncbi.nlm.nih.gov/articles/PMC3221787/
- **PMC3070914** — Exists; "Bcl-x(L) retrotranslocates Bax from the mitochondria into the cytosol" (*Cell* 2011). Exactly supports the retrotranslocation claim. Confirmed. https://pmc.ncbi.nlm.nih.gov/articles/PMC3070914/
- **PMC2681190** — Exists; "Mcl-1 is a key regulator of apoptosis during CNS development and after DNA damage" (*Journal of Neuroscience* 2008). Supports MCL1's CNS role, but the paper's inference ("overexpression low-risk in post-mitotic neurons") is **not** what this paper shows — it shows Mcl-1 loss causes massive neuronal apoptosis during development, i.e. MCL1 is essential, which argues for caution rather than low risk. Partially confirmed. https://pmc.ncbi.nlm.nih.gov/articles/PMC2681190/
- **PMC11584402** — Exists; "Profiling protein-protein interactions to predict the efficacy of B-cell-lymphoma-2-homology-3 mimetics for acute myeloid leukemia" (*Nature Biomedical Engineering* 2024). Supports the Mode 1 sequestration / BH3-mimetic efficacy context. Confirmed. https://pmc.ncbi.nlm.nih.gov/articles/PMC11584402/
- **PMC4714955** — Exists; "BH3 profiling identifies heterogeneous dependency on Bcl-2 family members in multiple myeloma and predicts sensitivity to BH3 mimetics" (*Leukemia* 2016). An oncology paper: supports BH3 profiling's established oncology use but says nothing about neurodegeneration, so it cannot evidence the neurodegeneration gap. Partially confirmed. https://pmc.ncbi.nlm.nih.gov/articles/PMC4714955/
- **Reactome R-HSA-198347** — Exists; "AKT phosphorylates BAD": "Activated AKT phosphorylates the BCL-2 family member BAD at serine 99 (corresponds to serine residue S136 of mouse Bad), blocking the BAD-induced cell death" (citing Datta 1997, del Peso 1997). Confirms the Ser99/136 numbering and mechanism. Confirmed. https://reactome.org/content/detail/R-HSA-198347
- **Haematologica 2023.283060** — Exists; Pan RA et al., "BH3 profiling as pharmacodynamic biomarker for the activity of BH3 mimetics", *Haematologica* 2024;109:1253, doi:10.3324/haematol.2023.283060. Supports BH3 profiling as a PD biomarker in oncology. Confirmed. https://haematologica.org/article/view/11319
- **Haematologica article view/11319 (ref [7])** — Resolves to the **same** Pan et al. paper as ref [6] — a second duplicate citation. Neither [6] nor [7] addresses neurodegeneration, so ref [7] cannot support the "absence of longitudinal BH3 profiling studies in ALS, Parkinson's" claim. Contradicted as support for that claim. https://haematologica.org/article/view/11319

---

## 11. The BCL-2 bridge — MCL1/BCL-XL as real cancer drug targets with clinical-stage programs

**VERDICT: Confirmed.**

The ALS↔oncology bridge rests on solid ground as a *mechanistic* bridge. Venetoclax (ABT-199), a selective BCL-2 inhibitor, received FDA accelerated approval on **April 11, 2016** as the first-in-class BCL-2 inhibitor for relapsed/refractory CLL with 17p deletion, based on an ~80% overall response rate in the pivotal Phase 2 trial, and is now standard of care in CLL and AML (including FDA-approved venetoclax + azacitidine in AML). Navitoclax (BCL-2/BCL-XL) reached clinical trials and its dose-limiting thrombocytopenia is the canonical BCL-XL on-target toxicity (PMC9257998). Seven MCL1 inhibitors reached clinical development (see §5), and the BH3-profiling assay the paper wants to port into neurodegeneration is an established oncology tool (PMC3770266, PMC8316436, Haematologica 2023.283060). The biology is shared: the same BCL-2 family proteins, the same BH3 interactions, the same Akt→Bad regulatory axis (Datta 1997; Reactome R-HSA-198347; JCI 170169 showing BAD phosphorylation modulates venetoclax response in patients). What is *not* established is the reverse direction: no BCL-2 family therapy has been validated in any neurodegenerative disease, and no MCL1 inhibitor has ever been approved for any indication. The bridge is real as a rationale for a research program; it is not evidence of therapeutic efficacy in ALS.

**Sources:** https://news.abbvie.com/2016-04-11-AbbVie-Receives-FDA-Accelerated-Approval-of-Venclexta-venetoclax-Tablets-the-First-BCL-2-Inhibitor-in-Relapsed-Refractory-Chronic-Lymphocytic-Leukemia-Patients-with-17p-Deletion ; https://pmc.ncbi.nlm.nih.gov/articles/PMC9257998/ ; https://www.mdpi.com/1422-0067/26/20/9859 — as of 2026-11-07.

---

## Summary table

| # | Item | Verdict |
|---|------|---------|
| 1 | PubMed 39167622 (AZD5991 cardiotoxicity) | Confirmed |
| 2 | PMC11528199 (disappointing efficacy) | Confirmed |
| 3 | PMC7731749 (cardiac MCL1 challenge) | Confirmed |
| 4 | AZD5991 numbers 83% (54/65), 3.9% (3/78) | Partially confirmed — arithmetic right, framing misleading (post hoc subset; 45% elevated pre-dose; 3.9% is derived, all responders MDS at 60%) |
| 5 | Seven inhibitors, none beyond Ph I/II, cardiotoxicity predominant | Partially confirmed — list real, none beyond Ph I/II; PRT1419 is a no-cardiotoxicity exception still in active development |
| 6 | PubMed 9346240 (Akt/Bad biology) | Confirmed |
| 7 | PubMed 31150457 (Akt as validated biomarker) | Partially confirmed — real paper, preclinical cell-line marker only, not clinically validated; duplicate of ref [11] |
| 8 | JCI 170169 (anchor for "no studies") | Contradicted as support — real oncology paper, contains no search and nothing about neurodegeneration |
| 9 | "No studies in neurodegeneration" | Partially confirmed — narrow claim not falsified, but 2012 patent + 2006/2007 papers already proposed pAkt as an ALS biomarker; search methods undocumented |
| 10 | Spot-checks (12 refs) | 8 confirmed, 3 partially confirmed, 1 contradicted as support; duplicates found: [10]=[11], [6]=[7] |
| 11 | BCL-2 bridge (MCL1/BCL-XL real cancer targets) | Confirmed |

## Required corrections before this paper is cited externally

1. **AZD5991 troponin:** state the post hoc nature, the 45.2% pre-dose elevation, and the 10.3% prospective AE rate alongside the 83%.
2. **AZD5991 response:** state 3/78 overall with the MDS 3/5 (60%) subgroup result; do not present 3.9% as a trial-reported figure.
3. **Seven inhibitors:** qualify "cardiotoxicity predominant" with the PRT1419 exception and date the "none beyond Phase I/II" claim.
4. **Refs [10]/[11] and [6]/[7]:** deduplicate; fix ref [11]'s description (Ser99/136 belongs to Datta/Reactome, not Rice).
5. **"Validated biomarker" (oncology):** downgrade to "preclinical cell-line marker of sensitivity; not clinically validated."
6. **Ref [9] / Discovery 5:** replace the JCI anchor with a documented systematic-search methods note, narrow the novelty claim to the exact combination (Akt/Bad phosphorylation *as a predictive biomarker for BCL-2 family therapy* in neurodegeneration), and disclose the 2012 pAkt-ALS patent (WO2012160563 / EP3263127B1) and Léger 2006 / Dewil 2007 as prior art at the boundary.
7. **PMC2681190:** do not cite it for "MCL1 overexpression is low-risk in post-mitotic neurons" — it shows MCL1 is essential during CNS development.

*Verification performed 2026-11-07. No live site, repo, or mailbox was touched. No content was published, sent, or deployed.*
