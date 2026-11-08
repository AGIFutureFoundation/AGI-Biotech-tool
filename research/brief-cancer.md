# Enhancement Brief — Cancer

**Staging only — local brief. Do NOT publish, push, deploy, email, or share.**
**Research date: 7 November 2026. Evidence: `RESEARCH.md` §4 (which consolidates `research-biodao-genomic-als-cancer.md`, `githubs.md`, `inventory-bio.md`).**
**Applies to:** any future cancer page, article, or series content on the Foundation site, and to the existing pages that mention cancer only in passing. A later worker should be able to apply this brief without re-researching: every item below gives the exact fact, its source URL, and its as-of date.

## Honesty lines (read first — they govern every item)

- **Zero cancer research content exists today — its enhancements are NEW content built from the verified open resources below (NCI, TCGA, cBioPortal, ClinicalTrials.gov), not corrections.** Do not present any new cancer page as a correction of existing research, and do not imply cancer content existed before.
- No cure, treatment, diagnosis, or medical-device claims. FDA approvals below are regulatory facts about **specific drugs for specific indications** — not endorsements, and not evidence about any other compound.
- The Cancer DAO is a **world/name only** today (Fred Hutchinson anchor, promo short, web-viewer world). It is not a research programme, a trial, or a dataset. Do not present it as one.
- Every number needs a source URL + as-of date. Where a figure could not be verified, say so — notably: no verified yearly total of FDA oncology approvals, no verified cBioPortal study count, and ClinicalTrials.gov counts that differ by source.
- TCGA/GDC data is **partly open, partly controlled (dbGaP)** — never describe the whole of TCGA as open download.

---

## 1. What exists today on Mike's sites / articles

From `inventory-bio.md` §§2, 5, 7, 9, 11.1 (paths included). **There is no cancer biology, oncology, or trial content anywhere on the machine.** "Cancer" appears only as:

- **(a) The Cancer DAO world/name:**
  - WorldForge Earth page "Original DAO Worlds (33)" marks Cancer Dao (Fred Hutchinson Cancer Center, Seattle) Live as a **web-viewer world only (not RP1-attached)** (memory 2026-10-26).
  - Cancer-dao + biota-blockchain among the first 41 WorldForge worlds (`~/workspace/your_files/rp1-review/` — promo-video manifests + WorldForge setup doc; Cancer Dao anchor Seattle 47.6263,-122.3292, Fred Hutchinson).
  - Promo-video manifests + bright-brand shorts incl. a Cancer DAO short (`~/workspace/your_files/rp1-review/promo-videos/`; memory 2026-11-04/05 — Cancer DAO short in Batch 2/3; Foundation video set 24/25 incl. Cancer DAO short; video-enhancement wave, 5 shorts incl. biota + cancer linking to series index as fallback — **no dedicated series page**).
  - Cancer DAO as one of 6 PBC focus-domain DAOs (Cancer, Robotics, Ecology, Climate, Education, Public Health) (memory 2026-10-26).
  - `~/workspace/your_files/worlds-3d-iwsdk/` and `~/workspace/your_files/worlds-3d-depth-2-drafts/` — world definitions only; no bio research content.
- **(b) One line in `als-01`:** `~/workspace/your_files/agifuturefoundation-articles/als/als-01-what-a-compound-library-is.md` — natural-product cancer drugs cited as an example class of compound libraries. (That is the full extent of cancer content in the ALS articles; see `brief-als.md`.)
- **(c) One line in `diagnostic-x-01`:** `~/workspace/your_files/agifuturefoundation-articles/diagnostic-x/diagnostic-x-01-screening-vs-diagnosis.md` — cervical cancer screening as the classic example of screening done as a programme. Its site page is `~/workspace/your_files/hostinger-email/sites/agifuturefoundation.org/articles/article-54-screening-vs-diagnosis.html` (the cancer hit on the Foundation site).
- **(d) A funder name in contacts CSVs:** Cancer Prevention and Research Institute of Texas (a funder name in `~/workspace/user/files/` ZoomInfo contacts CSVs and in `~/workspace/goals/contacts-and-molecule-file-consolidation/files/contacts-organized/` — a company/funder name, not research).
- **Foundation site counts:** cancer appears in 12 Foundation-site files — all catalog/cross-link mentions (series catalogs, features, project pages), not cancer content. There is **no cancer series page, no cancer article, and no cancer research page** on the Foundation site. (For contrast: the bio series that do have pages are S4/S5/S18/S27/S28 — see `brief-biodao-genomic-compounds.md`.)
- **Staged articles counts:** cancer appears in 2 staged-article files (the two one-line mentions above). `cognition-x/` has zero hits for any bio term.
- **Memory:** cancer appears in 6 memory files — all the world/promo-short/focus-domain mentions above, plus the 2026-11-03 website review (WAVE/bioacoustics.cloud live but separate; Fellowship site live).
- **Gmail cache:** zero cancer hits.
- **No cancer repo** in Mike's org is listed in `githubs.md` §12 (the org's bio repos are bioacoustics-cloud, bioacoustics-cloud-pages, AGI-Biotech-tool, toxicology, wave-site, wave.agifuturefoundation.org).

**Consequence for the worker:** do not "fix" a cancer page — there is none to fix. Items in §2 are **new-page specifications**. Each new page must be labelled as new content, dated, and sourced as below. If Mike has not approved a cancer page, do not create one — this brief is a specification for when he does.

---

## 2. Exactly what to add or correct, item by item

### Item 1 — NEW PAGE (when approved): "Cancer genomics — the open data" (TCGA via the NCI GDC)
- **Status:** new content. No existing page to correct.
- **Verified facts:**
  - **TCGA (The Cancer Genome Atlas):** large-scale collaborative effort organised by NCI and NHGRI, launched **2006**, completed **2018**, to characterise cancer at the molecular level using genomics. Legacy continues through the Pan-Cancer Atlas and the NCI Genomic Data Commons.
  - Scale: **~2.5 petabytes** of genomic, epigenomic, transcriptomic and proteomic data plus clinical information from **over 11,000 patients representing 33 cancer types** (NCI bioinformatics training page, accessed Nov 2026).
  - Access — open vs controlled: **not all TCGA data is open access.** Open-access data can be downloaded freely; data unique to an individual (individual germline variant data, primary sequence .bam files, clinical free-text, exon array files) are **controlled access** requiring certification through NCBI **dbGaP Authorized Access**. The primary hub is the **NCI Genomic Data Commons (GDC)**; legacy (non-GRCh38) datasets are no longer archived by the GDC — use the Broad GDAC Firehose / FireBrowse or cBioPortal DataHub for those. The original TCGA Data Portal is listed as **closed 2026** (re3data, last update 8 Sep 2026), succeeded by the GDC.
  - **NCI Genomic Data Commons (GDC):** NCI's repository and computational resource for cancer genomic data and associated clinical information. Includes data from **22 programmes (including TCGA), 83 projects, 69 primary sites, 44,637 cases** (NCI training page, Nov 2026). Data access and downloads are **free; no login required** except for controlled data (dbGaP authorisation, eRA Commons login). Portal: https://portal.gdc.cancer.gov/ (URL from NCI training material; not separately scraped).
  - Usage signal (Jan 2026): in NCI's Childhood Cancer Data Initiative download table for Jan 2026, TCGA-BRCA was the most-downloaded dataset (755.95 TB), with CCDI-MCI second (592.57 TB) — evidence TCGA data remains heavily used years after the programme ended.
- **Sources + as-of:** https://bioinformatics.ccr.cancer.gov/docs/btep-coding-club/CC2024/TCGA/TCGA_download/ (NCI CCR bioinformatics training — TCGA scale, open vs controlled, GDC counts); https://www.re3data.org/repository/r3d100011173 (TCGA Data Portal, closed 2026, succeeded by GDC; last update 8 Sep 2026); https://www.cancer.gov/research/areas/childhood/childhood-cancer-data-initiative/events-webinars/past-webinars/ccdi-virtual-symposium-series-1.pdf (CCDI symposium, 12 Mar 2026 — Jan 2026 download table)
- **Wording to use:** "TCGA (NCI/NHGRI, 2006–2018) characterised 11,000+ patients across 33 cancer types (~2.5 PB). Its data lives on in the NCI Genomic Data Commons (44,637 cases across 22 programmes, Nov 2026). Open-access processed data is free to download; individual-level data is controlled access via dbGaP."
- **Do NOT** link the original TCGA Data Portal as live — it is listed as closed 2026, succeeded by the GDC. Do NOT quote TCGA's exact current GDC file counts as live portal counts — they change with reprocessing; the 44,637-case total is the NCI training page's figure, not a live portal count.

### Item 2 — NEW PAGE / SECTION (when approved): "Exploring cancer genomics — cBioPortal"
- **Status:** new content. No existing page to correct.
- **Verified facts:**
  - **cBioPortal** is an open platform for exploratory, interactive visualisation, analysis and download of cancer genomics data (Memorial Sloan Kettering / Dana-Farber / others; NCI funds an instance). Users can view genomic alterations across patients/cancer types, run survival analysis and group comparisons, and explore by gene, mutation or cancer type. Best for exploration; for raw mRNA expression or full segmented copy-number files, use the GDC.
  - Access: open for exploration/download of the processed datasets it hosts; it does not hold controlled raw sequence data. NCI also runs a CCDI instance at cbioportal.ccdi.cancer.gov.
  - **CCDI (Childhood Cancer Data Initiative):** **40 multimodal paediatric/AYA studies** currently available (Mar 2026 symposium).
- **Sources + as-of:** https://www.cancer.gov/research/areas/childhood/childhood-cancer-data-initiative/events-webinars/past-webinars/ccdi-virtual-symposium-series-1.pdf (CCDI symposium, 12 Mar 2026 — 40 studies)
- **Wording to use:** "cBioPortal (cbioportal.org) is the open exploration front end for cancer genomics — view alterations across patients and cancer types, run survival analysis, and download processed datasets. It does not hold controlled raw sequence data; for that, use the GDC. NCI's Childhood Cancer Data Initiative reports 40 multimodal paediatric/AYA studies (Mar 2026)."
- **Do NOT quote a count of cBioPortal studies/samples** — no single current count was verified in this run.
- **Repos to link (verified via GitHub MCP, 2026-11-07):**
  - https://github.com/cBioPortal/cbioportal — cBioPortal for Cancer Genomics (main platform), Apache 2.0, last activity 2026-11-06, original, active (1,064 stars)
  - https://github.com/cBioPortal/cbioportal-frontend — React frontend, last activity 2026-11-06, original, active (152 stars)
  - https://github.com/cBioPortal/datahub — curated public cancer datasets for cBioPortal, last activity 2026-11-05, original, active (218 stars)
  - https://github.com/cBioPortal/cbioportal-docker-compose — run cBioPortal via Docker Compose, last activity 2026-10-29, original, active (23 stars)
  - https://github.com/BioinformaticsFMRP/TCGAbiolinks — R/Bioconductor toolkit for TCGA data access/analysis, last activity 2026-10-19, original, active (357 stars)
  - **OpenTargets platform:** main platform repo **not confirmed** in this pass — search surfaced only `opentargets-archive/*` (archived) and an unofficial MCP server (`Augmented-Nature/OpenTargets-MCP-Server`, 11 stars). **Do not cite a platform repo URL without verifying it separately.**

### Item 3 — NEW PAGE / SECTION (when approved): "Cancer registries — SEER"
- **Status:** new content. No existing page to correct.
- **Verified facts:**
  - **NCI (National Cancer Institute)** is the US federal government's principal agency for cancer research (NIH). It runs the GDC (Item 1), the **Childhood Cancer Data Initiative (CCDI)** — 40 multimodal paediatric/AYA studies available (Mar 2026), with a dedicated cBioPortal instance — and the **Surveillance, Epidemiology, and End Results (SEER)** programme.
  - **SEER:** funded continuously by NCI **since 1973**; **17 core registries + 11 research-support registries across 22 geographic areas**; covers **~45.9% of the US population**. Standard research files are **free to any user with a valid email address**; the linked SEER-Medicare product is not a public-use file and carries direct cost-recovery fees.
- **Source + as-of:** https://intuitionlabs.ai/pdfs/public-biomedical-datasets-2026.pdf (Public Biomedical Datasets 2026, 1 Aug 2026 — SEER coverage/fees, All of Us vs UK Biobank; citing seer.cancer.gov)
- **Wording to use:** "SEER (NCI, since 1973) covers ~45.9% of the US population through 17 core registries + 11 research-support registries across 22 geographic areas. Standard research files are free with an email registration; the linked SEER-Medicare product is fee-gated."

### Item 4 — NEW PAGE / SECTION (when approved): "Clinical trials — ClinicalTrials.gov" (with the count caveat)
- **Status:** new content. No existing page to correct.
- **Verified facts:**
  - **ClinicalTrials.gov** is the registry and results database of privately and publicly funded clinical studies worldwide, run by the US National Library of Medicine (NIH). The registry is free to search; its aggregate database **AACT** is publicly available for aggregate analysis. Registration is required for many trials by law/policy, but many trials remain unregistered, so the registry is **not a census of all clinical research**.
  - Scale (counts differ by date and definition — read carefully): a 2026 EACL paper's table gives **543,172 "all studies"** on ClinicalTrials.gov, with 60,449 completed with results. Wikipedia gives **over 444,000 trials from 221 countries**. A 2025 landscape paper gives **more than 345,000 interventional and observational studies**. The WHO ICTRP page still says "over 300,000" (stale).
  - Cancer-specific: a Frontiers in Epidemiology landscape analysis (Oct 2026) examined prevention/interception studies registered through Sep 2025: 296 retrieved, 209 eligible, 75.1% interventional — and found the field "structurally invisible" in registry categories, with 87.6% of records under generic "Other" funding.
- **Sources + as-of:** https://preview.aclanthology.org/ingest-lrec/2026.eacl-demo.26.pdf (CLINICALTRIALSHUB, EACL 2026 — 543,172 all studies); https://en.wikipedia.org/wiki/ClinicalTrials.gov (444,000+ trials, 221 countries); https://www.who.int/observatories/global-observatory-on-health-research-and-development/resources/databases/databases-on-processes-for-r-d/clinical-trials (WHO ICTRP — stale "300,000" figure, do not use as current); https://scienmag.com/cancer-interception-trials-are-hiding-in-plain-sight-on-clinicaltrials-gov/ (15 Oct 2026, Frontiers in Epidemiology landscape)
- **Wording to use:** pick ONE of the two current wordings and cite it — either "over 500,000 registrations (2026)" (EACL 2026, 543,172 "all studies") OR "over 444,000 trials from 221 countries" (Wikipedia). **Do not mix them into one number.** Add: "The registry is free to search, but it is not a census of all clinical research — many trials remain unregistered."
- **Do NOT** use the WHO "over 300,000" figure as current (stale).

### Item 5 — NEW PAGE / SECTION (when approved): "FDA oncology approvals — what an approval means" (individual approvals only, no yearly total)
- **Status:** new content. No existing page to correct.
- **Verified facts (all 2026, all for the specific indication stated — not general cancer claims):**
  - The FDA maintains a live **Cancer Accelerated Approvals** listing (ongoing approvals with postmarketing requirements to verify clinical benefit) and per-drug approval notices.
  - **Gedatolisib (Revtorpyk, Celcuity)** + fulvestrant ± palbociclib for HR-positive, HER2-negative locally advanced/metastatic breast cancer without a PIK3CA mutation — approved **14 Jul 2026** (VIKTORIA-1, NCT05501886, 392 adults).
  - **Dostarlimab (Jemperli)** for Stage II/III locally advanced dMMR/MSI-H rectal cancer — accelerated approval **19 Oct 2026** (AZUR-1, NCT05723562).
  - **Sevabertinib (Hyrnuo)** for HER2 (ERBB2) TKD-mutant non-squamous NSCLC — accelerated approval **9 Sep 2026** (SOHO-02).
  - **Amivantamab + hyaluronidase (Rybrevant Faspro)** for recurrent/metastatic head-and-neck squamous cell carcinoma — accelerated approval **5 Nov 2026** (OrigAMI-5).
  - A 2026 oncology round-up also lists approvals/expansions in early 2026 including nivolumab + chemotherapy for previously untreated Hodgkin lymphoma (20 Mar 2026), vepdegestrant for ESR1-mutated ER+/HER2- breast cancer (1 May 2026), relacorilant + nab-paclitaxel for platinum-resistant ovarian cancer (25 Mar 2026), teclistamab + daratumumab for relapsed/refractory multiple myeloma (5 Mar 2026), zongertinib for HER2-TKD NSCLC (26 Feb 2026), and others (JADPRO FDA Focus, 2026).
- **Sources + as-of:** https://www.fda.gov/drugs/cancer-approvals/ongoing-cancer-accelerated-approvals (FDA, ongoing accelerated approvals — accessed Nov 2026; entries dated Sep–Nov 2026); http://www.fda.gov/drugs/cancer-approvals/fda-approves-gedatolisib-fulvestrant-or-without-palbociclib-hr-positive-her2-negative-locally (FDA, 14 Jul 2026); https://jadpro.com/education/fda-focus/ (JADPRO FDA Focus, 2026 approvals list)
- **Wording to use:** "Each approval below is for the specific drug and indication stated, on the date stated. An approval is a regulatory fact about that drug for that indication — not an endorsement, and not evidence about any other compound. Accelerated approvals carry postmarketing requirements to verify clinical benefit."
- **Do NOT aggregate into a "2026 approval count"** — no verified total count for 2025 or 2026 was established in this run. Cite the FDA's own approval pages per drug/indication.

### Item 6 — Open cancer datasets summary table (for any new cancer page)
- **Status:** new content. Use this table verbatim (it is the verified summary from the research file).
  | Resource | What is open | Access |
  |---|---|---|
  | NCI GDC (incl. TCGA) | Open-access processed data free, no login; raw/individual-level data controlled via dbGaP | portal.gdc.cancer.gov |
  | cBioPortal (+ CCDI instance) | Processed cancer genomics, open exploration/download | cbioportal.org; cbioportal.ccdi.cancer.gov |
  | SEER | Standard research files free (email registration); SEER-Medicare fee-gated | seer.cancer.gov |
  | ClinicalTrials.gov / AACT | Registry + results + aggregate database, free | clinicaltrials.gov |
  | CCDI Hub | 40 multimodal paediatric/AYA studies | ccdi.cancer.gov |

### Item 7 — Corrections to the two existing one-line mentions (do NOT expand them into cancer content)
- **Where:** `als/als-01-what-a-compound-library-is.md` (staged article — hand to the publish coordinator) and `diagnostic-x/diagnostic-x-01-screening-vs-diagnosis.md` (staged article — same).
- **What to do:** leave both lines as they are — they are correct as example-class mentions (natural-product cancer drugs as an example of compound libraries; cervical cancer screening as the classic example of screening done as a programme). Do NOT expand either article into a cancer article, and do NOT add cancer figures to either. If a reader follows the mention, link to the new cancer page (Item 1) once it exists and is approved — not before.
- **Site pages:** the corresponding site pages are `agents/als/articles/what-a-compound-library-is.html` and `articles/article-54-screening-vs-diagnosis.html` — same instruction.

### Item 8 — Cancer DAO world: label it accurately; do not upgrade it to a research programme
- **Where:** any page that names Cancer DAO — the WorldForge Earth page, the rp1-review manifests, the video hub (`videos/index.html`), and any future series index.
- **Verified fact:** Cancer Dao (Fred Hutchinson Cancer Center, Seattle; anchor 47.6263,-122.3292) is marked Live as a **web-viewer world only (not RP1-attached)**. A Cancer DAO promo short exists (bright-brand template, Batch 2/3; Foundation video set 24/25). Cancer DAO is one of 6 PBC focus-domain DAOs (Cancer, Robotics, Ecology, Climate, Education, Public Health). The video-enhancement wave links the cancer short to the series index as fallback — **no dedicated series page** exists.
- **Wording to use:** "Cancer DAO is a world on WorldForge (web-viewer only) and a focus domain — not a research programme, a trial, or a dataset. For the open cancer data, see [new cancer page, once approved]."
- **Do NOT** present the world, the short, or the focus-domain listing as cancer research content, and do NOT invent a Cancer DAO series number, programme, partner, or timeline. (Cancer DAO has no W3 series number in the 33-series list — it is a world/focus domain, not a series.)

---

## 3. What NOT to claim

- Do NOT claim any cure, treatment, or diagnosis for any cancer. FDA approvals are regulatory facts about specific drugs for specific indications — not endorsements and not evidence about any other compound.
- Do NOT aggregate the FDA approvals into a yearly total — no verified total for 2025 or 2026 was established.
- Do NOT quote a cBioPortal study/sample count — none was verified.
- Do NOT mix ClinicalTrials.gov counts into one number — use either "over 500,000 registrations (2026)" (EACL) or "over 444,000 trials from 221 countries" (Wikipedia), with its source. Do NOT use the stale WHO "300,000" figure.
- Do NOT describe TCGA as wholly open download — individual-level data is controlled via dbGaP. Do NOT link the original TCGA Data Portal as live (closed 2026, succeeded by the GDC).
- Do NOT present the Cancer DAO world, promo short, or focus-domain listing as cancer research content, and do NOT invent a Cancer DAO series number, programme, partner, or timeline.
- Do NOT present the new cancer content as a correction of existing research — there was none. Label it as new content, dated 7 Nov 2026 (research) with its own publication date when it goes live.
- Do NOT cite an OpenTargets platform repo URL — the main platform repo was not verified in this pass.
- Do NOT quote NCI's total budget or CCDI funding levels — not researched in this run.
- Do NOT imply the ALS compound library treats cancer — `als-01` cites natural-product cancer drugs only as an example class of compound libraries (see `brief-als.md`).

---

## 4. Figure-alignment notes for this area

| Figure | Resolution |
|---|---|
| TCGA ~2.5 PB / 11,000+ patients / 33 types vs GDC 44,637 cases / 22 programmes / 83 projects / 69 sites | Different scopes (TCGA programme vs the whole GDC, which includes TCGA + 21 other programmes). Quote each with its scope; do not merge. |
| ClinicalTrials.gov 543,172 (EACL 2026) vs 444,000+ (Wikipedia) vs 345,000+ (2025 landscape) vs 300,000 (WHO ICTRP, stale) | Counts differ by date and definition. **Use one, with its source; do not mix.** Do not use the WHO figure as current. |
| FDA oncology approvals 2025 / 2026 totals | **No verified total — do not quote one.** List approvals individually with drug, indication, and date. |
| cBioPortal study/sample count | **Not verified — omit.** CCDI's 40 multimodal paediatric/AYA studies (Mar 2026) is the only verified study count in this area. |
| SEER ~45.9% US coverage | NCI SEER figure (IntuitionLabs, Aug 2026, citing seer.cancer.gov). Quote with its date. |
| Cancer content on Mike's machine | **Zero research content.** The only mentions are the world/name, two one-line examples, and a funder name. All cancer enhancements are new content. |

---

## 5. Open questions needing Mike's decision

1. **Should a cancer page exist at all, and in what form?** Options the research supports: (a) a single "Cancer genomics — the open data" page (Items 1–4 + 6); (b) separate TCGA/GDC, cBioPortal, SEER, and trials pages; (c) a Cancer DAO page that stays a world/focus-domain page and links out to the open-data page. Mike needs to choose before any page is built.
2. **Cancer DAO scope:** is Cancer DAO meant to become a research programme/series, or stay a world + focus domain? It has no W3 series number and no dedicated series page today. If it is to become a series, that is a corporate decision (counsel, filings) — not a content decision.
3. **FDA approvals page:** should the approvals section be a living list (updated per FDA notice) or a dated snapshot (Nov 2026)? A living list needs an owner and a re-verification cadence; a snapshot needs its as-of date on the page.
4. **ClinicalTrials.gov count:** which of the two current wordings should be the house wording — "over 500,000 registrations (2026)" (EACL) or "over 444,000 trials from 221 countries" (Wikipedia)?
5. **OpenTargets:** should a follow-up pass verify the OpenTargets platform repo URL before it is linked, or should OpenTargets be omitted from the cancer pages?
6. **NCI budget / CCDI funding:** should a follow-up pass research NCI's total budget and CCDI funding levels, or should the pages omit funding figures entirely? (Recommendation: omit until researched.)
7. **Linking from the two one-line mentions:** once a cancer page exists and is approved, should `als-01` and `diagnostic-x-01` link to it? (Recommendation: yes, as a single outbound link each — not an expansion of either article.)
