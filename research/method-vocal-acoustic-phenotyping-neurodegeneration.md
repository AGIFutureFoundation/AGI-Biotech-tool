# Vocal Acoustic Phenotyping for Neurodegeneration (VAP-N)

**Method document — Research Lab Loop 2, Track B, Worker B2**
**Date:** 7–8 November 2026
**Status:** Hypothesis + protocol document. Local staging only. Not published, not sent, not pushed, not a clinical tool, not medical advice.
**Parent programme:** Research Lab Loop 2 (19:15 PST 7 Nov 2026 → ~07:15 PST 8 Nov 2026), deep interoperability + content research.
**Companion dossier files:** `research-lab-loop/dossier/animal-voice-decoding-lit-review.md` (WAVE bioacoustics base); `research-lab-loop/dossier/bioacoustics-github-survey.md`; `research-lab-loop/dossier/cross-disease-patterns.md` (grading discipline); `research-lab-loop/dossier/parkinsons-gaucher-lysosomal-program.md`; `research-lab-loop/dossier/als-compounds-lit-review.md`; `research-lab-loop/dossier/pattern-deep-dive-02-alzheimers-three-network.md`.

---

## Status box — read first

- **This document contains NO discovery, cure, treatment, diagnosis, detection, or result.** A "discovery" in this work is a novel, well-grounded **hypothesis** with an experimental design, a falsification test, and an evidence grade. VAP-N is a phenotyping research method to be tested. It is not a screening test, not a diagnostic test, and not a detector.
- **VAP-N must never be described as diagnosing, screening for, or detecting Parkinson's disease (PD), amyotrophic lateral sclerosis (ALS), or Alzheimer's disease (AD).** Its output is a longitudinal acoustic phenotype: a set of measured vocal features and their change over time against a person's own baseline, for research use, alongside clinical measures. Any future clinical use would require separate validation, regulatory review, and clinical oversight that do not exist here and are not proposed here.
- **Predicted vs demonstrated is absolute.** Computational predictions are predictions. Cross-disease and cross-species transfer is the hypothesis under test, not a finding.
- **Voice is identifiable biometric data.** A recording can identify its speaker, can reveal health information, and cannot be fully anonymised without destroying the signal under study (see §7). Consent, governance, and data minimisation are part of the method, not an appendix to it.
- **The Foundation has no wet lab and no clinic.** Every human-recording study in this document requires a partner institution, an ethics approval, and a data-governance agreement — none identified, none costed, none approached. State that plainly wherever this work is described.
- **Foundation standing facts:** AGI Future Foundation is a filed California Nonprofit Public Benefit Corporation (Entity No. B20260196664, Articles filed 2026-04-24, SOS approval 2026-04-30, EIN 2026-05-07). **No IRS 501(c)(3) determination letter is on file — not tax-exempt, donations not tax-deductible.** AGI Corp: EIN only, not formed. W3 / SmartCiti.X / Delaware series: proposed, not formed. "33 named W3 sub-series in the April 2026 internal list" — never 35.
- **Settled figures used in this document:** Macaulay Library 3.2M+ audio recordings (Nov 2026 — see §2.5 for the source-and-date note); BirdNET production model v2.4 (June 2023) covers 6,522 classes (incl. 10 non-event classes); the 11,000+ figure is BirdNET's current platform figure (V3.0 generation, developer preview from June 2026); Xeno-canto ~1,040,000 recordings (NOT 1,111,111 — unsettled, do not use the larger figure). **Xeno-canto re-check note (8 Nov 2026, peer-review fix R4):** the founder's page (few.vu.nl/~rplanque, Bob Planqué) now states "about 1,100,000 recordings". The loop's settled figure ~1,040,000 is retained in this document pending Mike's decision on whether to adopt the higher figure — the change is not made unilaterally here. Perch 2.0 (August 2025, arXiv:2508.04665) covers 14,795 classes (14,597 species + 198 general sound-event classes), trained on 1,542,778 recordings (verified against the paper's Table 1, 8 Nov 2026).

## Evidence-grade scale (applies to every claim in this document)

Adapted from `cross-disease-patterns.md`. The grade sits next to every load-bearing claim.

| Grade | Meaning | What it takes |
|---|---|---|
| **A** | Direct published evidence | Peer-reviewed evidence in the relevant disease/context, verified against the primary source in this pass or in a cited dossier file. |
| **B** | Mechanistic plausibility from adjacent evidence | Published mechanism or evidence in a different disease, model, or context that makes the claim plausible — but the transfer itself is untested. |
| **C** | Speculative | Coherent with known biology or known methods, but no direct evidence for the claim as stated; the test is the first evidence. |
| **UNVERIFIED** | Cannot be verified from a source in front of the author | Marked as such; never quoted as fact. |

**Rule:** a method is only as strong as its weakest load-bearing grade, and the grade is visible. A Grade C claim stated as if it were Grade A is the failure mode this document exists to prevent.

## Contents

1. The hypothesis and the mechanism
2. What is established vs what is speculative — disease by disease
3. The cross-domain transfer: what actually moves from bioacoustics to human voice, and what does not
4. The method — protocol (Phases 0–3)
5. Feature extraction — the acoustic phenotype, feature by feature
6. Model design — classifier vs longitudinal change detection
7. Data collection, consent, privacy, and governance
8. Validation design and confound controls
9. Falsification battery — what kills it, what narrows it
10. Evidence grade per claim — the graded claim table
11. What must be true for it to matter + limitations
12. Pre-registration template (filled skeleton)
13. Sequencing, resources, and what this document does not do
14. References

---

## 1. The hypothesis and the mechanism

### 1.1 The hypothesis (one paragraph)

**VAP-N hypothesis:** Vocal production is simultaneously a motor act (respiration, phonation, articulation, resonance) and a cognitive–linguistic act (lexical retrieval, syntactic planning, discourse organisation, prosodic planning). Neurodegeneration that degrades motor control (PD, ALS) and cognition/language (AD) should therefore leave measurable signatures in the acoustic signal of the voice — in phonation stability, articulatory precision, speech timing, and prosody — and the same feature-extraction and classifier pipeline used for animal voice decoding (spectrogram representations, learned audio embeddings, small classifiers trained on top, rigorous held-out validation) can be adapted to human voice features as a **longitudinal phenotyping readout**: a repeatable, low-burden measurement of how a person's voice changes over time against their own baseline, correlated with — never substituting for — clinical measures of motor and cognitive function. **[Grade C as a whole-method claim; its components are graded separately in §2 and §10.]**

### 1.2 Why voice is a plausible readout — the mechanism

Speech production decomposes, in the standard source–filter account, into a source (vocal-fold vibration, characterised by fundamental frequency F0 and its stability), a filter (the vocal tract, characterised by formant frequencies F1–F3 and vowel space), an energy supply (respiration, characterised by intensity, maximum phonation time, and breath-group structure), and a control system (motor planning and linguistic planning, characterised by timing, rate, pauses, and prosody). Each subsystem maps onto a different part of the neurodegenerative process, and each yields a different family of acoustic features (§5). That decomposition is the reason a single recording can, in principle, carry information about more than one disease process at once — and also the reason a single acoustic feature can never be disease-specific: the same feature (for example, increased jitter) can arise from laryngeal rigidity, from respiratory weakness, from ageing, from a cold, or from a poor microphone.

The mechanism, stated as a chain with a grade at each link:

1. **PD damages basal-ganglia motor control of the laryngeal, respiratory, and articulatory musculature.** Rigidity and reduced range of motion in those muscles produce hypokinetic dysarthria: reduced loudness, monopitch, monoloudness, imprecise articulation, harsh/breathy voice quality, inappropriate pauses, and variable speech rate. **[Grade A — see §2.1.]** The acoustic correlates are reduced F0 and intensity variability, shorter maximum phonation time, lower harmonics-to-noise ratio (HNR) and cepstral peak prominence (CPP), restricted vowel space area (VSA) and lower vowel articulation index (VAI), longer voice onset time (VOT), and increased jitter and shimmer (Cao et al. 2025, npj Parkinson's Disease, review; see §2.1).
2. **ALS damages upper and lower motor neurons controlling the cranial nerves of speech (IX–XII) and respiration.** The result is a mixed spastic–flaccid dysarthria affecting all speech subsystems — respiratory, resonatory/velopharyngeal, phonatory, and articulatory — with slowed speech, imprecise consonants, hypernasality, strain–strangled voice, reduced pitch and loudness range, short phrases, and inappropriate pauses. **[Grade A — see §2.2.]** Over 80% of people with ALS develop dysphonia and dysarthria over the course of the disease, and speech impairment may begin up to 3 years before diagnosis (Pedersen et al. (eds.), *Voice-related Biomarkers*, Springer, 2026, ch. 11 — see §2.2).
3. **AD damages hippocampal–entorhinal lexical access, anterior-temporal semantic networks, and left inferior frontal syntactic planning, with motor speech planning affected later.** The result is prolonged and more frequent silent pauses (impaired word retrieval), reduced speech rate and prosodic disturbance as pathology extends, reduced information-unit density (more words to convey less content), and reduced verbal fluency. **[Grade A for the speech/language description; Grade B for the claim that acoustic features track disease stage — see §2.3.]**
4. **Acoustic features are measurable repeatably, remotely, and at low burden from a microphone.** Sustained-vowel phonation, reading, and spontaneous speech can be recorded with a standard microphone, and features can be extracted with standardised toolkits (Praat/Parselmouth, openSMILE/eGeMAPS, librosa). **[Grade A for measurability; Grade C for the claim that repeatable measurement implies clinical utility.]**
5. **Learned audio embeddings trained on large bioacoustic corpora transfer to new acoustic tasks with few examples.** Perch 2.0 is explicitly an embedding + classifier model for transfer learning ("agile modeling"); NatureLM-audio generalises zero-shot to unseen species. **[Grade A for bioacoustics transfer; Grade C for transfer to human neurodegeneration — the transfer has not been tested and is the hypothesis.]**
6. **Therefore, a pipeline that (a) records standardised speech tasks longitudinally, (b) extracts a pre-registered feature set, (c) models change against each person's own baseline, and (d) validates against clinical anchors in held-out cohorts, can test whether vocal acoustic change tracks neurodegenerative progression.** **[Grade C — this is the method to be tested, stated in §4.]**

### 1.3 What VAP-N is and is not

| VAP-N is | VAP-N is not |
|---|---|
| A longitudinal phenotyping research method | A diagnostic, screening, or detection test |
| A way to measure vocal change over time, against a person's own baseline, in a research cohort | A way to label a person as having PD, ALS, or AD |
| A complement to clinical scales (MDS-UPDRS, ALSFRS-R, MMSE/MoCA, and equivalents), tested for correlation with them | A substitute for clinical examination, imaging, genetics, or fluid biomarkers |
| A cross-domain adaptation of a bioacoustics pipeline (embeddings + small classifiers + held-out validation) | A claim that animal-voice models understand human speech, or that human speech models understand animal calls |
| A protocol with pre-registered features, splits, and falsification criteria | An exploratory fishing expedition over thousands of features with post-hoc selection |

The distinction in the last row matters most. The PD voice literature's most-cited weakness is exactly that failure mode: small datasets, many features, recording-level splits that leak speaker identity across train and test, and accuracies that collapse when the split is done by subject. VAP-N is designed around that failure mode from the start (§6, §8).

### 1.4 The cross-domain idea, stated precisely

The WAVE bioacoustics programme and the neurodegeneration programmes share a pipeline shape and differ in a ground-truth shape:

- **Shared pipeline shape:** audio in → spectrogram / learned embedding → small classifier or change detector on top → held-out evaluation. BirdNET does this for species; Perch 2.0 does this as a general transfer-learning design; VAP-N proposes to do this for vocal phenotype.
- **Different ground truth:** In bioacoustics, the ground truth for classification is a human label ("this is a robin"), and the ground truth for meaning is the animal's own behaviour in a playback experiment (animal-voice review §3). In VAP-N, the ground truth for the longitudinal claim is a **clinical anchor** — a validated clinical scale or a clinically judged state (dysarthria present/absent, medication ON/OFF, ALSFRS-R speech subscore) measured in the same person at the same time as the recording. There is no receiver whose behaviour validates a vocal feature. The clinical anchor is the only ground truth available, and it is a human-assigned label with its own noise. That limits what VAP-N can ever claim: it can claim correlation with a clinical anchor under stated conditions, never access to a disease state itself.
- **The transferable insight:** the bioacoustics field learned, expensively, that (i) classification is not decoding, (ii) benchmarks measure agreement with a label, not understanding, (iii) cluster reification and label leakage are the characteristic failure modes, and (iv) a small, well-curated, paired dataset beats a large, confounded one. VAP-N imports those four lessons wholesale (§3). The transferable artefact is the **discipline**, not the model weights: a Perch embedding trained overwhelmingly on birds (with almost no marine hydrophone data, and no human clinical speech data) is not a human-voice model, and treating it as one would repeat the bird-classification error in a clinical setting.

### 1.5 The three disease signatures, in one table

| Disease | Primary systems damaged | Speech phenotype (established) | Acoustic families most implicated | Temporal character |
|---|---|---|---|---|
| **PD** | Basal ganglia; laryngeal, respiratory, articulatory musculature | Hypokinetic dysarthria: reduced loudness, monopitch, monoloudness, imprecise articulation, harsh/breathy voice, inappropriate pauses, variable rate | Phonation (jitter, shimmer, HNR, CPP), prosody (F0/intensity variability), articulation (VSA, VAI, VOT), timing (pauses, rate) | Fluctuates with medication state (ON/OFF); progresses slowly |
| **ALS** | Upper + lower motor neurons; cranial nerves IX–XII; respiratory muscles | Mixed spastic–flaccid dysarthria: slowed speech, imprecise consonants, hypernasality, strain–strangled voice, reduced pitch/loudness range, short phrases | Timing (vowel duration, speech rate, pauses), phonation (jitter, shimmer, HNR, CPP), articulation (VSA), resonance (nasality) | Progressive; bulbar onset early, spinal onset later; rapid in bulbar disease |
| **AD / MCI** | Hippocampal–entorhinal, anterior temporal semantic networks, left inferior frontal planning; motor speech later | Word-finding difficulty, reduced fluency, reduced information density, more/longer pauses, reduced speech rate and prosodic variation as disease advances | Timing (pause frequency/duration, speech rate), prosody (F0 variability), linguistic (lexical diversity, information units) — acoustic features alone are weaker than acoustic + linguistic | Progressive; linguistic changes earliest, motor-speech changes later |

This table is the method's working map. It predicts that PD and ALS will be most visible in phonation/articulation/timing features, and AD/MCI most visible in timing/linguistic features, with prosody and timing shared across all three. That prediction is testable and falsifiable (§9, F5).

---

## 2. What is established vs what is speculative — disease by disease

The line is drawn per claim, not per disease. A disease can have Grade A descriptive literature and a Grade C predictive claim at the same time. That is the normal state of this field, and VAP-N is built to respect it.

### 2.1 Parkinson's disease — voice and speech

**ESTABLISHED [Grade A]:**

- **Hypokinetic dysarthria affects the large majority of people with PD.** A 2025 Moroccan case–control study states the figure as approximately 90% of PD patients (Neurodegener Dis Manag 2025;15(6):313–322, PMID 40801237). A 2026 Bioengineering review states it as "the large majority of individuals with PD" (Bioengineering 2026;13:1037). The exact percentage varies by cohort, stage, and definition; the qualitative claim — that speech/voice impairment is common in PD, not rare — is established. Do not quote a single percentage as a universal prevalence without its cohort.
- **The perceptual phenotype is consistent across languages and cohorts:** reduced loudness (soft/asthenic voice), reduced variability in loudness and pitch (monopitch, monoloudness), harsh and/or breathy voice quality, imprecise articulation, decreased intelligibility, inappropriate pauses, and inconsistent speech rates including abrupt deceleration or acceleration (Cao et al., "Speech and language biomarkers for Parkinson's disease prediction, early diagnosis and progression", npj Parkinson's Disease 2025;11:57, doi:10.1038/s41531-025-00913-4 — narrative review synthesising the field).
- **The objective acoustic correlates are documented:** reduced range and variation in voice intensity and fundamental frequency (F0), shorter maximum phonation time, lower HNR and CPP, restricted vowel space area (VSA) and lower vowel articulation index (VAI), longer voice onset time (VOT), and increased jitter (cycle-to-cycle F0 variation) and shimmer (cycle-to-cycle amplitude variation) (Cao et al. 2025, §2.1 above). At the laryngeal level, incomplete vocal-fold closure, asymmetrical vibration, and reduced respiratory drive yield elevated jitter and shimmer, reduced CPP, and lower HNR (Brain Sci 2025;15(11):1162, PMC12650346 — PC-GITA study, 50 Colombian Spanish speakers with PD and 50 age- and sex-matched healthy controls).
- **Articulatory weakening is measurable below the phoneme level.** In the PC-GITA study above, PD participants showed significantly higher [continuant] phonological-feature posteriors, especially for dental stops, reflecting increased spirantisation and articulatory weakening; [sonorant] posteriors did not differ, indicating reduced oral constriction without a shift toward approximant-like articulations. Deep-learning-derived articulatory features captured early, subphonemic weakening in PD speech, particularly for coronal consonants.
- **Medication state changes the voice, inconsistently.** This is established as a *fact of variability*, not as a stable direction. Thies et al. (npj Parkinson's Disease 2025;11:105, doi:10.1038/s41531-025-00959-4) compared 78 participants (51 male, 27 female) in medication-OFF (≥12 h withdrawal) and medication-ON (after 200 mg soluble levodopa) conditions: acute levodopa improved phonatory–respiratory speech functions and speech planning, while the articulatory system remained unaffected, and a speech-based biomarker score differentiated OFF from ON (a post-hoc machine-learning model distinguished ON/OFF with AUC 0.81). The same paper's literature summary states that prior studies report inconsistent findings — some found increased intensity, better voice control, and faster articulation, others found no change in pitch, articulation/speech rate, and intensity. A separate 2025 Moroccan case–control study (30 PD patients, 30 controls, recordings before and after dopaminergic treatment, Praat analysis) found significant alterations in shimmer, jitter, HNR, and noise-to-harmonic ratio, a hoarse/breathy quality, and an increased number of long pauses (≥500 ms). The PC-GITA study above found HNR did **not** distinguish PD from controls, "likely reflecting ON-medication recordings" — a direct demonstration that medication state can erase a group difference. **[Grade A that medication state is a confound; Grade B/C for any specific directional claim about levodopa and a given feature.]**
- **Speech changes can precede or co-occur with the earliest overt motor signs.** The Bioengineering 2026 review states vocal changes "can emerge early in the disease course, at times preceding or co-occurring with the earliest overt motor signs by as much as a decade" (citing prior literature). **Attribution note (peer-review fix R9, verified 8 Nov 2026):** the "as much as a decade" phrasing is present verbatim in Bioengineering 2026;13:1037, where it cites ref [8] — Cao et al. 2025, *npj Parkinson's Dis* 11:57 — as its source; the near-identical phrasing is also in Cao itself. The attribution to Bioengineering stands, with Cao named here as the underlying source. This is a literature-reported claim, not a VAP-N finding; the "as much as a decade" figure is an upper bound from cited sources, not a typical lead time. **[Grade B — reported in review literature, not established by a single prospective cohort in this pass.]**

**SPECULATIVE / UNTESTED [Grade C, unless noted]:**

- **That any acoustic feature or model *predicts* PD status or progression in a new cohort.** Cross-sectional classification accuracies in the literature are high in-sample and fragile out-of-sample. A 2026 Research Square preprint (multi-cohort pipeline, 996 recordings from 332 independent subjects across three public datasets, leave-one-subject-out validation, soft-voting ensemble of logistic regression, SVM, and random forest) reported subject-level AUC 0.8836, sensitivity 88.60%, specificity 70.19%, with MFCCs and HNR as dominant predictors — and explicitly framed its contribution as fixing subject-level data leakage, "a structural flaw endemic to the PD voice literature". That framing is the point: much of the earlier literature's accuracy is inflated by recording-level splits. A 2025 PMC study using spectrogram features reported 97% accuracy and AUC 0.95 with a BiLSTM on a dataset of 81 samples, and summarised prior work at 89.75% (Karaman et al., mPower, DenseNet161) and 96% accuracy / AUC 0.99 (Bukhari et al., UCI PD dataset, AdaBoost) — figures that must be read against their sample sizes (see §2.4). **[Grade C for generalisation; the preprint and the small-sample studies are cited as evidence of the *problem*, not as proof of a working detector.]**
- **That voice features track PD progression longitudinally in individuals.** Cross-sectional group differences do not imply longitudinal tracking. **Literature anchor for the expected annual change (peer review B2-G3, verified 8 Nov 2026):** Skodda et al. 2013 (*Parkinson's Disease*, PMC3872441) retested 80 PD patients and 60 controls after a mean interval of 32.5 months: shimmer rose 6.548 → 11.490 (p < 0.0001, Cohen's d 0.87) and noise-to-harmonics ratio 0.051 → 0.103 (p < 0.0001, d 0.61), while jitter did not change significantly — and deterioration did not correlate with the time interval. That is the only prior estimate of within-person vocal change over time found in this pass: a large shimmer change over ~2.7 years, with no per-year rate established. **Implication:** the 12-month window in §4 has no established basis — the pilot must show detectable change at 12 months above test–retest noise, or the window extends. **[UNVERIFIED as a 12-month longitudinal claim; Grade C as a hypothesis; the Skodda anchor is Grade B for change over ~2.7 years.]**
- **That a cross-species bioacoustics embedding (Perch, BirdNET, NatureLM-audio) improves PD voice modelling over a human-speech feature set (eGeMAPS/Praat).** No study in this pass tests this. **[Grade C.]**

### 2.2 Amyotrophic lateral sclerosis — voice and speech

**ESTABLISHED [Grade A]:**

- **Bulbar involvement affects speech in most people with ALS over the disease course.** Over 80% of individuals with ALS develop dysphonia and dysarthria, primarily a mixed spastic–flaccid subtype resulting from deterioration of both upper and lower motor neurons involved in speech production; 48% have dysphonia at onset (mainly bulbar phenotype); speech impairment may begin up to 3 years before diagnosis (Pedersen et al. (eds.), *Voice-related Biomarkers*, Springer, 2026, ch. 11, "Neurodegenerative Diseases: Aspects of Voice-Related Biomarkers"). The "up to 3 years before diagnosis" figure was not confirmed from the chapter text in this pass — verify against the chapter before external use (peer review §5B, B2-6). The mixed dysarthria affects all speech subsystems (respiratory, resonatory/velopharyngeal, phonatory, articulatory).
- **The perceptual phenotype is documented:** effortful, slow productions with short phrases, inappropriate pauses, imprecise consonants, hypernasality, strain–strangled voice, and decreased pitch and loudness range; perceptual features include harshness, strain–strangled voice, breathiness, tremor, and pitch abnormalities (Laryngeal dysfunction in ALS: review, BMC Ear Nose Throat Disord 2001;1:1, PMC60006). Upper motor neuron dysfunction produces spastic dysphonia; lower motor neuron dysfunction produces flaccid dysphonia — "extremely different phonatory disorders" from the same disease, which complicates any single acoustic summary (Pedersen et al. 2026, ch. 11).
- **The standard acoustic measures are jitter, shimmer, and HNR**, plus CPP (reduced CPP reflecting breathiness and strain), reduced vowel space area and vowel centralisation, slower articulation rates with more frequent pauses, and (in a 2026 Korean study, J Speech Sci 2026;18(3)) vowel duration as a marker: in a single standardised reading passage from 53 speakers (17 controls, 36 patients), vowel duration was the only measure significant in both contrasts (controls vs patients, and patients with vs without clinically judged dysarthria) and surviving correction for multiple comparisons — patients with dysarthria produced vowels approximately 20% longer than controls and 23% longer than patients without dysarthria, while patients without dysarthria did not differ from controls. HNR, F0 range, and pause duration distinguished patients from controls but did **not** differentiate patients by dysarthria status. That dissociation — a feature that separates patients from controls but not dysarthric from non-dysarthric patients — is exactly the kind of result VAP-N's design must be able to produce and report, rather than averaging away. **[Grade A for the descriptive findings in the cited studies; Grade B for generalisation beyond their cohorts.]**
- **Standard assessment batteries combine three task types:** sustained vowel phonation, diadochokinetic (DDK) syllable repetition, and passage reading (2026 Korean study, § above). VAP-N adopts the same three-task battery (§4.3) for comparability.
- **The ALS clinical context matters for what voice can add:** there is no treatment that stops or reverses ALS; three drugs are FDA-approved in the US with modest effects (riluzole 1995, edaravone 2017, tofersen 2023, SOD1-ALS only); Relyvrio was approved in 2022 and withdrawn in 2024 after a larger trial failed (ALS lit review, § status box; NINDS). The most important new screening result in the window is Bye et al. (Nat Neurosci 2026;29:40–52) — a 100-donor sporadic-ALS iPSC motor-neuron library, of which the drug screen itself was run on motor neurons from **7–16 SALS donors** (the paper's methods range; combination validation on **15 SALS donors** — red-team verification, Loop 2, Worker B3, 8 Nov 2026, donor-n precision corrected per peer review R2; state the screen range of 7–16 alongside the library n of 100, never imply all 100 were screen- or combination-tested); 107 trial drugs re-screened, fewer than 5% rescuing motor-neuron survival, and a three-drug combination (riluzole + memantine + baricitinib) showing **combination benefit** — the paper demonstrates the combination outperforming the single drugs, with no Bliss or other formal synergy analysis in the full text (zero occurrences of "Bliss"), so it is cited here as combination benefit only, never as formal synergy. ALS TDI's digital-biomarker research includes voice and movement data (ALS lit review §2.1). Voice phenotyping in ALS therefore sits alongside, not instead of, cellular and clinical programmes — and its value, if any, is as a low-burden longitudinal measure in trials and cohorts, not as a diagnostic shortcut.

**SPECULATIVE / UNTESTED [Grade C]:**

- **That acoustic features predict bulbar onset before clinical dysarthria is judged present.** The 2026 vowel-duration study shows a feature tracking *judged* dysarthria status; it does not show prediction before judgement. **[Grade C.]**
- **That a single acoustic summary can capture both spastic and flaccid dysarthria.** The two subtypes produce opposite phonatory disorders; a model trained on a mixed cohort may learn the cohort mix, not the disease. VAP-N therefore stratifies by UMN/LMN predominance where the clinical record permits (§8). **[Grade C as a modelling claim; Grade A that the subtypes differ.]**
- **That vocal change tracks ALSFRS-R decline longitudinally.** No longitudinal result is established in this pass. **[UNVERIFIED as a longitudinal claim.]**

### 2.3 Alzheimer's disease and mild cognitive impairment — speech and language

**ESTABLISHED [Grade A for description; Grade B for acoustic-only classification]:**

- **Language deficits are present from the early — even prodromal — stages, and are a key window for early detection.** Memory deficit is the earliest main symptom, accompanied by aphasia, apraxia, agnosia, and executive dysfunction; language impairment in AD occurs mainly through decline in semantic and pragmatic processing; early signs are word-finding difficulty (especially naming familiar people/objects), words replaced by wrong/meaningless words, and increased pauses; early-stage impairment involves lexical retrieval, loss of verbal fluency, and breakdown in higher-order written/spoken language comprehension (Front Psychol 2021 systematic review, "Ten Years of Research on Automatic Voice and Speech Analysis of People With Alzheimer's Disease and Mild Cognitive Impairment", Front Psychol 2021; and Encyclopedia MDPI, "Speech- and Language-Based Classification of Alzheimer's Disease").
- **The acoustic/temporal signature is consistent:** prolonged and more frequent silent pauses indicating slowing of word retrieval from impaired temporal–hippocampal memory networks; reductions in speech rate and perturbations in prosodic rhythm as pathology extends into motor speech planning networks, in a temporospatial gradient mirroring Braak staging; reduced information-unit density (more words to convey less content) reflecting progressive disorganisation of semantic knowledge networks in the anterior temporal lobe; filled-pause frequency reflecting impaired lexical retrieval; reduced function-word use and altered content density correlating with structural brain changes on MRI in MCI due to AD (Front Aging Neurosci 2026;27 Oct 2026, review, "Speech and sMRI as multimodal biomarkers for early detection of Alzheimer's disease").
- **Prosody is among the most-studied parameters:** speech rhythm (pauses, accents, speech rate), voice intensity and its variation over time, emission time, and F0 variation; reported F0 changes include decreased F0 variation, a decrease in F0 in female voices and an increase in male voices in the cited review, higher jitter and shimmer, reduced resonance, and more speech pauses (Front Psychol 2021 review, § above). The F0 sex-specific figures in that review are reported as review-level summaries, not as VAP-N thresholds — do not use them as cut-offs.
- **The community benchmarks are the DementiaBank Pitt Corpus (Cookie Theft picture-description task, Boston Diagnostic Aphasia Examination), the ADReSS Challenge dataset (Luz et al. 2020), and the Framingham Heart Study speech corpus** (Front Aging Neurosci 2026 review). The ADReSS dataset is a subset of the Pitt Corpus, balanced for age and gender: 156 participants (78 AD, 78 non-AD), 1,955 speech segments from non-AD subjects and 2,122 from AD subjects; ADReSSo contains 237 participants (Luz et al., "Alzheimer's Dementia Recognition through Spontaneous Speech: The ADReSS Challenge", arXiv:2004.06833, INTERSPEECH 2020). Luz et al.'s own baselines: acoustic features alone, up to **62.5% accuracy** on the AD classification task; linguistic features from manually produced transcripts, **76.85%**; MMSE regression baseline RMSE 6.14 (acoustic) and 5.21 (linguistic). The paper notes that higher accuracies reported elsewhere (up to 81.92%) used manual transcripts and unbalanced datasets, and that accuracy for the best-performing such model drops to 58.5% when feature selection is not performed on its original 370 features. **That 62.5% acoustic-only baseline — not the 80–90% figures in secondary reporting — is the number VAP-N must beat, under the same balanced conditions, to claim anything.** The Front Psychol 2021 systematic review (35 papers) reports most diagnostic studies at over 88% accuracy for AD and 80% for MCI — figures that must be read against the ADReSS baseline's warning about unbalanced data and transcript leakage. **[Grade A for the ADReSS baseline figures; Grade B for the 88%/80% summary, which aggregates heterogeneous studies.]**
- **Naturalistic speech carries signal beyond the lab.** An Interspeech 2026 study (175 participants, patient–nurse check-in phone calls) reported structured clinical data alone at AUC 0.74, adding phone calls improving performance, with the best attention-based fusion configuration at AUC 0.92 and F1 83.08 for cognitive-impairment detection — a conference paper, not a clinical validation, cited here as evidence that ecologically valid speech carries signal, not as a performance claim for VAP-N.

**SPECULATIVE / UNTESTED [Grade C]:**

- **That acoustic features alone (without transcripts/linguistic features) track AD progression longitudinally.** The ADReSS baseline shows acoustic-only classification is modest (62.5%) even cross-sectionally; longitudinal tracking is a harder claim. **[Grade C.]**
- **That a single vocal phenotype separates AD from PD or ALS.** Timing and prosody features are shared across diseases (§1.5); separation, if it exists, will come from the *pattern* across feature families (linguistic-heavy in AD, phonation/articulation-heavy in PD/ALS), not from any single feature. **[Grade C.]**
- **That speech features predict conversion from MCI to AD.** No prospective conversion result is established in this pass. **[UNVERIFIED.]**

### 2.4 The datasets the field actually has — and why they constrain everything

| Dataset / corpus | Size (verified) | What it is | Limitation VAP-N must respect |
|---|---|---|---|
| **UCI Parkinson's Disease Detection (Little et al.)** | 195 voice recordings from 31 people (23 PD, 8 healthy controls); ~6 recordings per person | Biomedical voice measurements (sustained vowel phonation); Little et al., IEEE Trans Biomed Eng 2009 (Little, McSharry, Hunter & Ramig) | 31 subjects. Any recording-level split leaks speaker identity. High accuracies on this dataset (96–97% in some papers) are not generalisation evidence. |
| **UCI Parkinson's Telemonitoring** | 5,875 voice recordings from 42 people with early-stage PD, 6-month trial | Voice measurements aimed at predicting motor/UPDRS scores | Single-cohort, early-stage only; no healthy longitudinal controls in the same protocol. |
| **PC-GITA** | 100 Colombian Spanish speakers: 50 PD, 50 age- and gender-matched healthy controls; 960 recordings; 44.1 kHz, 16-bit WAV; soundproof booth, Shure SM63L microphone | Sustained vowels (/a/, /e/, /i/, /o/, /u/), DDK, word/sentence reading, spontaneous monologue; UPDRS and Hoehn & Yahr; PD recorded ON-medication | Single language, single site, ON-medication only — HNR did not distinguish groups in one PC-GITA analysis, attributed to medication state. |
| **mPower (Sage Bionetworks)** | 8,320 participants (Bot et al. 2016, *Sci Data* 3:160011 — participants completing at least one survey or task in the first six months of data release; 9,520 consented overall); voice + mobility via smartphone, ResearchKit (Bot et al. 2016, Sci Data 3:160011) | Large, remote, real-world; sustained vowel /a/ and other tasks | Remote, uncontrolled recording conditions; device and environment variability is the confound, not a footnote. |
| **ADReSS (INTERSPEECH 2020)** | 156 participants, balanced age/gender (78 AD, 78 non-AD) | Cookie Theft picture description, Pitt Corpus subset; acoustic + linguistic baselines | Acoustic-only baseline 62.5%; linguistic 76.85%. Small; single task; English only. |
| **ADReSSo (INTERSPEECH 2021)** | 237 participants, balanced | As ADReSS, spontaneous speech | As ADReSS, larger but still small for deep models. |
| **DementiaBank Pitt Corpus** | Longitudinal spontaneous speech (larger, unbalanced) | Cookie Theft + other tasks; the source corpus for ADReSS | Unbalanced (age, gender, class); longitudinal observations — models trained on it without subject-level splits leak. |

The pattern across the table is the method's central constraint: **the field's datasets are small (tens to low hundreds of subjects), single-language or single-site, and often recorded under one medication state or one device.** Any VAP-N claim that does not name its dataset, its split, and its medication/device conditions is not a claim. Phase 0 (§4) exists to make that discipline mechanical.

### 2.5 What the bioacoustics side contributes — and its limits

**ESTABLISHED [Grade A, from the animal-voice review and GitHub survey]:**

- Machine-learning models can identify which species made a sound, at large scale: BirdNET v2.4 (June 2023) covers 6,522 classes (incl. 10 non-event classes) — not "6,522 bird species" (peer-review fix R3, verified against the BirdNET-Analyzer README, 8 Nov 2026: "V2.4, June 2023 — global selection of species (birds and non-birds) with 6,522 classes (incl. 10 non-event classes)"); Perch 2.0 (August 2025, arXiv:2508.04665) covers 14,597 species; NatureLM-audio (Nov 2024) generalises zero-shot to unseen species.
- The training data is overwhelmingly birds: Xeno-canto ~1,040,000 recordings (settled figure retained — see the 8 Nov 2026 re-check note: the founder's page now states about 1,100,000 recordings; adoption of the higher figure awaits Mike's decision); Macaulay Library 3.2M+ audio recordings (Wikipedia, accessed Nov 2026 — note: Cornell's own March 2025 piece said "more than 2.7 million", so the figure is growing and must be re-checked with a dated source before external use). Marine data is thin (Watkins Marine Mammal Sound Database ~2,000 unique recordings / >15,000 annotated clips).
- The pipeline components are open and reusable: BirdNET-Analyzer (MIT code; models CC BY-NC-SA 4.0), Perch (Apache 2.0; use `perch-hoplite` for inference), NatureLM-audio (MIT repo), OpenSoundscape (MIT; preprocessing, CNN training, detection; integrates BirdNET, Perch 2, HawkEars via the Bioacoustics Model Zoo), librosa (ISC; spectrograms, MFCCs), scikit-maad (BSD 3-Clause; acoustic indices), BEANS/BirdSet benchmarks (classification/detection only). **Model-weights licensing (peer review B2-G8, checked 8 Nov 2026):** Perch code is Apache 2.0 and the Perch v1 weights on Kaggle carry the Apache 2.0 licence (Kaggle model page, google/bird-vocalization-classifier). The Perch **v2** weights licence is to be confirmed against the Kaggle v2 model page before any governed dataset release in Phase 3 — the v1 licence does not automatically cover v2 — and the general speech-encoder licence remains "to be checked per use" (GAP-VAP-9).
- **Classification is not decoding.** No published study has assigned verified meanings to a wild animal's signal repertoire via machine learning; no programme (CETI, Earth Species Project, DolphinGemma) claims to have done so. The playback experiment, not the benchmark leaderboard, is the instrument that separates classification from meaning (animal-voice review §3). Sperm whale codas show combinatorial structure (156 distinct codas, Sharma et al. 2024, Nat Commun 15:3617) with zero verified meanings attached, by the researchers' own account.

**SPECULATIVE [Grade C] — the transfer:**

- That Perch embeddings, trained on 1,542,778 recordings that are overwhelmingly birdsong and general sound events, carry useful structure for human dysarthric speech. The embedding was not trained for this; any benefit is a transfer hypothesis to be tested against a human-speech baseline (eGeMAPS/Praat), not assumed.
- That NatureLM-audio's zero-shot generalisation to unseen *species* implies generalisation to unseen *clinical* tasks. It does not; zero-shot species classification and longitudinal clinical phenotyping are different tasks with different ground truths.
- That the WAVE engine contributes anything to VAP-N today. It does not: the public engine repo (`WAVETranslator/Wild-Animal-Voice-Engine`) is a 3-file stub with no code; the live predictor on bioacoustics.cloud is BirdNET, a species classifier. VAP-N uses the *upstream open tools* (Perch, openSMILE, Praat, librosa), not the WAVE stub.

---

## 3. The cross-domain transfer: what actually moves from bioacoustics to human voice, and what does not

This section is the cross-domain core of the document. A transfer claim that does not name what moves, what does not move, and how the difference will be tested is two summaries stapled together. VAP-N names all three.

### 3.1 What moves (transferable, with the test for each)

| Bioacoustics practice | Human-voice adaptation in VAP-N | Test that it moved |
|---|---|---|
| **Spectrogram + learned embedding as the representation** (Perch 2.0: audio in, embeddings out; BirdNET: spectrogram CNN) | Log-Mel spectrogram + Perch embedding as one representation arm, alongside handcrafted acoustic features (eGeMAPS/Praat). The two arms are compared head-to-head on the same splits, never blended before the comparison. | Phase 1 ablation: embedding-only vs handcrafted-only vs fused, on identical subject-level splits. If the embedding arm does not beat handcrafted features out-of-cohort, it is dropped. |
| **Agile modeling: small classifiers on frozen embeddings, few examples** (Perch 2.0 design; `perch-hoplite`) | Linear/logistic or small gradient-boosted classifiers on frozen embeddings, trained per cohort with few subjects. This matches the data reality (§2.4: tens to low hundreds of subjects) — a large fine-tuned model would overfit. | Phase 1: learning curves (accuracy vs training-subject count). If performance is still rising steeply at the maximum available N, the result is data-limited, not model-limited, and is reported as such. |
| **Standardised feature sets as a lingua franca** (eGeMAPS in affective computing; BEANS/BirdSet as shared benchmarks) | eGeMAPSv02 (88 features) as the primary handcrafted set, with Praat voice-quality measures as the reference implementation. Every feature is named, versioned, and extracted by a pinned toolkit version. | Cross-toolkit check (§8): the same recordings processed in openSMILE and Praat; features with poor cross-toolkit agreement are flagged and excluded from the primary analysis. |
| **Held-out evaluation by individual and by population** (BirdSet: held-out soundscapes; BEANS: held-out datasets) | Leave-one-subject-out (LOSO) as the minimum; leave-one-cohort-out (LOCO) as the pre-registered primary for any generalisation claim; leave-one-site/device-out where the data permit. | §8. A result reported only under random recording-level k-fold is not a result. |
| **Context-only baselines** (animal-voice review §6: a model must beat a context-only baseline to claim meaning-relevant structure) | Age + sex + device + medication-state + recording-condition baseline model. The acoustic model must beat this baseline, on held-out subjects, to claim anything beyond demographics and recording conditions. | §8, F2. If the acoustic model matches but does not beat the context baseline, the acoustic claim fails. |
| **Negative controls: scrambled/reversed stimuli should be unpredictable** (animal-voice review §6.5) | Time-reversed and phase-scrambled speech controls: a model that "predicts" clinical state from scrambled audio is leaking metadata or label information, not reading the voice. | §9, F6. Scrambled-audio accuracy must be at chance. |
| **Paired data beats bigger classifiers** (animal-voice review §7: the near-term product is a paired call-and-response dataset) | VAP-N's near-term product is a paired voice-and-clinical-anchor dataset: the same person, the same day, a recording and a clinical scale. No new classifier is proposed before that dataset exists. | Phase 0 deliverable is the dataset design and the retrospective re-analysis, not a model. |

### 3.2 What does not move (non-transferable, stated explicitly)

1. **Species identity as a label does not map to disease identity as a label.** A bird species is a stable, discrete category with a large, cleanly labelled training set. A neurodegenerative disease is a progressive, heterogeneous syndrome with overlapping phenotypes, uncertain onset, and clinical labels that are themselves probabilistic (especially early PD and MCI). A classifier that is 90% accurate at species ID has no implication for disease classification. **[Grade A that the label structures differ; Grade C for any claim that species-classification accuracy predicts clinical accuracy.]**
2. **Playback ground truth does not exist for human voice.** In animal work, the receiver's behaviour in a playback experiment is the ground truth for meaning. In VAP-N, there is no receiver; the clinical anchor is a human-assigned score. VAP-N therefore cannot claim to have measured a disease state, only to have measured correlation with a clinical anchor under stated conditions. Any language implying otherwise is excluded from reporting (§13).
3. **Zero-shot species generalisation does not imply cross-disease generalisation.** NatureLM-audio's zero-shot result (34.3% accuracy on unseen species against a 0.5% random baseline, as reported in secondary synthesis — cited as secondary reporting in the animal-voice review, not verified from the paper text in this pass) is a species-classification result. It says nothing about whether a model trained on PD voice generalises to ALS voice, or vice versa. Cross-disease transfer is a separate test (§4, Phase 2), with its own falsification criterion.
4. **Birdsong data volume does not imply human clinical data volume.** Xeno-canto ~1,040,000 (settled figure retained; founder's page re-check 8 Nov 2026 shows about 1,100,000 — adoption pending Mike's decision, see §2.5) and Macaulay 3.2M+ recordings are bird-dominated archives. The human clinical voice datasets in §2.4 are three orders of magnitude smaller in subjects. VAP-N must not borrow the bioacoustics field's scale rhetoric; its power calculations (§4.5) use human-subject numbers, not recording numbers.
5. **The WAVE engine, the WAVE agents, and any "talk to animals" framing do not transfer.** The WAVE repo is a stub; the agents are listed in Virtuals ACP and offline; no decoding result exists. VAP-N makes no decoding claim in either direction and must not be presented alongside one.

### 3.3 The transfer hypothesis, restated as a testable comparison

The cross-domain hypothesis is not "bioacoustics models work on human voice". It is the sharper, falsifiable comparison:

> **On identical subject-level and cohort-level splits, with identical clinical anchors, a pipeline using (a) a frozen bioacoustics embedding (Perch 2.0) plus a small classifier will perform no worse than, and will be tested for superiority over, (b) a pipeline using only standardised human-speech features (eGeMAPS + Praat), for the task of (i) cross-sectional group separation and (ii) longitudinal within-person change detection — and the *pattern* of which feature families drive performance will differ by disease in the direction predicted in §1.5 (phonation/articulation-heavy in PD/ALS, timing/linguistic-heavy in AD).**

If (a) does not beat (b), the bioacoustics transfer fails as a modelling claim (the discipline transfer in §3.1 still stands). If the feature-family pattern does not differ by disease as predicted, the disease-signature map in §1.5 fails. Both are falsifiable (§9).

### 3.4 Why this transfer is worth attempting despite the differences

Three reasons, each graded:

- **The data problem is the same shape.** Both fields have small, confounded, single-site datasets and a literature inflated by leaky splits. The bioacoustics field's response — shared benchmarks, held-out soundscapes, agile modeling on frozen embeddings — is a tested response to that exact problem. **[Grade B.]**
- **The measurement problem is the same shape.** Both fields measure a time-varying acoustic signal whose ground truth is external to the audio (a species label, a clinical anchor). Both need representations that are stable across devices and environments. **[Grade B.]**
- **The cost structure is the same shape.** Both fields benefit from a low-burden, repeatable, remote measurement (a field recorder; a phone microphone). If vocal phenotyping works, it is cheap to repeat — which is precisely what a longitudinal readout needs to be. **[Grade B for the cost claim; Grade C for the "if it works" conditional.]**

None of these reasons implies the transfer will work. They imply it is worth a pre-registered test with a handcrafted baseline that can win.

---

## 4. The method — protocol (Phases 0–3)

### 4.0 Overview

| Phase | What | Data | Duration (indicative) | Gate to next phase |
|---|---|---|---|---|
| **0 — Retrospective re-analysis** | Re-analyse published/public voice datasets with subject-level splits, context baselines, and negative controls. No new recordings. | UCI PD (195 recordings, 31 subjects), PC-GITA (100 subjects), mPower (subset, access permitting), ADReSS/ADReSSo (156/237 participants) | Months 1–4 | Phase 0 pre-registration filed and Phase 0 report published (including nulls), with data-access outcomes documented |
| **1 — Prospective single-cohort phenotyping** | One disease, one site, standardised protocol (§4.3), longitudinal recordings + clinical anchors | New cohort, partner institution, ethics approval required | Months 5–18 | Pre-specified longitudinal correlation achieved or failed; report published |
| **2 — Cross-cohort and cross-disease validation** | Same protocol in a second cohort (different site/device/language) and a second disease | New cohorts, partner institutions | Months 12–30 (overlaps Phase 1) | LOCO result reported; transfer claim tested |
| **3 — Reporting and dataset release** | Full reporting, dataset + code release under governance, no clinical claims | All phases | Months 18–36 | Dataset released (governed access) or reason for non-release documented |

No phase starts before its predecessor's pre-registration is filed and its gate is documented. Phase 1 does not start until the Phase 0 pre-registration is filed **and** the Phase 0 report is published (including nulls), with data-access outcomes documented — the same sequencing discipline as the animal-voice Playback-Prediction Test (animal-voice review §6.7). (Gate wording standardised per peer-review polish note: one gate, stated identically in §4.0 and §4.1.)

### 4.1 Phase 0 — Retrospective re-analysis (months 1–4, no new recordings, no ethics approval for new human data — dataset licences and data-use agreements still apply)

**Aim:** Establish, on data that already exists, (a) what cross-sectional separation is achievable under subject-level splits, (b) whether acoustic models beat context-only baselines, and (c) whether the bioacoustics-embedding arm beats the handcrafted arm — before any new person is recorded.

**Steps:**

1. **Assemble the datasets.** UCI Parkinson's Detection (195 recordings, 31 subjects); PC-GITA (100 subjects, access on request for academic use); mPower voice subset (access via Sage Bionetworks, governed); ADReSS (156 participants) and ADReSSo (237 participants) via DementiaBank (restricted, data-use agreement). Record, per dataset: source, licence/access route, N subjects, N recordings, language, device, medication state (where recorded), clinical anchor available, and every exclusion. **Gate:** verify each dataset's Data Availability / access terms first. If a dataset is not accessible, it enters Phase 0 only at the granularity its authors published, and the limitation is stated. Do not reconstruct unpublished labels. **Minimum Phase 0 dataset (peer review B2-G11):** UCI (31 subjects) + ADReSS (156 participants) is the floor. F1 can be run on UCI alone only as a single-dataset, single-language result with that limitation stated. If PC-GITA, mPower, and ADReSS/ADReSSo access all fail, Phase 0 reports on UCI + ADReSS only and the cross-sectional claim is correspondingly narrowed — the fallback is stated before access requests go out, not after they fail.
2. **Freeze the feature sets.** eGeMAPSv02 (88 features, openSMILE, pinned version) as the primary handcrafted set; Praat/Parselmouth voice-quality measures (jitter variants, shimmer variants, HNR, CPP, F0 statistics, formants F1–F3) as the reference implementation; log-Mel spectrogram + Perch 2.0 frozen embedding as the transfer arm; MFCCs as a secondary arm (MFCCs were the dominant predictors alongside HNR in the 2026 multi-cohort preprint). No feature is added after the pre-registration is filed.
3. **Freeze the splits.** For every dataset: leave-one-subject-out (LOSO) as the minimum; leave-one-cohort-out (LOCO) where more than one cohort is pooled; random recording-level k-fold is computed only as a *demonstration of leakage* (to show how much it inflates accuracy), never as a result. Splits are by subject, never by recording. Where a dataset contains longitudinal observations from the same subject (Pitt Corpus), all observations from a subject go in one fold.
4. **Freeze the baselines.** (a) Chance/majority-class; (b) context-only (age + sex + device + medication state + recording condition, where available); (c) handcrafted-only; (d) embedding-only. The acoustic claim is the *increment* over (b), not the raw accuracy.
5. **Freeze the metrics.** Primary: balanced accuracy and AUC (with 95% confidence intervals, bootstrap over subjects, not recordings) for cross-sectional separation; for the ADReSS MMSE regression task, RMSE and correlation, against the published baselines (acoustic RMSE 6.14, linguistic 5.21). Secondary: per-class F1, calibration, and feature-importance stability across folds. Success threshold (pre-registered): the acoustic model beats the context-only baseline by ≥10 percentage points in balanced accuracy (or ≥0.10 AUC) with a 95% CI excluding zero — the same threshold shape as the animal-voice Playback-Prediction Test. Report the threshold and the result; do not move the threshold after seeing the result.
6. **Negative controls.** (a) Label permutation: shuffled labels must collapse AUC to ~0.50 (the 2026 preprint's permutation test collapsed AUC to 0.556 — that is the expected shape of a clean result). (b) Scrambled/reversed audio: features extracted from time-reversed audio must not predict clinical state above chance. (c) Device-only model: a model given only device/recording metadata must not match the acoustic model.
7. **Deliverable:** Phase 0 report (all results including nulls, all splits, all baselines, full feature list, toolkit versions, analysis code archived openly under governance). A null result is a successful outcome of this design.

**Phase 0 falsification (see §9, F1–F3):** if no acoustic model beats the context-only baseline on held-out subjects in any dataset, Phase 1 does not proceed on the cross-sectional claim; the programme narrows to the longitudinal claim only if Phase 0 gives a positive reason to do so, or stops.

### 4.2 Phase 1 — Prospective single-cohort phenotyping (months 5–18, partner institution, ethics approval required)

**Aim:** Test, in a new cohort recorded under the standardised protocol, whether (a) cross-sectional separation replicates, and (b) within-person vocal change over time correlates with change in a clinical anchor.

**Disease choice:** PD first. Rationale: the PD voice literature is the largest, the clinical anchor (MDS-UPDRS, including the speech item, plus medication ON/OFF as a within-person manipulation) is the cleanest, and the medication confound — which is a threat in a cross-sectional design — becomes a *feature* in a longitudinal design (ON/OFF is a known, timed perturbation of the vocal system). ALS second (bulbar progression is faster, giving a longitudinal signal in a shorter window, but the UMN/LMN mix complicates the phenotype). AD/MCI third (the acoustic-only signal is weakest; the linguistic arm must be built first — see §5.4).

**Cohort (target, to be confirmed with the partner):** 60 PD participants + 60 age- and sex-matched healthy controls, recorded at baseline, 3, 6, 9, and 12 months (5 sessions). This N is a *target for the protocol*, not a power claim: no power calculation is presented here, because the effect size for longitudinal vocal change is unknown — that is what Phase 0 and the Phase 1 pilot (first 20+20 participants, first two sessions) are for. The pilot's observed within-person variability sets the sample size for the confirmatory cohort, and the recalculation is documented before the confirmatory cohort is locked. Do not quote a sample size as powered until that recalculation exists.

**Clinical anchors (collected at every session, same day as the recording):** MDS-UPDRS (total and Part III, including the speech item), Hoehn & Yahr stage, medication state (ON/OFF, time since last levodopa dose, levodopa-equivalent daily dose), MoCA (cognitive screen), and a clinician-judged dysarthria rating (present/absent, severity). For ALS (Phase 1b): ALSFRS-R (including the speech subscore), site of onset, UMN vs LMN predominance as judged clinically, and forced vital capacity (respiratory confound). For AD/MCI (Phase 1c): MMSE/MoCA, Clinical Dementia Rating, and a standardised language assessment. Anchors are collected by the partner's clinical team, not by the voice team, and the voice team is blind to the anchor values until the analysis is locked.

### 4.3 Data collection — the standardised recording protocol

**Tasks (all participants, every session, in fixed order):**

| # | Task | Duration | What it measures | Why this task |
|---|---|---|---|---|
| T1 | Sustained vowel /a/ (×3 repetitions, single breath each) | ~10 s each | Phonation: jitter, shimmer, HNR, CPP, F0 stability, maximum phonation time | The most standardised task in the field; isolates the laryngeal source; comparable to UCI (sustained vowel) and PC-GITA (sustained vowels /a/, /e/, /i/, /o/, /u/) |
| T2 | Sustained vowels /i/ and /u/ (×1 each) | ~10 s each | Phonation across vowel space; formants F1/F2 | Vowel-space measures need more than one vowel; /i/ and /u/ anchor the corners of the space |
| T3 | Diadochokinetic (DDK) syllable repetition: /pa-ta-ka/ as fast and as clearly as possible (×3) | ~10 s each | Articulation rate, regularity, and precision; motor planning | Standard in ALS batteries; sensitive to articulatory slowing and irregularity; isolates articulation from language |
| T4 | Standardised reading passage (language-specific, fixed text, e.g. the "Rainbow Passage" in English or the PC-GITA reading texts in Spanish) | ~60–90 s | Connected-speech timing (speech rate, pause frequency/duration, articulation rate), prosody (F0/intensity variability), vowel duration, intelligibility | The task in which the 2026 ALS vowel-duration finding was made (single standardised reading passage); the only task that yields timing + prosody + articulation together |
| T5 | Spontaneous speech: Cookie Theft picture description (AD/MCI) or a standardised monologue prompt (PD/ALS, e.g. "describe your morning routine") | ~60–120 s | Lexical retrieval (pauses, filled pauses, word-finding), information-unit density, discourse organisation, prosody in natural speech | The ADReSS task (Cookie Theft) for AD/MCI; a matched spontaneous task for PD/ALS so the timing/linguistic arm is comparable across diseases |
| T6 | (Optional, PD only) Modulated vowel: /a/ gliding from low to high pitch and back | ~10 s | Pitch range and control; prosodic range | PC-GITA includes modulated vowels; analysed separately as an *optional* task, so it cannot inflate the primary result. (An earlier draft quoted an 82–90% discrimination figure for this task; the figure was uncited and no source was found in this pass, so it is removed per peer-review fix R11 rather than carried without a citation.) |

**Recording conditions (fixed, logged at every session):**

- **Device:** a single specified recording device per cohort (e.g. a named headset microphone + audio interface), fixed across sessions for a given participant. Device model, serial/ID, and firmware are logged. If a participant's device changes, the session is flagged and the change is a covariate, not silently absorbed.
- **Environment:** quiet room, same room where possible; ambient noise level measured (dB SPL, phone sound-meter app or dedicated meter) and logged at the start of each session. Sessions with ambient noise above a pre-registered threshold are flagged, not deleted silently — the flag is a variable in the analysis.
- **Microphone distance:** fixed (e.g. 8 cm from the mouth, as in the UCI dataset's sound-treated-booth protocol, or a headset microphone at a fixed position). Distance is logged.
- **Sampling:** 44.1 kHz, 16-bit WAV (as PC-GITA), uncompressed. No lossy compression, no automatic gain control, no noise suppression, no enhancement. The raw WAV is the archival record; every derived feature is traceable to it.
- **Medication state (PD):** time since last levodopa dose, ON/OFF as judged clinically, and LEDD, logged at every session. Where feasible, one session per participant is recorded in a defined OFF state (≥12 h withdrawal, as in Thies et al. 2025) and one in a defined ON state — with the participant's clinician's approval and the participant's consent, and only if clinically safe. **OFF-session eligibility and rescue (peer review B2-G5):** the participant's clinician decides eligibility; exclusion from OFF sessions if there is a history of severe OFF freezing or falls, inability to tolerate ≥12 h withdrawal, or no escort/transport for the return journey. If withdrawal becomes intolerable mid-session, the session stops, levodopa is given immediately, and the session is recorded ON and flagged — an abandoned OFF session is never counted as a failed OFF session. OFF-state recording is never required; if it is not safe or not consented, the session is recorded ON and flagged.
- **Health state at the session:** cold/upper-respiratory infection, fatigue, time of day, and (ALS) respiratory status — logged as covariates. A cold changes jitter and shimmer; a model that does not know about colds will learn colds.

**Quality control (applied identically to every recording, before any analysis):**

- Signal-to-noise ratio computed and logged; recordings below a pre-registered SNR threshold are flagged.
- Clipping detection (samples at full scale); clipped recordings flagged.
- Voice-activity detection: proportion of the recording that is speech vs silence, logged.
- A random 10% of recordings are manually checked by a second annotator for task compliance (correct vowel, correct passage, no overlapping speech). Disagreements are logged.
- All QC flags are variables in the dataset, not deletion criteria applied silently. The primary analysis includes flagged recordings with the flag as a covariate; a sensitivity analysis excludes them. Both are reported.

### 4.4 Feature extraction — summary (full table in §5)

Three arms, frozen before analysis:

- **Arm H (handcrafted, primary):** eGeMAPSv02 (88 features, openSMILE, pinned version) + Praat/Parselmouth voice-quality measures (jitter local/RAP/PPQ5, shimmer local/dB/APQ3/APQ5/APQ11, HNR, CPP, F0 mean/SD/range, intensity mean/SD, formants F1–F3, maximum phonation time, vowel duration, speech rate, articulation rate, pause count/duration, phonation-time ratio).
- **Arm E (embedding, transfer):** log-Mel spectrogram + frozen Perch 2.0 embedding (via `perch-hoplite` / Kaggle model weights), plus a frozen general speech embedding as a control (e.g. a wav2vec 2.0 / TRILLsson-type encoder, if licensed for research use — licence to be checked per use, as with all model weights). The Perch arm is the transfer test; the speech-embedding arm is the control that separates "any learned embedding helps" from "a bioacoustics embedding specifically helps".
- **Arm L (linguistic, AD/MCI primary, PD/ALS secondary):** from an automatic transcript (ASR system named and versioned in the pre-registration; transcript quality measured by word-error rate on a manually transcribed subset): lexical diversity (type–token ratio), information-unit density, filled-pause rate, word-finding markers (repetitions, revisions, abandoned utterances), syntactic complexity (mean length of utterance), and content-word ratio. Arm L is *not* part of the primary PD/ALS analysis; it is the primary AD/MCI arm, because the ADReSS baseline shows linguistic features (76.85%) outperform acoustic-only features (62.5%).

All three arms are extracted from the same recordings, by pinned toolkit versions, with a versioned extraction script archived with the pre-registration. No feature is computed by hand, and no feature is added after the analysis is locked.

### 4.5 Power, sample size, and the pilot

No confirmatory sample size is stated in this document, because the longitudinal effect size is unknown. The sequence is:

1. Phase 0 gives the cross-sectional effect size under subject-level splits (balanced accuracy, AUC, and their CIs).
2. The Phase 1 pilot (first 20 PD + 20 controls, two sessions) gives the within-person variability (test–retest reliability, intraclass correlation) of each feature family and the within-person change over 3 months.
3. A power calculation is performed on the pilot's observed variability, for the pre-registered primary longitudinal endpoint (§6.3), and the confirmatory N is set from it and documented before the confirmatory cohort is locked.
4. If the pilot shows within-person variability swamping any plausible disease signal, Phase 1 stops and the result is reported — that is a finding, not a failure to find one.

Any document that quotes a powered N for VAP-N before steps 1–3 exist is inventing a number. This document does not.

### 4.6 What Phase 1 does not do

- It does not diagnose anyone. Participants are not told a vocal "result" about their disease state; they are told the study measures how voice changes over time for research.
- It does not return individual vocal scores to participants or clinicians as clinical information. Aggregate, cohort-level results are shared after publication.
- It does not use the voice data for any purpose beyond the pre-registered analysis without a new consent and a new ethics approval.
- It does not record anyone who has not consented, and it does not record in a participant's home or by phone unless that mode is itself the pre-registered protocol (remote recording is a *separate* protocol with its own device/environment controls — see §7.4 — not a convenience fallback).

---

## 5. Feature extraction — the acoustic phenotype, feature by feature

Every feature below is pre-registered with its task, its toolkit, its hypothesised direction, and its disease prediction. A feature whose direction is stated after the data are seen is not a finding. Directions are predictions from the literature in §2, not thresholds: no cut-off value is stated for any feature, because no validated cut-off exists.

### 5.1 Phonation (laryngeal source) — Tasks T1, T2, T4

| Feature | Definition | Toolkit | Predicted direction (disease vs matched control) | Disease prediction |
|---|---|---|---|---|
| Jitter (local, RAP, PPQ5) | Cycle-to-cycle variation in F0 | Praat/Parselmouth; eGeMAPS jitter local | Increased | PD, ALS |
| Shimmer (local, local dB, APQ3/5/11) | Cycle-to-cycle variation in amplitude | Praat/Parselmouth; eGeMAPS shimmer local dB | Increased | PD, ALS |
| HNR | Harmonics-to-noise ratio; turbulent noise in the voice signal | Praat; eGeMAPS log-HNR | Decreased | PD, ALS |
| CPP (cepstral peak prominence) | Prominence of the cepstral peak; breathiness/roughness index | Praat (via cepstral analysis) | Decreased | PD, ALS |
| F0 mean, SD, range | Fundamental frequency and its variability | Praat; eGeMAPS F0 semitone | SD/range decreased (monopitch) in PD; range decreased in ALS | PD (primary), ALS |
| Maximum phonation time (MPT) | Longest sustained /a/ on one breath | Stopwatch from T1 recording | Decreased | PD, ALS |
| Intensity mean, SD | Loudness and its variability | Praat; eGeMAPS loudness | Mean decreased, SD decreased (monoloudness) in PD | PD |
| Voice breaks, fraction unvoiced | Proportion of phonation with breaks / unvoiced frames | Praat | Increased | PD, ALS |

**Why these features, mechanistically:** jitter/shimmer/HNR/CPP all index the stability and completeness of vocal-fold vibration and glottal closure. Incomplete closure (PD rigidity, ALS weakness) creates turbulence (low HNR, low CPP) and aperiodic vibration (high jitter/shimmer). F0/intensity variability indexes prosodic and respiratory control, not just the larynx: monopitch/monoloudness is a control-system failure, not a vocal-fold failure, which is why F0 SD and intensity SD are analysed separately from jitter/shimmer and are predicted to behave differently under levodopa (Thies et al. 2025: phonatory–respiratory features improved on levodopa; articulation did not).

### 5.2 Articulation (vocal-tract filter) — Tasks T3, T4

| Feature | Definition | Toolkit | Predicted direction | Disease prediction |
|---|---|---|---|---|
| Vowel space area (VSA) | Area of the F1–F2 triangle/ quadrilateral from /a/, /i/, /u/ | Praat formants F1/F2 | Decreased (vowel centralisation) | PD, ALS |
| Vowel articulation index (VAI) | Formant-based index of vowel distinctness | Praat formants | Decreased | PD |
| Formant SD (F1, F2) during sustained vowels | Within-vowel variability of formant frequencies | Praat | Increased SD (instability) in PD (PC-GITA analyses) | PD |
| VOT (voice onset time) | Delay between stop release and voicing onset | Manual/forced-alignment measurement on T4 | Increased | PD |
| DDK rate and regularity | Syllables per second and coefficient of variation of inter-syllable intervals in /pa-ta-ka/ | Praat / forced alignment | Rate decreased, irregularity increased | PD, ALS |
| Spirantisation / [continuant] posteriors | Deep-learning phonological-feature posteriors (Phonet-type) for stop weakening | Phonet-type DNN (named and versioned in pre-registration; secondary arm only) | Increased [continuant] for dental stops | PD (PC-GITA finding) |
| Vowel duration (reading passage) | Mean vowel duration in T4 | Forced alignment + Praat | Increased (~20% in dysarthric ALS vs controls, 2026 Korean study) | ALS (primary) |

**Why these features:** articulation indexes the precision and speed of tongue, lip, and jaw movement. Reduced VSA/VAI is vowel centralisation — the articulators not reaching their targets. Increased vowel duration is slowing, not imprecision, and the 2026 ALS study's dissociation (vowel duration tracked dysarthria status; HNR/F0 range/pause duration separated patients from controls but did not track dysarthria status) is the reason VAP-N keeps articulation and phonation as separate families with separate predictions, rather than collapsing them into one "voice score".

### 5.3 Timing and prosody (control system) — Tasks T4, T5

| Feature | Definition | Toolkit | Predicted direction | Disease prediction |
|---|---|---|---|---|
| Speech rate (words/syllables per minute, including pauses) | Overall rate in connected speech | Transcript + audio timing | Decreased | PD, ALS, AD |
| Articulation rate (syllables per minute, excluding pauses) | Rate during speech segments only | Transcript + audio timing | Decreased | PD, ALS |
| Pause frequency and mean/median pause duration | Silent pauses ≥200 ms (and ≥500 ms long-pause count, as in the Moroccan PD study) | Voice-activity detection | Frequency and duration increased | PD, ALS, AD (primary in AD) |
| Phonation-time ratio | Speech time / total time | Voice-activity detection | Decreased | PD, ALS, AD |
| Filled-pause rate (um/uh per minute) | Filled pauses in spontaneous speech | Transcript (Arm L) | Increased | AD (primary — lexical retrieval) |
| F0 variability in connected speech (SD, range) | Prosodic variation across an utterance | Praat/eGeMAPS | Decreased (monopitch in connected speech) | PD, AD |
| Intensity variability in connected speech | Loudness variation across an utterance | Praat/eGeMAPS | Decreased | PD |

**Why these features:** timing separates *slowing* (articulation rate) from *stopping* (pauses). In AD the pauses are retrieval pauses (lexical access failure); in PD/ALS they are motor-planning and respiratory pauses (short phrases, breath groups). The same measured quantity (pause duration) has a different mechanism in each disease — which is why pause features are always reported alongside the task (reading vs spontaneous) and the disease, never as a disease-free "pause biomarker".

### 5.4 Linguistic features (Arm L) — Task T5 only, AD/MCI primary

| Feature | Definition | Source | Predicted direction in AD/MCI |
|---|---|---|---|
| Information-unit density | Information units (correct picture elements named, Cookie Theft) per word | Manual/automated scoring against the Cookie Theft information-unit list | Decreased |
| Lexical diversity (type–token ratio, moving-average TTR) | Distinct word types / total tokens | ASR transcript | Decreased |
| Content-word ratio / function-word use | Content words vs function words | ASR transcript + part-of-speech tagging | Content density altered; function-word use reduced (Front Aging Neurosci 2026 review) |
| Word-finding markers | Repetitions, revisions, abandoned utterances, circumlocutions per minute | Transcript annotation | Increased |
| Mean length of utterance / syntactic complexity | Words per utterance; clause density | Transcript | Decreased |

Arm L requires a transcript. The ASR system, its version, and its word-error rate on a manually transcribed subset (minimum 10% of recordings, double-transcribed) are reported with the results. A linguistic result from a transcript with an unmeasured error rate is not a result. **WER acceptability bar (peer review B2-G4):** an ASR system is admissible for Arm L only if its WER on the manually transcribed dysarthric subset is ≤25% (interim bar, confirmed or replaced from the pilot's measured WER distribution before the confirmatory cohort is locked). If no ASR system clears the bar, Arm L is dropped and the AD arm becomes acoustic-only, with that limitation stated — the AD claim is then graded down accordingly, not carried on an unmeasured transcript. Arm L is not used for PD/ALS primary analysis, and acoustic features are not used as a substitute for linguistic features in AD — the ADReSS baseline (acoustic 62.5% vs linguistic 76.85%) is the reason.

### 5.5 Embedding arm (Arm E) — all tasks

- **Log-Mel spectrogram** (librosa, pinned version; 128 Mel bins, 25 ms window, 10 ms hop — parameters frozen in the pre-registration) as the input representation for the embedding models.
- **Perch 2.0 frozen embedding** (via `perch-hoplite` / Kaggle model weights; Apache 2.0 code) — the transfer arm. **Input conditioning (peer review B2-G7):** Perch's frontend takes 5 s of audio at 32 kHz (160,000 samples; hop 10 ms, window 20 ms — arXiv:2508.04665). VAP-N recordings are 44.1 kHz, so the embedding arm resamples to 32 kHz and segments into 5-s windows before the embedding; the resampling applies to the embedding arm only. Praat jitter/shimmer and the other handcrafted features are computed on the original 44.1 kHz recordings, so resampling cannot distort them. The resampling step is validated in the pilot by confirming that embedding outputs are stable across the resampling (same recording, native 32 kHz vs downsampled 44.1→32 kHz, compared where a 32 kHz original exists) and the validation is reported.
- **General speech embedding control** (a frozen self-supervised speech encoder, e.g. wav2vec 2.0 / TRILLsson-type, named and versioned in the pre-registration, licence checked per use) — the control that separates "any learned embedding helps" from "a bioacoustics embedding specifically helps".
- **MFCCs** (13–20 coefficients + deltas, librosa) as a classical spectral arm — MFCCs were, alongside HNR, the dominant predictors in the 2026 multi-cohort PD preprint, so they are a named comparator, not an afterthought.

No embedding is fine-tuned in Phase 0 or Phase 1. Fine-tuning on tens of subjects would overfit and would destroy the transfer test's interpretability. If a fine-tuned model is ever proposed, it is a separate protocol with its own pre-registration.

### 5.6 Features explicitly excluded

- **Speaker-identity features** (speaker embeddings, voiceprints): excluded from the phenotype. They identify the person, which is both a privacy risk (§7) and a leakage risk (§8). A model that can identify the speaker can memorise the speaker's label.
- **Emotion/affect inference:** excluded. VAP-N measures acoustic properties of speech production; it does not infer mood, emotion, or inner state from voice.
- **Raw audio as a model input for the primary analysis:** the primary analysis uses the named feature sets above, not end-to-end audio, so that every result is traceable to a named, interpretable feature. End-to-end spectrogram models are a secondary, exploratory arm, reported separately and never as the primary result.

---

## 6. Model design — classifier vs longitudinal change detection

This is the design decision the whole method turns on. VAP-N's answer is: **both, in sequence, with different success criteria — and the longitudinal design is the primary one, because a cross-sectional classifier is the weaker claim and the easier one to inflate.**

### 6.1 The cross-sectional classifier (secondary)

- **Task:** separate a disease group from matched controls, at one time point, from one recording session.
- **Models:** logistic regression, support-vector machine, random forest, and gradient-boosted trees — the same small-model family as the 2026 multi-cohort preprint's soft-voting ensemble (logistic regression + SVM + random forest). No deep classifier is the primary model in Phase 0/1.
- **Inputs:** Arm H (primary), Arm E (transfer test), Arm H+E (fusion, tested only after the separate arms are reported). Arm L is added only for the AD/MCI analysis.
- **Success criterion (pre-registered, Phase 0):** balanced accuracy beating the context-only baseline by ≥10 percentage points, 95% CI (bootstrap over subjects) excluding zero, on LOSO and (where pooled cohorts permit) LOCO splits. A result that meets the criterion on random k-fold but not on LOSO is a leakage demonstration, not a success.
- **What it can and cannot show:** it can show that vocal features carry group-level information under stated conditions. It cannot show that vocal features track an individual, predict progression, or diagnose anyone. A cross-sectional classifier that works is a reason to run the longitudinal study; it is not a clinical tool.

### 6.2 The longitudinal change detector (primary)

- **Task:** detect change in a person's vocal phenotype over time, against that person's own baseline, and test whether that change correlates with change in a clinical anchor.
- **Why own-baseline:** between-person vocal variation (sex, age, anatomy, accent, habitual loudness, microphone) is large relative to any disease signal. A model that compares a person to a population norm will learn the norm's demographics. A model that compares a person to their own earlier recordings removes the largest variance component by design — the same logic as the ALS programme's longitudinal BH3-profiling design (cross-disease Pattern 5: priming measured as a trajectory, not a single value) and the same logic as a within-person medication manipulation.
- **Design:**
  1. **Baseline establishment:** the first two sessions (baseline + 3 months, both in the same medication state for PD) define the person's baseline distribution per feature family: mean and within-person standard deviation (test–retest reliability, intraclass correlation coefficient). Features with poor test–retest reliability (ICC < 0.5 in the pilot) are excluded from the primary longitudinal analysis — a noisy feature cannot track change.
  2. **Change score:** for each subsequent session, each feature family is expressed as a standardised change from the person's baseline (z-score using the person's own baseline mean and SD, and separately as a raw change with the baseline as a covariate). Both are reported; the pre-registered primary is the standardised change, because it is comparable across features with different units.
  3. **Change detection:** a pre-registered rule flags a session as "changed" when the standardised change in the primary feature family exceeds a pre-registered threshold (e.g. |z| ≥ 2, set from the pilot's within-person variability, not from the confirmatory data). The threshold is set before the confirmatory cohort is analysed. A cumulative-sum (CUSUM) detector over sessions is a secondary analysis, not the primary rule — CUSUM parameters tuned after seeing the data are not a test.
  4. **Clinical correlation (the primary longitudinal endpoint):** the correlation, across participants, between vocal change (standardised change in the primary feature family, 12 months minus baseline) and clinical change (MDS-UPDRS Part III change for PD; ALSFRS-R speech-subscore change for ALS; MMSE/MoCA change for AD/MCI), computed as a Pearson/Spearman correlation with a 95% CI, and as a linear mixed-effects model with participant as a random intercept, time as a fixed effect, and the clinical anchor as a time-varying covariate. The mixed model is the primary analysis because it uses all sessions and handles missing sessions; the simple 12-month correlation is a sensitivity check.
  5. **Medication-state manipulation (PD, the strongest within-person test):** in participants with a clinically safe, consented OFF session and a matched ON session, the ON–OFF difference in the phonation family is the pre-registered manipulation check. If the method cannot detect a known, timed perturbation (levodopa ON vs OFF, Thies et al. 2025: AUC 0.81 for ON/OFF discrimination from speech), it cannot be trusted to detect slow progression. This is the direct analogue of the red-team's strengthened falsification for the BCL-2 programme — a within-person pharmacological manipulation that bypasses between-person stratification noise entirely. If the ON/OFF manipulation fails, the longitudinal claim fails with it (§9, F4).
- **Success criterion (pre-registered, Phase 1):** the primary longitudinal endpoint — correlation between vocal change and clinical change — with a 95% CI excluding zero, **and** the ON/OFF manipulation check passed, **and** the result replicated in the sense of §8.4 (same direction in the second cohort). All three must hold. A correlation that holds in one cohort and reverses in the second is not a success.

### 6.3 Primary endpoints, named

| Phase | Primary endpoint | Success bar (pre-registered) |
|---|---|---|
| Phase 0 | Cross-sectional balanced accuracy, acoustic model vs context-only baseline, LOSO, pooled public datasets | Beat baseline by ≥10 pp, 95% CI excluding zero |
| Phase 1 (PD) | Longitudinal: correlation between 12-month vocal change (primary feature family, standardised vs own baseline) and MDS-UPDRS Part III change | 95% CI excluding zero, **plus** ON/OFF manipulation passed, **plus** same direction in second cohort (Phase 2) |
| Phase 1b (ALS) | Longitudinal: correlation between vocal change and ALSFRS-R speech-subscore change | As above, with the ALS anchor |
| Phase 1c (AD/MCI) | Longitudinal: correlation between vocal change (timing + linguistic families) and MMSE/MoCA change | As above, with the AD anchor; acoustic-only and linguistic arms reported separately |

### 6.4 What the model must never output

- No individual disease label, probability of disease, or risk score for any participant. The model outputs a feature vector, a change score, and a cohort-level correlation. That is the entire output surface.
- No "normal/abnormal" vocal judgement for an individual. Population norms for vocal features do not exist at the precision a per-person judgement would need, and a per-person judgement from a research phenotype would be a clinical act without a clinical basis.
- No output is returned to a participant or a clinician as clinical information (§4.6).

### 6.5 Interpretability requirement

Every reported model must be interpretable at the feature-family level: which families (phonation, articulation, timing/prosody, linguistic) drive performance, and in which direction. Feature-importance stability across folds is reported (as in the 2026 preprint, where MFCCs and HNR dominated). A black-box model with high accuracy and no stable feature attribution is not reported as a success — it is reported as an uninterpretable result, because an uninterpretable vocal model cannot be checked against the mechanism in §1.2 and cannot be debugged when it fails in a new cohort.

---

## 7. Data collection, consent, privacy, and governance

Voice is not like a blood-test value. A voice recording is identifiable, it carries health information, and it cannot be stripped of identity without destroying the signal. This section is part of the method, not a compliance afterthought: a VAP-N study that cannot meet this section cannot run.

### 7.1 Voice as identifiable biometric data

- A recording of a person's voice can identify them — by human listening, by speaker-recognition systems, and by cross-reference with publicly available recordings (social media, podcasts, phone conversations). Anonymised voice data can often be re-identified when cross-referenced with public recordings (Navigating the tradeoff between personal privacy and data utility in speech anonymization for clinical research, PMC12534620, 2025). The paper's summary of the trade-off is direct: data can be either useful or perfectly anonymous, but never both — and techniques that modify non-linguistic aspects of speech to reduce identifiability are not viable in clinical settings where analysis relies on acoustic signals to detect subtle abnormalities.
- Individuals with speech disorders face a higher risk of identification than those with typical speech (same source) — which is precisely the VAP-N population. The identifiability risk is therefore higher for the people the method studies, not lower.
- Under GDPR, biometric voice processing needs a stronger lawful basis, a data-protection impact assessment (DPIA), and written vendor agreements; explicit consent is required where voice is processed for identification/verification purposes, and voiceprints are sensitive personal information under CCPA/CPRA, with Illinois' BIPA requiring explicit opt-in consent before collecting audio features used to identify or verify people by voice (summarised in ASR Privacy for Custom Speech Systems, 2026; and in UK GDPR voice-cloning analysis, 2026). **This document is not legal advice.** The legal basis, DPIA, and consent form for any VAP-N study are the partner institution's counsel's work, not this document's. VAP-N's requirement is that they exist, are documented, and are approved before recording starts.
- **Consequence for the method:** VAP-N treats voice recordings as **pseudonymised, never anonymised**. A recording labelled `Speaker_014` with a re-link key held separately is pseudonymised data, still personal data, still governed. No VAP-N document, dataset release, or publication claims a voice dataset is "anonymised" or "de-identified" in the sense of being outside data-protection law. The description is: pseudonymised, access-controlled, with a documented re-identification risk assessment.

### 7.2 Consent (minimum content)

Consent must be specific, informed, and revocable, and must cover, in plain language:

1. That voice recordings are being collected for research into how voice changes over time in neurodegeneration, and that the recordings can identify the speaker.
2. That the recordings will be stored pseudonymised, who will have access, for how long, and for what analyses (the pre-registered analysis only).
3. That no individual disease label, risk score, or clinical result will be returned from the voice analysis.
4. That participation is voluntary, that withdrawal is possible at any time, and what happens to recordings already collected on withdrawal (deletion, or retention in aggregated form — stated explicitly, not left ambiguous).
5. That recordings will not be used for any other purpose (including model training for other projects, commercial use, or voice cloning/synthesis) without a new consent and a new ethics approval.
6. That data may be shared with named research partners under a data-use agreement, and will not be made publicly downloadable as raw audio.

Consent is obtained by the partner institution's research team, in the participant's language, with capacity assessed for participants with cognitive impairment (AD/MCI) and a legally authorised representative involved where capacity is lacking, per the partner's ethics approval. VAP-N does not design the consent form; it requires that the form contain the six points above.

### 7.3 Storage, access, and minimisation

- **Raw audio** is stored encrypted, access-controlled, on the partner institution's governed storage — never on a personal laptop, never in a public repository, never in a shared drive without access control.
- **Derived features** (the eGeMAPS/Praat/embedding vectors) are stored separately from the re-link key. Feature tables shared for analysis contain a participant code, session, task, and feature values — no name, no audio, no transcript content that could identify the person (transcripts are checked for names, addresses, and other identifiers before sharing, and identifiers are redacted with the redaction logged).
- **Retention:** a retention period is stated in the ethics approval and the consent form. **Default retention (peer review B2-G13, a default for the ethics approval, not a decided fact): 10 years from the last publication using the data.** At the end of retention, raw audio is deleted and the deletion is logged. Backups are covered by the same retention rule — a backup that retains audio past the retention period is a retention failure, not a technicality. **Deletion on withdrawal:** when a participant withdraws, their raw audio and derived features are deleted within 30 days of the withdrawal, the deletion is logged, and the withdrawal itself is recorded (counted, not named) in the study log; aggregate results already computed from their data are retained, as the consent form states. The named person responsible for deletion on withdrawal (§7.5) carries this out.
- **Data minimisation:** only the tasks in §4.3 are recorded. No ambient recording, no recording outside the session, no recording of conversations with family members or clinicians. The microphone is on for the tasks and off otherwise, and the participant can ask for the recording to stop at any time.
- **No voice cloning, synthesis, or speaker-identification research** is performed on VAP-N recordings. Speaker embeddings are excluded from the phenotype (§5.6) for the same reason: the method does not need to know who is speaking, only how that person's voice changes.

### 7.4 Remote / phone recording — a separate protocol, not a fallback

Remote recording (phone, home microphone) is attractive because it is low-burden and repeatable — the mPower model — and it is also the mode in which device, environment, and medication-state variability are largest and least controlled. VAP-N therefore treats remote recording as a **separate protocol** (Phase 2b), not as a convenience fallback for in-person sessions:

- The remote protocol specifies the device (participant's own phone, model logged; or a supplied recorder), the app, the environment instruction (quiet room, same room each time), the microphone distance instruction, and a calibration task (a standardised vowel + a standardised sentence, recorded at the start of every remote session, used to estimate session-level device/environment effects).
- In-person and remote recordings from the same person are never pooled without a mode covariate, and the primary longitudinal analysis is in-person only until the remote protocol has its own validation (same person, in-person and remote sessions within days, agreement measured by ICC per feature family).
- If remote recording cannot meet the QC thresholds in §4.3, it is not used. A larger, noisier dataset is not better than a smaller, controlled one for a change-detection method whose signal is small.

### 7.5 Ethics and governance prerequisites (all required before Phase 1)

- Ethics approval from the partner institution's review board, covering the protocol, consent, data handling, and retention.
- Data-use / data-sharing agreements with every party that receives audio or features.
- A DPIA (or the local equivalent) for biometric voice processing, where required.
- A named data controller and a named person responsible for deletion on withdrawal.
- No recording starts until all four exist and are documented. The absence of any one is a stop condition, not a risk to be managed while recording proceeds.

---

## 8. Validation design and confound controls

### 8.1 Split discipline (the non-negotiable rule)

| Split | What it tests | When it is required |
|---|---|---|
| Leave-one-subject-out (LOSO) | Generalisation to a new person | Every cross-sectional result |
| Leave-one-cohort-out (LOCO) | Generalisation to a new cohort (site, device, language) | Every generalisation claim |
| Leave-one-site / leave-one-device-out | Generalisation across recording conditions | Where the data permit |
| Random recording-level k-fold | Nothing — computed only to demonstrate leakage inflation | Never reported as a result |
| Leave-one-donor-group-out (ALS, by progression rate) | Generalisation across patient heterogeneity | ALS analyses, following the Bye panel's donor grouping |

**The leakage rule, stated once:** recordings from the same subject never appear on both sides of a split. A paper that splits by recording on a dataset with ~6 recordings per subject (UCI: 195 recordings, 31 subjects) has, in effect, trained on the test subjects. VAP-N's Phase 0 re-analysis exists in part to quantify how large that inflation is on the public datasets, so that the field's published accuracies can be read with the inflation attached.

### 8.2 Confound controls — the pre-registered covariate set

Every analysis includes, as covariates or as stratification variables, the following — measured at every session, never imputed from a baseline value:

| Confound | Why it matters | How VAP-N controls it |
|---|---|---|
| **Age** | F0, jitter, shimmer, speech rate, and pause structure all change with age; PD/ALS/AD cohorts are older than convenience controls | Age-matched controls; age as a covariate in every model; age-stratified sensitivity analysis |
| **Sex** | F0, formants, and intensity differ by sex; F0 changes in AD are reported as sex-specific in the literature | Sex-matched controls; sex as a covariate; sex-stratified sensitivity analysis (never pooled without the covariate) |
| **Recording device** | Microphone frequency response, compression, and noise floor change jitter/shimmer/HNR directly | Fixed device per cohort (§4.3); device as a covariate; leave-one-device-out where devices vary. **Harmonisation (peer review B2-G1):** where devices differ, ComBat-style batch harmonisation (neuroComBat-type, feature-level, with disease group protected as a biological covariate) is applied and its effect reported; the remote protocol's calibration task (a reference signal recorded at the start of each session) has the acceptance rule that a session whose reference-signal drift exceeds the pre-registered limit is flagged and excluded from the primary analysis. If the fixed device is discontinued mid-study, the replacement device is introduced with cross-device calibration recordings from the same participants, and the harmonisation is re-validated before the new device's data enter the primary analysis — device variability is controlled by harmonisation + calibration, not only logged and covaried. |
| **Recording environment / ambient noise** | Noise raises measured shimmer, lowers HNR, and masks pauses | Ambient-noise measurement logged per session; SNR as a covariate; flagged sessions analysed as a sensitivity check |
| **Medication state (PD)** | Levodopa changes phonation and speech planning inconsistently across studies; HNR group differences disappear ON-medication in one PC-GITA analysis | Medication state + time since last dose logged per session; ON/OFF as a covariate in cross-sectional models; ON/OFF manipulation as a within-person test (§6.2); primary longitudinal analysis uses same-state sessions |
| **Disease stage / severity** | A feature that separates advanced disease from controls may not separate early disease | Stage (Hoehn & Yahr, ALSFRS-R, CDR) as a covariate; stage-stratified analysis; early-stage-only sensitivity analysis |
| **Language** | Vowel inventories, speech rate norms, and pause norms differ by language; PC-GITA is Colombian Spanish, UCI is English | Language is a cohort variable, never pooled silently; cross-language transfer is a Phase 2 test, not an assumption |
| **Respiratory status (ALS)** | Forced vital capacity and respiratory weakness change intensity, MPT, and breath-group structure independently of bulbar function | FVC logged per session (ALS); respiratory status as a covariate |
| **Cold / upper-respiratory infection, fatigue, time of day** | All change phonation measures acutely | Logged per session as covariates; sessions with acute infection flagged |
| **Smoking status** | Smoking changes jitter, shimmer, and HNR independently of disease | Covariate, logged per session (current / former / never + pack-years at baseline) |
| **Depression** | Depression changes speech rate, pauses, and prosody | Covariate (PHQ-9 or equivalent, per session where the protocol permits) |
| **Respiratory disease (non-ALS)** | COPD/asthma change intensity, MPT, and breath-group structure | Covariate; diagnosed respiratory disease recorded at baseline and per session |
| **Hearing loss** | Hearing loss changes self-monitoring of voice and reading-task performance | Severe hearing loss is an exclusion for the reading task (T4); otherwise a covariate |
| **Reflux / laryngeal irritation** | Reflux changes hoarseness, jitter, and shimmer | Covariate (reflux symptoms logged per session) |
| **UMN vs LMN predominance (ALS)** | Spastic vs flaccid dysarthria are opposite phonatory disorders | Clinical predominance recorded; stratified analysis where the record permits |

A model that does not include the context-only baseline (§3.1, §4.1 step 4) has not been tested. The context-only model is not a straw man: age + sex + device + medication state may already separate groups well in a confounded dataset, and if the acoustic model cannot beat it, the acoustic claim fails (§9, F2).

### 8.3 Cross-toolkit and cross-feature checks

- The same recordings are processed in openSMILE (eGeMAPS) and Praat/Parselmouth for the overlapping features (F0, jitter, shimmer, HNR). Features with poor cross-toolkit agreement are flagged and excluded from the primary analysis; the agreement statistics are reported. (A 2025 comparative evaluation of openSMILE, Praat, and librosa on clinical speech found high cross-toolkit correlation for some measures (r = 0.962–0.999) and poor, even near-zero, agreement for others — e.g. F0 SD and formant values often had poor agreement, and jitter measurement differed between toolkits. That is why the check is mandatory, not optional.)
- Feature-importance stability is reported across folds. A feature that is "most important" in one fold and irrelevant in the next is not a biomarker; it is noise.
- Test–retest reliability (ICC) is reported per feature family from the pilot's repeated sessions. Features with ICC < 0.5 are excluded from the primary longitudinal analysis.

### 8.4 Replication standard

A VAP-N result is reported as **replicated** only when:

1. The same direction of effect is observed in a second, independent cohort (different site, and where possible different device/language), analysed with the *frozen* pipeline (same features, same model, same thresholds — no refitting of the feature set on the second cohort), and
2. The 95% CI in the second cohort excludes zero (for the longitudinal correlation) or the pre-registered success bar is met (for the cross-sectional accuracy), and
3. The result survives the sensitivity analyses (excluding flagged sessions, excluding the ON/OFF-mixed sessions, age/sex-stratified).

A result that holds in one cohort only is reported as **single-cohort, unreplicated**. A result that holds in the pooled data but reverses in one cohort is reported as **heterogeneous, not replicated**. No language upgrades a single-cohort result.

### 8.5 Reporting standard

All results — including nulls — are reported with: dataset, N subjects (not just N recordings), split, baselines, metrics with 95% CIs (bootstrap over subjects), toolkit versions, medication/device conditions, and the pre-registration identifier. A result reported without its N subjects is not a result. A result reported without its split is not a result.

---

## 9. Falsification battery — what kills it, what narrows it

**How to read this section (red-team discipline, Loop 2, Worker B3):** the strongest falsification test is one that can kill the method outright. Each test below is labelled **KILL** (the method as stated stops — no further phase on that claim) or **NARROW** (the scope is reduced, the method continues in a smaller form), with the distinction made explicitly. Tests that can only narrow are labelled as such and are not presented as kill tests. Where the red team's general lesson applies — a dichotomised interaction or a relative "best of a bad lot" rule cannot kill cleanly — VAP-N uses a continuous primary analysis and an absolute pre-registered bar instead. A null result on a KILL test is a successful outcome of the design, not a failure.

### F1 — No acoustic separation on held-out subjects (Phase 0) — **KILL (cross-sectional claim)**

- **Test:** On every public dataset in Phase 0, the acoustic model (Arm H, and separately Arm E) vs the context-only baseline, LOSO, balanced accuracy, pre-registered bar ≥10 pp over baseline with 95% CI excluding zero.
- **Kill condition:** No acoustic model beats the context-only baseline on held-out subjects in *any* dataset, for *any* disease. The cross-sectional claim dies. Phase 1 does not proceed on the cross-sectional claim.
- **What survives a kill:** Nothing of the cross-sectional claim. The longitudinal claim may still be tested **only** if Phase 0 gives a positive, pre-specified reason (e.g. a feature family with high test–retest reliability and a plausible within-person signal in the pilot) — otherwise the programme stops and the null is published.
- **What does NOT count as a kill:** a model that beats the baseline on random k-fold but not on LOSO (that is leakage, F6 territory); a model that beats the baseline in one dataset but not another (that is heterogeneity — see F7, NARROW).

### F2 — Features track recording conditions, not disease (Phase 0/1) — **KILL (acoustic claim as stated)**

- **Test:** (a) The device-only / environment-only model matches the acoustic model on held-out subjects. (b) The acoustic model's performance collapses when tested on a cohort recorded with a different device (LOCO by device), while the context-only model does not. (c) A feature's association with disease disappears when device/ambient-noise is added as a covariate.
- **Kill condition:** (a) or (b) holds — the acoustic signal is a recording-condition signal. The method as a *remote, device-agnostic* phenotyping tool dies. A narrower claim (same-device, same-room phenotyping only) may survive as a NARROW, but it must be re-stated as such, with the device restriction in the method's name and in every description — not silently narrowed.
- **Absolute bar (red-team lesson):** the kill is triggered by a pre-registered number, not by judgement: device-only model within 5 pp of the acoustic model on balanced accuracy, or a LOCO-by-device drop of ≥15 pp that is not recovered by device harmonisation. No "best of a bad lot" advance.
- **Single-device Phase 1 (peer review B2-G2):** F2 is vacuous in a single-device Phase 1 — a device-only model cannot be fitted where there is no device variance — so F2 bites in Phase 0 (multi-dataset, multi-device) and Phase 2 (LOCO by device). Phase 1 is protected against a device artefact it cannot detect by a device-variability sub-study: a subset of Phase 1 participants is recorded on a second device in one session, so a device-only contrast exists within Phase 1 and F2 can be tested there too. Without that sub-study, a Phase 1 result is reported as single-device and F2 as untested in that phase, not as passed.

### F3 — Longitudinal change does not track clinical progression (Phase 1) — **KILL (longitudinal claim)**

- **Test:** The primary longitudinal endpoint (§6.3): correlation between 12-month vocal change (standardised vs own baseline) and clinical-anchor change, analysed as a **continuous** correlation and a linear mixed-effects model — not as a median-split interaction. The red team's criticism of dichotomised interaction tests (deep dive #1, F1) applies here directly: a median split cannot discriminate a wrong cut-point, a noisy feature, and a false hypothesis, and it reports all three as the same null. VAP-N's primary is continuous; the median-split analysis is a sensitivity check only.
- **Kill condition:** The 95% CI for the longitudinal correlation includes zero in the confirmatory cohort, **and** the ON/OFF manipulation check (F4) also fails or is not passed. Either failure alone narrows; both together kill the longitudinal claim outright — the method does not track progression, and no further longitudinal phase is run on that disease.
- **Quantitative bar:** the pre-registered minimum meaningful correlation is **|r| ≥ 0.3** (interim bar, peer-review fix R1, 8 Nov 2026). **Owner + deadline:** the Phase 1 lead is the owner — at pre-registration, from the pilot's observed variability, the lead confirms this 0.3 bar or replaces it with a pilot-justified number, records the choice and its rationale, and locks it. **Confirmatory data collection cannot start until the number is locked.** A statistically significant but trivial correlation (CI excluding zero, |r| < the minimum) is reported as **statistically significant but not meaningful**, and does not pass the gate.
- **Second-stressor / second-anchor replication:** the longitudinal correlation must hold for a second clinical anchor in the same disease (e.g. MDS-UPDRS Part III *and* the clinician-judged dysarthria rating for PD) before any "tracking" language is used. A correlation with one anchor only is a single-anchor result, reported as such.

### F4 — The within-person medication manipulation fails (Phase 1, PD) — **KILL (longitudinal claim, PD)**

- **Test:** In participants with a clinically safe, consented OFF session and a matched ON session, the phonation family's ON–OFF difference (standardised, within-person), tested against zero, and the speech-based ON/OFF discrimination (Thies et al. 2025 reported AUC 0.81 for this discrimination — VAP-N's bar is set from the pilot, not copied from that paper). **Quantitative bar (peer-review fix R1, 8 Nov 2026):** the pre-registered minimum ON–OFF standardised difference is **Cohen's d ≥ 0.5** on the pre-specified primary feature family (phonation), with the ON/OFF discrimination AUC reported as a secondary check (floor AUC ≥ 0.70). **Owner + deadline:** the Phase 1 lead is the owner — at pre-registration, from the pilot's observed variability, the lead confirms these bars or replaces them with pilot-justified numbers, records the choice and its rationale, and locks them. **Confirmatory data collection cannot start until the numbers are locked.**
- **Kill condition:** No detectable ON–OFF difference in any feature family, in the within-person analysis, with adequate power as calculated from the pilot. If the method cannot detect a known, timed pharmacological perturbation of the vocal system, it cannot be trusted to detect slow progression — and the longitudinal claim for PD dies. This is the strongest single test in the battery, because it bypasses between-person stratification noise entirely (the red-team's strengthened design for the BCL-2 programme, applied to voice).
- **Scope:** F4 kills the PD longitudinal claim. It does not kill the ALS or AD longitudinal claims, which have no equivalent timed manipulation — those are tested by F3 alone, and their weaker manipulation basis is stated as a limitation (§11). **Grading consequence (peer review B2-G9):** the ALS/AD longitudinal claims therefore carry a weaker falsification standard by design, and are graded down accordingly — a positive ALS/AD longitudinal result is reported as "correlational tracking, manipulation-unconfirmed" until a timed perturbation exists for that disease. There is no ALS/AD equivalent of a known, timed perturbation in this design, and none is invented here.

### F5 — The disease-signature map fails (Phase 1/2) — **NARROW (not kill)**

- **Test:** The feature-family pattern predicted in §1.5 — phonation/articulation-heavy in PD/ALS, timing/linguistic-heavy in AD — tested by comparing feature-family importance across diseases on identical splits.
- **Narrow condition:** The pattern does not differ by disease as predicted (e.g. timing dominates in all three, or no family dominates in any). The disease-specific signature claim is withdrawn. What survives is a **generic vocal-change** method (voice changes with neurodegeneration, without a disease-specific signature) — a narrower, weaker claim, tested by F3 alone. The three-network-style goalpost move warned against by the red team (dropping a failed leg and declaring the remainder a success) is not permitted here: if the signature map fails, the document records the signature hypothesis as falsified and the generic claim as a *new, separate* hypothesis requiring its own pre-registration — it does not inherit the old hypothesis's success criteria.

### F6 — Leakage / negative-control failure (any phase) — **KILL (the result, and the pipeline if unfixable)**

- **Tests:** (a) Label permutation: shuffled labels must collapse AUC to ~0.50 (the 2026 preprint's permutation collapsed to 0.556 — that is the expected shape). (b) Scrambled/reversed audio must not predict clinical state above chance. (c) Random recording-level k-fold must not be reported as a result; if a published accuracy in the literature is reproduced only under recording-level splits and collapses under LOSO, that published accuracy is reported as leakage-inflated.
- **Kill condition:** Any of (a) or (b) fails — the pipeline is leaking label or metadata information, and every result from that pipeline is withdrawn until the leak is found and fixed. If the leak cannot be found, the pipeline is abandoned. A pipeline that "predicts" from scrambled audio has no valid result to report.
- **What does NOT count as a kill:** a single feature failing a negative control while the pre-registered primary feature family passes — that feature is excluded, the primary result stands, and the exclusion is reported (NARROW at the feature level).

### F7 — Cross-cohort validation fails (Phase 2) — **NARROW (generalisation claim) or KILL (if combined with F3)**

- **Test:** The frozen pipeline (same features, same model, same thresholds) applied to a second cohort (different site/device/language), LOCO.
- **Narrow condition:** Performance drops below the pre-registered bar in the second cohort while holding in the first. The generalisation claim dies; the method survives as a **single-cohort, single-device** method, re-stated as such. A second failure (a third cohort, or a failure combined with F3) kills the method outright — two independent generalisation failures with no identified cause is not a narrow method, it is a non-generalising one.
- **Absolute bar:** LOCO balanced accuracy must be within 10 pp of LOSO accuracy in the first cohort, and must itself beat the context-only baseline by ≥10 pp. A relative "best cohort wins" rule is not used.

### F8 — The bioacoustics transfer fails (Phase 0/1) — **NARROW (transfer claim only)**

- **Test:** Head-to-head, identical splits: Perch-embedding arm vs handcrafted-only arm (§3.3).
- **Narrow condition:** The embedding arm does not beat the handcrafted arm (or does not beat it out-of-cohort). The bioacoustics-transfer claim dies; VAP-N continues as a **human-speech-features-only** method. The discipline transfer (§3.1 — splits, baselines, negative controls, paired data) is unaffected by this failure, because it is a methodological import, not a modelling claim. The transfer failure is reported, not hidden: a null transfer result is the answer to the cross-domain question as posed.

### F9 — Test–retest reliability fails (Phase 1 pilot) — **KILL (longitudinal claim for the affected feature families)**

- **Test:** ICC per feature family from the pilot's repeated sessions (baseline + 3 months, same medication state).
- **Kill condition:** No feature family achieves ICC ≥ 0.5. A feature that cannot be measured reliably twice in the same person in the same state cannot track change in that person. The longitudinal claim dies for all families. If some families pass and others fail, the failing families are excluded (NARROW at the family level) and the passing families proceed.
- **Why this is a kill test, not a pilot detail:** within-person variability swamping the signal is the most likely failure mode for a longitudinal vocal method, and it is detectable in the pilot before the confirmatory cohort is run. Running a confirmatory cohort on unreliable features would be the expensive version of this test.
- **Pilot precision (peer review B2-G6):** the pilot's ICC estimates at n = 20 are noisy — an observed ICC of 0.5 from 20 subjects × 2 sessions has a 95% CI of approximately 0.09–0.77 (computed from the F-distribution for ICC(1,1); an observed 0.7 gives 0.39–0.87, an observed 0.3 gives −0.14–0.65). The pilot gate is therefore decided on the **lower confidence bound**, not the point estimate: a feature family proceeds only if its ICC lower 95% bound is ≥0.3 (with the point-estimate ≥0.5 rule retained for the confirmatory decision). A family whose point estimate clears 0.5 but whose lower bound does not is reported as unreliably estimated, not as passed.

### Summary of the battery

| Test | Phase | KILL or NARROW | What dies if it fails |
|---|---|---|---|
| F1 — no separation on held-out subjects | 0 | **KILL** (cross-sectional) | Cross-sectional claim |
| F2 — features track recording conditions | 0/1 | **KILL** (acoustic claim as stated) | Device-agnostic claim; survives only as same-device method, re-stated |
| F3 — longitudinal change does not track clinical change | 1 | **KILL** (longitudinal, if F4 also fails) | Longitudinal claim |
| F4 — ON/OFF manipulation fails (PD) | 1 | **KILL** (longitudinal, PD) | PD longitudinal claim |
| F5 — disease-signature map fails | 1/2 | **NARROW** | Disease-specific signature; generic claim needs new pre-registration |
| F6 — leakage / negative-control failure | Any | **KILL** (result/pipeline) | The affected results; the pipeline if unfixable |
| F7 — cross-cohort validation fails | 2 | **NARROW**, then **KILL** on second failure | Generalisation claim, then the method |
| F8 — bioacoustics transfer fails | 0/1 | **NARROW** | Transfer claim only |
| F9 — test–retest reliability fails | 1 pilot | **KILL** (affected families) | Longitudinal claim for those families |

Three of the nine tests (F1, F2, F4) can kill a central claim outright on their own; F3+F4 together kill the longitudinal claim; F6 can kill the pipeline. The battery is not a list of ways to narrow the method until something survives — it is a list of ways the method can die, with the narrowing cases labelled as such and the re-statement rule (a narrowed claim is a new claim, with new pre-registration) stated explicitly.

---

## 10. Evidence grade per claim — the graded claim table

Every load-bearing claim in this document, with its grade and its source. A claim not in this table is not a load-bearing claim.

| # | Claim | Grade | Source / basis |
|---|---|---|---|
| C1 | Hypokinetic dysarthria is common in PD, with reduced loudness, monopitch, monoloudness, imprecise articulation, harsh/breathy voice, inappropriate pauses, variable rate | **A** | Cao et al. 2025, npj Parkinson's Dis 11:57; Bioengineering 2026;13:1037 |
| C2 | Objective PD acoustic correlates: reduced F0/intensity variability, shorter MPT, lower HNR/CPP, restricted VSA, lower VAI, longer VOT, increased jitter/shimmer | **A** | Cao et al. 2025; Brain Sci 2025;15:1162 (PC-GITA, 50 PD + 50 controls) |
| C3 | Articulatory weakening in PD is measurable sub-phonemically ([continuant] posteriors, spirantisation) | **A** | Brain Sci 2025;15:1162, PC-GITA |
| C4 | Levodopa changes PD voice, inconsistently across studies; HNR group differences can disappear ON-medication | **A** (variability) / **B–C** (any specific direction) | Thies et al. 2025, npj Parkinson's Dis 11:105; Brain Sci 2025;15:1162; Neurodegener Dis Manag 2025;15:313–322 |
| C5 | PD vocal changes can precede/co-occur with earliest motor signs, by as much as a decade (upper bound) | **B** | Bioengineering 2026;13:1037, citing Cao et al. 2025 (npj Parkinson's Dis 11:57) as the source of the phrasing — verified verbatim in both, 8 Nov 2026 |
| C6 | Over 80% of people with ALS develop dysphonia/dysarthria (mixed spastic–flaccid); speech impairment may begin up to 3 years before diagnosis (figure not confirmed from the chapter text in this pass — verify before external use) | **A** (percentages verified; 3-year lead unconfirmed here) | Pedersen et al. (eds.), Voice-related Biomarkers, Springer 2026, ch. 11 |
| C7 | ALS mixed dysarthria: slowed speech, imprecise consonants, hypernasality, strain–strangled voice, reduced pitch/loudness range, short phrases, inappropriate pauses | **A** | BMC Ear Nose Throat Disord 2001;1:1; Pedersen et al. 2026, ch. 11 |
| C8 | Vowel duration tracks dysarthria status in ALS (20% longer in dysarthric patients vs controls); HNR/F0 range/pause duration separate patients from controls but do not track dysarthria status | **A** (in the cited cohort) / **B** (generalisation) | J Speech Sci 2026;18(3), 53 speakers (17 controls, 36 patients) |
| C9 | AD/MCI: word-finding difficulty, reduced fluency, reduced information density, more/longer pauses, reduced speech rate and prosodic variation as disease advances | **A** | Front Psychol 2021 systematic review (35 papers); Front Aging Neurosci 2026 review |
| C10 | ADReSS acoustic-only baseline 62.5% accuracy; linguistic 76.85%; MMSE RMSE 6.14 (acoustic) / 5.21 (linguistic) | **A** | Luz et al. 2020, arXiv:2004.06833 (ADReSS, 156 participants) |
| C11 | Systematic-review summary: most AD diagnostic studies >88% accuracy, MCI >80% | **B** | Front Psychol 2021 review — aggregates heterogeneous studies; read against C10 |
| C12 | BirdNET v2.4 (June 2023) covers 6,522 classes (incl. 10 non-event classes); Perch 2.0 covers 14,597 species; NatureLM-audio generalises zero-shot to unseen species | **A** | BirdNET-Analyzer README (v2.4, June 2023); Perch 2.0, arXiv:2508.04665 |
| C13 | Macaulay Library 3.2M+ recordings (Wikipedia, accessed Nov 2026; Cornell Mar 2025 said 2.7M — re-check before external use); Xeno-canto ~1,040,000 settled figure retained (not 1,111,111) — founder's page re-check 8 Nov 2026 shows about 1,100,000; adoption pending Mike's decision | **A** (settled figures, dated as stated) | Dossier settled figures, Nov 2026; founder's page few.vu.nl/~rplanque |
| C14 | Classification is not decoding; no verified meaning assigned to any wild animal signal by ML | **A** | Animal-voice review §§1, 3 |
| C15 | Perch embeddings transfer to new bioacoustic tasks with few examples (agile modeling) | **A** (bioacoustics) | Perch 2.0, arXiv:2508.04665 |
| C16 | Perch/bioacoustics embeddings improve human neurodegeneration voice modelling over eGeMAPS/Praat | **C** | Untested; the transfer hypothesis (§3.3) |
| C17 | Vocal acoustic change tracks neurodegenerative progression longitudinally in individuals | **C** | Hypothesis; no longitudinal result established in this pass |
| C18 | Any acoustic feature or model predicts PD/ALS/AD status or progression in a new cohort | **C** | Cross-sectional accuracies are in-sample/fragile; see §2.4 and F1/F7 |
| C19 | A single vocal phenotype separates AD from PD or ALS | **C** | Timing/prosody shared across diseases (§1.5); separation, if any, is a pattern across families |
| C20 | Voice recordings can identify the speaker and cannot be fully anonymised without destroying the clinical signal | **A** | PMC12534620 (2025), speech anonymisation trade-off |
| C21 | eGeMAPS (88 features) + Praat is a standardised, repeatable human-speech feature extraction route | **A** | Eyben et al. eGeMAPS; Boersma & Weenink Praat; openSMILE; 2025 cross-toolkit evaluation |
| C22 | Bye et al.: 100-donor library, screen on 7–16 SALS donors, combination validation on 15 SALS donors, 107 drugs, 3 hits, combination benefit (not formal Bliss synergy) | **A** | Bye et al. Nat Neurosci 2026;29:40–52; red-team verification (Loop 2, B3) — full text contains no "Bliss"; donor-n range corrected per peer review R2, 8 Nov 2026 |
| C23 | No treatment stops or reverses ALS; riluzole, edaravone, tofersen (SOD1 only) are FDA-approved with modest effects | **A** | ALS lit review; NINDS |
| C24 | PXT864 development in Alzheimer's was stopped by Pharnext 14 Feb 2023; no Phase 3; Phase 2 efficacy rested on a historical-placebo comparison with no concurrent control | **A** | Red-team verification (Loop 2, B3), Pharnext press release 14 Feb 2023; Chumakov et al. 2015, Sci Rep 5:7608 (preclinical leg verified) — see §11.4 |
| C25 | VAP-N as a whole method (hypothesis §1.1) | **C** | Components graded above; the whole is the test |

---

## 11. What must be true for it to matter + limitations

### 11.1 What must be true

1. **Vocal features must be measurable reliably in the same person, twice, in the same state.** If test–retest reliability fails (F9), there is no longitudinal method. This is the first thing the pilot tests, before any disease claim is made.
2. **Vocal change must track clinical change, not just separate groups.** A cross-sectional classifier that works and a longitudinal tracker that does not is a phenotyping curiosity, not a readout. F3 is the test.
3. **The signal must survive the confounds.** Age, sex, device, environment, medication state, and disease stage must be controlled, not assumed away. F2 is the test. A method that works only in one room, on one microphone, in one medication state, is a laboratory demonstration.
4. **The result must generalise to a second cohort.** A single-cohort result is a lead, not a method. F7 is the test.
5. **The bioacoustics transfer must beat the human-speech baseline, or be dropped.** A transfer that does not beat eGeMAPS/Praat is not a transfer. F8 is the test.
6. **Participants must consent, and the data must be governed.** A method that cannot meet §7 cannot run, however good its acoustics are. Governance is a precondition, not a downstream step.
7. **A partner institution, an ethics approval, and a clinical team must exist.** The Foundation has no wet lab and no clinic. Without a partner, VAP-N is a protocol document, not a study.

### 11.2 Limitations (stated plainly)

- **Voice changes are non-specific.** Jitter, shimmer, pauses, and prosody change with age, with a cold, with fatigue, with depression, with medication, with alcohol, with smoking, and with the microphone. No vocal feature is pathognomonic for any neurodegenerative disease. VAP-N's defence is the own-baseline longitudinal design and the confound controls in §8 — not a claim that any feature is specific.
- **The PD medication confound is structural, not incidental.** Levodopa changes the voice, inconsistently, and can erase group differences (HNR in PC-GITA). Any PD voice study that does not log medication state and time since last dose is uninterpretable. VAP-N logs both at every session and uses the ON/OFF manipulation as a test (F4) rather than treating medication as noise to be averaged away.
- **The ALS UMN/LMN mix complicates every summary.** Spastic and flaccid dysarthria are opposite phonatory disorders from the same disease. A single ALS "voice score" that averages them is meaningless. VAP-N stratifies by predominance where the record permits and reports the families separately.
- **The AD acoustic-only signal is weak.** The ADReSS baseline is 62.5% acoustic-only vs 76.85% linguistic. A vocal method for AD that ignores language is a weak method. VAP-N's AD arm is acoustic + linguistic, with the arms reported separately so the acoustic contribution is never overstated.
- **The datasets are small.** The field's corpora are tens to low hundreds of subjects (§2.4). VAP-N's power calculation is deferred to the pilot for that reason (§4.5), and no confirmatory N is stated here. A method built on small data must be modest about its claims.
- **Language and culture limit generalisation.** PC-GITA is Colombian Spanish; UCI is English; ADReSS is English. Speech-rate norms, vowel inventories, and pause norms differ by language. Cross-language transfer is a Phase 2 test, not an assumption.
- **Device variability is the largest practical threat.** The mPower experience — large, remote, uncontrolled — shows that device and environment variability can swamp a vocal signal. VAP-N's in-person-first design and its separate remote protocol (§7.4) are the response.
- **Voice is identifiable.** The privacy limitation is not solvable by anonymisation (§7.1). The method's answer is pseudonymisation, governance, and minimisation — not a technical claim that identity has been removed.
- **No clinical use follows from this document.** Even if every test passes, the result is a validated research phenotype and a correlation with clinical anchors — not a diagnostic, screening, or monitoring tool for clinical use. Clinical use would require separate validation, regulatory review, and clinical oversight that are not proposed here.

### 11.3 What would kill it (summary — see §9 for the full battery)

- Phase 0 kills the cross-sectional claim if no acoustic model beats the context-only baseline on held-out subjects (F1).
- Recording-condition confounding kills the acoustic claim as stated if device-only models match the acoustic model (F2).
- Longitudinal failure kills the longitudinal claim if vocal change does not track clinical change *and* the ON/OFF manipulation fails (F3+F4).
- Leakage kills the pipeline if scrambled audio predicts clinical state or permuted labels do not collapse to chance (F6).
- Reliability failure kills the longitudinal claim for the affected families if no family achieves ICC ≥ 0.5 (F9).
- The bioacoustics transfer dies (narrowing, not killing the method) if the Perch arm does not beat the handcrafted arm (F8); the disease-signature map dies (narrowing) if the feature-family pattern does not differ by disease as predicted (F5).

### 11.4 Consistency with the loop's shared facts (red-team report, Loop 2, Worker B3, 8 Nov 2026)

- **PXT864:** This document does **not** cite PXT864 as an ongoing or successful repurposing precedent. The corrected status, per the red-team verification, is: Pharnext stopped development of PXT864 in Alzheimer's disease on **14 February 2023** ("insufficient for commercialization in the short or medium term", no licensing partner); **no Phase 3 ever occurred**; the highest phase reached was Phase 2 (PLEODIAL-I NCT02361424 and PLEODIAL-II NCT02361242); the Phase 2 efficacy signal rested on a **historical-placebo comparison with no concurrent control** (exploratory, single-blind, 45 treatment-naïve mild-AD patients, 36 weeks, CTAD 2016). The preclinical leg (Chumakov et al. 2015, Sci Rep 5:7608 — baclofen + acamprosate synergistically protected neurons and endothelial structures in vitro against Aβ oligomers and alleviated cognitive deficits in two rodent AD models) is verified and is cited here only as preclinical evidence, not as a clinical precedent. PXT864 is a stopped programme, and VAP-N draws no precedent from it.
- **Bye et al.:** Cited with the red-team precision fix as corrected per peer review R2 (C22): library 100 donors, screen 7–16 SALS donors, combination validation on 15 SALS donors, combination benefit only, no formal Bliss synergy demonstrated.
- **Akt/Bad:** VAP-N makes **no novelty claim** about Akt/Bad phosphorylation as a biomarker, and does not depend on one. For the record, and for consistency with the loop's shared facts: the red team refuted in substance the flagship's GAP-FLAG-2 novelty claim — the Ovadia et al. patent family (priority 23 May 2011; EP 3263127 B1 granted 21 Aug 2019; US 10,288,622 B2 granted 14 May 2019, active) proposes pAkt/pAkt:tAkt as an ALS prognostic and treatment-responsiveness biomarker. The patent's direction is opposite to the MPS programme's (high pAkt → responsiveness to an Akt-raising peptide, vs MPS's low pAkt/pBad → benefit from BCL-XL stabilisation) — recorded here so that no VAP-N passage contradicts it. That refutation is B1's territory (flagship / deep dive #1); VAP-N records it here only so that no VAP-N passage contradicts it, and VAP-N's own hypotheses do not use Akt/Bad status as a variable.
- **AGI-183:** VAP-N does not use, cite, or depend on AGI-183. The red team's finding (confirmed absent from the public record; no BCL-XL stabiliser pharmacology known) is B1's territory and is recorded here only for consistency.
- **Falsification discipline:** §9 was written against the red team's bar — the strongest test is one that can kill outright. F1, F2, and F4 can each kill a central claim on their own; F3+F4 together kill the longitudinal claim; F6 can kill the pipeline. Tests that can only narrow (F5, F8, and F7 on first failure) are labelled NARROW explicitly, with the re-statement rule that a narrowed claim is a new claim requiring its own pre-registration — not a silent narrowing of the old claim.

---

## 12. Pre-registration template (filled skeleton)

File this template (e.g. on the Open Science Framework or equivalent) **before** any analysis of the confirmatory data, for each phase separately. The template below is filled for Phase 0; Phase 1/2 pre-registrations replace the bracketed fields and add the longitudinal endpoints in §6.3.

```
VAP-N PRE-REGISTRATION — Phase [0 / 1 / 2]
Date filed: [YYYY-MM-DD]  Filed by: [name, institution]  Version: [n]

1. HYPOTHESIS
   [One paragraph, copied from §1.1, with the phase-specific form stated.]

2. DATASETS / COHORT
   Datasets (Phase 0): [UCI PD / PC-GITA / mPower subset / ADReSS / ADReSSo]
     — N subjects, N recordings, language, device, medication state, access route, licence.
   Cohort (Phase 1/2): [disease, site, N target, inclusion/exclusion, matching]
   Clinical anchors: [MDS-UPDRS / ALSFRS-R / MMSE-MoCA + dysarthria rating, collected same day]

3. RECORDING PROTOCOL (Phase 1/2)
   Tasks T1–T6 as in §4.3, in fixed order. Device: [named device]. Sampling: 44.1 kHz, 16-bit WAV.
   Environment: [room, ambient-noise measurement]. Microphone distance: [fixed distance].
   Medication state (PD): [ON/OFF, time since last dose, LEDD logged per session].

4. FEATURE SETS (frozen)
   Arm H: eGeMAPSv02 (88 features, openSMILE version [x.y.z]) + Praat/Parselmouth
     (jitter local/RAP/PPQ5, shimmer local/dB/APQ3/5/11, HNR, CPP, F0, formants F1–F3, MPT).
   Arm E: log-Mel spectrogram (librosa [version], 128 bins, 25 ms / 10 ms) + frozen Perch 2.0
     embedding (perch-hoplite / Kaggle weights, version [x]) + frozen speech-embedding control
     ([named encoder, version]).
   Arm L (AD/MCI only): ASR [system, version], WER measured on [n]% manually transcribed subset;
     information-unit density, TTR, content-word ratio, word-finding markers, MLU.
   Excluded: speaker-identity features, emotion inference, raw-audio end-to-end primary model.

5. SPLITS
   Primary: leave-one-subject-out (LOSO). Generalisation: leave-one-cohort-out (LOCO).
   Random recording-level k-fold: computed only as a leakage demonstration, never as a result.
   All observations from one subject in one fold.

6. BASELINES
   (a) Chance/majority. (b) Context-only (age + sex + device + medication state + recording
   condition). (c) Handcrafted-only. (d) Embedding-only.
   The acoustic claim is the increment over (b).

7. MODELS
   Logistic regression, SVM, random forest, gradient-boosted trees; soft-voting ensemble as in
   the 2026 multi-cohort preprint. No deep classifier as primary in Phase 0/1. No fine-tuning.

8. METRICS AND SUCCESS BARS
   Phase 0 primary: balanced accuracy, acoustic vs context-only, LOSO.
     Bar: beat baseline by ≥10 pp, 95% CI (bootstrap over subjects) excluding zero.
   Phase 1 primary: longitudinal correlation (vocal change vs clinical-anchor change),
     continuous analysis + linear mixed-effects model (participant random intercept).
     Bar: 95% CI excluding zero AND |r| ≥ 0.3 (interim pre-registered bar; confirmed or
     replaced by the Phase 1 lead from pilot variability before the confirmatory cohort is
     locked — confirmatory collection cannot start until the number is locked) AND ON/OFF
     manipulation passed (PD; Cohen's d ≥ 0.5 on the phonation family, interim bar, same
     owner/deadline) AND same direction in second cohort (Phase 2).
   Secondary: per-class F1, AUC, calibration, feature-importance stability, ICC per family.

9. NEGATIVE CONTROLS
   Label permutation → AUC ~0.50. Scrambled/reversed audio → chance.
   Device-only model must not match the acoustic model.

10. CONFOUND COVARIATES
    Age, sex, device, ambient noise/SNR, medication state + time since last dose (PD),
    disease stage, language, FVC (ALS), cold/fatigue/time of day, UMN/LMN predominance (ALS),
    smoking status, depression (PHQ-9 or equivalent), respiratory disease, hearing loss
    (severe hearing loss excludes the reading task), reflux symptoms.
    All measured per session.

11. FALSIFICATION
    F1–F9 as in §9, with the KILL/NARROW label for each. A KILL result stops the claim;
    a NARROW result re-states the claim as a new hypothesis with a new pre-registration.

12. REPORTING
    All results including nulls, with N subjects, split, baselines, CIs, toolkit versions,
    medication/device conditions, and this pre-registration identifier.
    No individual disease label, risk score, or clinical result is returned to any participant.

13. ETHICS AND GOVERNANCE (Phase 1/2)
    Ethics approval: [reference]. DPIA: [reference]. Data-use agreements: [parties].
    Consent covers §7.2 points 1–6. Retention: [period — default 10 years from last
    publication, §7.3]. Deletion on withdrawal: [procedure — audio + derived features
    deleted within 30 days, deletion logged, §7.3].
    No recording starts until all four prerequisites in §7.5 exist.
```

---

## 13. Sequencing, resources, and what this document does not do

### 13.1 Sequencing

1. **Phase 0 first.** No new person is recorded until Phase 0 is pre-registered, run, and reported — including nulls. Phase 0 is compute + researcher time (one researcher, ~4 months, indicative). It needs no ethics approval for new human data, but it needs dataset licences and data-use agreements for every dataset it uses.
2. **Phase 1 only after the Phase 0 gate.** The Phase 1 pilot (20+20, two sessions) sets test–retest reliability and the power calculation. The confirmatory N is set from the pilot and documented before the confirmatory cohort is locked. No confirmatory N is quoted before that point.
3. **Phase 2 only with a frozen pipeline.** The second cohort is analysed with the pipeline frozen after Phase 1 — same features, same model, same thresholds. Refitting the feature set on the second cohort is not validation.
4. **No clinical use at any phase.** Even a fully successful Phase 2 yields a research phenotype, not a clinical tool.

### 13.2 Resources needed

- **Phase 0:** public datasets (access-governed, §4.1), openSMILE, Praat/Parselmouth, librosa, Perch (`perch-hoplite`, Kaggle weights), scikit-learn, a single workstation-class machine. No GPU required for the primary models.
- **Phase 1/2:** a partner institution with a neurology clinic (PD/ALS/AD cohorts), a clinical team to collect anchors, an ethics approval, governed storage, a standardised recording setup (named microphone + interface), and a researcher to run sessions and QC. No cost is estimated here — any figure would be invented. The Foundation runs no wet lab and no clinic; the partner sets the cost.
- **What is not needed:** no new bioacoustics model, no WAVE engine work, no animal fieldwork, no drug, no device development. VAP-N reuses open tools and standardised tasks.

### 13.3 What this document does not do

- It does not diagnose, screen for, or detect any disease.
- It does not claim a discovery, a treatment, a cure, or a result.
- It does not present PXT864 as a live or successful programme (§11.4).
- It does not claim Akt/Bad novelty (§11.4).
- It does not use AGI-183 or any BCL-XL stabiliser claim.
- It does not present suggested valuations, sites, or partnerships as real.
- It does not authorise any recording, any data sharing, or any clinical use. Those require a partner, an ethics approval, and a consent process that do not exist today.

### 13.4 Open items (VAP-N gaps)

- **GAP-VAP-1:** Phase 0 data access — PC-GITA (on request), mPower (governed), ADReSS/ADReSSo (DementiaBank data-use agreement) not yet requested. Access outcome to be documented in the Phase 0 report.

- **GAP-VAP-1:** Phase 0 data access — PC-GITA (on request), mPower (governed), ADReSS/ADReSSo (DementiaBank data-use agreement) not yet requested. Access outcome to be documented in the Phase 0 report.
- **GAP-VAP-2:** Longitudinal effect size unknown — no confirmatory N until the pilot (§4.5).
- **GAP-VAP-3:** Minimum meaningful longitudinal correlation (|r| bar for F3) and ON/OFF bar (F4) now set as interim pre-registered bars — |r| ≥ 0.3 and Cohen's d ≥ 0.5 on the phonation family (AUC floor 0.70 secondary) — owner: Phase 1 lead; deadline: pre-registration, from pilot variability, before the confirmatory cohort is locked (§9, F3/F4). GAP-VAP-3 closes only when the bars are confirmed or replaced and locked.
- **GAP-VAP-4:** ASR system for Arm L not yet selected — system, version, and WER measurement to be named in the Phase 1c pre-registration; interim WER bar ≤25% on the dysarthric subset (§5.4).
- **GAP-VAP-5:** Partner institution, ethics approval, DPIA, and data-use agreements — none identified. Phase 1 cannot start without them.
- **GAP-VAP-6:** Remote-recording protocol (Phase 2b) not yet validated — in-person/remote agreement (ICC) to be measured before remote data enter the primary analysis.
- **GAP-VAP-7:** Cross-language transfer (Spanish ↔ English) untested — a Phase 2 test, not an assumption.
- **GAP-VAP-8 (new, peer review B2-G3, 8 Nov 2026):** No prior estimate of within-person vocal change *per year* exists. The only anchor found is Skodda et al. 2013 (shimmer change over mean 32.5 months, ref 33); the 12-month window is unproven until the pilot shows detectable change at 12 months above test–retest noise.
- **GAP-VAP-9 (new, peer review B2-G8, 8 Nov 2026):** Perch v2 weights licence not yet confirmed against the Kaggle v2 model page (v1 weights are Apache 2.0); general speech-encoder licence still to be checked per use. Must be confirmed before any governed dataset release in Phase 3.

### 13.5 Peer-review questions (Loop 2, Worker W2-2, 8 Nov 2026) — answered or recorded as open items

Each reviewer question from the peer-review memo §6 is answered here with a factual answer where one exists, or recorded as an open item where it does not. Nothing is left unaddressed.

| # | Reviewer question | Answer / status |
|---|---|---|
| B2-G1 | When devices differ, what harmonisation is applied — and what do you do if the fixed device is discontinued mid-study? Is device variability controlled, or only logged and covaried? | **Answered (§8.2).** ComBat-style feature-level harmonisation (disease group protected) + reference-signal calibration task with a pre-registered drift limit; on discontinuation, cross-device calibration recordings from the same participants and re-validation before the new device's data enter the primary analysis. Controlled, not only logged. |
| B2-G2 | Which phase can actually fail F2? If Phase 1 uses one device throughout, what protects it against a device artefact it cannot detect? | **Answered (§9, F2).** F2 bites in Phase 0 (multi-dataset) and Phase 2 (LOCO by device); Phase 1 gains a device-variability sub-study (subset recorded on a second device) so F2 is testable within Phase 1. Without it, Phase 1's F2 is reported as untested, not passed. |
| B2-G3 | How much does jitter/shimmer/pause duration change per year in PD, and is 12 months enough to see it above test–retest noise? Cite one number. | **Answered in part (§2.1, ref 33).** Skodda et al. 2013: shimmer 6.548 → 11.490 over mean 32.5 months (d = 0.87); nhR 0.051 → 0.103 (d = 0.61); jitter unchanged. No per-year rate exists; whether 12 months suffices is a pilot question (GAP-VAP-8). |
| B2-G4 | What word-error rate on dysarthric speech would disqualify an ASR system for Arm L, and what happens to the AD arm if no system clears it? | **Answered (§5.4).** Interim bar WER ≤25% on the dysarthric subset; if no system clears it, Arm L is dropped and the AD arm becomes acoustic-only, graded down accordingly. |
| B2-G5 | Who is eligible for an OFF session, who decides, and what happens mid-session if the participant cannot continue? | **Answered (§4.3).** The participant's clinician decides; exclusions (severe OFF freezing/falls history, inability to tolerate ≥12 h withdrawal, no escort/transport); rescue: session stops, levodopa given immediately, session recorded ON and flagged. |
| B2-G6 | What is the confidence interval on a pilot ICC at n=20, and what ICC value (with what uncertainty) triggers exclusion of a feature family? | **Answered (§9, F9).** Observed ICC 0.5 at n=20 × 2 sessions → 95% CI ≈ 0.09–0.77 (computed). The pilot gate uses the lower bound: a family proceeds only if its ICC lower 95% bound is ≥0.3. |
| B2-G7 | What resampling is applied before the Perch embedding, and was the resampling validated not to distort jitter/shimmer-adjacent spectral features? | **Answered (§5.5).** 44.1 kHz → 32 kHz, 5-s windows (Perch frontend spec, arXiv:2508.04665); resampling applies to the embedding arm only — Praat jitter/shimmer are computed on the original 44.1 kHz, so they cannot be distorted by it; pilot validates embedding stability across resampling. |
| B2-G8 | What is the licence on the Perch v2 weights for clinical-research use, and does it permit the governed dataset release in Phase 3? | **Answered in part (§2.5, GAP-VAP-9).** Perch code Apache 2.0; Perch v1 weights Apache 2.0 per the Kaggle model page. The v2 weights licence is **not yet confirmed** — to be checked against the Kaggle v2 model page before any Phase 3 dataset release. |
| B2-G9 | What is the ALS/AD equivalent of a known, timed perturbation — or do those longitudinal claims carry a weaker falsification standard by design, and should they be graded down accordingly? | **Answered (§9, F4 scope).** There is no equivalent; the ALS/AD longitudinal claims carry a weaker standard by design (F3 alone) and are graded down — positive results are reported as "correlational tracking, manipulation-unconfirmed". |
| B2-G10 | Which non-age/sex voice confounds are exclusion criteria, which are covariates, and which are unmeasured? | **Answered (§8.2).** Smoking, depression, respiratory disease, reflux: covariates. Severe hearing loss: exclusion for the reading task, covariate otherwise. None of the listed confounds is left unmeasured. |
| B2-G11 | What is the minimum Phase 0 dataset set, and can F1 be run at all on UCI alone? | **Answered (§4.1 step 1).** Floor: UCI (31 subjects) + ADReSS (156 participants). F1 can run on UCI alone only as a single-dataset, single-language result with that limitation stated. |
| B2-G12 | For each settled figure, what is the source and as-of date, and who re-checks it before staging? | **Answered in part (§2.5, C12/C13, status box).** Macaulay 3.2M+ (Wikipedia, accessed Nov 2026; Cornell Mar 2025 said 2.7M — re-check before external use); Xeno-canto ~1,040,000 retained with the 8 Nov 2026 founder's-page re-check (~1,100,000) recorded and adoption pending Mike's decision; Perch 1,542,778 verified against arXiv:2508.04665 Table 1 (8 Nov 2026). Re-check owner before staging: not yet assigned — **open item for the coordinator.** |
| B2-G13 | What is the default retention period, and what exactly happens to audio already collected when a participant withdraws? | **Answered (§7.3).** Default 10 years from last publication (for the ethics approval, not a decided fact); on withdrawal, audio + derived features deleted within 30 days, deletion logged, aggregate results already computed retained. |

---

## 14. References

Only sources verified in this pass (browser search, 7–8 Nov 2026) or in the cited dossier files. No citation, statistic, person, or URL is invented. DOIs are given only where the search result or dossier file supplied them.

1. Cao, F., Vogel, A. P., Gharahkhani, P. & Renteria, M. E. Speech and language biomarkers for Parkinson's disease prediction, early diagnosis and progression. *npj Parkinson's Disease* (2025) 11:57. doi:10.1038/s41531-025-00913-4.
2. Thies, T. et al. Automatic speech analysis combined with machine learning reliably predicts the motor state in people with Parkinson's disease. *npj Parkinson's Disease* (2025) 11:105. doi:10.1038/s41531-025-00959-4.
3. Speech Markers of Parkinson's Disease: Phonological Features and Acoustic Measures. *Brain Sciences* (2025) 15(11):1162. PMCID PMC12650346. (PC-GITA, 50 PD + 50 matched controls.)
4. Voice fundamental characteristics in Parkinson's disease: a case-control study of the Moroccan population. *Neurodegener Dis Manag* (2025) 15(6):313–322. doi:10.1080/17582024.2025.2542667. PMID 40801237.
5. Toward Interpretable Voice-Based Parkinson's Disease Screening via Joint Transfer Function–Feature–Classifier–Ensemble Selection. *Bioengineering* (2026) 13:1037. doi:10.3390/bioengineering13091037.
6. An Interpretable and Auditable Pipeline for Robust Multi-Cohort Detection of Parkinson's Disease from Voice Data with Data Leakage Prevention. *Research Square* preprint (posted 15 May 2026). doi:10.21203/rs.3.rs-9430849/v1. (996 recordings, 332 subjects, LOSO, AUC 0.8836 — cited as evidence of the leakage problem and as a methodological model, not as a detector.)
7. Voice-Based Early Diagnosis of Parkinson's Disease Using Spectrogram Features and AI Models. *PMC* (2025). PMCID PMC12562018. (81-sample dataset; BiLSTM 97% accuracy — cited with its sample size, not as generalisation evidence.)
8. Little, M. A., McSharry, P. E., Hunter, E. J. & Ramig, L. O. Suitability of dysphonia measurements for telemonitoring of Parkinson's disease. *IEEE Trans Biomed Eng* (2009) 56:1015–1022. (UCI dataset: 195 recordings, 31 people, 23 PD + 8 controls.)
9. Orozco-Arroyave, J. R. et al. New Spanish speech corpus database for the analysis of people suffering from Parkinson's disease. *Proc LREC* (2014). (PC-GITA: 100 Colombian Spanish speakers, 50 PD + 50 controls, 44.1 kHz, 16-bit.)
10. Bot, B. M. et al. The mPower study, Parkinson disease mobile data collected using ResearchKit. *Sci Data* (2016) 3:160011. PMID 26938265.
11. Luz, S., Haider, F., de la Fuente, S., Fromm, D. & MacWhinney, B. Alzheimer's Dementia Recognition through Spontaneous Speech: The ADReSS Challenge. *INTERSPEECH 2020*. arXiv:2004.06833. (156 participants; acoustic baseline 62.5%, linguistic 76.85%.)
12. Ten Years of Research on Automatic Voice and Speech Analysis of People With Alzheimer's Disease and Mild Cognitive Impairment: A Systematic Review. *Front Psychol* (2021). (35 papers; >88% AD, >80% MCI as reported in the review — see C11.)
13. Speech and sMRI as multimodal biomarkers for early detection of Alzheimer's disease using machine learning, deep learning, and transformer-based models. *Front Aging Neurosci* (27 Oct 2026). doi:10.3389/fnagi.2026.1975870.
14. Natural Speech Encodes Early Markers of Cognitive Decline: Evidence from Clinical Conversations. *Interspeech 2026*. (175 participants, phone-call speech, best fusion AUC 0.92 — conference paper, cited as ecologically-valid signal, not as a validation.)
15. Vowel lengthening as a marker of dysarthria status in ALS: Evidence from read speech. *J Speech Sci* (2026) 18(3). doi:10.13064/KSSS.2026.18.3.109. (53 speakers; vowel duration ~20% longer in dysarthric ALS.)
16. Laryngeal dysfunction in Amyotrophic Lateral Sclerosis: a review and case report. *BMC Ear Nose Throat Disord* (2001) 1:1. PMCID PMC60006.
17. Pedersen, M. et al. (eds.) *Voice-related Biomarkers*. Springer (2026), ch. 11, Neurodegenerative Diseases: Aspects of Voice-Related Biomarkers. (ALS: >80% develop dysphonia/dysarthria; speech impairment may begin up to 3 years before diagnosis.)
18. Bye, C. R., Qian, E., et al. Large-scale drug screening in iPSC-derived motor neurons from sporadic ALS patients identifies a potential combinatorial therapy. *Nat Neurosci* (2026) 29:40–52. doi:10.1038/s41593-025-02118-7. PMID 41286450. (100-donor library; screen on 7–16 SALS donors; combination validation on 15 SALS donors; 107 drugs; combination benefit, no formal Bliss synergy — red-team verification, Loop 2, B3; donor-n range corrected per peer review R2, 8 Nov 2026.)
19. Navigating the tradeoff between personal privacy and data utility in speech anonymization for clinical research. *PMC* (2025). PMCID PMC12534620. (Voice re-identification; useful-or-anonymous trade-off.)
20. Chumakov, I. et al. Synergistic effects of baclofen and acamprosate (PXT864) in rodent models of Alzheimer's disease. *Sci Rep* (2015) 5:7608. doi:10.1038/srep07608. (Preclinical leg only. Development in Alzheimer's stopped 14 Feb 2023 — see ref. 21.)
21. Pharnext press release, 14 Feb 2023 (development of PXT864 in Alzheimer's stopped; no licensing partner; refocus on PXT3003). Reported via Fierce Biotech and financial filings; verified by red team, Loop 2, Worker B3, 8 Nov 2026. (No Phase 3; Phase 2 efficacy on a historical-placebo comparison, no concurrent control.)
22. Eyben, F. et al. The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for voice research and affective computing. *IEEE Trans Affective Computing* (2016) 7(2):190–202. (eGeMAPS; extended set eGeMAPSv02, 88 features, via openSMILE.)
23. Boersma, P. & Weenink, D. Praat: doing phonetics by computer. (Reference implementation for F0, formants, jitter/shimmer/HNR; via Parselmouth in Python.)
24. Perch 2.0: "Perch 2.0: The Bittern Lesson for Bioacoustics". arXiv:2508.04665. (14,795 classes — 14,597 species + 198 general; 1,542,778 recordings, verified against the paper's Table 1, 8 Nov 2026; frontend takes 5 s of audio at 32 kHz; agile modeling; code Apache 2.0, google-research/perch.)
25. Robinson, D. et al. NatureLM-audio: An Audio-Language Foundation Model for Bioacoustics. arXiv:2411.07186 (Nov 2024; ICLR 2025).
26. Sharma, P. et al. Contextual and combinatorial structure in sperm whale vocalisations. *Nat Commun* (2024) 15:3617. doi:10.1038/s41467-024-47221-8. (156 distinct codas; structure, no meanings assigned.)
27. Hagiwara, M. et al. BEANS: The Benchmark of Animal Sounds. *ICASSP 2023*. arXiv:2210.12300.
28. Rauch, L. et al. BirdSet: A large-scale dataset for audio classification in avian bioacoustics. *ICLR 2025*.
29. A Survey of Open Voice and Speech Datasets for the Screening and Evaluation of Parkinson's Disease. *Zenodo* (2026). doi:10.6084/m9.figshare.23849127. (Ten datasets; PC-GITA, MDVR-KCL, UCI, mPower usage.)
30. Comparative Evaluation of Acoustic Feature Extraction Tools for Clinical Speech Analysis. (2025). (openSMILE vs Praat vs librosa; cross-toolkit agreement varies by feature — the reason §8.3 is mandatory. Full citation details — authors, journal, DOI — to be confirmed before external use.)
31. Research Lab Loop dossier (internal, staged): `research-lab-loop/dossier/animal-voice-decoding-lit-review.md`; `bioacoustics-github-survey.md`; `cross-disease-patterns.md`; `parkinsons-gaucher-lysosomal-program.md`; `als-compounds-lit-review.md`; `pattern-deep-dive-02-alzheimers-three-network.md`.
32. Research Lab Loop 2, Worker B3 (verification / red team). Independent verification + red-team report, 8 Nov 2026. `research-lab-loop-2/dossier/verification-red-team.md`. (PXT864 stopped 14 Feb 2023; Bye screen n = 7–16, combination validation n = 15, no Bliss synergy; Akt/Bad novelty refuted in substance — Ovadia et al. patent family, US 10,288,622 B2; AGI-183 confirmed absent; falsification-battery stress test.)
33. Skodda, S., Grönheit, W., Mancinelli, N. & Schlegel, U. Progression of voice and speech impairment in the course of Parkinson's disease: a longitudinal study. *Parkinson's Disease* (2013) Article ID 389195. PMCID PMC3872441. (80 PD + 60 controls, mean interval 32.5 months: shimmer 6.548 → 11.490, p < 0.0001, Cohen's d 0.87; noise-to-harmonics ratio 0.051 → 0.103, p < 0.0001, d 0.61; jitter did not change significantly; deterioration did not correlate with the time interval — the longitudinal anchor for the 12-month window, §2.1.)

---

*Nothing in this document is medical advice. No method in it diagnoses, screens for, detects, treats, or cures any disease. All clinical claims are literature facts about specific studies for specific populations. Figures are as-of their source dates; verify again before any public use.*
