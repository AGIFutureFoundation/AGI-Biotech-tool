# Reimbursement Annex — Psychedelic-Assisted Therapy Coding Landscape

**Status:** Published research brief in this repo's `research/` folder — not a billing or coverage determination.
**Program:** Bio research expansion — psychedelic research section.
**Purpose:** A faithful extraction of the coding structure in the source guide, so the lab and its advisors can see what the reimbursement landscape looks like *if* a psychedelic-assisted therapy model ever reaches a billable, lawful clinical setting. This annex describes codes. It does not promise payment, coverage, or legality.

## Regulatory frame — read first

- **Psychedelics are Schedule I controlled substances under federal law.** This work is research, therapy-model design, and reimbursement-landscape mapping. It is **never an offer of treatment**, and nothing in this annex claims that any psychedelic treats, cures, or diagnoses any condition.
- **No psychedelic-assisted therapy is FDA-approved as a billable treatment at the time of writing.** MDMA-assisted therapy received an FDA complete response letter in 2024 (not approved). Psilocybin holds FDA Breakthrough Therapy designation for certain indications — a designation is not an approval. Oregon and Colorado operate state-regulated models; those are state programs, not federal approval and not a Medicare/Medicaid benefit.
- **No compound is proposed here for human use.** Any future human use would require its own stated regulatory path (e.g., FDA investigational new drug application, DEA Schedule I researcher registration, IRB oversight, state authorization where applicable). That path is not described here because no such proposal is being made.
- **Filed fact vs. proposed plan:** the codes below are filed, published CPT/HCPCS codes as listed in the source guide. A billable psychedelic-assisted therapy service built on them is a *proposed plan*, not a filed fact.

## Source

- *A Guide to CPT and HCPCS Codes for Psychedelic-Assisted Therapy — Charts* (PDF, 7 pages), file as provided: `~/workspace/user/files/A-Guide-to-CPT-and-HCPCS-Codes-for-Psychedelic-Assisted-Therapy_Charts.pdf`. No publication date is visible in the document as provided.
- **All RVU figures in this annex are 2023 Medicare non-facility Total Relative Value Units** (Work + Practice Expense + Malpractice RVUs), exactly as footnoted in the source guide. They are 2023 values, not current-year values, and they are Medicare non-facility values — other payers and settings differ.
- Code descriptions, times, RVUs, and MUEs below are transcribed from the guide's code-description tables. Where the guide's own pages disagree with each other, the disagreement is flagged rather than smoothed over (see "Discrepancies inside the source guide").

## How to read this annex

- **CPT** = Current Procedural Terminology (American Medical Association). **HCPCS** = Healthcare Common Procedure Coding System (CMS). **QHP** = qualified health care professional. **E/M** = evaluation and management. **MUE** = Medically Unlikely Edit — the maximum units a provider would report under most circumstances for a single patient on a single date of service (National Correct Coding Initiative).
- A **"+"** before a code means it is an **add-on code**: list it separately in addition to the primary procedure code. *Italics in the source guide* mark add-on codes for practitioner consideration based on services provided and factors present.
- **Restriction A** (Medicare billing): eligible providers include physicians (MD, DO), clinical psychologists (CP), clinical social workers (CSWs), clinical nurse specialists (CNSs), nurse practitioners (NPs), physician assistants (PAs), certified nurse-midwives (CNMs), independently practicing psychologists (IPPs), and certified registered nurse anesthetists (CRNAs, for supervision of diagnostic psychological and neuropsychological tests) — per CMS, 2022, as cited in the guide.
- **Restriction B**: CPT guidance instructs that E/M codes (99091, 99202–99499) should only be reported by physicians (MD, DO) or other qualified health care professionals, which CMS defines as NPs, CNSs, CNMs, and PAs.
- **Clinical staff**, per the AMA definition quoted in the guide: "a person who works under the supervision of a physician or other qualified health care professional, and who is allowed by law, regulation and facility policy to perform or assist in the performance of a specific professional service but does not individually report that professional service." Technician certification levels may range from a high school diploma to a baccalaureate or even a master's degree in psychology, with additional training in standardized administration and scoring of psychological and/or neuropsychological testing.
- The guide organizes the work into **three clinician columns**: (1) credentialed clinicians licensed to provide psychotherapy; (2) E/M-eligible clinicians only; (3) clinical staff or technician. Code choice depends on clinician type, services provided, session duration — and, repeatedly, **payer negotiation**.

---

## 1. Screening, assessment, and intake

Choice depends on clinician type and services provided.

### 1A. Psychiatric diagnostic evaluation

| Code | Description | Time | 2023 Medicare non-facility RVU | MUE | Restriction |
|---|---|---|---|---|---|
| 90791 | Psychiatric diagnostic evaluation | — | 5.16 | 1 | A |
| 90792 | Psychiatric diagnostic evaluation with medical services | — | 5.80 | 1 | A |
| +90785 | Interactive complexity; may be added to psychotherapy services (90791, 90832, 90834, 90837, or 90853) when complicating factors are present during the visit | — | 0.44 | 1 | A |

- 90791 is the psychotherapy-column evaluation; 90792 (with medical services) is the E/M-eligible-column evaluation. Consider +90785 with either when complicating factors are present.
- New-patient E/M codes may also apply at intake: 99202 (15–29 min, RVU 2.15), 99203 (30–44 min, 3.33), 99204 (45–59 min, 4.94), 99205 (60–74 min, 6.52) — all restriction B, MUE 1. Prolonged-service add-ons +99415–+99417 may apply with E/M codes (see §4).

### 1B. Psychological / neuropsychological testing

| Code | Description | Time | 2023 Medicare non-facility RVU | MUE | Restriction |
|---|---|---|---|---|---|
| 96130 | Psychological testing evaluation services by a physician or other QHP, including integration of patient data, interpretation of standardized test results and clinical data, clinical decision making, treatment planning and report, and interactive feedback to the patient, family member(s), or caregiver(s), when performed; first hour | ~60 min | 3.55 | 1 | A |
| +96131 | Each additional hour of 96130 | ~60 min | 2.56 | 7 | A |
| 96136 | Psychological or neuropsychological test administration and scoring by a physician or other QHP, two or more tests, any method, first 30 minutes | ~30 min | 1.26 | 1 | A |
| +96137 | Each additional 30 minutes of 96136 | ~30 min | 1.16 | 11 | A |
| 96138 | Psychological or neuropsychological test administration and scoring by technician, two or more tests, any method, first 30 minutes | ~30 min | 1.01 | 1 | Technician |
| +96139 | Each additional 30 minutes of 96138 | ~30 min | 1.04 | 11 | Technician |
| 96127 | Brief emotional/behavioral assessment (e.g., depression inventory, ADHD scale), with scoring and documentation, per standardized instrument; report code for each instrument used | — | 0.14 | 3 | A |
| 96146 | Psychological or neuropsychological test administration, with single automated, standardized instrument via electronic platform, with automated result only | — | 0.07 | 1 | A |

- 96127 is per standardized instrument (report once per instrument used); 96146 is the single-automated-instrument, electronic-platform equivalent.
- The guide's quick-reference grid also lists **96103** in the testing row (paired with +96131). 96103 does **not** appear in the guide's code-description tables, so no description, time, RVU, or MUE for it is given here. Treat 96103 as an unresolved reference, not as a confirmed code choice.

---

## 2. Preparation

Choice depends on payer negotiation, session duration, and clinician type.

### 2A. Psychotherapy (credentialed clinicians licensed to provide psychotherapy)

| Code | Description | Time | 2023 Medicare non-facility RVU | MUE | Restriction |
|---|---|---|---|---|---|
| 90832 | Psychotherapy, 30 minutes with patient | 16–37 min | 2.23 | 2 | A |
| 90834 | Psychotherapy, 45 minutes with patient | 38–52 min | 2.95 | 2 | A |
| 90837 | Psychotherapy, 60 minutes with patient | 53+ min | 4.34 | 2 | A |
| +90785 | Interactive complexity (see §1A) | — | 0.44 | 1 | A |
| 90853 | Group psychotherapy (other than of a multiple-family group), no more than 12 participants | 45–60 min | 0.79 | — | A |

- **Group:** practitioners using group therapy may consider 90837 (60 minutes) together with 90853, with **modifier 59** (distinct procedural service).
- **Two licensed psychotherapists:** if two licensed psychotherapists are involved, consider negotiating use of **modifier XP** (distinct service performed by a different practitioner).
- **90-minute session:** the guide suggests negotiating with the insurer to bill 90834 twice for a 90-minute session. That is a negotiation position, not a coding rule — see Limits.

### 2B. Psychotherapy with E/M (E/M-eligible clinicians only)

| Code | Description | Time | 2023 Medicare non-facility RVU | MUE | Restriction |
|---|---|---|---|---|---|
| +90833 | Psychotherapy, 30 minutes with patient, when performed with an evaluation and management service | 16–37 min | 2.05 | 2 | B |
| +90836 | Psychotherapy, 45 minutes with patient, when performed with an evaluation and management service | 38–52 min | 2.60 | 2 | B |
| +90838 | Psychotherapy, 60 minutes with patient, when performed with an evaluation and management service | 53+ min | 3.44 | 2 | B |
| 99212–99215 | E/M, established patient (see §4) | 10–54 min | 1.68–5.31 | 1–2 | B |
| +90785 | Interactive complexity | — | 0.44 | 1 | A |

- The same group-therapy (90837 + 90853, modifier 59), two-therapist (modifier XP), and bill-90834-twice-for-90-minutes negotiation points apply in this column as well.

### 2C. Medication management (E/M-eligible clinicians only)

- E/M 99212–99215, with a psychotherapy add-on if appropriate (+90833 / +90836 / +90838) and +90785 where complicating factors are present.

---

## 3. Medication administration session

Choice depends on payer negotiation and clinician type. This is the phase the guide treats as the least settled in coding terms.

### 3A. Psychedelic medication therapy codes (Category III — see Limits)

| Code | Description | Time | 2023 Medicare non-facility RVU | MUE | Who reports |
|---|---|---|---|---|---|
| 0820T | Continuous in-person monitoring and intervention (e.g., psychotherapy, crisis intervention), as needed, during psychedelic medication therapy; first physician or other QHP, each hour | 60 min | N/A | — | Physician or other QHP |
| +0821T | Same; second physician or other qualified health care professional, concurrent with first physician or other QHP, each hour | 60 min | N/A | — | Physician or other QHP |
| +0822T | Same; clinical staff under the direction of a physician or other QHP, concurrent with the first physician or other QHP, each hour | 60 min | N/A | — | Clinical staff |

- 0820T is the first QHP, per hour. +0821T is the second QHP, concurrent, per hour. +0822T is clinical staff under a physician/QHP's direction, concurrent, per hour.
- **RVU is N/A for all three codes.** Category III codes are tracking codes; they carry no established RVU in the guide's table.

### 3B. Medical oversight (E/M-eligible clinicians only)

- E/M for medical oversight only: **99212–99215** (established patient), plus prolonged-service add-ons **+99415, +99416, +99417** as needed (see §4).
- The guide presents two negotiation models for compensating practitioners in this phase:
  1. **Negotiate to compensate all practitioners (including medical oversight):** H2020.
  2. **Negotiate to compensate two practitioners, with medical oversight billed separately:** H2020 for the therapy team plus 99212–99215 with +99415–+99417 for medical oversight.
- On H2020 vs. H2010, see "Discrepancies inside the source guide" below. The guide's quick-reference grids cite H2020 for the team-based rate negotiation.

### 3C. What the session codes do not do

- The Category III codes describe **continuous in-person monitoring and intervention as needed** during psychedelic medication therapy. They do not describe the drug itself, its acquisition, its administration as a pharmacologic act, or any outcome. There is no drug code, no drug payment, and no efficacy claim in this annex.
- Staffing in the guide's model is explicitly a **two-practitioner model** (first QHP + second QHP and/or clinical staff), with medical oversight billed separately where applicable.

---

## 4. E/M and prolonged services (reference table)

| Code | Description | Time | 2023 Medicare non-facility RVU | MUE | Restriction |
|---|---|---|---|---|---|
| 99202 | E/M, new patient, straightforward MDM, minimal number/complexity of problems addressed | 15–29 min | 2.15 | 1 | B |
| 99203 | E/M, new patient, low MDM | 30–44 min | 3.33 | 1 | B |
| 99204 | E/M, new patient, moderate MDM | 45–59 min | 4.94 | 1 | B |
| 99205 | E/M, new patient, high MDM | 60–74 min | 6.52 | 1 | B |
| 99212 | E/M, established patient, straightforward MDM | 10–19 min | 1.68 | 2 | B |
| 99213 | E/M, established patient, low MDM | 20–29 min | 2.68 | 2 | B |
| 99214 | E/M, established patient, moderate MDM | 30–39 min | 3.79 | 2 | B |
| 99215 | E/M, established patient, high MDM | 40–54 min | 5.31 | 1 | B |
| +99415 | Prolonged clinical staff service during an E/M service in the office/outpatient setting, direct patient contact with physician supervision; first hour (use with 99202–99205, 99212–99215) | 30+ min | 0.56 | 1 | B |
| +99416 | Prolonged clinical staff service; each additional 30 minutes (use with 99415) | 15+ min | 0.26 | 3 | B |
| +99417 | Prolonged office/outpatient E/M service beyond the total time for Level 5 E/M code only (99205, 99215); each 15 minutes | 15 min | 0.92 | 6 | B |

MDM = medical decision making. These E/M codes appear in the guide at intake (new patient), in medication management, and as medical oversight during the administration session.

---

## 5. Integration

The guide states it directly: **"See code options above for Preparation."**

- Integration uses the same coding options as preparation: psychotherapy 90832 / 90834 / 90837 (+90785 where applicable), group 90853 with modifier 59, the two-therapist modifier XP consideration, and, for E/M-eligible clinicians, the psychotherapy add-ons +90833 / +90836 / +90838 with E/M 99212–99215.
- No separate integration-specific code is listed in the guide.

---

## 6. Full code list (as transcribed from the guide)

| Code | Short description | Time | 2023 RVU | MUE |
|---|---|---|---|---|
| +90785 | Interactive complexity | — | 0.44 | 1 |
| 90791 | Psychiatric diagnostic evaluation | — | 5.16 | 1 |
| 90792 | Psychiatric diagnostic evaluation with medical services | — | 5.80 | 1 |
| 90832 | Psychotherapy, 30 min | 16–37 min | 2.23 | 2 |
| +90833 | Psychotherapy, 30 min, with E/M service | 16–37 min | 2.05 | 2 |
| 90834 | Psychotherapy, 45 min | 38–52 min | 2.95 | 2 |
| +90836 | Psychotherapy, 45 min, with E/M service | 38–52 min | 2.60 | 2 |
| 90837 | Psychotherapy, 60 min | 53+ min | 4.34 | 2 |
| +90838 | Psychotherapy, 60 min, with E/M service | 53+ min | 3.44 | 2 |
| 90853 | Group psychotherapy, ≤12 participants | 45–60 min | 0.79 | — |
| 96127 | Brief emotional/behavioral assessment, per instrument | — | 0.14 | 3 |
| 96130 | Psychological testing evaluation, first hour | ~60 min | 3.55 | 1 |
| +96131 | Each additional hour of 96130 | ~60 min | 2.56 | 7 |
| 96136 | Test administration/scoring by physician/QHP, first 30 min | ~30 min | 1.26 | 1 |
| +96137 | Each additional 30 min of 96136 | ~30 min | 1.16 | 11 |
| 96138 | Test administration/scoring by technician, first 30 min | ~30 min | 1.01 | 1 |
| +96139 | Each additional 30 min of 96138 | ~30 min | 1.04 | 11 |
| 96146 | Single automated instrument via electronic platform | — | 0.07 | 1 |
| 99202–99205 | E/M, new patient | 15–74 min | 2.15–6.52 | 1 |
| 99212–99215 | E/M, established patient | 10–54 min | 1.68–5.31 | 1–2 |
| +99415 | Prolonged clinical staff service, first hour | 30+ min | 0.56 | 1 |
| +99416 | Prolonged clinical staff service, each additional 30 min | 15+ min | 0.26 | 3 |
| +99417 | Prolonged E/M beyond Level 5, each 15 min | 15 min | 0.92 | 6 |
| 0820T | Psychedelic medication therapy monitoring, first QHP, per hour | 60 min | N/A | — |
| +0821T | Same, second QHP, concurrent, per hour | 60 min | N/A | — |
| +0822T | Same, clinical staff, concurrent, per hour | 60 min | N/A | — |
| H2010 | Comprehensive medication services, per 15 min (not payable by Medicare) | 15 min | N/A | — |

H2020 (cited in the guide's quick-reference grids for team-based rate negotiation) has no entry in the guide's code-description table; see discrepancies below.

---

## 7. Limits — stated plainly

1. **0820T–0822T are Category III codes.** Category III is the CPT tracking-code category for emerging technology, services, and procedures. These codes exist so utilization can be tracked; they are not Category I codes, they carry no RVU in the guide (N/A), and their presence in a code book is not a coverage decision, a payment rate, or a promise that any payer will pay them.
2. **The guide itself says choices depend on payer negotiation.** Its preparation and administration-session sections are headed, verbatim in substance, "choice depends on payer negotiation, session duration, and clinician type" and "choice depends on payer negotiation and clinician type." Billing 90834 twice for a 90-minute session, using modifier XP for two therapists, and compensating the full team via H2020 are all framed in the guide as things to *negotiate* with an insurer — not as entitlements.
3. **This is the coding landscape, never a guarantee of payment.** Nothing in this annex states that Medicare, Medicaid, or any commercial payer covers psychedelic-assisted therapy, pays any of these codes in this combination, or will pay them in future. Coverage requires a lawful, approved service, a covered benefit, medical necessity as the payer defines it, and a negotiated rate. None of those exists for psychedelic-assisted therapy as a general billable service today.
4. **RVUs are 2023 Medicare non-facility values.** They are stale by construction and setting-specific. Do not quote them as current rates or as what any payer pays.
5. **A code is not a treatment claim.** Correct coding of a psychotherapy or monitoring session says nothing about whether the underlying intervention is safe, effective, approved, or lawful. No efficacy, safety, or treatment claim is made or implied anywhere in this annex.
6. **Scope of this annex.** It covers the therapy-model coding structure only: screening/assessment/intake, preparation, the medication administration session, and integration. It does not cover drug supply, drug cost, facility fees, licensure, DEA/FDA authorization, IRB approval, or state program rules. Any of those would need their own annex with their own sources.

## 8. Discrepancies inside the source guide (flagged, not resolved)

- **H2020 vs. H2010.** The guide's quick-reference grids cite **H2020** for negotiating a team-based rate to compensate all providers. The guide's code-description table lists **H2010** ("Comprehensive medication services, per 15 minutes — not payable by Medicare") and gives no description for H2020. These are different HCPCS codes. This annex reports both exactly as they appear and does not assume one is a typo for the other. A billing advisor must resolve which code, if either, applies before any use.
- **96103.** Listed in the quick-reference testing row (with +96131) but absent from the code-description tables. No description, time, RVU, or MUE is available from the guide.
- **No publication date.** The document as provided carries no visible publication date, author, or publisher imprint in the extracted text. RVU vintage (2023) is the only date anchor in the guide itself.

## 9. What would have to be true before any of this is billable

Stated as open conditions, not as predictions:

1. A lawful clinical setting: federal authorization for the substance and the service (FDA approval or an authorized investigational/state-regulated pathway), DEA registration, and state licensure.
2. A coverage decision: a payer benefit covering the service, with the Category III codes (or their successors) accepted for payment.
3. Negotiated rates: the team-based and two-practitioner compensation models the guide describes are negotiation outcomes, not defaults.
4. Current coding: re-verification against the current-year CPT/HCPCS code set and current Medicare RVUs, since this annex is anchored to 2023 values and a guide of unknown publication date.
5. Independent billing and legal review before any claim is submitted.

## Sources and dates

- *A Guide to CPT and HCPCS Codes for Psychedelic-Assisted Therapy — Charts* (7-page PDF, as provided in `~/workspace/user/files/`). RVU footnote: 2023 Medicare Non-facility Total RVU. No publication date visible in the document. Read in full, 2026-11-07.
- Regulatory context (Schedule I status; MDMA complete response letter 2024; psilocybin Breakthrough Therapy designation; Oregon/Colorado regulated models) is program standing context, not drawn from the coding guide. Verify against primary FDA/DEA sources before external use.
- This annex was staged 2026-11-07. It is a draft for internal program use. Nothing here has been submitted to any payer, regulator, or publisher.
