# Bio Research Expansion — GitHub Repo List

Research date: 2026-11-07. Source of truth: GitHub repo search via the connected GitHub MCP
(`search_repositories`, plus `get_file_contents` / `list_commits` spot-checks). "Last activity"
is the repo's `updated_at` as returned by GitHub search on 2026-11-07. Licenses were read
from the repo's LICENSE file where stated; "unknown" means not verified in this pass, not
a guess. Nothing here was invented — if a repo could not be found, that is recorded.

---

## 1. Wild Animal Voice Engine / WAVETranslator

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/WAVETranslator/Wild-Animal-Voice-Engine | The WAVE project repo. Description: "Wave: Wild Animal Voice Engine — Developed on the Virtual Protocol to help train robots to become translators of all Species" | MIT | 2026-07-14 | **STUB — confirmed** |

**Stub verification (done by hand, not assumed):** the repo contains exactly 3 files —
`.gitignore` (263 B), `LICENSE` (MIT, 1,071 B), `README.md` (154 B, two lines only).
One commit ever: "Initial commit", 2026-06-13. 1 star, 1 fork. There is **no code, no
model, no site source** in it. It is NOT the source of bioacoustics.cloud or any WAVE product.

No other WAVETranslator / Wild Animal Voice Engine repo was found. (Note: a GitHub search
for the string "WAVETranslator" itself returned 0 repos, even though the repo above
exists — search indexing quirk; the repo URL above was confirmed directly.)

## 2. BirdNET (official — Cornell K. Lisa Yang Center for Conservation Bioacoustics)

Org: `birdnet-team`.

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/birdnet-team/BirdNET-Analyzer | BirdNET analyzer for scientific audio data processing (Python) | MIT | 2026-11-06 | Original, active (1,743 stars) |
| https://github.com/birdnet-team/birdnet | Python library for identifying bird species by sound | MIT (`LICENSE.md`) | 2026-11-06 | Original, active (167 stars) |
| https://github.com/birdnet-team/birdnet-live-app | Official BirdNET mobile app (Flutter/Dart) | unknown | 2026-11-06 | Original, active (77 stars) |
| https://github.com/birdnet-team/BirdNET-Lite | TFLite version of BirdNET (>6,000 species) | unknown | 2026-10-15 | Original, **archived** |
| https://github.com/birdnet-team/BirdNET-V1 | Original soundscape analysis (Theano/Lasagne era) | unknown | 2026-08-24 | Original, **archived** |
| https://github.com/tphakala/birdnet-go | Community self-hosted realtime soundscape analyser (Go, Raspberry Pi) | unknown | 2026-11-07 | Original (community, not Cornell), very active (2,408 stars) |

## 3. Google Perch

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/google-research/perch | Official Perch bioacoustics model code (Google Research) | Apache 2.0 | 2026-11-06 | Original, active (403 stars) |
| https://github.com/google-research/perch-hoplite | Tooling for agile modeling on large machine-perception embedding databases | unknown | 2026-11-02 | Original, active (132 stars) |

**Not found:** no Perch repo under `google-deepmind` (search returned 0). Third-party
PyTorch ports exist but are unofficial, e.g. `bghani/perchv2-pytorch` (7 stars,
updated 2026-09-27) and `matijama/perch-v2-pytorch` (1 star, updated 2026-10-05) —
use only with a clear "unofficial port" label.

## 4. NatureLM

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/earthspecies/NatureLM-audio | Official NatureLM-audio repo from the Earth Species Project (the animal-communication audio model) | MIT | 2026-11-01 | Original, active (108 stars) |
| https://github.com/earthspecies/naturelm-audio-demo | Demo for NatureLM-audio | unknown | 2026-10-28 | Original (7 stars) |
| https://github.com/NatureLM/NatureLM.github.io | Project website only (no code) | unknown | 2025-11-06 | Original, website (6 stars) |

No public NatureLM repo exists outside the Earth Species Project org. The main
`NatureLM-audio` repo's contents beyond its license were not fully inspected in this pass.

## 5. BioDAO / Molecule

Org: `moleculeprotocol` (27 public repos). There is **no repo actually named "BioDAO"**
in the Molecule org, and no official BioDAO org repo was found — a search for "BioDAO"
returns only small, old, unrelated or third-party repos.

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/moleculeprotocol/IPNFT | IP-NFT smart contracts — the core DeSci building block for tokenising research IP | MIT | 2026-10-14 | Original, active (46 stars) |
| https://github.com/moleculeprotocol/biodao-bible | BioDAO "bible" docs site (Docusaurus) | unknown | 2023-04-29 | Original, stale (1 star) |
| https://github.com/moleculeprotocol/docs | Molecule docs | unknown | 2026-11-05 | Original, active (3 stars) |
| https://github.com/moleculeprotocol/elgora-contracts | Elgora escrow smart contracts | unknown | 2026-11-06 | Original, active (0 stars) |
| https://github.com/moleculeprotocol/mol-labs-plugin | Molecule Labs agent plugin (MCP tools + skills) | unknown | 2026-08-24 | Original (0 stars) |

Related (BIO Protocol, incubated by Molecule), org `bio-xyz` (23 repos):

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/bio-xyz/BioAgents | AI-scientist framework for autonomous deep research in biology | unknown | 2026-11-07 | Original, **archived** (185 stars) |
| https://github.com/bio-xyz/BioAgentsEliza | Agentic framework for scientific research/analysis | unknown | 2026-03-19 | Original (35 stars) |
| https://github.com/bio-xyz/tokenLists | ERC-20 token lists for the bio.xyz ecosystem (incl. BioDAO governance tokens) | unknown | 2026-02-07 | Original (3 stars) |
| https://github.com/bio-xyz/vesting-contracts | Vesting contracts | unknown | 2026-05-14 | Original (2 stars) |

Bottom line: BioDAOs run on Molecule/BIO shared contracts (IP-NFT, token/vesting);
individual BioDAOs generally do not have their own code repos.

## 6. VitaDAO

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/VitaDAO/VitaDAO-contracts | VitaDAO smart contracts | MIT-style (`LICENSE.md`, © 2021 VitaDAO) | 2026-10-23 | Original, active (16 stars) |
| https://github.com/VitaDAO/VitaDAO-dapp | VitaDAO dApp | unknown | 2026-10-23 | Original, active (11 stars) |
| https://github.com/VitaDAO/vitadao-global | Member-benefits / holdings overview app | unknown | 2026-10-22 | Original, **archived** (3 stars) |

## 7. AthenaDAO and other real DeSci / bio DAOs

| DAO / Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| AthenaDAO — **no official public repo found** | Real DAO (women's health, BIO network, token ATH, founded 2022). GitHub search for "AthenaDAO" returns 1 result only: `DeSciWorldDAO/dashboard-AthenaDAO`, a third-party dashboard (0 stars, updated 2023-01-27). Web sources confirm the DAO exists; no code repo exists publicly. | — | — | **Not found (repo)** |
| HairDAO — **no official org repo found** | Real DAO (hair-loss research, BIO network). Only community/dashboard repos found, e.g. `DeSciWorldDAO/dashboard-hairdao` (updated 2022-11-04) and `apbakst/hairdao-content-dashboard-` (updated 2026-01-30). | — | — | **Not found (official repo)** |
| CryoDAO — **no repo found** | Real DAO (cryopreservation, BIO network) per web sources. GitHub search for "CryoDAO" returns 0 repos. | — | — | **Not found** |
| ValleyDAO — **no official org repo found** | Real DAO (synthetic biology, BIO network). Only `DeSciWorldDAO/dashboard-valleydao` (updated 2025-08-28) and small community forks. | — | — | **Not found (official repo)** |

CerebrumDAO, PsyDAO and Curetopia were not searched in this pass. Note the pattern:
most BioDAOs have no public code repo of their own — their on-chain logic lives in the
shared Molecule / BIO Protocol contracts listed in §5.

## 8. Genomic tooling (GA4GH and open genomics)

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/ga4gh/vrs-python | GA4GH Variation Representation, Python implementation | Apache 2.0 | 2026-11-05 | Original, active (66 stars) |
| https://github.com/ga4gh/phenopacket-schema | GA4GH Phenopacket schema (phenotype + genomic data exchange) | unknown | 2026-11-06 | Original, active (103 stars) |
| https://github.com/ga4gh/ga4gh-schemas | Original GA4GH models/APIs | unknown | 2026-07-15 | Original, **retired 2018-01-24, archived** (220 stars) |
| https://github.com/ga4gh/ga4gh-server | Reference implementation of the retired APIs | unknown | 2026-07-15 | Original, **retired 2018-01-24, archived** (98 stars) |
| https://github.com/ga4gh-beacon/specification | GA4GH Beacon specification (genomic data discovery) | unknown | 2025-11-19 | Original, **archived** (33 stars) |

## 9. Compound-library / cheminformatics tooling

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/rdkit/rdkit | RDKit — the standard open-source cheminformatics library | BSD 3-Clause | 2026-11-07 | Original, very active (3,672 stars) |
| https://github.com/rdkit/rdkit-js | RDKit for JavaScript (molecule rendering + toolbelt) | unknown | 2026-11-04 | Original, active (257 stars) |
| https://github.com/rdkit/rdkit-tutorials | RDKit tutorials | unknown | 2026-11-02 | Original, active (316 stars) |
| https://github.com/chembl/chembl_webresource_client | Official Python client for the ChEMBL API (EMBL-EBI) | Apache 2.0 | 2026-10-22 | Original, active (453 stars) |
| https://github.com/chembl/ChEMBL_Structure_Pipeline | ChEMBL database structure pipelines | unknown | 2026-10-25 | Original, active (251 stars) |
| https://github.com/mcs07/PubChemPy | Python wrapper for the PubChem PUG REST API | MIT | 2026-11-03 | Original, active (518 stars) |

## 10. ALS research tooling

**No major dedicated ALS research repo exists on GitHub.** What exists is small,
individual/academic analysis code — no ALS equivalent of cBioPortal or RDKit.

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/iamjli/AnswerALS_QTL | eQTL/caQTL analyses for Answer ALS data (academic) | unknown | 2025-04-25 | Original, small (2 stars) |
| https://github.com/SOCR/ALS_PA | ALS Predictive Analytics (UCLA SOCR) | unknown | 2023-12-11 | Original, stale (5 stars) |
| https://github.com/JPLeRouzic/ALS-biomarkers | Biomarker analysis using the PRO-ACT ALS database | unknown | 2024-08-26 | Original, small (2 stars) |
| https://github.com/charlottebensaid/Projet-SLA-Data | Student ML project on ALS progression using PRO-ACT | unknown | 2026-07-01 | Original, small (0 stars) |

**Not found:** no public repo for Project MinE (ALS genomics consortium) — search
returns unrelated repos. PRO-ACT itself is a clinical-trial database, not a repo;
only small downstream analysis projects reference it. ALS data access is via
controlled-access datasets (Answer ALS, PRO-ACT), not open code.

## 11. Cancer genomics tooling

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/cBioPortal/cbioportal | cBioPortal for Cancer Genomics (main platform) | Apache 2.0 | 2026-11-06 | Original, active (1,064 stars) |
| https://github.com/cBioPortal/cbioportal-frontend | React frontend of cBioPortal | unknown | 2026-11-06 | Original, active (152 stars) |
| https://github.com/cBioPortal/datahub | Curated public cancer datasets for cBioPortal | unknown | 2026-11-05 | Original, active (218 stars) |
| https://github.com/cBioPortal/cbioportal-docker-compose | Run cBioPortal via Docker Compose | unknown | 2026-10-29 | Original, active (23 stars) |
| https://github.com/BioinformaticsFMRP/TCGAbiolinks | R/Bioconductor toolkit for TCGA data access/analysis | unknown | 2026-10-19 | Original, active (357 stars) |
| OpenTargets platform | Main platform repo not confirmed in this pass — search surfaced only `opentargets-archive/*` (archived) and an unofficial MCP server (`Augmented-Nature/OpenTargets-MCP-Server`, 11 stars). Do not cite a platform repo URL without verifying it separately. | unknown | — | **Not verified** |

## 12. AGIFutureFoundation's own bio-related repos

Org has 66 public repos (search `org:AGIFutureFoundation`, 2026-11-07). Bio-related ones:

| Repo | What it is | License | Last activity | Status |
|---|---|---|---|---|
| https://github.com/AGIFutureFoundation/bioacoustics-cloud | **Static website source for bioacoustics.cloud** (WAVE). 10 entries: `index.html` (25 KB), `script.js`, `styles.css`, `world/` dir. README: "Static site for the WAVE bioacoustics platform. Content migrated from the live Vercel-hosted site. Pure HTML + CSS + JS, no build step." TODOs include wiring the contact form and filling placeholder social links. NOT a model or engine — the site only. | unknown | 2026-11-04 | Original, site source |
| https://github.com/AGIFutureFoundation/bioacoustics-cloud-pages | bioacoustics.cloud regenerated as a Cloudflare Pages static site (WAVE) | unknown | 2026-11-06 | Original, site source |
| https://github.com/AGIFutureFoundation/AGI-Biotech-tool | "biodao.blockchain" — a molecular workspace for drug discovery (VR/browser, in the spirit of Nanome): pick up a protein, dock compounds, score fit. Wired to live public databases + the AGI compound collection. Focus: neurogenetic targets — ALS, Parkinson's, Shriners Children's conditions. Runs locally; sign-in/payments/on-chain anchoring optional. | unknown | 2026-10-12 | Original, app (not a stub — has real code/docs incl. `AGENT_TRAINING_COMPLETE.md`) |
| https://github.com/AGIFutureFoundation/toxicology | "Toxicology tools to monitor and advise ecology programs cleaning up federal super sites like the one in Hunter[s Point]" | unknown | 2026-07-11 | Original (no language detected — likely docs/early) |
| https://github.com/AGIFutureFoundation/wave-site | WAVE site repo (empty description) | unknown | 2026-11-04 | Original, site |
| https://github.com/AGIFutureFoundation/wave.agifuturefoundation.org | WAVE site (agifuturefoundation.org subdomain) | unknown | 2026-11-07 | Original, site |

**Honesty note for §12:** none of the org's bio repos is the Wild Animal Voice Engine
source. The engine repo (`WAVETranslator/Wild-Animal-Voice-Engine`, §1) is a 3-file
stub in a separate org. The org's bio work is: two static-site repos for
bioacoustics.cloud, one drug-discovery workspace app (`AGI-Biotech-tool`), one
toxicology repo, and WAVE site mirrors.

---

## What was NOT found (summary)

- **No public repo for the WAVE engine itself** — only the 3-file MIT stub (§1).
- **No official Perch repo under google-deepmind** — only `google-research/perch`.
- **No official BioDAO repo** — no repo named BioDAO in `moleculeprotocol` or elsewhere official; BioDAOs share Molecule/BIO contracts.
- **No official public repo for AthenaDAO, HairDAO, CryoDAO, or ValleyDAO** — the DAOs are
  real (per web sources) but have no own code repos; only third-party dashboards exist.
- **No Project MinE repo; no major ALS research repo** — only small academic/student
  analysis projects and PRO-ACT downstream code.
- **OpenTargets main platform repo not verified** in this pass.
- **No NatureLM repo outside Earth Species Project.**
