# Raw SMILES Inventory — Bio Research Expansion

**Published:** research brief in this repo's `research/` folder — raw harvest, no validation (see `validated-compound-library.md`).
Extracted 2026-11-07 (PST) by the bio extraction worker from three source PDFs (read-only).
Method: `pdftotext -layout <pdf> -` to stdout only; parsed in memory with Python stdlib.
No SMILES was chemically validated here — that is the RDKit worker's job. No structure was
guessed from any image. All POC/POM/POB/MOA claims below are **UNVERIFIED DOCUMENT CLAIMS**
(no citations in the sources).

## Sources

| # | File | Size | Pages | Notes |
|---|------|------|-------|-------|
| 1 | `AGI_Compound_001.pdf` | 2,786,539 B | 450 | macOS Notes export, created 2026-03-26 |
| 2 | `AGI_-Series.pdf` | 446,678 B | 184 | ChatGPT conversation export, 7,213 text lines |
| 3 | `Venetoclax_SMILES____CC_C__C_C__O_NC1_CC_C_C_C1_N2C_NC3_C2C_CC__C3.pdf` | 46,084 B | 26 | ChatGPT comparison log, 1,000 text lines |

## Counts summary (harvested only — document claims of "300 variations" / "250 compounds" are NOT treated as real)

| Document | Entry labels / blocks | SMILES occurrences | Distinct non-empty SMILES | No-SMILES entries | Broken / placeholder strings |
|----------|----------------------|--------------------|---------------------------|-------------------|------------------------------|
| 1 — AGI_Compound_001 | 417 heading blocks, 413 compounds AGI-001–AGI-413 | 427 (416 full + 1 broken fragment in blocks + 10 summary-style) | 25 (24 valid + 1 broken) | 0 blocks lack a SMILES (8 captured as a lone "●" — see §2.4) | 1 broken fragment (AGI-405, 1st occurrence) |
| 2 — AGI_-Series | 1,320 entry labels | 1,298 | 706 (across all 7 series) | 22 | 3 `[Generated SMILES N]` placeholders (Series 007); truncated fragments in Series 002/004 (see §3) |
| 3 — Venetoclax SMILES | 223 SMILES blocks | 223 | 6 | 0 | 1 truncated "Venetoclax" fragment (×9) + 1 typo variant (×2) |
| **Total** | | **1,948** | | | |

---

## 1. Document 1 — `AGI_Compound_001.pdf`

### 1.1 Headline correction: the catalog is 413 compounds, not 10

The brief described "10 compounds AGI-001 through AGI-010". The full text layer contains
**413 distinct numbered compounds, AGI-001 through AGI-413, contiguous** (no gaps), in
**417 heading-anchored blocks**. Duplicate headings: AGI-001 ×2, AGI-002 ×2, AGI-376 ×2,
AGI-405 ×2. Headings "AGI Compound 001/002" occur only on pp. 1–2; all others read
"Compound AGI-NNN". A summary table for AGI-011–AGI-020 on pp. 18–19 lists SMILES + MW +
LogP + ΔG + Description only (no IC50 / goodness / SMARTS) — those 10 occurrences are
counted separately from the 417 full blocks.

**Corrected full-catalog ranges** (parent's read corrected where it differs):

| Property | Parent's read | As extracted (all 413) |
|----------|---------------|------------------------|
| MW (g/mol) | 286–371 | **286.32–397.20** (max is AGI-203/217/228/… CI, 397.20) |
| LogP | 2.5–4.2 | **2.5–4.5** (max is CI, 4.5) |
| ΔG (kcal/mol) | −7.8 to −9.2 | **−9.2 to −7.4** (weakest is CN, −7.4) |
| Predicted IC50 (µM) | 0.3–1.0 | 0.3–1.0 ✓ (two-decimal values 0.59–0.72 appear from AGI-197 on) |
| Goodness score | 0.75–0.91 | 0.75–0.91 ✓ |

All 413 are CRBN-binding imidazo[4,5-c]pyridine-core compounds (same core
`C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=…`, except AGI-002 which uses a benzimidazole
ring `C3=NC4=CC=CC=C4N3C5=CC=CC=C5`). New substituent SMILES appear from AGI-197 on:
COCH3, CN(C)C, CBr, OCHF2, CI, CCl, CF2H, OCH2F.

### 1.2 AGI-001–AGI-010 — verified table (parent's numbers confirmed except as noted)

| ID | SMILES | MW | LogP | ΔG | IC50 | Goodness | Target (as extracted) |
|----|--------|----|----|----|----|----|----|
| 001 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=CC=C4` | 301.32 | 3.1 | −8.2 | 0.5 | 0.78 | p53 / Bax |
| 002 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC4=CC=CC=C4N3C5=CC=CC=C5` | 371.40 | 4.2 | −9.0 | 0.4 | 0.75 | BIM / PUMA |
| 003 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=CC=C4F` | 319.32 | 3.4 | −8.5 | 0.6 | 0.80 | Mcl-1 |
| 004 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC(=O)OC=C4` | 331.32 | 2.9 | −8.0 | 0.7 | 0.85 | cIAP1 via SMAC/DIABLO |
| 005 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(O)C=C4` | 307.31 | 2.5 | −7.8 | 1.0 | 0.83 | XIAP via SMAC/DIABLO |
| 006 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=NC=C4` | 286.32 | 2.8 | −8.3 | 0.5 | 0.88 | Bcl-2 / Bcl-xL |
| 007 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(C#N)C=C4` | 302.32 | 3.3 | −8.7 | 0.4 | 0.85 | survivin / IAP |
| 008 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(Br)C=C4` | 353.32 | 3.5 | −8.4 | 0.6 | 0.82 | FLIP |
| 009 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(Cl)C=C4` | 317.76 | 3.7 | −8.6 | 0.5 | 0.79 | Mdm2 / p53 |
| 010 | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(CF3)C=C4` | 355.32 | 4.1 | −9.2 | 0.3 | 0.91 | Bcl-2 / Bcl-xL |

Notes: AGI-002's first occurrence (p. 2) lacks a POM section in its block (segmentation
artifact — POM is present in the second occurrence, p. 5). AGI-003's SMILES is the
`C4=CC=CC=C4F` form; every other F occurrence in the catalog uses the
`C4=CC=C(F)C=C4` form (see §1.3). AGI-008's LogP is 3.5 here but the same Br SMILES
later carries LogP 3.9 and 4.1 with different MW/IC50 — see §1.5 (same-SMILES metadata
variants). Parent's per-compound numbers for 001–010 all confirmed as extracted.

### 1.3 ⚠️ AGI-183 IDENTITY COLLISION — DO NOT MERGE

Two different things share the name "AGI-183". Recorded separately:

| | This document's AGI-183 (p. 182) | ALS paper's AGI-183 (separate document, per parallel worker) |
|---|---|---|
| Mechanism | CRBN-binding **FLIP inhibitor**, pro-apoptotic | BCL-XL **stabilizer**, anti-apoptotic |
| Direction | Promotes apoptosis (cancer) | Prevents apoptosis (neuroprotective, ALS) |
| SMILES | `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=CC=C(Br)C=C4` | (not in this document — see ALS paper) |
| MW / LogP / ΔG / IC50 / Goodness | 353.32 / 4.1 / −8.6 / 0.5 µM / 0.82 | (ALS paper's values) |
| Doc text | "targets the CRBN-mediated degradation of FLIP… stabilizing FADD and caspase-8"; justification: "bromine atom to enhance polarizability…"; POC includes a xenograft-shrinkage claim (**UNVERIFIED DOCUMENT CLAIM**) | — |

Neighbouring entries for orientation: AGI-184 = Cl SMILES, Mdm2/p53, IC50 0.6;
AGI-185 = NO2 SMILES, Bcl-2, IC50 0.7. The collision is a naming conflict only —
the two AGI-183s have opposite mechanisms and must never be merged, averaged, or
presented as one compound.

### 1.4 Distinct SMILES in Document 1 (25 strings, with AGI numbers)

Core for all: `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3C4=` except AGI-002 (benzimidazole).
"F" and "F-alt" are the same molecule written two ways in the source — kept as two
distinct strings because the text writes them differently.

| Key | Full SMILES (terminal group shown) | Count | AGI numbers |
|-----|------------------------------------|-------|-------------|
| OCH3 | `…C4=CC=C(OCH3)C=C4` | 63 | 011, 018, 027, 029, 034, 040, 043, 051, 056, 059, 062, 072, 081, 092, 102, 112, 131, 137, 143, 157, 167, 178, 188, 193, 212, 235, 241, 255, 259, 264, 266, 273, 275, 280, 288, 291, 300, 304, 309, 314, 318, 324, 327, 331, 336, 342, 345, 350, 353, 358, 363, 369, 372, 375, 377, 383, 387, 390, 393, 397, 399, 400, 412 |
| CF3 | `…C4=CC=C(CF3)C=C4` | 47 | 010, 012, 021, 036, 042, 053, 060, 067, 077, 087, 097, 107, 117, 126, 128, 197, 200, 219, 222, 232, 242, 256, 260, 265, 268, 274, 277, 283, 289, 293, 299, 303, 308, 312, 317, 322, 329, 334, 340, 348, 356, 361, 367, 381, 394, 401, 408 |
| CBr | `…C4=CC=C(CBr)C=C4` | 44 | 201, 223, 229, 240, 245, 248, 251, 258, 263, 267, 272, 276, 281, 285, 287, 292, 295, 298, 302, 306, 313, 320, 323, 326, 330, 335, 338, 341, 344, 349, 352, 357, 362, 365, 368, 371, 374, 376 (2nd), 379, 385, 395, 402, 406, 411 |
| Cl | `…C4=CC=C(Cl)C=C4` | 41 | 009, 016, 023, 031, 038, 049, 055, 057, 063, 070, 073, 080, 084, 090, 093, 100, 103, 110, 113, 120, 123, 133, 136, 139, 142, 145, 148, 153, 156, 163, 166, 171, 174, 177, 181, 184, 187, 192, 207, 211, 215 |
| Br | `…C4=CC=C(Br)C=C4` | 39 | 008, 015, 025, 032, 037, 046, 048, 054, 064, 068, 074, 078, 083, 088, 094, 098, 104, 108, 114, 118, 127, 129, 135, 141, 147, 150, 152, 155, 162, 165, 173, 176, 183, 186, 206, 209, 213, 221, 236 |
| OCHF2 | `…C4=CC=C(OCHF2)C=C4` | 39 | 202, 220, 231, 238, 244, 247, 250, 254, 262, 269, 271, 278, 284, 286, 290, 294, 297, 301, 307, 311, 316, 321, 328, 333, 339, 347, 355, 360, 366, 380, 386, 389, 392, 396, 398, 403, 407, 409, 413 |
| CI | `…C4=CC=C(CI)C=C4` | 35 | 203, 217, 228, 239, 243, 246, 249, 261, 270, 279, 282, 296, 305, 310, 315, 319, 325, 332, 337, 343, 346, 351, 354, 359, 364, 370, 373, 376 (1st), 378, 382, 384, 388, 391, 404, 410 |
| CN | `…C4=CC=C(CN)C=C4` | 30 | 013, 020, 039, 045, 047, 058, 066, 069, 076, 079, 082, 086, 089, 096, 099, 106, 109, 116, 119, 125, 130, 159, 169, 180, 190, 195, 210, 218, 230, 253 |
| NO2 | `…C4=CC=C(NO2)C=C4` | 26 | 019, 026, 033, 065, 075, 085, 095, 105, 115, 124, 134, 140, 146, 149, 154, 158, 164, 168, 175, 179, 185, 189, 194, 208, 214, 227 |
| F | `…C4=CC=C(F)C=C4` | 20 | 014, 022, 028, 035, 041, 044, 052, 061, 071, 091, 101, 111, 122, 132, 138, 144, 160, 170, 191, 196 |
| OCF3 | `…C4=CC=C(OCF3)C=C4` | 9 | 121, 151, 161, 172, 182, 216, 226, 237, 252 |
| C#N | `…C4=CC=C(C#N)C=C4` | 5 | 007, 017, 024, 030, 050 |
| CCl | `…C4=CC=C(CCl)C=C4` | 4 | 204, 224, 233, 257 |
| CF2H | `…C4=CC=C(CF2H)C=C4` | 3 | 205, 225, 234 |
| phenyl | `…C4=CC=CC=C4` | 2 | 001 (×2 blocks) |
| benzimidazole | `…C3=NC4=CC=CC=C4N3C5=CC=CC=C5` | 2 | 002 (×2 blocks) |
| F-alt | `…C4=CC=CC=C4F` | 1 | 003 |
| lactone | `…C4=CC(=O)OC=C4` | 1 | 004 |
| phenol | `…C4=CC=C(O)C=C4` | 1 | 005 |
| pyridyl | `…C4=CC=NC=C4` | 1 | 006 |
| COCH3 | `…C4=CC=C(COCH3)C=C4` | 1 | 198 |
| CN(C)C | `…C4=CC=C(CN(C)C)C=C4` | 1 | 199 |
| OCH2F | `…C4=CC=C(OCH2F)C=C4` | 1 | 405 (2nd occurrence) |
| **BROKEN** | `` `C1=CN=C2C(=N1)C(=CC `` (fragment, p. 429) | 1 | 405 (1st occurrence) — no metadata |

Counts sum to 417 blocks. The 10 summary-style occurrences (AGI-011–020, pp. 18–19)
repeat SMILES already counted above and are not double-counted here.

### 1.5 Full catalog table — AGI-001–AGI-413 (417 blocks)

Target = first protein named in the block's "degradation of X" phrase, shortened.
† = that block's extracted fragment named no protein; value filled from sibling blocks
with the same SMILES + MW (all of which name the same target). "SMILES" here is the
substituent key from §1.4 — see that table for the full string. Pages are pdfinfo page
numbers (1-based). The broken AGI-405 first occurrence has no metadata.

| ID | Page | SMILES | MW | LogP | ΔG | IC50 | G | Target |
|----|------|--------|----|----|----|----|----|----|
| 001 | 1 | phenyl | 301.32 | 3.1 | −8.2 | 0.5 | 0.78 | p53/Bax |
| 001 | 3 | phenyl | 301.32 | 3.1 | −8.2 | 0.5 | 0.78 | p53/Bax |
| 002 | 2 | benzimidazole | 371.40 | 4.2 | −9.0 | 0.4 | 0.75 | BIM/PUMA |
| 002 | 5 | benzimidazole | 371.40 | 4.2 | −9.0 | 0.4 | 0.75 | BIM/PUMA |
| 003 | 6 | F-alt | 319.32 | 3.4 | −8.5 | 0.6 | 0.80 | Mcl-1 |
| 004 | 8 | lactone | 331.32 | 2.9 | −8.0 | 0.7 | 0.85 | SMAC/DIABLO |
| 005 | 9 | phenol | 307.31 | 2.5 | −7.8 | 1.0 | 0.83 | XIAP |
| 006 | 11 | pyridyl | 286.32 | 2.8 | −8.3 | 0.5 | 0.88 | Bcl-2/Bcl-xL |
| 007 | 12 | C#N | 302.32 | 3.3 | −8.7 | 0.4 | 0.85 | IAP family |
| 008 | 13 | Br | 353.32 | 3.5 | −8.4 | 0.6 | 0.82 | FLIP |
| 009 | 15 | Cl | 317.76 | 3.7 | −8.6 | 0.5 | 0.79 | Mdm2/p53 |
| 010 | 16 | CF3 | 355.32 | 4.1 | −9.2 | 0.3 | 0.91 | Bcl-xL |
| 011 | 20 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | SMAC/DIABLO |
| 012 | 21 | CF3 | 355.32 | 4.3 | −8.9 | 0.6 | 0.84 | Bcl-2 |
| 013 | 23 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 014 | 24 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.80 | Mcl-1 |
| 015 | 26 | Br | 363.32 | 4.1 | −8.7 | 0.5 | 0.82 | FLIP |
| 016 | 27 | Cl | 317.76 | 3.7 | −8.6 | 0.6 | 0.79 | Mdm2 |
| 017 | 29 | C#N | 302.32 | 3.2 | −8.1 | 0.7 | 0.85 | IAP family† |
| 018 | 30 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | SMAC/DIABLO |
| 019 | 31 | NO2 | 346.32 | 3.1 | −8.5 | 0.6 | 0.78 | Bcl-2 |
| 020 | 33 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 021 | 34 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 022 | 35 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | anti-apoptotic proteins |
| 023 | 36 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2† |
| 024 | 37 | C#N | 302.32 | 3.2 | −8.1 | 0.7 | 0.85 | IAP family† |
| 025 | 38 | Br | 353.32 | 3.9 | −8.6 | 0.6 | 0.81 | FLIP |
| 026 | 39 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 027 | 40 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 028 | 40 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 029 | 41 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 030 | 42 | C#N | 302.32 | 3.2 | −8.1 | 0.7 | 0.85 | IAP family† |
| 031 | 43 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2† |
| 032 | 44 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 033 | 45 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 034 | 46 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 035 | 47 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 036 | 48 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 037 | 49 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 038 | 50 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 039 | 50 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 040 | 51 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | anti-apoptotic proteins |
| 041 | 53 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 042 | 54 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 043 | 55 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 044 | 55 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 045 | 56 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 046 | 57 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 047 | 58 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 048 | 59 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 049 | 60 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 050 | 61 | C#N | 302.32 | 3.2 | −8.1 | 0.7 | 0.85 | Mcl-1 |
| 051 | 62 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 052 | 63 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 053 | 64 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 054 | 65 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 055 | 66 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 056 | 67 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 057 | 67 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 058 | 68 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 059 | 69 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 060 | 70 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 061 | 72 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 062 | 72 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 063 | 73 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 064 | 74 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 065 | 75 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 066 | 76 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 067 | 77 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 068 | 78 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 069 | 79 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 070 | 80 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 071 | 81 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 072 | 82 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 073 | 83 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 074 | 84 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 075 | 85 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 076 | 86 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 077 | 86 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 078 | 87 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 079 | 88 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 080 | 89 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 081 | 90 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 082 | 91 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 083 | 92 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 084 | 93 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 085 | 94 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 086 | 95 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 087 | 96 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 088 | 96 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 089 | 97 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 090 | 98 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 091 | 100 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 092 | 100 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 093 | 101 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 094 | 102 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 095 | 103 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 096 | 104 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 097 | 105 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 098 | 106 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 099 | 107 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 100 | 108 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 101 | 109 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 102 | 110 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 103 | 111 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 104 | 112 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 105 | 112 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 106 | 113 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 107 | 114 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 108 | 115 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 109 | 116 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 110 | 117 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 111 | 118 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 112 | 119 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 113 | 120 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 114 | 121 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 115 | 122 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 116 | 123 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 117 | 124 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 118 | 125 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 119 | 125 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 120 | 126 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 121 | 128 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 122 | 129 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 123 | 129 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2† |
| 124 | 130 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 125 | 131 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 126 | 132 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 127 | 133 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 128 | 134 | CF3 | 355.32 | 4.2 | −8.9 | 0.5 | 0.86 | Bcl-2 |
| 129 | 135 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 130 | 136 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | anti-apoptotic proteins |
| 131 | 137 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 132 | 138 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 133 | 139 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 134 | 140 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 135 | 140 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 136 | 141 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 137 | 142 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 138 | 143 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 139 | 144 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 140 | 145 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 141 | 146 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 142 | 147 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 143 | 147 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 144 | 148 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 145 | 149 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 146 | 150 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 147 | 151 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 148 | 152 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 149 | 152 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 150 | 153 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP† |
| 151 | 154 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 152 | 155 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 153 | 156 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 154 | 157 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 155 | 158 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 156 | 159 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 157 | 159 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 158 | 160 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 159 | 161 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 160 | 162 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 161 | 163 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 162 | 164 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 163 | 165 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 164 | 166 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 165 | 167 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 166 | 167 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 167 | 168 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 168 | 169 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 169 | 170 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 170 | 171 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 171 | 172 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 172 | 173 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 173 | 174 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 174 | 175 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 175 | 175 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 176 | 176 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 177 | 177 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 178 | 178 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 179 | 179 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 180 | 179 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | anti-apoptotic proteins |
| 181 | 181 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 182 | 182 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 183 | 182 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 184 | 183 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 185 | 184 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 186 | 185 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 187 | 186 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 188 | 187 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 189 | 187 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 190 | 188 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 191 | 189 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 192 | 190 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 193 | 191 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 194 | 192 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 195 | 192 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 196 | 193 | F | 319.32 | 3.4 | −7.8 | 0.6 | 0.82 | Mcl-1 |
| 197 | 195 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 198 | 195 | COCH3 | 335.34 | 2.8 | −7.7 | 0.7 | 0.80 | anti-apoptotic proteins |
| 199 | 196 | CN(C)C | 335.35 | 3.2 | −7.8 | 0.72 | 0.79 | XIAP |
| 200 | 197 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 201 | 198 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 202 | 199 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 203 | 200 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 204 | 201 | CCl | 331.21 | 3.7 | −8.1 | 0.64 | 0.80 | Mdm2 |
| 205 | 202 | CF2H | 353.32 | 3.8 | −7.9 | 0.66 | 0.82 | fragment — "destabilizing M…" |
| 206 | 203 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 207 | 204 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 208 | 205 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 209 | 206 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 210 | 207 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | anti-apoptotic proteins |
| 211 | 208 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 212 | 209 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 213 | 210 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 214 | 210 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 215 | 211 | Cl | 317.76 | 3.8 | −8.3 | 0.6 | 0.79 | Mdm2 |
| 216 | 212 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 217 | 213 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 218 | 214 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 219 | 215 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 220 | 216 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 221 | 217 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 222 | 218 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 223 | 219 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 224 | 220 | CCl | 331.21 | 3.7 | −8.1 | 0.64 | 0.80 | Mdm2 |
| 225 | 220 | CF2H | 353.32 | 3.8 | −7.9 | 0.66 | 0.82 | fragment — "destabilizing M…" |
| 226 | 222 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 227 | 223 | NO2 | 346.32 | 3.1 | −8.5 | 0.7 | 0.78 | Bcl-2 |
| 228 | 223 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 229 | 224 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 230 | 225 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 231 | 226 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 232 | 227 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 233 | 228 | CCl | 331.21 | 3.7 | −8.1 | 0.64 | 0.80 | Mdm2 |
| 234 | 229 | CF2H | 353.32 | 3.8 | −7.9 | 0.66 | 0.82 | fragment — "destabilizing M…" |
| 235 | 230 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 236 | 231 | Br | 353.32 | 4.1 | −8.6 | 0.5 | 0.82 | FLIP |
| 237 | 232 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 238 | 233 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 239 | 234 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 240 | 234 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 241 | 236 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 242 | 236 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 243 | 237 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 244 | 238 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 245 | 239 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 246 | 240 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 247 | 241 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 248 | 242 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 249 | 243 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 250 | 244 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 251 | 245 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 252 | 246 | OCF3 | 359.31 | 3.7 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 253 | 247 | CN | 305.31 | 2.5 | −7.4 | 0.8 | 0.79 | XIAP |
| 254 | 248 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 255 | 248 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 256 | 250 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 257 | 250 | CCl | 331.21 | 3.7 | −8.1 | 0.64 | 0.80 | Mdm2 |
| 258 | 251 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 259 | 252 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 260 | 253 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 261 | 254 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 262 | 255 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 263 | 256 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 264 | 257 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 265 | 258 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 266 | 259 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 267 | 260 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 268 | 260 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 269 | 261 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 270 | 262 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 271 | 263 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 272 | 264 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 273 | 265 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 274 | 266 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 275 | 267 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 276 | 268 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 277 | 269 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 278 | 270 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 279 | 271 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 280 | 271 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 281 | 273 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 282 | 273 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 283 | 274 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 284 | 275 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 285 | 276 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 286 | 277 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 287 | 278 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 288 | 279 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 289 | 280 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 290 | 281 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 291 | 282 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 292 | 283 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 293 | 284 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 294 | 284 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 295 | 285 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 296 | 286 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 297 | 287 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 298 | 288 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 299 | 289 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 300 | 290 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 301 | 291 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 302 | 292 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 303 | 293 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 304 | 294 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 305 | 294 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 306 | 296 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 307 | 297 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 308 | 298 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 309 | 298 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 310 | 299 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 311 | 301 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 312 | 301 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 313 | 302 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 314 | 303 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 315 | 304 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 316 | 305 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 317 | 306 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 318 | 307 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 319 | 308 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 320 | 309 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 321 | 310 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 322 | 311 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 323 | 312 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 324 | 313 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 325 | 313 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 326 | 314 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 327 | 315 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 328 | 316 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 329 | 317 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 330 | 318 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 331 | 319 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 332 | 320 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 333 | 321 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 334 | 322 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 335 | 323 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 336 | 323 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 337 | 324 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 338 | 325 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 339 | 326 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 340 | 327 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 341 | 328 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 342 | 329 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 343 | 330 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 344 | 331 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 345 | 331 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 346 | 332 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 347 | 333 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 348 | 334 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 349 | 335 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 350 | 336 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 351 | 337 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 352 | 338 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 353 | 339 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 354 | 340 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 355 | 341 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 356 | 342 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 357 | 342 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 358 | 343 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 359 | 344 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 360 | 345 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 361 | 346 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 362 | 347 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 363 | 348 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 364 | 349 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 365 | 350 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 366 | 351 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Mcl-1 |
| 367 | 352 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | Mcl-1 |
| 368 | 353 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 369 | 353 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 370 | 354 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 371 | 355 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 372 | 356 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 373 | 357 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 374 | 358 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 375 | 359 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | cIAP2 |
| 376 | 360 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 376 | 363 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 377 | 365 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | anti-apoptotic proteins |
| 378 | 367 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 379 | 369 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | Bax |
| 380 | 372 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | anti-apoptotic proteins |
| 381 | 374 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | anti-apoptotic proteins |
| 382 | 376 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 383 | 379 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | anti-apoptotic proteins |
| 384 | 381 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 385 | 383 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 386 | 386 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |
| 387 | 388 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | anti-apoptotic proteins |
| 388 | 390 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 389 | 392 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |
| 390 | 395 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | anti-apoptotic proteins |
| 391 | 397 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 392 | 399 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |
| 393 | 401 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | SMAC/DIABLO |
| 394 | 404 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | BIM |
| 395 | 406 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 396 | 408 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |
| 397 | 411 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | SMAC/DIABLO |
| 398 | 413 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |
| 399 | 415 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | SMAC/DIABLO |
| 400 | 417 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | SMAC/DIABLO |
| 401 | 420 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | BIM |
| 402 | 422 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 403 | 424 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |
| 404 | 427 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 405 | 429 | BROKEN | — | — | — | — | — | — |
| 405 | 429 | OCH2F | 333.31 | 3.5 | −7.8 | 0.72 | 0.80 | BIM |
| 406 | 431 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 407 | 434 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |
| 408 | 436 | CF3 | 335.32 | 3.9 | −8.0 | 0.65 | 0.83 | BIM |
| 409 | 438 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |
| 410 | 441 | CI | 397.20 | 4.5 | −8.4 | 0.59 | 0.85 | anti-apoptotic proteins |
| 411 | 443 | CBr | 371.21 | 4.0 | −8.2 | 0.6 | 0.84 | anti-apoptotic proteins |
| 412 | 445 | OCH3 | 321.32 | 2.9 | −7.6 | 0.7 | 0.81 | SMAC/DIABLO |
| 413 | 447 | OCHF2 | 348.30 | 3.6 | −7.9 | 0.68 | 0.82 | Bax |

### 1.6 Same SMILES, different stated metadata (6 SMILES; 18 of 24 valid SMILES have exactly 1 metadata set)

The document assigns different MW / LogP / ΔG / IC50 / goodness to the same SMILES string.
Flagged for the RDKit worker — do not average these.

| SMILES (key) | Variants (MW / LogP / ΔG / IC50 / G) |
|---|---|
| Br | (353.32 / 3.5 / −8.4 / 0.6 / 0.82) AGI-008 · (353.32 / 3.9 / −8.6 / 0.6 / 0.81) AGI-025 · (353.32 / 4.1 / −8.6 / 0.5 / 0.82) most Br blocks · (363.32 / 4.1 / −8.7 / 0.5 / 0.82) AGI-015 only |
| CF3 | (335.32 / 3.9 / −8.0 / 0.65 / 0.83) AGI-197 series · (355.32 / 4.1 / −9.2 / 0.3 / 0.91) AGI-010 · (355.32 / 4.2 / −8.9 / 0.5 / 0.86) most 355.32 blocks · (355.32 / 4.3 / −8.9 / 0.6 / 0.84) AGI-012 |
| Cl | (317.76 / 3.7 / −8.6 / 0.5 / 0.79) AGI-009, 016 · (317.76 / 3.8 / −8.3 / 0.6 / 0.79) most Cl blocks |
| C#N | (302.32 / 3.3 / −8.7 / 0.4 / 0.85) AGI-007 · (302.32 / 3.2 / −8.1 / 0.7 / 0.85) AGI-017, 024, 030, 050 |
| F | (319.32 / 3.4 / −7.8 / 0.6 / G 0.80) AGI-003, 014 · (319.32 / 3.4 / −7.8 / 0.6 / G 0.82) other F blocks |
| NO2 | (346.32 / 3.1 / −8.5 / 0.6 / 0.78) AGI-019 · (346.32 / 3.1 / −8.5 / 0.7 / 0.78) other NO2 blocks |

### 1.7 SMARTS notes

- 417 SMARTS occurrences (one per block, including the broken AGI-405 first occurrence
  which has no SMARTS). Common prefix:
  `[#6]1:[#7]:[#6]:[#7]2:[#6]:[#6]:[#6]:[#6]:[#6]:[#6]:2:[#6]:1:` + a variable tail
  per substituent (e.g. `[#7]:[#6]:[#6]:[#6]` for the phenyl core; Br tail `[#35]`,
  Cl tail `[#17]`, I tail `[#53]`, F tail `[#9]`).
- Anomalies: backtick-prefixed SMARTS in places; AGI-168 contains a `[#6**]` typo;
  some tails are unbracketed (e.g. `Br`, `Cl` written bare); truncated tails in late
  entries (384, 385, 388, 391, 395, 402, 404, 406, 410, 411 — e.g. `[#7]:[#53]`,
  `[#7]:[#35]`); AGI-077, 157, 198, 216, 255, 268 have empty SMARTS tails.
- The MW field label in the source is "Molecular Weight: NNN g/mol" (not "MW:").
  The ΔG label is "ΔG (Binding Free Energy):" — in AGI-270, 337 and 376 (1st) it is
  mistyped with a double closing paren, `ΔG (Binding Free Energy)):`; values still
  recovered (all −8.4).

### 1.8 POC / POM / POB / MOA presence — ALL CLAIMS UNVERIFIED

- POC present in 416/417 blocks (only the broken AGI-405 first occurrence lacks it).
- POM present in 415/417 (AGI-002 first occurrence and the broken AGI-405 lack it).
- POB missing in 1 block; MOA missing in 39 blocks.
- **Every POC/POM claim in this document is an UNVERIFIED DOCUMENT CLAIM**: in vitro
  IC50s, in vivo xenograft shrinkage, Western blots and co-IP are asserted with NO
  citations, no methods, no data tables. Do not cite them as results.
- Late entries (~AGI-376 on) often name no specific downstream target (CRBN only)
  and some add a "● Solubility:" field. Wording changes to "Justification for
  Modifications:" from ~AGI-400 on. Late entries (~379+) introduce Bax and BIM as
  downstream targets for the same substituents that earlier targeted Mcl-1 /
  anti-apoptotic proteins (e.g. OCHF2 → Mcl-1 before AGI-380, → Bax after).
- **AGI-376 duplicate with different SMILES**: AGI-376 p. 360 = CI SMILES
  (MW 397.20); AGI-376 p. 363 = CBr SMILES (MW 371.21). Same number, different
  compound — flag for the RDKit worker.

### 1.9 Picture-pages gap — the "~375 structure picture pages" claim is refuted

- Raw byte scan of all three PDFs: **0 `/Subtype /Image` and 0 `/XObject`** — there
  are no embedded raster images in any of the three documents.
- Document 1 content-stream check (stdlib `zlib` decompression of all 459 streams):
  **4 total path-painting operators** vs **59,084 text operators**; 0 streams with
  >50 path ops. There are **no vector structure drawings** either.
- 449/450 Document 1 pages carry ≥300 characters of extractable text (only p. 450
  has 110 chars, plus a trailing empty split page).
- Conclusion: Document 1 is a pure-text document. No structure pictures were
  harvested because none exist in the file as images or vector art. If structure
  diagrams exist anywhere for these compounds, they are not in this PDF.

### 1.10 Truncation and layout artifacts

- Document ends truncated: p. 450 has 110 characters and ends mid-sentence
  ("…specificity, potentially expanding the therapeutic applications of AGI-413
  to a…"). AGI-413's core metadata (SMILES, MW, LogP, ΔG, IC50, goodness) is complete.
- Lone-"●" layout artifact: in AGI-092, 105, 143, 151, 225, 347, 393, 400 the SMILES
  sits 2 lines below a lone bullet; values recovered and confirmed by their MWs
  (092 OCH3, 105 NO2, 143 OCH3, 151 OCF3, 225 CF2H, 347 OCHF2, 393 OCH3, 400 OCH3).
- AGI-405 first occurrence (p. 429) is a broken fragment only:
  `` `C1=CN=C2C(=N1)C(=CC `` with no metadata; the second AGI-405 occurrence on the
  same page is complete (OCH2F, MW 333.31, LogP 3.5, ΔG −7.8, IC50 0.72, G 0.80).

---

## 2. Document 2 — `AGI_-Series.pdf`

A ChatGPT conversation export. **The brief said 3 series; the file contains 7.**
The user asked for 300 variations per series; ChatGPT answered in batches of ~30 with
`...` placeholders. Harvested counts only — "300 variations" is not treated as real.

### 2.1 Per-series summary

| Series | Label in document | Entry labels | With SMILES | No SMILES | Distinct SMILES |
|--------|-------------------|--------------|-------------|-----------|-----------------|
| 001 | BCL-2 Inhibitors (Venetoclax) | 40 (VAR 1–30, 300) | 40 | 0 | 36 |
| 002 | BAX Activators (BAM7) | 639 (VAR 1–700) | 620 | 19 | 327 |
| 003 | MCL-1 Inhibitors (S63845) | 132 | 132 | 0 | 121 |
| 004 | Lisinopril-like, then Atorvastatin-like (see §2.5) | 196 (VAR 1–100 + 001–200) | 196 | 0 | 21 |
| 005 | Riluzole | 100 (VAR 001–100) | 100 | 0 | 70 |
| 006 | Pregabalin | 200 (VAR 001–200) | 200 | 0 | 140 |
| 007 | Recently-expired HIV drug (per user prompt) | 13 (VAR 001–010, 100) | 10 | 3 | 2 |
| **Total** | | **1,320** | **1,298** | **22** | **706 global** (11 strings shared across series) |

### 2.2 Header error (confirmed)

The Series 002 header reads **`ABT-199- BAX Activators (BAM7)`** — conflating ABT-199
(venetoclax) with BAM7 (a BAX activator). ABT-199 is a BCL-2 inhibitor, not a BAX
activator. Flagged as a document error, not corrected.

### 2.3 Label formats found

- A — `● AGI-00N-VARMMM:` — 487 labels
- B — `Variation NNN: AGI-Series 00N:` — 184 labels
- D — `. AGI-Series 00N: Variation NNN` — 401 labels
- F — bare `Variation NNN:` — 238 labels
- E-inline — `Variation NNN: SMILES: X` — 11 entries (Series 003)
- Exact `...` placeholder lines: 11. Drug mentions in the text: Pregabalin 9,
  Venetoclax 4, BAM7 3, S63845 2, ABT-199 1, Riluzole 7.

### 2.4 Scaffold drift in Series 002

- Intro VAR 01–05 (A-format) use the Series 001 quinoxaline scaffold.
- VAR 001+ (A-format) use an indole scaffold
  `CC1=C(C2=C(NC3=CC=CC=C23)...)` through VAR 500.
- From VAR 501 (B-format) the scaffold changes to small-fragment scaffolds
  (`C1CCN(CC1)...`, `CC(C1=CC=CC=C1)...`, etc.).
- From ~VAR 523 the strings become runaway repetitive phenyl chains, growing
  ~13 chars per VAR (VAR 562 = 195 chars … VAR 682 = 1,027 chars), ending in
  complete ring closures (e.g. `…C81=CC=CC=C81`). Two head scaffolds alternate:
  `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5…` and
  `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5…`.
- VAR 576 (len 149, ends mid-token `…C14=CC`) and the first VAR 634 occurrence
  (len 336, ends `…C28=CC=CC=C`) are truncated in the source text; a second,
  complete VAR 634 (len 715) follows.

### 2.5 Series 001 — BCL-2 / Venetoclax (40 entries, 36 distinct)

Quinoxaline scaffold `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4` + substituents.
**These are NOT venetoclax** (real venetoclax: C45H50ClN7O7S, MW ~868) — the series
uses a quinoxaline scaffold throughout. VAR 2, 3 and 30 each carry TWO strings
(the intro block repeats the label with a different string).

- [1] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4`
- [2] `C1=CC=C(C=C1)C2=NC(C3=CC=CC=C3)N=C2C4=CC=CC=C4`
- [2] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4O`
- [3] `C1=CC=C(C=C1)C2=NC(NC3=CC=CC=C3)N=C2C4=CC=CC=C4`
- [3] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4N`
- [4] `C1=CC=C(C=C1)C2=NC(C3=CC=CC=N3)N=C2C4=CC=CC=C4`
- [4] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4F`
- [5] `C1=CC=C(C=C1)C2=NC(C3=CC=CN=C3)N=C2C4=CC=CC=C4`
- [5] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4Cl`
- [6] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4Br`
- [7] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4I`
- [8] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CF3`
- [9] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4OCF3`
- [10] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4NO2`
- [11] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4SO2`
- [12] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4NH2`
- [13] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4SH`
- [14] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4OH`
- [15] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CH3`
- [16] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4C2H5`
- [17] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CH(CH3)2`
- [18] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4C(CH3)3`
- [19] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4C=O`
- [20] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4COOH`
- [21] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CONH2`
- [22] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CNH2`
- [23] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4COCH3`
- [24] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4COC2H5`
- [25] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4C(C=O)NH2`
- [26] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4C(=O)OC2H5`
- [27] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4COH`
- [28] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CBr`
- [29] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CCI`
- [30] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CNH3`
- [30] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CO2`
- [300] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4Cl2`

### 2.6 Series 002 — BAX / BAM7, A-format (VAR 1–441, 151 distinct)

Indole scaffold `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4…)C5=CC=CC=C15`.
VAR 1–5 and VAR 300 also carry quinoxaline-scaffold strings (intro block).
VAR 167's string ends with a stray `Y` in the extracted text
(`…C5=CC=CC=C15Y`) — extraction artifact, RDKit worker to check.

- [1] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4O`
- [1] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4)C5=CC=CC=C15`
- [2] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4N`
- [2] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4F)C5=CC=CC=C15`
- [3] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4F`
- [3] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4Cl)C5=CC=CC=C15`
- [4,30] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4Cl`
- [4] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4Br)C5=CC=CC=C15`
- [5] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4Br`
- [5] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4I)C5=CC=CC=C15`
- [6] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4NO2)C5=CC=CC=C15`
- [7] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4OH)C5=CC=CC=C15`
- [8] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4OCF3)C5=CC=CC=C15`
- [9,36,56,60,64-65,69,83-84,91,96,114,118,122-123,131,136,144,162,166,171,196,202,212,228,244,248,270,276,282,291,309] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CF3)C5=CC=CC=C15`
- [10] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4NH2)C5=CC=CC=C15`
- [11] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4SO2)C5=CC=CC=C15`
- [12] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CH3)C5=CC=CC=C15`
- [13,41] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C2H5)C5=CC=CC=C15`
- [14,54,112,160,242] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(CH3)3)C5=CC=CC=C15`
- [15,31,39,135,195,233,275] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CNH2)C5=CC=CC=C15`
- [16] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COOH)C5=CC=CC=C15`
- [17,42,88,129,174,200,221,237,254,280] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C=O)C5=CC=CC=C15`
- [18,45,103,151,185,205,223,265,285,302] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CBr)C5=CC=CC=C15`
- [19] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CCI)C5=CC=CC=C15`
- [20,55,113,161,243] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC2H5)C5=CC=CC=C15`
- [21,37] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCH3)C5=CC=CC=C15`
- [22,32,38,50,77,86,99,108,137,156,183,198,211,235,263,278,290,300] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CONH2)C5=CC=CC=C15`
- [23] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CNH3)C5=CC=CC=C15`
- [24,70,93] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(C=O)NH2)C5=CC=CC=C15`
- [25,134] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(=O)OC2H5)C5=CC=CC=C15`
- [26,47,105,153,180,207,217,260,287,297] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CNHCOCH3)C5=CC=CC=C15`
- [27,29] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COH)C5=CC=CC=C15`
- [28,76,87,100,128,138,146,172,197,220,234,253,277] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C=NN)C5=CC=CC=C15`
- [30,40,44,59,63,68,73,80,89,98,102,117,121,127,133,140,143,147,165,170,184,199,222,236,247,251-252,264,279] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CF2)C5=CC=CC=C15`
- [33,49,79,85,107,139,145,155,173,182,209-210,238,262,289] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COOCH3)C5=CC=CC=C15`
- [34,61,66,78,92,119,124,132,142,168,249] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CONHCOCH3)C5=CC=CC=C15`
- [35,48,106,154,181,208,218,261,288,298] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCH2OH)C5=CC=CC=C15`
- [43,101,179,191,203,216,229,259,271,283,296,312] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C#N)C5=CC=CC=C15`
- [46,104,152,186,206,224,266,286] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CI)C5=CC=CC=C15`
- [51,109,150,157,176,187,190,194,204,213,225,232,239,256,267,274,284,292] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(F)(F)F)C5=CC=CC=C15`
- [52,81,95,110,141,149,158,177,193,214,231,240,257,273,293-294] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CCl)C5=CC=CC=C15`
- [53,74,82,94,111,148,159,178,192,215,230,241,258,272,295] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCF3)C5=CC=CC=C15`
- [57,115,163,188,226,245,268] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CON(CH3)2)C5=CC=CC=C15`
- [58,75,90,97,116,130,164,189,201,219,227,246,269,281] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COOC2H5)C5=CC=CC=C15`
- [62,120,169,250] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CON(CH2)2)C5=CC=CC=C15`
- [67,125-126] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CON(CH2)3)C5=CC=CC=C15`
- [71] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(C=O)NHCOCH3)C5=CC=CC=C15`
- [72] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(CH3)3)C5=CC=CC=C15`
- [167] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CONHCOCH3)C5=CC=CC=C15Y` — trailing `Y` as extracted; verify
- [175,255,299] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COOCH2CH3)C5=CC=CC=C15`
- [300] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4SO2`
- [301] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CCC)C(=O)O)C5=CC=CC=C15`
- [303] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCH2CH3)C5=CC=CC=C15`
- [304] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CS)C5=CC=CC=C15`
- [305] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C=N)C5=CC=CC=C15`
- [306] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)CH3)C5=CC=CC=C15`
- [307] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(=O)N)C5=CC=CC=C15`
- [308,329] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(=O)OC)C5=CC=CC=C15`
- [310] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(=O)N(C)C)C5=CC=CC=C15`
- [311,336] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CCN)C5=CC=CC=C15`
- [313] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN=C=O)C5=CC=CC=C15`
- [314] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC)C5=CC=CC=C15`
- [315-316] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CNC(=O)C)C5=CC=CC=C15`
- [317] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)C)C5=CC=CC=C15`
- [318] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(O)C)C5=CC=CC=C15`
- [319] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CS(=O)C)C5=CC=CC=C15`
- [320] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)CC)C5=CC=CC=C15`
- [321] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCC)C5=CC=CC=C15`
- [322] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(C)C)C5=CC=CC=C15`
- [323] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(C)C)C5=CC=CC=C15`
- [324] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CNC(=O)CC)C5=CC=CC=C15`
- [325] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)C(=O)C)C5=CC=CC=C15`
- [326] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(CO)C)C5=CC=CC=C15`
- [327] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(N)CC)C5=CC=CC=C15`
- [328] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(CN)C)C5=CC=CC=C15`
- [330] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CNC(=O)OC)C5=CC=CC=C15`
- [331] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C(=O)C)CC)C5=CC=CC=C15`
- [332,341] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCCN)C5=CC=CC=C15`
- [333] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CS(=O)(=O)C)C5=CC=CC=C15`
- [334] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CC)C)C5=CC=CC=C15`
- [335] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(C)O)C5=CC=CC=C15`
- [337] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(C)O)C5=CC=CC=C15`
- [338] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC=O)C5=CC=CC=C15`
- [339] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CC)CC)C5=CC=CC=C15`
- [340,358] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(C)NC(=O)C)C5=CC=CC=C15`
- [342] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(=O)OCC)C5=CC=CC=C15`
- [343] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(O)CC)C5=CC=CC=C15`
- [344] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(=O)O)C5=CC=CC=C15`
- [345] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C(=O)C)C)C5=CC=CC=C15`
- [346] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(O)CO)C5=CC=CC=C15`
- [347] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(C)(C)C)C5=CC=CC=C15`
- [348] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C(=O)CC)C)C5=CC=CC=C15`
- [349] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(CN)C)C5=CC=CC=C15`
- [350] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C)C5=CC=CC=C15`
- [351] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(O)CCO)C5=CC=CC=C15`
- [352] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(C)N)C5=CC=CC=C15`
- [353] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C)C5=CC=CC=C15`
- [354] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CCN(C(=O)C)C)C5=CC=CC=C15`
- [355] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(O)COC)C5=CC=CC=C15`
- [356] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(O)CC(C)C)C5=CC=CC=C15`
- [357] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)CO)C5=CC=CC=C15`
- [359] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C)C5=CC=CC=C15`
- [360] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)CN)C5=CC=CC=C15`
- [361] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(N)CO)C5=CC=CC=C15`
- [362,378] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCC(O)C)C5=CC=CC=C15`
- [363] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)NC)C5=CC=CC=C15`
- [364] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)CO)C5=CC=CC=C15`
- [365] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)CN(C)C)C5=CC=CC=C15`
- [366] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)CC)C5=CC=CC=C15`
- [367,388] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)O)C5=CC=CC=C15`
- [368,386,402] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)C)C5=CC=CC=C15`
- [369] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)N)C5=CC=CC=C15`
- [370] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)N)C5=CC=CC=C15`
- [371] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)CC)C5=CC=CC=C15`
- [372] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)NC)C5=CC=CC=C15`
- [373] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)C)C5=CC=CC=C15`
- [374,391,398] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)N(C)C)C5=CC=CC=C15`
- [375] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCC(=O)N)C5=CC=CC=C15`
- [376,389] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)O)C5=CC=CC=C15`
- [377] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)NC(=O)C)C5=CC=CC=C15`
- [379,397] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)NC(=O)C)C5=CC=CC=C15`
- [380] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)C(=O)CC)C5=CC=CC=C15`
- [381,393,417] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)OC)C5=CC=CC=C15`
- [382,394,401] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)OC)C5=CC=CC=C15`
- [383] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCC(O)C(=O)O)C5=CC=CC=C15`
- [384] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)OC(=O)C)C5=CC=CC=C15`
- [385,412] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)NC)C5=CC=CC=C15`
- [387] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCC(O)C(=O)N)C5=CC=CC=C15`
- [390] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)N(C)C)C5=CC=CC=C15`
- [392] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)N)C5=CC=CC=C15`
- [395] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)OC)C5=CC=CC=C15`
- [396,426,435] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCC(O)C(=O)NC)C5=CC=CC=C15`
- [399,413] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)N(C)C)C5=CC=CC=C15`
- [400] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)NC)C5=CC=CC=C15`
- [403] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COCC(O)C(=O)N(C)C)C5=CC=CC=C15`
- [404,427] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)NC(=O)CC)C5=CC=CC=C15`
- [405,420] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)OCC)C5=CC=CC=C15`
- [406] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)NC(=O)C)C5=CC=CC=C15`
- [407,416] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)NC)C5=CC=CC=C15`
- [408] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)O)C5=CC=CC=C15`
- [409] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)OC(=O)C)C5=CC=CC=C15`
- [411] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)NC(=O)C)C5=CC=CC=C15`
- [414] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)OC(=O)C)C5=CC=CC=C15`
- [421] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)NCC)C5=CC=CC=C15`
- [422] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)N(CC)C)C5=CC=CC=C15`
- [423] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)NC(=O)CC)C5=CC=CC=C15`
- [424] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CC(O)C(=O)N(C)CC)C5=CC=CC=C15`
- [425] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)C(=O)NCC)C5=CC=CC=C15`
- [428] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)N(C)CC)C5=CC=CC=C15`
- [432] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CO)NC(=O)OC)C5=CC=CC=C15`
- [441] `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4COC(=O)N(C)C(=O)C)C5=CC=CC=C15`

### 2.7 Series 002 — BAX / BAM7, B-format (VAR 501–682, 176 distinct)

Small-fragment scaffolds from VAR 501; the phenyl chain starts accumulating at
VAR 523 and grows ~13 chars per VAR. Two head scaffolds alternate (A on even VARs,
B on odd VARs from 562 on):

- Head A: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C…`
- Head B: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C…`

Each further phenyl ring appends `C<n>=CC=CC=C<n>` (13 chars). The table below gives
VAR, string length, head, and final ring number — the full string is head + the
phenyl chain to that ring. Boundary rows are quoted in full; the RDKit worker can
re-extract any full string from the source PDF.

VAR 501–540 (full strings, as extracted):

- [501] `C1CC2=CC=CC=C2N1CC(C3=CC=CC=C3)C=O`
- [502] `CC(C1=CC=CC=C1)N2CC3=CC=CC=C3C2`
- [503] `C1CCN(CC1)C(C2=CC=CC=C2)C=O`
- [504] `CC(C1=CC=CC=C1)C2=CN=CC=C2`
- [505] `C1CCC(CC1)C2=CC=CC=C2`
- [506] `C1CCC2C(CC1)C=CC=C2`
- [507] `CC(C1=CC=CC=C1)C=O`
- [508] `C1CCC(CN1)C2=CC=CC=C2`
- [509] `C1CC2C(CC1)C3=CC=CC=C3C2`
- [510] `C1CC2=CC=CC=C2C(CN1)C=O`
- [511] `CC(CN1CCC1)C2=CC=CC=C2`
- [512] `C1CC2=CC=CC=C2N1CC3=CC=CC=C3`
- [513] `C1CC2=CC=CC=C2C1(CN3CCOCC3)`
- [514] `C1CCC(CC1)N2C=CC=CC2`
- [515] `CC(C1=CC=CC=C1)C2N=CC=CC2`
- [516] `CC1=CC=CC=C1C2=CN=CC=C2`
- [517] `C1CC2=CC=CC=C2C(C1)N3CCOCC3`
- [518] `CC(C1=CC=CC=C1)C2CCC2`
- [519] `C1CCC(CC1)C2CCN2C3=CC=CC=C3`
- [520] `CC(C1=CC=CC=C1)C2C3=CC=CC=C3CC2`
- [521] `C1CCC(CC1)C2CN3CCOCC3C2`
- [522] `C1CCC(CN1)C2N=CC=CC2`
- [523] `CC(C1=CC=CC=C1)N2CCC(CC2)C3=CC=CC=C3`
- [524] `C1CCC2C(CC1)C3=CC=CC=C3CC2`
- [525] `CC(C1=CC=CC=C1)C2CCC(CC2)N3CCC(C3)C4=CC=CC=C4`
- [526] `C1CCC(C2=CC=CC=C2)CC1C3=CC=CC=C3`
- [527] `CC(C1=CC=CC=C1)C2C3=CC=CC=C3CCC2`
- [528] `C1CCC2C(CC1)C3=CC=CC=C3CC2N4CCOCC4`
- [529] `CC(C1=CC=CC=C1)C2N3CCC(C3)CC2`
- [530] `C1CCC2C(CC1)C3=CC=CC=C3CCC2`
- [531] `C1CCC(CC1)C2N3CCOCC3CC2`
- [532] `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCOCC4C3`
- [533] `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCOCC4`
- [534] `C1CCC(CC1)C2N3CCC(CC3)C4=CC=CC=C4C5=CC=CC=C5C2`
- [535] `CC(C1=CC=CC=C1)C2N3CCC(CC3)C4=CC=CC=C4C5=CC=CC=C5C2`
- [536] `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5`
- [537] `C1CCC(CC1)C2N3CCOCC3C4=CC=CC=C4C5=CC=CC=C5C2`
- [538] `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C3`
- [539] `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6`
- [540] `C1CCC(CC1)C2N3CCC(CC3)C4=CC=CC=C4C5=CC=CC=C5C6=CC=CC=C6C2`

VAR 541–561 (first 70 chars … last 40 chars, length):

- [541] len 71: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `C(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C3`
- [542] len 69: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7`
- [543] len 68: `C1CCC(CC1)C2N3CCC(CC3)C4=CC=CC=C4C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C2`
- [544] len 82: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `CC=C5C6=CC=CC=C6C7=CC=CC=C7C8=CC=CC=C8C3`
- [545] len 80: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `C=CC=C5C6=CC=CC=C6C7=CC=CC=C7C8=CC=CC=C8`
- [546] len 90: `C1CCC(CC1)C2N3CCC(CC3)C4=CC=CC=C4C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C8=C` … `CC=C6C7=CC=CC=C7C8=CC=CC=C8C9=CC=CC=C9C2`
- [547] len 106: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `=C7C8=CC=CC=C8C9=CC=CC=C9C10=CC=CC=C10C3`
- [548] len 104: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `CC=C7C8=CC=CC=C8C9=CC=CC=C9C10=CC=CC=C10`
- [549] len 114: `C1CCC(CC1)C2N3CCC(CC3)C4=CC=CC=C4C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C8=C` … `=C8C9=CC=CC=C9C10=CC=CC=C10C11=CC=CC=C11`
- [550] len 117: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `=C8C9=CC=CC=C9C10=CC=CC=C10C11=CC=CC=C11`
- [551] len 130: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `9C10=CC=CC=C10C11=CC=CC=C11C12=CC=CC=C12`
- [552] len 130: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `9C10=CC=CC=C10C11=CC=CC=C11C12=CC=CC=C12`
- [553] len 143: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `0C11=CC=CC=C11C12=CC=CC=C12C13=CC=CC=C13`
- [554] len 143: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `0C11=CC=CC=C11C12=CC=CC=C12C13=CC=CC=C13`
- [555] len 156: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `1C12=CC=CC=C12C13=CC=CC=C13C14=CC=CC=C14`
- [556] len 156: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `1C12=CC=CC=C12C13=CC=CC=C13C14=CC=CC=C14`
- [557] len 169: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `2C13=CC=CC=C13C14=CC=CC=C14C15=CC=CC=C15`
- [558] len 169: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `2C13=CC=CC=C13C14=CC=CC=C14C15=CC=CC=C15`
- [559] len 182: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `3C14=CC=CC=C14C15=CC=CC=C15C16=CC=CC=C16`
- [560] len 182: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `3C14=CC=CC=C14C15=CC=CC=C15C16=CC=CC=C16`
- [561] len 195: `C1CCC2C(CC1)C3=CC=CC=C3CCC2N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `4C15=CC=CC=C15C16=CC=CC=C16C17=CC=CC=C17`

VAR 562–682 (VAR | length | head | final ring). Head A = `CC(C1=CC=CC=C1)…`,
head B = `C1CCC2C(CC1)…` (full heads above). The phenyl chain runs to the final ring;
each ring adds 13 chars. Anomalies marked *.

| VAR | len | head | last ring | VAR | len | head | last ring |
|-----|-----|------|-----------|-----|-----|------|-----------|
| 562 | 195 | A | 17 | 622 | 624 | A | 50 |
| 563 | 208 | B | 18 | 623 | 624 | B | 50 |
| 564 | 208 | A | 18 | 624 | 637 | A | 51 |
| 565 | 221 | B | 19 | 625 | 637 | B | 51 |
| 566 | 221 | A | 19 | 626 | 650 | A | 52 |
| 567 | 234 | B | 20 | 627 | 663 | B | 53 |
| 568 | 234 | A | 20 | 628 | 663 | A | 53 |
| 569 | 247 | B | 21 | 629 | 676 | B | 54 |
| 570 | 247 | A | 21 | 630 | 689 | A | 55 |
| 571 | 260 | B | 22 | 631 | 702 | B | 56 |
| 572 | 260 | A | 22 | 632 | 702 | A | 56 |
| 573 | 273 | B | 23 | 633 | 715 | B | 57 |
| 574 | 273 | A | 23 | 634 | 336* | A | 28* |
| 575 | 286 | B | 24 | 634 | 715 | A | 57 |
| 576 | 149* | A | 14* | 635 | 728 | B | 58 |
| 577 | 299 | B | 25 | 636 | 728 | A | 58 |
| 578 | 299 | A | 25 | 637 | 741 | B | 59 |
| 579 | 312 | B | 26 | 638 | 741 | A | 59 |
| 580 | 312 | A | 26 | 639 | 754 | B | 60 |
| 581 | 325 | B | 27 | 640 | 754 | A | 60 |
| 582 | 325 | A | 27 | 641 | 767 | B | 61 |
| 583 | 338 | B | 28 | 642 | 780 | A | 62 |
| 584 | 338 | A | 28 | 643 | 780 | B | 62 |
| 585 | 351 | B | 29 | 644 | 793 | A | 63 |
| 586 | 351 | A | 29 | 645 | 793 | B | 63 |
| 587 | 364 | B | 30 | 646 | 806 | A | 64 |
| 588 | 364 | A | 30 | 647 | 806 | B | 64 |
| 589 | 377 | B | 31 | 648 | 819 | A | 65 |
| 590 | 377 | A | 31 | 649 | 767* | B | 61* |
| 591 | 390 | B | 32 | 650 | 780 | A | 62 |
| 592 | 390 | A | 32 | 651 | 793 | B | 63 |
| 593 | 403 | B | 33 | 652 | 806 | A | 64 |
| 594 | 403 | A | 33 | 653 | 806 | B | 64 |
| 595 | 416 | B | 34 | 654 | 819 | A | 65 |
| 596 | 416 | A | 34 | 655 | 832 | B | 66 |
| 597 | 429 | B | 35 | 656 | 832 | A | 66 |
| 598 | 429 | A | 35 | 657 | 845 | B | 67 |
| 599 | 442 | B | 36 | 658 | 845 | A | 67 |
| 600 | 455 | A | 37 | 659 | 858 | B | 68 |
| 601 | 468 | B | 38 | 660 | 871 | A | 69 |
| 602 | 468 | A | 38 | 661 | 871 | B | 69 |
| 603 | 481 | B | 39 | 662 | 884 | A | 70 |
| 604 | 481 | A | 39 | 663 | 884 | B | 70 |
| 605 | 494 | B | 40 | 664 | 897 | A | 71 |
| 606 | 494 | A | 40 | 665 | 884* | B | 70* |
| 607 | 507 | B | 41 | 666 | 910 | A | 72 |
| 608 | 507 | A | 41 | 667 | 923 | B | 73 |
| 609 | 520 | B | 42 | 668 | 936 | A | 74 |
| 610 | 520 | A | 42 | 669 | 936 | B | 74 |
| 611 | 533 | B | 43 | 670 | 949 | A | 75 |
| 612 | 546 | A | 44 | 671 | 949 | B | 75 |
| 613 | 546 | B | 44 | 672 | 962 | A | 76 |
| 614 | 559 | A | 45 | 673 | 962 | B | 76 |
| 615 | 559 | B | 45 | 674 | 975 | A | 77 |
| 616 | 572 | A | 46 | 675 | 975 | B | 77 |
| 617 | 585 | B | 47 | 676 | 988 | A | 78 |
| 618 | 585 | A | 47 | 677 | 988 | B | 78 |
| 619 | 598 | B | 48 | 678 | 1001 | A | 79 |
| 620 | 598 | A | 48 | 679 | 1001 | B | 79 |
| 621 | 611 | B | 49 | 680 | 1014 | A | 80 |
| | | | | 681 | 1014 | B | 80 |
| | | | | 682 | 1027 | A | 81 |

Anomalies in VAR 562–682: VAR 576 is truncated in the source (len 149, ends
mid-token `…C14=CC`); VAR 634 occurs twice — first truncated (len 336, ends
`…C28=CC=CC=C`), then complete (len 715); VAR 649 (len 767, ring 61) repeats
VAR 641's string exactly (chain reset); VAR 665 (len 884, ring 70) repeats VAR 663's
string exactly (chain reset). VAR 682 ends in a complete ring closure
(`…C81=CC=CC=C81`) — not truncated.

Boundary rows in full (first 70 … last 40):

- [562] len 195: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `4C15=CC=CC=C15C16=CC=CC=C16C17=CC=CC=C17`
- [576] len 149 (truncated): `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `C=CC=C11C12=CC=CC=C12C13=CC=CC=C13C14=CC`
- [634] len 336 (truncated, 1st occurrence): `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `C25C26=CC=CC=C26C27=CC=CC=C27C28=CC=CC=C`
- [634] len 715 (complete, 2nd occurrence): `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `4C55=CC=CC=C55C56=CC=CC=C56C57=CC=CC=C57`
- [682] len 1027: `CC(C1=CC=CC=C1)N2CCC(CC2)C3N4CCC(C4)C5=CC=CC=C5C6=CC=CC=C6C7=CC=CC=C7C` … `8C79=CC=CC=C79C80=CC=CC=C80C81=CC=CC=C81`

### 2.8 Series 002 — no-SMILES tail (VAR 683–700)

VAR 683–700 (18 labels + a duplicate VAR 683 label) are prose-only: Structural
Modifications / Therapeutic Insights / Pharmacokinetics / Potential Applications
sections with no SMILES strings. The document then moves to Series 003.

### 2.9 Series 003 — MCL-1 / S63845 (132 entries, 121 distinct)

Four blocks re-number VAR 001–010, so VAR 1–10 each carry up to four different
strings. **The parent "Drug X" SMILES is salbutamol-like
(`CC(C)NCC(O)c1ccc(O)c(c1)C(C)C`) — it is NOT S63845** (real S63845 is a much
larger MCL-1 inhibitor). VAR 71 has two strings (one complete, one backticked
truncated fragment).

Block 1 — intro, quinoxaline strings (VAR 01–05, 030, 300):

- [1] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CF3`
- [2] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4OCF3`
- [3] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4NO2`
- [4,30] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4SO2`
- [5] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4CO2`
- [300] `C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4ClO2`

Block 2 — E-inline, alanine-like with `@` stereo (VAR 001–010, 100):

- [1] `CC@HC(=O)O`
- [2] `CC@@HC(=O)O`
- [3] `CC(C(=O)O)N`
- [4] — not recovered in this pass (gap — the E-inline VAR 004 string was not captured; RDKit worker to re-extract)
- [5] `CCC@@HC(=O)O`
- [6] `CCC(N)C(=O)O`
- [7] `CC@HN`
- [8] `CC@@HN`
- [9] `CCC@HN`
- [10] `CCC@@HN`
- [100] `CC@HO`

Block 3 — name-block, acetaminophen-like (VAR 001–010, 100):

- [1] `CC(=O)NC1=CC=C(O)C=C1`
- [2] `CC(=O)NC1=CC=C(O)C=C1C`
- [3] `CC(=O)NC1=CC=C(OC)C=C1`
- [4] `CC(=O)NC1=CC=C(O)C=C1Cl`
- [5] `CC(=O)NC1=CC=C(O)C=C1F`
- [6] `CC(=O)NC1=CC=C(O)C=C1Br`
- [7] `CC(=O)NC1=CC=C(O)C=C1I`
- [8] `CC(=O)NC1=CC=C(O)C=C1N`
- [9] `CC(=O)NC1=CC=C(O)C=C1CN`
- [10] `CC(=O)NC1=CC=C(O)C=C1CO`
- [100] `CC(=O)NC1=CC=C(O)C=C1CF3`

Block 4 — Drug-X block, salbutamol-like (VAR 1–100):

- [1] `CC(C)NC(C)C(O)c1ccc(O)c(c1)C(C)C`
- [2] `CC(C)NCC(O)c1ccc(O)c(c1)C(Cl)C`
- [3] `CC(Cl)NCC(O)c1ccc(O)c(c1)C(C)C`
- [4] `CC(C)NCC(O)c1cc(O)c(c1)C(C)C`
- [5] `CC(C)NCC(O)c1ccc(Cl)c(c1)C(C)C`
- [6] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)Br`
- [7] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)F`
- [8] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)I`
- [9] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C#N`
- [10] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C=O`
- [11] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)O`
- [12] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)OC`
- [13] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)N`
- [14] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)S`
- [15] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)S(=O)`
- [16] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)S(=O)(=O)`
- [17] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)N(C)C`
- [18] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(O)`
- [19] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)O`
- [20] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)N`
- [21] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)N(C)C`
- [22] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)C`
- [23] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)S`
- [24] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)S(O)`
- [25] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)S(O)(=O)`
- [26] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)OCC`
- [27] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)NCC`
- [28] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)NCO`
- [29] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)OCN`
- [30] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)CN`
- [31] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)CCl`
- [32] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)CBr`
- [33] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)CF`
- [34] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)CI`
- [35] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)Cl`
- [36] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)Br`
- [37] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)F`
- [38] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)I`
- [39] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)CN`
- [40] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC`
- [41] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OC`
- [42] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCO`
- [43] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCO`
- [44,60] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCC`
- [45] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCCC`
- [46] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)ON`
- [47] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCN`
- [48] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCOC`
- [49] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCOC`
- [50] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCOC(O)C`
- [51] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCOC(O)C`
- [52] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCOCC`
- [53] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCCCCC`
- [54] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCCCO`
- [55] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCCCN`
- [56] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCOCCN`
- [57] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCCCNCO`
- [58] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCCN`
- [59] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCN`
- [61] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCCC(C)C`
- [62] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)C`
- [63] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)O`
- [64,70-71] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)N`
- [65,72] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)S`
- [66,75] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)Cl`
- [67,76] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)Br`
- [68] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)F`
- [69,77] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)I`
- [71] `` `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C `` — backtick-prefixed, truncated; second string under VAR 71 (the complete `…OCC(C)N` is listed above)
- [73] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)CN`
- [74] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)CO`
- [78] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)CNCl`
- [79] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)CNBr`
- [80] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)CNF`
- [81] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)CNO`
- [82] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COO`
- [83] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCO`
- [84] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)CON`
- [85] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCl`
- [86] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COBr`
- [87] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COI`
- [88] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCN`
- [89] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCOC`
- [90] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCON`
- [91] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCOCl`
- [92] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCOBr`
- [93] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCOI`
- [94] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCONCl`
- [95] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCONBr`
- [96] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)CONF`
- [97] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCONO`
- [98] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCONOCl`
- [99] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCONOBr`
- [100] `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C)COCONOF`

### 2.10 Series 004 — Lisinopril-like, then Atorvastatin-like (196 entries, 21 distinct)

**Flag: Series 004 is reused for two different parent drugs.** VAR 1–100 is a
lisinopril-like block; VAR 001–200 is an atorvastatin block. Neither parent SMILES
is the real drug: the lisinopril-like `C1CC(CN1C(=O)C@@HNC(=O)C@HN)C(=O)O` lacks
lisinopril's phenylpropyl chain, and the atorvastatin parent
`CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=CC=C4C5=CC=CC=C5`
is NOT real atorvastatin (wrong structure).

Lisinopril-like block (VAR 1–100):

- [1-3,5-20,100] `C1CC(CN1C(=O)C@@HNC(=O)C@HN)C(=O)O`
- [4,21-35] `C1CC(CN1C(=O)C@@HNC(=O)C@HN)C(=O)F`
- [36-48] `C1CC(CN1C(=O)C@@HNC(=O)C@HN)C(=O)Br`
- [49-100] `C1CC(CN1C(=O)C@@HNC(=O)C@HN)C(=O)Cl`
- [58] `C1CC(CN1C(=O)[C@@H](CC2` — truncated fragment from a cut-off ChatGPT turn ("You said: continue" follows); the complete `…C(=O)Cl` string for VAR 58 appears later in the document
- [87] `C1CC(CN1C(=O)[C@@H` — truncated fragment, same note; complete `…C(=O)Cl` string for VAR 87 appears later

Atorvastatin block (VAR 001–200), parent SMILES as stated in the document:

- [1] `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(=O)O)C4=CC=C(C=C4)C5=CC=CC=C5`
- [2] `CCC(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=CC=C4C5=CC=CC=C5`
- [3] `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)O)C4=CC=C(C=C4)C5=CC=CC=C5`
- [4] `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=C(C=C4)C5=CC=CC=C5`
- [100] `CCC(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)O)C4=CC=C(C=C4)C5=CC=CC=C5`
- [101] `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=C(C=C4)C5=CC=CN=C5`
- [102,107,109,122,127,129,134,136,138,140,159,163,171,173] `CCC(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)O)C4=CC=C(C=C4)C5=CC=NC=C5`
- [103,123] `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=CC=C4C5=CC=CC=N5`
- [104,120,150-151,153,167,179,181,183,185,187,189,191,197,199] `CCC(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=C(C=C4)C5=CC=CN=C5`
- [105,125,132,152,166] `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)O)C4=CC=C(C=C4)C5=CC=NC=C5`
- [106,108,110,121,126,128,130,133,135,137,139,154,156,158,160,162,164,168,170,172,174,176,178,180,186,188,198] `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=CC=C4C5=CC=CN=C5`
- [124,193,195] `CCC(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)O)C4=CC=C(C=C4)C5=CC=CN=C5`
- [131,155,157,161,165,169,175] `CCC(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=C(C=C4)C5=CC=NC=C5`
- [177] `` `CCC(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)O) `` — backtick-prefixed; complete apart from the backtick
- [182,184,190,192,194,196,200] `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)O)C4=CC=CC=C4C5=CC=CN=C5`

### 2.11 Series 005 — Riluzole (100 entries, 70 distinct)

Parent strings are benzamide-like, e.g.
`CN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2)C3=CC=CC=C3` — **NOT real riluzole**
(real riluzole is a benzothiazole). VAR 006/008/010 wrap with single-char
continuations. "(Continue this pattern until reaching 100 variations)" appears
after VAR 010, but VAR 011–100 labels with SMILES do follow. VAR 26–100 cycle
elements as terminal acyl groups (As, Sb, Bi, Ge, Sn, Si, Ti, Zr, Hf, Cr, Mo, W,
Mn, Tc, Re, Os, Ru, Rh, Pd, Pt, Cu, Ag, Au, Zn, Cd, Hg, Pb, Ni, Co, Fe, V, Sc, Y,
Nb, Ta, Ir, Tl, Te, Se) — chemically absurd substitutions, recorded as written.

- [1] `CN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2)C3=CC=CC=C3`
- [2] `CCN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2)C3=CC=CC=C3`
- [3] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3`
- [4,7] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3C`
- [5] `CN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2C)C3=CC=CC=C3`
- [6] `CN(CC1=CC=CC=C1C)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3`
- [8] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C`
- [9] `CCN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3`
- [10] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C`
- [11] `CCN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3C`
- [12] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)F`
- [13] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)Cl`
- [14] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)Br`
- [15] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)I`
- [16] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C#N`
- [17] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C=C`
- [18] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C=O`
- [19] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)C`
- [20] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)N`
- [21] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)O`
- [22] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)S`
- [23] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)P`
- [24] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Se`
- [25] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Te`
- [26,78,86,94] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)As`
- [27,71,79,87,95] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Sb`
- [28,70] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Bi`
- [29] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Ge`
- [30,74,82,90,98] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Sn`
- [31,77,85,93] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Si`
- [32] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Ti`
- [33] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Zr`
- [34] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Hf`
- [35] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Cr`
- [36] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Mo`
- [37] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)W`
- [38] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Mn`
- [39] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Tc`
- [40] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Re`
- [41] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Os`
- [42] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Ru`
- [43] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Rh`
- [44] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Pd`
- [45] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Pt`
- [46] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Cu`
- [47,65] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Ag`
- [48] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Au`
- [49] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Zn`
- [50,68] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Cd`
- [51] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Hg`
- [52] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Pb`
- [53] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Ni`
- [54] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Co`
- [55] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Fe`
- [56] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)V`
- [57] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Sc`
- [58] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Y`
- [59] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Nb`
- [60] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Ta`
- [61] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Ir`
- [62] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Pt`
- [63] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Cu`
- [64] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Zn`
- [66] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Hg`
- [67] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Au`
- [69] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Tl`
- [72,80,88,96] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Te`
- [73,81,89,97] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Se`
- [75,83,91,99] `CN(CC1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Pb`
- [76,84,92,100] `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=C(C=C3)C(=O)Ge`

Note: VAR 005/006 differ only in methyl placement (VAR 005 = methyl on the
anilide phenyl; VAR 006 = methyl on the benzyl phenyl) — verify against the source
if the distinction matters; the two strings were captured as written above.

### 2.12 Series 006 — Pregabalin (200 entries, 140 distinct)

Pregabalin-like piperidine scaffold `CC(C)C1CCC(CN1)C(=O)O` and variants.
**This is NOT real pregabalin** (real pregabalin: `CC(C)CC(N)CC(=O)O`) — the
series uses a cyclic piperidine-2-carboxylic-acid scaffold. VAR 023+ SMILES sit
on the line after a bare label.

- [1,11] `CC(C)C1CCC(CN1)C(=O)O`
- [2] `CCC(C)C1CC(CN1)C(=O)O`
- [3] `CC(C)C1CC(CN1)C(=O)N`
- [4] `CC(C)C1CC(CN1)C(=O)C`
- [5] `CC(C)C1CCC(C1)C(=O)O`
- [6] `CC(C)C1CC(CN1C)C(=O)O`
- [7] `CC(C)C1CC(CN1)C(=O)N(C)C`
- [8] `CC(C)C1CC(CN1)C(=O)OCC`
- [9] `CC(C)C1CC(CN1C)C(=O)OC`
- [10] `CC(C)C1CCC(CN1)C(=O)N`
- [12] `CC(C)C1CC(CN1)C(=O)OC`
- [13] `CC(C)C1CC(CN1)C(=O)OCH3`
- [14] `CC(C)C1CC(CN1)C(=O)NC`
- [15] `CC(C)C1CC(CN1C)C(=O)OC2`
- [16] `CC(C)C1CC(CN1)C(=O)NH`
- [17] `CC(C)C1CC(CN1)C(=O)NH2`
- [18] `CC(C)C1CC(CN1)C(=O)NC2`
- [19] `CC(C)C1CCC(CN1)C(=O)OCH3`
- [20] `CC(C)C1CC(CN1)C(=O)OCC2`
- [21] `CC(C)C1CC(CN1C)C(=O)OC3`
- [22] `CC(C)C1CC(CN1)C(=O)OC2C`
- [23] `CC(C)C1CCC(CN1)C(=O)NCH3`
- [24] `CC(C)C1CC(CN1C)C(=O)NC3`
- [25] `CC(C)C1CC(CN1)C(=O)N(CH3)2`
- [26] `CC(C)C1CC(CN1)C(=O)NCH2CH3`
- [27] `CC(C)C1CC(CN1C)C(=O)N(CH3)2`
- [28] `CC(C)C1CCC(CN1C)C(=O)OCH2CH3`
- [29,80,91,102,113] `CC(C)C1CC(CN1)C(=O)OCH2CH3`
- [30] `CC(C)C1CC(CN1C)C(=O)NCH3`
- [31] `CC(C)C1CC(CN1)C(=O)OC2H5`
- [32] `CC(C)C1CC(CN1)C(=O)NCH3CH2`
- [33] `CC(C)C1CC(CN1C)C(=O)N(CH2)2`
- [34] `CC(C)C1CCC(CN1)C(=O)OC2H5`
- [35] `CC(C)C1CC(CN1)C(=O)NCH(CH3)2`
- [36] `CC(C)C1CC(CN1C)C(=O)OC3H7`
- [37] `CC(C)C1CC(CN1)C(=O)OC(CH3)3`
- [38] `CC(C)C1CCC(CN1)C(=O)OC3H7`
- [39] `CC(C)C1CC(CN1)C(=O)OCH(CH3)2`
- [40] `CC(C)C1CC(CN1)C(=O)N(CH3)C2H5`
- [41] `CC(C)C1CC(CN1)C(=O)OC2(CH3)3`
- [42,46] `CC(C)C1CC(CN1C)C(=O)OCH2CH(CH3)2`
- [43] `CC(C)C1CCC(CN1)C(=O)NCH(CH3)2`
- [44] `CC(C)C1CC(CN1C)C(=O)OC(CH3)2H5`
- [45,53] `CC(C)C1CC(CN1)C(=O)OC2H4CH3`
- [47,55] `CC(C)C1CCC(CN1)C(=O)OC3H7CH3`
- [48,57] `CC(C)C1CC(CN1)C(=O)OC2(CH3)3H7`
- [49,58] `CC(C)C1CC(CN1)C(=O)NCH3C(CH3)3`
- [50,56] `CC(C)C1CC(CN1)C(=O)OCH2CH(CH3)2`
- [51] `CC(C)C1CC(CN1C)C(=O)NCH2CH2CH3`
- [52] `CC(C)C1CCC(CN1)C(=O)OC3H8CH2`
- [54] `CC(C)C1CC(CN1C)C(=O)OCH(CH3)2CH3`
- [59] `CC(C)C1CCC(CN1C)C(=O)OC3H7CH2`
- [60] `CC(C)C1CC(CN1)C(=O)OC2H4(CH3)3`
- [61] `CC(C)C1CC(CN1)C(=O)OCH2CH2CH3`
- [62,73,84,95,106,117] `CC(C)C1CC(CN1)C(=O)OC(CH3)3CH2`
- [63] `CC(C)C1CCC(CN1)C(=O)OCH2CH(CH3)3`
- [64,75,86,97,108,119] `CC(C)C1CC(CN1)C(=O)OC2H5CH(CH3)2`
- [65] `CC(C)C1CC(CN1)C(=O)NCH(CH3)2CH3`
- [66] `CC(C)C1CC(CN1C)C(=O)OCH(CH3)3`
- [67,78,89,100,111] `CC(C)C1CC(CN1)C(=O)OCH2CH2(CH3)2`
- [68] `CC(C)C1CC(CN1)C(=O)OC3H8CH(CH3)3`
- [69] `CC(C)C1CC(CN1C)C(=O)OCH2CH3`
- [70,81,92,103,114] `CC(C)C1CC(CN1)C(=O)OC3H7CH(CH3)2`
- [71,82,93,104,115] `CC(C)C1CCC(CN1)C(=O)NCH(CH3)3`
- [72,83,94,105,116,143,178] `CC(C)C1CC(CN1C)C(=O)OCH2CH2CH3`
- [74,85,96,107,118] `CC(C)C1CCC(CN1)C(=O)OCH2CH(CH3)3`
- [76,87,98,109,120] `CC(C)C1CC(CN1C)C(=O)NCH(CH3)2CH3`
- [77,88,99,110] `CC(C)C1CC(CN1)C(=O)OCH(CH3)3`
- [79,90,101,112] `CC(C)C1CC(CN1C)C(=O)OC3H8CH(CH3)3`
- [121] `CC(C)C1CC(CN1)C(=O)OC(CH3)2CH2CH3`
- [122] `CC(C)C1CC(CN1)C(=O)OC2CH5CH(CH3)CH2`
- [123] `CC(C)C1CC(CN1)C(=O)OCH2CH2CH2CH3`
- [124] `CC(C)C1CC(CN1)C(=O)NCH2CH2(CH3)2`
- [125] `CC(C)C1CCC(CN1)C(=O)OC2CH5(CH3)2CH2`
- [126] `CC(C)C1CC(CN1)C(=O)OC3H8CH(CH3)CH2`
- [127] `CC(C)C1CC(CN1C)C(=O)OC2CH2CH(CH3)CH3`
- [128] `CC(C)C1CC(CN1)C(=O)OC3H7CH(CH3)CH2`
- [129] `CC(C)C1CC(CN1)C(=O)OC3H6CH2(CH3)CH2`
- [130] `CC(C)C1CC(CN1C)C(=O)NCH2CH2CH(CH3)2`
- [131] `CC(C)C1CC(CN1)C(=O)OCH(CH3)CH2CH3`
- [132] `CC(C)C1CCC(CN1)C(=O)OC3H7CH2(CH3)CH2`
- [133] `CC(C)C1CC(CN1)C(=O)OCH2CH3CH(CH3)2`
- [134] `CC(C)C1CC(CN1)C(=O)OC3H6CH3(CH3)CH2`
- [135] `CC(C)C1CC(CN1C)C(=O)OCH2CH2(CH3)CH2`
- [136] `CC(C)C1CC(CN1)C(=O)OCH(CH2)2CH3`
- [137] `CC(C)C1CC(CN1)C(=O)OC3H6CH2CH(CH3)2`
- [138] `CC(C)C1CC(CN1C)C(=O)OCH2CH2(CH3)CH3`
- [139] `CC(C)C1CC(CN1)C(=O)OC3H5CH2CH(CH3)2`
- [140] `CC(C)C1CC(CN1)C(=O)OC3H6CH3CH2(CH3)2`
- [141] `CC(C)C1CC(CN1)C(=O)OC(CH3)2C2H5`
- [142] `CC(C)C1CC(CN1)C(=O)OC3H7CH(CH3)CH3`
- [144] `CC(C)C1CC(CN1)C(=O)OC2H4CH3`
- [145,191] `CC(C)C1CC(CN1)C(=O)OC3H7CH2CH2`
- [146,198] `CC(C)C1CC(CN1C)C(=O)OCH2CH(CH3)CH2`
- [147] `CC(C)C1CCC(CN1)C(=O)OC(CH3)CH3`
- [148] `CC(C)C1CC(CN1)C(=O)OC3H6CH3`
- [149] `CC(C)C1CC(CN1C)C(=O)OC2H5CH2CH3`
- [150] `CC(C)C1CC(CN1)C(=O)OCH3CH3`
- [151,185] `CC(C)C1CC(CN1)C(=O)OC2H6CH(CH3)CH2`
- [152] `CC(C)C1CC(CN1C)C(=O)OC3H8CH3`
- [153] `CC(C)C1CC(CN1)C(=O)OCH(CH2)3`
- [154,180] `CC(C)C1CC(CN1)C(=O)OC2H7CH2CH3`
- [155] `CC(C)C1CC(CN1C)C(=O)OCH3CH2`
- [156] `CC(C)C1CC(CN1)C(=O)OC3H7CH(CH3)2`
- [157,174] `CC(C)C1CC(CN1)C(=O)OC3H6CH2CH3`
- [158] `CC(C)C1CC(CN1C)C(=O)OC2H5CH3`
- [159,167] `CC(C)C1CCC(CN1)C(=O)OCH2CH(CH3)CH3`
- [160] `CC(C)C1CC(CN1)C(=O)OC3H7CH3`
- [161] `CC(C)C1CCC(CN1)C(=O)OCH(CH3)CH2CH3`
- [162] `CC(C)C1CC(CN1)C(=O)OC2H5CH(CH3)CH2`
- [163,186] `CC(C)C1CC(CN1C)C(=O)OCH2CH(CH3)CH3`
- [164] `CC(C)C1CC(CN1)C(=O)OCH(CH2CH3)CH3`
- [165] `CC(C)C1CC(CN1)C(=O)OC3H6CH(CH3)CH3`
- [166] `CC(C)C1CC(CN1C)C(=O)OC2H7CH(CH3)CH2`
- [168] `CC(C)C1CC(CN1)C(=O)OC3H8CH3`
- [169] `CC(C)C1CC(CN1C)C(=O)OC2H5CH(CH2)3`
- [170] `CC(C)C1CC(CN1)C(=O)OCH2CH2CH(CH3)`
- [171] `CC(C)C1CC(CN1)C(=O)OC3H7CH(CH2)3`
- [172] `CC(C)C1CC(CN1C)C(=O)OC2H5CH3CH3`
- [173] `CC(C)C1CC(CN1)C(=O)OCH2CH(CH3)2`
- [175] `CC(C)C1CC(CN1C)C(=O)OC2H6CH3`
- [176] `CC(C)C1CC(CN1)C(=O)OCH3CH2CH2`
- [177] `CC(C)C1CC(CN1)C(=O)OC2H6CH(CH3)CH3`
- [179] `CC(C)C1CC(CN1)C(=O)OC3H7CH(CH2)3`
- [181] `CC(C)C1CC(CN1)C(=O)OCH2CH(CH2)3`
- [182] `CC(C)C1CC(CN1)C(=O)OC2H8CH(CH3)CH3`
- [183] `CC(C)C1CC(CN1C)C(=O)OC3H7CH2CH3`
- [184] `CC(C)C1CC(CN1)C(=O)OCH(CH2CH2)3`
- [187] `CC(C)C1CC(CN1)C(=O)OCH3CH(CH2)3`
- [188] `CC(C)C1CC(CN1)C(=O)OC2H5CH2CH3`
- [189] `CC(C)C1CC(CN1C)C(=O)OC3H6CH(CH3)`
- [190] `CC(C)C1CC(CN1)C(=O)OCH(CH3)CH3`
- [192] `CC(C)C1CC(CN1C)C(=O)OC2H6CH(CH3)`
- [193] `CC(C)C1CC(CN1)C(=O)OCH(CH2CH3)CH2`
- [194] `CC(C)C1CC(CN1)C(=O)OC3H8CH(CH3)`
- [195] `CC(C)C1CC(CN1C)C(=O)OC2H7CH3`
- [196] `CC(C)C1CC(CN1)C(=O)OCH3CH(CH2CH3)`
- [197] `CC(C)C1CC(CN1)C(=O)OC3H6CH3CH2`
- [199] `CC(C)C1CC(CN1)C(=O)OCH(CH2)3CH3`
- [200] `CC(C)C1CC(CN1)C(=O)OC2H8CH(CH2)3`

### 2.13 Series 007 — recently-expired HIV drug (13 entries, 2 distinct real SMILES)

Tenofovir-like phosphonate strings. VAR 001, 002 and 100 also appear as
`[Generated SMILES N]` placeholders (label-only lines; the real SMILES for
VAR 001/002 appear on later lines). The document ends with ChatGPT twice
refusing to continue generating long SMILES lists ("technical limitations of
this platform", text lines ~7166 and ~7193).

- [1] `CC(CCOCP(=O)(COC(=O)N)COC(=O)N1CCC(O)(C1)C2=NC=CC(=N2)N)O`
- [2–10] `CC(CCOCP(=O)(COC(=O)N1CCC(O)(C1)C2=NC=CC(=N2)N)COC(=O)N)O`
- [1] `[Generated SMILES 1]` — placeholder, no real SMILES
- [2] `[Generated SMILES 2]` — placeholder, no real SMILES
- [100] `[Generated SMILES 100]` — placeholder, no real SMILES

---

## 3. Document 3 — Venetoclax comparison log

**Source:** `~/workspace/user/files/Venetoclax_SMILES____CC_C__C_C__O_NC1_CC_C_C_C1_N2C_NC3_C2C_CC__C3.pdf`
(46,084 B, 26 pages, 1,000 text lines). ChatGPT comparison log ("Venetoclax
SMILES" vs generated hypotheticals, "250 hypothetical SMILES").

### 3.1 The six distinct strings (223 SMILES blocks total)

| # | SMILES | × | MW pairings in doc |
|---|--------|---|--------------------|
| A | `CC1=CC=CC=C1C(=O)NC2=CC=CC=C2C(=O)N3CC4CCNCC4C3` | 75 | 342.41 ×71 |
| B | `CC1=CC=CC=C1C(=O)NC2=CC=CC=C2C(=O)N3CCNCC3` | 69 | 296.34 ×68, 426.55 ×1 |
| C | `CCC1=CC=CC=C1C(=O)NC2=CC=CC=C2C(=O)N3CCN(CC3)C4=CC=CC=C4` | 67 | 426.55 ×67 |
| D | `CCC1=CC=CC=C1C(=O)NC2=CC=CC=C2C(=O)N3CCN(C3)C4=CC=CC=C4` | 2 | 426.55 ×2 |
| F (fragment) | `(C)C(=O)NC1=CC=C(C=C1)N2C=NC3=C2C=CC(=C3)C(=O)NC4=CC=C(C=C4)OC(F)(F)F` | 9 | none (no following MW) |
| G (full) | `` `CC(C)(C)C(=O)NC1=CC=C(C=C1)N2C=NC3=C2C=CC(=C3)C(=O)NC4=CC=C(C=C4)OC(F)(F)F` `` | 1 | none (no following MW) |

### 3.2 MW pairings and conflicts

- MW lines: 210 with numbers (342.41 ×71, 426.55 ×70, 296.34 ×69) + 1 MW line
  with no number.
- Pairings: A–342.41 ×71, B–296.34 ×68, C–426.55 ×67, D–426.55 ×2, **B–426.55 ×1**
  (the first comparison labels B as 426.55), **A–296.34 ×1** — **the same SMILES is
  given two different MWs**. 13 blocks have no following MW (9 fragments + 1 full
  + 3 generated in comparison examples).
- "Venetoclax SMILES" label ×10; `CC(C)(C)C(=O)` ×1; `(C)C(=O)NC1=` ×11.

### 3.3 The "250 hypothetical SMILES" claim — rebutted

The document repeatedly claims "250 hypothetical SMILES" ("continue list to
include 250", "Continuing from 151 to 250", "from 188 to 250"), but only **3
unique generated structures** (A, B, C) cycle through the 223 blocks. The other
three strings are a typo variant (D), a truncated fragment (F), and one
backticked full string (G). **Do not cite 250 as a real count.**

### 3.4 The "Venetoclax SMILES" is a fragment, NOT venetoclax

The stated "Venetoclax SMILES" (F) is truncated — missing the leading `CC` of
the tert-butyl group (`(C)C(=O)…` instead of `CC(C)(C)C(=O)…`). The full form
(G) appears once, backticked, in Example Comparison 4. **Neither is real
venetoclax** (real venetoclax: C45H50ClN7O7S, MW ~868). The document's stated
venetoclax MW 868.44 does not match the given SMILES. The three generated
structures (A, B, C) are benzamide–piperazine structures, not venetoclax-like.

---

## 4. Cross-document integrity flags (consolidated)

| # | Flag | Documents |
|---|------|-----------|
| 1 | **AGI-183 name collision**: Doc 1 AGI-183 = CRBN-binding FLIP inhibitor, pro-apoptotic, cancer (SMILES `…C4=CC=C(Br)C=C4`, MW 353.32, IC50 0.5). ALS paper's AGI-183 = BCL-XL stabilizer, anti-apoptotic, neuroprotective. Same name, opposite mechanism. Do NOT merge. | Doc 1 §1.3 |
| 2 | **Catalog is 413, not 10**: parent brief said AGI-001–AGI-010; full text layer has AGI-001–AGI-413 contiguous. | Doc 1 §1.1/§1.5 |
| 3 | **Same SMILES, different stated metadata** (6 SMILES; Br and CF3 each have 4 metadata variants). No single SMILES maps to one MW/LogP/ΔG/IC50/goodness set. | Doc 1 §1.6 |
| 4 | **AGI-376 number reused** for two different compounds (p. 360 CI, MW 397.20; p. 363 CBr, MW 371.21). | Doc 1 §1.5 |
| 5 | **Doc 1 ranges differ from parent's read**: MW max 397.20 (not 371), LogP max 4.5 (not 4.2), ΔG max −7.4 (not −7.8). IC50 0.3–1.0 and goodness 0.75–0.91 confirmed. | Doc 1 §1.1 |
| 6 | **All POC/POM claims are UNVERIFIED DOCUMENT CLAIMS** (in vitro IC50s, in vivo xenograft shrinkage, Western blots, co-IP — no citations). | Doc 1 §1.8 |
| 7 | **Picture-pages gap refuted as stated**: 0 `/Subtype /Image` and 0 `/XObject` in all three PDFs; 449/450 Doc-1 pages carry ≥300 chars of extractable text; vector check found 4 total path-painting operators vs 59,084 text operators. There are no raster images and no vector structure drawings. | Doc 1 §1.9 |
| 8 | **Doc 2 is 7 series, not 3** (Series 004–007 also present). | Doc 2 §2.1 |
| 9 | **Header error**: `ABT-199- BAX Activators (BAM7)` conflates ABT-199/venetoclax with BAM7. | Doc 2 §2.2 |
| 10 | **Series 004 reused for two different parent drugs** (lisinopril-like, then atorvastatin-like). | Doc 2 §2.10 |
| 11 | **Parent-drug SMILES are NOT the real drugs**: S1 venetoclax-like, S2 BAM7, S3 S63845 (salbutamol-like "Drug X"), S4 lisinopril/atorvastatin, S5 riluzole, S6 pregabalin, Doc 3 "Venetoclax SMILES" fragment. | Doc 2, Doc 3 |
| 12 | **Doc 2 scaffold drift**: S2 indole scaffold through VAR500 → small fragments from VAR501 → runaway repetitive phenyl-chain strings VAR 562–682 (len 195→1027, +13 chars/VAR), with chain resets at VAR 649 and VAR 665. | Doc 2 §2.7 |
| 13 | **Doc 3 "250" claim rebutted**: only 3 unique generated structures cycle through 223 blocks. | Doc 3 §3.3 |
| 14 | **Same SMILES given two different MWs** (Doc 3: B as 296.34 and 426.55; A as 342.41 and 296.34). | Doc 3 §3.2 |
| 15 | **Truncated/fragment SMILES**: Doc 1 broken AGI-405 fragment; S2 VAR 576 truncated, VAR 634 first truncated then complete; S3 VAR 71 backticked truncated; S4 VAR 58/87 cut-off-turn fragments; Doc 3 "Venetoclax" fragment (9×). | throughout |
| 16 | **Placeholders**: 11 exact `'...'` lines in Doc 2; 3 `[Generated SMILES N]` placeholders in S7; Doc 3's "250" numbering is placeholder-like repetition. | Doc 2, Doc 3 |
| 17 | **Doc 1 ends truncated**: p. 450 ends mid-sentence; AGI-413 core metadata is complete. | Doc 1 §1.9 |
| 18 | **Doc 2 ends in ChatGPT refusals** (S7: twice refused to continue generating long SMILES lists). | Doc 2 §2.13 |

## 5. RDKit handoff notes (for the validation worker)

- **Doc 1, S2 VAR 167**: string ends with stray "Y"
  (`…C5=CC=CC=C15Y`) — extraction artifact; check whether the intended string
  ends at `…C15`.
- **S2 VAR 576**: truncated at len 149, ends mid-token `…C14=CC`.
- **S2 VAR 634**: appears twice — first truncated (len 336), then complete (len 715).
  Use the complete one.
- **Doc 1 AGI-376**: two different compounds share the number (CI vs CBr) — treat
  as two entries.
- **Doc 1 same-SMILES metadata variants** (§1.6): Br and CF3 each have 4 stated
  metadata sets — do not collapse to one.
- **S3 E-inline VAR 4**: string not recovered in this pass — re-extract.
- **S4 VAR 58/87**: truncated fragments from a cut-off ChatGPT turn; complete
  `…C(=O)Cl` strings appear later in the document — use those.
- **Doc 3 string D**: typo variant of C (`CCN(C3)` instead of `CCN(CC3)`) — missing
  a carbon in the piperazine ring.
- **Doc 3 string F**: truncated fragment — missing leading `CC`; the full form (G)
  appears once.
- **F string has two written forms** in Doc 1 (`C4=CC=CC=C4F` vs
  `C4=CC=C(F)C=C4`) — same molecule, two strings; kept as two distinct strings
  in this inventory.
- **Element-soup tails** (S5 VAR 26–100): terminal acyl groups cycle through
  As, Sb, Bi, Ge, Sn, Si, Ti, Zr, Hf, Cr, Mo, W, Mn, Tc, Re, Os, Ru, Rh, Pd, Pt,
  Cu, Ag, Au, Zn, Cd, Hg, Pb, Ni, Co, Fe, V, Sc, Y, Nb, Ta, Ir, Tl, Te, Se —
  expect many to fail validation; recorded as written.

---

*End of inventory. No SMILES were chemically validated in this pass — that is the
RDKit worker's job. No structures were guessed from images (there were no images).
All POC/POM claims are UNVERIFIED DOCUMENT CLAIMS.*
