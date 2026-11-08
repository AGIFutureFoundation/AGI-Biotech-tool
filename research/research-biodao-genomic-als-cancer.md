# Bio Research Expansion — BioDAO / Genomic Go / AGI Compounds / ALS / Cancer

**Published:** research file in this repo's `research/` folder. Not a live-site edit.
**Research date: 7 November 2026. All figures are as-of the source date given; verify again before any public use.**
**Scope note:** "AGI Compounds" = the ALS Researcher agent's compound library (Virtuals, $ALS, not graduated). Its jobs, per the task brief: compound_library_snapshot $10/24h, compound_research_report $25/48h, compound_data_access $50/24h, compound_lookup $2/30min, library_growth_report $15/48h, compound_screening_pack $150/72h. The ALS agent is "not a medical device" — nothing in this file claims diagnosis, treatment, or cure for ALS, cancer, or any disease.
**W3 series named here (S4 Curable.X, S5 BioPharma.Go, S18 BioDAO, S27 Genomic DAO, S28 Genome.Blockchain) are PROPOSED, not formed.** ALS has no series number. AURA Maternal is a separate project and is not folded into this work.
**Method:** `browser.search` to find source pages, then Firecrawl scrape of key primary pages via `~/workspace/custom-connectors/custom.firecrawl/bin/firecrawl_scrape.py` (1 credit per successful scrape). Firecrawl proof scrape of example.com succeeded 7 Nov 2026; UK Biobank access page scraped successfully the same day (success=true); the EurekAlert Answer ALS release also scraped successfully (success=true, confirmed by the background result, 7 Nov 2026 — full text matches the figures cited in §7). A scrape of the Caper VitaDAO page returned HTTP 403; that item is therefore cited from search-result text, not from a scrape.

---

## 1. BioDAO / Molecule — the IP-tokenisation layer

### What it is
- **Molecule** is the infrastructure layer for decentralised science (DeSci). Its core innovation is attaching legal IP rights to an NFT — an **IP-NFT** — so a research asset can be co-owned and governed by a community. It is the tokenisation engine behind the Bio Protocol / BioDAO ecosystem.
- **Bio Protocol (bio.xyz, BIO token)** is the meta-protocol incubated by Molecule and stewarded by the Bio.xyz Association. Communities form **BioDAOs** (one therapeutic area each), tokenise IP as **IP-Tokens (IPTs)**, and more recently launch AI research agents (**BioAgents**) with their own tokens. BIO is deployed on Ethereum, Base, BNB Chain and Solana.
- **IP-Tokens:** fractional ERC-20 tokens against an IP-NFT (later, against a Lab — see below). The Bio Protocol documentation is explicit that an IPT carries **governance and information rights but no guaranteed financial return**; whether IPT holders are paid on commercialisation is left to the IP owner. Do not present IPTs as equity, revenue shares, or investment returns.

### Current status (as of Oct–Nov 2026)
- Molecule's first-generation IP-NFT stack is now legacy: its contract index marks the Ethereum/Sepolia IP-NFT sections **"UNMAINTAINED"** and lists the live deployment as **"Molecule Labs core (v0.1.0)" on Base**.
- **V3 — the Lab:** the primitive is now a **Lab**: "an NFT (ERC-721) that is permanently bound to its own smart contract wallet (ERC-6551)" with account abstraction (ERC-4337), installable modules (ERC-7579) and an attestation registry (ERC-7484). The research project is an account holding its own treasury, data anchor and licences; transferring the Lab NFT hands over the whole thing.
- **V3 traction (on-chain, as reported 12 Oct 2026):** LabNFT contract reported **151 Labs**, the first minted **8 July 2026**. The OclTokenizer had issued **five IP Tokens**, the first on **18 September 2026**, none since 6 October 2026 (as of the 12 Oct 2026 check). That is early, thin adoption — do not describe V3 as widely deployed.
- IP-NFT contracts reached **V2 in 2024**; in 2025 Molecule extended toward bridging tokenised IP into the real-world-asset (RWA) market.
- Molecule founder/CEO Paul Kohlhaas also launched **Pump.science**, a Solana tokenised-experiment launchpad funding longevity compound trials through freely tradeable tokens.
- Bio Protocol V2 replaced the earlier curation/auction launchpad model with a fixed-price **Ignition Sale** plus post-launch liquidity mechanisms. The launchpad contracts themselves are **not public**; six published audit reports are the only technical description. The BioDAO building blocks (governance token, vesting, Merkle airdrop — three Solidity projects — plus one Solana governance program) **are** open source under the bio-xyz organisation.
- BIO token: initial supply **3,320,000,000**, described as uncapped (issuing more would require deploying a new token contract). Four-token economy: BIO, vBIO, veBIO, BioXP. Governance is still transitioning from BIO/vBIO voting to veBIO.

### What is open vs licensed/gated
- **Open:** Molecule IP-NFT V2 contracts (open source); BioDAO token/vesting/airdrop contracts (open source, Foundry projects); Bio Protocol documentation.
- **Gated / not open:** the V2 launchpad contracts (closed source, audit reports only); IP itself — an IP-NFT/Lab represents legal IP rights, which are owned, licensed and governed, not public-domain data. IPTs give governance/information rights, not a right to the underlying data or a guaranteed payout.
- **Licence note:** an IPT is not a licence to use the IP commercially; commercialisation terms sit with the IP owner / Lab.

### Key figures (with dates)
| Figure | Value | As of / source date |
|---|---|---|
| Labs minted (LabNFT, Base) | 151 | 12 Oct 2026 |
| IP Tokens issued via OclTokenizer | 5 | 12 Oct 2026 (first 18 Sep 2026) |
| BIO initial supply | 3,320,000,000 | Bio Protocol overview, 18 Sep 2026 |
| BioDAOs listed in Bio Protocol docs | 8 (VitaDAO, HairDAO, CerebrumDAO, ValleyDAO, AthenaDAO, CryoDAO, PsyDAO, Curetopia, "and others") | Sep 2026 |

### Sources
- https://caper.network/wiki/desci/ecosystem/molecule (published 28 Jun 2026, updated 27 Oct 2026)
- https://github.com/rya-sge/access-denied/blob/HEAD/_posts/2026-09-18-bio-protocol-overview.md (Bio Protocol overview, 18 Sep 2026)
- https://daotimes.com/understanding-investment-daos-a-comprehensive-guide/ (updated Jul 2026 — secondary; treat its "$15M into research pipelines" and "$315M DeSci market, Apr 2026" as secondary, unverified here)

### Gaps / could not verify
- No primary Molecule/Bio Protocol press page was scraped in this run; the Lab counts above come from a third-party wiki (Caper) reading on-chain data, not from Molecule's own site. Verify the 151-Lab / 5-IPT figures against the Base contracts before quoting them publicly.
- Whether any Lab has yet produced a licensed/commercialised asset could not be verified.
- The "roughly $15 million into active research pipelines" figure (DAO Times, Jul 2026) is secondary and was not verified against Bio Protocol's own reporting.

---

## 2. VitaDAO — longevity, the first BioDAO

### What it is
A community-owned collective funding early-stage longevity / ageing research and holding the resulting IP on-chain as IP-NFTs, governed by VITA token holders. Launched June 2021 from a whitepaper by Tyler Golato and Paul Kohlhaas (Molecule). Now a BioDAO inside the Bio Protocol ecosystem.

### Current status (as of 2026)
- **Status: ongoing**, but with a governance slowdown visible in public records: the vote.vitadao.eth Snapshot space carried **129 proposals** against a **1,150,000 VITA quorum**, and recorded **no new proposal since 9 September 2025** (checked in the Caper dossier, updated Oct 2026). The most recent binding vote cited was VDP-163 (FOXO3 oligos funding), closed 16 Sep 2025 with 17 voters, 6,618,900 VITA cast, all For. The Jan 2025 BIO-airdrop vote drew 37 voters.
- The public site's "Launch app" destination (app.vitadao.com) is, as of 18 Aug 2026, a subscription longevity-AI product whose deployed JavaScript bundle contains no occurrence of `governance`, `proposal`, `vote`, or any Snapshot host — i.e. governance did not move there. Bio Protocol's own documentation lists no governance page either.
- VitaDAO holds a **21 million BIO allocation** from Bio Protocol's bio/acc rewards programme; VDP-161 put **6.9 million BIO** back to the community as an airdrop (80% / 5.52M to VITA holders, 20% / 1.38M to IP-token holders, tiered by holding) and kept **14.1 million BIO** in treasury to fund science.
- VITA is an ERC-20 (Ethereum; mirrors on Solana and Base). Total supply **64,298,880 tokens**.

### What is open vs licensed/gated
- **Open:** the VitaDAO model, IP-NFT approach, Snapshot proposal history (readable), and the funded-project list are public. The first IP token, VITA-FAST (Korolchuk Lab, Newcastle University), was created by VITA-holder vote.
- **Gated:** the IP itself is DAO-owned and licensed, not open data. Voting requires holding VITA in an Ethereum wallet; proposal creation is restricted to an allowlist of thirteen addresses (five admins, eight members).
- **Not a treatment claim:** VitaDAO funded research and one supplement product (VD001, a high-dose spermidine supplement said to be approved by Thailand's FDA, per a Nov 2024 article updated Aug 2026). No longevity treatment or cure is claimed here; that product claim was not independently verified.

### Key figures (with dates)
| Figure | Value | As of / source date |
|---|---|---|
| Projects funded | 31 (reported as "30+" in Feb 2026) | 2026 (Caper/Onchain Atlas, verified 26 Jul 2026) |
| Funding deployed | ~$4.7M (one source says $4.2M / 24 projects — see gaps) | 2026 |
| Split | 3 target-discovery, 18 drug-discovery, 3 preclinical, 3 clinical drug-development projects; 8 IP tokens; 3 companies founded | 2026 |
| VITA total supply | 64,298,880 | Nov 2026 |
| VITA price / market cap | ~$0.163–0.164, market cap ~$3.9–4.4M | 7 Nov 2026 (CoinPaprika / TokenRadar — market data, volatile) |
| Strategic raise | $4.1M, Jan 2023, incl. Pfizer Ventures, Shine Capital, L1 Digital, BeakerDAO, Spaceship DAO | Jan 2023 |
| BIO allocation | 21M BIO | 2025–26 |

### Sources
- https://caper.network/wiki/desci/ecosystem/vitadao (updated Oct 2026)
- https://www.onchainatlas.org/vitadao/ (last verified 26 Jul 2026)
- https://www.techflowpost.com/en-US/article/21685 (published 19 Nov 2024, updated 21 Aug 2026)
- https://coinpaprika.com/coin/vita-vitadao and https://tokenradar.ai/tokens/vitadao (price, 7 Nov 2026)

### Gaps / could not verify
- **Conflicting deployment figures:** Caper/Onchain Atlas say 31 projects / ~$4.7M; a TechFlowPost article says 24 projects / $4.2M. The difference may be date (Nov 2024 vs 2026) — use "31 projects, ~$4.7M deployed (2026)" and note the older figure.
- **Conflicting treasury figure:** a secondary matrix cites a "$55.8M treasury" (VitaDAO newsletter, Mar 2026), including "$38M of IP assets/IP-NFTs valued" — that is a self-reported valuation of illiquid IP, not cash, and it sits next to a ~$4M VITA market cap in Nov 2026. **Do not quote $55.8M as a current treasury without a fresh primary source.**
- Whether VitaDAO's Snapshot inactivity since Sep 2025 reflects a move to another venue or a genuine pause could not be established from public sources in this run. Do not present VitaDAO governance as currently active without checking Snapshot / Bio Protocol first.

---

## 3. AthenaDAO (now AthenaBIO) and other real bio/DeSci DAOs

### AthenaDAO → AthenaBIO
- **What it is:** founded **2022** by Laura Minquini as a DeSci organisation sourcing, funding and incubating women's-health R&D (ovarian ageing, reproductive longevity, diagnostics). A Bio Protocol BioDAO; token **ATH** (capped ERC-20, max supply 100M, ~30M circulating per a Feb 2026 table).
- **Current status:** on **8 March 2026** it published "AthenaBIO: The first Science-First Ecosystem for Women's Health R&D", introducing itself as **AthenaBIO (formerly AthenaDAO)**. The rename had not reached the public site as of 25 Oct 2026 (athenadao.co still said "AthenaDAO", 2026 copyright, "Get ATH Token" link). The shift began **Sep 2025**, when AthenaDAO launched **AthenaBIO as an equity vehicle** — a holding company with SPVs (not a closed-end fund) — to carry vetted assets through validation, regulation and scale, aiming to raise **~$5M against ~15 early-stage assets** (AI diagnostics, ovarian health, reproductive technology).
- **Funding to date:** the Web3 community deployed **~$1.5M**, funding **6 labs, 2 start-ups, 10 fellowships, 100+ live events** (BeautyMatter, 8 Jan 2026). Named bets: ovarian-ageing therapeutic targets with AI drug-discovery firm Gero; the integrated stress response (ISR) pathway for ovarian follicle survival; the cGAS–STING inflammatory pathway in reproductive ageing.
- **Governance:** binding votes ran on Snapshot at athenadao.eth — **18 proposals between Oct 2023 and Sep 2025**, none since Sep 2025 (as of the Oct 2026 check). A 15 Sep 2026 thesis for a new translational research organisation on ovary biology names no token, no vote and no funding round.
- **What is open vs gated:** the community, fellowships and events are open; funded IP is DAO-governed/licensed, not open data. AthenaBIO is an equity vehicle — its assets are held via SPVs, i.e. conventionally gated, not on-chain open.

### Other real BioDAOs (Bio Protocol network — only sourced ones listed)
| DAO | Focus | Token | Sourced status note |
|---|---|---|---|
| **HairDAO** | Hair-loss research | HAIR | BIO-incubated, listed as active (Apr 2026 matrix; Bio Protocol docs Sep 2026). One secondary table claims "~$48M treasury" (DAO Times, Jul 2026) — **unverified, do not quote**. |
| **CryoDAO** | Cryopreservation (organ/tissue storage) | CRYO | BIO-incubated, active. Secondary claim: "$3M raised, partnered with Oxford Cryotechnology" — unverified here. Snapshot ballot CRYO-26 closed 31 Jul 2026 (cited as evidence of live governance in the VitaDAO dossier). |
| **PsyDAO** | Psychedelic research (depression, addiction, PTSD) | PSY | BIO-incubated, active. |
| **ValleyDAO** | Synthetic biology / climate (engineered microbes, carbon capture, biodegradable materials) | GROW | BIO-incubated, active. Secondary claim: "$2M+, partnered with Imperial College London" — unverified here. |
| **CerebrumDAO** | Neurodegeneration / brain health (Alzheimer's, inflammation, blood–brain barrier) | NEURON | BIO-incubated, active. Secondary claim: "struck a deal with Fission Pharma on neurodegeneration" — unverified here. |
| **Curetopia** | Rare diseases | $CURES (Solana, max 100,000,000) | First BioDAO to run a community auction on Solana; led by Dr. Ethan Perlstein. Tokenises funded research as IP-NFTs via Molecule; identified a potential treatment for **AARS2** (fatal rare disease, no approved therapy) and moved to file a provisional patent and tokenise it. **Governance gap:** as of Sep 2026, curetopia.xyz linked no voting venue; Snapshot has no Curetopia space and the Solana Realms registry (314 realms) has no entry. Its executive body of record is a Swiss *Verein*. Science/site/token are current; on-chain governance is not evidenced. |
| **Quantum Biology DAO** | Quantum biology | — | Named in a Bio Protocol pipeline list (undated social post) — **existence as a live BioDAO not verified from a primary source in this run**. |

### Sources
- https://caper.network/wiki/desci/ecosystem/athenadao (updated Oct 2026)
- https://beautymatter.com/articles/how-athena-bio-is-rewriting-rd-funding-for-womens-health (8 Jan 2026)
- https://caper.network/wiki/desci/ecosystem/curetopia (published 18 Jul 2026, updated 18 Oct 2026)
- https://github.com/bucket-foundation/bucket-foundation/blob/HEAD/docs/COMPETITOR_MATRIX.md (23 Apr 2026 — secondary matrix)
- https://github.com/rya-sge/access-denied/blob/HEAD/_posts/2026-09-18-bio-protocol-overview.md (18 Sep 2026)
- https://agenticscience.website/DeSci/DeSciAREA.html (updated 28 Feb 2026 — token-supply table)

### Gaps / could not verify
- Treasury/raise figures for HairDAO, CryoDAO, ValleyDAO and CerebrumDAO appear only in secondary round-ups; none was verified against a primary source. Do not quote them.
- No primary 2026 activity (new proposals, new funding rounds) was verified for HairDAO, PsyDAO, ValleyDAO or CerebrumDAO in this run beyond their listing as active in Bio Protocol docs.
- "Quantum Biology DAO" is named only in a social-media pipeline list; treat as unconfirmed.

---

## 4. Genomic data-sharing initiatives

### GA4GH (Global Alliance for Genomics and Health)
- **What it is:** a global standards-setting organisation for genomics, formed **2013**, uniting **500+** leading institutions. It develops technical standards, policy frameworks and open-source tools for voluntary, secure genomic data sharing.
- **What is open:** its standards are open — notably the **Data Use Ontology (DUO)**, a hierarchical vocabulary of human- and machine-readable data-use terms, implemented by the Broad and Sanger Institutes and used in annotation of **over 200,000 datasets worldwide** (Cell Genomics, Nov 2021, still cited 2026); the **GA4GH Passport** standard for data authorisation/access; and a data-sharing lexicon (including "data visiting" and "federated data analysis") developed by a study group formed Sep 2023, draft Apr 2024, **finalised Jul 2025** (Human Genomics 2025, 19:80).
- **Model:** "data visiting" — shared data is analysed inside the provider's computing environment rather than downloaded — is the direction of travel for UK Biobank and All of Us (see below). GA4GH does not hold genomic data itself.

### All of Us Research Program (NIH, USA)
- **What it is:** NIH programme to gather data from **1 million+ people** in the US to accelerate health research and precision medicine, prioritising historically underrepresented populations.
- **Current status (May–Jun 2026, NIH Council of Councils update, 14 May 2026):** **880,000+ participants** from all 50 states; **22,580+ registered researchers** from **1,360+ organisations**; **1,350+ publications** (>500 in 2025); **14.7 million biosample aliquots**; **499,000+ EHRs**; 2.9M survey responses; DNA results returned to **733,000+ individuals / 277,000+ participants** (figures as presented in the May 2026 deck — the deck's own phrasing is ambiguous on the DNA-results count; cite as "733,000+ individual DNA results returned"). Goal: enrol 1 million participants by end of 2026 and expand data to include whole genomes for 1 million participants. As of Dec 2025: **872,000+ consented, 613,000+ providing biospecimens**.
- **Genomes:** whole-genome sequencing data released for **over 245,000 participants** (per a 2025 review cited by Capgemini, 2026); a Jun 2026 data release (Researcher Workbench V8, 2025) is described as the world's largest genomic + EHR dataset. An Oct 2026 Exeter study analysed **nearly 1 million whole genomes** from UK Biobank + All of Us combined (Genome Medicine, 22 Oct 2026).
- **Access terms:** data via the **Researcher Workbench** (cloud); aggregate data publicly searchable via the Data Browser. **No access fee, but user-borne computational costs** (Genomics, Proteomics & Bioinformatics, Nov 2025, Table 1). Individual-level genomic data is controlled access, not open download. Consent is broad, with return of DNA results to participants.

### UK Biobank
- **What it is:** large-scale biomedical database of **~500,000 volunteers** (UK), with genotyping, imaging, EHR linkage and whole-genome sequencing.
- **Current status:** whole-genome sequencing of **490,640 participants** reported (Nature, 2025). Data available to eligible researchers worldwide (academic, charity, government, commercial) for health-related research in the public interest.
- **Access terms (verified by Firecrawl scrape of the official access page, 7 Nov 2026):** eligibility requires a track record of legitimate health-related research, affiliation with a recognised research organisation, and operation from a country complying with international regulations and not subject to UK/US/EU sanctions. Background checks on every applicant. Proposals raising concerns go to an expert **Access Committee**, consulting the Ethics Advisory Committee and Participant Advisory Group. **Since Jan 2025, applications from insurance companies for direct access to de-identified data are no longer approved** (they may collaborate with / fund approved researchers, or use published findings). Researchers must sign a legal agreement (Material Transfer Agreement); they are **prohibited from trying to re-identify participants and from sharing data with non-collaborators**. Since **2024, access is by default via the UK Biobank Research Analysis Platform (UKB-RAP)**, a restricted cloud platform — downloads are no longer the default — and researchers agree to delete data when the project ends. Tiered access fees apply (per the Nov 2025 data-sharing review).
- **What is open vs gated:** summary/aggregate findings are public; individual-level genomic + phenotypic data are **controlled access, not open**. This is the model to copy for consent and governance — not an open-download dataset.

### openSNP — CLOSED (important)
- **What it was:** open-source site (founded 2011 by Bastian Greshake) where users uploaded consumer genotype files (23andMe, Ancestry, FamilyTreeDNA, deCODEme) under **CC0** (public domain), with code on GitHub under MIT. ~13,000 people shared data; the site warned users there was zero privacy/anonymity.
- **Current status: dissolved / shut down.** Announced 31 Mar 2025; **all user data deleted 10 Apr 2025** (announced date was 30 Apr 2025; the farewell page says 10 Apr). Cause cited: the **23andMe Chapter 11 bankruptcy (23 Mar 2025)** and public fears of DNA misuse; the founder judged that "the risk/benefit calculus of providing free & open access to individual genetic data in 2025 is very different compared to 14 years ago" and that the transformative use of consumer genetic data had turned out to be law-enforcement genealogy rather than biomedical research. **Do not cite openSNP as a live open-genomics resource.** Its archived data still appears in research (e.g. a May 2026 arXiv benchmarking paper across 80 openSNP phenotypes, using pre-shutdown data).
- **Lesson for Genomic DAO / S27 (proposed):** the openSNP closure is the clearest recent evidence that fully open, CC0 individual-level genomic data is now regarded by its own stewards as unsafe to hold. Any proposed genomic data-sharing model should be framed as controlled / federated / data-visiting (GA4GH model), with consent and re-identification protections — not as open download.

### "Open Genes" — not verified
- No distinct, live resource called "Open Genes" was verified as an open genomics dataset in this run. There is a longevity-genetics database sometimes called Open Genes / OpenGenes (human ageing genetics), but its current status, licence and contents were **not verified** — do not cite it. If the programme needs it, that is a follow-up search, not a finding.

### Sources
- https://www.ukbiobank.ac.uk/about-us/how-we-work/access-to-uk-biobank-data/ (official; **Firecrawl-scraped 7 Nov 2026, success=true**)
- https://dpcpsi.nih.gov/sites/dpcpsi/files/2026-05/1045AM-May-15-All-of-Us-Update-508.pdf (NIH Council of Councils, 14 May 2026)
- https://files.simpler.grants.gov/opportunities/aae1388d-369b-4899-be47-2b34c587b623/attachments/58897ff4-836a-4ebd-8e31-7491c7494b42/PAR-27-069-Full-Announcement.html (NIH funding announcement, posted 19 May 2026; Dec 2025 enrolment figures)
- https://gpb.big.ac.cn/articles/download/1282 (Genomics, Proteomics & Bioinformatics 2025, 23(5), qzaf100; advance access 6 Nov 2025 — tiered-fee / no-fee comparison)
- https://en.wikipedia.org/wiki/OpenSNP and http://rip.so/opensnp.html (closure dates; Wikipedia last updated 6 days before 7 Nov 2026)
- https://www.capgemini.com/insights/expert-perspectives/trends-in-2026-for-healthcare-part-3-how-are-clinical-research-and-genomics-creating-personalized-patient-care/ (2026; WGS counts)
- https://scienmag.com/average-human-genome-characterised-for-first-time-from-nearly-one-million-sequences/ (26 Oct 2026, Genome Medicine study)

### Gaps / could not verify
- "Open Genes" as a named open resource — not verified (see above).
- UK Biobank's current tiered fee schedule (exact prices) — not verified; only that tiered fees exist.
- All of Us whole-genome count beyond "245,000+" (2025 review) — the Jun 2026 release size was not pinned to a single verified number in this run.

---

## 5. Cancer genomics resources — NCI, TCGA, cBioPortal

### TCGA (The Cancer Genome Atlas)
- **What it is:** large-scale collaborative effort organised by NCI and NHGRI, launched **2006**, completed **2018**, to characterise cancer at the molecular level using genomics. Legacy continues through follow-up initiatives (notably the Pan-Cancer Atlas and the NCI Genomic Data Commons).
- **Scale:** **~2.5 petabytes** of genomic, epigenomic, transcriptomic and proteomic data plus clinical information from **over 11,000 patients representing 33 cancer types** (NCI bioinformatics training page, accessed Nov 2026).
- **Access — open vs controlled:** **not all TCGA data is open access.** Open-access data can be downloaded freely; data unique to an individual (individual germline variant data, primary sequence .bam files, clinical free-text, exon array files) are **controlled access** requiring certification through NCBI **dbGaP Authorized Access**. The primary hub is the **NCI Genomic Data Commons (GDC)**; legacy (non-GRCh38) datasets are no longer archived by the GDC — use the Broad GDAC Firehose / FireBrowse or cBioPortal DataHub for those. The original TCGA Data Portal is listed as **closed 2026** (re3data, last update 8 Sep 2026), succeeded by the GDC.

### NCI Genomic Data Commons (GDC)
- **What it is:** NCI's repository and computational resource for cancer genomic data and associated clinical information. Includes data from **22 programmes (including TCGA), 83 projects, 69 primary sites, 44,637 cases** (NCI training page, Nov 2026).
- **Access:** data access and downloads are **free; no login required** except for controlled data (dbGaP authorisation, eRA Commons login). Portal: https://portal.gdc.cancer.gov/ (URL from NCI training material; not separately scraped).
- **Usage signal (Jan 2026):** in NCI's Childhood Cancer Data Initiative download table for Jan 2026, TCGA-BRCA was the most-downloaded dataset (755.95 TB), with CCDI-MCI second (592.57 TB) — evidence TCGA data remains heavily used years after the programme ended.

### cBioPortal
- **What it is:** open platform for exploratory, interactive visualisation, analysis and download of cancer genomics data (Memorial Sloan Kettering / Dana-Farber / others; NCI funds an instance). Users can view genomic alterations across patients/cancer types, run survival analysis and group comparisons, and explore by gene, mutation or cancer type. Best for exploration; for raw mRNA expression or full segmented copy-number files, use the GDC.
- **Access:** open for exploration/download of the processed datasets it hosts; it does not hold controlled raw sequence data. NCI also runs a CCDI instance at cbioportal.ccdi.cancer.gov.
- **Scale note:** the number of studies/datasets hosted on cBioPortal was **not pinned to a single verified figure in this run** — do not quote a count. The CCDI reports **40 multimodal paediatric/AYA studies** currently available (Mar 2026 symposium).

### Sources
- https://bioinformatics.ccr.cancer.gov/docs/btep-coding-club/CC2024/TCGA/TCGA_download/ (NCI CCR bioinformatics training — TCGA scale, open vs controlled, GDC counts)
- https://www.cancer.gov/research/areas/childhood/childhood-cancer-data-initiative/events-webinars/past-webinars/ccdi-virtual-symposium-series-1.pdf (CCDI symposium, 12 Mar 2026 — 40 studies; Jan 2026 download table)
- https://www.re3data.org/repository/r3d100011173 (TCGA Data Portal, closed 2026, succeeded by GDC; last update 8 Sep 2026)

### Gaps / could not verify
- A single current count of cBioPortal studies/samples was not verified — omitted deliberately.
- TCGA's exact current GDC file counts change with reprocessing; the 44,637-case GDC total is the NCI training page's figure, not a live portal count.

---

## 6. Drug-compound resources — ChEMBL, PubChem, DrugBank

### ChEMBL (EMBL-EBI)
- **What it is:** manually curated database of bioactive, drug-like molecules, maintained by EMBL's European Bioinformatics Institute; the standard curated bioactivity resource for drug discovery (SAR, potency, targets).
- **Current version — ChEMBL 37, prepared 1 May 2026** (release notes, EBI FTP): **2,921,148 compounds** (2,897,819 with mol files), **3,824,604 compound records** (non-unique), **24,527,044 activities**, **1,970,438 assays**, **101,100 documents**. (ChEMBL 36, Sep 2025: 2,878,000 compounds, 24,270,000 activities — for the growth trend.)
- **Licence / access:** **CC BY-SA 3.0**; ChEMBL asks that ChEMBL IDs and the release number be preserved on reuse. Free REST API (JSON/XML), bulk download via FTP (TSV/SDF/SQL). Funded by Wellcome Trust, EMBL member states, Open Targets, EU IMI and EU Framework 7.
- **What is open:** the full curated database is open under CC BY-SA. Note: ChEMBL incorporates data from sources including BindingDB and SureChEMBL patent bioactivity data and PubChem BioAssays — downstream reuse must respect the original sources where they differ.

### PubChem (NCBI / NLM / NIH, USA)
- **What it is:** the world's largest free general chemistry database, run by the US National Center for Biotechnology Information; compounds, substances, bioassays, properties, patents, toxicity.
- **Current size (checked Oct 2026):** **~124 million compounds, ~349 million substances** (PubChem homepage, Oct 2026). Peer-reviewed PubChem 2025 update reported **118.6 million compounds as of Sep 2024** (Kim et al., Nucleic Acids Res. 2025, doi:10.1093/nar/gkae1059). A Jun 2026 catalogue cites 114M compounds / 302M substances / 304M bioactivities across 903 sources — older snapshot; prefer the Oct 2026 homepage figures.
- **Licence / access:** **free to use; US federal public-domain resource** — but reuse rights follow each depositor/source, so check the source before redistributing a given record. API: PUG-REST, PUG-View; bulk via PUG Download (up to 250,000 records/request) or FTP. Rate limits ~5 requests/sec, 400/min.

### DrugBank
- **What it is:** comprehensive database of drug and drug-target information (approved, investigational, experimental drugs; drug–drug interactions).
- **Current version — 5.1.22, released 27 Jun 2026** (go.drugbank.com/releases/latest): "All drugs" dataset 204 MB; full drug structures (SDF) 11 MB; structure external links 1.98 MB. Datasets released under **CC BY-NC 4.0** (Attribution–NonCommercial).
- **Access — gated, and currently paused:** **"All Academic downloads are temporarily paused"** while DrugBank updates how it distributes data (notice on the releases page, Jun 2026; also reported May 2026). API access remains available (paid API; registration required). Academic licence is free for qualifying researchers; **commercial use requires a commercial licence**. The full database is not open for commercial reuse.
- **Scale (conflicting sources — see gaps):** DrugBank 6.0 (2024) is cited as **11,891 drug entries, incl. 4,563 approved and 6,231 investigational drugs, plus 1.41M drug–drug interactions**. A Jun 2026 catalogue cites ~15,000 drugs (2,700 FDA-approved small molecules, 1,500 FDA-approved biologics, 134 nutraceuticals, ~6,700 experimental). Use the 6.0 figures with their date; do not present a single current drug count as verified.

### What this means for AGI Compounds (proposed)
- ChEMBL and PubChem are the legitimate open foundations for a compound library: ChEMBL (CC BY-SA, attribution + share-alike + preserve IDs/release) and PubChem (public domain, per-source reuse terms). Any compound data the ALS agent serves should cite its source database, version and date — exactly as ChEMBL requires.
- DrugBank is **not** a free input for a commercial product: CC BY-NC, academic downloads paused, commercial licence required. Do not build a commercial compound product on DrugBank data without a licence.
- None of these databases is a treatment resource: they are chemistry/bioactivity data. The ALS agent's "not a medical device" line must stay attached to any compound output.

### Sources
- https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/chembl_37_release_notes.txt (ChEMBL 37, prepared 1 May 2026)
- https://www.moldraw.com/blog/free-chemical-databases-guide.html (published 6 Oct 2026, data checked Oct 2026 — PubChem/ChEMBL sizes and licences)
- https://go.drugbank.com/releases/latest (DrugBank 5.1.22, released 27 Jun 2026; academic downloads paused; CC BY-NC 4.0)
- https://zenn.dev/kent_kamome/articles/df8ff7d14ee8ea?locale=en (May 2026 status table — DrugBank pause, PubChem/ChEMBL licences)

### Gaps / could not verify
- DrugBank's current drug-entry count: the 6.0 (2024) and Jun-2026 catalogue figures conflict; the 5.1.22 release page does not state a headline drug count. Omitted as a single figure.
- PubChem's exact current compound count moves daily; ~124M is an Oct 2026 homepage snapshot.
- BindingDB's current size (~3.29M binding datapoints, ~1.35M molecules, ~9,454 targets, as of 2025) was cited in a Jun 2026 catalogue and not verified against BindingDB itself.

---

## 7. ALS research — ALS TDI, Answer ALS, Project MinE, NEALS

*No treatment, cure or diagnosis claims are made in this section. Research directions and open resources only.*

### Answer ALS + Neuromine (the largest open ALS resource)
- **What it is:** Answer ALS is one of the most comprehensive ALS research consortia, producing clinical + multi-omics data and biological samples and openly sharing them via the cloud-based **Neuromine Data Portal**.
- **Current status — full dataset release, 3 Nov 2025 (New Orleans):** the complete dataset from **over 1,100 Answer ALS participants**, integrated with **ALS TDI's ALS Research Collaborative (ARC)** study data, in a unified cloud platform. Together: **over 150 terabytes of harmonised data spanning more than 2,500 ALS patient profiles**. Data layers per participant: whole-genome sequencing, RNA-seq transcriptomics, proteomics/biomarkers, epigenomics (e.g. DNA methylation), longitudinal clinical histories/outcomes, plus patient-derived stem-cell neural models.
- **Adoption:** since Neuromine's launch in **2021, 500+ independent ALS research projects** have been initiated (520+ by Mar 2026, per Microsoft) and dozens of papers published. Researchers can go from hypothesis to data access and matched biosamples in **about two weeks** (Microsoft, Mar 2026). Answer ALS estimates the model could accelerate research timelines by as much as 65% over the next couple of years (Microsoft, Mar 2026 — an estimate, not a measured outcome).
- **New in 2026:** **Champion Insights** — a nationwide study (with ALS TDI and Augie's Quest) on why elite athletes, military veterans and first responders develop ALS at higher rates; active operations commenced **4 Feb 2026**, enrolling **500 participants** (genetic, biological, environmental factors). **NFL committed $500,000** to Champion Insights (announced **20 Oct 2026**).
- **Also 2025:** **LADDIA** (Louisiana AI Drug Development Infrastructure for ALS), launched **22 Jul 2025** with GATC Health and others, for AI-powered drug discovery for ALS and other neurodegenerative diseases.

### ALS Therapy Development Institute (ALS TDI)
- **What it is:** a registered **501(c)(3) nonprofit** (EIN 04-3462719), the world's first nonprofit biotech focused on ALS; runs the **ALS Research Collaborative (ARC)** — a longitudinal, patient-driven study collecting deep clinical, molecular and biomarker data over time.
- **Current status (2025 Annual Report; CEO letter, 31 Dec 2025; 2026 priorities):** ARC has **more than 1,800 participants** across **50 countries** (2025 annual report). In early 2026 ALS TDI announced a landmark expansion of its laboratories. 2026 focus: (1) expanding the team to carry ideas "from first experiment to first patient"; (2) accelerating programmes in motion — **TDI-1831** (copper-biology candidate, most advanced; advanced into **IND-enabling studies** in 2025) for rare genetically defined ALS, a **precision mRNA delivery platform for the CNS** (lipid nanoparticles with Dr. Michael Mitchell, University of Pennsylvania, begun 2025), and expanding ARC; (3) launching **Champion Insights**. Also in 2025: type I **PRMT inhibitors** (discovered 2020 in relation to C9orf72, the most common genetic cause of ALS) advanced through preclinical evaluation; first comprehensive characterisation of a **Profilin1 mouse model** published; digital-biomarker research (voice and movement data) expanded.
- **Language caution:** ALS TDI's CEO explicitly wrote "I cannot promise you which program will reach a clinical trial." Quote that, not a timeline. TDI-1831 and the mRNA platform are investigational; no efficacy claim is made here.

### Project MinE
- **What it is:** a multinational ALS sequencing consortium (whole-genome and whole-exome sequencing) aiming to find the genetic basis of ALS.
- **Current status:** the **Project MinE Data Browser is open access** (databrowser.projectmine.com, **v1.7, last updated 14 Oct 2026**): an interactive platform for gene-, domain- and variant-level rare-variant associations in ALS, with statistical results and biological annotations. The **whole-exome dataset is the largest ALS exome dataset to date: 13,138 ALS patients and 69,775 controls** (processed as in Hop et al., 2026). Whole-genome data from **>6,000 individuals** underpins recent analyses (e.g. CYP2D6 pharmacogenetic analysis, SSRN preprint 2 Oct 2025, using 4,140 cases / 1,812 controls for risk and 4,459 cases for survival). A 2026 exome harmonisation (Hop et al., 2026) analysed **17,919 ALS cases and 200,703 controls** across 22 cohorts (discovery + replication).
- **Related open aggregation:** the **Longitude Prize on ALS** (£7.5M, MND Association / Challenge Works) convened WGS from **>9,000 ALS cases and >3,500 controls** (Project MinE, ALS Compute, NYGC, ALS TDI, Answer ALS), plus multi-omics from >2,000 cases, via DNAnexus/AWS; entry window closed 3 Dec 2025; **20 teams awarded £100,000 Discovery Awards in Apr 2026**.

### NEALS (now Network of Excellence for ALS)
- **What it is:** the clinical-trials network for ALS, founded as the Northeast ALS Consortium; at its 2025 annual meeting (30th anniversary) it announced its new name, **Network of Excellence for ALS**, with **150+ sites across the US, Canada and internationally**.
- **Current status:** 2025 meeting themes: combination treatment, expansion in genetics, gene therapies (adenoviral vectors; antisense oligonucleotides) aimed at targets relevant to sporadic ALS, not only mutation-specific subsets, and earlier identification after symptom onset. NEALS-affiliated trials process partners industry/investigator trials. **2026 annual meeting: 30 Oct 2026, Clearwater, Florida.** Trials featured there included Pridopidine PREVAiLS Phase 3 (~500 participants, ~60% enrolled as of Oct 2026, recruitment expected complete Q1 2027, topline Q1 2028 — investigational, not approved) and NeuroSense PrimeC PARADIGM Phase 2b → PARAGON Phase 3 (FDA clearance to initiate Phase 3 reported Oct 2026). Both are investigational; no efficacy claim is made here.

### ALS in numbers (context only)
- **~450,000 people worldwide live with ALS** (Microsoft / Answer ALS, Mar 2026). That is an estimate, not a registry count.

### Sources
- https://www.eurekalert.org/news-releases/1104438 (Answer ALS full dataset release, 3 Nov 2025 — **Firecrawl-scraped 7 Nov 2026, success=true**; confirms 1,100+ participants, 150+ TB, 2,500+ profiles, 500+ projects since 2021, ARC collecting for 8+ years, free webinar 11 Dec 2025)
- https://unlocked.microsoft.com/steve-gleason-answer-als-neuromine/ (26 Mar 2026 — 520+ projects, 2,500+ profiles, ~2-week access, 450,000 prevalence estimate)
- https://www.answerals.org/category/press-release/ (press releases incl. NFL $500k, 20 Oct 2026; Champion Insights launch, 4 Feb 2026; LADDIA, 22 Jul 2025)
- http://www.als.net/news/on-progress-in-als-research/ (ALS TDI CEO letter, 31 Dec 2025 — 2026 priorities, TDI-1831, mRNA platform)
- http://www.als.net/about-als-tdi/annual-reports/2025/ (ALS TDI 2025 Annual Report — ARC >1,800 participants, 50 countries; PRMT, Profilin1, digital biomarkers)
- http://databrowser.projectmine.com/ (Project MinE Data Browser v1.7, updated 14 Oct 2026 — 13,138 patients / 69,775 controls exome)
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5444471 (CYP2D6 / Project MinE preprint, posted 2 Oct 2025)
- https://aijourn.com/delivering-on-a-decade-of-als-data-the-role-of-ai-in-drug-discovery/ (Longitude Prize on ALS — £7.5M, WGS counts, Discovery Awards Apr 2026)
- https://podscan.fm/podcasts/neurologylive-mind-moments/episodes/154-neals-2025-takeaways-that-matter-for-als-care (NEALS 2025 takeaways — rename, 150+ sites, 30th anniversary)
- https://www.businesswire.com/news/home/20261028286138/en/Prilenia-and-Ferrer-to-Share-New-Pridopidine-Data-and-PREVAiLS-Study-Updates-at-the-NEALS-Consortium-2026-Annual-Meeting (PREVAiLS enrolment, Oct 2026)

### Gaps / could not verify
- Whether the Neuromine portal requires registration/approval vs fully open download: sources say "openly accessible" and "about two weeks" to access + biosamples, implying a request step. Do not describe it as anonymous open download.
- No 2026 update to Project MinE's total WGS case count beyond ">6,000" was verified.
- The 65% timeline-acceleration estimate (Microsoft) is Answer ALS's own estimate, not a measured result.

---

## 8. Cancer research landscape — NCI, FDA approvals, trials, open datasets

*No cure or treatment claims. Approvals are regulatory facts about specific drugs for specific indications; they are not endorsements and not evidence about any other compound.*

### NCI (National Cancer Institute)
- **What it is:** the US federal government's principal agency for cancer research (NIH). Runs the GDC (see §5), the **Childhood Cancer Data Initiative (CCDI)** — 40 multimodal paediatric/AYA studies available (Mar 2026), with a dedicated cBioPortal instance — and the **Surveillance, Epidemiology, and End Results (SEER)** programme.
- **SEER:** funded continuously by NCI **since 1973**; **17 core registries + 11 research-support registries across 22 geographic areas**; covers **~45.9% of the US population**. Standard research files are **free to any user with a valid email address**; the linked SEER-Medicare product is not a public-use file and carries direct cost-recovery fees. (IntuitionLabs, Aug 2026, citing seer.cancer.gov.)

### FDA oncology approvals landscape (2025–2026)
- The FDA maintains a live **Cancer Accelerated Approvals** listing (ongoing approvals with postmarketing requirements to verify clinical benefit) and per-drug approval notices. Recent examples from the listing/notices (all 2026, all for the specific indication stated — not general cancer claims):
  - **Gedatolisib (Revtorpyk, Celcuity)** + fulvestrant ± palbociclib for HR-positive, HER2-negative locally advanced/metastatic breast cancer without a PIK3CA mutation — approved **14 Jul 2026** (VIKTORIA-1, NCT05501886, 392 adults).
  - **Dostarlimab (Jemperli)** for Stage II/III locally advanced dMMR/MSI-H rectal cancer — accelerated approval **19 Oct 2026** (AZUR-1, NCT05723562).
  - **Sevabertinib (Hyrnuo)** for HER2 (ERBB2) TKD-mutant non-squamous NSCLC — accelerated approval **9 Sep 2026** (SOHO-02).
  - **Amivantamab + hyaluronidase (Rybrevant Faspro)** for recurrent/metastatic head-and-neck squamous cell carcinoma — accelerated approval **5 Nov 2026** (OrigAMI-5).
- A 2026 oncology round-up also lists approvals/expansions in early 2026 including nivolumab + chemotherapy for previously untreated Hodgkin lymphoma (20 Mar 2026), vepdegestrant for ESR1-mutated ER+/HER2- breast cancer (1 May 2026), relacorilant + nab-paclitaxel for platinum-resistant ovarian cancer (25 Mar 2026), teclistamab + daratumumab for relapsed/refractory multiple myeloma (5 Mar 2026), zongertinib for HER2-TKD NSCLC (26 Feb 2026), and others (JADPRO FDA Focus, 2026).
- **How to use this:** cite the FDA's own approval pages per drug/indication; do not aggregate into a "2026 approval count" — no verified total count for 2025 or 2026 was established in this run.

### ClinicalTrials.gov
- **What it is:** the registry and results database of privately and publicly funded clinical studies worldwide, run by the US National Library of Medicine (NIH).
- **Scale (counts differ by date and definition — read carefully):** a 2026 EACL paper's table gives **543,172 "all studies"** on ClinicalTrials.gov, with 60,449 completed with results. Wikipedia gives **over 444,000 trials from 221 countries**. A 2025 landscape paper gives **more than 345,000 interventional and observational studies**. The WHO ICTRP page still says "over 300,000" (stale). **Use "over 500,000 registrations (2026)" with the EACL source, or "over 444,000 trials from 221 countries" with Wikipedia — do not mix them into one number.** The registry is free to search; its aggregate database **AACT** is publicly available for aggregate analysis. Registration is required for many trials by law/policy, but many trials remain unregistered, so the registry is not a census of all clinical research.
- **Cancer-specific:** a Frontiers in Epidemiology landscape analysis (Oct 2026) examined prevention/interception studies registered through Sep 2025: 296 retrieved, 209 eligible, 75.1% interventional — and found the field "structurally invisible" in registry categories, with 87.6% of records under generic "Other" funding.

### Open cancer datasets (summary — see also §5)
| Resource | What is open | Access |
|---|---|---|
| NCI GDC (incl. TCGA) | Open-access processed data free, no login; raw/individual-level data controlled via dbGaP | portal.gdc.cancer.gov |
| cBioPortal (+ CCDI instance) | Processed cancer genomics, open exploration/download | cbioportal.org; cbioportal.ccdi.cancer.gov |
| SEER | Standard research files free (email registration); SEER-Medicare fee-gated | seer.cancer.gov |
| ClinicalTrials.gov / AACT | Registry + results + aggregate database, free | clinicaltrials.gov |
| CCDI Hub | 40 multimodal paediatric/AYA studies | ccdi.cancer.gov |

### Sources
- https://www.fda.gov/drugs/cancer-approvals/ongoing-cancer-accelerated-approvals (FDA, ongoing accelerated approvals — accessed Nov 2026; entries dated Sep–Nov 2026)
- http://www.fda.gov/drugs/cancer-approvals/fda-approves-gedatolisib-fulvestrant-or-without-palbociclib-hr-positive-her2-negative-locally (FDA, 14 Jul 2026)
- https://jadpro.com/education/fda-focus/ (JADPRO FDA Focus, 2026 approvals list)
- https://preview.aclanthology.org/ingest-lrec/2026.eacl-demo.26.pdf (CLINICALTRIALSHUB, EACL 2026 — 543,172 all studies)
- https://en.wikipedia.org/wiki/ClinicalTrials.gov (444,000+ trials, 221 countries)
- https://intuitionlabs.ai/pdfs/public-biomedical-datasets-2026.pdf (Public Biomedical Datasets 2026, 1 Aug 2026 — SEER coverage/fees, All of Us vs UK Biobank)
- https://www.who.int/observatories/global-observatory-on-health-research-and-development/resources/databases/databases-on-processes-for-r-d/clinical-trials (WHO ICTRP — stale "300,000" figure, do not use as current)
- https://scienmag.com/cancer-interception-trials-are-hiding-in-plain-sight-on-clinicaltrials-gov/ (15 Oct 2026, Frontiers in Epidemiology landscape)

### Gaps / could not verify
- No verified total count of FDA oncology approvals for 2025 or for 2026 year-to-date was established; the FDA pages list approvals individually. Do not quote a yearly total.
- ClinicalTrials.gov counts differ across sources by date/method; the spread (345k–543k) is documented above rather than resolved to one number.
- NCI's total budget / CCDI funding levels were not researched in this run.

---

## Cross-cutting notes for the programme

1. **The honest model is controlled/federated, not open-download.** UK Biobank (RAP, 2024), All of Us (Workbench, user-borne compute), TCGA controlled data (dbGaP) and GA4GH data-visiting all point the same way — and openSNP's Apr 2025 closure (data deleted) is the cautionary tale for any proposed Genomic DAO (S27, proposed) that imagines CC0 individual genomes. Frame S27/S28 as consent-gated, federated, GA4GH-aligned — not as open data.
2. **The honest IP model is DAO-governed licensing, not open IP.** Molecule/Bio Protocol/VitaDAO/AthenaDAO all keep the IP itself owned and licensed; what is open is the governance, the contracts, and (sometimes) the data. IPTs carry governance/information rights with no guaranteed return. Any proposed BioDAO (S18, proposed) should copy that distinction, not blur it.
3. **Governance is thinning in the BioDAO cohort.** VitaDAO (no Snapshot proposal since 9 Sep 2025) and AthenaDAO (none since Sep 2025) both show a pause in on-chain voting even as their science/equity vehicles continue. Curetopia shows no findable voting venue at all. Do not present BioDAO governance as currently active without a fresh check.
4. **Compound data has a clean open stack — with one trap.** ChEMBL (CC BY-SA 3.0, v37, 1 May 2026) + PubChem (public domain, ~124M compounds, Oct 2026) are safe foundations for AGI Compounds, with source/version/date attribution. DrugBank (CC BY-NC 4.0, academic downloads paused Jun 2026) is the trap: do not build a commercial compound product on it without a commercial licence.
5. **ALS has a genuinely open flagship to build beside, not duplicate.** Answer ALS / Neuromine (full release 3 Nov 2025; 1,100+ participants, 150+ TB, 2,500+ profiles with ARC) plus Project MinE's open Data Browser (v1.7, 14 Oct 2026) are the resources an ALS compound agent should cite and, where permitted, query — not re-collect. No treatment claims attach to any of it.
6. **Cancer has the deepest open data, but the counts move.** TCGA (~2.5 PB, 11,000+ patients, 33 types) via the GDC (44,637 cases across 22 programmes) is the anchor; SEER (~45.9% US coverage, since 1973) is the registry anchor. Quote each with its date and access tier (open vs dbGaP-controlled).

## What was NOT done
- No live site tree was edited; no push, deploy, publish, email or share.
- No contact was made with any DAO, biobank, institute or company.
- No medical, treatment, diagnostic or cure claim is made anywhere in this file.
- Figures marked secondary or conflicting above were not resolved to a single number; they are flagged for a follow-up check before any public use.
