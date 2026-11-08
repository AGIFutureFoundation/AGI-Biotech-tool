# Patent Status Verification — Bio Research Expansion Package

**Verification date:** 2026-11-07 PST (Google Patents pages crawled 2026-11-08 00:57–01:02 UTC)
**Verifier:** patent-status verification worker (local staging only)
**Scope:** four patents in the bio research expansion / SmartCiti patent set
**Status of this file:** staging record for the lab loop. This is a verification record, **not a legal opinion and not a freedom-to-operate (FTO) clearance**. No patent in this file may be treated as free to use on the strength of this file alone — see "The expired ≠ free to use rule" below.

## Method and sources used

For each patent the following were tried, in order:

1. **Google Patents direct page fetch** (`browser.open` on `patents.google.com/patent/<number>/en`) — including the page's Info block, timeline, and the USPTO-sourced **Legal Events** table at the foot of the page (maintenance-fee payments, lapse events, abandonment events).
2. **Espacenet bibliographic record** via the Firecrawl helper (`~/workspace/custom-connectors/custom.firecrawl/bin/firecrawl_scrape.py`, scrapes 01a1b8ad-2ca7-7162-a8d7-be3afd8864cb and 01a1b8ad-de67-7583-bb27-d13bb0c18e74) — for priority chains and family members.
3. **EPO Global Dossier** via Firecrawl (scrapes 01a1b8af-0510-7798-9d37-f57ca0aa1d90 and 01a1b8af-055d-71c1-921a-0d0757d574d6) — returned only the "Dossier documents are being retrieved..." shell; the dossier content loads by AJAX and was **not** retrievable this way.
4. **USPTO Patent Center** via Firecrawl (`patentcenter.uspto.gov/applications/11269908`, scrape 01a1b8ad-2d0c-764f-9413-9664d24925a1) — **HTTP 403 Forbidden**; the page body was only the "Loading..." shell. Patent Center could not be reached by any non-browser route tried.
5. **Lens.org** (`lens.org/lens/patent/<number>`) via `browser.open` — **HTTP 403, access denied**, for both patents tried. Not retried (access denial).
6. **Web search** (`browser.search`) — used for the JP patent only; returned no register page for the patent itself.

**Standing caveat on Google Patents:** Google itself states its legal-status label "is an assumption and is not a legal conclusion. Google has not performed a legal analysis and makes no representation as to the accuracy of the status listed." Where Google's header status and its own USPTO-sourced legal-events table conflict (US 8,918,278 B2, below), the conflict is recorded, not resolved by picking one side.

---

## 1. JP6062995B2 — Pharnext, Alzheimer's drug combinations

| Field | Value |
|---|---|
| Title | A new therapeutic approach to treat Alzheimer's disease |
| Assignee | Pharnext SA |
| Inventors | Daniel Cohen, Ilya Chumakov, Serguei Nabirotchkin |
| JP application | JP2015090340A, filed 2015-04-27 |
| Grant | JP6062995B2, granted 2017-01-18 |
| Priority | EP09306048A, filed 2009-11-03 (Espacenet); PCT family WO2011054759A1 |
| Anticipated expiration (per brief, **unverified**) | 2030-10-29 |
| **Verified status** | **COULD NOT VERIFY — needs live-browser agent (J-PlatPat)** |

### What was established

- The patent exists and the bibliographic facts above are confirmed by Espacenet (family 041693027) and by the Google Patents page (crawled 2026-11-08 00:59 UTC; DC dates 2015-04-27 and 2017-01-18; application JP:2015090340A).
- Family members confirmed on Espacenet include US8809302B2 (US grant), EP2496226B1, CA2779070C, EA024465B1, JP5977172B2 (earlier JP grant in the same family), JP2013510114A, and WO2011054759A1. The family is large and multi-jurisdictional.
- The brief's stated status is "Expired — Fee Related" with anticipated expiration 2030-10-29. The 2030-10-29 date is consistent with a 20-year term running from a PCT filing date of 2010-10-29 (claiming the 2009-11-03 EP priority) — but the PCT filing date itself was **not** confirmed in this pass, so the date is carried as **unverified**.

### What was NOT established (the failure, stated plainly)

- The Google Patents page for JP6062995B2 was fetched successfully, but the fetched text contains **no Info / legal-status block at all**: `browser.find` for "Legal status", "Expired", "Legal Events", and "2015-04-27" on the fetched page returned zero matches. The Firecrawl scrape of the same page (scrapeId 01a1b8ad-2d03-7265-9a24-e0ad0f87f967; ~573 KB of specification text) likewise contains no status block — a text search of the scraped output for "Expired" / "Legal status" / "Anticipated expiration" found nothing.
- The EPO Global Dossier for JP2015090340 returned only its loading shell (AJAX content not retrievable).
- Web search returned no J-PlatPat or other register page for this patent.
- **Therefore: the "Expired — Fee Related" status and the lapse date are NOT verified.** The Alzheimer's brief itself already records this honestly (brief-alzheimers.md, line 47: "Independent live verification: NOT achieved on 2026-11-07").

### What it means for freedom-to-operate

- **Do not treat this patent as expired, and do not assume FTO.** Until the JPO register (J-PlatPat) is checked, we do not know whether the JP right lapsed, when it lapsed, or whether a restoration window is open.
- Even if the JP right did lapse for annuity nonpayment, the **family is the risk, not the single patent**: US8809302B2, EP2496226B1, CA2779070C and other family members must each be status-checked before any work touches the claimed combinations. A lapsed JP patent does not clear the US or EP family members.
- The Alzheimer's brief already makes a J-PlatPat check (exact lapse date, restoration window) plus a family-status sweep **gate 0** — "No work that assumes FTO may start before this." That gate stands and is reinforced by this verification.

### Still to verify (live-browser agent)

1. J-PlatPat register entry for JP6062995B2: current status, lapse date if lapsed, and whether restoration is available.
2. PCT filing date (to confirm the 2030-10-29 anticipated expiration).
3. Status of the family members US8809302B2, EP2496226B1, CA2779070C, JP5977172B2.

---

## 2. US 8,512,957 B2 — Snodgrass / Vistagen, liver toxicity typing

| Field | Value |
|---|---|
| Title | Toxicity typing using liver stem cells |
| Inventor | H. Ralph Snodgrass |
| Assignee | Vistagen Therapeutics Inc |
| Application | US13/401,623, filed 2012-02-21 |
| Priority date (Google Patents) | 2000-06-14 |
| Grant / publication | 2013-08-20 |
| Claims | 25 |
| **Verified status** | **EXPIRED — fee related (lapsed for failure to pay maintenance fees), effective 2025-08-20** |

### Verification source

Google Patents page, crawled 2026-11-08 00:57 UTC. Header legal status: "Expired — Fee Related". The USPTO-sourced Legal Events table at the foot of the page gives the complete fee history:

| Date | Event | Detail |
|---|---|---|
| 2017-02-20 | FPAY — fee payment | Year of fee payment: 4 (3.5-year maintenance fee paid) |
| 2021-02-22 | MAFP — maintenance fee payment | Payment of maintenance fee, 8th year, small entity (7.5-year fee paid) |
| 2025-04-07 | FEPP — fee payment procedure | Maintenance fee reminder mailed (11.5-year fee outstanding) |
| 2025-09-22 | LAPS — lapse for failure to pay maintenance fees | "PATENT EXPIRED FOR FAILURE TO PAY MAINTENANCE FEES" |
| 2025-09-22 | STCH — patent discontinuation | "PATENT EXPIRED DUE TO NONPAYMENT OF MAINTENANCE FEES UNDER 37 CFR 1.362" |
| 2025-10-14 | FP — lapsed due to failure to pay maintenance fee | **Effective date: 2025-08-20** |

The 11.5-year maintenance fee was due 2025-02-20 (11.5 years after the 2013-08-20 grant); the 6-month grace period ended 2025-08-20, which is the recorded effective lapse date. **This patent expired less than three months before this verification (2025-08-20).**

### Term / priority-chain question (task asked: 2001 vs 2006)

- Google's "anticipated expiration 2021-06-14" is **inconsistent with the fee record** and should not be quoted: the patent demonstrably remained in force past that date (8th-year fee paid February 2021; 11.5-year fee reminder mailed April 2025). The 2021-06-14 figure appears to be a Google miscalculation from the 2000-06-14 priority date and is not the operative expiry.
- The assignment record on the same page (effective date 2001-06-12, Snodgrass → Vistagen) supports an earliest non-provisional filing in **June 2001**, not 2006. The 2006 date is not supported by anything seen in this pass.
- The exact 20-year term-end date was not separately confirmed (Patent Center unreachable, see Method). It does not change the outcome: the patent is expired by fee lapse as of 2025-08-20 regardless of the term computation.

### What it means for freedom-to-operate

- The US claims of this patent are **not currently enforceable** — the patent expired 2025-08-20 for nonpayment. That is the best FTO news in this set, and it is recent.
- **But expired ≠ free to use:**
  - **Revival window is open.** A US patent expired for nonpayment may be reinstated on petition showing the delay was unintentional (37 CFR 1.378), generally within 2 years of the lapse — i.e. until about **August 2027** for this patent. Vistagen could still revive it. Re-check status before relying on expiry for any product or publication decision.
  - **Family / continuations were not swept.** A continuation or divisional sharing the 2000/2001 priority chain could still be pending or granted with overlapping claims. No family sweep was in scope for this verification.
  - **The specification is prior art** regardless of expiry; it does not block use, but it does block re-patenting the same method as novel.
  - The 25 claims cover LSC gene/protein-expression profiling, profile libraries, and integrated comparison systems. Any safety-screening design should be checked claim-by-claim against the expired claims only as a record of what was covered, not as live rights.

### Still to verify

1. Patent Center record for 13/401,623 (exact term-end date; confirmation no revival petition has been filed).
2. Family/continuation sweep for the Snodgrass/Vistagen chain.
3. Re-check status after August 2027 (revival window close) if the programme ever relies on this expiry.

---

## 3. US 2022/0251662 A1 — Condeelis et al., Mena splice variants

| Field | Value |
|---|---|
| Title | Metastasis specific splice variants of Mena and uses thereof in diagnosis, prognosis and treatment of tumors |
| Inventors | John S. Condeelis, Sumanta Goswami, Frank Gertler, Paola Nistico |
| Applicants / assignees | Istituti Fisioterapici Ospitalieri (IFO-Regina Elena); Albert Einstein College of Medicine; Massachusetts Institute of Technology |
| Application | US17/477,327, filed 2021-09-16 |
| Publication | US20220251662A1, published 2022-08-11 |
| Priority | US provisional 60/899,307, filed 2007-02-02; PCT/US2008/001343 (WO2008097466A2), filed 2008-01-31 |
| **Verified status** | **ABANDONED — application, never granted. Abandoned 2024-09-10 for failure to respond to an office action** |

### Verification source

Google Patents page, crawled 2026-11-08 00:59 UTC. Header legal status: "Abandoned". Legal Events table: 2024-09-10 STCB, "ABANDONED — FAILURE TO RESPOND TO AN OFFICE ACTION". The application never issued as a patent; **US 2022/0251662 A1 is a publication, not a granted patent, and it confers no rights.**

### Family verification (task asked to confirm US 9,719,142 and US 8,603,738)

**Confirmed — both exist, both are family members, both are ACTIVE.** Google Patents family ID 39682291, "Family Applications (4)":

| Application | Publication | Status (Google Patents, 2026-11-08) |
|---|---|---|
| US12/462,324, filed 2009-07-31 | **US8603738B2**, granted 2013-12-10 | **Active, expires 2030-01-28** (adjusted expiration) |
| US14/074,089, filed 2013-11-07 | **US9719142B2**, granted 2017-08-01 | **Active, expires 2028-07-27** (adjusted expiration) |
| US15/661,021, filed 2017-07-27 | US20170335406A1 | Abandoned (checked directly — same title/inventors) |
| US17/477,327, filed 2021-09-16 | US20220251662A1 | Abandoned 2024-09-10 |

Both granted patents carry the identical title, the same four inventors, the same assignees, and the same 2007-02-02 priority date; each lists the 2021-09-16 priority claim to US17/477,327 (i.e. the abandoned application was their continuation). The chain as stated on the application's own front page (quoted in brief-cancer-dao.md §7): continuation of 17/248,146 (filed 2021-01-11, abandoned) → continuation of 15/661,021 (abandoned) → division of 14/074,089 (now US 9,719,142) → division of 12/462,324 (now US 8,603,738) → continuation-in-part of PCT/US2008/001343 → provisional 60/899,303, filed 2007-02-02. The individual status of parent application 17/248,146 was not separately opened (its publication number was not located in this pass) — it is stated as abandoned on the front-page chain.

Foreign family (Google Patents country status): EP2126566B1 **not-in-force**; CA2676179C **expired — fee related**; DK2126566T3 active; ES2627011T3 active; WO2008097466A2 ceased.

### What it means for freedom-to-operate

- **The 2022 publication itself is no obstacle** — an abandoned application grants nothing. But that is the least important fact in this family.
- **The family is live.** US8603738B2 (to 2030-01-28) and US9719142B2 (to 2028-07-27) are granted, active US patents on the same Mena ++/+++ isoform invention. **Any Mena-based diagnostic, prognostic, or therapeutic work must be cleared against the claims of those two patents.** The Cancer DAO brief already states this correctly (§7: "the Mena-isoform invention has granted US patent protection through the two B2 patents… but the 2022 continuation… did not itself grant").
- **Revival is possible in principle.** The abandoned 17/477,327 application could be revived by petition (unintentional delay); if revived it could also spawn further continuations while pending. A revival check belongs in any pre-launch clearance.
- The granted patents' claim scope was **not** verified in this pass (neither here nor in the brief) — do not quote their claims. A claim-scope read of US8603738B2 and US9719142B2 is a defined follow-up before any Mena assay or product work.

### Still to verify

1. Claim scope of US8603738B2 and US9719142B2 (read the granted claims).
2. Status of parent application 17/248,146 (stated abandoned; not separately opened).
3. Whether any continuation of this family is currently pending.
4. Re-check the abandoned application's revival status before relying on the abandonment.

---

## 4. US 8,918,278 B2 — Feldman / INRIX, vehicular traffic modeling

| Field | Value |
|---|---|
| Title | Method and system for modeling and processing vehicular traffic data and information and applying thereof |
| Inventors | Israel Feldman, Arie Trinker, Yochai Meltzer, Allon Eshpar, Amnon Lotem |
| Assignee | INRIX Global Services Ltd (now INRIX UK Ltd) |
| Application | US11/269,908, filed 2005-11-08 |
| Priority | US provisional 60/227,905, filed 2000-08-28 |
| Grant / publication | 2014-12-23 |
| Claims | 46 |
| **Verified status** | **EXPIRED — LIFETIME, per Google Patents (anticipated expiration 2021-08-28) — BUT with a conflicting USPTO fee record; exact expiry date / PTA NOT verified. Treat as expired for planning; confirm in Patent Center before relying on it.** |

### Verification source

Google Patents page, crawled 2026-11-08 00:59 UTC. Header legal status: "Expired — Lifetime". Timeline: "2021-08-28 Anticipated expiration".

### Correction to the brief's premise

The task brief (and MEMORY.md) stated the term as "20-year term from Nov 2005 filing → ~Nov 8 2025 (PTA 0 days)". **That is wrong.** Espacenet (family 026921868) confirms the priority chain:

- US provisional 60/227,905 — 2000-08-28
- **US non-provisional 09/939,620 — 2001-08-28**
- US 10/461,478 — 2003-06-16
- US 10/999,994 — 2004-12-01
- US 11/269,908 — 2005-11-08 (the application that issued as US8918278B2)

Under 35 U.S.C. §154(a)(2) the 20-year term runs from the **earliest US non-provisional filing date in the chain — 2001-08-28** — not from the 2005 filing. Base term end: **2021-08-28**, plus any patent term adjustment (PTA). The November 2025 date in the brief must not be used.

### Corroboration that the family is expired by lifetime

The latest family continuation, **US10984652B2** (application US16/182,178, filed 2018-11-06, granted 2021-04-20), was checked directly on Google Patents (crawled 2026-11-08 01:02 UTC): **"Expired — Lifetime, expires 2022-07-03"**, "2022-07-03 Adjusted expiration". That is the same 2001-08-28 base date plus 309 days of PTA — confirming the family's term base and that the family is expired by lifetime. Other family members on Espacenet: US6587781B2, US6879907B2, US9324232B2, US9552725B2, US10121366B2, US10984652B2.

### The conflict — recorded, not resolved

The USPTO-sourced Legal Events table on the same Google Patents page shows:

| Date | Event | Detail |
|---|---|---|
| 2018-06-06 | MAFP — maintenance fee payment | 4th-year fee, small entity |
| 2022-04-05 | MAFP — maintenance fee payment | **8th-year fee, small entity** |
| 2023-06-28 | AS — assignment | Release by secured party (Runway Growth Finance Corp. → INRIX UK Ltd.) |
| 2026-08-10 | FEPP — fee payment procedure | **Maintenance fee reminder mailed** (11.5-year fee) |

If the patent expired 2021-08-28, the 8th-year fee (due window Dec 2021 – Jun 2022) should not have been payable, and no fee reminder should have issued in August 2026. Two explanations are possible and **cannot be distinguished from the sources reached**:

- **(a)** The patent's actual PTA is substantial (the application spent 9 years in prosecution, 2005–2014; B-delay alone could be large), pushing the real expiry past April 2022 — in which case Google's "anticipated expiration 2021-08-28" (implying PTA 0) is wrong. Note the sibling's 309-day PTA shows PTA in this family is non-zero.
- **(b)** The USPTO maintenance-fee system processes payments and mails reminders from the grant date without checking term expiry, so the 2022 payment and 2026 reminder are artifacts of an expired patent.

The 11.5-year fee (due 2026-06-23, grace to 2026-12-23) appears unpaid per the August 2026 reminder — so **if** the patent were somehow still alive, it would lapse 2026-12-23 for nonpayment. Either way, the patent is not safely treatable as in force — but the exact expiry date is unresolved.

### Attempts to resolve (all failed — needs live-browser agent)

- USPTO Patent Center (application 11/269,908) via Firecrawl: **HTTP 403 Forbidden**, loading shell only. Patent Center shows the authoritative PTA and adjusted expiration date.
- EPO Global Dossier (US26990805) via Firecrawl: AJAX loading shell only, no dossier content.
- Lens.org: **HTTP 403, access denied**; not retried.
- No "154(b)" / PTA statement appears in the Google Patents page text for this patent.

### What it means for freedom-to-operate

- **Planning position: expired.** The preponderance (Google header status + sibling continuation expired 2022-07-03 on an adjusted date) says this patent's term has run. Traffic-modeling work built on the Feldman method (oriented road sections, NTT per section, fusing partial pictures, future-picture prediction) is on the expired side of the line.
- **Do not rely on it yet.** Before any product, publication, or investment decision assumes FTO, a live-browser Patent Center check must confirm (i) the PTA for 11/269,908, (ii) the adjusted expiration date, and (iii) that no revival/reinstatement event exists. If the true PTA were large, the patent could theoretically still be alive until the 11.5-year fee lapse on 2026-12-23 — a matter of weeks from this verification date.
- **Family check is still required.** The sibling continuations (US6587781B2, US6879907B2, US9324232B2, US9552725B2, US10121366B2) were not individually status-checked in this pass; the latest (US10984652B2) is expired, but the others should be confirmed in the same Patent Center pass, since a live sibling with overlapping claims would still block use.
- Assignment note: the patent was assigned to INRIX UK Ltd. (2019), was under a security interest to Runway Growth Credit Fund (2019–2023, released 2023-06-28). Ownership history is clean for FTO purposes; it does not affect expiry.

### Still to verify (live-browser agent — Patent Center, application 11/269,908)

1. Patent term adjustment (PTA) days and adjusted expiration date.
2. Whether a terminal disclaimer applies.
3. Confirmation of current status (expired — lifetime) and of no pending revival/reinstatement.
4. Status of sibling continuations US10121366B2, US9552725B2, US9324232B2, US6879907B2, US6587781B2.

---

## The expired ≠ free to use rule (applies to all four patents)

1. **A database status label is not a legal conclusion.** Google Patents says so on every page; Espacenet/INPADOC labels are the same. Only the issuing office's register (USPTO Patent Center / PAIR, JPO J-PlatPat) is authoritative, and only counsel's opinion is clearance.
2. **Expired for nonpayment can come back.** In the US, reinstatement on petition for unintentional delay (37 CFR 1.378) is generally available for 2 years after lapse (US8512957B2: until ~August 2027). In Japan, lapsed patents can in some circumstances be restored. Always re-check before relying on a lapse.
3. **The family is the unit of risk, not the single publication.** A lapsed or abandoned member does not clear its parents, children, divisionals, continuations, or foreign counterparts. In this set the Mena family proves the point: the abandoned 2022 publication sits between two active granted patents (to 2028 and 2030).
4. **Term is computed from the earliest non-provisional filing, not the filing date of the application in hand.** The Feldman patent shows why: the brief's November 2025 date was four years late because the chain reaches back to 2001. Always walk the priority chain.
5. **Maintenance-fee history is evidence, not proof of term.** The Feldman fee record (payment in 2022, reminder in 2026) conflicts with the term record (expiry 2021). Fee events and term must be reconciled in the office register before any reliance.
6. **An expired patent's specification is prior art.** Expiry frees practice of its claims (once confirmed), but the disclosure itself blocks later patenting of the same thing as novel.

---

## Summary table

| Patent | Verified status (2026-11-07) | Key dates | Confidence |
|---|---|---|---|
| JP6062995B2 (Pharnext, Alzheimer's) | **Could not verify — needs live-browser agent (J-PlatPat)**. Brief says "Expired — Fee Related", anticipated expiry 2030-10-29; neither confirmed. | Filed 2015-04-27; granted 2017-01-18 | Low — register not reached |
| US8512957B2 (Snodgrass, liver toxicity) | **Expired — fee related, effective 2025-08-20** (11.5-yr fee unpaid) | Filed 2012-02-21; granted 2013-08-20; lapsed 2025-08-20 | High — USPTO legal events |
| US20220251662A1 (Mena) | **Abandoned 2024-09-10** (failure to respond to office action); never granted. Family patents US8603738B2 (active to 2030-01-28) and US9719142B2 (active to 2028-07-27) **confirmed** | Filed 2021-09-16; published 2022-08-11; abandoned 2024-09-10 | High — USPTO legal events + family table |
| US8918278B2 (Feldman, traffic) | **Expired — lifetime per Google Patents, anticipated 2021-08-28; exact date/PTA NOT verified; conflicting fee record** | Filed 2005-11-08; granted 2014-12-23; term base 2001-08-28 | Medium — header + sibling corroboration, but fee record conflicts |

## Verification log (attempts)

| # | Check | Result |
|---|---|---|
| 1 | Google Patents JP6062995B2 (browser.open) | Page fetched; **no status block in text** |
| 2 | Google Patents US8512957B2 (browser.open) | Expired — Fee Related; full legal events incl. lapse eff. 2025-08-20 |
| 3 | Google Patents US20220251662A1 (browser.open) | Abandoned; abandonment event 2024-09-10; family table |
| 4 | Google Patents US8918278B2 (browser.open) | Expired — Lifetime, anticipated 2021-08-28; fee events conflict |
| 5 | Google Patents US9719142B2 (browser.open) | Active, expires 2028-07-27 |
| 6 | Google Patents US8603738B2 (browser.open) | Active, expires 2030-01-28 |
| 7 | Google Patents US20170335406A1 (browser.open) | Abandoned (Mena family) |
| 8 | Google Patents US10984652B2 (browser.open) | Expired — Lifetime, adjusted expiration 2022-07-03 (Feldman sibling) |
| 9 | Firecrawl: Google Patents JP6062995B2 | Spec text only; no status block |
| 10 | Firecrawl: Espacenet US8918278B2 | Priority chain incl. 09/939,620 (2001-08-28); family list |
| 11 | Firecrawl: Espacenet JP6062995B2 | Priority EP 2009-11-03; JP app/grant dates; family list |
| 12 | Firecrawl: Patent Center 11/269,908 | **HTTP 403 Forbidden** |
| 13 | Firecrawl: Global Dossier JP2015090340 | AJAX shell only |
| 14 | Firecrawl: Global Dossier US26990805 | AJAX shell only |
| 15 | Lens.org JP6062995B2 / US8918278B2 (browser.open) | **HTTP 403, access denied** |
| 16 | Web search JP6062995B2 status | No register page found |

## Open items for the live-browser agent

1. **J-PlatPat** — JP6062995B2 status, lapse date, restoration window; PCT filing date; family-member status sweep.
2. **USPTO Patent Center** — US8918278B2 (application 11/269,908): PTA, adjusted expiration, terminal disclaimer, current status; sibling continuations US10121366B2, US9552725B2, US9324232B2, US6879907B2, US6587781B2.
3. **USPTO Patent Center** — US8512957B2 (application 13/401,623): confirm term-end date and that no revival petition has been filed; family/continuation sweep.
4. **USPTO Patent Center** — Mena family: claim scope of US8603738B2 and US9719142B2; status of parent application 17/248,146; any pending continuation.

*This file is a staging verification record. It is not legal advice. Freedom-to-operate decisions require a written opinion from patent counsel on the office registers.*
