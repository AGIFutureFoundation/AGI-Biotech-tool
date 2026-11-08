# Compound Entry — DacomiLertib (BCL-XL inhibitor, cancer — HYPOTHETICAL / UNVERIFIED)

**Staging only — local compound-library validation entry. Do NOT publish, push, deploy, email, or share.**
**Validation date: 7 November 2026. Primary source: `~/workspace/user/files/DacomiLertib_effectively_binds_to_BCL-XL__thereby_promoting_apoptosis.pdf` — a ChatGPT conversation export (macOS Notes export, created 2026-08-22, 182 pages, 748,384 B).**
**Status: HYPOTHETICAL / UNVERIFIED candidate entry. Not a stocked compound, not a priced job, not a library holding, not a measured result.**

## Honesty lines (read first — they govern every field)

- **SIMULATED / PREDICTED / DOCUMENT-CLAIMED ONLY — absolute rule.** Every number attached to DacomiLertib in the source is a ChatGPT simulation or QSAR prediction. There are **zero citations, zero references, zero PMID/DOI mentions, and zero experiments** anywhere in the 182-page document (verified by text search: 0 matches for "PMID", "doi.org", "et al.", "references", "citation"). **Never present any DacomiLertib number as a measured result.** Label every value "document-claimed (simulated/predicted)" in every sentence that states it.
- **No treatment, cure, diagnosis, or medical-device claims anywhere.** DacomiLertib is a hypothetical compound in a chat export. Nothing here claims it treats, cures, or diagnoses cancer or any disease. The ALS Researcher / Cancer DAO "not a medical device" line applies to every compound output.
- **No valid full-structure SMILES exists in the document for the claimed 645.63 Da compound.** The one full-length SMILES given is INVALID as written, and even after stripping its tag artifacts it recomputes to MW 503.58 — not 645.63. **Do NOT reconstruct a structure.** If a future pass needs a structure, it must be drawn de novo and labelled as a new proposal, never presented as "the document's structure".
- **Do NOT merge this entry with AGI-183 (either of its two entries) or with AGI-010.** Same target family, different compounds, different directions of effect — see §8.

---

## 1. Identity (per the source document only)

| Field | Value | Source / note |
|---|---|---|
| Name | **DacomiLertib** (spelled "DacomiLertib" throughout the document) | Source PDF, title + entry headers |
| Class (per document) | **BCL-XL inhibitor**, purine-core, claimed to promote apoptosis in cancer cells | Source PDF, entry #201 header + §1 |
| Proposed indication area | Cancer (apoptosis promotion) — research hypothesis only, **not a treatment** | Source PDF |
| Target | BCL-XL, in the context of a document-claimed **V132F mutation** | See §10 — V132F is document-claimed only |
| Claimed key residues | **Asp 84, Lys 123, Leu 120, Ile 80, Phe 116** | Document-claimed binding residues; no structure or assay supports them |
| Claimed co-target / pathway | **"ML-1"** (likely MCL-1 — **unconfirmed**, see §10) "to prevent ANT/DPX release" | "DPX" is unresolved — see §10 |
| Claimed kinase profile | **"No Kinase Binding"** | Document claim only; no data |
| SMILES | **No valid full-structure SMILES** — see §3/§4 | 1 Modified + 15 Enhanced variants, all INVALID as written |
| Molecular weight | **Not established.** Document claims 645.63 g/mol; no given SMILES recomputes to it | See §5 |
| LogP | **Not established.** Document claims 4.7; no given SMILES is attributable as its source | See §5 |
| ΔG / IC50 / goodness | **Document-claimed simulations only** — ΔG −9.7 kcal/mol; predicted IC50 0.39 µM (390 nM); goodness 0.89; activity ratio 1.4; BCL-XL vs BCL-2 selectivity 1.28 | See §6 |
| Source / synthesis / supplier | **None given** | Do not invent |
| Regulatory status | None. Not approved, not in a trial, no IND. Not a known drug | See §10 name collision with dacomitinib |
| Provenance label | **HYPOTHETICAL / UNVERIFIED — "ChatGPT simulation, no experimental data"** | See §2 |

---

## 2. Document structure and repetition count (verified by text extraction, 2026-11-07)

The source is a 182-page ChatGPT conversation export, not a paper. It is a long numbered compound list built up through repeated "continue" prompts. What was actually found:

- **Entry #201 "DacomiLertib-BCL-XL Pathways + ML-1 + V132F (Asp 84, Lys 123, Leu 120, Ile 80, Phe 116, No Kinase Binding)" appears 13 times** (text-layer lines 14, 142, 265, 385, 511, 624, 733, 844, 956, 1066, 1176, 1285, 2907) — **not ~8 as briefed; the actual count is 13**. Content is near-identical across repetitions, with the Enhanced-SMILES list growing each time the conversation continued.
- **Entry #202 "DacomiLertib-BCL-XL Pathways + ML-1 + Y108F (…)" also appears 13 times** (lines 3092–4267) — a **sibling variant of the same hypothetical compound in a Y108F mutation context**. It is NOT part of this entry; it is recorded here only so a future pass does not mistake its variants for #201's. The consolidated summary sections at the end of the document (Enhanced SMILES numbered up to 248, with ΔG −10.3 kcal/mol and selectivity 2.68–3.04) belong to the **#202 / Y108F family**, not to #201 — and they contradict #201's own claimed ΔG −9.7 / selectivity 1.28 (internal inconsistency, §5).
- **Enhanced-variant growth inside entry #201:** repetitions 1–4 carry Enhanced SMILES 1–5; repetitions 5–12 carry 1–10; repetition 13 carries **1–15**. Distinct V132F-tagged Enhanced variants in the whole document: **exactly 15 (numbered 1–15)**. Variants numbered 16–248 are Y108F-tagged (#202 family) and are out of scope for this entry.
- **Claimed-value repetition:** the strings "Molecular Weight: 645.63" and "LogP: 4.7" each occur **70 times** in the full text (across both entries and the summary sections); "Molecular Weight:" occurs 154 times overall. The same single MW/LogP pair is pasted identically against every variant — see §5 for why that is itself a red flag.
- **Fragment SMILES** ("Purine Ring", "Linker", "Phenyl Ring", "Substituent") are repeated in every #201 block but are **never assembled into one molecule** in the document.

---

## 3. Every SMILES string the document gives (verbatim as written — all INVALID as written except the fragments)

### 3a. Fragment SMILES (these three DO parse — they are fragments, not the compound)

| Fragment | SMILES as written | RDKit result |
|---|---|---|
| Purine Ring / Purine Core Region | `C1=NC2=C(N1)N=CN=C2` | Parses. Canonical `c1ncc2nc[nH]c2n1`, formula C5H4N4, **MW 120.11**, LogP (Crippen) 0.35 |
| Linker Region | `C=CC=CO` | Parses. C4H6O, MW 70.09, LogP 1.24 |
| Phenyl Ring Region | `C1=CC=CC=C1` | Parses. C6H6, MW 78.11, LogP 1.69 |
| Substituent Region | `Cl or OH` (later repetitions: "Multiple substituent groups explored, including Cl, OH, CF3, NO2, N=O, N=N+, and others") | Not a SMILES — a word list |

### 3b. Modified SMILES (one per #201 repetition, identical every time)

As written (line-break in the PDF text layer rejoined; the string is continuous in the document):

```
CN1CC2=CC=CC=C2N(C1)C(=O)NC3=CC=C(C=C3)N=C(S1)N(C1=O)C(CO)C4=CC=COC=C4-[BCL-XL-ML1-V132F]
```

**INVALID as written** — RDKit 2026.09.1: `SMILES Parse Error: syntax error … check for mistakes around position 74: C(CO)C4=CC=COC=C4-[BCL-XL-ML1-V132F]`. Reason: the appended bracketed tag `-[BCL-XL-ML1-V132F]` is a protein/mutation label, not SMILES syntax. (The PDF text layer also splits it across lines as `C(C` / `O)` and inserts spaces inside the Enhanced variants — both are additional artifacts.)

### 3c. Enhanced SMILES 1–15 (V132F family; common prefix + variable tail)

Common prefix (identical in all 15):

```
CN1CC2=CC=CC=C2N(C1)C(=O)NC3=CC=C(C=C3)N=C(S1)N(C1=O)C(CO)C4=CC=COC=C4
```

Variable tails, as written (tag after the `-` is the document's residue label, not chemistry):

| # | Tail as written | Tag as written |
|---|---|---|
| 1 | `C=CC=CN-` | `[BCL-XL-ML1-V132F-Asp84-Lys123-Leu120]` |
| 2 | `OCC=CC=[O]-` | `[BCL-XL-ML1-V132F-Ile80-Phe116]` |
| 3 | `C=CC=CCl-` | `[BCL-XL-ML1-V132F-Lys123-Phe116]` |
| 4 | `C=CN=CC=[O]-` | `[BCL-XL-ML1-V132F-Asp84-Lys123-Leu120]` |
| 5 | `C=CCN=CC=[N]-` | `[BCL-XL-ML1-V132F-Ile80-Phe116]` |
| 6 | `C=CC(CF3)C-` | `[BCL-XL-ML1-V132F-Phe116]` |
| 7 | `N=CC=CN-` | `[BCL-XL-ML1-V132F-Lys123]` |
| 8 | `C=CC=CNCl-` | `[BCL-XL-ML1-V132F-Asp84-Lys123-Leu120]` |
| 9 | `OCC=CC(Cl)=O-` | `[BCL-XL-ML1-V132F-Leu120-Phe116]` |
| 10 | `N=CC=COCF3-` | `[BCL-XL-ML1-V132F-Asp84-Lys123-Leu120]` |
| 11 | `C(CH3)N=[O]-` | `[BCL-XL-ML1-V132F-Phe116-Asp84]` |
| 12 | `C(CN)N=[N+](O-)-` | `[BCL-XL-ML1-V132F-Lys123-Leu120]` |
| 13 | `C(Cl)C=[O]-` | `[BCL-XL-ML1-V132F-Phe116-Ile80]` |
| 14 | `N=CC(N)NCl-` | `[BCL-XL-ML1-V132F-Leu120-Asp84]` |
| 15 | `C(CF3)C=[O]-` | `[BCL-XL-ML1-V132F-Lys123-Phe116]` |

**All 16 full-length strings (1 Modified + 15 Enhanced) are INVALID as written** — every one carries an appended `-[BCL-XL-…]` tag, and most carry embedded spaces from the PDF text layer. Tag formatting also varies between repetitions (e.g. `Asp84Lys123Leu120` vs `Asp84-Lys123-Leu120`), a text-layer hyphenation artifact, not a chemical difference.

---

## 4. RDKit validation (RDKit 2026.09.1, run 2026-11-07)

Method: each string parsed as written; then re-parsed after stripping ONLY the tag artifacts (bracketed `-[…]` labels and spaces/newlines) to test whether any valid core remains. Stripping is a diagnostic only — the stripped strings are **not** the document's structures and must not be quoted as "DacomiLertib's SMILES".

### 4a. Base purine SMILES — parses, and refutes the claimed MW/LogP

- `C1=NC2=C(N1)N=CN=C2` → canonical `c1ncc2nc[nH]c2n1`, C5H4N4, **MW 120.11** (exact 120.04), **LogP (Crippen) 0.35**.
- The document's claimed MW 645.63 / LogP 4.7 **cannot possibly describe this SMILES**: a bare purine ring is ~120 Da, ~5.4× lighter than claimed, and far more polar than LogP 4.7. The purine SMILES is a fragment, not the compound.

### 4b. Modified SMILES — INVALID as written; stripped core parses but does NOT match the claimed MW

- As written: **PARSE FAIL** (see §3b).
- Stripped core `CN1CC2=CC=CC=C2N(C1)C(=O)NC3=CC=C(C=C3)N=C(S1)N(C1=O)C(CO)C4=CC=COC=C4` → **parses**. Canonical: `CN1Cc2ccccc2N(C(=O)Nc2ccc(N=C3SC(=O)N3C(CO)C3=CC=COC=C3)cc2)C1`. Formula **C26H25N5O4S, MW 503.58** (exact 503.16), **LogP (Crippen) 4.63**, 36 atoms.
- **The stripped core contains NO purine ring** (RDKit substructure match for the purine fragment: 0 matches). The document's "purine core" claim is not present in its own full-length structure — the core is a thiazolidinone-like scaffold with a phenyl, a pyran-like ring and a hydroxymethyl group. The purine SMILES and the Modified SMILES describe different things; the document never reconciles them.
- The stripped core's LogP 4.63 is close to the claimed 4.7, but its MW 503.58 is **142.05 Da short** of the claimed 645.63. LogP proximity without MW agreement does not validate the claim.

### 4c. Enhanced SMILES 1–15, tag-stripped — 10 of 15 parse, 5 fail even after stripping

| # | Stripped core parses? | Recomputed MW | Recomputed LogP (Crippen) | Formula |
|---|---|---|---|---|
| 1 | OK | 570.68 | 5.03 | C30H30N6O4S |
| 2 | OK | 587.66 | 4.73 | C30H29N5O6S |
| 3 | OK | 590.11 | 6.31 | C30H28ClN5O4S |
| 4 | OK | 584.66 | 4.78 | C30H28N6O5S |
| 5 | OK | 596.69 | 4.50 | C31H30N7O4S |
| 6 | **FAIL** — "unclosed ring" | — | — | — |
| 7 | OK | 571.66 | 4.50 | C29H29N7O4S |
| 8 | OK | 605.12 | 5.81 | C30H29ClN6O4S |
| 9 | OK | 622.10 | 5.30 | C30H28ClN5O6S |
| 10 | **FAIL** — "unclosed ring" | — | — | — |
| 11 | **FAIL** — "syntax error / extra open parentheses" | — | — | — |
| 12 | **FAIL** — "syntax error / extra open parentheses" | — | — | — |
| 13 | OK | 580.07 | 4.81 | C28H26ClN5O5S |
| 14 | OK | 609.11 | 4.06 | C28H29ClN8O4S |
| 15 | **FAIL** — "unclosed ring" | — | — | — |

Failure reasons (verified against minimal fragments):
- **#6, #10, #15 — "unclosed ring":** each tail contains `CF3`. In SMILES, a bare digit is a ring-closure digit, so `CF3` opens ring 3 and never closes it. Valid trifluoromethyl notation is `C(F)(F)F` (verified: `CCC(F)(F)F` parses, `CCCF3` fails). The document writes CF3 as if it were a formula, not a SMILES token.
- **#11 — "syntax error / extra open parentheses":** tail contains `C(CH3)`. Same digit problem: `CH3` opens ring 3 and never closes it (verified: `CC(CH3)N` fails). The terminal `N=[O]` fragment alone parses, so the CH3 digit is the breaking defect.
- **#12 — "syntax error / extra open parentheses":** tail `C(CN)N=[N+](O-)` fails even as a standalone fragment (`CC(CN)N=[N+](O-)` → FAIL), while the correctly written nitro control `CC[N+](=O)[O-]` parses. The `N=[N+](O-)` grouping as written is not valid SMILES.

**Invalid-SMILES tally: 16 of 16 full-length strings INVALID as written (1 Modified + 15 Enhanced). After tag-stripping only, 11 of 16 yield a parseable core (Modified + Enhanced 1–5, 7–9, 13–14) and 5 remain invalid (Enhanced 6, 10, 11, 12, 15).**

---

## 5. Claimed MW / LogP vs recomputed values — the claimed numbers match NOTHING in the document

| Claimed (document, repeated identically in all 13 repetitions) | Recomputed (RDKit) | Verdict |
|---|---|---|
| MW 645.63 g/mol | Purine fragment 120.11; stripped Modified core 503.58; Enhanced variants 570.68–622.10 (closest: #9 at 622.10, still 23.53 Da short) | **Matches no structure the document gives.** No valid full-structure SMILES for a 645.63 Da compound exists in the document. |
| LogP 4.7 | Purine 0.35; stripped Modified core 4.63; Enhanced variants 4.06–6.31 (closest: #2 at 4.73) | Close to several structures by coincidence, but LogP alone cannot identify a compound, and the MW mismatch rules out attribution to any of them. |
| One MW/LogP pair for 16 different structures | 16 different strings recompute to 11 different MWs (503.58–622.10) | **Internally inconsistent.** A single MW/LogP pair cannot describe 16 distinct structures. The numbers were pasted, not computed per structure. |

**What the document does establish:** a purine fragment (MW 120.11), a linker, a phenyl ring, and a set of tag-corrupted candidate strings whose parseable cores are 503–622 Da.
**What it does NOT establish:** any structure with MW 645.63 / LogP 4.7; any link between the claimed numbers and any given SMILES; any measured property of any real molecule. **Do NOT present 645.63 / 4.7 as properties of a structure.**

Additional internal inconsistency (for the merge worker): the document's own end-of-document summary gives **different** claimed values for the consolidated variants — ΔG −10.3 kcal/mol (vs −9.7 in entry #201) and BCL-XL vs BCL-2 selectivity **2.68–3.04** (vs 1.28 in entry #201) — with no explanation. The document disagrees with itself.

---

## 6. Document-claimed values (ALL simulated / predicted / document-claimed — never measured)

| Value | Document claim | Status |
|---|---|---|
| ΔG (binding free energy) | −9.7 kcal/mol | Simulated, document-claimed |
| Predicted IC50 | 0.39 µM (390 nM) — labelled "QSAR Modeling: Predicted IC50" and "Simulated IC50" | Predicted, document-claimed |
| Molecular Goodness Score | 0.89 | Simulated, document-claimed (scoring method undefined in the document) |
| Activity ratio (targeted vs non-targeted) | 1.4 | Simulated, document-claimed |
| Selectivity ratio (BCL-XL vs BCL-2) | 1.28 | Simulated, document-claimed (contradicted by the document's own summary: 2.68–3.04, §5) |
| Key residues | Asp 84, Lys 123, Leu 120, Ile 80, Phe 116 (+ V132F context) | Document-claimed; no structure, docking output, or assay in the document |
| "No Kinase Binding" | Claimed as a property of the entry | Document claim only; no selectivity panel or data |
| Mechanism narrative | BCL-XL inhibition releases BAX/BAK → MOMP → cytochrome c release → caspase activation → apoptosis | Standard textbook BCL-XL biology as narrated by the chat export, not a finding about this compound |

---

## 7. Comparison against the catalog's existing BCL-XL entries

| Entry | Target / direction | Numbers (provenance) | Standing |
|---|---|---|---|
| **AGI-010** (catalog) | Bcl-xL, CF3-bearing, inhibitor (cancer) | IC50 0.3, goodness 0.91 — **strongest on paper** in the catalog | Catalog-claimed; per coordinator brief |
| **DacomiLertib** (this entry) | BCL-XL inhibitor (cancer, promote apoptosis) | Predicted IC50 0.39 µM, goodness 0.89, selectivity 1.28 — **weaker on paper than AGI-010** on both IC50 and goodness | HYPOTHETICAL / UNVERIFIED — ChatGPT simulation, no data |
| **AGI-183 — paper** (`compound-agi183.md` §§1–4) | **BCL-XL stabilizer** (ALS neuroprotection, prevent apoptosis) | No SMILES, no MW, no IC50 for AGI-183 itself; combination-model predictions only | Candidate entry; paper-grounded, predictions labelled |
| **AGI-183 — catalog** (`compound-agi183.md` §5) | **CRBN-binding FLIP inhibitor** (cancer, pro-apoptotic) | Catalog-claimed SMILES, MW 353.32, LogP 4.1, ΔG −8.6, IC50 0.5 µM, goodness 0.82 | Unresolved identity tension with the paper's AGI-183 — DO NOT MERGE |

On paper only (all numbers document-claimed, none measured): AGI-010 (IC50 0.3, goodness 0.91) > DacomiLertib (0.39, 0.89) > catalog AGI-183 (0.5, 0.82). This ranking compares **three different provenances** (catalog claim vs chat simulation vs catalog claim) and must never be presented as a measured potency ranking.

---

## 8. THE KEY SCIENTIFIC TENSION — recorded here for merge into `brief-cancer-dao.md` and the BCL-2 program briefs

**BCL-XL INHIBITION (DacomiLertib — cancer, promote apoptosis) vs BCL-XL STABILIZATION (AGI-183, ALS paper — prevent apoptosis). Same target, opposite directions of effect, per disease.**

- **DacomiLertib direction:** inhibit BCL-XL → release BAX/BAK → MOMP → apoptosis. Desired in cancer (kill the cell).
- **AGI-183 (paper) direction:** stabilize BCL-XL → keep BAX sequestered / retrotranslocated → prevent MOMP → survival. Desired in ALS motor neurons (save the cell).
- Both cannot be the program's single "BCL-XL strategy". Any brief, library page, or DAO document that mentions BCL-XL must state the direction **per compound and per disease** — never "BCL-XL therapy" unqualified.
- **Compounding tension:** the catalog's AGI-183 is itself a *third* direction (CRBN/FLIP, pro-apoptotic, cancer) sharing the paper AGI-183's name. Until Mike resolves the AGI-183 identity tension in writing, the library carries **two compounds named AGI-183 with opposite mechanisms plus DacomiLertib as a third BCL-XL actor**. Do not let a merge collapse these into one row.
- **Wording contradiction inside the DacomiLertib document itself:** the entry claims the compound *inhibits* BCL-XL to *promote* apoptosis, yet describes the key-residue interactions as "critical for **preventing ANT/DPX release**". Preventing release from mitochondria is what BCL-XL *normally does* (anti-apoptotic); an inhibitor would *permit* release. The document's phrasing conflates the target's normal function with the inhibitor's effect. Flag for the merge worker: do not carry "preventing ANT/DPX release" into any brief as a mechanism statement for an inhibitor.

### Safety note — on-target thrombocytopenia (VERIFIED in this pass)

BCL-XL inhibition carries a **known on-target toxicity: thrombocytopenia**. Platelets depend on BCL-XL for survival; inhibiting it shortens platelet lifespan and drops platelet counts, and this was the dose-limiting toxicity for navitoclax (ABT-263) — verified 2026-11-07 via web search (Wikipedia, "Navitoclax": "Because navitoclax inhibits Bcl-xL, it reduces platelet lifespan, causing thrombocytopenia, and this makes it dose-limiting"; consistent with `compound-agi183.md` §4, which cites PMC9257998 for the same point). **Implication for any DacomiLertib program:** the document's claim of "minimizing off-target effects" is unsubstantiated, and the *on-target* platelet liability is the primary safety design constraint for any BCL-XL inhibitor — it cannot be waved away by a selectivity ratio. No platelet, animal, or human data exists for DacomiLertib; the navitoclax precedent is a class warning, not a finding about this compound.

---

## 9. Validated-library table entry (for the full-library validation worker to fold in)

| Library field | Value |
|---|---|
| Name | DacomiLertib |
| Entry # in source | 201 (V132F context) |
| Target | BCL-XL (inhibitor, cancer) |
| Provenance label | **HYPOTHETICAL / UNVERIFIED** |
| Provenance | ChatGPT simulation, no experimental data (source: ChatGPT conversation export, 182 pp., zero citations) |
| SMILES (as written) | INVALID — 16/16 full-length strings invalid as written (1 Modified + 15 Enhanced) |
| SMILES (tag-stripped, diagnostic only) | 11/16 parseable cores; 5 fail even stripped (Enhanced 6, 10, 11, 12, 15) |
| MW (document-claimed) | 645.63 g/mol — **matches no recomputed structure** |
| MW (RDKit recomputed) | Purine fragment 120.11; stripped Modified core 503.58; Enhanced cores 570.68–622.10 |
| LogP (document-claimed) | 4.7 — unattributable to any given SMILES |
| LogP (RDKit recomputed) | Purine 0.35; stripped Modified core 4.63; Enhanced cores 4.06–6.31 |
| Predicted IC50 (document-claimed) | 0.39 µM (390 nM) — simulated, not measured |
| ΔG (document-claimed) | −9.7 kcal/mol — simulated, not measured |
| Goodness (document-claimed) | 0.89 — simulated, method undefined |
| Selectivity BCL-XL vs BCL-2 (document-claimed) | 1.28 — contradicted by the document's own summary (2.68–3.04) |
| Key residues (document-claimed) | Asp 84, Lys 123, Leu 120, Ile 80, Phe 116 |
| Status | Candidate entry only — do not list as stocked, priced, or screened |

---

## 10. Unresolved items (explicit flags — do not resolve by guessing)

1. **"ML-1" — likely MCL-1, UNCONFIRMED.** The document never defines "ML-1". MCL-1 is the standard BCL-2 family anti-apoptotic protein and the plausible reading (the ALS paper's combination partner is MCL1; the catalog's BCL-2 program discusses MCL1 throughout), but "ML-1" is not a standard gene/protein symbol and the document gives no expansion. **Do not write "MCL-1" as fact for this entry until confirmed.** If ML-1 is MCL-1, note the cross-entry link: DacomiLertib would then touch the same MCL1 axis as the AGI-183 + AAV6-hSyn-MCL1 combination — in the opposite direction.
2. **"DPX" — UNRESOLVED.** The phrase "prevent ANT/DPX release" appears in the entry title and throughout. ANT = adenine nucleotide translocator (mitochondrial permeability transition pore component) is the plausible expansion for ANT. **DPX has no definition anywhere in the 182-page document and no standard meaning in apoptosis biology was established in this pass.** Do not guess an expansion (it is not DPI, not Bax, not a standard abbreviation found here). Flag for the merge worker / Mike.
3. **Name collision with dacomitinib — VERIFIED different compound.** Dacomitinib (brand Vizimpro) is a real, FDA-approved (September 2018) irreversible pan-HER/EGFR tyrosine kinase inhibitor for EGFR-mutant metastatic NSCLC; FDA label molecular formula C24H25ClFN5O2·H2O, MW 487.95 Da (verified 2026-11-07 via web search: FDA DailyMed label via fda.report; Wikipedia, "Dacomitinib"). "DacomiLertib" (claimed MW 645.63, purine-core BCL-XL binder) shares only a similar name — different target, different mechanism, different mass. **The similar name is a confusion risk in any external communication: never present DacomiLertib as related to, derived from, or comparable to dacomitinib/Vizimpro.** Note also the irony the merge worker should catch: the document claims "No Kinase Binding" for DacomiLertib while its name evokes a kinase inhibitor.
4. **V132F context — document-claimed only.** The document frames all of entry #201 "in the context of the V132F mutation in BCL-XL" but gives no source, no UniProt/PDB reference, no residue-numbering scheme, and no evidence that V132F is a real or characterised BCL-XL variant (resistance mutation or otherwise). The five "key residues" are asserted, not derived from any shown docking or structure. Treat V132F and the residue list as **unverified document assertions**, not as established binding facts. (Sibling entry #202 uses Y108F in the same unanchored way.)
5. **"No Kinase Binding" — no data.** No panel, assay, or structure supports this; it is a label in the entry header.
6. **The 645.63 Da compound has no structure.** If the program ever wants a real DacomiLertib structure, it must be proposed de novo (drawn, named, and labelled as a new proposal) — the document does not contain one to recover.

---

## 11. What NOT to claim (compound-entry edition)

- Do NOT present MW 645.63, LogP 4.7, ΔG −9.7, IC50 0.39 µM, goodness 0.89, activity ratio 1.4, or selectivity 1.28 as measured results. All are document-claimed simulations/predictions.
- Do NOT quote any of the 16 full-length SMILES as valid structures. All are INVALID as written. Do not quote the tag-stripped cores as "DacomiLertib's SMILES" — they are diagnostic reconstructions, not the document's structures.
- Do NOT present the purine fragment SMILES (`C1=NC2=C(N1)N=CN=C2`, MW 120.11) as the compound, and do NOT claim the compound contains a purine ring — the parseable core contains none.
- Do NOT reconstruct a 645.63 Da structure to make the numbers fit.
- Do NOT claim DacomiLertib treats, cures, or diagnoses cancer or any disease. "Not a medical device" stays attached to every compound output.
- Do NOT claim DacomiLertib minimizes off-target effects, has no kinase binding, or is safe — no data exists; the class warning is on-target thrombocytopenia (§8).
- Do NOT confuse DacomiLertib with dacomitinib (Vizimpro) — different compound, different target.
- Do NOT expand "ML-1" to MCL-1 or "DPX" to anything as fact — both unresolved (§10).
- Do NOT list DacomiLertib as a stocked library compound, a priced job, or a screening result. It is a hypothetical candidate entry.
- Do NOT carry "preventing ANT/DPX release" into any brief as the mechanism of a BCL-XL inhibitor — it contradicts the inhibitor's stated effect (§8).
- Do NOT use entry #202 (Y108F) variants or the end-of-document summary values (ΔG −10.3, selectivity 2.68–3.04) as #201 data.

---

## 12. Open questions needing Mike's decision / merge-worker handoff

1. **Merge target:** the §8 tension (BCL-XL inhibition vs stabilization, same target, opposite directions per disease) is recorded here for the merge worker to fold into `brief-cancer-dao.md` and the BCL-2 program briefs. This file was NOT edited into those briefs (a merge worker is appending to `brief-cancer-dao.md` concurrently).
2. **Naming:** keep "DacomiLertib" as the entry name, or rename to avoid the dacomitinib collision? If the compound is ever developed, the name must change.
3. **ML-1 / DPX:** confirm or drop. If ML-1 is MCL-1, the entry gains a cross-link to the AGI-183/MCL1 combination work (opposite direction — see §8).
4. **Structure:** is there any value in commissioning a de novo drawn structure for a "DacomiLertib v2" proposal, or should the entry stay structure-less (candidate, hypothetical) until a real design exists?
5. **Entry #202 (Y108F):** separate validation entry, or fold as a variant note under this file? The 16–248 variant numbering and the summary values belong to that family, not this one.

---

## Sources

- `~/workspace/user/files/DacomiLertib_effectively_binds_to_BCL-XL__thereby_promoting_apoptosis.pdf` — ChatGPT conversation export; title "DacomiLertib effectively binds to BCL-XL, thereby promoting apoptosis…"; macOS Notes export, created 2026-08-22; 182 pages; 748,384 B. All DacomiLertib fields, SMILES strings, and claimed values are from this file. Repetition counts verified by `pdftotext` extraction (entry #201 ×13; entry #202 ×13; "Molecular Weight: 645.63" ×70; zero citation/PMID/DOI matches).
- RDKit 2026.09.1 (`python3 -c "from rdkit import Chem"`) — all parse / MW / LogP (Crippen) / formula / substructure results in §4–§5 were computed in this pass, 2026-11-07.
- `~/workspace/your_files/bio-research-expansion/compound-agi183.md` — AGI-183 paper entry (BCL-XL stabilizer, ALS) and catalog entry (CRBN/FLIP inhibitor); AGI-010 catalog facts (Bcl-xL CF3, IC50 0.3, goodness 0.91) per coordinator brief; navitoclax thrombocytopenia via PMC9257998 as cited therein.
- Navitoclax / thrombocytopenia verification (web search, 2026-11-07): Wikipedia, "Navitoclax" — "Because navitoclax inhibits Bcl-xL, it reduces platelet lifespan, causing thrombocytopenia, and this makes it dose-limiting" (https://en.wikipedia.org/wiki/Navitoclax).
- Dacomitinib verification (web search, 2026-11-07): FDA DailyMed label via fda.report (C24H25ClFN5O2·H2O, MW 487.95 Da; Vizimpro, first-line EGFR-mutant metastatic NSCLC, approved September 2018) and Wikipedia, "Dacomitinib" (https://en.wikipedia.org/wiki/Dacomitinib).
- The ALS Researcher is not a medical device. It provides compound-library research information only. It does not diagnose, treat, or cure ALS or any disease.

---

## 13. Structure image

**Identifier:** AGI-050 / DacomiLertib-208 — the image file is labelled `50._DacomiLertib-208__AGI-050__copy.png`. This section records the image as the document's structure diagram for this entry. It does not change the entry's status: **HYPOTHETICAL / UNVERIFIED**, all DacomiLertib numbers document-claimed (simulated/predicted), no treatment/cure/diagnosis claim.

**Image file (white-background composite, library copy):** `assets/dacomiLertib-agi050-white.png` (708 × 828 px, RGB PNG, 40,254 bytes). Source: `~/workspace/user/media_library/image/50._DacomiLertib-208__AGI-050__copy.png`. The composite was regenerated in this pass (2026-11-07) from the source; the source file itself was not modified.

**Rendering trap — read this before reusing the image:** the source PNG looks pure black / blank because its pixels are RGB all 0 with all structure living in the **alpha channel** (verified in this pass: 586,224 pixels, 0 with RGB ≠ (0,0,0); alpha 0–255, 21,582 pixels with alpha > 0, 12,366 fully opaque). It is black-on-transparent, so on any dark background it is invisible and on a checkerboard/transparent viewer it reads as a black void. **Always composite onto a white/light background before use; never place the raw transparent PNG on a dark background and never ship it as-is.** The library copy above is already composited onto white — use that file, not the raw source.

**Structure features verified against the white-background composite (visual check, 2026-11-07):**

- **Methoxy-bromophenyl group — CONFIRMED.** Left-hand benzene ring bearing a methoxy (–O–CH₃) substituent and a bromo (Br) substituent.
- **Thiazolidinone-type ring (S, N, C=O, C=N-aryl) — CONFIRMED.** Small S/N ring at top: C=O, S, C=N (to the aryl N), and ring N; the ring N links to the benzylic CH.
- **Para-substituted phenyl — CONFIRMED.** Central benzene ring with the C=N–aryl N at the top and the –NH– at the bottom (1,4-disubstitution).
- **Amide link — CONFIRMED.** –NH–C(=O)–N< joining the para-phenyl to the fused system below.
- **N-methyl tetrahydroquinazoline-type fused system — CONFIRMED.** Bottom fused bicyclic: benzene fused to a saturated six-membered ring with two nitrogens, one carrying a methyl (N–CH₃), the other joined to the amide carbonyl.
- **Also visible (not in the brief's feature list):** a hydroxymethyl –CH₂OH group on the benzylic CH that links the methoxy-bromophenyl ring to the thiazolidinone-type ring N (shown as "HO" in the diagram).

**Validation cross-note — image vs the RDKit-validated stripped core (§4b): NO MATCH established.**

- The §4b stripped core is C₂₆H₂₅N₅O₄S, MW 503.58 (RDKit-recomputed, diagnostic only — not the document's structure). Its left-hand ring is a **pyran ring** (oxygen inside the ring, `C4=CC=COC=C4`) and it contains **no bromine**.
- The image's left-hand ring is a **substituted benzene** (all-carbon ring) bearing **Br** and a methoxy group — bromine is plainly labelled "Br" in the diagram, and the formula C₂₆H₂₅N₅O₄S contains no Br.
- The two agree on the right-hand ~two-thirds (N-methyl tetrahydroquinazoline-type fused system + amide + para-phenyl + thiazolidinone-type ring + the –CH(CH₂OH)– linker), but they disagree on the left-hand ring. **The image structure and the §4b stripped core therefore do not describe the same molecule.** No full formula for the image molecule is asserted here — deriving one would be new chemistry, not verification.
- Consequence: the image is the document's structure diagram and the SMILES strings are the document's strings; the two may or may not describe the same molecule, and on current evidence they do not match. Do not quote the image as "the structure of C₂₆H₂₅N₅O₄S", do not quote any §3/§4 SMILES as "the SMILES of the pictured structure", and do not use the image to rescue the document-claimed MW 645.63 — the image molecule's mass was not established in this pass and the claimed 645.63 g/mol still matches no structure in the document (§5).
