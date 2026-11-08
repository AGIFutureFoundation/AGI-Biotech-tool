# PEER REVIEW — Loop 2 Track B method documents

**Reviewer:** Worker W2-2 (method peer review), Research Lab Loop 2
**Date:** 8 Nov 2026
**Documents reviewed (read in full):**
- B1 — `method-mitochondrial-priming-stratification.md` (Mitochondrial Priming Stratification, MPS)
- B2 — `method-vocal-acoustic-phenotyping-neurodegeneration.md` (Vocal Acoustic Phenotyping for Neurodegeneration, VAP-N)
- B3 — `verification-red-team.md` (Worker B3, independent verification / red team, 8 Nov 2026)

**Method:** fresh-eyes cross-read of B1 against B2 and of each against B3; independent spot-check of 7 load-bearing references from B1 and 8 from B2 via `browser.search` (searches run 8 Nov 2026). Verdicts use VERIFIED / PARTIAL / NOT-FOUND. No citation, statistic, or URL is invented in this memo; where a check could not confirm a sub-figure from the returned snippets, that is stated.

---

## 1. Per-document verdicts

### B1 (MPS) — CONDITIONAL PASS, subject to Required Fixes R1, R2, R6, R7, R8, R10, R12, R14

B1 is the stronger of the two documents on red-team incorporation. The novelty withdrawal is genuine and carried through the status box, §2.1 V16, §6.6 (F6 closed), §10, and §12 — not a cosmetic mention. The "there is no drug" finding is carried as the central gating fact in the status box, §1.3, §7.1, and §9.3, including the red team's exact framing that the programme is "currently untestable, not merely untested." The F1 upgrade is substantively adopted (continuous primary, within-line PI3K manipulation, second-stressor replication, quantitative stabiliser bar). The Rohn 2008 replacement citation is correct and independently confirmed by this review (see §4).

The conditions are not cosmetic. The single most important red-team demand — a **quantified** minimum meaningful interaction — is adopted in form only; the number is deferred to the executing lab with no owner and no deadline (R1). The Bye donor-n fix that both documents carry is itself imprecise (R2). And the F1 kill logic has an undefined case (R8). None of these overturns the method, but all three must be closed before staging, because each is exactly the kind of gap a reviewer uses to argue a null result is uninterpretable.

### B2 (VAP-N) — CONDITIONAL PASS, subject to Required Fixes R2, R3, R4, R5, R9, R10, R11, R13

B2 is well-built on falsification discipline — its §9 explicitly adopts the red team's bar, labels KILL vs NARROW per test, and sets absolute bars in several places (F1 ≥10 pp, F2 device-only within 5 pp / LOCO drop ≥15 pp, F7 within 10 pp, F9 ICC ≥0.5). The PXT864 correction is correctly applied (§11.4, C24) and PXT864 is cited nowhere as a live precedent. The citation spot-checks came back stronger than expected: Cao 2025, Thies 2025, Luz/ADReSS, Pedersen ch. 11, Jang 2026, and the Interspeech 2026 phone-call study all verified against primary sources.

The conditions are factual, not structural. B2 contains three verifiable factual errors (BirdNET v2.4 date, "6,522 bird species", Front. Aging Neurosci. date) and one probable misattribution (the "as much as a decade" claim). A document whose selling point is settled figures cannot stage with wrong settled figures. The remaining required fixes are citation hygiene (uncited T6 accuracy, unnamed mPower source, PXT864 quote wording).

**Neither document is rejected. Neither is ready to stage as-is.**

---

## 2. Cross-consistency table — B1 vs B2 (shared facts)

| # | Shared fact | B1 | B2 | Verdict |
|---|---|---|---|---|
| C-1 | Bye library size | 100 SALS donors (V13, §2.6) | 100-donor library (§2.2, C22) | CONSISTENT |
| C-2 | Bye drug-screen n | Screen on **16** SALS donors (V13, §2.6) | Screen on **16** SALS donors (§2.2, C22) | CONSISTENT with each other; BOTH IMPRECISE against the primary — see C-2a |
| C-2a | Bye screen n, primary text | — | — | **FLAG.** The Nature article's methods state "Drug screening/testing was conducted using **7–16** sporadic ALS donors" (found in this review's search of the primary text). "16" is the maximum, not a uniform n, and the combination-validation donor n is not separately stated in either document. Both documents share the same oversimplification. Required Fix R2. |
| C-3 | Bye: 107 drugs, 97% failed, 3 hits (riluzole, baricitinib, memantine) | V13: 107 at 2.5 µM; 97% failed; 3 rescued | §2.2: 107 trial drugs; "fewer than 5%" rescuing; same 3 drugs | CONSISTENT (97% failed = 3% rescued, inside "fewer than 5%") |
| C-4 | Bye: combination benefit, NOT formal synergy (no "Bliss" in full text) | V13, §8.1: combination benefit only | §2.2, C22: combination benefit only, "no Bliss" | CONSISTENT |
| C-5 | Bye: triple combo 100% donors responding, min rescue 16.5 days; memantine+riluzole +12.5 days (P=0.0109) | V13 | Not stated (omitted) | NO CONFLICT (omission, not contradiction) |
| C-6 | Bye: LD50 extension 30.3 days (p<0.0001) is review-reported, not primary | V13: stated as review-reported (PMC13292465) | Not stated (omitted) | NO CONFLICT |
| C-7 | PXT864 stopped 14 Feb 2023; no Phase 3; partner sought; refocus PXT3003 | V18, §8.3, §12.2 | §11.4, C24, ref 21 | CONSISTENT; both verified against the Pharnext release in this review |
| C-8 | PXT864 Phase 2: 45 treatment-naïve mild-AD patients, 36 weeks, single-blind, historical-placebo comparison, no concurrent control | V18 | §11.4 | CONSISTENT |
| C-9 | AGI-183: no public record; no BCL-XL stabiliser pharmacology known to exist | §7.1 (detailed), status box | §11.4: records only, "B1's territory" | CONSISTENT |
| C-10 | Ovadia patent family: priority 23 May 2011; EP 3263127 B1 granted 21 Aug 2019; US 10,288,622 B2 granted 14 May 2019, Active | V16, §10.2 (full detail incl. CA2836503C granted 2020-09-22) | §11.4 (summary: same priority/grant dates, Active) | CONSISTENT on every date B2 states. B2 omits the direction (high pAkt → responsiveness to an Akt-raising peptide) and the internal tension B1 notes (V16/§10.2). A reader of B2 alone would not know the patent runs opposite to MPS. Minor; see R-fix note in §6. |
| C-11 | Ovadia: no peer-reviewed journal article found; patent is prior art regardless | §10.4–10.5 | §11.4 (implies; does not restate the journal-article search) | CONSISTENT |
| C-12 | Navitoclax thrombocytopenia N=26: 14/26 (53.8%) all-grade, 10/26 (38.5%) grade 3/4 | V9, §1.5 | Not cited | NO CONFLICT |
| C-13 | AZD5991: post-hoc hs-troponin T 54/65 (83.1%) after any dose; 14/31 pre-dose; 3 objective responses in 78 | V1, §2.2 | Not cited | NO CONFLICT |
| C-14 | Foundation standing facts (Entity B20260196664; Articles 2026-04-24; SOS 2026-04-30; EIN 2026-05-07; no 501(c)(3) letter; AGI Corp EIN only; W3/SmartCiti.X/Delaware proposed not formed) | Status box | Status box | CONSISTENT, verbatim-equivalent |
| C-15 | "33 named W3 sub-series in the April 2026 internal list" — never 35 | Status box | Status box | CONSISTENT |
| C-16 | Macaulay Library 3.2M+ recordings | Not stated | Status box, §2.5, §3.2 | B2 ONLY — internal check in §2-B below |
| C-17 | BirdNET v2.4 covers 6,522; 11,000+ is the V3.0 platform figure | Not stated | Status box, §2.5, C12 | B2 ONLY — **ERROR found** (see §2-B) |
| C-18 | Xeno-canto ~1,040,000 recordings (NOT 1,111,111) | Not stated | Status box, §2.5, C13, §3.2 | B2 ONLY — **STALE** (see §2-B) |
| C-19 | Perch 2.0: 14,795 classes (14,597 species + 198 general); trained on 1,542,778 recordings | Not stated | Status box, §2.5, §5.5, C12/C15, ref 24 | B2 ONLY — classes/species split VERIFIED in this review; recording total not confirmed from returned snippets (see §4) |
| C-20 | Answer ALS 1,000-line iPS analysis did not report survival deficits etc. (GAP-ALS-13) | §2.6 | Not stated | NO CONFLICT |

### 2-B. B2-only settled figures — internal check (this review's findings)

- **BirdNET v2.4 date — ERROR.** B2 (status box, §2.5) dates v2.4 to "March 2025". The BirdNET-Analyzer README (found in this review's search) dates V2.4 to **June 2023** ("V2.4, June 2023 — more than 6,000 species worldwide"). March 2025 is not the v2.4 release date. Required Fix R3.
- **BirdNET "6,522 bird species" — IMPRECISE.** The same README states "6,522 classes (incl. 10 non-event classes)". 6,522 is a class count, not a species count; the species count is 6,512 by that arithmetic (6,522 − 10). B2's phrasing overstates species by 10 and conflates classes with species — the exact class/species distinction B2 itself handles correctly for Perch. Required Fix R3.
- **Xeno-canto ~1,040,000 — STALE/LOW.** The Xeno-canto founder's page (few.vu.nl/~rplanque) currently states "about **1,100,000** recordings". Wikipedia states "over 1,000,000". B2's 1,040,000 is therefore already ~60,000 below the founder's current figure. The instruction "do not use 1,111,111" remains sound (that figure is not the settled count either), but 1,040,000 needs re-dating or softening. Required Fix R4.
- **Macaulay 3.2M+ — SOURCE-DEPENDENT.** A Cornell alumni piece (Mar 2025) states "more than 2.7 million audio recordings"; a secondary source states "over 3.2 million audio recordings". B2's 3.2M+ is plausible for Nov 2026 but the two sources in this review disagree by ~500k, so the figure needs a dated source citation, not bare assertion. See §6, gap B2-G12.
- **Perch 2.0 — classes VERIFIED.** The Perch 2.0 paper (arXiv:2508.04665) states "14,795 different classes of which 14,597 are species labels and the remaining 198 classes are general sound event classes". B2's split is exact. The "1,542,778 recordings" training total was not confirmed in the snippets returned by this review's search and is marked accordingly in §4; it is not contradicted, only unconfirmed here.

---

## 3. B1 against the red-team report (B3)

Red-team findings as enumerated in the task: (1) novelty withdrawal + reframing; (2) "there is no drug" as gating fact; (3) Bye fix; (4) AZD5991/navitoclax exactness; (5) PHP.eB correction; (6) PXT864 status; (7) F1 upgrade (continuous primary + within-line manipulation + second-stressor replication + quantitative stabiliser bar).

| # | Red-team finding | Incorporated in B1? | Assessment |
|---|---|---|---|
| 1 | Novelty withdrawal + reframing | YES — status box, V16, §6.6 (F6 closed), §10.5 table, §12 (GAP-FLAG-2 closed as refutation) | **Genuine.** The withdrawal is stated in the status box, the reframe (method, not biomarker idea, is the contribution) is explicit, and the narrowed reformulation is correctly labelled "candidate, NOT asserted" pending its own documented search (GAP-MPS-2). The Ovadia direction (opposite) and the active-US-patent counsel flag (D-PAT) are carried. No passage in B1 still claims biomarker novelty. |
| 2 | "There is no drug" as gating fact | YES — status box, §1.3, §7.1, §9.1 item 1, §9.3 | **Genuine.** B1 carries the red team's strongest objection verbatim in substance ("currently untestable, not merely untested", §7.1) and makes Gate 0b the invention of a new pharmacology, not routine characterisation. The two arms' fates are kept separate (§6.6, §7.2). |
| 3 | Bye fix (screen 16 not 100; combination benefit, no Bliss synergy) | YES, with a precision gap — V13, §2.6, §8.1, App. C | **Substantially incorporated, one layer short.** The 16/100 distinction and the no-synergy correction are applied everywhere Bye is cited. But the primary text says screening used **7–16** donors (see C-2a), so the flat "16" is itself an overstatement, and the combination-validation donor n is never stated. Required Fix R2. |
| 4 | AZD5991 / navitoclax exactness | YES — V1 (with post-hoc caveats), V9 (N=26), §1.5, §2.2 | **Genuine, one rounding inconsistency.** V1's post-hoc vs protocol-AE distinction (54/65 retrospective vs 8/78 recorded) is exact and matches the Desai abstract verified in this review. V9's N=26 percentages are exact. Trivial defect: the response rate appears as 3.8% (V1 table) and 3.85% (§2.2); standardise to "3/78 (3.8%)" (R14). |
| 5 | PHP.eB correction (2018 papers tested PHP.B, not PHP.eB; Chan 2017 + Hordeaux 2019 for the Ly6a link) | YES — §4.7 (full correction with all four citations), §12.2 item 6 | **Genuine.** The correction is stated with the right capsid attribution and the right mechanism citations. |
| 6 | PXT864 status (stopped 14 Feb 2023; no Phase 3; historical-placebo Phase 2) | YES — V18, §8.3, §12.2 item 6 | **Genuine, one wording drift.** Dates, phase, and historical-placebo caveat are all correct and verified in this review. Wording drift: B1 quotes the stop reason as "insufficient for commercial exploitation" (V18, §8.3); the press release wording per the red team and the Euronext release is "insufficient for commercialization in the short or medium term". Required Fix R10 (quote exactly). |
| 7 | F1 upgrade (continuous primary; PI3K within-line manipulation; second-stressor replication; quantitative stabiliser bar; quantified minimum meaningful interaction) | MOSTLY — §3.3, §3.5 rule 1, §4.5, §6.1, §6.7 | **Substantially incorporated, with the central quantification deferred — the one superficial incorporation in B1.** Continuous primary: adopted. PI3K manipulation: adopted as part of the primary falsification design. Second-stressor replication: adopted. Stabiliser bar: adopted quantitatively (§6.7: ≥1.5× retrotranslocation, ≥20% EC50 shift, knockdown abolition). **Quantified minimum meaningful interaction: NOT quantified.** §3.3 rule 1, §3.5 rules 1 and 6, and §4.5 all define the *form* (EC50 difference between lowest and highest pBad quartiles) but defer the *number* to "the executing lab at pre-registration time, from the pilot". The red team asked for a pre-registered quantitative minimum; B1 pre-registers a formula for computing one later. That leaves the exact failure mode the red team identified (a null that can be argued about) partly open. Required Fix R1. Two further soft spots: (a) the PI3K manipulation has no quantitative bar of its own ("moves in the predicted direction" — by how much?); (b) F1's kill logic is undefined when (a)+(b) hold but (c) (second-stressor null) fails — see §6 and R8. |

**B1 red-team score: 6 of 7 fully incorporated; 1 (F1 quantification) incorporated in form only.**

---

## 4. B2 against the red-team report (B3)

The red team's B2-relevant findings are (i) the PXT864 correction and (ii) the falsification bar (continuous primary analysis, absolute bars instead of relative "best of a bad lot" rules, KILL vs NARROW labels).

| Red-team item | Incorporated in B2? | Assessment |
|---|---|---|
| PXT864 correction | YES — §11.4 (full corrected status, dates, trial numbers, historical-placebo caveat), C24, ref 21 | **Genuine.** PXT864 appears nowhere as a live or successful precedent. Same wording drift as B1: "insufficient for commercial exploitation" vs the release's "insufficient for commercialization in the short or medium term" (R10). |
| Falsification bar — continuous primary | YES — §9 intro (explicitly invokes the red-team lesson), F3 (continuous correlation + mixed model, median split demoted to sensitivity check) | **Genuine.** B2 is the better of the two documents on this point: it names the red-team criticism of dichotomised tests and applies the continuous-primary rule to its own longitudinal endpoint. |
| Falsification bar — absolute bars, KILL vs NARROW | YES — §9: F1 ≥10 pp over context baseline; F2 device-only within 5 pp / LOCO drop ≥15 pp; F7 within 10 pp of LOSO; F9 ICC ≥0.5; F5/F8 labelled NARROW with the re-statement rule (a narrowed claim is a new claim requiring new pre-registration) | **Genuine, with two deferred numbers.** F3's minimum meaningful correlation is deferred to the pilot ("e.g. |r| ≥ 0.3 — the number is set from the pilot's observed variability before the confirmatory cohort is locked"; GAP-VAP-3 admits it is not yet set). F4's ON/OFF bar is likewise "set from the pilot, not copied from that paper". The pattern is the same as B1's R1: the *shape* of the bar is pre-registered, the *number* is not. This is a lesser defect in B2 than in B1 because F1, F2, F7, and F9 *are* numerically specified — but F3/F4 are the longitudinal claim's kill tests, so the deferral matters. Required Fix R1 applies to B2's F3/F4 numbers as well (state the number, or record an explicit owner + deadline for setting it from the pilot before confirmatory lock). |
| Falsification bar — scope honesty | YES — §9 F4 scope note (kills PD longitudinal only; ALS/AD have no equivalent manipulation), §11.3 summary | **Genuine.** B2 states the asymmetry rather than hiding it. |

**B2 red-team score: both items incorporated; the falsification bar is numerically specified except for the F3/F4 thresholds, which are deferred.**

---

## 5. Citation spot-checks (independent verification by this review)

### 5A. B1 — 7 references checked

| # | Reference as cited in B1 | Verdict | Evidence / note |
|---|---|---|---|
| B1-1 | Rohn et al. 2008, *J Neurosci* 28(12):3051–3059 — Bcl-2 overexpression in 3xTg-AD mice limits caspase-9, reduces plaques/tangles, improves memory (V15, replacement for withdrawn Raghupathi 2005) | **VERIFIED** | PubMed/PMC: "Lack of Pathology in a Triple Transgenic Mouse Model of Alzheimer's Disease after Overexpression of the Anti-Apoptotic Protein Bcl-2", *J Neurosci* 19 Mar 2008;28(12):3051–3059, doi:10.1523/JNEUROSCI.5620-07.2008, PMID 18354008. Abstract confirms limited caspase-9 activation, reduced caspase cleavage of tau, attenuated APP/tau processing, reduced NFTs and extracellular Aβ deposits, improved place recognition memory. The replacement citation is correct; B1's §2.5 correction is validated. |
| B1-2 | Datta et al. 1997, *Cell* 91:231–241, PMID 9346240 — Akt phosphorylates BAD, blocks BAD-induced death of primary neurons | **VERIFIED** | PubMed: *Cell* 1997 Oct 17;91(2):231–41, doi:10.1016/S0092-8674(00)80405-5, PMID 9346240. Abstract: "Akt phosphorylates BAD in vitro and in vivo, and blocks the BAD-induced death of primary neurons in a site-specific manner." Exact as cited. |
| B1-3 | Ovadia et al., US 10,288,622 B2, granted 14 May 2019, Active; EP 3263127 B1 granted 21 Aug 2019; priority 23 May 2011 | **VERIFIED** | Google Patents US10288622B2: publication 2019-05-14, status Active, prior-art date 2011-05-23, inventors Ovadia/Cohen/Herkel/Margalit/Pevsner-Fischer, assignees Yeda / Universitätsklinikum Hamburg-Eppendorf. Specification confirms "high levels of pAkt and high levels of pAkt:tAkt ratio (e.g. above 1) correlate with responsiveness to treatment of ALS with the peptides of the invention" and "low Akt phosphorylation … indicate rapidly progressing ALS". The CA2836503C grant date (2020-09-22) stated in B1 was not checked in this review's searches — not contradicted, only unconfirmed here. |
| B1-4 | Rice et al. 2019, *PLoS ONE* 14(5):e0217657, PMID 31150457 — high pAKT (S473) marks sensitivity to combined MCL-1 + BCL-2/xL inhibition (maritoclax + navitoclax, NSCLC lines) | **PARTIAL** | Existence and central claim VERIFIED: PLOS ONE 14(5):e0217657, doi:10.1371/journal.pone.0217657, published 31 May 2019; abstract confirms "a high level of phosphorylated AKT (S473) was identified as a marker for sensitivity to the combination treatment" in a 9-line NSCLC panel with maritoclax + navitoclax. The specific statistics B1 quotes (Bliss-synergy correlation R² = 0.759, p = 0.0022) were **not confirmed** from the abstract/snippets returned; they require a full-text check. B1's qualification (preclinical cell lines, not a validated biomarker, measures pAKT not pBad) is correct. |
| B1-5 | Steckley et al. 2007, *J Neurosci* 27:12989–12999, PMID 18032672 — PUMA dominant regulator of oxidative-stress BAX activation / neuronal apoptosis | **VERIFIED** | Citation confirmed: *J Neurosci* 2007 Nov 21;27(47):12989–12999, doi:10.1523/JNEUROSCI.3400-07.2007; PMC figure captions confirm Puma required for oxidative-stress-induced Bax activation. B1's rodent-cortical-neuron qualification is correctly stated. |
| B1-6 | Desai et al. 2024, *Clin Cancer Res* 30(21):4844–4855, PMID 39167622 — AZD5991 post-hoc hs-troponin T 54/65 (83.1%) after any dose; 14/31 pre-dose; 8/78 (10.3%) protocol AE; development halted | **VERIFIED** | PMC11528199 / PubMed abstract confirms all figures verbatim: "elevated troponin T in 14/31 patients before any AZD5991 dose and in 54/65 patients after any AZD5991 dose at or after Cycle 1"; "Asymptomatic elevations … in eight (10.3%) patients"; "These issues precluded further clinical development of AZD5991." |
| B1-7 | Edlich et al. 2011, *Cell* 145:104–116, PMID 21458670 — BCL-XL retrotranslocates BAX | **VERIFIED** | PMC3070914 / PubMed: *Cell* 2011 Apr 1;145(1):104–116, doi:10.1016/j.cell.2011.02.034, PMID 21458670. FLIP reveals constant retrotranslocation of WT Bax; "Bcl-xL increases the rate of Bax retrotranslocation." Exact as cited. |
| B1-8 (extra) | Llambi et al. 2011, *Mol Cell* 44:517–531, PMID 22036586 — MODE 1 / MODE 2 | **VERIFIED** | PMC3221787: *Mol Cell* 2011;44(4):517–531, doi:10.1016/j.molcel.2011.10.001. Abstract confirms MODE 1 (sequestering direct-activator BH3-only proteins) vs MODE 2 (binding active BAX/BAK); "MODE 1 sequestration is less efficient and more easily de-repressed." B1's qualification (cancer/developmental models; neuronal transfer assumed) is correct. |
| B1-9 (extra) | c-Jun/BIM paper, *Neuroscience* 2019, DOI 10.1016/j.neuroscience.2018.12.026 | **VERIFIED** | ScienceDirect: *Neuroscience* Vol 399, 10 Feb 2019, pp 117–124, "c-Jun/Bim Upregulation in Dopaminergic Neurons Promotes Neurodegeneration in the MPTP Mouse Model of Parkinson's Disease". Abstract confirms BIM transcriptionally induced in SNpc dopaminergic neurons after MPTP; dopaminergic-neuron-specific *Bim* null (BimΔDat) mice resistant to MPTP neurotoxicity; induction c-Jun-dependent. B1's author line "Li M, et al." in the reference list was not confirmed against the author list in the returned snippets — trivial; the paper itself is verified. |
| B1-10 (extra) | Bye et al. 2026, *Nat Neurosci* 29:40–52, PMID 41286450 | **VERIFIED with the C-2a caveat** | Nature/PubMed confirm: library from 100 SALS patients; 97% of drugs failed; combination of riluzole + memantine + baricitinib significantly increased survival. The primary text's methods line "Drug screening/testing was conducted using 7–16 sporadic ALS donors" is the basis for R2. |

**B1 spot-check summary: 7 VERIFIED, 1 PARTIAL (Rice R²/p unconfirmed from snippets), 1 VERIFIED-with-caveat (Bye donor n). No NOT-FOUND.**

### 5B. B2 — 8 references checked

| # | Reference as cited in B2 | Verdict | Evidence / note |
|---|---|---|---|
| B2-1 | Cao et al. 2025, *npj Parkinson's Dis* 11:57, doi:10.1038/s41531-025-00913-4 — PD speech/language biomarkers review | **VERIFIED** | PMC11933288 / PMID 40128529: *npj Parkinson's Dis* 2025 Mar 24;11:57. Narrative review; abstract and text confirm speech impairments "affecting up to 90% of PwPD", alterations that "often precede the defining motor signs and PD diagnosis by as much as a decade", and the acoustic correlates B2 lists (reduced loudness, monopitch/monoloudness, harsh/breathy voice, imprecise articulation, lower HNR/CPP, restricted VSA). Note: the "as much as a decade" phrasing is in **Cao**, which bears on B2-7 below. |
| B2-2 | Thies et al. 2025, *npj Parkinson's Dis* 11:105, doi:10.1038/s41531-025-00959-4 — levodopa ON/OFF speech, 78 participants (51M/27F), 200 mg levodopa, AUC 0.81 | **VERIFIED** | PMC12048546 / PMID 40316531: *npj Parkinson's Dis* 2025 May 2;11:105. Abstract confirms 78 participants (51 males, 27 females), OFF ≥12 h withdrawal vs ON after 200 mg soluble levodopa, levodopa improves phonatory–respiratory functions and speech planning while articulation remains unaffected. Full text confirms ON/OFF discrimination AUC 0.81. Exact as cited. |
| B2-3 | Luz et al. 2020, arXiv:2004.06833 (ADReSS, INTERSPEECH 2020) — 156 participants (78 AD/78 non-AD); acoustic baseline 62.5%, linguistic 76.85%; MMSE RMSE 6.14 acoustic / 5.21 linguistic | **VERIFIED** (RMSE second value partially confirmed) | arXiv:2004.06833 confirms: 1,955 segments from 78 non-AD subjects and 2,122 from 78 AD subjects; "Machine learning methods operating on automatically extracted voice features provide a baseline accuracy of up to 62.5% on the AD classification task, while linguistic features extracted from manually produced transcripts yielded 76.85% accuracy". The RMSE figures (6.14 acoustic / 5.21 linguistic) appear in B2 §2.3; the returned snippet truncated at "A baseline RMSE of 6.14 and 5…" — the 6.14 is confirmed, the 5.21 is consistent with the paper but was not fully visible in the snippet. Treat as verified on the accuracies, partial on the RMSE pair. |
| B2-4 | Perch 2.0, arXiv:2508.04665 — 14,795 classes (14,597 species + 198 general); trained on 1,542,778 recordings | **PARTIAL** | Classes/species split VERIFIED: the Perch 2.0 paper states "the data contains 14,795 different classes of which 14,597 are species labels and the remaining 198 classes are general sound event classes". The training total "1,542,778 recordings" was **not confirmed** in the snippets returned by this review's search (the paper's training-data section lists Xeno-Canto, iNaturalist, Tierstimmenarchiv, FSD50K without the total visible in the snippet). Not contradicted; needs a one-line full-text confirmation before staging. The "7 August 2025" date in B2 §2.5 was likewise not confirmed here. |
| B2-5 | BirdNET v2.4 covers 6,522 bird species; March 2025 | **PARTIAL (two errors)** | The 6,522 figure exists, but as **classes**, not species: BirdNET-Analyzer README states "6,522 classes (incl. 10 non-event classes)". The date is wrong: the same README dates V2.4 to **June 2023**, not March 2025. The 11,000+ V3.0 figure is corroborated by secondary sources as a separate preview version, so B2's version separation is correct; only the v2.4 date and the species/classes wording are wrong. Required Fix R3. |
| B2-6 | Pedersen et al. (eds.), *Voice-related Biomarkers*, Springer 2026, ch. 11 — >80% of ALS develop dysphonia/dysarthria; 48% dysphonia at onset; speech impairment may begin up to 3 years before diagnosis | **PARTIAL** | Chapter VERIFIED as existing and the two percentages VERIFIED verbatim: Springer ch. 11 (Camesasca; first online 3 Jan 2026; doi:10.1007/978-3-032-03134-1_11) states "Over 80% of individuals with Amyotrophic Lateral Sclerosis develop dysphonia and dysarthria, primarily a mixed spastic-flaccid subtype" and "48% of the patients have dysphonia at onset (mainly bulbar phenotype)". The "up to 3 years before diagnosis" figure was **not confirmed** in the returned snippets — it may be in the chapter text, but this review could not verify it from the search results. Downgrade to "not confirmed here" rather than treating it as established. |
| B2-7 | Bioengineering 2026;13:1037 — "vocal changes can emerge early … by as much as a decade" (B2 §2.1, C5) | **PARTIAL (probable misattribution)** | The paper EXISTS and is correctly cited: Yuan et al., *Bioengineering* 2026 Sep 6;13(9):1037, doi:10.3390/bioengineering13091037, PMID 42791909; abstract confirms "Hypokinetic dysarthria is estimated to affect the large majority of individuals with PD". The "as much as a decade" phrasing was **not found** in the Bioengineering abstract/snippets returned — but the near-identical phrasing IS in Cao 2025 (B2-1 above: "precede the defining motor signs and PD diagnosis by as much as a decade"). B2 likely attributes Cao's sentence to Bioengineering. Required Fix R9: verify against the Bioengineering full text or re-attribute to Cao 2025. |
| B2-8 | Jang 2026, *J Speech Sci* 18(3), doi:10.13064/KSSS.2026.18.3.109 — vowel duration in ALS: 53 speakers (17 controls, 36 patients); ~20% longer vs controls, 23% longer vs non-dysarthric; only measure significant in both contrasts | **VERIFIED** | Korean Society of Speech Sciences, Vol.18 No.3, 30 Sep 2026, pp. 109–115: abstract confirms 53 speakers (17 controls, 36 patients), single standardised reading passage, vowel duration the only measure significant in both contrasts and surviving multiple-comparison correction, "~20% longer than controls and 23% longer than patients without dysarthria". Exact as cited, including the HNR/F0-range/pause dissociation. |
| B2-9 (extra) | Haghbin et al., Interspeech 2026 — 175 participants, phone-call speech, structured data AUC 0.74, best fusion AUC 0.92, F1 83.08 | **VERIFIED** | ISCA Archive (Interspeech 2026, 27 Sep–1 Oct 2026, Sydney): 175 participants; structured clinical data alone AUC 0.74; adding phone calls AUC 0.76; best configuration (EHR + check-in call + patient–nurse communications) AUC 0.92 and F1 83.08. Exact as cited in B2 §2.3 / ref 14. |
| B2-10 (extra) | Ramineni et al. 2026, *Front. Aging Neurosci.* 18:1975870, doi:10.3389/fnagi.2026.1975870 — speech + sMRI review | **VERIFIED (with the date error)** | Frontiers: published **27 October 2026**, Vol. 18:1975870, doi as cited. B2 §2.3 cites it as "17 Oct 2026" — the day is wrong (17 vs 27). The paper exists and the DOI is correct; only the in-text date is wrong. Required Fix R5. |
| B2-11 (extra) | Xeno-canto ~1,040,000; Macaulay 3.2M+ | **PARTIAL (stale / source-dependent)** | Xeno-canto founder's page currently states "about 1,100,000 recordings"; Wikipedia "over 1,000,000". B2's 1,040,000 is below the founder's current figure. Macaulay: Cornell alumni (Mar 2025) "more than 2.7 million audio recordings" vs a secondary source "over 3.2 million audio recordings" — the two sources disagree, so B2's 3.2M+ needs a dated source. Required Fix R4 / gap B2-G12. |

**B2 spot-check summary: 5 VERIFIED (Cao, Thies, ADReSS accuracies, Jang, Interspeech 2026, Ramineni existence), 5 PARTIAL (Perch recording total, BirdNET date/species, Pedersen 3-year lead, Bioengineering decade attribution, Xeno-canto/Macaulay counts). No NOT-FOUND.**

---

## 6. Gaps — what each document fails to address, with the reviewer question

### B1 gaps

| # | Gap | Reviewer question |
|---|---|---|
| B1-G1 | **No ALS-specific BCL-2-family evidence exists in the document (admitted as GAP-FLAG-7), yet ALS is rung 1.** The mechanism chain is built from rodent cortical neurons (Steckley), mouse MPTP (BIM), and mouse AD (Rohn). | "Why does the validation ladder start in the disease with the least direct BCL-2 evidence? What ALS-specific result would you need before rung 1 is even worth running — and why is that result not a Phase 0 gate?" |
| B1-G2 | **PI3K-inhibitor manipulation is unnamed and unbarred.** No inhibitor named, no dose, no quantitative bar for "moves in the predicted direction", no toxicity control. PI3K inhibition itself impairs survival via mTOR/FOXO, independent of BAD. | "Which PI3K inhibitor, at what dose, and how do you distinguish 'lowering pAkt increased the stabiliser's benefit' from 'PI3K inhibition made the neurons sicker, so everything looks bigger'? What is the numerical bar for this manipulation passing, and what is its own vehicle + inhibitor-only control?" |
| B1-G3 | **Between-line phospho variance is never quantified or gated.** The continuous interaction is only testable if pBad varies enough between donor lines; if all lines cluster, the interaction is unpowered regardless of N. | "What between-line variance (or ICC) in baseline pBad would make the stratification untestable, and what happens if the pilot shows the lines barely differ?" |
| B1-G4 | **Sequencing ambiguity: does the vector-only arm wait for D1?** §6.6/§9.3 say the gene-therapy arm survives independently, but §3.1 prerequisite 1 and the Phase 0 gates read as blocking all downstream work until D1 resolves. | "Can the AAV-MCL1-only factorial start before a stabiliser exists, or does the whole programme idle on D1? State the sequencing in one sentence." |
| B1-G5 | **Stressor mechanism unexamined.** Chronic glutamate kills partly via calcium overload and necrosis, not necessarily via BAX/BAK MOMP; no evidence is cited that glutamate-stressed iPSC motor neurons die through MOMP. | "What proportion of glutamate-induced death in your model is BAX/BAK-dependent? If a BAX/BAK inhibitor does not rescue glutamate death, does the model or the hypothesis fail?" |
| B1-G6 | **BH3-profiling transfer has no numeric acceptance criteria.** The pilot "validates" mitochondrial yield, peptide delivery, and JC-1 readouts, but no yield, purity, or dynamic-range threshold is stated. | "What mitochondrial yield, what EC50 shift under a positive control, and what coefficient of variation would count as 'BH3 profiling works in neurons' — and what counts as failure?" |
| B1-G7 | **MCL1 dose undefined.** No target fold-change, no MOI rationale, no upper bound; overexpression level itself changes priming. | "What MCL1 fold-change are you aiming for, why that level, and at what fold-change does the vector arm become uninterpretable?" |
| B1-G8 | **Rohn 2008 is a developmental-overexpression model.** Bcl-2 is overexpressed in all postmitotic neurons from development; the AD rung tests adult intervention. B1 never notes this. | "How do you separate a developmental neuroprotection effect in Rohn's mice from an adult-intervention effect your design would test?" |
| B1-G9 | **D3 (AGI-006/010 engagement) has no assay and no bar.** | "Engagement by what assay, at what IC50/Kd threshold, and does engagement without stabilisation (the §6.7 bar) count as a D3 'yes'?" |
| B1-G10 | **No cost, funder, or timeline for Phase 0.** Admitted (GAP-FLAG-5), but Phase 0 is the critical path. | "What does Gate 0a–0c cost, who pays, and what is the decision date if no compound is produced?" |
| B1-G11 | **iPSC monoculture lacks glia, vasculature, and immune context; no discussion of what that omission does to priming.** | "Which non-neuronal contributors to priming are you assuming away, and what is the first co-culture test?" |
| B1-G12 | **Sporadic ALS is absent from rung 1** (Q331K familial only), despite the Bye-vs-Answer-ALS discrepancy being the document's own standing warning. | "Given GAP-ALS-13, why does rung 1 contain no sporadic-ALS lines, and at what point do sporadic lines enter — before or after the ALS verdict?" |

### B2 gaps

| # | Gap | Reviewer question |
|---|---|---|
| B2-G1 | **Device variability: controlled in design, but no harmonisation method is named.** Fixed device per cohort + device covariate + leave-one-device-out + F2 bar are specified; no batch-correction / calibration method (e.g. ComBat-style harmonisation, reference-signal calibration) is named, and the remote protocol's calibration task has no acceptance rule. | "When devices differ, what harmonisation is applied — and what do you do if the fixed device is discontinued mid-study? Is device variability controlled, or only logged and covaried?" |
| B2-G2 | **F2 is vacuous in a single-device Phase 1.** A device-only model cannot be fitted where there is no device variance; F2 can only bite in multi-device Phase 0/2. | "Which phase can actually fail F2? If Phase 1 uses one device throughout, what protects it against a device artefact it cannot detect?" |
| B2-G3 | **No literature anchor for expected annual vocal change.** No prior estimate of within-person change per year in any feature family is cited, so the 12-month window and the 60+60 N have no basis beyond the pilot. | "How much does jitter/shimmer/pause duration change per year in PD, and is 12 months enough to see it above test–retest noise? Cite one number." |
| B2-G4 | **ASR system unnamed (GAP-VAP-4) and no WER acceptability bar.** Dysarthric speech degrades ASR; Arm L (the AD primary arm) collapses if WER is high. | "What word-error rate on dysarthric speech would disqualify an ASR system for Arm L, and what happens to the AD arm if no system clears it?" |
| B2-G5 | **OFF-state sessions: no eligibility rule, no rescue plan.** "Only if clinically safe" is stated, but no criteria for who may withdraw levodopa ≥12 h, and no plan if withdrawal is intolerable. | "Who is eligible for an OFF session, who decides, and what happens mid-session if the participant cannot continue?" |
| B2-G6 | **Pilot n (20+20, two sessions) is too small to estimate ICC precisely, and no ICC precision is stated.** ICC estimates at n=20 have wide confidence intervals; an ICC ≥0.5 gate decided on n=20 is noisy. | "What is the confidence interval on a pilot ICC at n=20, and what ICC value (with what uncertainty) triggers exclusion of a feature family?" |
| B2-G7 | **Perch input conditioning unspecified.** Perch expects a specific sample rate / window; B2 records at 44.1 kHz and extracts log-Mel with librosa parameters, but resampling to Perch's expected input is never specified. | "What resampling is applied before the Perch embedding, and was the resampling validated not to distort jitter/shimmer-adjacent spectral features?" |
| B2-G8 | **Model-weights licensing asserted, not checked.** B2 asserts Perch weights via Kaggle and says the speech-encoder licence is "to be checked per use". | "What is the licence on the Perch v2 weights for clinical-research use, and does it permit the governed dataset release in Phase 3?" |
| B2-G9 | **ALS/AD have no manipulation analogue to F4.** B2 admits this (§9 F4 scope note). The longitudinal claim for two of three diseases therefore rests on correlation alone. | "What is the ALS/AD equivalent of a known, timed perturbation — or do those longitudinal claims carry a weaker falsification standard by design, and should they be graded down accordingly?" |
| B2-G10 | **Control matching is age/sex only.** Smoking, depression, respiratory disease, hearing loss, and reflux all change voice and are not matched or listed as exclusion/stratification variables. | "Which non-age/sex voice confounds are exclusion criteria, which are covariates, and which are unmeasured?" |
| B2-G11 | **Phase 0 minimum dataset undefined.** If PC-GITA access is refused, mPower access fails, and ADReSS DUA stalls, Phase 0 shrinks to UCI (31 subjects). | "What is the minimum Phase 0 dataset set, and can F1 be run at all on UCI alone? State the fallback before access requests go out." |
| B2-G12 | **Settled figures lack dated sources.** Macaulay 3.2M+, Xeno-canto ~1,040,000, Perch training total 1,542,778 are stated without a source-and-date line, so they rot silently (as the Xeno-canto figure already has). | "For each settled figure, what is the source and as-of date, and who re-checks it before staging?" |
| B2-G13 | **Retention period and deletion procedure unstated.** §7.3 requires a retention period in the ethics approval, but no period or deletion-on-withdrawal procedure is proposed even as a default. | "What is the default retention period, and what exactly happens to audio already collected when a participant withdraws?" |

---

## 7. Falsification-battery grades

### B1 battery — CAN KILL OUTRIGHT (with one soft spot)

- **F1 (strengthened):** kill-capable in principle — (a) continuous interaction null with CI excluding the minimum meaningful effect, **and** (b) within-line PI3K manipulation fails, **and** (c) null under the second stressor. The three-legged structure is the right design. **Soft spots:** (i) the minimum meaningful effect is deferred (R1), so leg (a)'s "CI excludes the minimum" cannot currently be evaluated; (ii) leg (b) has no quantitative bar; (iii) the verdict for (a)+(b) hold but (c) fails is undefined — is that a kill, a narrow, or an untested second stressor? (R8).
- **F2 (no combination benefit):** kill-capable for the combination claim. Clean.
- **F3 (assay failure, repeated across two runs):** kill-capable for H-MPS-3. Clean, with the two-run rule preventing a single bad run from killing the assay.
- **F4 / stabiliser bar (§6.7):** kill-capable for the small-molecule arm. Clean and quantitative (≥1.5× retrotranslocation, ≥20% EC50, knockdown abolition).
- **F5 (model failure):** kill-capable for the synergy prediction. Clean.
- **F6 (novelty):** already triggered and closed. Correct handling.
- **Overall:** the battery can kill the central claim outright (F1), the combination (F2), the small-molecule arm (F4), the assay transfer (F3-repeated), and the model prediction (F5). It is **not** a narrow-until-something-survives battery. Grade: **kill-capable; soften the verdict by one notch until R1 and R8 close.**

### B2 battery — CAN KILL OUTRIGHT (with two soft spots)

- **F1 (no separation on held-out subjects):** kill-capable for the cross-sectional claim. Clean and numerically specified (≥10 pp over context baseline, CI excluding zero).
- **F2 (features track recording conditions):** kill-capable for the device-agnostic claim, with absolute bars (device-only within 5 pp; LOCO-by-device drop ≥15 pp). **Soft spot:** vacuous in a single-device Phase 1 (B2-G2) — the test can only bite where device variance exists.
- **F3 (longitudinal change does not track clinical change):** kill-capable **only jointly with F4** ("both together kill"). Alone it narrows. **Soft spot:** the minimum meaningful correlation |r| is deferred to the pilot (GAP-VAP-3), so the "statistically significant but not meaningful" judgement cannot currently be applied.
- **F4 (ON/OFF manipulation fails, PD):** kill-capable for the PD longitudinal claim on its own — the strongest single test in the battery, correctly identified as such. **Soft spot:** its bar is deferred to the pilot ("set from the pilot, not copied from that paper").
- **F6 (leakage / negative-control failure):** kill-capable for the result and the pipeline. Clean.
- **F9 (test–retest reliability, ICC ≥0.5):** kill-capable for the affected families. Clean as a bar; noisy as a pilot estimate at n=20 (B2-G6).
- **F5, F8 (narrow-only) and F7 (narrow, then kill on second failure):** correctly labelled as narrowing, with the re-statement rule that a narrowed claim is a new claim requiring new pre-registration — the anti-goalpost-moving rule the red team demanded, properly applied.
- **Overall:** three tests (F1, F2, F4) can kill a central claim outright on their own; F3+F4 together kill the longitudinal claim; F6 can kill the pipeline. Grade: **kill-capable; soften by one notch until the F3/F4 numbers are set (R1) and the F2 single-device limitation is addressed (B2-G2).**

---

## 8. REQUIRED FIXES (coordinator must apply or route before staging for push)

These are ordered by importance. "Required" means the document should not be staged with the defect in place.

| # | Fix | Document / location | What to do |
|---|---|---|---|
| R1 | **Quantify the minimum meaningful effect (B1) and the F3/F4 bars (B2).** | B1 §3.3 rule 1, §3.5 rules 1/6, §4.5, §6.1; B2 §9 F3/F4, GAP-VAP-3 | State the number (B1: the quartile EC50 difference in stated units; B2: the minimum \|r\| and the minimum ON/OFF standardised difference), or record an explicit owner + deadline for setting it from the pilot *before* confirmatory lock, with the rule that confirmatory data collection cannot start until the number is locked. A formula for computing the number later is not a pre-registered bar. |
| R2 | **Bye screen n: replace flat "16 donors" with the primary-text range and state the combination-validation n.** | B1 V13, §2.6; B2 §2.2, C22 | The primary text states drug screening/testing used **7–16** SALS donors. Both documents must state the range (and the per-assay n where the paper gives it) and must state the donor n for the combination validation separately, rather than implying all 100 — or all 16 — were combination-tested. |
| R3 | **BirdNET v2.4: correct the date and the species/classes wording.** | B2 status box, §2.5, C12 | Change "v2.4 (March 2025)" to "v2.4 (June 2023)" per the BirdNET-Analyzer README, and change "6,522 bird species" to "6,522 classes (6,512 bird species + 10 non-event classes)" — verifying the 6,512 arithmetic against the source before asserting it; at minimum use "6,522 classes". |
| R4 | **Xeno-canto count: re-check live and date-stamp, or soften.** | B2 status box, §2.5, C13, §3.2 | The founder's page currently states ~1,100,000. Re-check the live count, record source + as-of date, and use the re-checked figure (or "over 1,000,000 (Nov 2026)"). Do not retain 1,040,000 as a settled figure. |
| R5 | **Front. Aging Neurosci. date: "17 Oct 2026" → "27 Oct 2026".** | B2 §2.3 | The paper (Vol. 18:1975870, doi:10.3389/fnagi.2026.1975870) was published 27 October 2026. Correct the in-text date. |
| R6 | **Venetoclax misplacement in the B1 inversion table.** | B1 §1.5 (MCL1 row) | Venetoclax is a BCL-2 inhibitor, not an MCL1 inhibitor. Remove it from the MCL1-inhibition list or re-label it explicitly as a combination partner used with MCL1 inhibitors (as in Desai 2024). |
| R7 | **Reconcile the catalog counts in one sentence.** | B1 §7.4 | "413 numbered entries (AGI-001–AGI-413) built from only 24 distinct SMILES" vs "336 HYPOTHETICAL structures and 0 verified" leaves 77 entries unaccounted for. State what the 413, the 336, and the 24 each count, and how they relate. |
| R8 | **Close the F1 kill-logic gap and bar the PI3K manipulation.** | B1 §6.1, §6.11, §3.3 | Define the verdict when (a)+(b) hold but (c) (second-stressor null) fails, and when (a) fails but (b) holds; and state a quantitative bar for the within-line PI3K manipulation (which inhibitor, what dose, what minimum increase in stabiliser benefit counts as "moves in the predicted direction", with its inhibitor-only control). |
| R9 | **"As much as a decade" attribution: verify or re-attribute.** | B2 §2.1, C5 | Verify the decade claim against the Bioengineering 2026 full text; if it is not there, re-attribute it to Cao et al. 2025, where the near-identical phrasing was confirmed in this review. |
| R10 | **PXT864 stop-reason quote: use the press-release wording.** | B1 V18, §8.3; B2 §11.4 | Standardise to "insufficient for commercialization in the short or medium term" (Pharnext, 14 Feb 2023). "Insufficient for commercial exploitation" is a paraphrase, not the quote. |
| R11 | **T6 "82–90%" discrimination figure is uncited — cite or delete.** | B2 §4.3 (Task T6) | The modulated-vowel row claims PD-vs-control discrimination of 82–90% "in one analysis" with no citation. Add the source or remove the figure. |
| R12 | **Clean stale self-references.** | B1 §3.3 ("§3.3 rule 3 in the earlier draft"), §4.2 (self-reference "(§4.2, §4.4)") | Remove or correct both; a staged document should not refer to an earlier draft. |
| R13 | **mPower "8,320 participants (systematic-review table)" — name the review or drop the number.** | B2 §2.4 | The figure is attributed only to an unnamed "systematic-review table". Name the review (with citation) or remove the participant count. |
| R14 | **Standardise the AZD5991 response-rate rounding.** | B1 V1 table (3.8%) vs §2.2 (3.85%) | Use "3 objective responses in 78 enrolled patients (3.8%)" everywhere. |

---

## 9. Optional polish (not blocking staging)

- **B1 §8.1:** "PXT864 (4 of 5 criteria met, the fifth absent)" and "Bye (3.5 of 5)" mix a count of criteria with the rubric's 0–2-per-criterion scoring (total /10). State both as scores out of 10 or as criterion counts, not both at once.
- **B2 §4.0 vs §4.1:** the Phase 0 gate is worded two ways — "published **or** pre-registered with data-access outcome documented" (§4.0) vs "Phase 0 report published" (§4.1 table). Pick one gate.
- **B1 §2.2:** the source's refs [6], [7], [9], [12], [13] are already flagged as not independently verified; consider dropping them from the reference list or marking them "not verified" there as well as in §2.2.
- **B2 ref 30** (2025 cross-toolkit comparative evaluation) has no DOI, journal, or authors. Add full citation details or mark as "details to be confirmed".
- **B2 §2.4:** the UCI Telemonitoring (5,875 recordings, 42 people) and Watkins (~2,000 recordings / >15,000 clips) figures were not spot-checked in this review; confirm them in a future verification pass.
- **B1 V16 / §10.2:** the CA2836503C grant date (2020-09-22) and the CA2836503A1 publication date were not confirmed in this review's searches; confirm against the patent record before external use.
- **B2 §2.5:** the Perch 2.0 date "7 August 2025" and the training total "1,542,778 recordings" were not confirmed from the snippets returned; confirm against the arXiv full text (one-line check).
- **B2 §2.2:** the "up to 3 years before diagnosis" figure (Pedersen ch. 11) could not be confirmed from the search snippets; confirm against the chapter text.
- **B1 §2.1 V13 / B2 §2.2:** consider adding the Bye paper's own statement that drug screening used 7–16 donors as the source note for R2, once R2 is applied.
- **Both documents:** the Ovadia internal-direction tension (B1 V16/§10.2) is worth one line in B2 §11.4 so a B2-only reader knows the patent's direction is opposite to MPS's — currently B2's summary omits direction entirely.

---

## 10. What this review did not find

- No cross-document contradiction on any shared *date, donor count, trial status, or Foundation fact* beyond the items listed above (C-2a, §2-B). The two documents agree with each other and with the red team on Bye, PXT864, AGI-183, Ovadia, and the Foundation facts.
- No failed citation among the 15 references spot-checked (0 NOT-FOUND). The failures found were precision errors (dates, classes-vs-species, ranges, attributions), not invented references — with the exception, already corrected by B1 itself, of the withdrawn Raghupathi 2005 citation, whose replacement (Rohn 2008) this review independently verified.
- No falsification battery that can only narrow. Both batteries contain multiple outright kill tests (B1: F1, F2, F3-repeated, F4, F5; B2: F1, F2, F4, F6, F9, F3+F4). The softness in each battery is deferred quantification (R1) and one undefined case (R8) / one vacuous-in-one-phase test (B2-G2), not an absence of kill tests.

---

*End of peer review. Verdicts: B1 CONDITIONAL PASS; B2 CONDITIONAL PASS. Required fixes R1–R14 must be applied or routed before staging for push.*
