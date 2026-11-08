# Enhancement Brief — Cancer DAO: a research agenda from the BCL-2 bridge (als_4_8.pdf)

**Published:** research brief in this repo's `research/` folder.
**Research date: 7 November 2026. Evidence: `~/workspace/user/files/als_4_8.pdf` — "Synergistic Neuroprotection in ALS: Akt/Bad Phosphorylation as a Predictive Biomarker for BCL-2 Family Therapy", authors x@agicorp.network and Bios (bios@bio.xyz). PDF 1,053,308 B, created 2026-04-08, LaTeX via pandoc.**
**Applies to:** any future Cancer DAO page, article, or series content on the Foundation site, and to the existing pages that mention Cancer DAO only as a world/name. Complements (does NOT replace) `brief-cancer.md`, which covers the open cancer data (TCGA/GDC, cBioPortal, SEER, ClinicalTrials.gov, FDA approvals) — this brief adds a second, distinct content pillar: the BCL-2 family therapeutics agenda that follows from the ALS paper. A later worker should be able to apply this brief without re-reading the paper: every item below gives the exact paper-grounded fact and its location in the paper.**

## Honesty lines (read first — they govern every item)

- **THE PAPER DOES NOT LAUNCH OR MENTION ANY DAO.** A full-text search of als_4_8.pdf finds **no "DAO" mention anywhere in the paper**. The paper never launches, proposes, or describes a DAO — not the Cancer DAO, not an ALS DAO, not any DAO. **Do not write that the paper "launches the Cancer DAO" or "launches both DAOs". That framing is wrong.** The paper is a **scientific launchpad** for Cancer DAO work: the BCL-2 / Akt-Bad biology bridges oncology and ALS, and the MCL1 inhibitor failure history is oncology history. The paper gives the Cancer DAO a research agenda — **not an existence**.
- **The Cancer DAO itself remains a proposed entity.** Today it is only a world name with a Fred Hutchinson anchor (see §1). It is not a research programme, a trial, a dataset, a series, or a formed entity. Nothing in this brief forms it.
- **PREDICTED, NOT DEMONSTRATED — absolute rule.** The paper is a research proposal plus computational-model predictions. All five of its discoveries are computational-model predictions ("predicted", "aims to validate"). Label every model result as a prediction in every sentence that states it. **Never write "the study found / showed / demonstrated" for model outputs.** There are no wet-lab results in this paper.
- **No treatment, cure, diagnosis, or medical-device claims anywhere.** Nothing here claims any compound treats, cures, or diagnoses any cancer or any disease. FDA approvals cited in `brief-cancer.md` are regulatory facts about specific drugs for specific indications — not endorsements, and not evidence about any other compound.
- **Citation status: VERIFIED WITH CORRECTIONS, 2026-11-07.** The paper's external citations were independently verified (`verification-als-4-8-citations.md`, 2026-11-07). Seven corrections were applied to this brief: (1) AZD5991 troponin reframed as a post hoc analysis with pre-dose baseline; (2) the 3.9% response rate given with its MDS subgroup breakdown; (3) the seven-inhibitor "uniform failure" claim qualified with the PRT1419 exception; (4) duplicate refs [10]=[11] and [6]=[7] noted; (5) "validated biomarker in oncology" downgraded to preclinical cell-line evidence; (6) the JCI 170169 anchor dropped and 2012 patent + 2006/2007 prior art disclosed; (7) the PMC2681190 "low-risk MCL1 overexpression" inference corrected — it argues for caution. Claims below carry **[verified 2026-11-07]** (confirmed as cited) or **[corrected per verification 2026-11-07]** (framing fixed per the verification file). No external citation in this brief is presented as verified beyond what the verification file establishes.
- **Cancer DAO has no W3 series number.** It is a world / focus domain, not a series. Do not invent one. "33 named W3 sub-series in the April 2026 internal list" — never 35. W3 series are proposed, not formed; filed fact (Foundation B20260196664, Fellowship B20260229217) stays apart from proposed plans.
- **The ALS agent is offline** — listed in Virtuals ACP, no instance deployed, 0 jobs completed, $0 earned (as of 2026-11-06). There is no Cancer DAO agent at all.

---

## 1. What exists today — honest inventory

From `inventory-bio.md` §§2, 5, 7, 9, 11.1 and `brief-cancer.md` §1. **There is zero cancer research content anywhere on the machine.** "Cancer" appears only as:

- **(a) The Cancer DAO world/name:**
  - WorldForge Earth page "Original DAO Worlds (33)" marks Cancer Dao (Fred Hutchinson Cancer Center, Seattle) **Live as a web-viewer world only (not RP1-attached)** (memory 2026-10-26).
  - Cancer-dao + biota-blockchain among the first 41 WorldForge worlds (`~/workspace/your_files/rp1-review/` — promo-video manifests + WorldForge setup doc; Cancer Dao anchor Seattle **47.6263, -122.3292**, Fred Hutchinson).
  - Promo-video manifests + bright-brand shorts incl. a Cancer DAO short (`~/workspace/your_files/rp1-review/promo-videos/`; memory 2026-11-04/05 — Cancer DAO short in Batch 2/3; Foundation video set 24/25 incl. Cancer DAO short; video-enhancement wave, 5 shorts incl. biota + cancer linking to series index as fallback — **no dedicated series page**).
  - Cancer DAO as one of 6 PBC focus-domain DAOs (Cancer, Robotics, Ecology, Climate, Education, Public Health) (memory 2026-10-26).
  - `~/workspace/your_files/worlds-3d-iwsdk/` and `~/workspace/your_files/worlds-3d-depth-2-drafts/` — world definitions only; no bio research content.
- **(b) One line in `als-01`:** `~/workspace/your_files/agifuturefoundation-articles/als/als-01-what-a-compound-library-is.md` — natural-product cancer drugs cited as an example class of compound libraries.
- **(c) One line in `diagnostic-x-01`:** `~/workspace/your_files/agifuturefoundation-articles/diagnostic-x/diagnostic-x-01-screening-vs-diagnosis.md` — cervical cancer screening as the classic example of screening done as a programme. Its site page is `~/workspace/your_files/hostinger-email/sites/agifuturefoundation.org/articles/article-54-screening-vs-diagnosis.html`.
- **(d) A funder name in contacts CSVs:** Cancer Prevention and Research Institute of Texas (a funder name in `~/workspace/user/files/` ZoomInfo contacts CSVs and in `~/workspace/goals/contacts-and-molecule-file-consolidation/files/contacts-organized/` — a company/funder name, not research).
- **Foundation site counts:** cancer appears in 12 Foundation-site files — all catalog/cross-link mentions, not cancer content. **No cancer series page, no cancer article, and no cancer research page** exists.
- **Staged articles counts:** cancer appears in 2 staged-article files (the two one-line mentions above).
- **No cancer repo** in Mike's org (`githubs.md` §12; the org's bio repos are bioacoustics-cloud, bioacoustics-cloud-pages, AGI-Biotech-tool, toxicology, wave-site, wave.agifuturefoundation.org).

**Consequence for the worker:** do not "fix" a cancer page — there is none to fix. Items in §3 are **new-page specifications**. Each new page must be labelled as new content, dated, and sourced as below. If Mike has not approved a cancer page, do not create one — this brief is a specification for when he does. **And do not present the ALS paper as the Cancer DAO's founding document — it is not. It is a scientific source the Cancer DAO's research agenda draws on.**

---

## 2. The BCL-2 bridge — what the paper actually gives the Cancer DAO

The paper is an ALS paper. Its value to the Cancer DAO is that **the same biology is oncology biology**. Three strands of the paper are oncology history or oncology-validated science, ported into an ALS proposal:

### Strand A — MCL1 and BCL-XL are cancer drug targets
- The paper's premise is that anti-apoptotic BCL-2 family members (BCL-XL, MCL1) sequester pro-apoptotic BAX/BAK and prevent MOMP. That is the same mechanism that makes them cancer drug targets: cancer cells depend on these proteins to evade apoptosis.
- The paper states MCL1 and BCL-XL provide orthogonal protection by preferentially sequestering **BAK** and **BAX** respectively, and that BCL-XL actively retrotranslocates BAX from mitochondria [verified 2026-11-07 — PMC3221787 (Mol Cell 2011) for orthogonal sequestration; PMC3070914 (Cell 2011) for retrotranslocation].
- **Cancer DAO relevance:** this is the shared target biology. A Cancer DAO research agenda on BCL-2 family therapeutics starts from the same target map the ALS paper uses — MCL1/BAK, BCL-XL/BAX, BH3-only proteins, MOMP as the readout.

### Strand B — The systemic MCL1 inhibitor failures are oncology history
- The paper's Discovery 4 is a systematic review of **clinical-stage MCL1 inhibitors developed for cancer** that failed in oncology trials. This is oncology history, synthesised in an ALS paper as the rationale for a tissue-targeted approach.
- Paper's figures, **CORRECTED per verification 2026-11-07** (Desai et al., *Clinical Cancer Research* 2024;30(21):4844–4855, NCT03218683; PMID 39167622 / PMC11528199): **seven clinical-stage MCL1 inhibitors — ABBV-467, AMG 176, AMG 397, AZD5991, GS-9716, MIK665, PRT1419 — and "none advanced beyond Phase I/II" is accurate as of 2026-11-07** (no MCL1 inhibitor has reached Phase III or approval) [verified 2026-11-07]. BUT "cardiotoxicity the predominant dose-limiting factor" is **not universal across the class**: **PRT1419 remains in active development as of late 2025** and "demonstrated acceptable safety and tolerability in patients with advanced or metastatic solid tumors… notably without cardiac toxicity", and **GS-9716's failure mode is undocumented**. "Uniformly failed" overstates the current state. [corrected per verification 2026-11-07]
- Paper's AZD5991 figures, **CORRECTED framing**: the 54/65 figure is real but comes from a **post hoc retrospective analysis** of stored samples using a high-sensitivity troponin T assay — **not "83% of treated patients"**. Correct statement: "In a post hoc analysis of stored samples, high-sensitivity troponin T was elevated in **54/65 (83%)** patients after any AZD5991 dose, versus **14/31 (45%)** before any dose; prospectively reported troponin elevations were **8/78 (10.3%)**." And the response rate: **3/78 overall (3.9%) is arithmetically correct but a derived figure, not stated in the trial paper** — correct statement: "3/78 overall (3.9%), **all in MDS (3/5, 60%)**; no responses in AML (0/38), myeloma, or other histologies (0/35)." [corrected per verification 2026-11-07]
- The paper attributes the toxicity to MCL1's essential role in cardiomyocyte survival [verified 2026-11-07 — review PMC7731749, J Hematol Oncol 2020, confirmed; primary evidence Thomas et al. Genes Dev 2013, PMID 23788623]. Presenting systemic MCL1 inhibition as a failed paradigm is the paper's framing; the PRT1419 exception above qualifies it.
- **Cancer DAO relevance:** this is the cautionary core of any Cancer DAO BCL-2 programme. The failure mode (on-target cardiotoxicity, narrow therapeutic window, poor efficacy) is the problem a Cancer DAO agenda must design around — it is not a problem the ALS paper solves for cancer. The paper's proposed solution (neuron-targeted gain-of-function) is ALS-specific and does not transfer to oncology; the oncology transfer is the *question* (tissue-selective delivery, see §3 Item 3), not an answer.

### Strand C — The Akt/Bad biomarker was validated in oncology and is being ported to ALS
- The paper's Discovery 5 states Akt/Bad phosphorylation status **is a validated predictive biomarker in oncology**. **DOWNGRADED per verification 2026-11-07:** the cited source (Rice et al., PLOS ONE 2019, PMID 31150457) is **preclinical NSCLC cell-line work** identifying phosphorylated AKT (S473) as a marker for sensitivity to combined MCL-1 + BCL-2/xL inhibition; it states the data "support the design of a clinical trial" — it does **not** clinically validate any biomarker in patients, and it measures pAKT, not Bad phosphorylation. Correct framing: **"preclinical evidence supporting trial design"**. Also note the paper's refs [10] and [11] are the **same Rice 2019 paper** cited twice. [corrected per verification 2026-11-07]
- The paper's systematic literature review (Job ID 74038966-e7bc-47d0-a9fe-8773bd86d1de) states it found **no peer-reviewed studies proposing or validating Akt/Bad phosphorylation as a predictive biomarker in ALS or any other neurodegenerative disease**. The narrow claim was **not falsified** by independent verification searches (2026-11-07) [verified 2026-11-07 — narrow claim survived]. BUT: the paper's anchor ref [9] (JCI 170169) does **not** support the claim — it is an oncology paper with no literature search and nothing about neurodegeneration; do not cite it as the anchor. And prior art narrows the novelty: a granted patent (**WO2012160563 / CA2836503 / EP3263127B1**, filed 2012, granted 2019) claims pAkt as a biomarker for ALS progression prognosis and assessing responsiveness to treatment, and **Léger et al. 2006 / Dewil et al. 2007** showed pAkt dysregulation in ALS patients. "Completely novel / never proposed" is therefore overstated — disclose this prior art. The direction of travel is **oncology → ALS**, not the reverse. [corrected per verification 2026-11-07]
- **Cancer DAO relevance:** the Cancer DAO's side of this bridge is the *source* science. A Cancer DAO page can present the Akt/Bad stratification science — but only in the corrected framing: preclinical cell-line evidence (Rice 2019, pAKT S473), not a clinically validated biomarker, and only for combined MCL-1 and BCL-2/BCL-XL inhibition in oncology. Do not extend it to other drug classes, other biomarkers, or other cancers without a separate source. [corrected per verification 2026-11-07]

### What the paper does NOT give the Cancer DAO
- No cancer cell-line data, no tumour data, no oncology experiment, no cancer patient data.
- No claim that AGI-183 treats any cancer. (Note the identity tension: the paper's AGI-183 is a BCL-XL stabilizer proposed for neuroprotection; the separate `AGI_Compound_001.pdf` catalog entry also named AGI-183 describes a CRBN-binding FLIP inhibitor for cancer — same name, opposite mechanisms, unresolved. See `compound-agi183.md` §5. Do not merge them.)
- No DAO, no governance, no token, no funding, no partner, no timeline for any Cancer DAO work.
- The paper's model predictions (42-day MOMP 0.764 → 0.040 predicted; Bliss peak +0.0305 day 13.25 predicted; BH3 EC50 ~112.42 vs 65.29 → 15.84 predicted) are predictions about **motor neurons under chronic glutamate stress**. They say nothing about any cancer. Do not quote them on a cancer page except to note they are ALS-model predictions.

---

## 3. Exactly what to add — new content, item by item

These items are **new-page specifications** for when Mike approves a Cancer DAO page. They do not duplicate `brief-cancer.md` Items 1–6 (TCGA/GDC, cBioPortal, SEER, ClinicalTrials.gov, FDA approvals, open-datasets table) — a Cancer DAO page should link to that open-data content, not re-state it.

### Item 1 — NEW PAGE (when approved): "Cancer DAO — research agenda" (the BCL-2 pillar)
- **Status:** new content. No existing page to correct. The page must be labelled as new content, dated, and must open with the status line in the wording block below.
- **What to add:** a research-agenda page organised around the three strands in §2:
  1. **BCL-2 family therapeutics** — MCL1 and BCL-XL as cancer drug targets; the shared target map (MCL1/BAK, BCL-XL/BAX, BH3-only proteins, MOMP as readout). State that this target biology is the same biology the ALS paper builds on.
  2. **BH3 profiling as a stratification tool** — BH3 profiling as a functional assay measuring mitochondrial apoptotic priming, with established utility in oncology [verified 2026-11-07 — PMC3770266 (Cancer Lett 2013); PMC8316436 (Cell Death Dis 2021); Pan et al. Haematologica 2024]. The paper notes BH3 profiling has been extensively applied in oncology but remains underexplored in neurodegeneration — the Cancer DAO's contribution here is on the oncology side: BH3 profiling as a *stratification* tool for BCL-2 family therapy, paired with the Akt/Bad biomarker (Strand C).
  3. **Tissue-selective delivery** — the open question the MCL1 failure history poses: systemic MCL1 inhibition failed on cardiotoxicity, so what delivery strategies could achieve tissue selectivity? Frame this as an open research question, not a programme. No delivery technology, partner, or approach is named in the paper or in any verified source for the Cancer DAO.
- **Wording to use (status line, verbatim at the top of the page):** "Cancer DAO is a proposed research programme. Today it is a world on WorldForge (web-viewer only, Fred Hutchinson Cancer Center anchor, Seattle) and a focus domain — not a research programme, a trial, or a dataset. The agenda below is drawn from published science, including an ALS research proposal (als_4_8.pdf, 7 Nov 2026) whose BCL-2 biology is shared with oncology. That paper does not mention or launch any DAO."
- **Sources + as-of:** `~/workspace/user/files/als_4_8.pdf` (7 Nov 2026); `brief-cancer.md` for the open-data pillar; `inventory-bio.md` §§2, 5, 7 for the world/name inventory.

### Item 2 — NEW SECTION (when approved): "What oncology already learned: the MCL1 inhibitor failures"
- **Where:** on the new Cancer DAO agenda page (Item 1), or on the new cancer open-data page (`brief-cancer.md` Item 1) as a linked section — not both; pick one home and link from the other.
- **What to add:** the Strand B facts from §2, in the corrected framing: seven inhibitors named, none beyond Phase I/II as of 7 Nov 2026, with the PRT1419 exception disclosed; AZD5991 troponin 54/65 (83%) post-dose in a post hoc analysis vs 14/31 (45%) pre-dose, prospective AE rate 8/78 (10.3%); response 3/78 (3.9%) overall, all in MDS (3/5, 60%); on-target cardiotoxicity attributed to MCL1's role in cardiomyocyte survival.
- **Wording to use:** "Seven clinical-stage MCL1 inhibitors were developed for cancer. The ALS paper's review states none advanced beyond Phase I/II as of 7 Nov 2026, but the failure was not uniform: PRT1419 remains in active development and reported acceptable safety without cardiac toxicity in solid tumors. For AZD5991, high-sensitivity troponin T was elevated in 54/65 (83%) patients after any dose in a post hoc analysis of stored samples, versus 14/31 (45%) before any dose; prospectively reported troponin elevations were 8/78 (10.3%). Overall response was 3/78 (3.9%), all in MDS (3/5, 60%). [corrected per verification 2026-11-07] This failure history is the starting point for any tissue-selective BCL-2 programme — it is a record of what did not work, not a result the Cancer DAO produced."
- **Do NOT** present the failure list as Cancer DAO research. It is the paper's synthesis of oncology clinical history.

### Item 3 — NEW SECTION (when approved): "Stratification: Akt/Bad and BH3 profiling"
- **Where:** on the new Cancer DAO agenda page (Item 1).
- **What to add:** the Strand C facts from §2, plus the BH3-profiling framing: BH3 profiling measures mitochondrial priming by quantifying MOMP in response to BH3-domain peptides [verified 2026-11-07 — PMC3770266]. Present Akt/Bad phosphorylation status as a biomarker with **preclinical cell-line evidence** in oncology for combined MCL-1 and BCL-2/BCL-XL inhibition (Rice 2019, pAKT S473 — not clinically validated, not pBad), and BH3 profiling as the functional assay that could pair with it. [corrected per verification 2026-11-07]
- **Wording to use:** "In oncology, phosphorylated AKT (S473) was identified in preclinical NSCLC cell-line work as a marker for sensitivity to combined MCL-1 and BCL-2/BCL-XL inhibition (Rice 2019) — preclinical evidence supporting trial design, not a clinically validated biomarker. [corrected per verification 2026-11-07] BH3 profiling is the functional assay for mitochondrial priming that pairs with such a biomarker. The Cancer DAO agenda is to build on this stratification science — it has not yet done so."
- **Do NOT** claim Akt/Bad predicts response to any other drug class, or that BH3 profiling is a Cancer DAO capability. It is not — no assay, lab, or dataset exists for the Cancer DAO.

### Item 4 — CORRECT the Cancer DAO world label wherever it appears (do NOT upgrade it)
- **Where:** any page that names Cancer DAO — the WorldForge Earth page, the rp1-review manifests, the video hub (`videos/index.html`), and any future series index.
- **Verified fact:** Cancer Dao (Fred Hutchinson Cancer Center, Seattle; anchor 47.6263,-122.3292) is marked Live as a **web-viewer world only (not RP1-attached)**. A Cancer DAO promo short exists (bright-brand template, Batch 2/3; Foundation video set 24/25). Cancer DAO is one of 6 PBC focus-domain DAOs. The video-enhancement wave links the cancer short to the series index as fallback — **no dedicated series page** exists.
- **Wording to use:** "Cancer DAO is a world on WorldForge (web-viewer only) and a focus domain — not a research programme, a trial, or a dataset. For the open cancer data, see [new cancer page, once approved]; for the BCL-2 research agenda, see [Cancer DAO agenda page, once approved]."
- **Do NOT** present the world, the short, or the focus-domain listing as cancer research content; do NOT invent a Cancer DAO series number, programme, partner, or timeline; and do NOT describe the ALS paper as the DAO's founding or launch document.

### Item 5 — LINK, do not duplicate, the `brief-cancer.md` open-data pillar
- **Where:** the new Cancer DAO agenda page (Item 1).
- **What to do:** link out to the TCGA/GDC, cBioPortal, SEER, and ClinicalTrials.gov content specified in `brief-cancer.md` Items 1–4 + 6. Do not restate the TCGA scale figures, the GDC case counts, or the trials counts here — those live in `brief-cancer.md` with their own sources and caveats (including the ClinicalTrials.gov count rule: use one wording with its source, never mix).
- **Rationale:** the Cancer DAO agenda has two pillars — open data (`brief-cancer.md`) and BCL-2 therapeutics (this brief). One page per pillar, cross-linked, keeps each pillar's sources and caveats intact.

---

## 4. What NOT to claim

- Do NOT claim the paper launches, proposes, mentions, or describes the Cancer DAO or any DAO. **It does not — full-text search finds no "DAO" in the paper.**
- Do NOT claim the Cancer DAO exists as a research programme, trial, dataset, series, or formed entity. Today it is a world name + focus domain. It is proposed, not formed.
- Do NOT claim any cure, treatment, or diagnosis for any cancer. FDA approvals are regulatory facts about specific drugs for specific indications — not endorsements and not evidence about any other compound.
- Do NOT quote the paper's ALS-model predictions (42-day MOMP 0.764 → 0.040; Bliss +0.0305 day 13.25; BH3 EC50 ~112.42) as cancer results. They are predictions about motor neurons under chronic glutamate stress.
- Do NOT present the MCL1 failure list or the AZD5991 figures as Cancer DAO research, and do NOT use the paper's original framing — never "troponin elevation in 83% of treated patients" and never 3.9% without the MDS subgroup (3/5, 60%). The corrected framing is in §2 Strand B. [corrected per verification 2026-11-07]
- Do NOT call Akt/Bad a "validated predictive biomarker" in oncology — the evidence is preclinical NSCLC cell-line work (Rice 2019, pAKT S473), not clinical validation. Do NOT cite JCI 170169 as support for any "no studies" claim, and do NOT write "completely novel / never proposed" without disclosing the 2012 pAkt-ALS patent (WO2012160563 / EP3263127B1) and the Léger 2006 / Dewil 2007 papers.
- Do NOT present the Cancer DAO world, promo short, or focus-domain listing as cancer research content, and do NOT invent a Cancer DAO series number, programme, partner, or timeline.
- Do NOT aggregate the FDA approvals into a yearly total — no verified total for 2025 or 2026 was established (`brief-cancer.md` §3).
- Do NOT describe TCGA as wholly open download — individual-level data is controlled via dbGaP. Do NOT link the original TCGA Data Portal as live (closed 2026, succeeded by the GDC).
- Do NOT present the new cancer content as a correction of existing research — there was none. Label it as new content, dated 7 Nov 2026 (research) with its own publication date when it goes live.
- Do NOT imply the ALS compound library treats cancer — `als-01` cites natural-product cancer drugs only as an example class of compound libraries (see `brief-als.md`).
- Do NOT import the `AGI_Compound_001.pdf` AGI-183 entry (CRBN-binding FLIP inhibitor) into Cancer DAO content as if it were the paper's AGI-183 (BCL-XL stabilizer). Same name, different mechanism, unresolved — see `compound-agi183.md` §5.

---

## 5. Figure-alignment notes for this area

| Figure | Resolution |
|---|---|
| AZD5991 troponin 54/65 (83%) vs response 3/78 (3.9%) | **Corrected per verification 2026-11-07.** Troponin: post hoc retrospective analysis of stored samples — 54/65 (83%) post-dose vs 14/31 (45%) pre-dose; prospective AE rate 8/78 (10.3%). Never "83% of treated patients". Response: 3/78 (3.9%) is derived, not trial-stated; all responders MDS (3/5, 60%), 0/38 AML, 0/35 others. Source: Desai et al. Clin Cancer Res 2024, PMID 39167622 / PMC11528199. |
| Seven MCL1 inhibitors, none beyond Phase I/II | **Corrected per verification 2026-11-07.** List real (ABBV-467, AMG 176, AMG 397, AZD5991, GS-9716, MIK665, PRT1419); "none beyond Phase I/II" accurate as of 2026-11-07. But "uniformly failed / cardiotoxicity predominant" is not universal: PRT1419 remains in active development with acceptable safety without cardiac toxicity in solid tumors; GS-9716's failure mode undocumented. |
| "Validated biomarker" (oncology) | **Corrected per verification 2026-11-07.** Rice 2019 (PMID 31150457) is preclinical NSCLC cell-line work on pAKT (S473) — downgrade to "preclinical evidence supporting trial design". Not clinically validated; not pBad. |
| "No studies in neurodegeneration" | **Corrected per verification 2026-11-07.** Narrow claim not falsified, but "completely novel / never proposed" overstated: 2012 patent WO2012160563 / CA2836503 / EP3263127B1 proposed pAkt as an ALS biomarker; Léger 2006 / Dewil 2007 showed pAkt dysregulation in ALS patients. JCI 170169 does NOT support the claim. |
| Refs [10]=[11], refs [6]=[7] | **Duplicates, verified 2026-11-07.** [10] and [11] are both Rice 2019; [6] and [7] are both Pan et al. Haematologica. Deduplicate. |
| "DAO" in als_4_8.pdf | **Zero mentions.** Full-text search finds no "DAO". The paper is not a DAO document. |
| Cancer DAO status | World (web-viewer only) + focus domain. Proposed entity, not formed, not a programme/trial/dataset/series. |
| TCGA ~2.5 PB / 11,000+ patients / 33 types vs GDC 44,637 cases | Different scopes — see `brief-cancer.md` §4. Do not merge; link, do not restate. |
| ClinicalTrials.gov counts | Use one wording with its source; do not mix — see `brief-cancer.md` §4. |

---

## 6. Open questions needing Mike's decision

1. **Should a Cancer DAO page exist at all, and in what form?** Options: (a) a single agenda page combining the open-data pillar (`brief-cancer.md`) and the BCL-2 pillar (this brief); (b) separate open-data and agenda pages, cross-linked (recommended — keeps each pillar's sources intact); (c) the Cancer DAO stays a world/focus-domain page only, linking out to the open-data page. Mike needs to choose before any page is built (see also `brief-cancer.md` §5 item 1).
2. **Cancer DAO scope:** is Cancer DAO meant to become a research programme/series, or stay a world + focus domain? It has no W3 series number and no dedicated series page today. If it is to become a series, that is a corporate decision (counsel, filings) — not a content decision.
3. **Tissue-selective delivery:** the MCL1 failure history poses the question, but no delivery approach is named anywhere. Should a follow-up pass research tissue-selective delivery strategies (e.g. antibody-drug conjugates, targeted nanoparticles, gene therapy vectors) as a separate, sourced research item — or leave Item 1 §3 as an open question only? (Recommendation: open question only until researched.)
4. **Akt/Bad verification — COMPLETE (2026-11-07):** the oncology evidence was downgraded to preclinical cell-line work (Rice 2019, pAKT S473), not clinical validation, and the "no studies" novelty claim was narrowed with prior art disclosed (2012 patent, Léger 2006, Dewil 2007). The Cancer DAO agenda page should use the corrected framing in §2 Strand C and §3 Item 3 — it does not need to wait for any further verification, but it must not revert to the paper's original "validated biomarker" / "completely novel" wording.
5. **AGI-183 identity tension:** the paper's AGI-183 (BCL-XL stabilizer) vs the catalog's AGI-183 (CRBN-binding FLIP inhibitor) — same name, opposite mechanisms. Until resolved, no Cancer DAO page may present AGI-183 as a cancer compound. See `compound-agi183.md` §5.

---

## Sources

- `~/workspace/user/files/als_4_8.pdf` — "Synergistic Neuroprotection in ALS: Akt/Bad Phosphorylation as a Predictive Biomarker for BCL-2 Family Therapy", x@agicorp.network and Bios (bios@bio.xyz), created 2026-04-08. All paper-grounded facts in §§2–3 are from this paper; external-citation claims are marked [verified 2026-11-07] or [corrected per verification 2026-11-07]. The paper contains no "DAO" mention (full-text search, 7 Nov 2026).
- `~/workspace/your_files/bio-research-expansion/brief-cancer.md` — the companion cancer brief (open cancer data: TCGA/GDC, cBioPortal, SEER, ClinicalTrials.gov, FDA approvals). This brief adds the BCL-2 agenda pillar only.
- `~/workspace/your_files/bio-research-expansion/brief-als-agi183.md` — the companion ALS brief (the paper's combination, design, and five predicted discoveries in full).
- `~/workspace/your_files/bio-research-expansion/inventory-bio.md` — where cancer content lives today (§§2, 5, 7, 9, 11.1): world/name only, zero research content.
- `~/workspace/your_files/bio-research-expansion/compound-agi183.md` — the AGI-183 compound entry (same directory), including the catalog identity tension.
- `~/workspace/your_files/bio-research-expansion/verification-als-4-8-citations.md` — citation verification, completed 2026-11-07 (Desai et al. PMID 39167622 / PMC11528199; PMC7731749; Datta 1997 PMID 9346240; Rice 2019 PMID 31150457; JCI 170169; patent WO2012160563 / EP3263127B1; Léger 2006; Dewil 2007; PMC2681190; PMC3221787; PMC3070914; PMC9257998; PMC3770266; PMC8316436; Pan et al. Haematologica; Reactome R-HSA-198347). All 7 required corrections from that file are applied in this brief.

---

## 7. MENA metastasis biomarker programme — new pillar (added 2026-11-07)

**Published:** research brief in this repo's `research/` folder.
**Research date: 7 November 2026. Evidence: `~/workspace/user/files/frank_gerter.pdf` — US Patent Application Publication US 2022/0251662 A1, "Metastasis Specific Splice Variants of Mena and Uses Thereof in Diagnosis, Prognosis and Treatment of Tumors", Condeelis et al., applicants Albert Einstein College of Medicine / MIT / IFO-Regina Elena Cancer Institute, published 11 August 2022, inventor Frank Gertler (among four inventors). PDF 2,257,070 B, 25 pages (12 drawing sheets + specification + sequence listing).**
**Applies to:** any future Cancer DAO page, article, or series content on the Mena metastasis biomarker. This is the **third** Cancer DAO content pillar, alongside the open-data pillar (`brief-cancer.md`) and the BCL-2 pillar (§§2–6 above). It does NOT duplicate either: no BCL-2 content and no open-data figures are restated here. A later worker should be able to apply this section without re-reading the application: every item below gives the exact application-grounded fact and its location in the application, plus the peer-reviewed verification for each key claim.

### Honesty lines for this section (read first — they govern every item)

- **THE APPLICATION IS NOT A GRANTED PATENT, AND THE 2022 APPLICATION ITSELF IS ABANDONED.** US 2022/0251662 A1 is an **application publication** (application 17/477,327, filed 16 September 2021, published 11 August 2022). Google Patents lists its legal status as **Abandoned** [verified 2026-11-07]. The **family** does include two granted US patents — **US 9,719,142 B2 (granted 1 August 2017, active, adjusted expiration 2028-07-27)** and **US 8,603,738 B2 (granted 10 December 2013, active, adjusted expiration 2030-01-28)** — both with the same title and inventors [verified 2026-11-07, Google Patents]. The granted patents carry the claims; the 2022 publication does not. **Never write "patent US 2022/0251662" or "the patent shows" for the 2022 publication. Correct wording: "the application reports…", "the granted family patents claim…".** Do not state the scope of the granted claims from this brief — the claims of US 9,719,142 and US 8,603,738 were not read in full for this brief (only their existence, dates, and status were verified); a worker who needs claim scope must read the granted patents.
- **PATENT-REPORTED, NEVER CLINICAL EVIDENCE.** Everything in §7.3 is what the **application reports** from its own experiments (rat MTLn3 allograft, mouse PyMT transgenic model, human breast cancer cell lines, 18-mouse FNA study, 4-patient human FNA set). The application is not peer-reviewed and is not clinical evidence. Where peer-reviewed literature independently supports a claim, §7.4 says so with citations; where it does not, §7.4 says so.
- **No treatment, cure, diagnosis, or medical-device claims anywhere.** Nothing here claims any Mena test diagnoses, predicts, or treats any cancer in patients, and nothing here is a diagnostic product. MenaCalc and TMEM scoring are **research assays** used in retrospective cohorts — neither is an FDA-cleared or approved test, and no Mena-based test has any regulatory clearance established in this brief. The therapeutic direction (§7.5 Item 3) is a **research direction only**: no Mena-targeted drug exists, and no clinical trial of one was found.
- **The Cancer DAO itself remains a proposed entity.** Today it is only a world name with a Fred Hutchinson anchor (see §1). It is not a research programme, a trial, a dataset, a series, or a formed entity. Nothing in this section forms it, and the Mena programme has no lab, no assay, no dataset, no partner, and no timeline.
- **Cancer DAO has no W3 series number.** It is a world / focus domain, not a series. Do not invent one. "33 named W3 sub-series in the April 2026 internal list" — never 35. W3 series are proposed, not formed; filed fact (Foundation B20260196664, Fellowship B20260229217) stays apart from proposed plans.

### 7.1 What exists today — the application and its family (verified 2026-11-07)

- **The application:** US 2022/0251662 A1, "Metastasis Specific Splice Variants of Mena and Uses Thereof in Diagnosis, Prognosis and Treatment of Tumors". Application No. 17/477,327, filed 16 September 2021, published 11 August 2022. Inventors: John S. Condeelis, Sumanta Goswami, Frank Gertler, Paola Nistico. Applicants/assignees: Albert Einstein College of Medicine (Bronx, NY), Massachusetts Institute of Technology (Cambridge, MA), IFO-Regina Elena Cancer Institute (Rome, IT). Classifications: C12Q 1/6886, G01N 33/574, A61K 31/713. Government support: NCI grant CA100324 (application ¶0002). **Legal status: Abandoned** (Google Patents, checked 2026-11-07). The application states its own chain on its front page: continuation of 17/248,146 (filed 11 January 2021, abandoned) → continuation of 15/661,021 (filed 27 July 2017, abandoned) → division of 14/074,089 (filed 7 November 2013, now US 9,719,142) → division of 12/462,324 (filed 31 July 2009, now US 8,603,738) → continuation-in-part of PCT/US2008/001343 (filed 31 January 2008) → provisional 60/899,303 (filed 2 February 2007).
- **Granted family members [verified 2026-11-07, Google Patents]:**
  - **US 9,719,142 B2** — granted 1 August 2017, application 14/074,089 filed 7 November 2013, status **Active, adjusted expiration 2028-07-27**. Same title and inventors.
  - **US 8,603,738 B2** — granted 10 December 2013, application 12/462,324 filed 31 July 2009, status **Active, adjusted expiration 2030-01-28**. Same title and inventors.
  - PCT application WO2008097466 (PCT/US2008/001343, published 14 August 2008) — status **Ceased** (Google Patents).
- **What the family claim means in practice:** the Mena-isoform invention has granted US patent protection through the two B2 patents (expiring 2028 and 2030 on Google Patents' adjusted dates), but the 2022 continuation that Mike's file contains did **not** itself grant — it was abandoned. Any page that mentions the 2022 publication must say so. The granted patents' claim scope was **not** verified in this pass; do not quote their claims.
- **The application contains no claims section in the uploaded PDF** (25 pages: 12 drawing sheets, specification ¶¶0001–0085, 25-sequence listing). The methods are described in the Summary of the Invention (¶¶0008–0016) and Detailed Description (¶¶0038–0050); that is the source for §7.3.

### 7.2 Nomenclature map — patent names vs literature names

The application uses `+`, `++`, `+++`, and `11a` for the four alternatively included Mena (gene *ENAH*) exons. The peer-reviewed literature renamed two of them; the map below is what a Cancer DAO page must use so readers can follow the citations.

| Application name | What it is (application Figs. 4A–4B, ¶¶0021, 0060) | Literature name | Literature status |
|---|---|---|---|
| Mena `+++` | 19-amino-acid exon (SEQ ID NO: 4, AQSKVTATQDSTNLRCIFC), just after the EVH1 domain | **MenaINV** (formerly Mena+++) | The invasion isoform. Functional work is on this isoform — see §7.4. |
| Mena `++` | 4-amino-acid exon (SEQ ID NO: 2, FYLG), just after the EVH1 domain | **Mena++** (no separate literature name) | Co-upregulated with +++ in invasive cells (Goswami 2009), but no peer-reviewed paper found that isolates a distinct Mena++ protein function — see §7.4, claim 2. |
| Mena `11a` | 21-amino-acid exon inside the EVH2 domain (SEQ ID NO: 24/25) | **Mena11a** | The epithelial / non-invasive isoform; downregulated in invasive cells. |
| Mena `+` | Constitutively detected exon; similar levels in invasive cells and average primary tumour cells | — | Control/background isoform in the application (¶0058). No programme relevance. |

- **Mena** itself: an actin-regulatory protein of the Ena/VASP family, controlling cell movement, motility, and shape by anti-capping actin filament barbed ends (application ¶0006, citing Barzik 2005, Gertler 1996). Pan-Mena is upregulated in invasive rodent mammary cells and overexpressed in human breast cancer tissue (application ¶0006, citing Wang 2004, Di Modugno 2004).
- **MenaCalc:** a literature term, **not** an application term. It is a multiplex quantitative immunofluorescence (MQIF) score = normalised pan-Mena minus Mena11a, i.e. the fraction of Mena lacking the 11a exon, used to infer the presence of invasive tumour cells (Agarwal et al. 2012; defined in the *Scientific Reports* 2016 paper, §7.4). Do not attribute MenaCalc to the application.
- **TMEM (tumour microenvironment of metastasis):** also a literature term, **not** an application term. A three-cell microanatomical structure — a Mena-overexpressing tumour cell, a TIE2-high macrophage, and an endothelial cell in direct contact — that forms an intravasation doorway (Robinson et al. 2009; Karagiannis et al. 2017). Do not attribute TMEM to the application.

### 7.3 What the application reports (patent-reported only)

All facts below are **as reported in US 2022/0251662 A1**; paragraph numbers are the application's own. None of this is peer-reviewed or clinical evidence.

**The core pattern — isoform switching in invasive cells (¶¶0057–0059, Figs. 1–2):**
- In two mammary tumour models — the MTLn3 rat adenocarcinoma allograft and the MMTV-PyMT mouse transgenic model — invasive tumour cells collected by an *in vivo* invasion (microneedle chemotaxis) assay showed **upregulation of the Mena `++` and `+++` exons and downregulation of the `11a` exon** relative to average primary tumour cells (APTCs). Pan-Mena was upregulated **3–4 fold** in invasive cells (¶0057, citing Wang 2004). The `++` exon was upregulated **2–3 fold**; the `11a` message was **undetectable in PyMT invasive cells, indicating at least an eight-fold downregulation** (¶0058 and Goswami 2009, which reports the same figures).
- The `++` and `+++` exons are on **separate transcripts** (RACE cloning, ≥10 clones each, 100% match to published mouse sequences; ¶0060, Fig. 4).
- The pattern **persists after dissemination**: `++` and `+++` remained upregulated in tumour cells that had intravasated into blood (circulating tumour cells) and in lung metastases; `11a` was not detected in lung metastases (¶0059, Fig. 2). The application interprets this as a **stable** change, not a transient induction — and reports controls (Figs. 6–7) showing the pattern is induced by the tumour microenvironment, not by the collection procedure (¶¶0053, 0057).
- The `+++` variant is expressed in human breast cancer cell lines MDA-MB-231 and T47D (¶0020, Fig. 3).

**Fine-needle aspiration (FNA) — mouse (¶0063, Fig. 10):**
- 18 PyMT mice, 10–26 weeks old: 9 with 2–3 mm adenoma/MIN tumours without invasion, 9 with 1–2 cm invasive carcinomas with histologically confirmed lung metastasis. **Mena `+++` expression was 7.5-fold higher** in invasive metastatic carcinomas than in adenomas/MINs; **Mena11a fell to 30%** of the early-tumour level.

**FNA — human (¶0064, Table 3, Fig. 11):**
- 4 invasive ductal carcinomas (IDC) and 1 fibroadenoma (FA). **Mena `+++` was increased 3- to 37-fold** in 3 of the 4 IDC patients vs the fibroadenoma (fold changes 3.39, 34.84, 10.99; one IDC, patient 5609, showed 0.3). **Mena11a was exceedingly low or not detectable in all 4 IDC patients.** In patient 5609, where `+++` itself was decreased, the **Mena `+++`/11a ratio was 7.5 vs 1 in the control** — the application's basis for a ratiometric marker. **n = 4 IDC + 1 control. This is application data only; it was not found in any peer-reviewed publication (see §7.4, claim 6).**

**The methods the application describes (¶¶0008–0016, 0038–0050):**
- **Determining whether a subject has a metastatic tumour:** assay a blood, tissue, and/or tumour sample for `++` and/or `+++` expression; overexpression indicates a metastatic tumour (¶0008). A second version uses `++`/`+++` overexpression **plus** `11a` decrease together (¶0009).
- **Assessing therapy efficacy:** in a subject undergoing treatment, continued overexpression of `++`/`+++` (with or without `11a` decrease) indicates a need to continue therapy (¶¶0010–0011).
- **Assessing prognosis:** prognosis improves with a decrease in `++`/`+++` expression, and with an increase in `11a` (¶¶0012–0013).
- **Inhibiting metastasis:** reducing the presence/activity of the `++` (SEQ ID NO: 2) and/or `+++` (SEQ ID NO: 4) isoform and/or increasing Mena11a (SEQ ID NO: 24), by antisense, ribozyme, RNA interference, antibody, or aptamer, at DNA, RNA, and/or protein level (¶¶0014, 0046–0047). A migration experiment is reported: expressing Mena `+++` enhanced tumour-cell migration (Fig. 8), and redirecting Mena to the wrong place in the cell ("mito", a mislocalisation construct) inhibited migration of metastatic cells (¶0062, Fig. 9).
- **Screening for candidate compounds:** contact a compound with a cell line/tissue culture expressing `++`/`+++` and/or 11a; reduction in `++`/`+++` (or increase in 11a) marks a candidate metastasis inhibitor (¶¶0015, 0048).
- **Kits:** antibody, peptide, or aptamer specifically binding `++`, `+++`, or 11a; and/or nucleic-acid probes or PCR primers specifically hybridising to the encoding nucleic acids (SEQ ID NOs: 1, 3, 25); kits may cover two or all three isoforms (¶0050). The application notes such tests could be run in conventional pathology labs (¶0050).
- **Scope claim (¶¶0065–0066):** the application proposes the `++`/`+++` vs 11a ratio as a ratiometric prognostic marker, and asserts the invasion signature — and therefore Mena `+++`/`++` as diagnostic/therapeutic targets — will apply to **all common adenocarcinomas** (breast, prostate, pancreas, colon, brain, liver, lung, head and neck). **That generalisation is the application's assertion, not a demonstrated result — see §7.4, claim 7.**
- **Historical context only:** the application's background cites 2006 US breast-cancer figures (212,920 new invasive cases, 61,980 in situ, 40,970 deaths; American Cancer Society, Breast Cancer Facts and Figures 2006 — application ¶0004). These are **2006 figures, not current**; do not quote them as today's numbers.

### 7.4 Literature verification — per key claim [verified 2026-11-07]

Each claim from the application was checked against the peer-reviewed literature. Status is **SUPPORTED** (peer-reviewed evidence found), **PARTLY SUPPORTED**, or **NOT FOUND** (no peer-reviewed support found in this pass — not proof it does not exist).

| # | Application claim | Literature verdict | Evidence |
|---|---|---|---|
| 1 | Mena `++` and `+++` upregulated, `11a` downregulated, specifically in invasive mammary tumour cells | **SUPPORTED** | Goswami et al., *Clin Exp Metastasis* 2009, 26(2):153–159 (PMID 18985426; PMC3042857) — the peer-reviewed publication of the application's own data, same authors (Goswami, Philippar, Sun, Patsialou, Avraham, Wang, Di Modugno, Nistico, Gertler, Condeelis). Abstract: "two isoforms of Mena, ++ and +++, are upregulated in the invasive tumor cells and one isoform, 11a, is downregulated… may provide a new biomarker for the presence of metastatic cancer cells and for prognosis." Same fold figures (`++` 2–3 fold; `11a` ≥8-fold down). [verified 2026-11-07] |
| 2 | `+++` (MenaINV) is the functionally pro-metastatic isoform | **SUPPORTED** | Philippar et al., *Dev Cell* 2008, 15(6):813–828 — "A Mena invasion isoform potentiates EGF-induced carcinoma cell invasion and metastasis." MenaINV sensitises carcinoma cells to EGF (a conference summary of the Condeelis programme reports ~50-fold sensitisation of EGFR to EGF — secondary source, treat as approximate). Roussos et al., *J Cell Sci* 2011, 124:2120–2131 (PMID 21670198) — MenaINV promotes multicellular streaming motility and transendothelial migration in a mouse breast-cancer model, dependent on a macrophage–tumour-cell paracrine loop. Roussos et al., *Clin Exp Metastasis* 2011, 28:515–527 — MenaINV and Mena11a play distinct roles in breast-cancer cell cohesion and association with TMEM. [verified 2026-11-07] |
| 3 | Mena11a is anti-invasive / invasion-suppressing | **SUPPORTED** | Roussos et al. 2011 (*J Cell Sci*, above): increased Mena11a correlates with decreased CSF-1 expression and a dramatically decreased ability to participate in paracrine-mediated invasion and intravasation. Forse et al. and the *Sci Rep* 2016 paper (below) report Mena11a decreases EGF-elicited 3D invasion *in vitro* and *in vivo*, and Mena11a-expressing tumours do not metastasise efficiently. [verified 2026-11-07] |
| 4 | The isoform pattern has prognostic value in human breast cancer (pan-Mena minus Mena11a) | **SUPPORTED, with a caveat** | Agarwal et al., "Quantitative assessment of invasive Mena isoforms (MenaCalc) as an independent prognostic marker in breast cancer", published September 2012 — MQIF MenaCalc (pan-Mena minus Mena11a) in two independent primary breast-cancer cohorts (n=501 and n=296): high MenaCalc associated with poor disease-specific survival (log-rank P=0.0004 and P=0.0321); multivariate analysis showed it independent of age, node status, receptor status, and tumour size. Neither total Mena nor Mena11a alone was significantly associated with outcome. A third axillary node-negative cohort (n=403) gave HR 2.18 (95% CI 1.19–4.00, P=0.0199) for death from any cause. **Caveat:** the *Scientific Reports* 2016 paper ("The alternatively-included 11a sequence modifies the effects of Mena…", *Sci Rep* 6:35298) reports it could **not** find a stable MenaCalc–survival correlation in the TCGA breast-cancer cohort (BRCA), likely due to short follow-up (patients with >10 years follow-up: n=55 alive, n=73 deceased, P=0.05 at the ¼ cutoff), and no significant correlation with metastasis formation in that cohort. Report both. [verified 2026-11-07] |
| 5 | Mena isoforms mark the TMEM intravasation doorway, a prognostic structure | **SUPPORTED** | Robinson et al., *Clin Cancer Res* 2009 — TMEM in human breast carcinoma, a potential prognostic marker linked to haematogenous dissemination. Rohan et al., *J Natl Cancer Inst* 2014 (doi:10.1093/jnci/dju136) — in 481 patients, TMEM density highly correlated with risk of metastasis in ER-positive/HER2-negative early-stage breast cancer. Karagiannis et al., *Sci Transl Med* 2017, 9:eaan0026 (PMID 28679654) — TMEM sites are "clinically validated as prognostic markers of metastasis in breast cancer patients" (the paper's wording = validation in retrospective patient cohorts, **not** a regulatory clearance); in 20 patients before/after neoadjuvant chemotherapy, TMEM score and MenaINV expression both increased, and the pro-metastatic effect was reversed in models by the TIE2 inhibitor rebastinib or by MENA knockdown. [verified 2026-11-07] |
| 6 | Human FNA data (4 IDC + 1 fibroadenoma; `+++` 3–37 fold; ratio 7.5 in patient 5609) support a diagnostic/prognostic test | **NOT FOUND** | No peer-reviewed publication of this 4-patient FNA dataset was found in this pass. The numbers exist only in the application (¶0064, Table 3, Fig. 11). n=4 is a case series, not a validation cohort. Do not present it as clinical evidence. [verified 2026-11-07 — search found no matching publication] |
| 7 | Mena `++`/`+++` as diagnostic/therapeutic targets for **all common adenocarcinomas** (breast, prostate, pancreas, colon, brain, liver, lung, head and neck) | **NOT FOUND as an isoform-specific claim** | Pan-Mena upregulation is reported beyond breast — e.g. pancreas, lung, colon, cervix (Forse et al., *Clin Exp Metastasis* 2015, 33(3):249–261, introduction; Roussos et al. 2011) — but the **isoform-specific** (`+++` up / `11a` down) evidence is breast-cancer evidence. No peer-reviewed paper found extending the MenaINV/Mena11a isoform pattern, let alone a test or therapy, to prostate, brain, liver, or head-and-neck cancer. The application's ¶0066 generalisation is an extrapolation. [verified 2026-11-07] |
| 8 | A **blood** assay for metastatic disease via Mena isoforms in circulating tumour cells | **NOT FOUND** | The application reports `++`/`+++` elevation in blood-borne tumour cells in the rat model (¶¶0059, 0061, Figs. 2, 6–7) and asserts a blood assay is therefore possible. No peer-reviewed validation of a Mena-isoform blood test (CTC assay or cell-free assay) in patients was found in this pass. The 2016 *J Cell Sci* review cites CTC gene-expression work generally (De Mattos-Arruda et al. 2013) but not a Mena-isoform blood test. Do not present a blood test as existing. [verified 2026-11-07 — search found no matching publication] |
| 9 | Therapeutic inhibition of MenaINV (antisense / RNAi / antibody / aptamer) inhibits metastasis | **PARTLY SUPPORTED — mechanism only, no therapeutic agent** | Mechanism: Mena deficiency delays tumour progression and reduces invasion, intravasation, and metastatic spread in the MMTV-PyMT model (reported in the *Sci Rep* 2016 paper, citing the Condeelis programme's Mena-deficiency work); MENA knockdown reversed chemotherapy-induced dissemination in Karagiannis 2017; the application's own Fig. 9 shows mislocalised Mena blocks migration. **No Mena-targeted drug, antisense, RNAi, antibody, or aptamer therapy exists, and no clinical trial was found.** The application's ¶¶0014/0046–0047 methods are proposals, not results. [verified 2026-11-07] |
| 10 | An isoform-specific MenaINV antibody exists as a research tool | **SUPPORTED** | Forse et al., *Clin Exp Metastasis* 2015, 33(3):249–261 — "Characterization of the expression of the pro-metastatic MenaINV isoform during breast tumor progression." A MenaINV isoform-specific monoclonal antibody was developed and validated in three assays; MenaINV protein expression increases during tumorigenesis and progression and correlates with blood-vessel density. Research tool, not a diagnostic product. [verified 2026-11-07] |

**Net assessment:** the application's **core biology is well supported** by the peer-reviewed literature — the isoform switch (Goswami 2009), the pro-metastatic function of MenaINV (Philippar 2008; Roussos 2011), the anti-invasive role of Mena11a (Roussos 2011; *Sci Rep* 2016), and the prognostic signal of the MenaCalc score in retrospective breast-cancer cohorts (Agarwal 2012; Rohan 2014 for TMEM) are all published, mostly by the same Condeelis/Gertler programme. What is **not** supported is everything that would make this a product: the 4-patient human FNA data, a blood test, the all-adenocarcinoma generalisation, and any therapy. The Mena programme is therefore a **biomarker research programme with real published biology and no clinical product** — which is exactly how a Cancer DAO page must frame it.

### 7.5 Exactly what to add — new content, item by item

These items are **new-page specifications** for when Mike approves a Cancer DAO page. They do not duplicate `brief-cancer.md` Items 1–6 (open cancer data) or §§2–3 above (BCL-2 pillar) — a Cancer DAO page should link to those, not re-state them.

#### Item 1 — NEW PAGE (when approved): "Cancer DAO — MENA metastasis biomarker programme"
- **Status:** new content. No existing page to correct. The page must be labelled as new content, dated, and must open with the status line in the wording block below.
- **What to add:** a research-programme page organised as:
  1. **The biology in one paragraph** — Mena (*ENAH*), an Ena/VASP actin-regulatory protein; alternative splicing produces a pro-invasive isoform (MenaINV, the 19-aa `+++` exon) and an epithelial isoform (Mena11a, the 21-aa exon). Invasive tumour cells switch from Mena11a-high to MenaINV-high. State the nomenclature map (§7.2) so readers can follow the citations.
  2. **What exists today** — the application (US 2022/0251662 A1, published 11 August 2022, application now **abandoned**) and the granted family (US 9,719,142, granted 2017; US 8,603,738, granted 2013), plus the peer-reviewed literature in §7.4. State the family status exactly as in §7.1.
  3. **The prognostic evidence** — MenaCalc (Agarwal 2012: two cohorts, n=501 and n=296, P=0.0004 and P=0.0321) and TMEM (Robinson 2009; Rohan 2014, n=481 ER+/HER2− early-stage breast cancer), **with the TCGA caveat** (no stable correlation in TCGA BRCA, *Sci Rep* 2016) and the explicit statement that these are retrospective-cohort research findings, not a cleared test.
  4. **The research agenda** — §7.6, as open validation steps, not as a programme that exists.
- **Wording to use (status line, verbatim at the top of the page):** "Cancer DAO is a proposed research programme. Today it is a world on WorldForge (web-viewer only, Fred Hutchinson Cancer Center anchor, Seattle) and a focus domain — not a research programme, a trial, or a dataset. The MENA programme below is a research agenda drawn from a patent application (US 2022/0251662 A1, published 11 August 2022; the application is abandoned — the granted family patents are US 9,719,142 and US 8,603,738) and from peer-reviewed papers by the Condeelis/Gertler programme. Nothing here is a diagnostic test, a treatment, or a product."
- **Sources + as-of:** `~/workspace/user/files/frank_gerter.pdf` (7 Nov 2026); Google Patents family-status check (7 Nov 2026); Goswami 2009 (PMID 18985426); Philippar 2008; Roussos 2011 (PMID 21670198); Agarwal 2012; Rohan 2014; Karagiannis 2017 (PMID 28679654); Forse 2015; *Sci Rep* 2016 (6:35298).

#### Item 2 — NEW SECTION (when approved): "What the literature supports — and what it does not"
- **Where:** on the new MENA programme page (Item 1).
- **What to add:** the §7.4 table, condensed to prose: the isoform switch, MenaINV function, Mena11a suppression, and MenaCalc/TMEM prognostic signal are peer-reviewed; the 4-patient FNA data, the blood test, the all-adenocarcinoma claim, and any therapy are not. Include the TCGA non-replication caveat.
- **Wording to use:** "The core biology is published: invasive breast-cancer cells switch from Mena11a to MenaINV (Goswami 2009), MenaINV drives invasion and metastasis in mouse models (Philippar 2008; Roussos 2011), and a pan-Mena-minus-Mena11a score (MenaCalc) was associated with poor survival in two retrospective breast-cancer cohorts of 501 and 296 patients (Agarwal 2012) — though the same score did not replicate in the TCGA breast-cancer cohort. What is not published: the application's 4-patient human FNA data, any Mena blood test, any extension of the isoform pattern beyond breast cancer, and any Mena-targeted therapy. This programme is biomarker research, not a diagnostic product."
- **Do NOT** present the application's figures as clinical evidence, and do NOT drop the TCGA caveat.

#### Item 3 — NEW SECTION (when approved): "Therapeutic targeting — a research direction, not a drug"
- **Where:** on the new MENA programme page (Item 1).
- **What to add:** the application's proposed inhibition methods (antisense, RNAi, antibody, aptamer; ¶¶0014, 0046–0047) framed strictly as proposals; the mechanistic support (Mena deficiency reduces metastasis in PyMT mice; MENA knockdown reverses chemotherapy-induced dissemination, Karagiannis 2017); the MenaINV isoform-specific antibody as a research tool (Forse 2015); and the explicit statement that **no Mena-targeted therapeutic exists and no clinical trial was found**.
- **Wording to use:** "The application proposes inhibiting metastasis by reducing MenaINV and/or increasing Mena11a (antisense, RNAi, antibody, or aptamer). The mechanism has support in mouse models — Mena deficiency reduces invasion and metastasis, and MENA knockdown reverses chemotherapy-induced dissemination — but no Mena-targeted drug exists and no clinical trial has been found. Therapeutic targeting is a research direction for this programme, not a treatment claim."
- **Do NOT** name any compound as a Mena therapy, and do NOT imply the "mito" mislocalisation construct in the application's Fig. 9 is a drug candidate — it is an experimental tool.

### 7.6 Research agenda — validation steps (what the programme would do, in order)

These are **proposed steps for a programme that does not exist yet**. Each step names what would have to be true for it to matter, in the order it would have to happen. No step is funded, staffed, partnered, or scheduled.

1. **Reproduce the isoform switch in independent data.** Re-analyse public RNA-seq (TCGA, METABRIC, and the open-data pillar in `brief-cancer.md`) for *ENAH* exon-level usage: is the MenaINV-high / Mena11a-low pattern detectable in bulk tumour RNA-seq, and does it track with metastatic outcome? Falsification test: if exon-level signal is undetectable in bulk data or does not track outcome, the programme's first premise fails at the data level. (Note the existing TCGA caveat: MenaCalc did not stably correlate with survival in TCGA BRCA — the programme must explain or work around this before building on it.)
2. **Independent-cohort prognostic validation.** A pre-registered analysis of MenaCalc (or an RNA-based MenaINV/Mena11a score) in at least one independent breast-cancer cohort with long follow-up, with the endpoint and cutoff fixed before analysis. Success criterion: replication of the Agarwal 2012 direction and magnitude; failure criterion: no association, as in TCGA BRCA.
3. **Assay development (research-grade).** Isoform-specific antibodies (building on Forse 2015) and/or exon-specific RT-qPCR / RNA-seq assays, with analytical validation (sensitivity, specificity, reproducibility) in a research lab. No clinical assay, no regulatory submission, no diagnostic claim at this step.
4. **Blood / circulating-tumour-cell feasibility.** Only after step 3: test whether the isoform pattern is detectable in CTCs or cell-free RNA from patients. This is the application's ¶0061 assertion, which has **no peer-reviewed support** — treat it as a hypothesis to test, not a capability.
5. **Beyond breast cancer — or not.** Test the isoform pattern in one non-breast adenocarcinoma (e.g. pancreas or colon, where pan-Mena upregulation is reported) before repeating the application's all-adenocarcinoma claim anywhere. If the pattern does not hold, the programme stays breast-only.
6. **Therapeutic hypothesis testing (preclinical only).** Isoform-specific knockdown / splice-switching in mouse models, measuring metastasis endpoints — the experiment the application's ¶¶0014/0046 proposes but does not report as a therapy. No human work, no drug development, no trial design until a preclinical signal exists.
7. **TMEM integration.** Evaluate whether Mena isoform scoring adds prognostic information to TMEM doorway scoring (Rohan 2014; Karagiannis 2017) in the same cohorts, rather than treating them as separate markers.

### 7.7 What it would need to be real

- **A lab and a dataset owner:** an academic or commercial partner with breast-cancer cohorts, tissue, and assay capability. None exists for the Cancer DAO today.
- **Access to the granted patents:** the family patents (US 9,719,142; US 8,603,738) are held by Albert Einstein College of Medicine / MIT / IFO-Regina Elena. Any use of the claimed methods would need a licence or a freedom-to-operate opinion — **counsel to advise; this brief does not give legal advice**. The 2022 application's abandonment does not remove the granted family patents.
- **Regulatory honesty from the start:** any future assay would need analytical and clinical validation and, for patient use, the applicable regulatory pathway (FDA clearance/approval or LDT framework as it then stands). Nothing in this brief starts that process.
- **Funding and governance:** the Cancer DAO is a proposed entity with no funds, no governance, and no legal form. A MENA programme cannot start until the DAO question in §6 item 2 is decided.

### 7.8 What NOT to claim

- Do NOT call US 2022/0251662 A1 a granted patent, and do NOT omit that the application is abandoned. The granted patents are US 9,719,142 (2017) and US 8,603,738 (2013) — cite those numbers only for the granted family, and do not quote their claim scope (not verified in this pass).
- Do NOT present the application as peer-reviewed or as clinical evidence. It is a patent application reporting its own experiments.
- Do NOT claim any Mena test diagnoses, predicts, or detects metastatic cancer in patients. MenaCalc and TMEM are research assays in retrospective cohorts — neither is FDA-cleared or approved, and no Mena-based test has regulatory clearance established in this brief.
- Do NOT claim any treatment or cure. No Mena-targeted drug exists; the application's inhibition methods are proposals; the "mito" construct in Fig. 9 is an experimental tool, not a drug candidate.
- Do NOT quote the 4-patient human FNA data (3–37 fold; ratio 7.5) as clinical evidence. It is application-only data, n=4 + 1 control.
- Do NOT present a Mena blood test as existing. The application's blood-assay assertion has no peer-reviewed support found.
- Do NOT repeat the application's all-adenocarcinoma generalisation (breast, prostate, pancreas, colon, brain, liver, lung, head and neck) as fact. Isoform-specific evidence is breast-cancer evidence.
- Do NOT drop the TCGA caveat: MenaCalc did not stably correlate with survival in the TCGA breast-cancer cohort (*Sci Rep* 2016). Present Agarwal 2012 and the TCGA result together.
- Do NOT quote the application's 2006 breast-cancer statistics (212,920 new invasive cases; 40,970 deaths) as current figures. They are 2006 ACS figures.
- Do NOT attribute MenaCalc or TMEM to the application. Both are literature terms from the Condeelis programme's peer-reviewed work.
- Do NOT present the MENA programme as existing. It is a proposed research agenda for a proposed entity (the Cancer DAO), with no lab, assay, dataset, partner, funding, or timeline.
- Do NOT aggregate this pillar with the BCL-2 pillar or the open-data pillar into a single claim about the Cancer DAO's research output. The Cancer DAO has produced no research.

### 7.9 Figure-alignment notes for this area

| Figure | Resolution |
|---|---|
| US 2022/0251662 A1 status | **Application publication, abandoned** (Google Patents, 2026-11-07). Filed 2021-09-16, published 2022-08-11, app 17/477,327. Never "the patent US 2022/0251662". |
| Granted family: US 9,719,142 + US 8,603,738 | **Verified 2026-11-07 (Google Patents).** 9,719,142 granted 2017-08-01, active, expires 2028-07-27. 8,603,738 granted 2013-12-10, active, expires 2030-01-28. Claim scope NOT verified — do not quote claims. |
| Pan-Mena 3–4 fold up in invasive cells | **Patent-reported + peer-reviewed.** Application ¶0057 (citing Wang 2004); Goswami 2009. |
| Mena `++` 2–3 fold up; `11a` ≥8-fold down | **Patent-reported + peer-reviewed.** Application ¶0058; Goswami 2009 (PMID 18985426). |
| Mouse FNA: `+++` 7.5-fold up; 11a to 30% | **Patent-reported only.** Application ¶0063, Fig. 10 (18 PyMT mice, 9 early vs 9 late). |
| Human FNA: `+++` 3–37 fold; ratio 7.5 (patient 5609) | **Patent-reported only, n=4 IDC + 1 FA.** Application ¶0064, Table 3, Fig. 11. No peer-reviewed publication found. |
| MenaCalc prognostic (501 + 296 cohorts; P=0.0004, 0.0321) | **Peer-reviewed, with caveat.** Agarwal et al. 2012. Caveat: no stable correlation in TCGA BRCA (*Sci Rep* 2016, 6:35298). |
| TMEM prognostic (n=481, ER+/HER2−) | **Peer-reviewed.** Robinson 2009; Rohan 2014 (JNCI dju136). Karagiannis 2017 (n=20 neoadjuvant cohort; PMID 28679654). "Clinically validated" in Karagiannis 2017 = retrospective-cohort validation, not regulatory clearance. |
| MenaINV function (invasion/metastasis) | **Peer-reviewed.** Philippar 2008 (Dev Cell 15:813–828); Roussos 2011 (J Cell Sci 124:2120–2131, PMID 21670198); Roussos 2011 (Clin Exp Metastasis 28:515–527). |
| MenaINV antibody (research tool) | **Peer-reviewed.** Forse et al. 2015 (Clin Exp Metastasis 33:249–261). |
| Blood test / all-adenocarcinoma claim / therapy | **NOT FOUND in peer-reviewed literature.** Application assertions only (¶¶0061, 0066, 0014/0046–0047). |
| Mena `++` (4-aa FYLG exon) distinct function | **NOT FOUND.** Co-upregulated with `+++` (Goswami 2009); no peer-reviewed paper found isolating a distinct Mena++ protein function. Functional literature is on MenaINV (`+++`). |

### 7.10 Open questions needing Mike's decision

1. **Does the MENA programme belong on a Cancer DAO page at all, and in what form?** Options: (a) a third section on the single Cancer DAO agenda page (Item 1 in §3); (b) a separate MENA programme page, cross-linked (recommended — keeps each pillar's sources and caveats intact, consistent with §6 item 1 option (b)); (c) the Cancer DAO stays a world/focus-domain page only. Mike needs to choose before any page is built.
2. **Patent position:** should counsel review the granted family patents (US 9,719,142; US 8,603,738) for claim scope and freedom-to-operate before any MENA content goes live, given the claims were not read in this pass? (Recommendation: yes — a one-page counsel note on what the granted claims actually cover, and whether the 2022 application's abandonment affects anything.)
3. **TCGA caveat handling:** the MenaCalc TCGA non-replication is a real scientific wrinkle. Should the programme's first research step (re-analysis of public RNA-seq, §7.6 step 1) be commissioned as a standalone verification pass before any MENA page is written — or is the caveat, stated on the page, enough? (Recommendation: verification pass first; it is cheap and it decides whether the programme's premise survives contact with public data.)
4. **Therapeutic direction:** the application proposes MenaINV inhibition as a therapy. Should the Cancer DAO page include the therapeutic direction at all (Item 3), or hold it until a preclinical signal exists? (Recommendation: include as a labelled research direction only, with the "no drug exists" line in the same paragraph — never as a standalone promise.)

### Sources for §7

- `~/workspace/user/files/frank_gerter.pdf` — US 2022/0251662 A1, Condeelis et al., published 11 August 2022 (25 pages; read in full 7 Nov 2026). All application-grounded facts in §7.3 are from this document, cited by paragraph/figure; the application contains no claims section in the uploaded PDF.
- Google Patents (checked 7 Nov 2026): US 2022/0251662 A1 — status Abandoned (app 17/477,327); US 9,719,142 B2 — granted 1 August 2017, Active, adjusted expiration 2028-07-27; US 8,603,738 B2 — granted 10 December 2013, Active, adjusted expiration 2030-01-28; WO2008097466 — Ceased. Google Patents notes its legal-status display "is an assumption and is not a legal conclusion".
- Goswami S et al., "Identification of invasion specific splice variants of the cytoskeletal protein Mena present in mammary tumor cells during invasion in vivo", *Clin Exp Metastasis* 2009, 26(2):153–159. PMID 18985426; PMC3042857.
- Philippar U et al., "A Mena invasion isoform potentiates EGF-induced carcinoma cell invasion and metastasis", *Dev Cell* 2008, 15(6):813–828.
- Roussos ET et al., "Mena invasive (MenaINV) promotes multicellular streaming motility and transendothelial migration in a mouse model of breast cancer", *J Cell Sci* 2011, 124:2120–2131. PMID 21670198.
- Roussos ET et al., "Mena invasive (Mena(INV)) and Mena11a isoforms play distinct roles in breast cancer cell cohesion and association with TMEM", *Clin Exp Metastasis* 2011, 28:515–527.
- Agarwal S et al., "Quantitative assessment of invasive Mena isoforms (MenaCalc) as an independent prognostic marker in breast cancer", published September 2012 (cohorts n=501 and n=296; log-rank P=0.0004 and P=0.0321).
- Robinson BD et al., "Tumor microenvironment of metastasis in human breast carcinoma: a potential prognostic marker linked to hematogenous dissemination", *Clin Cancer Res* 2009.
- Rohan TE et al., *J Natl Cancer Inst* 2014 (doi:10.1093/jnci/dju136) — TMEM density and metastasis risk, n=481 ER-positive/HER2-negative early-stage breast cancer.
- Karagiannis GS et al., "Neoadjuvant chemotherapy induces breast cancer metastasis through a TMEM-mediated mechanism", *Sci Transl Med* 2017, 9:eaan0026. PMID 28679654.
- Forse CL et al., "Characterization of the expression of the pro-metastatic MenaINV isoform during breast tumor progression", *Clin Exp Metastasis* 2015, 33(3):249–261.
- "The alternatively-included 11a sequence modifies the effects of Mena on actin cytoskeletal organization and cell behavior", *Sci Rep* 2016, 6:35298 (doi:10.1038/srep35298) — Mena11a anti-invasive function; MenaCalc in three cohorts; TCGA BRCA non-replication caveat.
- Karagiannis GS et al., "Signatures of breast cancer metastasis at a glance", *J Cell Sci* 2016, 129:1751–1758 (PMC4893654) — review synthesising the MenaINV-high / Mena11a-low pattern and TMEM.
- Di Modugno F et al., "Human Mena protein, a serex-defined antigen overexpressed in breast cancer…", *Int J Cancer* 2004, 109(6):909–918 (cited in the application ¶0006; pan-Mena overexpression in human breast cancer).
- Wang W et al., "Identification and testing of a gene expression signature of invasive carcinoma cells within primary mammary tumors", *Cancer Res* 2004, 64(23):8585–8594 (cited in the application; invasion signature and 3–4 fold pan-Mena upregulation).

---

*Merged from inspiration-bio-patents.md, 2026-11-07 — inspiration layer; hypotheses + designs, not results.*

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
