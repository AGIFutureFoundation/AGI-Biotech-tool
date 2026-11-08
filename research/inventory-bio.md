# Bio References Inventory — Mike's computer (read-only sweep)

**Built:** 2026-11-07 (evening PST), by the bio-research inventory worker. **Read-only task: nothing was edited, pushed, deployed, published, or sent during the inventory sweep.** Published in this repo's `research/` folder as a research brief.
**Scope searched:** `~/workspace`, `~/memory`, `~/workspace/user/files`, site trees under `~/workspace/your_files/hostinger-email/sites/`, plus the staged articles, agent sites, WAVE/Fellowship/Foundation trees, `~/workspace/your_files/bio-research-expansion/`, interactive builds, homepage redesigns, org wikis, corporate paperwork, worlds-3d, and the Gmail cache.
**Method:** `grep -ri` (case-insensitive, files-with-matches) per term. Counts below = **files containing the term**, not mention counts. "ALS" was matched with word boundaries (`\bALS\b`) so "also" etc. are excluded; remaining ALS hits are the ALS Researcher agent / $ALS token / amyotrophic lateral sclerosis. "Perch" hits were context-checked: every bio-area hit is Google's Perch model (no fish/perch-seating false positives found in the counted files).
**Terms:** bioacoustics, biodao, biota, genomic, genome, compound, cancer, ALS, birdnet, perch, naturelm, xeno-canto, macaulay, watkins, cetacean, curable, biopharma.
**Duplicates warning:** large parts of the hit counts are mirrors — `~/workspace/goals/*/files/` holds copies of the same site trees and corporate paperwork, `~/workspace/self_improvement/staging/` holds MEMORY.md snapshots, and `~/workspace/email/gmail/` is a hashed cache of Gmail messages. Mirror counts are reported separately (§10) and NOT double-counted as new content.

## 0. This program's own staging dir — `~/workspace/your_files/bio-research-expansion/`

Did not exist at the start of this sweep; the bio coordinator created three research files during it (timestamps Nov 8 00:28 VM clock). Read, not edited, here.

- `githubs.md` (189 lines) — GitHub repo list researched 2026-11-07 via GitHub search: WAVETranslator Wild-Animal-Voice-Engine confirmed a 3-file stub (no code/model/site source); BirdNET official + community repos; Google Perch; NatureLM; Bio Protocol / BioDAO / Molecule; ALS/cancer research orgs.
- `research-wave.md` (284 lines) — WAVE/bioacoustics findings via web search + Firecrawl scrapes: verified figures BirdNET v2.4 6,522 species (Mar 2025) / V3.0 11,000+ (June 2026), Perch 2.0 14,795 classes, Xeno-canto 1,111,111 recordings, Macaulay 3.2M+ audio, Watkins ~2,000 recordings, NatureLM-audio 26.4M pairs, Project CETI 156-coda alphabet.
- `research-biodao-genomic-als-cancer.md` (343 lines) — BioDAO/Molecule IP-NFT + Lab (V3) research, Bio Protocol/BIO token, AGI Compounds = ALS agent compound library, ALS + cancer research sections; explicit honesty scope (no diagnosis/treatment/cure claims; W3 series proposed not formed).
- `inventory-bio.md` — this file.

## 1. Counts per term, by area (files containing the term)

| Term | Staged articles | WAVE regen (bioacoustics.cloud) | Agent sites (wave+als) | Foundation site | Interactive builds | Memory | Gmail cache |
|---|---|---|---|---|---|---|---|
| bioacoustics | 13 | 47 | 4 | 14 | 5* | 17 | 69 |
| biodao | 5 | —† | 0 | 44 | 0 | 7 | 0 |
| biota | 5 | —† | 0 | 48 | 0 | 10 | 0 |
| genomic | 0 | —† | 0 | 39 | 0 | 6 | 0 |
| genome | 1 | —† | 0 | 34 | 0 | 3 | 0 |
| compound | 8 | —† | 16 | 13 | 5* | 7 | 0 |
| cancer | 2 | —† | 1 | 12 | 0 | 6 | 0 |
| ALS (word-boundary) | 24 | 0‡ | 20 | 15 | 7 | 6 | 0 |
| birdnet | 8 | 43 | 3 | 1 | 2* | 3 | 0 |
| perch | 4 | 22 | 0 | 4 | 0 | 4 | 1 |
| naturelm | 7 | 22 | 3 | 4 | 0 | 4 | 1 |
| xeno-canto | 9 | 11 | 6 | 0 | 2* | 4 | 0 |
| macaulay | 9 | 11 | 6 | 0 | 2* | 4 | 0 |
| watkins | 10 | 43 | 6 | 1 | 1* | 4 | 0 |
| cetacean | 1 | 2 | 1 | 0 | 0 | 0 | 0 |
| curable | 0 | —† | 0 | 32 | 0 | 7 | 0 |
| biopharma | 1 | —† | 0 | 25 | 0 | 7 | 0 |

\* Interactive-builds counts are file lists, not per-term counts — see §6 for the exact files.
† Not separately counted per term in the WAVE regen (WAVE-focused tree; combined-pattern hits are the blog/index/agent-skills files listed in §3).
‡ ALS count 0 in the regen is from the combined per-term loop scope; the regen is WAVE-only and contains no ALS agent content by inspection of its file list.
Memory counts include `~/memory/bank/` (experience/opinions/reflections/world.md); daily-note files matching are 2026-10-24→2026-11-07 (14 files).
**No term is zero everywhere.** Per-area zeroes: genomic + curable in staged articles; biodao/biota/genomic/genome/perch/curable/biopharma in agent sites; xeno-canto/macaulay/cetacean in the Foundation site; cetacean in memory; biodao/biota/genomic/genome/compound/cancer in the Gmail cache.

## 2. Staged articles — `~/workspace/your_files/agifuturefoundation-articles/` (read-only; publish coordinator active here)

### als/ (3 articles + charts) — the ALS / compound-library core
- `als/als-01-what-a-compound-library-is.md` — explains compound libraries (incl. natural-product libraries; cancer drugs cited as an example class) as the ALS Researcher agent's product.
- `als/als-02-from-compound-to-treatment.md` — the long road from a compound to a treatment; ALS drug-development context.
- `als/als-03-als-research-field.md` — the ALS research field itself (disease, research landscape).
- `als/assets/charts/als-jobs-by-price.svg` — chart of the 6 ALS ACP jobs by price (compound_* jobs).
- ALS (24 files incl. MANIFEST.md + chart SVGs in other families that list the $ALS agent in the family catalog).

### biota/ (3 articles + charts)
- `biota/biota-01-counting-life.md` — Biota as a forest-biome world (anchored South Atlantic -38.713, -27.248; 36 nodes, 6 zones incl. Personalized Therapy Lab, Biopharma AGI Agents Hub); names BioDAO (S18) in the series context; ALS Researcher + CMMC appear as in-world agent companions.
- `biota/biota-02-listening-to-the-ocean.md` — ocean bioacoustics; cites BirdNET, Watkins database, Xeno-canto/Macaulay archives.
- `biota/biota-03-the-living-twin.md` — the "living twin" concept; compound + ALS mentions (agent companion / catalog context).
- `biota/assets/charts/w3-series-by-category.svg` — 33-series chart (Biota has no series number — noted gap).

### wave-bioacoustics/ (3 articles + charts) — the bioacoustics core
- `wave-bioacoustics/wave-bioacoustics-01-reef-soundscapes.md` — reef soundscapes; framing para: live predictor is BirdNET (11,000+ platform / 6,522 in v2.4 Mar 2025), Perch/NatureLM NOT connected, marine classification is Watkins cross-reference only, WAVETranslator repo is a stub, no reef-diagnosis claim.
- `wave-bioacoustics/wave-bioacoustics-02-forest-alarm-system.md` — forest acoustic threat detection; same BirdNET/Perch/NatureLM framing; threat detection credited to Rainforest Connection et al., not WAVE.
- `wave-bioacoustics/wave-bioacoustics-03-frog-chorus-census.md` — frog chorus census; same framing; frog ID credited to FrogID (Australian Museum).
- `wave-bioacoustics/assets/charts/archive-sizes.svg` — open-archive sizes chart (Xeno-canto ~1.04M as of Nov 2026 per Mike's decision, Macaulay 3.2M, Watkins).

### wave-agent/ (3 articles + charts)
- `wave-agent/wave-agent-01-animal-voice-dataset.md` — animal-voice datasets; Project CETI / Cetacean Translation Initiative (156 codas, 2024 study), Watkins as historical counterpart (7 decades of recordings); BirdNET/NatureLM/archive figures.
- `wave-agent/wave-agent-02-species-identification-by-sound.md` — species ID by sound; BirdNET, Perch/NatureLM, archives.
- `wave-agent/wave-agent-03-acoustic-monitoring-conservation-evidence.md` — acoustic monitoring for conservation evidence; BirdNET/archives; ALS appears only via the family-catalog chart.
- `wave-agent/assets/charts/open-archive-sizes.svg` — same archive-size chart as wave-bioacoustics.

### cognition-x / empathic-x / diagnostic-x — almost no bio content
- `diagnostic-x/diagnostic-x-01-screening-vs-diagnosis.md` — cancer appears once only: cervical cancer screening as the classic example of screening done as a programme.
- `empathic-x/empathic-x-02-empathy-as-a-skill-how-it-works-and-how-it-is-learned.md` — "genome" appears once only: twin studies / genome-wide study on heritability of empathy (~28% genetics).
- `cognition-x/` — zero hits for any term in this sweep.
- `omega/omega-02-stewardship-and-governance.md` — "compound" appears (governance context, not the compound library).
- `MANIFEST.md` — the articles manifest; records the BirdNET/Perch/NatureLM framing, the Macaulay 2.7M (Mar 2025) vs 3.2M figure tension, and word counts.
- `publish-staging/smartciti-x/*.html` (3 files) — bioacoustics/biodao appear only in a shared footer/nav catalog listing, not as content.

## 3. WAVE site — `~/workspace/your_files/hostinger-email/sites/bioacoustics.cloud-regen/` (96 files, local regen of bioacoustics.cloud)

The densest bioacoustics concentration on the machine. 30 blog posts + index/soundmap/translate pages + agent skills + ai-catalog.
- `index.html` — WAVE homepage; "Cetacean" appears here (and in `llms.txt`); BirdNET as live predictor; Perch/NatureLM not connected.
- `blog/birdnet-and-the-democratization-of-bioacoustics/index.html` — BirdNET deep dive.
- `blog/foundation-models-for-nature/index.html` — "what NatureLM and Perch really promise"; Perch + NatureLM as foundation models for animal sound.
- `blog/reef-soundscapes/index.html`, `blog/forest-alarm-system/index.html`, `blog/frog-chorus-census/index.html`, `blog/listening-to-the-ocean/index.html` — mirror the staged wave-bioacoustics articles (BirdNET/Watkins framing).
- `blog/how-a-species-classifier-is-trained/index.html`, `blog/how-wave-decodes-animal-communication/index.html`, `blog/the-data-landscape-of-animal-translation/index.html`, `blog/can-we-really-translate-animals/index.html` — classifier training, animal-translation status, archive landscape (Xeno-canto, Macaulay, Watkins, CETI).
- `blog/the-hydrophone-the-instrument-that-opened-the-ocean/index.html`, `blog/the-cocktail-party-problem-underwater/index.html`, `blog/the-infrasonic-world-of-elephants/index.html`, `blog/bats-and-the-ultrasonic-frontier/index.html`, `blog/the-vanishing-chorus-insects-and-the-quiet-crisis/index.html`, `blog/soundscape-ecology-reading-a-whole-habitat/index.html`, `blog/passive-acoustic-monitoring-explained/index.html`, `blog/acoustic-monitoring-and-the-future-of-protected-areas/index.html`, `blog/a-short-history-of-listening-to-animals/index.html`, `blog/dialects-in-the-wild/index.html`, `blog/dialects-culture-and-the-question-of-animal-tradition/index.html`, `blog/do-animals-have-names-signature-calls-and-individual-identity/index.html`, `blog/edge-ai-in-the-field/index.html`, `blog/from-recording-to-insight-a-fieldworkers-workflow/index.html`, `blog/sound-as-shape-geometry-of-communication/index.html`, `blog/the-base-rate-problem-why-rare-species-fool-detectors/index.html`, `blog/the-ethics-of-listening-to-wild-animals/index.html`, `blog/what-a-spectrogram-really-shows/index.html`, `blog/the-hydrophone...` (see list) — full 30-post blog; most carry Watkins/BirdNET/archive mentions in body or related-links blocks (hence Watkins 43 files, BirdNET 43 files — near-site-wide).
- `.well-known/agent-skills/{acoustic-fingerprint,identify-species,search-archives}.md` + `ai-catalog.json` + `agent.json` — WAVE agent skills (species ID, archive search) and catalog.
- `soundmap/index.html`, `translate/index.html` — Sound Map + Translator pages (live site's flagship features; regen notes the Translator/Sound Map need a model backend and cannot work statically).
- `README-DEPLOY.md` — deploy notes for the regen (Cloudflare Pages preview; live site is Kylon Next.js on Vercel).

## 4. Agent sites — `~/workspace/your_files/hostinger-email/sites/agents/` (wave + als; omega/cmmc/tactile have no bio terms)

### agents/als/ — ALS Researcher ($ALS), "Developing a Synthetic Compound Library"
- `agent.json` — name ALS Researcher; 6 jobs + 1 sub (compound_library_snapshot $10/24h, compound_research_report $25/48h, compound_data_access $50/24h, compound_lookup $2/30min, library_growth_report $15/48h, compound_screening_pack $150/72h; library_weekly $25/30d); token $ALS, Base, mcap $3.6K, 1 holder, not graduated; status as of 2026-11-06, 0 jobs completed, $0 earned, offline (no instance deployed).
- `index.html`, `jobs.html`, `about.html`, `hire.html` — homepage + full ACP catalog at real prices + offline honesty note ("not currently online to receive or deliver hires").
- `articles/what-a-compound-library-is.html`, `articles/from-compound-to-treatment.html`, `articles/als-research-field.html` — the staged ALS articles as site pages (cancer mentioned once, natural-product cancer drugs).
- `.well-known/ai-catalog.json`, `.well-known/agent-skills/{hire-on-virtuals,read-agent-facts,read-agent-pages,token-facts}.md`, `llms.txt`, `auth.md` — machine-readable catalog/skills; compound-job names throughout.
- Live state (per `~/workspace/your_files/omega-hive-live/ACP_PUBLIC_STATE_2026-11-06.md`): ALS site live at als.agifuturefoundation.org (200); 29 jobs + 6 subs verified live in Virtuals ACP 2026-11-06; instances offline, no hire fulfillable.

### agents/wave/ — WAVE ($WAVE), "WAVE : Wild Animal Voice Engine"
- `agent.json` — 6 jobs + 1 sub (species_identification $5/30min, animal_voice_dataset $25/48h, continuous_animal_voice_access $50/24h, sound_clip_id $1/5min, species_acoustic_profile $15/24h, expedition_sound_map $100/72h; field_listener $30/30d); token $WAVE, not graduated; offline as of 2026-11-06.
- `index.html`, `jobs.html`, `about.html`, `hire.html` — homepage + catalog + offline note; WAVE homepage shows no animal-data claims (name only) per memory 2026-11-06.
- `articles/animal-voice-dataset.html`, `articles/species-identification-by-sound.html`, `articles/acoustic-monitoring-conservation-evidence.html` — staged wave-agent articles as site pages (CETI/cetacean, Watkins, BirdNET, NatureLM, Xeno-canto, Macaulay).
- `.well-known/ai-catalog.json`, `.well-known/agent-skills/*.md`, `llms.txt`, `auth.md` — catalog/skills.
- Note: a SECOND WAVE agent (no token, Pro) exists in Virtuals with the same name/description; it has no repo/site — duplicate-naming decision still open (memory 2026-11-06/07).

## 5. Foundation site — `~/workspace/your_files/hostinger-email/sites/agifuturefoundation.org/`

Bio-series pages + articles; "still undefined" honesty labels on the bio series. (Counts are html/md/txt/json only; videos excluded.)
- `articles/article-05-curable-x.html` — "Curable.X — Curative, Treatment-Focused Work, Still Undefined".
- `articles/article-06-biopharma-go.html` — "BioPharma.Go — Biopharmaceutical Work, Still Undefined".
- `articles/article-07-molecular.html` — Molecular series article.
- `articles/article-10-curable-blockchain-dao.html` — Curable.Blockchain DAO.
- `articles/article-11-biodao-blockchain.html` — "BioDAO.blockchain DAO — Biology, Bioacoustics, and a Shared Ledger".
- `articles/article-12-genomic-dao.html` — "Genomic DAO — Consent, Privacy, and Shared Benefit for Genomic Data".
- `articles/article-13-genome-blockchain.html` — "Genome.Blockchain — A Verifiable Record Layer for Genomic Data".
- `series/S04-curable-x.html`, `series/S05-biopharma-go.html`, `series/S18-biodao-blockchain.html`, `series/S27-genomic-dao.html`, `series/S28-genome-blockchain.html` — the five bio-series pages (S4/S5/S18/S27/S28).
- `series/S11-molecular.html` — Molecular series page (ALS appears here).
- `series/S03-diagnostic-x.html`, `series/S14-askdoc-x.html`, `series/S17-curable-blockchain-dao.html`, `series/S08-locator-x.html` — neighbouring health-series pages carrying bio terms.
- `projects/biodao-tools.html` — BioDAO tools project page.
- `projects/agi-corp.html`, `projects/agi-fellowship.html`, `projects/index.html`, `projects/insidr-w3llc.html`, `projects/metropolis-smartciti.html`, `projects/plaudguard-ai.html`, `projects/rp1-ecosystem.html`, `projects/worldforge.html`, `projects/fiduciary-corporate-shield.html` — project pages mentioning bio series in catalogs/lists.
- `features/feature-01-the-wave.html` — "The WAVE — Listening to the Earth" feature.
- `features/feature-02-biotech-swarm.html` — "The Biotech Swarm" feature.
- `features/feature-03-flow-zone.html`, `feature-06-worlds-on-real-maps.html`, `feature-10-agents-operate-people-govern.html`, `feature-21-the-proof-is-the-product.html` — features mentioning bio terms (catalog/agent context).
- `articles/category-2-health-life-sciences.html`, `articles/category-3-metaverse-spatial.html`, `articles/index.html` — category/index pages listing the bio articles.
- `articles/article-66-counting-life.html`, `article-67-listening-to-the-ocean.html`, `article-68-the-living-twin.html` — Biota articles as site pages.
- `articles/article-52-empathy-as-a-skill-how-it-works-and-how-it-is-learned.html` — the genome-wide-study empathy article (genome hit).
- `articles/article-54-screening-vs-diagnosis.html` — the cervical-cancer-screening article (cancer hit).
- `articles/article-04-diagnostic-x.html`, `article-09-askdoc-x.html`, `article-14-locator-x.html`, `article-15-avatar-chat-dao.html`, `article-16-metaverse-dao.html`, `article-17-worldforge.html`, `article-18-rp1-ecosystem.html`, `article-19-get-delivery-dao.html`, `article-20-robotics-dao.html`, `article-21-aerospace-dao.html`, `article-22-blockchain.html`, `article-28-plaudguard-ai.html`, `article-32-agi-corp.html`, `article-43-lyka-dao.html` — articles mentioning bio terms in series catalogs/cross-links.
- `BIO_VISUALS_PLAN_2026-11-06.md` — LOCAL-ONLY plan for bio-series/article illustrations (photorealistic-style editorial illustrations, AI-generated captions; no images generated, no `<img>` tags exist yet).
- `llms.txt`, `agent.json`, `ARTICLES-NOTE.md`, `FEATURES-NOTE.md`, `PHASE-3-REPORT.md`, `VIDEO-PLACEMENT.md`, `DEPLOY-NOTE-DAO-EXPANSION.md`, `DEPLOY-NOTE-ADDENDUM.md`, `DEPLOY-BINARIES-MANIFEST.md` — site notes/manifests mentioning bio series, Biota/cancer video shorts, and bio visuals.
- `investors/series-raises.html` — series-raise page (bio series in the raise list; Russell site-fix list says remove investor pages — unapproved, untouched).
- `videos/index.html`, `vr/index.html` — video hub (40 videos incl. bio shorts) and VR index mentioning bio worlds.
- Per-term gaps on this site: xeno-canto 0, macaulay 0, cetacean 0, birdnet 1, watkins 1 — the archive/model detail lives in the WAVE regen + staged articles, not on the Foundation site.

## 6. Interactive components + staged homepages

### `~/workspace/your_files/interactive-builds/` (staged only, nothing live)
- `wave-bioacoustics/archive-explorer.html` — archive explorer (8 public archives: Xeno-canto, Macaulay, Watkins, etc.).
- `wave-bioacoustics/birdnet-explainer.html` — BirdNET explainer (5-step; 11,000+ species headline, v2.4 6,522 footnote).
- `wave-bioacoustics/sound-blog-explorer.html` — sound/blog explorer.
- `wave-bioacoustics/INTEGRATION.md` — integration notes for the above.
- `wave-agent/data.js` — wave-agent component data (bioacoustics/archive terms).
- `als/job-explorer.html`, `als/hire-walkthrough.html`, `als/subscription-explorer.html`, `als/data.js`, `als/INTEGRATION.md` — ALS job/hire/subscription explorers (compound jobs at real ACP prices).
- `foundation/series-explorer.html` — 33-series explorer with verified categories (S10 in Cities not Robotics); bio series included.
- `foundation/article-explorer.html` — article explorer (bio articles listed).
- `README.md` — program README (mentions ALS + bio components).

### `~/workspace/your_files/homepage-redesign/` (staged only, 9 sites)
- `wave-bioacoustics/index.html` + `README.md` — staged WAVE homepage (5 dropdowns, verified stats, Perch/NatureLM stated not connected, forms removed, Macaulay 2.7M Mar 2025 figure — tension vs the 3.2M Nov 2026 figure Mike settled).
- `wave-agent/index.html`, `als/index.html` + `README.md` — staged agent homepages (3 dropdowns each, "Listed, not yet online" banner, featured jobs at real ACP prices).
- `foundation/README.md` — Foundation redesign notes (bio series/KPI strip).
- `omega/index.html`, `tactile/index.html`, `cmmc/index.html` — other agent homepages (bio terms only via the shared family catalog listing ALS/WAVE).

## 7. Memory — `~/MEMORY.md` + `~/memory/*.md`

Daily notes matching (14 files): 2026-10-24 → 2026-11-07. `~/memory/bank/` (experience/opinions/reflections/world.md) also matches. Key entries (one line each):
- `~/MEMORY.md` — bio-research expansion ordered 2026-11-07 ~16:23 PST (Firecrawl + GitHubs for WAVE + BioDAO/Genomic, cancer + ALS as well as bioacoustics; AGI Compounds = ALS library jobs; bio series S4/S5/S18/S27/S28; Biota + ALS have no series numbers; AURA Maternal separate); 12-hour research-lab loop ordered 2026-11-07 ~16:28 PST (cure cancer/ALS, talk to animals; hourly updates to Bino); Macaulay figure settled 3.2M+ as of Nov 2026; Xeno-canto settled ~1,040,000 as of Nov 2026 (later research file says 1,111,111 milestone — figure tension, see §11); BirdNET settled "over 11,000 species" (v2.4 6,522 footnote).
- `memory/2026-11-07.md` — bio expansion order; research-lab loop order; articles program (als/biota/wave-bioacoustics/wave-agent 3 each); interactive builds (WAVE archive explorer, ALS explorers); homepage redesign (WAVE Perch/NatureLM not connected); ACP 29 jobs + 6 subs reconciliation; ALS/WAVE agent status.
- `memory/2026-11-06.md` — bioacoustics.cloud Cloudflare zone complete (nameservers anastasia + carl, DS record, pending Mike's nameserver flip); WAVE apps finding (live predictor BirdNET, Perch/NatureLM NOT connected, marine = Watkins cross-reference only, WAVETranslator stub, Sound Map fingerprint off); Virtuals inventory (ALS Researcher $ALS + WAVE $WAVE, jobs/prices, duplicate WAVE); agent sites built/pushed; bioacoustics.cloud Pages repo complete (96 files).
- `memory/2026-11-05.md` — Foundation video set 24/25 incl. Cancer DAO short; video-enhancement wave (5 shorts incl. biota + cancer linking to series index as fallback — no dedicated series page).
- `memory/2026-11-04.md` — AGI promo shorts Batch 2/3: Cancer DAO short (bright brand template), Curable.X + BioPharma.Go shorts (Batch 3a).
- `memory/2026-11-03.md` — W3 LLC 33-series list uploaded (S4 Curable.X, S5 BioPharma.Go, S17 Curable.Blockchain DAO, S18 BioDAO.blockchain DAO, S27 Genomic DAO, S28 Genome.Blockchain; Biota NOT in the list); website review (WAVE/bioacoustics.cloud live but separate; Fellowship site live).
- `memory/2026-10-26.md` — Cancer DAO as one of 6 PBC focus-domain DAOs (Cancer, Robotics, Ecology, Climate, Education, Public Health); WorldForge Earth page "Original DAO Worlds (33)" marks Cancer Dao (Fred Hutchinson Cancer Center, Seattle) Live as a web-viewer world only (not RP1-attached); cancer-dao + biota-blockchain among first 41 WorldForge worlds.
- `memory/2026-10-24→2026-11-02.md` — early bio mentions (WAVE, BioDAO, compound library, bioacoustics) in daily logs; no standalone bio research before 2026-11-03.
- `memory/bank/*.md` — ALS + bio terms appear in the consolidated bank notes (same facts as the daily logs, duplicated).
- Per-term gaps in memory: cetacean 0 files (Project CETI is covered in articles/regen, not in memory notes).

## 8. Corporate paperwork + uploaded files — `~/workspace/your_files/corporate-paperwork/`, `~/workspace/user/files/`

- `~/workspace/user/files/W3_LLC.pdf` (3 pages, PDF dated 2026-04-03, internal printout, NOT a Wyoming SOS filing) — the 33 named W3 sub-series incl. S4 Curable.X, S5 BioPharma.Go, S17 Curable.Blockchain DAO, S18 BioDAO.blockchain DAO, S27 Genomic DAO, S28 Genome.Blockchain; Biota does NOT appear (gap).
- `corporate-paperwork/complete/30-W3-LLC-Series-Evidence-from-Upload.md` (+ copy in `per-entity/04-W3-LLC-Wyoming-Series/`) — evidence note for the W3 list above.
- `corporate-paperwork/complete/` (other bio-mentioning docs) — venture-studio / raise-structure docs naming the bio series as proposed portfolio (S4/S5/S18/S27/S28), valuations doc (SmartCiti.X first studio raise; bio series $100k–$500k each suggested, illustrative only).
- `per-entity/03-AGI-Corp-Wyoming/`, `per-entity/04-W3-LLC-Wyoming-Series/`, `per-entity/05-Delaware-Cohort-Series-LLC/` — per-entity packs mentioning the bio series as proposed/intended (no filings).
- `~/workspace/user/files/` (24 files matched the combined pattern) — almost all are ZoomInfo contacts CSVs whose match is a COMPANY name, not research: BioLegend, Biotech-CFO, Circular Genomics, Estrella Biopharma, Prana Thoracic (funder: Cancer Prevention and Research Institute of Texas). Plus `AGI_Future_Foundation_Worlds.zip` (worlds bundle incl. biota/cancer-dao worlds). No compound-library data file, no molecule file, no bio research paper in `~/workspace/user/files/`.
- `~/workspace/your_files/foundation-github-review/GITHUB_REVIEW_2026-11-05.md` — source for the org-wiki bio entries (§9); lists the bio repos and their status.

## 9. Worlds, wikis, ACP state, videos, research-lab loop

### Worlds-3d (Biota + Cancer DAO worlds — no bio research content, world definitions only)
- `~/workspace/your_files/worlds-3d-iwsdk/src/data/worlds/biota-blockchain.json` (+ `src/data/worlds-data.js`, `src/data/holodeck-fabric.js`, `src/data/advisors.js`, `src/player.js`, `src/lobby.js`, `scripts/verify-*.mjs`) — Biota world fabric (forest biome, South Atlantic anchor, 36 nodes, 6 zones, ALS Researcher + CMMC as in-world companions).
- `~/workspace/your_files/worlds-3d-depth-2-drafts/` (worlds + staging + harness copies) — same Biota world + diagnostic-x world, duplicated across staging dirs.
- `~/workspace/your_files/vr-spaces-loop/metaprompts-and-ideas-2026-11-07.md` — 3-hour build-loop collection; series.json has 35 entries S1–S35 incl. S34 ALS + S35 Parkinsons — TENSION vs the 33-series W3 list (unresolved).
- `~/workspace/your_files/rp1-review/` — promo-video manifests + WorldForge setup doc (cancer-dao, biota-blockchain among first 41 worlds; Cancer Dao anchor Seattle 47.6263,-122.3292, Fred Hutchinson).
- `~/workspace/your_files/rp1-review/promo-videos/` — bright-brand shorts incl. Cancer DAO, Curable.X, BioPharma.Go (filenames in memory 2026-11-04/05; video files themselves are binaries, not grepped).
- `~/workspace/your_files/8h-site-program-notes.md`, `8h-review-pass-report.txt` — site-program notes mentioning bio series/WAVE.
- `~/workspace/your_files/x402-workers/` (4 files) — x402 worker data mentioning bio terms (catalog context).
- `~/workspace/your_files/wordcount-trim-drafts-2026-11-06/` (6 files) — trim drafts of bio articles.

### Org wikis — `~/workspace/your_files/org-wikis/` (all "NOT re-verified live 2026-11-07" — GitHub MCP 429; facts per the 2026-11-05 review)
- `genomic-site/WIKI.md` (+ `assets/status.svg`, `VIDEO-OVERVIEW.md`) — repo AGIFutureFoundation/genomic-site, public, JS, last activity 2026-11-04, root README stub.
- `bioacoustics-cloud/WIKI.md` (+ `VIDEO-OVERVIEW.md`, `assets/status-not-reverified.svg`) — repo AGIFutureFoundation/bioacoustics-cloud ("WAVE bioacoustics platform site; content migrated from the live Vercel-hosted site"); maps to S18 BioDAO/WAVE; review noted the strong BioDAO coverage is in AGI-Biotech-tool, not this repo.
- `AGI-Biotech-tool/WIKI.md` (+ `VIDEO-OVERVIEW.md`) — repo AGIFutureFoundation/AGI-Biotech-tool, describes itself as "biodao.blockchain": molecular workspace for drug discovery in headset/browser; neurogenetic targets (ALS, Parkinson's, Shriners Children's conditions); live public DBs; 339-line README, Python (per 2026-11-05 review, not re-read 2026-11-07).
- `wave-site/WIKI.md` — repo AGIFutureFoundation/wave-site: EMPTY shell as of 2026-11-05 (no main branch, no README, no content).
- `agif-swarm/meta.json`, `agi-corp-worlds/WIKI.md` — swarm/worlds wikis mentioning bio series in passing.

### ACP / agent marketplace state — `~/workspace/your_files/omega-hive-live/`
- `ACP_PUBLIC_STATE_2026-11-06.md` — ALS 6 jobs + 1 sub, WAVE 6 jobs + 1 sub verified live in ACP; all instances offline; 29 jobs + 6 subs total; duplicate WAVE agent noted.
- `OMEGA_MARKETPLACE_REPORT_2026-11-06.md`, `OTHER_MARKETPLACES_2026-11-06.md`, `HUB_UPDATES_PENDING.md` — marketplace reports mentioning ALS/WAVE jobs.
- `~/workspace/your_files/virtuals-agents/JOB_DRAFTS.md` — job drafts incl. ALS compound jobs + WAVE sound jobs.

### Research-lab loop (separate coordinator, started 2026-11-07 ~16:30 PST — read-only note here, not searched in depth)
- `~/workspace/your_files/research-lab-loop/README.md` + `dossier/ecosystem-inventory.md` — 12-hour loop (H01–H12) workspace; its dossier cites this program's `bio-research-expansion/{githubs.md, research-wave.md, research-biodao-genomic-als-cancer.md}` and restates the honesty frame (BirdNET live, Perch/NatureLM not connected, no cure claims). `progress/`, `repos/`, `sites/`, `drafts/`, `monetization/` were empty at inventory time.

## 10. Mirrors, caches, and low-signal hits (reported as counts, not new content)

- `~/workspace/goals/hostinger-email-and-website-deployment/files/hostinger-email/sites/` — full MIRROR of the site trees in §3–§5 (Foundation articles 30 files, series 22, projects 10, features 7, bioacoustics.cloud-regen 6 + 4 _next chunks + 4 agent-skills, sites root 10, hostinger-email root 11; plus `worlds-hub-fellowship-chat/` 9 files). Same content as the primaries — do not count twice.
- `~/workspace/goals/agi-corporate-paperwork-and-safe-fundraising-setup/files/corporate-paperwork/` — MIRROR of §8 (complete/ 8 files, per-entity 04/ 5, 03/ 4, 05/ 4).
- `~/workspace/goals/agi-corp-worlds-on-rp1/files/` — MIRROR of worlds-3d/rp1-review (worlds-3d 10, rp1-review 10, details 4).
- `~/workspace/goals/contacts-and-molecule-file-consolidation/files/contacts-organized/` — 27 files (+16 in organized-lists/) matched; ALL are contacts CSVs (company-name matches: BioLegend, Biotech, Circular Genomics, Estrella Biopharma, Cancer Prevention and Research Institute of Texas). NOTE: despite the goal name, NO molecule/compound data file was found anywhere in this sweep (find `*molecule*` / `*compound*` returned only the goal directory itself, no data files).
- `~/workspace/email/gmail/` — 69 cached Gmail messages matched, ALL on "bioacoustics" (bioacoustics.cloud Cloudflare/email threads) + 1 "perch" + 1 "naturelm" (same thread family); zero for biodao/biota/genomic/genome/compound/cancer/birdnet/xeno-canto/macaulay/watkins/cetacean/curable/biopharma. Hashed filenames; not individually listed.
- `~/workspace/.fellowship-html-backup-2026-11-06/` (3 files) — Fellowship backup copies mentioning bio terms in passing (community-service articles).
- `~/workspace/self_improvement/staging/` — MEMORY.md snapshots (excluded from counts; duplicates of §7).
- `~/workspace/proactivity/hidden_files/` (3 dirs, ~14 files) — proactivity drafts mentioning bio terms.
- `~/workspace/your_files/omega-hive/electron/node_modules/` — binary/locale matches (electron dist files) — noise, not content.
- Extra-area sweep total (text extensions only, priority trees excluded): **693 files** matching the combined pattern — dominated by the mirrors/caches/CSVs above.
- Fellowship site trees (`agifellowship.church-host/`, `agifellowship.church-v2/`) — bio terms appear only in 3 files (`articles/25-many-sparks-one-light.html`, `articles/community-service.html`, `series/14-community-service.html` — "bio" in community-service context, not bio research).

## 11. Notable gaps and figure tensions (for the bio coordinator)

1. **No cancer research content anywhere.** "Cancer" appears only as: (a) the Cancer DAO world/name (Fred Hutchinson anchor, promo short), (b) one line in als-01 (natural-product cancer drugs), (c) one line in diagnostic-x-01 (cervical cancer screening), (d) a funder name in contacts CSVs (Cancer Prevention and Research Institute of Texas). No cancer biology, oncology, or trial content exists on the machine.
2. **No genomic/genome research content.** "Genomic"/"genome" appear only as DAO names + consent/privacy framing (Genomic DAO, Genome.Blockchain articles/series pages) and one empathy twin-study line. No sequence data, no genomics methods, no UK Biobank content beyond the research file's scrape note.
3. **No compound-library data.** The ALS compound library exists ONLY as: 6 ACP job listings + agent site + 3 staged articles + research-file description. No compound list, no molecule file, no screening data on disk (see §10 note).
4. **No BioDAO product.** BioDAO exists as a series/article/project page + the AGI-Biotech-tool repo description (molecular workspace, per 2026-11-05 review, not re-verified). No BioDAO code, contracts, or data on the machine.
5. **Biota has no series number** (W3 list has no Biota; worlds-3d anchors it as a world anyway). **ALS has no series number** (vr-spaces-loop series.json invents S34 ALS / S35 Parkinsons — tension vs the 33-series list, unresolved).
6. **Perch / NatureLM are referenced but not present.** No Perch/NatureLM code, weights, or API on the machine; every mention states they are NOT connected to WAVE.
7. **WAVETranslator repo is a stub** (3 files, 1 KB README, no code) — confirmed in `githubs.md`; it is NOT the source of bioacoustics.cloud (live site is Kylon Next.js on Vercel; regen is local only).
8. **Figure tensions to align before publishing:** Macaulay 2.7M (Mar 2025, staged homepage + MANIFEST) vs 3.2M+ (Nov 2026, Mike-settled + research-wave.md); Xeno-canto ~1,040,000 (Mike-settled, Nov 2026) vs 1,111,111 milestone (research-wave.md, Nov 2026); BirdNET 6,500+ vs 6,522 (v2.4) vs 11,000+ (platform/V3.0) — all three appear in different files.
9. **Cetacean coverage is thin and second-hand:** 1 staged article (CETI), 2 regen files (index + llms.txt), 1 agent-site article; nothing in memory or the Foundation site.
10. **AURA Maternal is out of scope** per the program brief (separate project) — not inventoried here beyond noting the exclusion.

## 12. Method notes / limits

- Binary files (mp4, webp, pdf, zip) were NOT content-grepped except by filename; PDFs/CSVs in `~/workspace/user/files/` were grepped as text where possible (W3_LLC.pdf content is known from the evidence note, not from a fresh PDF parse here).
- The first workspace-wide grep was killed after ~6 min (binary-heavy trees) and replaced by a text-extension sweep (693 extra-area files) plus targeted per-tree greps; coverage of the priority areas (§2–§6) is complete, coverage of the long tail is by file list + counts.
- GitHub repos were NOT re-read in this sweep (GitHub MCP hit HTTP 429 on 2026-11-07 per the org wikis); repo facts here come from `bio-research-expansion/githubs.md` (researched 2026-11-07) and the 2026-11-05 org review.
- Live-site status was NOT re-verified here; "live" claims cite the 2026-11-06 ACP/deploy records in memory and `omega-hive-live/`.
