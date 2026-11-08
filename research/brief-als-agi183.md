# Enhancement Brief — ALS: AGI-183 + AAV6-hSyn-MCL1 (from als_4_8.pdf)

**Published:** research brief in this repo's `research/` folder.
**Research date: 7 November 2026. Evidence: `~/workspace/user/files/als_4_8.pdf` — "Synergistic Neuroprotection in ALS: Akt/Bad Phosphorylation as a Predictive Biomarker for BCL-2 Family Therapy", authors x@agicorp.network and Bios (bios@bio.xyz). PDF 1,053,308 B, created 2026-04-08, LaTeX via pandoc.**
**Applies to:** the staged ALS articles, the ALS agent site, the ALS interactive components, and the staged ALS homepage. Complements (does NOT replace) `brief-als.md`, which covers the compound-library jobs table, the "not a medical device" line, Answer ALS / Neuromine, ALS TDI, Project MinE / NEALS, ChEMBL / PubChem / DrugBank, repo links, the series-number correction, and `als-02` honesty. A later worker should be able to apply this brief without re-reading the paper: every item below gives the exact paper-grounded fact and its location in the paper.**

## Honesty lines (read first — they govern every item)

- **PREDICTED, NOT DEMONSTRATED — absolute rule.** The paper is a research proposal plus computational-model predictions. **All five discoveries are computational-model predictions** ("predicted", "aims to validate"). Label every model result as a prediction in every sentence that states it. **Never write "the study found / showed / demonstrated" for model outputs.** There are no wet-lab results in this paper. AGI-183 + AAV6-hSyn-MCL1 is **not a proven therapy**.
- **No treatment, cure, diagnosis, or medical-device claims anywhere.** The ALS Researcher is "not a medical device." Nothing here claims AGI-183 treats, cures, or diagnoses ALS or any disease.
- **Citation status: VERIFIED WITH CORRECTIONS, 2026-11-07.** The paper's external citations were independently verified (`verification-als-4-8-citations.md`, 2026-11-07). Seven corrections were applied to this brief (see §3 and §7): (1) AZD5991 troponin reframed as a post hoc analysis with pre-dose baseline; (2) the 3.9% response rate given with its MDS subgroup breakdown; (3) the seven-inhibitor "uniform failure" claim qualified with the PRT1419 exception; (4) duplicate refs [10]=[11] and [6]=[7] noted; (5) "validated biomarker in oncology" downgraded to preclinical cell-line evidence; (6) the JCI 170169 anchor dropped and 2012 patent + 2006/2007 prior art disclosed; (7) the PMC2681190 "low-risk MCL1 overexpression" inference corrected — it argues for caution. Claims below carry **[verified 2026-11-07]** (confirmed as cited) or **[corrected per verification 2026-11-07]** (framing fixed per the verification file). No external citation in this brief is presented as verified beyond what the verification file establishes.
- **The paper never mentions a DAO.** A full-text search of als_4_8.pdf finds no "DAO" mention. The paper is a hypothesis + computational-predictions source for the ALS work, not a DAO document. It does not launch, propose, or describe any DAO. The ALS DAO / Cancer DAO framing is ours, not the paper's.
- **ALS has no W3 series number.** Never give it one. Do NOT adopt vr-spaces-loop `series.json` S34 ALS / S35 Parkinsons.
- **W3 series are proposed, not formed.** Filed fact (Foundation B20260196664, Fellowship B20260229217) stays apart from proposed plans. "33 named W3 sub-series in the April 2026 internal list" — never 35.
- **The ALS agent is offline** — listed in Virtuals ACP, no instance deployed, 0 jobs completed, $0 earned (as of 2026-11-06). Do not claim it can take hires.
- **AGI-183 identity tension (unresolved):** the paper calls AGI-183 a BCL-XL stabilizer. A separate file, `~/workspace/user/files/AGI_Compound_001.pdf`, has an entry also named "Compound AGI-183" that describes a CRBN-binding FLIP inhibitor (pro-apoptotic, cancer) — the opposite mechanism. See §5. **Do NOT merge the two descriptions.** The paper's AGI-183 is the only one this brief describes.

---

## 1. What the paper is

- **Title:** "Synergistic Neuroprotection in ALS: Akt/Bad Phosphorylation as a Predictive Biomarker for BCL-2 Family Therapy".
- **Authors:** x@agicorp.network and Bios (bios@bio.xyz).
- **Type:** a research proposal + computational predictions. The abstract states the study "aims to validate" the combination and "aims to" test the biomarker hypothesis. The five discoveries are all labelled in the paper as computational-model predictions (see §3).
- **Combination:** **AGI-183**, described in the paper as "a BCL-XL stabilizer" and "an AGI compound", plus **AAV6-hSyn-MCL1**, a vector for neuron-specific MCL1 overexpression.
- **Model system (proposed, not yet run):** iPSC-derived **TDP-43 Q331K** motor neurons under **chronic glutamate stress**.
- **Design (proposed):** a **2x2 factorial** study — control, AGI-183 alone, AAV6-hSyn-MCL1 alone, combination.
- **Central hypothesis:** **Akt/Bad phosphorylation status can stratify therapeutic response** to BCL-2 family-targeted therapy in ALS. The paper predicts Akt-low / pBad-low neuronal subpopulations will show greater marginal benefit from the combination, because low Akt phosphorylation of Bad leaves BCL-XL functionally antagonized (see §2).

---

## 2. Mechanism, as the paper states it

- The BCL-2 family regulates apoptosis by controlling **mitochondrial outer membrane permeabilization (MOMP)**, the key event in the intrinsic apoptotic pathway. Anti-apoptotic members BCL-XL and MCL1 sequester pro-apoptotic proteins, preventing MOMP and cell death.
- **Orthogonal protection (the core rationale for combining them):** MCL1 and BCL-XL provide orthogonal anti-apoptotic protection by preferentially sequestering **BAK** and **BAX**, respectively [verified 2026-11-07 — PMC3221787, "A unified model of mammalian BCL-2 protein family interactions at the mitochondria", Mol Cell 2011].
- **BCL-XL retrotranslocation:** BCL-XL actively retrotranslocates the pro-apoptotic protein BAX from mitochondria — a survival function the paper proposes a stabilizing agent like AGI-183 can enhance [verified 2026-11-07 — PMC3070914, "Bcl-x(L) retrotranslocates Bax from the mitochondria into the cytosol", Cell 2011].
- **Akt/Bad link:** the PI3K/Akt pathway phosphorylates Bad, inhibiting its pro-apoptotic activity by promoting sequestration via 14-3-3 proteins. Low Akt phosphorylation of Bad leaves BCL-XL functionally antagonized, so the paper predicts neurons in that state would derive greater marginal benefit from a BCL-XL stabilizing therapy [verified 2026-11-07 — Datta et al. Cell 1997, PMID 9346240; Reactome R-HSA-198347 confirms Akt phosphorylates BAD at Ser99 (mouse Ser136)].
- **Safety rationale (paper's design argument, not a demonstrated result):** neuron-targeted MCL1 gain-of-function plus BCL-XL stabilization is designed to circumvent the known on-target toxicities of systemic inhibitors — **cardiotoxicity (MCL1)** and **thrombocytopenia (BCL-XL)** [verified 2026-11-07 with a split: PMC9257998 (navitoclax, Leuk Lymphoma 2021) supports the thrombocytopenia half; the cardiotoxicity half rests on refs [1]–[3], incl. review PMC7731749, confirmed]. **CORRECTED INFERENCE:** the paper further states that MCL1 overexpression, while oncogenic in dividing cells, is considered low-risk in post-mitotic neurons, citing PMC2681190 — **that citation does not support the inference.** PMC2681190 (J Neurosci 2008, "Mcl-1 is a key regulator of apoptosis during CNS development and after DNA damage") shows Mcl-1 loss causes massive neuronal apoptosis during CNS development, i.e. MCL1 is essential in developing neurons — which argues for **caution**, not low risk. [corrected per verification 2026-11-07] **Do not cite PMC2681190 for "MCL1 overexpression is low-risk in post-mitotic neurons".** All of this is design rationale, not safety data — no toxicity experiment is reported in the paper.
- **What the paper does NOT give for AGI-183:** no SMILES, no molecular weight, no structure, no dose, no source or synthesis, no binding data. Do not invent any of these. (The separate `AGI_Compound_001.pdf` entry named AGI-183 gives a SMILES and properties — but for a CRBN-binding FLIP inhibitor, a different mechanism; see §5. Do not import those values here.)

---

## 3. The five discoveries — ALL computational-model predictions

Every bullet below is a **prediction from a computational model**, not a wet-lab result. The paper's own model-run identifiers are given so a later worker can trace them.

### Discovery 1 — Near-additive acute MOMP inhibition (mechanistic floor effect) — PREDICTED
- The paper predicts the combination gives **near-additive, rather than synergistic or antagonistic, acute inhibition of MOMP** due to a mechanistic floor effect: both interventions are individually sufficient to prevent MOMP over 42 days, so the combination cannot show further benefit on that binary endpoint.
- Predicted numbers: initial static modeling suggested antagonism, **Bliss excess −0.0422** (95.1% of simulated conditions antagonistic; example at 2x BCL-XL + 2x MCL1; Job ID 66508061-1f24-483d-98bf-1cc51221b94e). The extended stochastic model incorporating retrotranslocation and BH3-only compensation predicts a **near-additive Bliss excess of +0.0052 at day 2** (Job ID 8f7cbc88-c397-4b73-a53f-4e2cdc4bdb3a), with **+0.00815 at Day 1** confirming the absence of acute antagonism (Job ID 42347ca2-f06e-4c0c-8c95-57422b7b1721).
- **Wording to use:** "The model predicts near-additive acute MOMP inhibition (Bliss +0.0052 at day 2) — not synergy, not antagonism — because each intervention alone is predicted to be sufficient to prevent MOMP, a floor effect."

### Discovery 2 — Strengthening long-term synergy by suppressing delayed apoptosis — PREDICTED
- The paper predicts the combination effect transitions from near-additive acutely to robust, strengthening synergy over time, as delayed-onset MOMP becomes the dominant failure mode.
- Predicted numbers: **42-day MOMP probability 0.764 in the control arm → 0.040 in the combination arm** (a 94.8% reduction in cumulative MOMP incidence, as the paper calculates it). Time-resolved Bliss excess predicted at **+0.008 at day 1, peaking at +0.0305 at day 13.25, and +0.029 at day 42** (re-analysis: +0.00815 day 1, +0.03048 day 13.25, +0.02898 day 42). The abstract states sustained positive Bliss interaction with **ΔBliss > 0.025**.
- **Wording to use:** "The model predicts 42-day MOMP probability falls from 0.764 (control) to 0.040 (combination), with Bliss excess predicted to peak at +0.0305 around day 13.25 — a strengthening synergy over time that the proposed wet-lab study aims to validate."

### Discovery 3 — Attenuated mitochondrial priming (novel endpoint in neurodegeneration) — PREDICTED
- The paper predicts the combination maintains a higher apoptotic threshold (less-primed mitochondria) under chronic stress, a mechanism it presents as not previously explored in neurodegeneration.
- Predicted numbers: over 42 days, control neurons' **BH3 profiling EC50 falls from 65.29 to 15.84** (increasing priming), while the combination arm is predicted to maintain a stable **EC50 around 112.42**.
- The paper states there is an absence of longitudinal BH3 profiling / dynamic mitochondrial priming measurements in neurodegenerative disease models, despite established utility in oncology. The oncology utility is confirmed [verified 2026-11-07 — PMC3770266 (Cancer Lett 2013); PMC8316436 (Cell Death Dis 2021); Pan et al. Haematologica 2024, doi:10.3324/haematol.2023.283060]. The gap claim itself was not contradicted — no longitudinal BH3 profiling study in a neurodegenerative model surfaced in the verification searches — BUT the paper's refs [6] and [7] are the **same Pan et al. paper cited twice**, and neither addresses neurodegeneration, so ref [7] cannot evidence the gap; the paper's search methods are undocumented (no search strings, databases, dates, or inclusion criteria). [corrected per verification 2026-11-07]
- **Wording to use:** "The model predicts the combination holds BH3 EC50 near 112.42 over 42 days, while control EC50 is predicted to fall from 65.29 to 15.84 — attenuated mitochondrial priming, a new testable endpoint the paper proposes for neurodegeneration."

### Discovery 4 — Systemic MCL1 inhibitors fail clinically (on-target cardiotoxicity, low efficacy) — PAPER'S SYNTHESIS OF CLINICAL HISTORY
- This is the paper's systematic review of clinical-stage MCL1 inhibitors, not a model output. It is the rationale for the neuron-targeted approach.
- Paper's figures, **CORRECTED per verification 2026-11-07** (Desai et al., "A Phase 1 First-in-Human Study of the MCL-1 Inhibitor AZD5991", *Clinical Cancer Research* 2024;30(21):4844–4855, NCT03218683; PMID 39167622 / PMC11528199): **seven clinical-stage MCL1 inhibitors — ABBV-467, AMG 176, AMG 397, AZD5991, GS-9716, MIK665, PRT1419 — and "none advanced beyond Phase I/II" is accurate as of 2026-11-07** (no MCL1 inhibitor has reached Phase III or approval) [verified 2026-11-07]. BUT the paper's "cardiotoxicity the predominant dose-limiting factor" is **not universal across the class**: **PRT1419 remains in active development as of late 2025** and "demonstrated acceptable safety and tolerability in patients with advanced or metastatic solid tumors… notably without cardiac toxicity", and **GS-9716's failure mode is undocumented** ("listed trial but not recruiting"). "Uniformly failed" overstates the current state — PRT1419 is the counterexample. [corrected per verification 2026-11-07]
- Paper's AZD5991 troponin figure, **CORRECTED framing**: the 54/65 figure is real but comes from a **post hoc retrospective analysis** using a high-sensitivity troponin T assay on stored plasma samples, in the subset with available samples — **not "83% of treated patients"**. Correct statement: "In a post hoc analysis of stored samples, high-sensitivity troponin T was elevated in **54/65 (83%)** patients after any AZD5991 dose, versus **14/31 (45%)** before any dose; prospectively reported troponin elevations were **8/78 (10.3%)**." The 45% pre-dose elevation means a large share reflects pre-existing elevation in a heavily pretreated relapsed/refractory population, not drug-attributable injury. **Never write "troponin elevation in 83% of treated patients".** [corrected per verification 2026-11-07]
- Paper's AZD5991 response figure, **CORRECTED framing**: **3/78 overall (3.9%) is arithmetically correct but is a derived figure, not a number the trial paper states** — the trial paper reports ORR by subgroup only. Correct statement: "3/78 overall (3.9%), **all in MDS (3/5, 60%)**; no responses in AML (0/38), myeloma, or other histologies (0/35)." Presenting 3.9% without the subgroup breakdown understates the drug's activity in MDS. The trial was terminated early for the unfavorable risk/benefit ratio and the MTD was never determined — that part of the paper's framing is accurate. [corrected per verification 2026-11-07]
- The paper attributes the toxicity to MCL1's essential role in cardiomyocyte survival [verified 2026-11-07 — review PMC7731749, J Hematol Oncol 2020, confirmed; primary evidence Thomas et al. Genes Dev 2013, PMID 23788623: cardiomyocyte-specific Mcl-1 ablation caused rapid cardiomyopathy and death].
- **Wording to use:** "The paper's review states that all seven clinical-stage MCL1 inhibitors failed to advance beyond Phase I/II as of 7 Nov 2026, but the failure was not uniform: PRT1419 remains in active development and reported acceptable safety without cardiac toxicity in solid tumors. For AZD5991, high-sensitivity troponin T was elevated in 54/65 (83%) patients after any dose in a post hoc analysis of stored samples, versus 14/31 (45%) before any dose; prospectively reported troponin elevations were 8/78 (10.3%). Overall response was 3/78 (3.9%), all in MDS (3/5, 60%). [corrected per verification 2026-11-07 — see verification-als-4-8-citations.md]"

### Discovery 5 — Akt/Bad phosphorylation as a novel, untested predictive biomarker in neurodegeneration — PAPER'S LITERATURE-REVIEW FINDING
- The paper's systematic literature review (Job ID 74038966-e7bc-47d0-a9fe-8773bd86d1de) states it found **no peer-reviewed studies proposing or validating Akt/Bad phosphorylation as a predictive biomarker for BCL-2 family-targeted therapies in ALS or any other neurodegenerative disease**. The narrow claim was **not falsified** by independent verification searches (2026-11-07) [verified 2026-11-07 — narrow claim survived]. BUT the novelty framing is overstated, and the paper's anchor is invalid:
  - **Invalid anchor — do not cite it:** the paper's ref [9] (JCI 170169, Chong et al. J Clin Invest 2023) is an oncology paper about BAD hyperphosphorylation and venetoclax resistance. It contains **no systematic literature search and says nothing about neurodegeneration**. A single oncology paper cannot evidence a negative search result. Do NOT cite JCI 170169 as the anchor for the "no studies" claim. [corrected per verification 2026-11-07]
  - **Prior art at the boundary — disclose it:** a granted patent, "Use of Akt phosphorylation as a biomarker for prognosing neurodegenerative diseases and treating same" (**WO2012160563 / CA2836503 / EP3263127B1**, filed 2012, granted 2019), claims pAkt and pAkt:tAkt ratio as biomarkers for ALS progression prognosis and for assessing responsiveness to treatment. And peer-reviewed papers showed pAkt dysregulation in ALS patients years ago: **Léger et al., FASEB J 2006** (significantly lower phosphorylated Akt in ALS patients vs controls) and **Dewil et al., Neuropathol Appl Neurobiol 2007** (Akt pathway dysfunction in motor neurons of sporadic and familial ALS patients). These are prognostic / disease-biology, not predictive for BCL-2 family therapy — so they do not strictly falsify the narrow claim — but they mean "pAkt as a stratification biomarker in ALS" was proposed 14 years ago, and the paper's "completely novel" / "never been proposed" language is overstated. [verified 2026-11-07]
  - The paper's own systematic-search methodology is not described anywhere in the PDF (no search strings, databases, dates, or inclusion criteria), so the negative claim is not reproducible as stated.
- The paper states Akt/Bad phosphorylation status **is** a validated predictive biomarker in oncology. **DOWNGRADED per verification:** the cited source (Rice et al., PLOS ONE 2019, PMID 31150457) is **preclinical NSCLC cell-line work** identifying phosphorylated AKT (S473) as a marker for sensitivity to combined MCL-1 + BCL-2/xL inhibition; it states the data "support the design of a clinical trial" — it does **not** clinically validate any biomarker in patients, and it measures pAKT, not Bad phosphorylation. Correct framing: **"preclinical evidence supporting trial design"**, not "validated as a predictive biomarker". [corrected per verification 2026-11-07]
- **Duplicate citation:** the paper's refs [10] and [11] are the **same Rice 2019 paper** cited twice (PMID 31150457 = DOI 10.1371/journal.pone.0217657). Ref [11]'s description ("Akt phosphorylation of Bad at Ser99/136") does not match Rice 2019 at all — that Ser99/136 biology is established by Datta 1997 and Reactome R-HSA-198347. Deduplicate. [verified 2026-11-07]
- **Wording to use:** "The paper proposes — it does not demonstrate — Akt/Bad status as a stratification biomarker for ALS. The exact combination (Akt/Bad phosphorylation as a predictive biomarker for BCL-2 family therapy in neurodegeneration) appears unproposed in peer-reviewed literature, but pAkt as an ALS biomarker was proposed in a 2012 patent (WO2012160563 / EP3263127B1) and pAkt dysregulation in ALS patients was shown in 2006–2007 papers, so 'completely novel / never proposed' overstates the case. In oncology, the evidence is preclinical cell-line work (Rice 2019, pAKT S473), not clinical validation. [corrected per verification 2026-11-07]"

---

## 4. Exactly what to add or correct, item by item

These are **new content items** for the ALS pages. They complement `brief-als.md` Items 1–9; do not duplicate them. **Do NOT edit any file yourself** — staged articles go to the publish coordinator; agent-site and homepage edits go through the normal approval route. Hand each item to the right worker with its wording below.

### Item 1 — NEW SECTION in `als-03-als-research-field.md`: "A proposed combination: AGI-183 + AAV6-hSyn-MCL1"
- **Where:** `~/workspace/your_files/agifuturefoundation-articles/als/als-03-als-research-field.md` (staged article — hand to the publish coordinator) and its site page `~/workspace/your_files/hostinger-email/sites/agents/als/articles/als-research-field.html`.
- **What to add:** a short section, using the wording in §3, that (a) names the combination and the paper, (b) states the 2x2 factorial design in iPSC-derived TDP-43 Q331K motor neurons under chronic glutamate stress, (c) states the Akt/Bad stratification hypothesis, and (d) gives the five predicted numbers with "predicted" in every sentence. Lead with: "This is a research proposal with computational predictions, not a proven therapy and not wet-lab results."
- **Do NOT** present the combination as a treatment, a trial, or an available therapy. It is not in a trial; no trial is named in the paper.

### Item 2 — NEW SECTION in `als-02-from-compound-to-treatment.md`: "Why the model predicts synergy only over time"
- **Where:** `~/workspace/your_files/agifuturefoundation-articles/als/als-02-from-compound-to-treatment.md` (staged article — hand to the publish coordinator) and its site page `~/workspace/your_files/hostinger-email/sites/agents/als/articles/from-compound-to-treatment.html`.
- **What to add:** the Discovery 1 → Discovery 2 arc as a worked example of the compound-to-treatment road: the model predicts near-additivity acutely (Bliss +0.0052 day 2, floor effect) and strengthening synergy over time (Bliss peak +0.0305 day 13.25; 42-day MOMP 0.764 → 0.040 predicted). Frame it as "why a 42-day experiment, not a 2-day one, is the proposed test" — the paper's own point about time-resolved analysis.
- **Wording to use:** "The paper predicts the benefit, if real, would appear over weeks, not days — which is why the proposed validation is a 42-day longitudinal study, not a single-timepoint screen."

### Item 3 — NEW SECTION in `als-01-what-a-compound-library-is.md`: "A candidate entry: AGI-183"
- **Where:** `~/workspace/your_files/agifuturefoundation-articles/als/als-01-what-a-compound-library-is.md` (staged article — hand to the publish coordinator) and its site page `~/workspace/your_files/hostinger-email/sites/agents/als/articles/what-a-compound-library-is.html`.
- **What to add:** one short paragraph introducing AGI-183 as the first named candidate compound entry for the library (full entry: `compound-agi183.md` in this directory). State only what the paper states: a BCL-XL stabilizer, an AGI compound, proposed in combination with AAV6-hSyn-MCL1. Attach the "not a medical device" line. Do NOT give a structure, SMILES, dose, or price for AGI-183 — none is in the paper.
- **Link target (once approved):** the compound entry `compound-agi183.md` / its future library page. Do not link the `AGI_Compound_001.pdf` catalog entry — it describes a different mechanism under the same name (see §5).

### Item 4 — ADD to `agents/als/about.html`: the validation experiments the paper proposes
- **Where:** `~/workspace/your_files/hostinger-email/sites/agents/als/about.html` (agent site — approval route, do not edit directly).
- **What to add:** a "Proposed validation" block listing the paper's own proposed experiments:
  1. **2x2 factorial wet-lab validation** in iPSC-derived TDP-43 Q331K motor neurons under chronic glutamate stress (control / AGI-183 / AAV6-hSyn-MCL1 / combination).
  2. **Longitudinal BH3 profiling** over 42 days, testing the predicted EC50 trajectories (control 65.29 → 15.84; combination held ~112.42).
  3. **Time-resolved survival analysis** over 42 days, testing the predicted MOMP trajectory (0.764 → 0.040) and the predicted Bliss time-course (peak +0.0305 at day 13.25).
  4. **Stratification test:** whether baseline Akt-low / pBad-low neuronal subpopulations show greater marginal benefit, testing the Akt/Bad biomarker hypothesis.
  5. **"Antagonism-as-resilience" test:** whether acute near-additivity (Bliss +0.0052 day 2) genuinely transitions to long-term synergy, as the model predicts.
- **Wording to use:** "These experiments are proposed in the paper. None has been run or reported. The predictions above are what the experiments aim to test."

### Item 5 — ADD to the ALS interactive explorers: a "predictions, not results" disclaimer block
- **Where:** `~/workspace/your_files/interactive-builds/als/` (`job-explorer.html`, `hire-walkthrough.html`, `subscription-explorer.html`, `data.js`) — staged only, nothing live.
- **What to add:** wherever a compound entry is displayed, a one-line disclaimer: "Model predictions from als_4_8.pdf (7 Nov 2026) — not wet-lab results. The ALS Researcher is not a medical device."
- **Do NOT** add AGI-183 to `data.js` as a priced job or a library holding. The library has no data file (see `brief-als.md` §1); AGI-183 is a candidate entry in a brief, not a stocked compound.

### Item 6 — CORRECT: do not let the ALS pages imply the paper is a completed study
- **Where:** any ALS page, article, or catalog that mentions the paper, the combination, or AGI-183.
- **What to do:** use "the paper proposes / predicts / aims to validate" in every sentence. Never "the study found / showed / demonstrated / proved" for model outputs. The abstract's own verbs are "aims to validate" and "aims to" test — mirror them.
- **Check:** the staged ALS homepage (`~/workspace/your_files/homepage-redesign/als/index.html`) and the Foundation series page `series/S11-molecular.html` — if either ever names AGI-183 or the combination, it must carry the same predicted-not-demonstrated language and the "not a medical device" line.

---

## 5. Open tensions and questions needing Mike's decision

1. **AGI-183 identity tension (unresolved, do not paper over it):** `als_4_8.pdf` describes AGI-183 as a **BCL-XL stabilizer** (anti-apoptotic, neuroprotective in combination). `~/workspace/user/files/AGI_Compound_001.pdf` (450-page catalog, 2,786,539 B) has an entry also named "Compound AGI-183" describing a **CRBN-binding FLIP inhibitor** (pro-apoptotic, cancer) with SMILES `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(Br)C=C4`, MW 353.32 g/mol, LogP 4.1, predicted IC50 0.5 µM, and claimed in-vitro / xenograft results. Same identifier, opposite mechanisms. **Until Mike resolves which AGI-183 is which (same compound with two proposed mechanisms? two compounds sharing a name? a catalog error?), do NOT merge the entries, do NOT quote the catalog's SMILES/MW/IC50 as properties of the paper's AGI-183, and do NOT present the catalog's in-vitro/xenograft claims as validation of the paper's predictions.** The compound entry `compound-agi183.md` records both descriptions side by side with this tension flagged.
2. **Citation verification COMPLETE (2026-11-07):** the verification file (`verification-als-4-8-citations.md`) confirmed most cited sources and required 7 corrections, all applied in this brief (see honesty lines). No ALS page should revert any corrected framing to the paper's original wording — the paper's phrasing on AZD5991 troponin/response, the seven-inhibitor failure claim, the "validated biomarker" claim, the JCI 170169 anchor, and the PMC2681190 inference is superseded by the corrected framing in §3.
3. **Is the paper itself publishable as an article?** The paper is an internal research proposal + computational predictions by x@agicorp.network and Bios. Whether it becomes a staged article, a library entry only, or stays an internal brief is Mike's decision. This brief assumes library-entry + short sections only.
4. **Who owns the wet-lab validation?** The paper proposes experiments (2x2 factorial, BH3 profiling, survival analysis) with no lab, partner, timeline, or funding named. No ALS page may imply a lab or partner exists.
5. **AGI-183 sourcing:** the paper gives no source, synthesis, or supplier for AGI-183. If the library is to stock it, sourcing is a separate decision (see `brief-als.md` §5 item 2, compound-library data question).

---

## 6. What NOT to claim

- Do NOT claim AGI-183 + AAV6-hSyn-MCL1 treats, cures, or diagnoses ALS or any disease. **"Not a medical device" stays attached to every compound output.**
- Do NOT write "the study found / showed / demonstrated / proved" for any model output. All five discoveries are predictions.
- Do NOT present the 42-day MOMP (0.764 → 0.040), Bliss (+0.0052 day 2; +0.0305 day 13.25), or BH3 EC50 (~112.42 vs 65.29 → 15.84) figures as measured results. They are model predictions the proposed experiments aim to test.
- Do NOT present the AZD5991 figures in the paper's original framing — never write "troponin elevation in 83% of treated patients". Use the corrected framing: post hoc 54/65 (83%) post-dose vs 14/31 (45%) pre-dose; prospective AE rate 10.3% (8/78). Do NOT present 3.9% (3/78) without the subgroup breakdown: all responders MDS (3/5, 60%), 0/38 AML, 0/35 others.
- Do NOT present the seven-inhibitor failure as uniform — PRT1419 remains in active development and reported acceptable safety without cardiac toxicity in solid tumors; GS-9716's failure mode is undocumented. Date "none beyond Phase I/II" as of 2026-11-07.
- Do NOT call Akt/Bad a "validated predictive biomarker" in oncology — the evidence is preclinical NSCLC cell-line work (Rice 2019, pAKT S473), not clinical validation. Do NOT cite JCI 170169 as the anchor for the "no studies in neurodegeneration" claim, and do NOT write "completely novel / never proposed" without disclosing the 2012 pAkt-ALS patent (WO2012160563 / EP3263127B1) and the Léger 2006 / Dewil 2007 papers.
- Do NOT cite PMC2681190 for "MCL1 overexpression is low-risk in post-mitotic neurons" — it shows Mcl-1 loss causes massive neuronal apoptosis during CNS development, arguing for caution.
- Do NOT cite the paper's refs [10] and [11] as two sources, or refs [6] and [7] as two sources — each pair is the same paper cited twice.
- Do NOT give a structure, SMILES, molecular weight, dose, or price for the paper's AGI-183. None is in the paper.
- Do NOT import the `AGI_Compound_001.pdf` AGI-183 entry's SMILES, MW, IC50, or in-vitro/xenograft claims into the ALS briefs. Same name, different mechanism, unresolved (see §5 item 1).
- Do NOT claim the combination is in a trial, has a trial date, a lab, a partner, or funding. None is named in the paper.
- Do NOT number ALS as S34. ALS has no series number.
- Do NOT claim the ALS agent is online or able to take hires. It is offline as of 2026-11-06; 0 jobs completed, $0 earned.
- Do NOT claim the paper's safety rationale (neuron-targeted delivery circumventing cardiotoxicity/thrombocytopenia; MCL1 overexpression low-risk in post-mitotic neurons) is safety data. It is design rationale.
- Do NOT present the "antagonism-as-resilience" hypothesis as an established mechanism. It is the paper's own framing of its model predictions.

---

## 7. Figure-alignment notes for this area

| Figure | Resolution |
|---|---|
| Bliss −0.0422 (static model) vs +0.0052 day 2 (extended model) | Different models. Static model predicted antagonism; extended stochastic model (retrotranslocation + BH3-only compensation) predicts near-additivity. Quote each with its model. |
| Bliss +0.0305 (Discovery 2 text) vs +0.03048 (re-analysis) vs +0.029 day 42 vs +0.02898 (re-analysis) | Same values, different rounding. Use +0.0305 peak / +0.029 day 42 in prose; +0.03048 / +0.02898 only when quoting the re-analysis exactly. |
| Abstract "ΔBliss > 0.025" vs peak +0.0305 | Consistent: sustained Bliss above 0.025 with a peak near 0.0305. Quote the abstract's threshold and the peak together. |
| BH3 EC50 "around 112.42" vs ">112" (Key Insights) | Same prediction, different rounding. Use ~112.42 in prose. |
| AZD5991 troponin 54/65 (83%) vs response 3/78 (3.9%) | **Corrected per verification 2026-11-07.** Troponin: post hoc retrospective analysis of stored samples — 54/65 (83%) post-dose vs 14/31 (45%) pre-dose; prospective AE rate 8/78 (10.3%). Never "83% of treated patients". Response: 3/78 (3.9%) is a derived figure, not trial-stated; all responders MDS (3/5, 60%), 0/38 AML, 0/35 others. Source: Desai et al. Clin Cancer Res 2024, PMID 39167622 / PMC11528199. |
| Seven inhibitors, none beyond Phase I/II | **Corrected per verification 2026-11-07.** List real (ABBV-467, AMG 176, AMG 397, AZD5991, GS-9716, MIK665, PRT1419); "none beyond Phase I/II" accurate as of 2026-11-07. But "uniformly failed / cardiotoxicity predominant" is not universal: PRT1419 remains in active development with acceptable safety without cardiac toxicity in solid tumors; GS-9716's failure mode undocumented. |
| "Validated biomarker" (oncology) | **Corrected per verification 2026-11-07.** Rice 2019 (PMID 31150457) is preclinical NSCLC cell-line work on pAKT (S473) as a sensitivity marker — downgrade to "preclinical evidence supporting trial design". Not clinically validated; not pBad. |
| "No studies in neurodegeneration" | **Corrected per verification 2026-11-07.** Narrow claim not falsified, but "completely novel / never proposed" overstated: 2012 patent WO2012160563 / CA2836503 / EP3263127B1 proposed pAkt as an ALS biomarker; Léger 2006 / Dewil 2007 showed pAkt dysregulation in ALS patients. JCI 170169 does NOT support the claim — do not cite it as the anchor. Paper's search methods undocumented. |
| Refs [10]=[11], refs [6]=[7] | **Duplicates, verified 2026-11-07.** [10] and [11] are both Rice 2019; [6] and [7] are both Pan et al. Haematologica 2023/2024. Deduplicate; ref [11]'s Ser99/136 description belongs to Datta 1997 / Reactome R-HSA-198347. |
| PMC2681190 / MCL1 low-risk inference | **Corrected per verification 2026-11-07.** PMC2681190 shows Mcl-1 loss causes massive neuronal apoptosis during CNS development — argues for caution, not low risk. Do not cite it for "MCL1 overexpression is low-risk in post-mitotic neurons". |
| BH3 profiling oncology utility | **Verified 2026-11-07.** PMC3770266, PMC8316436, Pan et al. Haematologica confirmed. Gap claim (no longitudinal BH3 profiling in neurodegeneration) not contradicted, but ref [7] cannot evidence it (same Pan paper, oncology only). |
| AGI-183 in als_4_8.pdf vs AGI-183 in AGI_Compound_001.pdf | **Unresolved identity tension — do NOT merge.** BCL-XL stabilizer (paper) vs CRBN-binding FLIP inhibitor (catalog). |

---

## Sources

- `~/workspace/user/files/als_4_8.pdf` — "Synergistic Neuroprotection in ALS: Akt/Bad Phosphorylation as a Predictive Biomarker for BCL-2 Family Therapy", x@agicorp.network and Bios (bios@bio.xyz), created 2026-04-08. All facts in §§1–4 are from this paper; external-citation claims are marked [verified 2026-11-07] or [corrected per verification 2026-11-07].
- `~/workspace/your_files/bio-research-expansion/brief-als.md` — the companion ALS brief (jobs table, Answer ALS, ALS TDI, Project MinE, ChEMBL/PubChem, series-number correction). This brief adds the paper-grounded content only.
- `~/workspace/your_files/bio-research-expansion/inventory-bio.md` — where ALS content lives today (§§2, 4, 6).
- `~/workspace/your_files/bio-research-expansion/compound-agi183.md` — the AGI-183 compound entry (same directory).
- `~/workspace/user/files/AGI_Compound_001.pdf` — 450-page compound catalog; its "Compound AGI-183" entry is cited only for the identity tension in §5, not as a source for the paper's AGI-183.
- `~/workspace/your_files/bio-research-expansion/verification-als-4-8-citations.md` — citation verification, completed 2026-11-07 (Desai et al. PMID 39167622 / PMC11528199; PMC7731749; Datta 1997 PMID 9346240; Rice 2019 PMID 31150457; JCI 170169; patent WO2012160563 / EP3263127B1; Léger 2006; Dewil 2007; PMC2681190; PMC3221787; PMC3070914; PMC9257998; PMC3770266; PMC8316436; Pan et al. Haematologica; Reactome R-HSA-198347). All 7 required corrections from that file are applied in this brief.

---

## 8. NotebookLM video — "A New Strategy Against ALS" (appended 2026-11-07)

**Source video:** `~/workspace/user/media_library/video/dd/dd7b675cc59a9a9c9409d9129379213a9e1be8552cae1dcf18e9bae66d4478ed.mp4` — NotebookLM, 7m 23s, 1280x720, 47 MB. **Frame-derived notes only — no transcript exists** (Whisper not installed in this environment; checked 2026-11-07). Full scene-by-scene notes: `notebooklm-videos-als-desci.md` in this directory. **Published in this repo's `research/` folder as a research brief.**

### What the video shows (on-screen text only; narration not captured)

- Title: "A New Strategy Against ALS". Opening: "In ALS, the battle is to **save motor neurons**, the cells that control voluntary movement." Then: "**TDP-43 WEAKENS THE BCL-XL BODYGUARD** / LEAVING NEURONS VULNERABLE."
- Section "2 — The Secret Switch / A New Activation Method", with a definition card: "**Allosteric Site** — A 'secret switch' on a protein, distinct from its active site, that can modulate its function."
- A chart titled "**Top 5 Stabilizer Candidates — Simulated FP Dose Response Curves**" with the text: "A screening process identified **five promising stabilizer candidates from the AGI compound library**."
- "**KINETIC STABILIZATION: BINDING DURATION**" — short binding duration vs prolonged stabilization, with **AGI-183** shown bound to the protein (padlock icon). Both mini-charts label the y-axis "Enegy" [sic — on-screen typo].
- Three further dose-response panels — **Neuronal Survival**, **Cleaved Caspase-3**, **Mitochondrial Membrane Potential** (dose 0.001–10 µM) — with legends naming five candidates: **AGI-183, AGI-138, AGI-124, AGI-120, AGI-129**. Caption: "Payoff: The best stabilizer, **AGI-183**, was also the most potent for neuronal survival."
- Section "4 — Resilience & Redundancy / Solving the Paradox" ("redundant, robust defense"), a closing hub ("A New Era of Research": Open-Source Compounds, Decentralized Funding, Global Data Collaboration, AI-Driven Discovery), and the closing question: "**If antagonism creates resilience in ALS, what's next?**"
- Sections 1 and 3 title cards were not caught in the sampled frames; their titles are not recorded — do not guess them.

### Honesty rules for any use of this video

- **All dose-response curves in this video are SIMULATED — never measured.** The chart title says so ("Simulated FP Dose Response Curves"). Label them SIMULATED in every place they are mentioned. They prove nothing.
- **The video's "five" is NOT the paper's "five".** The paper's five discoveries are five **computational-model predictions** (near-additive acute MOMP, Bliss +0.0052 day 2; strengthening synergy, 42-day MOMP 0.764 → 0.040, Bliss peak +0.0305 day 13.25; BH3 EC50 ~112.42 vs 65.29 → 15.84; seven MCL1 inhibitors, none beyond Phase I/II; Akt/Bad biomarker) — **none of them is a candidate compound**. Do NOT conflate the video's five candidate compounds with the paper's five predicted discoveries.
- **Video-only, no paper counterpart:** the five-candidate screening (AGI-138, AGI-124, AGI-120, AGI-129 appear nowhere in `als_4_8.pdf` — the paper names no candidate besides AGI-183), the SIMULATED dose-response curves, the neuronal-survival / caspase-3 / membrane-potential assays, the allosteric-site and kinetic-stabilization framing, and the "antagonism creates resilience" framing. The paper gives no SMILES, structure, dose, or screening data for AGI-183.
- **Paper-only, absent from the video:** the combination partner **AAV6-hSyn-MCL1**, the **Akt/Bad** stratification hypothesis, **Bliss** analysis, **BH3 profiling**, and the proposed **2x2 factorial** validation. The video presents AGI-183 alone; the paper's proposal is the combination.
- **Overlap is one point only:** AGI-183 as a BCL-XL stabilizer, in a TDP-43 / BCL-XL / motor-neuron framing consistent with the paper's background. The video's "most potent for neuronal survival" claim is the video's claim about its own SIMULATED curves — not a paper finding, not a measured result.
- **Do NOT add AGI-138, AGI-124, AGI-120, or AGI-129** to the compound library, `data.js`, or any priced job — they are names on a video frame, with no paper source, no structure, no data file, and no verified identity.
- The video's AGI-183 is the paper's BCL-XL stabilizer — the §5 identity tension still applies (do NOT merge with the catalog's CRBN-binding FLIP inhibitor of the same name).
- No treatment, cure, diagnosis, or medical-device claims. The ALS Researcher is not a medical device.

### Placement

- Companion explainer for the ALS briefs and the AGI-183 compound entry (`compound-agi183.md`), labelled as NotebookLM video content, not paper content. Usable with `als-02-from-compound-to-treatment.md` ONLY with the SIMULATED label and the "video's claim, not the paper's finding" line attached.
- Stills staged locally (binaries, browser web-upload route only): `assets/video1-als_tdp43-bclxl-bodyguard.jpg`, `assets/video1-als_simulated-dose-response.jpg`, `assets/video1-als_kinetic-stabilization-agi183.jpg`. The source video (47 MB) was NOT pushed.
