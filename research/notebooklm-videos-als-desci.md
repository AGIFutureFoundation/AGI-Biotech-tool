# NotebookLM Videos — ALS / DeSci: Frame-Derived Notes

**Published:** research notes in this repo's `research/` folder.
**Research date: 7 November 2026.**
**Sources (local files only):**
- Video 1: `~/workspace/user/media_library/video/dd/dd7b675cc59a9a9c9409d9129379213a9e1be8552cae1dcf18e9bae66d4478ed.mp4` — 7m 23s (443.0s), 1280x720, 47 MB.
- Video 2: `~/workspace/user/media_library/video/46/4652134ce265e7bc177b276f934b690d772b7cf867180d9b8f80f957b2bcfc66.mp4` — 6m 35s (395.4s), 1280x720, 21 MB.
- Grounding docs (read-only): `brief-als-agi183.md`, `brief-als.md`, `compound-agi183.md` in this directory; underlying paper `~/workspace/user/files/als_4_8.pdf`.

## Method and limits — read first

- **No transcript was possible.** Whisper is NOT installed in this environment: no `whisper` binary, and `python3 -c "import whisper"` and `import faster_whisper` both fail with `ModuleNotFoundError` (checked 2026-11-07). No transcription was attempted beyond that check, and no transcript exists for either video.
- **Frame-derived only.** 11 frames per video were extracted with ffmpeg at even intervals and read visually, plus 3 targeted re-check frames (Video 1 at 4:55, Video 2 at 0:20 and 0:30) and one zoomed crop of the Video 1 dose-response chart. Timestamps below are approximate (±~5s, the sampling interval).
- **Only on-screen text is quoted.** Narration was not captured. Do NOT invent dialogue or narration for either video. Where a section title card was not caught in the sampled frames, this file says so instead of guessing the title.
- **Neither video is about CMMC.** Frame inspection confirms Video 1 is ALS molecular biology and Video 2 is ALS/DeSci — no CMMC content appears in any sampled frame.
- **No treatment, cure, diagnosis, or medical-device claims anywhere.** Nothing in these notes claims any compound treats, cures, or diagnoses ALS or any disease. The ALS Researcher is not a medical device.
- **All dose-response curves in Video 1 are SIMULATED — never measured.** The chart itself is titled "Simulated FP Dose Response Curves". Every mention of these curves in this file and in the appended brief sections carries the SIMULATED label. The curves prove nothing; they are the video's illustration of a screening claim.
- **"The video's claim" vs "the paper's finding" are kept apart throughout.** The videos are NotebookLM summaries; they are not the paper, not wet-lab results, and not verification of anything.

---

## Video 1 — "A New Strategy Against ALS" (7m 23s)

NotebookLM video. Title card: **"A New Strategy Against ALS"** over a protein-structure illustration.

### Scene by scene (on-screen text only)

| Approx. time | What the frame shows / says |
|---|---|
| 0:05 | Title card: "A New Strategy Against ALS". Protein ribbon structure with a small orange molecule at its centre. |
| 0:50 | Motor-neuron illustration (purple). Text: "In ALS, the battle is to **save motor neurons**, the cells that control voluntary movement." |
| 1:35 | Red TDP-43 mass attacking a blue neuron inside a cracked hexagonal shield. Headline: "**TDP-43 WEAKENS THE BCL-XL BODYGUARD** / LEAVING NEURONS VULNERABLE." |
| 2:20 | Section card: "**2 — The Secret Switch** / A New Activation Method". (Section 1's title card was not caught in the sampled frames; its title is not recorded here.) |
| 3:05 | Definition card: "**Allosteric Site** — A 'secret switch' on a protein, distinct from its active site, that can modulate its function." Toggle-switch graphic, magnifying glass, protein ribbons. |
| 3:50 | Chart panel titled "**Top 5 Stabilizer Candidates — Simulated FP Dose Response Curves**" (five small panels, sigmoid fits with error bars; individual panel titles not legible at 1280x720). Text at right: "A screening process identified **five promising stabilizer candidates from the AGI compound library**." |
| 4:35 | "**KINETIC STABILIZATION: BINDING DURATION**" — left: "SHORT BINDING DURATION" (protein + small molecule, red energy-vs-time decay curve); right: "PROLONGED STABILIZATION" (protein with a padlock icon and a green molecule labelled "**AGI-183**", blue energy-vs-time decay curve). Both mini-charts label the y-axis "Enegy" [sic — on-screen typo for "Energy"] and the x-axis "Time". |
| 4:55 | Three dose-response panels — "**Neuronal Survival**", "**Cleaved Caspase-3**", "**Mitochondrial Membrane Potential**" — dose on the x-axis from 0.001 to 10 µM, five coloured curves per panel. Legends name five candidates: **AGI-183, AGI-138, AGI-124, AGI-120, AGI-129**. Caption: "Payoff: The best stabilizer, **AGI-183**, was also the most potent for neuronal survival." |
| 5:20 | Section card: "**4 — Resilience & Redundancy** / Solving the Paradox". (Section 3's title card was not caught in the sampled frames; its title is not recorded here.) |
| 6:05 | Neuron inside a green ring. Highlighted text: "**redundant, robust defense**". |
| 6:50 | Hub diagram, centre: "**A New Era of Research**". Spokes: "Open-Source Compounds", "Decentralized Funding", "Global Data Collaboration", "AI-Driven Discovery" (plus one unlabeled brain icon). |
| 7:15 | Closing question over a protein/neuron backdrop: "**If antagonism creates resilience in ALS, what's next?**" Small caption: "resilient, redundant system". |

### What the video claims (as the video's claims, not as facts)

- That TDP-43 weakens the BCL-XL "bodyguard", leaving motor neurons vulnerable.
- That allosteric modulation ("a secret switch") and kinetic stabilization (prolonged binding duration) are the mechanism by which a stabilizer could protect BCL-XL.
- That a screening process identified **five promising stabilizer candidates from the AGI compound library**: AGI-183, AGI-138, AGI-124, AGI-120, AGI-129 (names read from the 4:55 frame legends).
- That the best stabilizer, **AGI-183, was also the most potent for neuronal survival** — per the video's **SIMULATED** dose-response curves (Neuronal Survival / Cleaved Caspase-3 / Mitochondrial Membrane Potential, 0.001–10 µM).
- That antagonism can create resilience — a redundant, robust defense — and that this points to a new era of open-source, decentralised, AI-driven research.

### Cross-check against the ALS paper (`als_4_8.pdf`, via `brief-als-agi183.md` / `compound-agi183.md`)

- **Overlaps (one point only):** the paper names **AGI-183** as a BCL-XL stabilizer, and its background (TDP-43, BCL-XL/BAX, motor-neuron death) is consistent with the video's opening framing. That is the full overlap.
- **Does NOT overlap — the video's "five" is not the paper's "five":** the paper's five discoveries are five **computational-model predictions** — (1) near-additive acute MOMP inhibition (predicted Bliss +0.0052 at day 2, floor effect); (2) strengthening long-term synergy (predicted 42-day MOMP probability 0.764 → 0.040; Bliss peak +0.0305 at day 13.25); (3) attenuated mitochondrial priming (predicted BH3 EC50 held ~112.42 vs control 65.29 → 15.84); (4) systemic MCL1 inhibitors failing clinically (seven inhibitors, none beyond Phase I/II, with the PRT1419 correction); (5) Akt/Bad phosphorylation as a proposed predictive biomarker. **None of these is a candidate compound.** Do NOT conflate the video's five candidate compounds with the paper's five predicted discoveries.
- **Video-only (no counterpart in the paper):** the five-candidate screening (AGI-138, AGI-124, AGI-120, AGI-129 appear nowhere in the paper — the paper names no candidate besides AGI-183); the SIMULATED dose-response curves; the neuronal-survival / cleaved-caspase-3 / mitochondrial-membrane-potential assays; the allosteric-site and kinetic-stabilization framing; the "antagonism creates resilience" framing. The paper gives no SMILES, structure, dose, or screening data for AGI-183, and no screening result for any other compound.
- **Paper-only (absent from every sampled video frame):** the combination partner **AAV6-hSyn-MCL1**, the **Akt/Bad** stratification hypothesis, **Bliss** synergy analysis, **BH3 profiling**, and the proposed **2x2 factorial** validation in iPSC-derived TDP-43 Q331K motor neurons under chronic glutamate stress. The video presents AGI-183 alone; the paper's proposal is the combination.
- **Identity tension still applies:** the video's AGI-183 is the paper's BCL-XL stabilizer (anti-apoptotic, neuroprotective). Do NOT merge it with the `AGI_Compound_001.pdf` catalog entry also named "AGI-183", which describes a CRBN-binding FLIP inhibitor (pro-apoptotic, cancer) — same name, opposite mechanism, unresolved (see `compound-agi183.md` §5).
- **Do NOT present the video's screening story as paper-grounded.** Only AGI-183 is shared between video and paper, and the video's "most potent for neuronal survival" claim is the video's claim about its own SIMULATED curves — not a paper finding, not a measured result, not a treatment claim.

### Placement notes (Video 1)

- Belongs with the ALS briefs (`brief-als-agi183.md` — appended section there) and the AGI-183 compound entry (`compound-agi183.md`), as a **video explainer of the screening concept**, clearly labelled as NotebookLM video content, not paper content.
- Usable as a companion visual for `als-02-from-compound-to-treatment.md` (the compound-to-treatment road) ONLY with the SIMULATED label and the "video's claim, not the paper's finding" line attached; the five-candidate screening must never be presented as the paper's screening result.
- Do NOT add AGI-138, AGI-124, AGI-120, or AGI-129 to the compound library, `data.js`, or any priced job — they are names on a video frame, with no paper source, no structure, no data file, and no verified identity.
- The "Enegy" typo is on-screen in the video; quote it as "[sic]" if reproduced, or paraphrase without reproducing the typo.

---

## Video 2 — "Science, Unchained" (6m 35s)

NotebookLM video. Title card: **"Science, Unchained"** (NotebookLM logo) over a breaking chain illustration. An ALS / decentralised-science (DeSci) explainer in three numbered sections.

### Scene by scene (on-screen text only)

| Approx. time | What the frame shows / says |
|---|---|
| 0:05 | Title card: "Science, Unchained". Rusted chain breaking apart. |
| 0:20 | Quotation card: "**ALS is not an incurable disease. It is an underfunded one.**" ("incurable" and "underfunded" highlighted.) |
| 0:30 | Section card: "**1 — The Problem** / Science Friction". |
| 0:45 | Definition card: "**Science Friction** — The institutional, ethical, and technical barriers that slow data sharing and therapeutic development." |
| 1:25 | Section card: "**2 — The Agitation** / The Fight Against ALS". |
| 2:05 | "**Patient-Led Initiatives**" list: "ARC: Share data from home." / "ALL ALS: Accessible research for everyone." / "Answer ALS: Open, collaborative quest." / "Data Commons: Datasets for global researchers." |
| 2:45 | Section card: "**3 — A Decentralized Solution**". |
| 3:25 | Definition card: "**DAO** — A community-governed organization where stakeholders vote on key decisions, like research funding." |
| 4:05 | Table, "DeSci Project" / "Focus Area": **Molecule — IP Marketplace**; **VitaDAO — Longevity Science**; **ResearchHub — Open Publication**; **DeSci Labs — Transparent Publishing**; **CerebrumDAO — Brain Health**. |
| 4:45 | "**A New Funding Model**" — four steps: "Step 1: Discovery — A researcher has a new discovery but needs funding." → "Step 2: IP-NFT — They create an IP-NFT for their research on a DeSci platform." → "Step 3: DAO Funding — The **ALS DAO** community directly funds the project via the IP-NFT." → "Step 4: Acceleration — Research moves forward, faster and more transparently." |
| 5:25 | Donut chart labelled "DeSci" with an illustrative split: Transparency 30%, Democratized Funding 25%, Global Collaboration 20%, Fairer IP Management 15%, Researcher Empowerment 10%. Text: "By redesigning incentives, DeSci tackles **science friction** head-on, creating a virtuous cycle for progress." No source is given on screen for these percentages. |
| 6:05 | Closing statement: "By removing barriers, DeSci invites **everyone** — scientists, patients, and advocates — to shape the **future of knowledge** together." |
| 6:28 | Closing question: "If communities can **directly fund** the science they need, what **breakthrough** will we unlock next?" |

### What the video claims (as the video's claims, not as facts)

- That ALS is underfunded rather than incurable (the video's framing line, quoted above).
- That "science friction" — institutional, ethical, and technical barriers — slows data sharing and therapeutic development.
- That patient-led initiatives (ARC, ALL ALS, Answer ALS, Data Commons) are already pushing open, collaborative ALS research.
- That a DAO is a community-governed organisation voting on key decisions such as research funding, and that DeSci projects (Molecule, VitaDAO, ResearchHub, DeSci Labs, CerebrumDAO) exemplify the model.
- That a new funding model — discovery → IP-NFT → DAO funding → acceleration — lets an "ALS DAO community" directly fund research.
- That redesigning incentives tackles science friction, with the video's own illustrative split (Transparency 30% / Democratized Funding 25% / Global Collaboration 20% / Fairer IP Management 15% / Researcher Empowerment 10%).

### Cross-check against the BioDAO brief (`brief-biodao-genomic-compounds.md`)

- **Consistent framing:** the video's IP-NFT → DAO-funding model matches the Molecule / Bio Protocol model documented in the brief (§2 Item 1): IP-NFTs attach legal IP rights to a token so a research asset can be co-owned and governed by a community; BioDAOs tokenise IP as IP-Tokens.
- **Missing caveat — flag it:** the video does not mention that an IP-Token carries **governance and information rights but no guaranteed financial return**. Any page use must add that line from the brief; never present IPTs as equity, revenue shares, or investment returns.
- **"ALS DAO" is the video's framing, not an existing product.** No BioDAO / ALS DAO code, contracts, or data exists on the machine, and the ALS paper (`als_4_8.pdf`) never mentions a DAO (see `brief-als-agi183.md` honesty lines). Do NOT present the video's "ALS DAO community" as a live DAO, a deployment, or a funding channel that exists today.
- **The donut percentages are the video's own illustrative split, unsourced on screen.** Do NOT quote Transparency 30% / Democratized Funding 25% / etc. as measured data or as anyone's research finding.
- **Patient-led initiatives named:** ARC, ALL ALS, Answer ALS, Data Commons. Answer ALS is already in `brief-als.md` (open, collaborative); ARC / ALL ALS / Data Commons are the video's list — verify each independently before presenting any of them as a live programme with a stated function beyond what the video's one-line descriptions say.
- **DeSci table vs the brief:** Molecule, VitaDAO, ResearchHub are covered in the brief's DeSci research; DeSci Labs and CerebrumDAO appear in the video's table with one-line focus areas only ("Transparent Publishing", "Brain Health") — treat those two lines as the video's characterisation, not as verified profiles.

### Placement notes (Video 2)

- Belongs with the BioDAO / Genomic brief (`brief-biodao-genomic-compounds.md` — appended section there), as a **DeSci explainer video** for the BioDAO (S18) / Genomic DAO (S27) pages — with the "no DAO product exists" honesty line and the IPT no-guaranteed-return line attached.
- Usable as a companion visual for the BioDAO series/article pages ONLY as an explainer of the DeSci model; the "ALS DAO" step must be labelled as the video's illustrative model, not an existing ALS DAO.
- The "ALS is not an incurable disease. It is an underfunded one." line is a rhetorical framing line from the video, not a medical claim — do not present it as a finding that ALS is curable, and keep it out of any treatment/cure context.

---

## Frame stills extracted (for later upload — binaries, browser web-upload route)

Stills are in `~/workspace/your_files/bio-research-expansion/assets/`. They are JPG binaries staged locally only; they were NOT pushed or uploaded (binaries need the browser web-upload route, per the github_pages_deploy skill). The source videos themselves (47 MB + 21 MB) were NOT pushed — far over snapshot limits.

| File | Source frame | Shows |
|---|---|---|
| `assets/video1-als_tdp43-bclxl-bodyguard.jpg` | Video 1, ~1:35 | "TDP-43 WEAKENS THE BCL-XL BODYGUARD / LEAVING NEURONS VULNERABLE." |
| `assets/video1-als_simulated-dose-response.jpg` | Video 1, ~3:50 | "Top 5 Stabilizer Candidates — Simulated FP Dose Response Curves" (SIMULATED — label on any use). |
| `assets/video1-als_kinetic-stabilization-agi183.jpg` | Video 1, ~4:35 | "KINETIC STABILIZATION: BINDING DURATION" — AGI-183, prolonged stabilization (on-screen "Enegy" typo). |
| `assets/video2-desci_als-underfunded-quote.jpg` | Video 2, ~0:20 | "ALS is not an incurable disease. It is an underfunded one." |
| `assets/video2-desci_project-table.jpg` | Video 2, ~4:05 | DeSci project table (Molecule, VitaDAO, ResearchHub, DeSci Labs, CerebrumDAO). |
| `assets/video2-desci_funding-model.jpg` | Video 2, ~4:45 | "A New Funding Model" — Discovery → IP-NFT → DAO Funding → Acceleration. |

---

## Sources

- Video 1 file: `~/workspace/user/media_library/video/dd/dd7b675cc59a9a9c9409d9129379213a9e1be8552cae1dcf18e9bae66d4478ed.mp4` (47 MB, 7m 23s, 1280x720).
- Video 2 file: `~/workspace/user/media_library/video/46/4652134ce265e7bc177b276f934b690d772b7cf867180d9b8f80f957b2bcfc66.mp4` (21 MB, 6m 35s, 1280x720).
- `~/workspace/your_files/bio-research-expansion/brief-als-agi183.md` — ALS paper brief (five predicted discoveries, verification corrections, identity tension).
- `~/workspace/your_files/bio-research-expansion/brief-als.md` — companion ALS brief (compound-library jobs, "not a medical device" line, Answer ALS).
- `~/workspace/your_files/bio-research-expansion/compound-agi183.md` — AGI-183 compound entry (paper's BCL-XL stabilizer; catalog identity tension §5).
- `~/workspace/your_files/bio-research-expansion/brief-biodao-genomic-compounds.md` — BioDAO / Genomic brief (Molecule IP-NFT → Lab, IPT no-guaranteed-return line, no-DAO-product honesty line).
- `~/workspace/user/files/als_4_8.pdf` — underlying ALS paper (via the briefs above; not re-read in this pass).
