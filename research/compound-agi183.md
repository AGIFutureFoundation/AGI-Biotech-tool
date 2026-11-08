# Compound Entry — AGI-183

**Published:** compound-library entry in this repo's `research/` folder.
**Research date: 7 November 2026. Primary source: `~/workspace/user/files/als_4_8.pdf` — "Synergistic Neuroprotection in ALS: Akt/Bad Phosphorylation as a Predictive Biomarker for BCL-2 Family Therapy", authors x@agicorp.network and Bios (bios@bio.xyz), created 2026-04-08.**
**Status: CANDIDATE entry. Not a stocked compound, not a priced job, not a library holding. The ALS compound library has no data file (see `brief-als.md` §1) — this entry is a brief for the library work, not library data.**

## Honesty lines (read first — they govern every field)

- **PREDICTED, NOT DEMONSTRATED — absolute rule.** Everything the paper says about AGI-183's effects is a **computational-model prediction** ("predicted", "aims to validate"). Label every model result as a prediction in every sentence that states it. **Never write "the study found / showed / demonstrated" for model outputs.** There are no wet-lab results for AGI-183 in the paper.
- **No treatment, cure, diagnosis, or medical-device claims anywhere.** The ALS Researcher is "not a medical device." Nothing here claims AGI-183 treats, cures, or diagnoses ALS or any disease.
- **Citation status: VERIFIED WITH CORRECTIONS, 2026-11-07.** The paper's external citations were independently verified (`verification-als-4-8-citations.md`, 2026-11-07). Seven corrections were applied to this entry: (1) AZD5991 troponin reframed as a post hoc analysis with pre-dose baseline; (2) the 3.9% response rate given with its MDS subgroup breakdown; (3) the seven-inhibitor "uniform failure" claim qualified with the PRT1419 exception; (4) duplicate refs [10]=[11] and [6]=[7] noted; (5) "validated biomarker in oncology" downgraded to preclinical cell-line evidence; (6) the JCI 170169 anchor dropped and 2012 patent + 2006/2007 prior art disclosed; (7) the PMC2681190 "low-risk MCL1 overexpression" inference corrected — it argues for caution. Claims below carry **[verified 2026-11-07]** (confirmed as cited) or **[corrected per verification 2026-11-07]** (framing fixed per the verification file). No external citation in this entry is presented as verified beyond what the verification file establishes.
- **The paper never mentions a DAO.** AGI-183 is a compound in a research proposal, not a DAO document or launch. Do not frame it as one.
- **IDENTITY TENSION — READ §5 BEFORE USING ANY FIELD BELOW.** A second file, `~/workspace/user/files/AGI_Compound_001.pdf`, contains an entry also named "Compound AGI-183" describing a **CRBN-binding FLIP inhibitor** (pro-apoptotic, cancer) — the opposite mechanism to the paper's **BCL-XL stabilizer** (anti-apoptotic, neuroprotective). Same identifier, opposite mechanisms. **Do NOT merge the two entries.** All fields in §§1–4 describe the paper's AGI-183 only. §5 records the catalog entry separately, with the tension flagged as unresolved.

---

## 1. Identity (per the paper only)

| Field | Value | Source / note |
|---|---|---|
| Name | **AGI-183** | als_4_8.pdf, throughout |
| Class (per paper) | **BCL-XL stabilizer**; described as "an AGI compound" | als_4_8.pdf, Abstract + Background |
| Role | One half of a proposed combination: **AGI-183 + AAV6-hSyn-MCL1** (a vector for neuron-specific MCL1 overexpression) | als_4_8.pdf, Abstract |
| Proposed indication area | ALS neuroprotection (research proposal — **not a treatment**) | als_4_8.pdf |
| SMILES | **Not given in the paper** | Do not invent. See §5 for why the catalog's SMILES must NOT be imported here. |
| Molecular weight | **Not given in the paper** | Do not invent. |
| Structure | **Not given in the paper** | Do not invent. |
| Dose / concentration | **Not given in the paper** | Do not invent. |
| Source / synthesis / supplier | **Not given in the paper** | Sourcing is an open question (see §6). |
| Binding / potency data | **None in the paper** (no IC50, Kd, EC50 for AGI-183 itself) | The EC50 figures in §3 are BH3-profiling readouts of the *combination's predicted effect on neurons*, not AGI-183 potency. Do not confuse them. |
| Regulatory status | None. Not approved, not in a trial, no IND. | No trial, lab, partner, or funding is named in the paper. |

---

## 2. Mechanism (per the paper)

- **What it is proposed to do:** stabilise **BCL-XL**, an anti-apoptotic BCL-2 family protein, enhancing its survival function.
- **BCL-XL's survival function:** BCL-XL sequesters the pro-apoptotic protein **BAX**, preventing it from inducing mitochondrial outer membrane permeabilization (MOMP). BCL-XL also **actively retrotranslocates BAX from mitochondria** — a key survival function the paper proposes a stabilizing agent like AGI-183 can enhance [verified 2026-11-07 — PMC3070914, "Bcl-x(L) retrotranslocates Bax from the mitochondria into the cytosol", Cell 2011].
- **Orthogonality to MCL1 (the combination rationale):** MCL1 and BCL-XL provide orthogonal anti-apoptotic protection by preferentially sequestering **BAK** and **BAX**, respectively [verified 2026-11-07 — PMC3221787, "A unified model of mammalian BCL-2 protein family interactions at the mitochondria", Mol Cell 2011]. AGI-183 (BCL-XL/BAX arm) and AAV6-hSyn-MCL1 (MCL1/BAK arm) are therefore proposed to cover both pro-apoptotic effectors.
- **Akt/Bad interaction:** the PI3K/Akt pathway phosphorylates Bad, inhibiting its pro-apoptotic activity via 14-3-3 sequestration. Low Akt phosphorylation of Bad leaves BCL-XL functionally antagonized — so the paper predicts neurons in an Akt-low / pBad-low state would derive greater marginal benefit from a BCL-XL stabilizing therapy such as AGI-183 [verified 2026-11-07 — Datta et al. Cell 1997, PMID 9346240; Reactome R-HSA-198347 confirms Akt phosphorylates BAD at Ser99 (mouse Ser136)]. This is the mechanistic basis of the paper's Akt/Bad stratification hypothesis.
- **What AGI-183 is NOT, per the paper:** it is not described as an inhibitor, a degrader, a BH3 mimetic, or a CRBN binder anywhere in als_4_8.pdf. Any CRBN description of "AGI-183" comes from the separate catalog file — see §5.

---

## 3. Model-predicted effects (all predictions — combination arm, not AGI-183 alone)

The paper's model predictions are for the **combination** (AGI-183 + AAV6-hSyn-MCL1). The paper does not isolate a predicted AGI-183-alone effect size for the long-term endpoints; single-agent arms are predicted to be individually sufficient to prevent MOMP acutely (the floor effect). Quote combination predictions as combination predictions.

- **Acute MOMP inhibition — predicted near-additive (Discovery 1):** the extended stochastic model predicts a **near-additive Bliss excess of +0.0052 at day 2** (and +0.00815 at Day 1), i.e. the combination is predicted to be neither synergistic nor antagonistic acutely, because each intervention alone is predicted to be sufficient to prevent MOMP over 42 days (mechanistic floor effect). The initial static model had predicted antagonism (Bliss −0.0422); the extended model supersedes it for the paper's conclusions.
- **Long-term synergy — predicted strengthening (Discovery 2):** the model predicts **42-day MOMP probability 0.764 (control) → 0.040 (combination)**, a 94.8% reduction in cumulative MOMP incidence as the paper calculates it. Time-resolved Bliss excess is predicted at **+0.008 at day 1, peaking at +0.0305 at day 13.25, and +0.029 at day 42** (re-analysis: +0.00815 / +0.03048 / +0.02898). The abstract states sustained positive Bliss interaction with **ΔBliss > 0.025**.
- **Attenuated mitochondrial priming — predicted (Discovery 3):** the model predicts the combination holds **BH3 profiling EC50 around 112.42** over 42 days, while control EC50 is predicted to fall from **65.29 to 15.84** (increasing priming). The paper presents this as a novel, testable endpoint for neurodegeneration.
- **Stratification — predicted (Discovery 5 / central hypothesis):** the paper predicts **Akt-low / pBad-low neuronal subpopulations will show greater marginal benefit** from the combination, and proposes Akt/Bad phosphorylation status as a predictive biomarker. The paper's literature review states no study has proposed or validated this biomarker in neurodegeneration — the **narrow claim was not falsified** by independent verification searches (2026-11-07) [verified 2026-11-07 — narrow claim survived] — BUT: the paper's anchor ref [9] (JCI 170169) does **not** support the claim (oncology paper, no literature search, nothing about neurodegeneration — do not cite it as the anchor), and prior art narrows the novelty: a granted patent (**WO2012160563 / CA2836503 / EP3263127B1**, filed 2012, granted 2019) claims pAkt as a biomarker for ALS progression prognosis and assessing responsiveness to treatment, and **Léger et al. 2006 / Dewil et al. 2007** showed pAkt dysregulation in ALS patients — so "completely novel / never proposed" is overstated. The paper states the biomarker is validated in oncology for combined MCL-1 and BCL-2/BCL-XL inhibition — **DOWNGRADED per verification:** the cited source (Rice et al., PLOS ONE 2019, PMID 31150457) is **preclinical NSCLC cell-line work** on pAKT (S473) as a sensitivity marker; it does not clinically validate any biomarker in patients, and it measures pAKT, not pBad. Correct framing: **"preclinical evidence supporting trial design"**. The paper's refs [10] and [11] are the same Rice 2019 paper cited twice. [corrected per verification 2026-11-07]
- **Wording to use on any library output:** "AGI-183 is a proposed BCL-XL stabilizer. In combination with AAV6-hSyn-MCL1, computational models predict [figure], in iPSC-derived TDP-43 Q331K motor neurons under chronic glutamate stress. These are predictions the proposed 2x2 factorial study aims to validate — not measured results. The ALS Researcher is not a medical device."

---

## 4. Safety rationale (paper's design argument — NOT safety data)

- **The argument:** neuron-targeted MCL1 gain-of-function plus BCL-XL stabilization is *designed to circumvent* the known on-target toxicities of systemic inhibitors — **cardiotoxicity (MCL1)** and **thrombocytopenia (BCL-XL)** [verified 2026-11-07 with a split: PMC9257998 (navitoclax, Leuk Lymphoma 2021) supports the thrombocytopenia half; the cardiotoxicity half rests on refs [1]–[3], incl. review PMC7731749, confirmed].
- **The MCL1 precedent, CORRECTED per verification 2026-11-07:** the paper's review states all seven clinical-stage systemic MCL1 inhibitors (ABBV-467, AMG 176, AMG 397, AZD5991, GS-9716, MIK665, PRT1419) failed to advance beyond Phase I/II. "None beyond Phase I/II" is accurate as of 2026-11-07, but "uniformly failed" is not: **PRT1419 remains in active development** and reported acceptable safety without cardiac toxicity in solid tumors, and GS-9716's failure mode is undocumented. For AZD5991, the correct framing is: high-sensitivity troponin T elevated in **54/65 (83%)** patients after any dose in a **post hoc** analysis of stored samples, versus **14/31 (45%)** before any dose; prospectively reported troponin elevations **8/78 (10.3%)**. Overall response **3/78 (3.9%)**, all in MDS (**3/5, 60%**); no responses in AML (0/38) or other histologies (0/35). Never write "troponin elevation in 83% of treated patients" and never present 3.9% without the MDS breakdown. (Desai et al. Clin Cancer Res 2024, PMID 39167622 / PMC11528199.)
- **The post-mitotic argument, CORRECTED per verification 2026-11-07:** the paper states MCL1 overexpression, while oncogenic in dividing cells, is considered low-risk in post-mitotic neurons, citing PMC2681190 — **that citation does not support the inference.** PMC2681190 (J Neurosci 2008) shows Mcl-1 loss causes massive neuronal apoptosis during CNS development, i.e. MCL1 is essential in developing neurons — which argues for **caution**, not low risk. **Do not cite PMC2681190 for "MCL1 overexpression is low-risk in post-mitotic neurons".**
- **What this is not:** no toxicity experiment, no dose, no animal data, and no safety result is reported in the paper. **Do NOT present the safety rationale as safety data, a safety finding, or evidence that AGI-183 is safe.** It is a design argument for a proposed experiment.

---

## 5. Identity tension — the `AGI_Compound_001.pdf` entry also named AGI-183 (DO NOT MERGE)

**What was found:** `~/workspace/user/files/AGI_Compound_001.pdf` (450-page compound catalog, 2,786,539 B) contains an entry headed **"Compound AGI-183"** (text layer, around line 8309 of the extracted text). A second file in the same directory, `Venetoclax_SMILES____CC_C__C_C__O_NC1_CC_C_C_C1_N2C_NC3_C2C_CC__C3.pdf`, is a SMILES file for venetoclax (a BCL-2 inhibitor) — adjacent reference material, not AGI-183.

**What the catalog entry says (the catalog's own words, summarised — NOT verified by this worker):**
- SMILES: `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(Br)C=C4`; MW 353.32 g/mol; LogP 4.1; ΔG −8.6 kcal/mol; QSAR-predicted IC50 0.5 µM; Molecular Goodness Score 0.82.
- Mechanism stated in the catalog: **binds CRBN** (E3 ubiquitin ligase component) with high specificity via a bromine atom; **targets CRBN-mediated degradation of FLIP**, stabilising pro-apoptotic FADD and caspase-8 and promoting **extrinsic apoptosis** in FLIP-dependent cancers.
- The catalog further claims in-vitro apoptosis induction in FLIP-dependent cancer cell lines (IC50 0.5 µM) and tumour reduction in xenograft models, with mechanism "validated" by Western blot and apoptosis assays.

**Why this is a tension, not a complement:**
- The paper's AGI-183 is a **BCL-XL stabilizer** — **anti-apoptotic**, proposed to *prevent* neuronal death.
- The catalog's AGI-183 is a **CRBN-binding FLIP inhibitor** — **pro-apoptotic**, claimed to *induce* cancer-cell death.
- Same identifier, opposite directions of effect on apoptosis, different targets (BCL-XL vs CRBN/FLIP), different disease areas (ALS neuroprotection vs cancer).
- The catalog's in-vitro / xenograft claims are the catalog's own unverified claims. They were **not** checked against any primary source in this session and must **not** be presented as validation of the paper's predictions, or as evidence about the paper's AGI-183.

**Rules until Mike resolves it:**
1. Do NOT merge the entries. Do NOT quote the catalog's SMILES, MW, LogP, ΔG, IC50, or Goodness Score as properties of the paper's AGI-183.
2. Do NOT present the catalog's in-vitro / xenograft claims as results for the paper's AGI-183.
3. Do NOT use the catalog entry to fill the paper's missing fields (§1: SMILES, MW, structure, dose, source). Those fields stay "not given in the paper".
4. Possible resolutions (for Mike, not assumed here): same compound with two proposed mechanisms; two different compounds sharing the name "AGI-183"; a catalog error; or a naming collision between the ALS proposal and the compound catalog. The 450-page catalog numbers compounds sequentially (AGI-001…AGI-183…AGI-185+ seen in the extracted text), which suggests "AGI-183" is a catalog sequence number — but that does not by itself resolve the mechanism conflict.
5. Any future library page for AGI-183 must carry a visible note of this tension until it is resolved in writing.

---

## 6. How AGI-183 connects to the ALS compound-library jobs

The ALS Researcher ($ALS) offers six compound-library jobs plus one subscription (verified live in Virtuals ACP 2026-11-06; **agent offline, 0 jobs completed, $0 earned** — see `brief-als.md` Item 1). AGI-183 is a **candidate entry** for that library, not a stocked compound. Its fit per job:

| Job (price / turnaround) | How AGI-183 fits | What must NOT happen |
|---|---|---|
| **compound_lookup** ($2 / 30min) | The natural lookup target: return this entry — name, class (BCL-XL stabilizer, per the paper), combination partner, predicted effects with "predicted" labelling, and the §5 identity tension. | Do not return a SMILES, MW, or dose — none is in the paper. Do not return the catalog's values. |
| **compound_research_report** ($25 / 48h) | The natural report subject: the full paper-grounded dossier — mechanism (§2), the five predicted discoveries with numbers (§3), the safety rationale as design argument (§4), the validation experiments proposed, and the identity tension (§5). Attach the "not a medical device" line. | Do not present predictions as results. Do not revert any corrected framing to the paper's original wording. Do not present the catalog's xenograft claims as validation. |
| **compound_screening_pack** ($150 / 72h) | **Not applicable yet.** A screening pack implies screening data or a screen design. The paper proposes a 2x2 factorial validation (iPSC-derived TDP-43 Q331K motor neurons, chronic glutamate stress; endpoints: longitudinal BH3 profiling, time-resolved survival analysis) — that design can be *described* in a pack, but no screen has been run and no screening data exists. | Do not sell or imply a screening result for AGI-183. Do not quote a library size or screening outcome. |
| compound_library_snapshot ($10 / 24h) | AGI-183 appears only as a candidate entry count of one, labelled candidate — and only once the entry is approved for the library. | Do not count it as a stocked compound before approval. |
| compound_data_access ($50 / 24h) | **Nothing to serve.** No AGI-183 data file exists (no structure, no assay data, no screening data). | Do not claim data access delivers AGI-183 data. |
| library_growth_report ($15 / 48h) | AGI-183 can be listed as a candidate added by this brief, once approved. | Do not present candidate addition as library growth in stocked compounds. |
| library_weekly ($25 / 30d) | Future updates on the citation verification and the identity-tension resolution belong here, once approved. | Do not promise updates on a schedule no one owns. |

**Every compound output must carry, verbatim:** "The ALS Researcher is not a medical device. It provides compound-library research information only. It does not diagnose, treat, or cure ALS or any disease." (Per `brief-als.md` Item 2.)

---

## 7. Proposed validation (what would test this entry)

From the paper (proposed, not run — see `brief-als-agi183.md` §4 Item 4 for the full list):

1. **2x2 factorial wet-lab validation** in iPSC-derived TDP-43 Q331K motor neurons under chronic glutamate stress (control / AGI-183 / AAV6-hSyn-MCL1 / combination).
2. **Longitudinal BH3 profiling** over 42 days — tests the predicted EC50 trajectories (control 65.29 → 15.84; combination held ~112.42).
3. **Time-resolved survival analysis** over 42 days — tests the predicted MOMP trajectory (0.764 → 0.040) and Bliss time-course (peak +0.0305 at day 13.25).
4. **Stratification test** — whether baseline Akt-low / pBad-low subpopulations show greater marginal benefit (tests the Akt/Bad biomarker hypothesis).
5. **"Antagonism-as-resilience" test** — whether acute near-additivity (Bliss +0.0052 day 2) genuinely transitions to long-term synergy, as the model predicts.

**None of these has been run or reported. No lab, partner, timeline, or funding is named in the paper.** The entry's status stays "candidate — predictions only" until at least the factorial validation is reported.

---

## 8. What NOT to claim (compound-entry edition)

- Do NOT claim AGI-183 treats, cures, or diagnoses ALS or any disease. **"Not a medical device" stays attached to every compound output.**
- Do NOT write "the study found / showed / demonstrated / proved" for any model output. All effects in §3 are predictions.
- Do NOT give a SMILES, molecular weight, structure, dose, IC50, or supplier for the paper's AGI-183. None is in the paper.
- Do NOT import the catalog entry's SMILES (`C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(Br)C=C4`), MW 353.32, LogP 4.1, ΔG −8.6, IC50 0.5 µM, or Goodness Score 0.82 into this entry. Same name, different mechanism, unresolved (§5).
- Do NOT present the catalog's in-vitro / xenograft claims as validation of the paper's predictions.
- Do NOT present the safety rationale (§4) as safety data. It is a design argument.
- Do NOT present the AZD5991 figures in the paper's original framing — never "troponin elevation in 83% of treated patients"; use the corrected framing in §4 (post hoc 54/65 post-dose vs 14/31 pre-dose; prospective 8/78). Do NOT present 3.9% (3/78) without the MDS subgroup (3/5, 60%). Do NOT present the seven-inhibitor failure as uniform — PRT1419 remains in active development without cardiac toxicity; GS-9716's failure mode is undocumented.
- Do NOT call Akt/Bad a "validated predictive biomarker" in oncology — the evidence is preclinical NSCLC cell-line work (Rice 2019, pAKT S473). Do NOT cite JCI 170169 as the anchor for the "no studies" claim, and do NOT write "completely novel / never proposed" without disclosing the 2012 pAkt-ALS patent (WO2012160563 / EP3263127B1) and the Léger 2006 / Dewil 2007 papers.
- Do NOT cite PMC2681190 for "MCL1 overexpression is low-risk in post-mitotic neurons" — it shows Mcl-1 loss causes massive neuronal apoptosis during CNS development, arguing for caution.
- Do NOT cite the paper's refs [10] and [11] as two sources, or refs [6] and [7] as two sources — each pair is the same paper cited twice.
- Do NOT list AGI-183 as a stocked library compound, a priced job, or a screening result. It is a candidate entry.
- Do NOT frame AGI-183 as a DAO document or launch. The paper never mentions a DAO.
- Do NOT number ALS as S34. ALS has no series number.

---

## 9. Open questions needing Mike's decision

1. **AGI-183 identity tension (§5):** same compound with two proposed mechanisms, two compounds sharing a name, or a catalog error? Until resolved in writing, the two entries stay separate and the paper's fields stay blank where the paper is silent.
2. **Sourcing:** the paper gives no source, synthesis, or supplier for AGI-183. If the library is to stock it, who sources it and who verifies identity (structure confirmation) before it is listed?
3. **Citation verification — COMPLETE (2026-11-07):** the 7 required corrections from `verification-als-4-8-citations.md` are applied in this entry (§§2–4, §8). The entry uses the corrected framing throughout and does not need to wait for any further verification — but it must not revert to the paper's original wording on AZD5991, the seven-inhibitor claim, the "validated biomarker" claim, the JCI 170169 anchor, or the PMC2681190 inference.
4. **Screening pack:** the paper proposes a validation design but no screen exists. Should a future pass design a screening pack around the 2x2 factorial + BH3 profiling protocol, or should `compound_screening_pack` stay inapplicable for AGI-183 until wet-lab data exists?
5. **Catalog cross-check:** should a follow-up pass systematically check the `AGI_Compound_001.pdf` catalog for other name collisions with paper compounds (AGI-183 is #183 of a numbered sequence; the catalog's numbering may collide with other paper compound names)?

---

## Sources

- `~/workspace/user/files/als_4_8.pdf` — "Synergistic Neuroprotection in ALS: Akt/Bad Phosphorylation as a Predictive Biomarker for BCL-2 Family Therapy", x@agicorp.network and Bios (bios@bio.xyz), created 2026-04-08. All fields in §§1–4, 7 are from this paper; external-citation claims are marked [verified 2026-11-07] or [corrected per verification 2026-11-07].
- `~/workspace/user/files/AGI_Compound_001.pdf` — 450-page compound catalog (2,786,539 B). Its "Compound AGI-183" entry is recorded in §5 only, as the other side of an unresolved identity tension — not as a source for the paper's AGI-183.
- `~/workspace/user/files/Venetoclax_SMILES____CC_C__C_C__O_NC1_CC_C_C_C1_N2C_NC3_C2C_CC__C3.pdf` — venetoclax SMILES file in the same directory; adjacent BCL-2 reference material, not AGI-183.
- `~/workspace/your_files/bio-research-expansion/brief-als-agi183.md` — the companion ALS brief (full five-discovery write-up, validation experiments, add/correct items).
- `~/workspace/your_files/bio-research-expansion/brief-als.md` — the companion ALS brief (compound-library jobs table with real ACP prices, "not a medical device" rule, series-number correction).
- `~/workspace/your_files/bio-research-expansion/brief-cancer-dao.md` — the companion Cancer DAO brief (BCL-2 bridge; the paper does not launch or mention any DAO).
- `~/workspace/your_files/bio-research-expansion/verification-als-4-8-citations.md` — citation verification, completed 2026-11-07 (Desai et al. PMID 39167622 / PMC11528199; PMC7731749; Datta 1997 PMID 9346240; Rice 2019 PMID 31150457; JCI 170169; patent WO2012160563 / EP3263127B1; Léger 2006; Dewil 2007; PMC2681190; PMC3221787; PMC3070914; PMC9257998; PMC3770266; PMC8316436; Pan et al. Haematologica; Reactome R-HSA-198347). All 7 required corrections from that file are applied in this entry.
