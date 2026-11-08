# Fixes Applied — Research Lab Loop 2, Peer Review R1–R14

**Worker:** W2-4 (required-fixes application)
**Date:** 8 November 2026
**Peer review:** `PEER-REVIEW.md` (Worker W2-2, 8 Nov 2026), REQUIRED fixes R1–R14, plus reviewer questions B1-G1–G12 and B2-G1–G13
**Documents corrected (in place, filenames unchanged):**
- `method-mitochondrial-priming-stratification.md` (B1) — 21,321 → **23,778 words**
- `method-vocal-acoustic-phenotyping-neurodegeneration.md` (B2) — 20,001 → **23,006 words**
- `method-three-network-transfer-stage1.md` (third document, W2-3) — 12,835 → **12,844 words**

All corrections were verified against a real source via web search before being written. No citation, statistic, or URL was invented. Where a correction note refers to "an earlier draft", it is a deliberate audit-trail note explaining what was wrong, not a stale self-reference.

**Final verification (8 Nov 2026):** zero matches for "honest"/"honestly" in all three documents; zero flat "16 donors" / "16-donor" / "16 SALS" phrasings remain — every donor-n hit is the corrected "7–16" range or "15 SALS donors"; zero "commercial exploitation" phrasings remain.

---

## B1 — method-mitochondrial-priming-stratification.md

### R1 — Quantified minimum-effect bars
- **§3.3 rule 1, §3.5 rules 1 and 6, §4.5, §5 item 5, Appendix A item 5, Appendix B row 1:** interim pre-registered bar set — EC50 difference between lowest and highest pBad quartiles **≥20% of the pre-stress baseline BH3 EC50** (same 20% magnitude as the §6.7 stabiliser bar), CI excluding the minimum. Owner: executing-lab PI. Deadline: confirm or replace from pilot variance at pre-registration, before confirmatory lock. Confirmatory data collection cannot start until locked.

### R2 — Bye donor count
- **§2.2 V13 (line 179), §2.6, §12.2 item 6, Appendix C:** screen range **7–16 donors**; combination validation on **15 donors**. The +30.3-day triple-combination LD50 extension (p < 0.0001) was corrected from "review-reported, not read in the primary paper" to **in the primary paper (Fig. 5c)** — the earlier label was wrong. Verification: primary paper full text (Nat Neurosci 2026;29:40–52, doi:10.1038/s41593-025-02118-7); triple combination 100% of 15 validation donors responding, minimum rescue 16.5 days; memantine+riluzole +12.5 days (P=0.0109); baricitinib+memantine +23.5 days; baricitinib+riluzole +24.5 days.

### R3 — BirdNET (not applicable to B1; B1 contains no BirdNET claim)

### R4 — Xeno-canto (not applicable to B1; B1 contains no Xeno-canto figure)

### R5 — Front. Aging Neurosci. date (not applicable to B1; B1 does not cite Ramineni et al.)

### R6 — Venetoclax misplaced as an MCL1 inhibitor
- **§1.5 inversion table:** MCL1 row now "Inhibit (AZD5991, AMG 176, S63845)" — venetoclax removed. **Correction note added after the table:** venetoclax (ABT-199) is BCL-2-selective — Ki <0.01 nM for BCL-2 vs 48 nM for BCL-XL and >440 nM for MCL-1 (Souers et al., *Nat Med* 2013, via PMC5457565). Used in oncology only in combination with MCL1 inhibitors, never as one.

### R7 — Catalog 413 vs 336 vs 24 SMILES
- **§7.4 reconciliation paragraph added:** 413 = numbered catalog entries (AGI-001–AGI-413, incl. duplicates/variation records/entries without usable structure); 336 = entries counted as HYPOTHETICAL structures; 24 = distinct SMILES among entries that carry one. The 77-entry remainder (413 − 336) is unitemised → new open item **GAP-MPS-3**. **§0.2 rule 3** updated to "336 HYPOTHETICAL structures (of 413 numbered entries)".

### R8 — F1 kill-logic gap + PI3K manipulation bar
- **§3.3 rule 7:** manipulation now names **LY294002**, pilot titration 10–50 µM, target ≥50% reduction in pAkt (S473) and pBad (S136) vs vehicle, inhibitor-only + vehicle controls in the same lines (if LY294002 alone kills neurons, the manipulation is uninterpretable, not a chain fail), quantitative bar ≥20% increase in stabiliser benefit on Day 42 BH3 EC50, CI excluding zero. Same bar carried into §3.5 rule 1, §4.2 bullet, §4.5 within-line test.
- **§6.1 legs (a)/(b)** now reference the quantified bars. **Verdict logic** now defines the two previously undefined cases: (a)+(b) hold but (c) fails → **NARROW** (stressor-specific stratification, no cross-stressor biomarker language); (a) fails but (b) holds → **NARROW** (mechanism supported within lines; stratification not demonstrated at a meaningful magnitude). **§6.11 table** gained both rows.
- Verification: LY294002 is a reversible PI3K inhibitor, IC50 1.4 µM; 10 µM reduces p-Akt+ neurons in neural-progenitor culture (*J Neurosci* 2013;33:14318–14330); 50 µM abolishes PI3K activity without apparent toxicity (Vlahos et al., *J Biol Chem* 1994;269:5241–5248); 100 µM abolishes NGF-evoked pAKT-S in DRG neurons.

### R9 — Decade-claim attribution (not applicable to B1; B1 does not carry the decade claim)

### R10 — PXT864 quote
- **§8.3 and ref 20:** corrected to "insufficient for commercialization in the short or medium term" (Pharnext press release, 14 Feb 2023, per red-team §1(e)).

### R11 — Uncited figure (not applicable to B1; no uncited T6-style figure)

### R12 — Stale self-references
- **§3.3 rule 2:** "(§3.3 rule 3 in the earlier draft)" → "(rule 3 below)". **§4.2 line 340:** self-reference "(§4.2)" → "(see §3.3 rule 7)". The two remaining "earlier draft" mentions in B1 are deliberate correction-note audit trails (the R6 note), not stale references.

### R13 — mPower source (not applicable to B1; B1 does not cite mPower)

### R14 — AZD5991 rounding standardisation
- **§2.2 V1 note:** 3/78 = 3.846% unrounded, quoted as **3.8%** everywhere with N=78 stated each time.

### Reviewer questions B1-G1–G12 — new §12.3 table (closing statement renumbered to §12.4)
- **G2** answered (LY294002, §3.3 rule 7). **G3** answered (§3.7 Phase 1: ICC ≥0.5 for baseline pBad across lines, else the between-line claim does not proceed). **G4** answered (§3.7 Phase 0: vector-only arm may start before D1 resolves; small-molecule factorial waits for D1). **G5** answered (§3.7 Phase 1: BAX/BAK-inhibitor rescue arm; model fails, not hypothesis; published proportion not found = open item). **G6** answered (Appendix C BH3 acceptance: JC-1 dynamic range ≥2-fold vs FCCP control; CV ≤20%; positive-control EC50 shift ≥20%; yield/purity per run vs pilot reference range). **G8** answered (Rohn developmental confound, §4.3: Bcl-2 overexpressed from development; rung tests adult intervention). **G9** answered (D3 assay/bar, §7.3: fluorescence-polarisation competition binding with stated Kd/IC50; engagement without §6.7 stabilisation = D3 "no"). **G12** answered (two sporadic-ALS lines run in parallel in rung 1, §4.2; verdict per cohort).
- **Open items recorded:** G1 (partially — pilot MOMP check is the first ALS-specific evidence); G7 (MCL1 fold-change → **GAP-MPS-5**, owner executing-lab PI, deadline Phase 0 Gate 0c); G10 (Phase 0 cost/funder/timeline → **GAP-FLAG-5**, owner coordinator/Mike, no figures invented); G11 (neuron–astrocyte co-culture as first co-culture test, Phase 3 extension → **GAP-MPS-6**, design not yet written).

### B1 new gaps (§12.1)
- **GAP-MPS-3** (catalog 77-entry remainder), **GAP-MPS-5** (MCL1 fold-change), **GAP-MPS-6** (co-culture extension).

### Optional polish applied
- **§8.1:** rubric scores now consistent criterion counts ("4 of 5 criteria met" / "3.5 of 5 criteria met").

---

## B2 — method-vocal-acoustic-phenotyping-neurodegeneration.md

### R1 — Quantified minimum-effect / F3–F4 bars
- **§9 F3:** interim pre-registered bar **|r| ≥ 0.3** (locked as the bar, not floated as an example). Owner: Phase 1 lead; deadline: pre-registration, from pilot variability, before confirmatory cohort lock; confirmatory collection cannot start until locked.
- **§9 F4:** interim bar **Cohen's d ≥ 0.5** on the pre-specified primary feature family (phonation), with ON/OFF discrimination AUC ≥ 0.70 as a secondary check (Thies et al. 2025 reported AUC 0.81; the bar is not copied from that paper). Same owner/deadline.
- **GAP-VAP-3 (§13.4)** updated to record the bars as set; **§12 template item 8** updated ("|r| ≥ [minimum set from pilot]" → "|r| ≥ 0.3 (interim pre-registered bar; confirmed or replaced from pilot before confirmatory lock)").

### R2 — Bye donor count
- **§2.2 (line 133), §10 C22, §11.4, ref 18:** "7–16 SALS donors (methods range); combination validation on 15 SALS donors"; ref 32 note updated to the same range. Verification: primary paper full text (see B1 R2 above).

### R3 — BirdNET date + classes wording
- **Status box (line 19), §2.5, §10 C12:** "BirdNET v2.4 (June 2023) covers 6,522 classes (incl. 10 non-event classes)" — not March 2025, not "6,522 bird species". Verified against the BirdNET-Analyzer README: "V2.4, June 2023 — more than 6,000 species worldwide … global selection of species (birds and non-birds) with 6,522 classes (incl. 10 non-event classes)". The derived species count 6,512 (6,522 − 10) is **not** asserted anywhere, because the classes include non-bird species.

### R4 — Xeno-canto re-check
- **Status box, §2.5, §3.2, §10 C13:** dated re-check note added (8 Nov 2026): the founder's page (few.vu.nl/~rplanque, Bob Planqué) now states "about 1,100,000 recordings"; the loop's settled figure **~1,040,000 is retained** and the adoption of the higher figure awaits Mike's decision. The figure 1,111,111 is not used. (xeno-canto.org's own stats page showed 1,017,393 on an older crawl.)

### R5 — Front. Aging Neurosci. date
- **§2.3 (line 146):** "Front Aging Neurosci 2026;27 Oct 2026" (ref 13 already said 27 Oct). Verified: Ramineni et al., *Front. Aging Neurosci.* 18:1975870, doi:10.3389/fnagi.2026.1975870, published **27 October 2026** (frontiersin.org). The "17 Oct 2026" date was wrong.

### R6 — Venetoclax (not applicable to B2; B2 does not carry the venetoclax claim)

### R7 — Catalog numbers (not applicable to B2; B2 has no catalog)

### R8 — PI3K manipulation (not applicable to B2; B2 has no PI3K manipulation)

### R9 — Decade-claim attribution
- **§2.1, §10 C5:** the "as much as a decade" phrasing is **verbatim in Bioengineering 2026;13:1037** (Yuan et al., MDPI PDF: "Such vocal changes can emerge early in the disease course, at times preceding or co-occurring with the earliest overt motor signs by as much as a decade [8]"), where ref [8] is Cao et al. 2025 (*npj Parkinson's Dis* 11:57), which contains the near-identical phrasing. Fix applied as **dual attribution** (Bioengineering stands, Cao named as underlying source), not re-attribution to Cao alone. This was a resolution, not a misattribution.

### R10 — PXT864 quote
- **§11.4:** "insufficient for commercial exploitation" → "insufficient for commercialization in the short or medium term" (Pharnext press release, 14 Feb 2023). **§11.4** also gains an Ovadia-direction line: the patent's direction is opposite to MPS (high pAkt → responsiveness to an Akt-raising peptide, vs MPS's low pAkt/pBad → benefit from BCL-XL stabilisation).

### R11 — Uncited T6 "82–90%"
- **§4.3 T6:** the figure "discriminated PD from controls at 82–90% in one analysis" is **removed**. A targeted search for a PC-GITA modulated-vowel discrimination source returned no match, so the figure was removed rather than cited to a guessed source. The task description is kept, with a note recording the removal and the reason.

### R12 — Stale self-references
- **§4.0 table gate + §4.0 paragraph:** standardised to one gate, stated identically in §4.0 and §4.1: "Phase 0 pre-registration filed and Phase 0 report published (including nulls), with data-access outcomes documented" (previously §4.0 said "published **or** pre-registered"). The remaining "earlier draft" mention in B2 is a deliberate correction-note audit trail (the T6 R11 note), not a stale reference.

### R13 — mPower source
- **§2.4 mPower row:** "8,320 participants (Bot et al. 2016, *Sci Data* 3:160011 — at least one survey/task in first six months; 9,520 consented overall)". Verification: 8,320 = participants completing at least one survey or task in the first six months of data release (Bot et al. 2016).

### R14 — Rounding (not applicable to B2; B2 has no AZD5991-style rounding issue)

### Reviewer questions B2-G1–G13 — new §13.5 table
- **G1 (§8.2):** ComBat-style feature-level harmonisation (disease group protected) + reference-signal calibration task with a pre-registered drift limit; on device discontinuation, cross-device calibration recordings from the same participants and re-validation before the new device's data enter the primary analysis.
- **G2 (§9 F2):** F2 bites in Phase 0 (multi-dataset) and Phase 2 (LOCO by device); Phase 1 gains a device-variability sub-study (subset recorded on a second device) so F2 is testable within Phase 1. Without it, Phase 1's F2 is reported as untested, not passed.
- **G3 (§2.1, ref 33):** Skodda et al. 2013 (*Parkinson's Disease*, PMC3872441) — 80 PD + 60 controls, mean interval 32.5 months: shimmer 6.548 → 11.490 (p < 0.0001, d = 0.87); noise-to-harmonics ratio 0.051 → 0.103 (p < 0.0001, d = 0.61); jitter did not change significantly; deterioration did not correlate with the time interval. No per-year rate exists; whether 12 months suffices is a pilot question (**GAP-VAP-8**).
- **G4 (§5.4 Arm L):** interim WER bar ≤25% on a manually transcribed dysarthric subset; if no ASR clears it, Arm L is dropped and the AD arm becomes acoustic-only, graded down accordingly.
- **G5 (§4.3):** OFF-session eligibility decided by the participant's clinician; exclusions: history of severe OFF freezing/falls, inability to tolerate ≥12 h withdrawal, no escort/transport. Rescue: session stops, levodopa given immediately, session recorded ON and flagged.
- **G6 (§9 F9):** pilot ICC gate decided on the **lower 95% confidence bound (≥0.3)**, not the point estimate. Computed 8 Nov 2026 (ICC(1,1), n=20, k=2): observed ICC 0.5 → 95% CI 0.09–0.77; ICC 0.7 → 0.39–0.87; ICC 0.3 → −0.14–0.65.
- **G7 (§5.5 Arm E):** Perch input conditioning — resample 44.1 kHz → 32 kHz, 5-s windows (Perch frontend: 5 s at 32 kHz, hop 10 ms, window 20 ms; arXiv:2508.04665). Resampling applies to the embedding arm only; Praat jitter/shimmer are computed on the original 44.1 kHz audio.
- **G8 (§2.5, GAP-VAP-9):** Perch code Apache 2.0; Perch **v1** weights Apache 2.0 per the Kaggle model page. Perch **v2** weights licence **not yet confirmed** — to be checked against the Kaggle v2 model page before any governed dataset release in Phase 3.
- **G9 (§9 F4 scope, mirrored in §11):** ALS/AD longitudinal claims carry a weaker falsification standard by design (F3 alone, no manipulation analogue) and are graded down — a positive ALS/AD longitudinal result is reported as "correlational tracking, manipulation-unconfirmed" until a timed perturbation exists.
- **G10 (§8.2):** confound rows added — smoking status, depression (PHQ-9), respiratory disease, hearing loss (severe = exclusion for the reading task, otherwise covariate), reflux symptoms — all covariates except severe hearing loss.
- **G11 (§4.1 step 1):** minimum Phase 0 dataset = UCI (31 subjects) + ADReSS (156 participants) as the floor; F1 can run on UCI alone only as a single-dataset, single-language result with the limitation stated; if PC-GITA/mPower/ADReSS access all fail, Phase 0 reports on UCI+ADReSS only and the cross-sectional claim is correspondingly narrowed.
- **G12 (§2.5, C12/C13, status box):** settled figures given with source + as-of date (Macaulay 3.2M+ per Wikipedia accessed Nov 2026 vs Cornell Mar 2025 2.7M — re-check before external use; Xeno-canto ~1,040,000 retained with 8 Nov 2026 re-check recorded; Perch 1,542,778 verified against arXiv:2508.04665 Table 1, 8 Nov 2026). **Open item:** re-check owner before staging is not yet assigned — for the coordinator.
- **G13 (§7.3, §12 template item 13):** default retention **10 years from last publication** (a default for the ethics approval, not a decided fact); on withdrawal, audio + derived features deleted within 30 days, deletion logged, already-analysed aggregate results retained.

### Other B2 fixes applied
- **3-year caveat (§2.2 line 129, §10 C6, §13.5):** the "up to 3 years before diagnosis" figure was not confirmed from the Pedersen et al. chapter text in this pass — verify against the chapter before external use (peer review §5B, B2-6). (The §1.2 item 2 statement cites §2.2 and is covered by the same caveat.)
- **Perch training total (§2.5, ref 24):** 1,542,778 recordings verified against arXiv:2508.04665 Table 1 (Xeno-Canto 896,255 + iNaturalist 571,698 + Tierstimmenarchiv 33,859 + FSD50K 40,966); 14,795 classes (14,597 species + 198 general). Date anchor corrected to "August 2025" (the exact day was not verified).
- **Macaulay Library (§2.5, C13):** 3.2M+ kept with dated source note — Wikipedia (accessed Nov 2026) vs Cornell alumni piece Mar 2025 saying 2.7M; figure growing, re-check before external use.
- **§10 C5:** source now "Bioengineering 2026;13:1037, citing Cao et al. 2025 (npj Parkinson's Dis 11:57)". **§12 template item 10:** confounds added. **Ref 30:** "(details to be confirmed)" added. **New ref 33:** Skodda et al. 2013.
- **§13.4:** GAP-VAP-3 updated (bars set); **GAP-VAP-8** added (longitudinal anchor + 12-month window unproven); **GAP-VAP-9** added (Perch v2 weights licence + speech-encoder licence before Phase 3 dataset release).

---

## Third document — method-three-network-transfer-stage1.md

Scope extension (received 19:50 PST 7 Nov 2026). Same treatment as B1/B2.

### R2 — Bye donor count
- **§3.1 (line 89):** "(100-donor library; screen run on 7–16 SALS donors; combination validation on 15 SALS donors — peer-review fix R2, 8 Nov 2026)" — the old clause "combination validation donor n to be stated wherever the result is cited — red-team precision correction" is replaced by the stated n (15).
- **§8.1 model-transfer guard (line 203):** "Bye-style 100-donor-library/7–16-donor-screen assay".
- **§8.2 (line 209):** "The Bye screen's 7–16-donor screen n and the 15-donor combination-validation n are stated in every report of Bye-derived numbers".
- **Ref 6 (line 278):** "(7–16 SALS donors; combination validation on 15 SALS donors)".

### R3/R4 — BirdNET / Xeno-canto
- **Not applicable.** Grep-verified 8 Nov 2026: the document contains no BirdNET mention and no Xeno-canto mention at all, so no figure or date needed correction and no re-check note was added.

### R10 — PXT864 status
- **Already correct; verified, not changed.** Line 57 quotes the press release correctly: "insufficient for commercialization in the short or medium term". Lines 15, 55, 59 state the stopped-14-Feb-2023 status correctly (no Phase 3, highest phase Phase 2, PLEODIAL-I/II). No "commercial exploitation" phrasing anywhere in the document.

### "Honest/honestly" filler
- **None found.** Grep-verified 8 Nov 2026: zero occurrences.

### Other R-fixes checked
- **R12 stale self-references:** none found (no "earlier draft" phrasing in the document).
- **R11-style uncited figures:** no uncited percentage claim of the T6 type was found in this pass. The document's quantitative claims carry citations; no figure was removed.
- **R14-style rounding:** no AZD5991-style rounding issue found.
- **No other R-fix applies** to this document.

---

## Open items (not silent skips)

| Item | Document | What is missing / who decides |
|---|---|---|
| GAP-MPS-3 | B1 §7.4 | 77-entry catalog remainder (413 − 336) unitemised |
| GAP-MPS-5 (B1-G7) | B1 | MCL1 fold-change; owner executing-lab PI; deadline Phase 0 Gate 0c |
| GAP-MPS-6 (B1-G11) | B1 | Neuron–astrocyte co-culture as first co-culture test, Phase 3 extension; design not yet written |
| GAP-FLAG-5 (B1-G10) | B1 | Phase 0 cost/funder/timeline; owner coordinator/Mike; no figures invented |
| B1-G1 (partial) | B1 | Pilot MOMP check is the first ALS-specific evidence; fuller answer pending |
| B1-G5 | B1 | Published proportion for the BAX/BAK-inhibitor rescue arm not found |
| GAP-VAP-8 | B2 | 12-month longitudinal window unproven; Skodda 2013 cited, pilot must prove detectability at 12 months |
| GAP-VAP-9 | B2 | Perch v2 weights licence + speech-encoder licence to be confirmed before Phase 3 dataset release |
| 3-year figure (B2-6) | B2 | "Up to 3 years before diagnosis" (Pedersen ch. 11) not confirmed from chapter text — verify before external use |
| B2-G12 (partial) | B2 | Re-check owner for settled figures before staging not yet assigned — for the coordinator |
| Xeno-canto settled figure | B2 | Founder's page re-check 8 Nov 2026 shows ~1,100,000; settled ~1,040,000 retained — adoption is **Mike's decision, still pending** |

---

## Verification sources used (8 Nov 2026, all via web search / text fetch)

- BirdNET-Analyzer README (GitHub): v2.4, June 2023; 6,522 classes (incl. 10 non-event classes)
- Bob Planqué founder's page (few.vu.nl/~rplanque): "about 1,100,000 recordings"; xeno-canto.org stats page: 1,017,393 (older crawl)
- Ramineni et al., *Front. Aging Neurosci.* 18:1975870 (frontiersin.org): published 27 October 2026
- Souers et al., *Nat Med* 2013 (via PMC5457565): venetoclax Ki <0.01 nM BCL-2 vs 48 nM BCL-XL, >440 nM MCL-1
- Bioengineering 2026;13:1037 (Yuan et al., MDPI PDF) + Cao et al. 2025, *npj Parkinson's Dis* 11:57: "as much as a decade" phrasing verbatim in both
- Bot et al. 2016, *Sci Data* 3:160011: mPower 8,320 participants (≥1 survey/task in first six months), 9,520 consented
- Bye et al., *Nat Neurosci* 2026;29:40–52 (doi:10.1038/s41593-025-02118-7): screen 7–16 SALS donors; combination validation 15 SALS donors; triple-combination +30.3 days LD50 (Fig. 5c)
- Pharnext press release, 14 Feb 2023 (via red-team §1(e)): "insufficient for commercialization in the short or medium term"
- Perch 2.0, arXiv:2508.04665 Table 1: 1,542,778 recordings; 14,795 classes; 5 s at 32 kHz, hop 10 ms, window 20 ms
- Skodda et al. 2013, *Parkinson's Disease* (PMC3872441): shimmer 6.548 → 11.490 (d 0.87), nhR 0.051 → 0.103 (d 0.61), jitter unchanged, mean interval 32.5 months
- LY294002: *J Neurosci* 2013;33:14318–14330 (10 µM reduces p-Akt+ neurons); Vlahos et al., *J Biol Chem* 1994;269:5241–5248 (50 µM abolishes PI3K activity)
- ICC CIs computed 8 Nov 2026 (ICC(1,1), n=20, k=2): 0.5 → 0.09–0.77; 0.7 → 0.39–0.87; 0.3 → −0.14–0.65
- Macaulay Library: Wikipedia 3.2M audio recordings vs Cornell alumni piece Mar 2025 (2.7M)
- Perch v1 weights licence: Apache 2.0 per the Kaggle model page (google/bird-vocalization-classifier); v2 weights licence unconfirmed
