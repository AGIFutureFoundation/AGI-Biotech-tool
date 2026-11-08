# Enhancement Brief — ALS

**Staging only — local brief. Do NOT publish, push, deploy, email, or share.**
**Research date: 7 November 2026. Evidence: `RESEARCH.md` §3 (which consolidates `research-biodao-genomic-als-cancer.md`, `githubs.md`, `inventory-bio.md`).**
**Applies to:** the staged ALS articles, the ALS agent site, the ALS interactive components, the staged ALS homepage, and the ALS series-adjacent pages (Molecular S11). A later worker should be able to apply this brief without re-researching: every item below gives the exact fact, its source URL, and its as-of date.

## Honesty lines (read first — they govern every item)

- **The ALS Researcher agent is "not a medical device."** Nothing in this brief claims diagnosis, treatment, or cure for ALS or any disease. Every compound output must carry the "not a medical device" line.
- The agent is **offline** — listed in Virtuals ACP, no instance deployed, no hire fulfillable. 0 jobs completed, $0 earned (as of 2026-11-06).
- **ALS has no W3 series number.** The vr-spaces-loop `series.json` S34 ALS / S35 Parkinsons must NOT be adopted.
- **No compound-library data file exists.** The library is 6 ACP job listings + agent site + 3 staged articles. Do not quote a library size or contents.
- Answer ALS / Neuromine and Project MinE are open resources to **build beside, not duplicate** — cite and, where permitted, query them; do not claim to re-collect their data.
- Investigational programmes (TDI-1831, mRNA platform, Pridopidine, PrimeC) are investigational. Quote ALS TDI's CEO — "I cannot promise you which program will reach a clinical trial" — not a timeline.
- Every number needs a source URL + as-of date. Where a figure could not be verified, say so.

---

## 1. What exists today on Mike's sites / articles

From `inventory-bio.md` §§2, 4, 6 (paths included):

**Staged articles — `~/workspace/your_files/agifuturefoundation-articles/als/` (read-only; publish coordinator active — do NOT edit these files yourself; hand corrections to the coordinator):**
- `als/als-01-what-a-compound-library-is.md` — explains compound libraries (incl. natural-product libraries; cancer drugs cited as an example class) as the ALS Researcher agent's product.
- `als/als-02-from-compound-to-treatment.md` — the long road from a compound to a treatment; ALS drug-development context.
- `als/als-03-als-research-field.md` — the ALS research field itself (disease, research landscape).
- `als/assets/charts/als-jobs-by-price.svg` — chart of the 6 ALS ACP jobs by price (compound_* jobs).
- ALS appears in 24 staged-article files incl. `MANIFEST.md` + chart SVGs in other families that list the $ALS agent in the family catalog.

**Agent site — `~/workspace/your_files/hostinger-email/sites/agents/als/` — ALS Researcher ($ALS), "Developing a Synthetic Compound Library":**
- `agent.json` — name ALS Researcher; 6 jobs + 1 sub (compound_library_snapshot $10/24h, compound_research_report $25/48h, compound_data_access $50/24h, compound_lookup $2/30min, library_growth_report $15/48h, compound_screening_pack $150/72h; library_weekly $25/30d); token $ALS, Base, mcap $3.6K, 1 holder, not graduated; status as of 2026-11-06, **0 jobs completed, $0 earned, offline (no instance deployed)**.
- `index.html`, `jobs.html`, `about.html`, `hire.html` — homepage + full ACP catalog at real prices + offline honesty note ("not currently online to receive or deliver hires").
- `articles/what-a-compound-library-is.html`, `articles/from-compound-to-treatment.html`, `articles/als-research-field.html` — the staged ALS articles as site pages (cancer mentioned once, natural-product cancer drugs).
- `.well-known/ai-catalog.json`, `.well-known/agent-skills/{hire-on-virtuals,read-agent-facts,read-agent-pages,token-facts}.md`, `llms.txt`, `auth.md` — machine-readable catalog/skills; compound-job names throughout.
- Live state (per `~/workspace/your_files/omega-hive-live/ACP_PUBLIC_STATE_2026-11-06.md`): ALS site live at als.agifuturefoundation.org (200); 29 jobs + 6 subs verified live in Virtuals ACP 2026-11-06; instances offline, no hire fulfillable.

**Interactive components (staged only, nothing live) — `~/workspace/your_files/interactive-builds/als/`:**
- `job-explorer.html`, `hire-walkthrough.html`, `subscription-explorer.html`, `data.js`, `INTEGRATION.md` — ALS job/hire/subscription explorers (compound jobs at real ACP prices).

**Staged homepage — `~/workspace/your_files/homepage-redesign/als/index.html` + `README.md`:**
- 3 dropdowns, "Listed, not yet online" banner, featured jobs at real ACP prices.

**Foundation site — `~/workspace/your_files/hostinger-email/sites/agifuturefoundation.org/`:**
- `series/S11-molecular.html` — Molecular series page (ALS appears here).
- ALS appears in 15 Foundation-site files (series catalogs, features, project pages — catalog context, not ALS research content).

**Worlds:**
- `~/workspace/your_files/worlds-3d-iwsdk/src/data/worlds/biota-blockchain.json` (+ `src/data/worlds-data.js`, `src/data/holodeck-fabric.js`, `src/data/advisors.js`, `src/player.js`, `src/lobby.js`) — Biota world fabric; ALS Researcher + CMMC appear as in-world agent companions.

**Mike's own repos:**
- https://github.com/AGIFutureFoundation/AGI-Biotech-tool — molecular workspace for drug discovery (VR/browser); neurogenetic targets — ALS, Parkinson's, Shriners Children's conditions; last activity 2026-10-12; original, app (not a stub). Worth linking from the ALS pages.

**What does NOT exist:**
- No compound-library data file, no molecule file, no screening data on disk (inventory §§10–11). The library exists only as the job listings + site + articles above.
- No ALS research data on the machine beyond the articles and the agent listing. ALS data access in the wider world is via controlled-access datasets (Answer ALS, PRO-ACT), not open code (see §2 item 6).

---

## 2. Exactly what to add or correct, item by item

### Item 1 — Add the compound-library jobs table, with real ACP prices and the offline note, to every ALS page that names the product
- **Where:** `agents/als/index.html`, `jobs.html`, `about.html`, `hire.html` (already carry the catalog — verify against this table); `als-01` (already explains the library — verify the job names/prices match); the staged ALS homepage; the ALS interactive explorers (`job-explorer.html`, `hire-walkthrough.html`, `subscription-explorer.html`, `data.js`).
- **Verified fact (ACP, verified live 2026-11-06):** 6 jobs + 1 subscription:
  | Job | Price | Turnaround |
  |---|---|---|
  | compound_library_snapshot | $10 | 24h |
  | compound_research_report | $25 | 48h |
  | compound_data_access | $50 | 24h |
  | compound_lookup | $2 | 30min |
  | library_growth_report | $15 | 48h |
  | compound_screening_pack | $150 | 72h |
  | library_weekly (subscription) | $25 | 30d |
- **Agent facts to keep attached:** token $ALS, Base, market cap $3.6K, 1 holder, not graduated; status as of 2026-11-06: **0 jobs completed, $0 earned, offline (no instance deployed)**. Site live at als.agifuturefoundation.org (200).
- **Source + as-of:** `~/workspace/your_files/omega-hive-live/ACP_PUBLIC_STATE_2026-11-06.md` (verified live in Virtuals ACP 2026-11-06); `agents/als/agent.json`.
- **Wording to use:** "The ALS Researcher ($ALS) offers six compound-library jobs, $2–$150, plus a $25/30d weekly subscription. The agent is listed in Virtuals ACP and is not currently online to receive or deliver hires (0 jobs completed, $0 earned, as of 6 Nov 2026). **The ALS Researcher is not a medical device.**"

### Item 2 — Add the "not a medical device" line to every compound output / page
- **Where:** every ALS agent page (`index.html`, `jobs.html`, `about.html`, `hire.html`), every staged ALS article, the ALS interactive explorers, the staged ALS homepage, and any compound-library description.
- **Verified fact:** per the programme brief and the research file, the ALS agent is "not a medical device" — nothing claims diagnosis, treatment, or cure for ALS, cancer, or any disease. ChEMBL/PubChem/DrugBank are chemistry/bioactivity data, not treatment resources (see Item 5).
- **Wording to use (verbatim, on every compound page/output):** "The ALS Researcher is not a medical device. It provides compound-library research information only. It does not diagnose, treat, or cure ALS or any disease."
- **Do NOT** soften this to "for research purposes only" without the "not a medical device" sentence, and do NOT drop it from any page that lists a compound job.

### Item 3 — Add Answer ALS + Neuromine as the flagship open resource (build beside, not duplicate)
- **Where:** `als-03-als-research-field.md` (staged article — hand to the publish coordinator) and `agents/als/about.html` / `articles/als-research-field.html`.
- **Verified facts:**
  - Answer ALS is one of the most comprehensive ALS research consortia, producing clinical + multi-omics data and biological samples and openly sharing them via the cloud-based **Neuromine Data Portal**.
  - Full dataset release, **3 Nov 2025 (New Orleans)**: the complete dataset from **over 1,100 Answer ALS participants**, integrated with **ALS TDI's ALS Research Collaborative (ARC)** study data, in a unified cloud platform. Together: **over 150 terabytes of harmonised data spanning more than 2,500 ALS patient profiles**. Data layers per participant: whole-genome sequencing, RNA-seq transcriptomics, proteomics/biomarkers, epigenomics (e.g. DNA methylation), longitudinal clinical histories/outcomes, plus patient-derived stem-cell neural models.
  - Adoption: since Neuromine's launch in **2021, 500+ independent ALS research projects** have been initiated (520+ by Mar 2026, per Microsoft) and dozens of papers published. Researchers can go from hypothesis to data access and matched biosamples in **about two weeks** (Microsoft, Mar 2026). Answer ALS estimates the model could accelerate research timelines by as much as 65% over the next couple of years (Microsoft, Mar 2026 — **an estimate, not a measured outcome**).
  - New in 2026: **Champion Insights** — a nationwide study (with ALS TDI and Augie's Quest) on why elite athletes, military veterans and first responders develop ALS at higher rates; active operations commenced **4 Feb 2026**, enrolling **500 participants** (genetic, biological, environmental factors). **NFL committed $500,000** to Champion Insights (announced **20 Oct 2026**).
  - Also 2025: **LADDIA** (Louisiana AI Drug Development Infrastructure for ALS), launched **22 Jul 2025** with GATC Health and others, for AI-powered drug discovery for ALS and other neurodegenerative diseases.
- **Sources + as-of:** https://www.eurekalert.org/news-releases/1104438 (Answer ALS full dataset release, 3 Nov 2025 — **Firecrawl-scraped 7 Nov 2026, success=true**; confirms 1,100+ participants, 150+ TB, 2,500+ profiles, 500+ projects since 2021, ARC collecting for 8+ years, free webinar 11 Dec 2025); https://unlocked.microsoft.com/steve-gleason-answer-als-neuromine/ (26 Mar 2026 — 520+ projects, 2,500+ profiles, ~2-week access, 450,000 prevalence estimate); https://www.answerals.org/category/press-release/ (NFL $500k, 20 Oct 2026; Champion Insights launch, 4 Feb 2026; LADDIA, 22 Jul 2025)
- **Method correction to carry forward:** the EurekAlert Answer ALS scrape SUCCEEDED (success=true, confirmed by the background result, 7 Nov 2026 — full text matches the figures cited here). The HTTP 403 in this research pass was the Caper VitaDAO page, not EurekAlert.
- **Wording to use:** "The largest open ALS resource is Answer ALS / Neuromine: 1,100+ participants, 150+ TB of harmonised data, 2,500+ patient profiles with ALS TDI's ARC study (full release 3 Nov 2025). Our compound library builds beside it — it cites and, where permitted, queries these resources; it does not re-collect their data."
- **Caveat to keep:** whether the Neuromine portal requires registration/approval vs fully open download is not established — sources say "openly accessible" and "about two weeks" to access + biosamples, implying a request step. **Do not describe it as anonymous open download.**

### Item 4 — Add ALS TDI (ARC, TDI-1831, mRNA platform) with the CEO's own caution
- **Where:** `als-03-als-research-field.md` and `agents/als/articles/als-research-field.html`.
- **Verified facts:**
  - ALS Therapy Development Institute (ALS TDI) is a registered **501(c)(3) nonprofit** (EIN 04-3462719), the world's first nonprofit biotech focused on ALS; runs the **ALS Research Collaborative (ARC)** — a longitudinal, patient-driven study collecting deep clinical, molecular and biomarker data over time.
  - ARC has **more than 1,800 participants** across **50 countries** (2025 annual report). In early 2026 ALS TDI announced a landmark expansion of its laboratories.
  - 2026 focus: (1) expanding the team to carry ideas "from first experiment to first patient"; (2) accelerating programmes in motion — **TDI-1831** (copper-biology candidate, most advanced; advanced into **IND-enabling studies** in 2025) for rare genetically defined ALS, a **precision mRNA delivery platform for the CNS** (lipid nanoparticles with Dr. Michael Mitchell, University of Pennsylvania, begun 2025), and expanding ARC; (3) launching **Champion Insights**.
  - Also in 2025: type I **PRMT inhibitors** (discovered 2020 in relation to C9orf72, the most common genetic cause of ALS) advanced through preclinical evaluation; first comprehensive characterisation of a **Profilin1 mouse model** published; digital-biomarker research (voice and movement data) expanded.
- **Sources + as-of:** http://www.als.net/news/on-progress-in-als-research/ (ALS TDI CEO letter, 31 Dec 2025); http://www.als.net/about-als-tdi/annual-reports/2025/ (2025 Annual Report)
- **Wording to use (include the quote):** "ALS TDI's CEO wrote: 'I cannot promise you which program will reach a clinical trial.' TDI-1831 (IND-enabling studies, 2025) and the precision mRNA delivery platform are investigational; no efficacy claim is made here."
- **Do NOT** give a timeline for TDI-1831, the mRNA platform, or any programme reaching a clinical trial.

### Item 5 — Add Project MinE (open Data Browser) and NEALS, with investigational labels
- **Where:** `als-03-als-research-field.md` and `agents/als/articles/als-research-field.html`.
- **Project MinE — verified facts:** multinational ALS sequencing consortium (whole-genome and whole-exome sequencing) aiming to find the genetic basis of ALS. The **Project MinE Data Browser is open access** (databrowser.projectmine.com, **v1.7, last updated 14 Oct 2026**): interactive platform for gene-, domain- and variant-level rare-variant associations in ALS. The **whole-exome dataset is the largest ALS exome dataset to date: 13,138 ALS patients and 69,775 controls** (processed as in Hop et al., 2026). Whole-genome data from **>6,000 individuals** underpins recent analyses (e.g. CYP2D6 pharmacogenetic analysis, SSRN preprint 2 Oct 2025, using 4,140 cases / 1,812 controls for risk and 4,459 cases for survival). A 2026 exome harmonisation (Hop et al., 2026) analysed **17,919 ALS cases and 200,703 controls** across 22 cohorts (discovery + replication).
  - Related: the **Longitude Prize on ALS** (£7.5M, MND Association / Challenge Works) convened WGS from **>9,000 ALS cases and >3,500 controls** (Project MinE, ALS Compute, NYGC, ALS TDI, Answer ALS), plus multi-omics from >2,000 cases, via DNAnexus/AWS; entry window closed 3 Dec 2025; **20 teams awarded £100,000 Discovery Awards in Apr 2026**.
  - Sources: http://databrowser.projectmine.com/ (v1.7, updated 14 Oct 2026); https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5444471 (posted 2 Oct 2025); https://aijourn.com/delivering-on-a-decade-of-als-data-the-role-of-ai-in-drug-discovery/
- **NEALS — verified facts:** the clinical-trials network for ALS, founded as the Northeast ALS Consortium; at its 2025 annual meeting (30th anniversary) it announced its new name, **Network of Excellence for ALS**, with **150+ sites across the US, Canada and internationally**. 2025 meeting themes: combination treatment, expansion in genetics, gene therapies (adenoviral vectors; antisense oligonucleotides) aimed at targets relevant to sporadic ALS, not only mutation-specific subsets, and earlier identification after symptom onset. **2026 annual meeting: 30 Oct 2026, Clearwater, Florida.** Trials featured there: Pridopidine PREVAiLS Phase 3 (~500 participants, ~60% enrolled as of Oct 2026, recruitment expected complete Q1 2027, topline Q1 2028 — investigational, not approved) and NeuroSense PrimeC PARADIGM Phase 2b → PARAGON Phase 3 (FDA clearance to initiate Phase 3 reported Oct 2026). Both are investigational; no efficacy claim is made here.
  - Sources: https://podscan.fm/podcasts/neurologylive-mind-moments/episodes/154-neals-2025-takeaways-that-matter-for-als-care; https://www.businesswire.com/news/home/20261028286138/en/Prilenia-and-Ferrer-to-Share-New-Pridopidine-Data-and-PREVAiLS-Study-Updates-at-the-NEALS-Consortium-2026-Annual-Meeting (Oct 2026)
- **ALS in numbers (context only):** **~450,000 people worldwide live with ALS** (Microsoft / Answer ALS, Mar 2026). That is an estimate, not a registry count. Source: https://unlocked.microsoft.com/steve-gleason-answer-als-neuromine/

### Item 6 — Add the compound-data foundation (ChEMBL + PubChem) and the DrugBank trap to the compound-library explainer
- **Where:** `als-01-what-a-compound-library-is.md` (staged article — hand to the publish coordinator) and `agents/als/articles/what-a-compound-library-is.html`.
- **Verified facts:**
  - **ChEMBL 37, prepared 1 May 2026** (EMBL-EBI): **2,921,148 compounds** (2,897,819 with mol files), **3,824,604 compound records** (non-unique), **24,527,044 activities**, **1,970,438 assays**, **101,100 documents**. Licence: **CC BY-SA 3.0**; ChEMBL asks that ChEMBL IDs and the release number be preserved on reuse. Free REST API, bulk download via FTP.
    - Source: https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/chembl_37_release_notes.txt
  - **PubChem (NCBI/NLM/NIH):** **~124 million compounds, ~349 million substances** (homepage, Oct 2026). Peer-reviewed 2025 update: **118.6 million compounds as of Sep 2024** (Kim et al., Nucleic Acids Res. 2025, doi:10.1093/nar/gkae1059). Licence: **free to use; US federal public-domain resource** — but reuse rights follow each depositor/source.
  - **DrugBank — the trap:** version **5.1.22, released 27 Jun 2026**; datasets under **CC BY-NC 4.0**; **"All Academic downloads are temporarily paused"** (Jun 2026); API access remains available (paid API; registration required); **commercial use requires a commercial licence**. Do NOT build a commercial compound product on DrugBank data without a licence.
    - Source: https://go.drugbank.com/releases/latest
- **Wording to use:** "Any compound data the ALS Researcher serves cites its source database, version and date — ChEMBL 37 (1 May 2026, CC BY-SA 3.0) and PubChem (~124M compounds, Oct 2026, public domain) are the open foundations. DrugBank (CC BY-NC 4.0, academic downloads paused Jun 2026) is not a free input for a commercial product. **The ALS Researcher is not a medical device.**"
- **Repos to link (verified via GitHub MCP, 2026-11-07):**
  - https://github.com/rdkit/rdkit — RDKit, BSD 3-Clause, last activity 2026-11-07, original, very active (3,672 stars)
  - https://github.com/chembl/chembl_webresource_client — official Python client for the ChEMBL API, Apache 2.0, last activity 2026-10-22, original, active (453 stars)
  - https://github.com/mcs07/PubChemPy — Python wrapper for PubChem PUG REST API, MIT, last activity 2026-11-03, original, active (518 stars)
  - https://github.com/AGIFutureFoundation/AGI-Biotech-tool — Mike's molecular workspace (VR/browser), ALS/Parkinson's targets, last activity 2026-10-12, original, app (not a stub)

### Item 7 — State plainly that there is no major ALS research repo — link only the small academic projects, labelled as such
- **Where:** any repo-link block on the ALS agent site or articles.
- **Verified fact:** **No major dedicated ALS research repo exists on GitHub.** What exists is small, individual/academic analysis code — no ALS equivalent of cBioPortal or RDKit. **No public repo for Project MinE** — search returns unrelated repos. PRO-ACT itself is a clinical-trial database, not a repo.
- **Repos that may be linked (verified via GitHub MCP, 2026-11-07; label each as small/academic):**
  - https://github.com/iamjli/AnswerALS_QTL — eQTL/caQTL analyses for Answer ALS data (academic), last activity 2025-04-25, original, small (2 stars)
  - https://github.com/SOCR/ALS_PA — ALS Predictive Analytics (UCLA SOCR), last activity 2023-12-11, original, stale (5 stars)
  - https://github.com/JPLeRouzic/ALS-biomarkers — biomarker analysis using the PRO-ACT ALS database, last activity 2024-08-26, original, small (2 stars)
  - https://github.com/charlottebensaid/Projet-SLA-Data — student ML project on ALS progression using PRO-ACT, last activity 2026-07-01, original, small (0 stars)
- **Do NOT** present any of these as an ALS platform, toolkit, or official resource.

### Item 8 — Correct the ALS series-number error wherever it appears
- **Where:** any page, chart, or catalog that numbers ALS as a series — in particular the vr-spaces-loop `series.json` (35 entries S1–S35 incl. S34 ALS / S35 Parkinsons; `~/workspace/your_files/vr-spaces-loop/metaprompts-and-ideas-2026-11-07.md` collection).
- **Verified fact:** ALS has no series number. The 33-series W3 list (`~/workspace/user/files/W3_LLC.pdf`, 3 pages, PDF dated 2026-04-03, internal printout, NOT a Wyoming SOS filing) does not include ALS or Biota. The S34/S35 entries are a tension vs the 33-series list, unresolved.
- **What to do:** do NOT adopt S34 ALS / S35 Parkinsons in any ALS page, chart, or catalog. Refer to ALS as "the ALS Researcher agent ($ALS)" with no series number. If the vr-spaces-loop file is ever edited, that is Mike's decision (see §5 item 1) — this brief does not authorise the edit.

### Item 9 — Keep the ALS drug-development article honest (`als-02`)
- **Where:** `als-02-from-compound-to-treatment.md` (staged article — hand to the publish coordinator).
- **What to do:** verify the article's "long road from a compound to a treatment" framing against the investigational labels in Items 4–5: TDI-1831 is in IND-enabling studies (2025), not in a trial; Pridopidine PREVAiLS is Phase 3 (topline Q1 2028 expected); PrimeC PARAGON Phase 3 has FDA clearance to initiate (Oct 2026). No article may imply any of these is approved or effective. Add the ALS TDI CEO quote (Item 4) if it is not already there. Do not add a timeline for any programme reaching patients.

---

## 3. What NOT to claim

- Do NOT claim the ALS Researcher diagnoses, treats, or cures ALS or any disease. **"Not a medical device" stays attached to every compound output.**
- Do NOT claim the agent is online or able to take hires — it is offline as of 2026-11-06; 0 jobs completed, $0 earned.
- Do NOT quote a compound-library size, contents, or screening results — no data file exists.
- Do NOT claim to have re-collected Answer ALS / Neuromine or Project MinE data. Cite them; query them only where permitted; do not describe Neuromine as anonymous open download (access implies a request step, ~2 weeks).
- Do NOT present the 65% timeline-acceleration figure as a measured result — it is Answer ALS's own estimate (Microsoft, Mar 2026).
- Do NOT give a timeline for TDI-1831, the mRNA platform, Pridopidine, or PrimeC reaching patients. Quote the CEO's "I cannot promise you which program will reach a clinical trial" instead.
- Do NOT number ALS as S34 (or Parkinsons as S35). ALS has no series number.
- Do NOT build a commercial compound product on DrugBank data without a commercial licence (CC BY-NC 4.0; academic downloads paused Jun 2026).
- Do NOT present any small academic ALS repo as a platform or official resource, and do NOT claim a Project MinE repo exists — none was found.
- Do NOT claim the ~450,000 worldwide ALS prevalence figure is a registry count — it is an estimate (Microsoft / Answer ALS, Mar 2026).

---

## 4. Figure-alignment notes for this area

| Figure | Resolution |
|---|---|
| Answer ALS 500+ projects (Nov 2025 release) vs 520+ (Mar 2026) | Different dates, both true. Use "500+ since 2021 (Nov 2025); 520+ by Mar 2026". |
| Project MinE exome 13,138 patients / 69,775 controls vs harmonisation 17,919 cases / 200,703 controls (2026) | Different analyses (largest exome dataset to date vs 2026 harmonisation across 22 cohorts, discovery + replication). Quote each with its scope. |
| Project MinE WGS ">6,000 individuals" | No 2026 update beyond ">6,000" was verified — do not inflate it. |
| ALS prevalence ~450,000 | Estimate, not a registry count (Microsoft / Answer ALS, Mar 2026). |
| S34 ALS / S35 Parkinsons vs 33-series list | **Unresolved tension — do NOT adopt S34/S35.** ALS has no series number. |
| Compound job prices | Real ACP prices, verified live 2026-11-06 (see Item 1 table). The chart `als-jobs-by-price.svg` must match this table exactly. |

---

## 5. Open questions needing Mike's decision

1. **S34/S35 tension:** reconcile the vr-spaces-loop `series.json` (S34 ALS + S35 Parkinsons) with the 33-series W3 list, or remove the S34/S35 entries? Until he decides, no ALS page may number ALS as a series.
2. **Compound-library data:** there is no data file. Does Mike want one built (from ChEMBL/PubChem, with source/version/date attribution), or should the library remain a job-listing product only? If built, who owns the sourcing, the attribution, and the "not a medical device" review of every output?
3. **Neuromine access:** should the ALS agent seek registered access to Answer ALS / Neuromine (implying a ~2-week request step), or cite it only? No contact has been made with Answer ALS, ALS TDI, or Project MinE.
4. **AGI-Biotech-tool linking:** confirm the repo (VR/browser molecular workspace, ALS/Parkinson's) is the right thing to link from the ALS pages, and whether its "AGI compound collection" wording needs a data-file correction.
5. **Agent online status:** the ALS agent is offline with 0 jobs completed. Is there a plan (and a top-up/deployment step) to bring an instance online, or should the pages keep the "listed, not yet online" banner indefinitely?
6. **Pridopidine / PrimeC tracking:** both are investigational with 2027–2028 milestones. Should a future pass update the ALS field article when PREVAiLS recruitment completes (expected Q1 2027) or PARAGON initiates?
