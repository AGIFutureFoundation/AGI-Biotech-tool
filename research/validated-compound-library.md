# Validated Compound Library — Bio Research Expansion

**Published:** validation output in this repo's `research/` folder.
**Validation date: 7 November 2026. Validator: RDKit validation worker (subagent).**
**Rebuilt 2026-11-07 (second pass): the §3 table in the first pass was defective
(MW/formula/LogP mismatches, sort breaks, duplicate canonicals, spurious tail
rows). This version is rebuilt from the validation script's output
(`validate_library.py`, re-run 2026-11-07) and every row was re-verified by
re-parsing the table with RDKit — see §10.**
**Inputs:** `raw-smiles-inventory.md` (1,586 lines), `smiles-smarts-reference.md`,
`compound-dacomilertib.md`, `compound-agi183.md` — all under
`~/workspace/your_files/bio-research-expansion/`.
**Tool: RDKit 2026.09.1** (`python3 -c "from rdkit import Chem"` verified this pass).
Canonical SMILES below are **RDKit canonical SMILES from RDKit 2026.09.1** — never
compare them as strings against Daylight unique SMILES from any source document
(reference §6: same family of algorithm, different tie-breaking; a string mismatch
is not a structural difference).

**No treatment, cure, diagnosis, or medical-device claims are made in this document.**
Every entry is a research compound-library record. A pattern hit is a structural
feature match, not evidence of biological activity. All POC/POM/IC50/ΔG/goodness
values from the source documents are **UNVERIFIED DOCUMENT CLAIMS** and are labelled
as such wherever they appear next to RDKit-recomputed values.

## Method (reference §8 rules applied)

1. **Extraction.** **766 input occurrences** (bullets + special cases) yielding
   **728 distinct input strings**, plus: Doc 1 full strings reconstructed from the
   §1.4 terminal groups on the stated core `C1=CN=C2C(=N1)C(=CC=C2)C3=NC=CN3` (+ the
   §1.2 full strings, which dedup against the reconstructions); the Doc 2 Series 002
   phenyl-chain strings VAR 541–682 reconstructed from the validated generative rule
   (see below); S3 E-inline VAR 4 recovered from the source PDF text layer
   (inventory §2.9 gap); the S3 "Drug X" parent `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C`
   from the §2.9 intro prose (not a bullet — missed in the first rebuild); S4 [177]
   (backticked string with a trailing space — missed in the first rebuild by a
   segment-strip bug in the extractor, fixed this pass).
   Excluded as non-entries: 4 prose fragment mentions (`C4=CC=CC=C4F`,
   `C4=CC=C(F)C=C4`, `CC(C)(C)C(=O)`, `C3=NC4=CC=CC=C4N3C5=CC=CC=C5` — terminal/ring
   fragments quoted in §1.1/§1.2/§3.2 prose, not library entries) and the real-pregabalin
   SMILES cited for comparison in §2.12 (`CC(C)CC(N)CC(=O)O` — a reference structure,
   not a series entry; it is used in the parent check in §7 instead).
2. **Series 002 chain reconstruction (validated, not assumed).** VAR 541–682 strings are
   head + `C{k}=CC=CC=C{k}` per phenyl ring (k = 8…N), with the trailing closure read off
   the inventory's own first/last-40 text: A-head VAR 541/544/547 end `C3`; C-head VAR
   543/546 end `C2` (closes ring 2 — an earlier `C3` guess for these two was wrong and
   failed to parse; the inventory's full 68-char VAR 543 string ends `C2`); B-head strings
   and all later strings end with a ring closure and no tail. Length check: **0
   mismatches** across all 142 chains (21/21 VAR 541–561 and 121/121 VAR 562–682 match
   the inventory lengths exactly).
   VAR 576 is the 149-char prefix of its ring-14 build (truncated mid-token, ends
   `…C14=CC`); VAR 634 1st occurrence is the 336-char prefix of the complete 715-char
   build; VAR 649 repeats VAR 641's string exactly; VAR 665 repeats VAR 663's.
3. **Parse.** Every distinct input string parsed in RDKit with sanitisation. No string
   was silently repaired: a string that fails to parse is listed in §5 INVALID with
   a failure reason (SYNTAX = formula-style fragment — bare H / bare-digit subscript;
   UNCLOSED-RING = a genuine ring-closure digit never closed; RING-DIGIT-DUP = bare
   two-digit ring numbers ≥ 10; KEKULIZE = RDKit cannot Kekulé-assign; TRUNCATED =
   cut off mid-token; AROMATIC-NONRING = aromatic atoms that never form a ring).
   **Tautomer policy (§8 rule 4a): each tautomer kept as its own row; no tautomer
   normalisation.** Chirality: absence of `@`/`@@` means unspecified, never racemic
   (§8 rule 5). Alternative valid valence models accepted (§3.4.4); only genuinely
   invalid valence rejected.
4. **Dedup.** Dedup key is the RDKit canonical SMILES. Two input strings → one canonical
   SMILES = one library row, with the extra input string(s) recorded as DUPLICATE (§6).
   Cross-document duplicates collapse the same way (e.g. S1/S2/S3 quinoxaline strings).
5. **Properties.** MW = RDKit `Descriptors.MolWt` (average molecular weight); LogP = RDKit
   Crippen `MolLogP`. Formula = RDKit `CalcMolFormula`. Document-claimed MW/LogP are
   shown only as "doc-claimed" next to the recomputed values, never as validated.
6. **Parents.** The seven claimed parent drugs were checked against PubChem PUG REST
   (name lookup, 2026-11-07): the PubChem record's SMILES was parsed in RDKit and its
   RDKit-canonical form compared with the RDKit-canonical form of the document's claimed
   parent SMILES (§7). **VERIFIED requires a match; no claimed parent matched, so
   VERIFIED = 0.**
7. **SMARTS.** Each §7 pattern was parsed in RDKit first (all 17 parse), then run against
   the RDKit-canonicalised validated structures (§8 rule 7). Co-occurrence patterns P-03
   and P-12 were run as intersections of the component queries (§8).

## How to read the table (§3)

- **ID** — `L-001`…`L-336`, sorted by RDKit MW ascending. One row per unique canonical
  structure. Structure-less candidate rows (DacomiLertib, AGI-183 paper) are `X-01`/`X-02`
  in §4, not in this table.
- **Canonical SMILES** — RDKit 2026.09.1 canonical SMILES. Input SMILES as written is
  shown in Notes only where it differs materially (Kekulé input, duplicate writings).
- **MW / LogP** — RDKit-recomputed (see Method 5). Anything labelled "doc-claimed" is an
  unverified document value.
- **Prov.** — provenance label: `HYPOTHETICAL` (parsed + unique + untested) or `VERIFIED`
  (parsed + parent confirmed vs PubChem). There are **no VERIFIED rows** in this pass
  (see §7). `INVALID` and `DUPLICATE` strings are not rows here; they are in §5/§6.
- **Kekulé note** — **209 rows** were written Kekulé-style in the source (input has no
  lowercase aromatic atoms) and canonicalise to aromatic form in RDKit. That is the
  normal Daylight conversion (reference §3.4.2: "Kekulé input is converted to aromatic
  internally"), not a data error. **0 rows** had aromatic input become non-aromatic in
  RDKit (no aromaticity-perception divergence requiring human review on that axis).

## 3. Validated library table — 336 unique canonical structures

| ID | Canonical SMILES | Formula | MW (RDKit) | LogP (RDKit) | Source(s) / Entry IDs | Notes |
|----|------------------|---------|-----------:|-------------:|-----------------------|-------|
| L-001 | `CC(N)C(=O)O` | C3H7NO2 | 89.09 | -0.58 | S3: [3] |  |
| L-002 | `CCC(N)C(=O)O` | C4H9NO2 | 103.12 | -0.19 | S3: [6] |  |
| L-003 | `CC(C=O)c1ccccc1` | C9H10O | 134.18 | 1.99 | S2-B: [507] | Kekulé input → aromatic canonical (normal conversion) |
| L-004 | `C1=CC2CCCCCC2C=C1` | C11H16 | 148.25 | 3.31 | S2-B: [506] |  |
| L-005 | `CC(=O)Nc1ccc(O)cc1` | C8H9NO2 | 151.16 | 1.35 | S3: [1] | Kekulé input → aromatic canonical (normal conversion) |
| L-006 | `CC(=O)C1CNC(C(C)C)C1` | C9H17NO | 155.24 | 1.21 | S6: [4] |  |
| L-007 | `CC(C)C1CCC(C(=O)O)C1` | C9H16O2 | 156.22 | 2.14 | S6: [5] |  |
| L-008 | `CC(C)C1CC(C(N)=O)CN1` | C8H16N2O | 156.23 | 0.11 | S6: [3] |  |
| L-009 | `CC(c1ccccc1)C1CCC1` | C12H16 | 160.26 | 3.59 | S2-B: [518] | Kekulé input → aromatic canonical (normal conversion) |
| L-010 | `c1ccc(C2CCCCC2)cc1` | C12H16 | 160.26 | 3.73 | S2-B: [505] | Kekulé input → aromatic canonical (normal conversion) |
| L-011 | `c1ccc(C2CCCNC2)cc1` | C11H15N | 161.25 | 2.15 | S2-B: [508] | Kekulé input → aromatic canonical (normal conversion) |
| L-012 | `C1=CCN(C2CCCCC2)C=C1` | C11H17N | 163.26 | 2.70 | S2-B: [514] |  |
| L-013 | `C1=CCC(C2CCCNC2)N=C1` | C10H16N2 | 164.25 | 1.39 | S2-B: [522] |  |
| L-014 | `CC(=O)Nc1ccc(O)cc1C` | C9H11NO2 | 165.19 | 1.66 | S3: [2] | Kekulé input → aromatic canonical (normal conversion) |
| L-015 | `COc1ccc(NC(C)=O)cc1` | C9H11NO2 | 165.19 | 1.65 | S3: [3] | Kekulé input → aromatic canonical (normal conversion) |
| L-016 | `CC(=O)Nc1ccc(O)cc1N` | C8H10N2O2 | 166.18 | 0.93 | S3: [8] | Kekulé input → aromatic canonical (normal conversion) |
| L-017 | `CC(=O)Nc1ccc(O)cc1F` | C8H8FNO2 | 169.15 | 1.49 | S3: [5] | Kekulé input → aromatic canonical (normal conversion) |
| L-018 | `Cc1ccccc1-c1cccnc1` | C12H11N | 169.23 | 3.06 | S2-B: [516] | Kekulé input → aromatic canonical (normal conversion) |
| L-019 | `CC(C)C1CCC(C(N)=O)CN1` | C9H18N2O | 170.26 | 0.50 | S6: [10] |  |
| L-020 | `CNC(=O)C1CNC(C(C)C)C1` | C9H18N2O | 170.26 | 0.37 | S6: [14] |  |
| L-021 | `CC(C)C1CC(C(=O)O)CN1C` | C9H17NO2 | 171.24 | 1.05 | S6: [6] |  |
| L-022 | `CC(C)C1CCC(C(=O)O)CN1` | C9H17NO2 | 171.24 | 1.10 | S6: [1,11] | Doc-claimed pregabalin parent (piperidine) — MISMATCH vs PubChem pregabalin (§7) |
| L-023 | `CCC(C)C1CC(C(=O)O)CN1` | C9H17NO2 | 171.24 | 1.10 | S6: [2] |  |
| L-024 | `COC(=O)C1CNC(C(C)C)C1` | C9H17NO2 | 171.24 | 0.79 | S6: [12] |  |
| L-025 | `c1ccc2c(c1)CC1CCCCC21` | C13H16 | 172.27 | 3.52 | S2-B: [509] | Kekulé input → aromatic canonical (normal conversion) |
| L-026 | `O=CC1CNCCc2ccccc21` | C11H13NO | 175.23 | 1.11 | S2-B: [510] | Kekulé input → aromatic canonical (normal conversion) |
| L-027 | `CC(CN1CCC1)c1ccccc1` | C12H17N | 175.28 | 2.50 | S2-B: [511] | Kekulé input → aromatic canonical (normal conversion) |
| L-028 | `CC(=O)Nc1ccc(O)cc1CN` | C9H12N2O2 | 180.21 | 0.81 | S3: [9] | Kekulé input → aromatic canonical (normal conversion) |
| L-029 | `CC(=O)Nc1ccc(O)cc1CO` | C9H11NO3 | 181.19 | 0.84 | S3: [10] | Kekulé input → aromatic canonical (normal conversion) |
| L-030 | `CC(c1ccccc1)c1cccnc1` | C13H13N | 183.25 | 3.23 | S2-B: [504] | Kekulé input → aromatic canonical (normal conversion) |
| L-031 | `CC(C)C1CC(C(=O)N(C)C)CN1` | C10H20N2O | 184.28 | 0.71 | S6: [7] |  |
| L-032 | `CC(c1ccccc1)C1CC=CC=N1` | C13H15N | 185.27 | 3.19 | S2-B: [515] | Kekulé input → aromatic canonical (normal conversion) |
| L-033 | `CCOC(=O)C1CNC(C(C)C)C1` | C10H19NO2 | 185.27 | 1.18 | S6: [8] |  |
| L-034 | `COC(=O)C1CC(C(C)C)N(C)C1` | C10H19NO2 | 185.27 | 1.14 | S6: [9] |  |
| L-035 | `CC(=O)Nc1ccc(O)cc1Cl` | C8H8ClNO2 | 185.61 | 2.00 | S3: [4] |  |
| L-036 | `c1ccc2c(c1)CCC1CCCCCC21` | C15H20 | 200.32 | 4.30 | S2-B: [524] | Kekulé input → aromatic canonical (normal conversion) |
| L-037 | `O=CC(c1ccccc1)N1CCCCC1` | C13H17NO | 203.28 | 2.41 | S2-B: [503] | Kekulé input → aromatic canonical (normal conversion) |
| L-038 | `c1ccc(CN2CCc3ccccc32)cc1` | C15H15N | 209.29 | 3.25 | S2-B: [512] | Kekulé input → aromatic canonical (normal conversion) |
| L-039 | `C1CCC(C2CC3COCCN3C2)CC1` | C13H23NO | 209.33 | 2.29 | S2-B: [521] |  |
| L-040 | `C1CCC(C2CCC3COCCN32)CC1` | C13H23NO | 209.33 | 2.43 | S2-B: [531] |  |
| L-041 | `c1ccc2c(c1)CCCC1CCCCCC21` | C16H22 | 214.35 | 4.69 | S2-B: [530] | Kekulé input → aromatic canonical (normal conversion) |
| L-042 | `CC(c1ccccc1)C1CCC2CCN1C2` | C15H21N | 215.34 | 3.27 | S2-B: [529] | Kekulé input → aromatic canonical (normal conversion) |
| L-043 | `c1ccc(N2CCC2C2CCCCC2)cc1` | C15H21N | 215.34 | 3.85 | S2-B: [519] | Kekulé input → aromatic canonical (normal conversion) |
| L-044 | `c1ccc2c(c1)CCC2CN1CCOCC1` | C14H19NO | 217.31 | 2.05 | S2-B: [513] | Kekulé input → aromatic canonical (normal conversion) |
| L-045 | `c1ccc2c(c1)CCCC2N1CCOCC1` | C14H19NO | 217.31 | 2.40 | S2-B: [517] | Kekulé input → aromatic canonical (normal conversion) |
| L-046 | `CC(c1ccccc1)C1CCc2ccccc21` | C17H18 | 222.33 | 4.52 | S2-B: [520] | Kekulé input → aromatic canonical (normal conversion) |
| L-047 | `CC(c1ccccc1)N1Cc2ccccc2C1` | C16H17N | 223.32 | 3.76 | S2-B: [502] | Kekulé input → aromatic canonical (normal conversion) |
| L-048 | `CC(=O)Nc1ccc(O)cc1Br` | C8H8BrNO2 | 230.06 | 2.11 | S3: [6] |  |
| L-049 | `CC(c1ccccc1)C1CCCc2ccccc21` | C18H20 | 236.36 | 4.91 | S2-B: [527] | Kekulé input → aromatic canonical (normal conversion) |
| L-050 | `c1ccc(C2CCCC(c3ccccc3)C2)cc1` | C18H20 | 236.36 | 5.13 | S2-B: [526] | Kekulé input → aromatic canonical (normal conversion) |
| L-051 | `CC(C)NCC(O)c1ccc(O)c(C(C)C)c1` | C14H23NO2 | 237.34 | 2.55 | S3: [intro (Drug X parent)] | Doc-claimed S63845 parent (salbutamol-like) — MISMATCH vs PubChem S63845 (§7) |
| L-052 | `CC(C)NCC(O)c1ccc(O)c(C(C)N)c1` | C13H22N2O2 | 238.33 | 1.44 | S3: [13] |  |
| L-053 | `CC(C)NCC(O)c1ccc(O)c(C(C)O)c1` | C13H21NO3 | 239.31 | 1.48 | S3: [19] |  |
| L-054 | `CC(C)NCC(O)c1ccc(O)c(C(C)F)c1` | C13H20FNO2 | 241.31 | 2.45 | S3: [7] |  |
| L-055 | `CC(C)NCC(O)c1ccc(O)c(C(C)C#N)c1` | C14H20N2O2 | 248.33 | 2.05 | S3: [9] |  |
| L-056 | `CC(C)NCC(O)c1ccc(O)c(C(C)C=O)c1` | C14H21NO3 | 251.33 | 1.73 | S3: [10] |  |
| L-057 | `O=CC(CN1CCc2ccccc21)c1ccccc1` | C17H17NO | 251.33 | 3.03 | S2-B: [501] | Kekulé input → aromatic canonical (normal conversion) |
| L-058 | `CC(C)NC(C)C(O)c1ccc(O)c(C(C)C)c1` | C15H25NO2 | 251.37 | 2.94 | S3: [1] |  |
| L-059 | `CC(C)NCC(O)c1ccc(O)c(C(C)CN)c1` | C14H24N2O2 | 252.36 | 1.49 | S3: [30] |  |
| L-060 | `CC(C)NCC(O)c1ccc(O)c(C(C)CO)c1` | C14H23NO3 | 253.34 | 1.52 | S3: [18] |  |
| L-061 | `COC(C)c1cc(C(O)CNC(C)C)ccc1O` | C14H23NO3 | 253.34 | 2.13 | S3: [12] |  |
| L-062 | `CC(C)NCC(O)c1ccc(O)c(C(C)CF)c1` | C14H22FNO2 | 255.33 | 2.50 | S3: [33] |  |
| L-063 | `CC(C)NCC(O)c1ccc(O)c(C(C)S)c1` | C13H21NO2S | 255.38 | 2.41 | S3: [14] |  |
| L-064 | `CC(C)NCC(O)c1ccc(Cl)c(C(C)C)c1` | C14H22ClNO | 255.79 | 3.49 | S3: [5] |  |
| L-065 | `CC(C)NCC(O)c1ccc(O)c(C(C)Cl)c1` | C13H20ClNO2 | 257.76 | 2.72 | S3: [2] |  |
| L-066 | `CC(Cl)NCC(O)c1ccc(O)c(C(C)C)c1` | C13H20ClNO2 | 257.76 | 2.72 | S3: [3] |  |
| L-067 | `CC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C15H23NO3 | 265.35 | 2.12 | S3: [22] |  |
| L-068 | `CC(c1ccccc1)N1CCC(c2ccccc2)CC1` | C19H23N | 265.40 | 4.63 | S2-B: [523] | Kekulé input → aromatic canonical (normal conversion) |
| L-069 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(N)=O)c1` | C14H22N2O3 | 266.34 | 1.01 | S3: [20] |  |
| L-070 | `CC(C)NCC(O)c1ccc(O)c(C(C)N(C)C)c1` | C15H26N2O2 | 266.38 | 2.05 | S3: [17] |  |
| L-071 | `CCNC(C)c1cc(C(O)CNC(C)C)ccc1O` | C15H26N2O2 | 266.38 | 2.09 | S3: [27] |  |
| L-072 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)O)c1` | C14H21NO4 | 267.32 | 1.61 | S3: [11] |  |
| L-073 | `CCOC(C)c1cc(C(O)CNC(C)C)ccc1O` | C15H25NO3 | 267.37 | 2.52 | S3: [26] |  |
| L-074 | `CC(C)NCC(O)c1ccc(O)c(C(C)NCO)c1` | C14H24N2O3 | 268.36 | 1.02 | S3: [28] |  |
| L-075 | `CC(C)NCC(O)c1ccc(O)c(C(C)OCN)c1` | C14H24N2O3 | 268.36 | 1.42 | S3: [29] |  |
| L-076 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)F)c1` | C14H20FNO3 | 269.32 | 2.02 | S3: [37] |  |
| L-077 | `CC(C)NCC(O)c1ccc(O)c(C(C)SO)c1` | C13H21NO3S | 271.38 | 2.69 | S3: [24] |  |
| L-078 | `CC(C)NCC(O)c1ccc(O)c(C(C)[SH]=O)c1` | C13H21NO3S | 271.38 | 1.43 | S3: [15] |  |
| L-079 | `CC(C)NCC(O)c1ccc(O)c(C(C)CCl)c1` | C14H22ClNO2 | 271.79 | 2.77 | S3: [31] |  |
| L-080 | `c1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C17H12N4 | 272.31 | 3.48 | Doc1: [AGI-01,phenyl] | Doc1 key phenyl; doc-claimed MW 301.32 / LogP 3.1 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-081 | `c1cc(-c2nccn2-c2ccncc2)c2nccnc2c1` | C16H11N5 | 273.30 | 2.88 | Doc1: [AGI-06,pyridyl] | Doc1 key pyridyl; doc-claimed MW 286.32 / LogP 2.8 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-082 | `CC(=O)Nc1ccc(O)cc1I` | C8H8INO2 | 277.06 | 1.96 | S3: [7] | Kekulé input → aromatic canonical (normal conversion) |
| L-083 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)CN)c1` | C15H24N2O3 | 280.37 | 1.05 | S3: [39] |  |
| L-084 | `COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C15H23NO4 | 281.35 | 1.70 | S3: [41] |  |
| L-085 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)ON)c1` | C14H22N2O4 | 282.34 | 0.94 | S3: [46] |  |
| L-086 | `c1ccc(-c2nc3ccccc3nc2-c2ccccc2)cc1` | C20H14N2 | 282.35 | 4.96 | S1: [1] | Kekulé input → aromatic canonical (normal conversion) |
| L-087 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)S)c1` | C14H21NO3S | 283.39 | 1.98 | S3: [23] |  |
| L-088 | `c1ccc2c(c1)CC(N1CCOCC1)C1CCCCCC21` | C19H27NO | 285.43 | 3.61 | S2-B: [528] | Kekulé input → aromatic canonical (normal conversion) |
| L-089 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)Cl)c1` | C14H20ClNO3 | 285.77 | 2.29 | S3: [35] |  |
| L-090 | `CC(C)NCC(O)c1ccc(O)c(C(C)S(=O)O)c1` | C13H21NO4S | 287.38 | 1.71 | S3: [25] |  |
| L-091 | `CC(C)NCC(O)c1ccc(O)c(C(C)[SH](=O)=O)c1` | C13H21NO4S | 287.38 | 1.10 | S3: [16] |  |
| L-092 | `Oc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C17H12N4O | 288.31 | 3.19 | Doc1: [AGI-05,phenol] | Doc1 key phenol; doc-claimed MW 307.31 / LogP 2.5 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-093 | `O=c1cc(-n2ccnc2-c2cccc3nccnc23)cco1` | C16H10N4O2 | 290.28 | 2.44 | Doc1: [AGI-04,lactone] | Doc1 key lactone; doc-claimed MW 331.32 / LogP 2.9 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-094 | `Fc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C17H11FN4 | 290.30 | 3.62 | Doc1: [F] | Doc1 key F; doc-claimed MW 319.32 / LogP 3.4 (doc-claimed, unvalidated); para-F isomer — distinct from the ortho-F (F-alt) row; inventory "same molecule" claim is wrong (§10); Kekulé input → aromatic canonical (normal conversion) |
| L-095 | `Fc1ccccc1-n1ccnc1-c1cccc2nccnc12` | C17H11FN4 | 290.30 | 3.62 | Doc1: [F-alt,AGI-03] | Doc1 key F-alt; doc-claimed MW 319.32 / LogP 3.4 (doc-claimed, unvalidated); ortho-F isomer — distinct from the para-F (F) row; inventory "same molecule" claim is wrong (§10); Kekulé input → aromatic canonical (normal conversion) |
| L-096 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)N(C)C)c1` | C16H26N2O3 | 294.40 | 1.62 | S3: [21] |  |
| L-097 | `CCOC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C16H25NO4 | 295.38 | 2.09 | S3: [40] |  |
| L-098 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCN)c1` | C15H24N2O4 | 296.37 | 0.99 | S3: [47] |  |
| L-099 | `c1ccc(C2=NC(c3ccccc3)N=C2c2ccccc2)cc1` | C21H16N2 | 296.37 | 4.68 | S1: [2] | Kekulé input → aromatic canonical (normal conversion) |
| L-100 | `N#Cc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C18H11N5 | 297.32 | 3.35 | Doc1: [C#N,AGI-07] | Doc1 key C#N; doc-claimed MW 302.32 / LogP 3.2, 3.3 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-101 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCO)c1` | C15H23NO5 | 297.35 | 1.02 | S3: [42] |  |
| L-102 | `Nc1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C20H15N3 | 297.36 | 4.55 | S1: [3]; S2-A: [2] | Kekulé input → aromatic canonical (normal conversion) |
| L-103 | `c1ccc(C2=NC(c3ccccn3)N=C2c2ccccc2)cc1` | C20H15N3 | 297.36 | 4.07 | S1: [4] | Kekulé input → aromatic canonical (normal conversion) |
| L-104 | `c1ccc(C2=NC(c3cccnc3)N=C2c2ccccc2)cc1` | C20H15N3 | 297.36 | 4.07 | S1: [5] | Kekulé input → aromatic canonical (normal conversion) |
| L-105 | `Oc1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C20H14N2O | 298.35 | 4.67 | S1: [2]; S2-A: [1] | Kekulé input → aromatic canonical (normal conversion) |
| L-106 | `c1ccc2c(c1)CCC(N1CCOCC1)C1CCCCCC21` | C20H29NO | 299.46 | 4.00 | S2-B: [533] | Kekulé input → aromatic canonical (normal conversion) |
| L-107 | `Fc1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C20H13FN2 | 300.34 | 5.10 | S1: [4]; S2-A: [3] | Kekulé input → aromatic canonical (normal conversion) |
| L-108 | `CC(c1ccccc1)N1CCC(C2CC3COCCN32)CC1` | C19H28N2O | 300.45 | 2.93 | S2-B: [532] | Kekulé input → aromatic canonical (normal conversion) |
| L-109 | `NCc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C18H15N5 | 301.35 | 2.94 | Doc1: [CN] | Doc1 key CN; doc-claimed MW 305.31 / LogP 2.5 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-110 | `CC(C)NCC(O)c1ccc(O)c(C(C)Br)c1` | C13H20BrNO2 | 302.21 | 2.88 | S3: [6] |  |
| L-111 | `Clc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C17H11ClN4 | 306.76 | 4.14 | Doc1: [Cl,AGI-09] | Doc1 key Cl; doc-claimed MW 317.76 / LogP 3.7, 3.8 (doc-claimed, unvalidated) |
| L-112 | `CC1=C(c2c(-c3ccccc3)[nH]c3ccccc23)c2ccccc21` | C23H17N | 307.40 | 6.13 | S2-A: [1] | Kekulé input → aromatic canonical (normal conversion) |
| L-113 | `CCCOC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H27NO4 | 309.41 | 2.48 | S3: [44,60] |  |
| L-114 | `O=Cc1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C21H14N2O | 310.36 | 4.78 | S1: [19] | Kekulé input → aromatic canonical (normal conversion) |
| L-115 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCCN)c1` | C16H26N2O4 | 310.39 | 1.03 | S3: [59] |  |
| L-116 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCCO)c1` | C16H25NO5 | 311.38 | 1.06 | S3: [43] |  |
| L-117 | `COCOC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C16H25NO5 | 311.38 | 1.67 | S3: [48] |  |
| L-118 | `c1ccc(NC2N=C(c3ccccc3)C(c3ccccc3)=N2)cc1` | C21H17N3 | 311.39 | 4.37 | S1: [3] | Kekulé input → aromatic canonical (normal conversion) |
| L-119 | `CC(C)NCC(O)c1ccc(O)c(C(C)CBr)c1` | C14H22BrNO2 | 316.24 | 2.92 | S3: [32] |  |
| L-120 | `CN(Cc1ccc(C(=O)Nc2ccccc2)cc1)c1ccccc1` | C21H20N2O | 316.40 | 4.58 | S5: [1,3] | Doc-claimed riluzole parent (benzamide-like) — MISMATCH vs PubChem riluzole (§7); Also written as: `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3`; `CN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2)C3=CC=CC=C3`; Kekulé input → aromatic canonical (normal conversion) |
| L-121 | `Clc1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C20H13ClN2 | 316.79 | 5.62 | S1: [5]; S2-A: [4,30] |  |
| L-122 | `ClCc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C18H13ClN4 | 320.78 | 4.22 | Doc1: [CCl] | Doc1 key CCl; doc-claimed MW 331.21 / LogP 3.7 (doc-claimed, unvalidated) |
| L-123 | `c1ccc(-n2c(-c3cccc4nccnc34)nc3ccccc32)cc1` | C21H14N4 | 322.37 | 4.64 | Doc1: [AGI-02,benzimidazole] | Doc1 key benzimidazole; doc-claimed MW 371.40 / LogP 4.2 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-124 | `Cc1ccccc1C(=O)Nc1ccccc1C(=O)N1CCNCC1` | C19H21N3O2 | 323.40 | 2.29 | Doc3: [B] | Doc3 B; doc-claimed MW 296.34 (x68; once 426.55 — same SMILES, two MWs); Kekulé input → aromatic canonical (normal conversion) |
| L-125 | `CC(C)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29NO4 | 323.43 | 2.73 | S3: [62] |  |
| L-126 | `CCCCOC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29NO4 | 323.43 | 2.87 | S3: [45] |  |
| L-127 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCCCN)c1` | C17H28N2O4 | 324.42 | 1.42 | S3: [58] |  |
| L-128 | `CC(N)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H28N2O4 | 324.42 | 1.42 | S3: [64,70-71] |  |
| L-129 | `CC1=C(c2c(-c3ccccc3F)[nH]c3ccccc23)c2ccccc21` | C23H16FN | 325.39 | 6.27 | S2-A: [2] | Kekulé input → aromatic canonical (normal conversion) |
| L-130 | `CC(O)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H27NO5 | 325.41 | 1.45 | S3: [63] |  |
| L-131 | `COCCOC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H27NO5 | 325.41 | 1.72 | S3: [49] |  |
| L-132 | `CC(F)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H26FNO4 | 327.40 | 2.43 | S3: [68] |  |
| L-133 | `CN(C)Cc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C20H19N5 | 329.41 | 3.54 | Doc1: [CN(C)C] | Doc1 key CN(C)C; doc-claimed MW 335.35 / LogP 3.2 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-134 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)Br)c1` | C14H20BrNO3 | 330.22 | 2.45 | S3: [36] |  |
| L-135 | `CCN(Cc1ccc(C(=O)Nc2ccccc2)cc1)c1ccccc1` | C22H22N2O | 330.43 | 4.97 | S5: [2,9] | Also written as: `CCN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3`; `CCN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2)C3=CC=CC=C3`; Kekulé input → aromatic canonical (normal conversion) |
| L-136 | `Cc1ccc(NC(=O)c2ccc(CN(C)c3ccccc3)cc2)cc1` | C22H22N2O | 330.43 | 4.88 | S5: [8] | Kekulé input → aromatic canonical (normal conversion) |
| L-137 | `Cc1ccccc1NC(=O)c1ccc(CN(C)c2ccccc2)cc1` | C22H22N2O | 330.43 | 4.88 | S5: [5,4,7] | Also written as: `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3C`; `CN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2C)C3=CC=CC=C3`; Kekulé input → aromatic canonical (normal conversion) |
| L-138 | `CC1=C(c2c(-c3ccccc3C#N)[nH]c3ccccc23)c2ccccc21` | C24H16N2 | 332.41 | 6.00 | S2-A: [43,101,179,191,203,216,229,259,271,283,296,312] | Kekulé input → aromatic canonical (normal conversion) |
| L-139 | `CC(c1ccccc1)C1CCC(N2CCC(c3ccccc3)C2)CC1` | C24H31N | 333.52 | 5.84 | S2-B: [525] | Kekulé input → aromatic canonical (normal conversion) |
| L-140 | `CN(Cc1ccc(C(=O)Nc2ccc(F)cc2)cc1)c1ccccc1` | C21H19FN2O | 334.39 | 4.71 | S5: [12] | Kekulé input → aromatic canonical (normal conversion) |
| L-141 | `CC1=C(c2c(-c3ccccc3C=N)[nH]c3ccccc23)c2ccccc21` | C24H18N2 | 334.42 | 6.12 | S2-A: [305] | Kekulé input → aromatic canonical (normal conversion) |
| L-142 | `CC1=C(c2c(-c3ccccc3C=O)[nH]c3ccccc23)c2ccccc21` | C24H17NO | 335.41 | 5.94 | S2-A: [17,42,88,129,174,200,221,237,254,280] | Kekulé input → aromatic canonical (normal conversion) |
| L-143 | `CC(C)CCOC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H31NO4 | 337.46 | 3.12 | S3: [61] |  |
| L-144 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCCCCN)c1` | C18H30N2O4 | 338.45 | 1.81 | S3: [55] |  |
| L-145 | `CC(CN)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H30N2O4 | 338.45 | 1.67 | S3: [73] |  |
| L-146 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCCCCO)c1` | C18H29NO5 | 339.43 | 1.84 | S3: [54] |  |
| L-147 | `CC(CO)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29NO5 | 339.43 | 1.70 | S3: [74] |  |
| L-148 | `CCOCCOC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29NO5 | 339.43 | 2.11 | S3: [52] |  |
| L-149 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCOC(C)O)c1` | C17H27NO6 | 341.40 | 1.38 | S3: [51] |  |
| L-150 | `CN(Cc1ccc(C(=O)Nc2ccc(C#N)cc2)cc1)c1ccccc1` | C22H19N3O | 341.41 | 4.45 | S5: [16] | Kekulé input → aromatic canonical (normal conversion) |
| L-151 | `CC(S)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H27NO4S | 341.47 | 2.39 | S3: [65,72] |  |
| L-152 | `CC1=C(c2c(-c3ccccc3Cl)[nH]c3ccccc23)c2ccccc21` | C23H16ClN | 341.84 | 6.78 | S2-A: [3] |  |
| L-153 | `CC(Cl)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H26ClNO4 | 343.85 | 2.70 | S3: [66,75] |  |
| L-154 | `Cc1ccc(NC(=O)c2ccc(CN(C)Cc3ccccc3)cc2)cc1` | C23H24N2O | 344.46 | 4.88 | S5: [10] | Kekulé input → aromatic canonical (normal conversion) |
| L-155 | `Cc1ccccc1CN(C)Cc1ccc(C(=O)Nc2ccccc2)cc1` | C23H24N2O | 344.46 | 4.88 | S5: [6] | Kekulé input → aromatic canonical (normal conversion) |
| L-156 | `c1ccc2c(c1)CC(C1CCCCC1)N1CCC(CC1)c1ccccc1-2` | C25H31N | 345.53 | 6.04 | S2-B: [534] | Kekulé input → aromatic canonical (normal conversion) |
| L-157 | `c1ccc2c(c1)CC(C1CCCCC1)N1CCOCC1c1ccccc1-2` | C24H29NO | 347.50 | 5.23 | S2-B: [537] | Kekulé input → aromatic canonical (normal conversion) |
| L-158 | `CC(C)NCC(O)c1ccc(O)c(C(C)I)c1` | C13H20INO2 | 349.21 | 2.92 | S3: [8] |  |
| L-159 | `CC1=C(c2c(-c3ccccc3C=NN)[nH]c3ccccc23)c2ccccc21` | C24H19N3 | 349.44 | 5.42 | S2-A: [28,76,87,100,128,138,146,172,197,220,234,253,277] | Kekulé input → aromatic canonical (normal conversion) |
| L-160 | `CC1=C(c2c(-c3ccccc3C(N)=O)[nH]c3ccccc23)c2ccccc21` | C24H18N2O | 350.42 | 5.23 | S2-A: [307] | Kekulé input → aromatic canonical (normal conversion) |
| L-161 | `CC1=C(c2c(-c3ccccc3CCN)[nH]c3ccccc23)c2ccccc21` | C25H22N2 | 350.47 | 5.63 | S2-A: [311,336] | Kekulé input → aromatic canonical (normal conversion) |
| L-162 | `Brc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C17H11BrN4 | 351.21 | 4.25 | Doc1: [Br,AGI-08] | Doc1 key Br; doc-claimed MW 353.32, 363.32 / LogP 3.5, 3.9, 4.1 (doc-claimed, unvalidated); Doc1 AGI-183 (catalog, CRBN/FLIP) — DO NOT MERGE with AGI-183 paper row X-02 (§4/§10) |
| L-163 | `CC1=C(c2c(-c3ccccc3C(C)O)[nH]c3ccccc23)c2ccccc21` | C25H21NO | 351.45 | 6.18 | S2-A: [318,337] | Also written as: `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(C)O)C5=CC=CC=C15`; `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(O)C)C5=CC=CC=C15`; Kekulé input → aromatic canonical (normal conversion) |
| L-164 | `COCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C25H21NO | 351.45 | 6.27 | S2-A: [314] | Kekulé input → aromatic canonical (normal conversion) |
| L-165 | `CCCCCCOC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C20H33NO4 | 351.49 | 3.65 | S3: [53] |  |
| L-166 | `CC1=C(c2c(-c3ccccc3CS)[nH]c3ccccc23)c2ccccc21` | C24H19NS | 353.49 | 6.56 | S2-A: [304] | Kekulé input → aromatic canonical (normal conversion) |
| L-167 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCCOCCN)c1` | C18H30N2O5 | 354.45 | 1.05 | S3: [56] |  |
| L-168 | `CC(CNO)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H30N2O5 | 354.45 | 1.69 | S3: [81] |  |
| L-169 | `CC(CON)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H30N2O5 | 354.45 | 1.60 | S3: [84] |  |
| L-170 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCCOC(C)O)c1` | C18H29NO6 | 355.43 | 1.43 | S3: [50] |  |
| L-171 | `CC(COO)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29NO6 | 355.43 | 2.20 | S3: [82] |  |
| L-172 | `CC1=C(c2c(-c3ccccc3CCl)[nH]c3ccccc23)c2ccccc21` | C24H18ClN | 355.87 | 6.87 | S2-A: [52,81,95,110,141,149,158,177,193,214,231,240,257,273,293-294] |  |
| L-173 | `CC(CNF)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29FN2O4 | 356.44 | 2.18 | S3: [80] |  |
| L-174 | `C=Cc1ccc(NC(=O)c2ccc(CN(C)Cc3ccccc3)cc2)cc1` | C24H24N2O | 356.47 | 5.21 | S5: [17] | Kekulé input → aromatic canonical (normal conversion) |
| L-175 | `CN(Cc1ccccc1)Cc1ccc(C(=O)Nc2ccc(C=O)cc2)cc1` | C23H22N2O2 | 358.44 | 4.38 | S5: [18] | Kekulé input → aromatic canonical (normal conversion) |
| L-176 | `CCN(Cc1ccccc1)Cc1ccc(C(=O)Nc2ccccc2C)cc1` | C24H26N2O | 358.49 | 5.27 | S5: [11] | Kekulé input → aromatic canonical (normal conversion) |
| L-177 | `c1ccc(C2CCN(C3CCc4ccccc4C4CCCCCC43)C2)cc1` | C26H33N | 359.56 | 6.15 | S2-B: [536] | Kekulé input → aromatic canonical (normal conversion) |
| L-178 | `Brc1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C20H13BrN2 | 361.24 | 5.73 | S1: [6]; S2-A: [5] |  |
| L-179 | `CC1=C(c2c(-c3ccccc3CN=C=O)[nH]c3ccccc23)c2ccccc21` | C25H18N2O | 362.43 | 5.96 | S2-A: [313] | Kekulé input → aromatic canonical (normal conversion) |
| L-180 | `CC(C)NCC(O)c1ccc(O)c(C(C)CI)c1` | C14H22INO2 | 363.24 | 2.96 | S3: [34] |  |
| L-181 | `Cc1ccccc1C(=O)Nc1ccccc1C(=O)N1CC2CCNCC2C1` | C22H25N3O2 | 363.46 | 2.93 | Doc3: [A] | Doc3 A; doc-claimed MW 342.41 (x71; once 296.34 — same SMILES, two MWs); Kekulé input → aromatic canonical (normal conversion) |
| L-182 | `CC1=C(c2c(-c3ccccc3CC(C)C)[nH]c3ccccc23)c2ccccc21` | C27H25N | 363.50 | 7.33 | S2-A: [322] | Kekulé input → aromatic canonical (normal conversion) |
| L-183 | `CC1=C(c2c(-c3ccccc3C(C)CN)[nH]c3ccccc23)c2ccccc21` | C26H24N2 | 364.49 | 6.19 | S2-A: [328] | Kekulé input → aromatic canonical (normal conversion) |
| L-184 | `CC1=C(c2c(-c3ccccc3CC(C)N)[nH]c3ccccc23)c2ccccc21` | C26H24N2 | 364.49 | 6.02 | S2-A: [352] | Kekulé input → aromatic canonical (normal conversion) |
| L-185 | `CC1=C(c2c(-c3ccccc3CN(C)C)[nH]c3ccccc23)c2ccccc21` | C26H24N2 | 364.49 | 6.19 | S2-A: [317] | Kekulé input → aromatic canonical (normal conversion) |
| L-186 | `CCC(N)c1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H24N2 | 364.49 | 6.54 | S2-A: [327] | Kekulé input → aromatic canonical (normal conversion) |
| L-187 | `CN(Cc1ccccc1)Cc1ccc(C(=O)Nc2ccc(Cl)cc2)cc1` | C22H21ClN2O | 364.88 | 5.22 | S5: [13] |  |
| L-188 | `BrCc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C18H13BrN4 | 365.23 | 4.38 | Doc1: [CBr] | Doc1 key CBr; doc-claimed MW 371.21 / LogP 4.0 (doc-claimed, unvalidated) |
| L-189 | `CC1=C(c2c(-c3ccccc3CC(=O)O)[nH]c3ccccc23)c2ccccc21` | C25H19NO2 | 365.43 | 5.75 | S2-A: [344] | Kekulé input → aromatic canonical (normal conversion) |
| L-190 | `CC1=C(c2c(-c3ccccc3COC=O)[nH]c3ccccc23)c2ccccc21` | C25H19NO2 | 365.43 | 5.80 | S2-A: [338] | Kekulé input → aromatic canonical (normal conversion) |
| L-191 | `CC1=C(c2c(-c3ccccc3CC(C)O)[nH]c3ccccc23)c2ccccc21` | C26H23NO | 365.48 | 6.05 | S2-A: [350] | Kekulé input → aromatic canonical (normal conversion) |
| L-192 | `CCC(O)c1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H23NO | 365.48 | 6.57 | S2-A: [343] | Kekulé input → aromatic canonical (normal conversion) |
| L-193 | `CCOCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H23NO | 365.48 | 6.66 | S2-A: [321] | Kekulé input → aromatic canonical (normal conversion) |
| L-194 | `CC1=C(c2c(-c3ccccc3C(O)CO)[nH]c3ccccc23)c2ccccc21` | C25H21NO2 | 367.45 | 5.15 | S2-A: [346] | Kekulé input → aromatic canonical (normal conversion) |
| L-195 | `CC(c1ccccc1)C1Cc2ccccc2-c2ccccc2C2CCN1CC2` | C27H29N | 367.54 | 6.26 | S2-B: [535] | Kekulé input → aromatic canonical (normal conversion) |
| L-196 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)OCCCCNCO)c1` | C19H32N2O5 | 368.47 | 1.39 | S3: [57] |  |
| L-197 | `CC(COCN)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H32N2O5 | 368.47 | 1.64 | S3: [88] |  |
| L-198 | `CC(COCO)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H31NO6 | 369.46 | 1.67 | S3: [83] |  |
| L-199 | `CC(CONF)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29FN2O5 | 372.44 | 2.11 | S3: [96] |  |
| L-200 | `CC(=O)c1ccc(NC(=O)c2ccc(CN(C)Cc3ccccc3)cc2)cc1` | C24H24N2O2 | 372.47 | 4.77 | S5: [19] | Kekulé input → aromatic canonical (normal conversion) |
| L-201 | `CC(CNCl)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29ClN2O4 | 372.89 | 2.45 | S3: [78] |  |
| L-202 | `CN(Cc1ccccc1)Cc1ccc(C(=O)Nc2ccc(C(N)=O)cc2)cc1` | C23H23N3O2 | 373.46 | 3.67 | S5: [20] | Kekulé input → aromatic canonical (normal conversion) |
| L-203 | `CC(COCl)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H28ClNO5 | 373.88 | 2.88 | S3: [85] |  |
| L-204 | `CN(Cc1ccccc1)Cc1ccc(C(=O)Nc2ccc(C(=O)O)cc2)cc1` | C23H22N2O3 | 374.44 | 4.27 | S5: [21] | Kekulé input → aromatic canonical (normal conversion) |
| L-205 | `BrCc1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C21H15BrN2 | 375.27 | 5.86 | S1: [28] |  |
| L-206 | `CC1=C(c2c(-c3ccccc3C(F)(F)F)[nH]c3ccccc23)c2ccccc21` | C24H16F3N | 375.39 | 7.15 | S2-A: [51,109,150,157,176,187,190,194,204,213,225,232,239,256,267,274,284,292] | Kekulé input → aromatic canonical (normal conversion) |
| L-207 | `CC(C)NCC(O)c1ccc(O)c(C(C)C(=O)I)c1` | C14H20INO3 | 377.22 | 2.49 | S3: [38] |  |
| L-208 | `CC1=C(c2c(-c3ccccc3CC(C)(C)C)[nH]c3ccccc23)c2ccccc21` | C28H27N | 377.53 | 7.72 | S2-A: [347] | Kekulé input → aromatic canonical (normal conversion) |
| L-209 | `CC(=O)NCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H22N2O | 378.48 | 5.76 | S2-A: [315-316] | Kekulé input → aromatic canonical (normal conversion) |
| L-210 | `CC1=C(c2c(-c3ccccc3C(=O)N(C)C)[nH]c3ccccc23)c2ccccc21` | C26H22N2O | 378.48 | 5.83 | S2-A: [310] | Kekulé input → aromatic canonical (normal conversion) |
| L-211 | `CC1=C(c2c(-c3ccccc3CC(C)CN)[nH]c3ccccc23)c2ccccc21` | C27H26N2 | 378.52 | 6.26 | S2-A: [349] | Kekulé input → aromatic canonical (normal conversion) |
| L-212 | `CCN(C)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H26N2 | 378.52 | 6.58 | S2-A: [320,334] | Also written as: `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)CC)C5=CC=CC=C15`; `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CC)C)C5=CC=CC=C15`; Kekulé input → aromatic canonical (normal conversion) |
| L-213 | `CC(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H21NO2 | 379.46 | 6.19 | S2-A: [373] | Kekulé input → aromatic canonical (normal conversion) |
| L-214 | `CCOC(=O)c1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H21NO2 | 379.46 | 6.30 | S2-A: [342] | Kekulé input → aromatic canonical (normal conversion) |
| L-215 | `COC(=O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H21NO2 | 379.46 | 5.84 | S2-A: [308,329] | Kekulé input → aromatic canonical (normal conversion) |
| L-216 | `CC1=C(c2c(-c3ccccc3CC(C)CO)[nH]c3ccccc23)c2ccccc21` | C27H25NO | 379.50 | 6.30 | S2-A: [326] | Kekulé input → aromatic canonical (normal conversion) |
| L-217 | `CC1=C(c2c(-c3ccccc3COC(C)C)[nH]c3ccccc23)c2ccccc21` | C27H25NO | 379.50 | 7.05 | S2-A: [323] | Kekulé input → aromatic canonical (normal conversion) |
| L-218 | `CC1=C(c2c(-c3ccccc3COC(N)=O)[nH]c3ccccc23)c2ccccc21` | C25H20N2O2 | 380.45 | 5.72 | S2-A: [370] | Kekulé input → aromatic canonical (normal conversion) |
| L-219 | `CC1=C(c2c(-c3ccccc3CC(N)CO)[nH]c3ccccc23)c2ccccc21` | C26H24N2O | 380.49 | 4.99 | S2-A: [361] | Kekulé input → aromatic canonical (normal conversion) |
| L-220 | `CC1=C(c2c(-c3ccccc3CC(O)CN)[nH]c3ccccc23)c2ccccc21` | C26H24N2O | 380.49 | 4.99 | S2-A: [360] | Kekulé input → aromatic canonical (normal conversion) |
| L-221 | `CC1=C(c2c(-c3ccccc3CN(C)CO)[nH]c3ccccc23)c2ccccc21` | C26H24N2O | 380.49 | 5.51 | S2-A: [353,359] | Kekulé input → aromatic canonical (normal conversion) |
| L-222 | `CC1=C(c2c(-c3ccccc3COCCN)[nH]c3ccccc23)c2ccccc21` | C26H24N2O | 380.49 | 5.60 | S2-A: [332,341] | Kekulé input → aromatic canonical (normal conversion) |
| L-223 | `CNC(O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H24N2O | 380.49 | 5.21 | S2-A: [363,372] | Kekulé input → aromatic canonical (normal conversion) |
| L-224 | `CC1=C(c2c(-c3ccccc3COC(=O)O)[nH]c3ccccc23)c2ccccc21` | C25H19NO3 | 381.43 | 6.32 | S2-A: [408] | Kekulé input → aromatic canonical (normal conversion) |
| L-225 | `CC1=C(c2c(-c3ccccc3C(O)CCO)[nH]c3ccccc23)c2ccccc21` | C26H23NO2 | 381.48 | 5.54 | S2-A: [351] | Kekulé input → aromatic canonical (normal conversion) |
| L-226 | `CC1=C(c2c(-c3ccccc3CC(O)CO)[nH]c3ccccc23)c2ccccc21` | C26H23NO2 | 381.48 | 5.02 | S2-A: [357] | Kekulé input → aromatic canonical (normal conversion) |
| L-227 | `CC1=C(c2c(-c3ccccc3COC(C)O)[nH]c3ccccc23)c2ccccc21` | C26H23NO2 | 381.48 | 5.98 | S2-A: [335] | Kekulé input → aromatic canonical (normal conversion) |
| L-228 | `COCC(O)c1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H23NO2 | 381.48 | 5.81 | S2-A: [355] | Kekulé input → aromatic canonical (normal conversion) |
| L-229 | `CCCC(=O)NC1CCC(C(c2ccccc2)(c2ccccc2)C(O)O)CC1` | C24H31NO3 | 381.52 | 3.76 | S4: [177] | Kekulé input → aromatic canonical (normal conversion) |
| L-230 | `COCOCC(C)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C20H33NO6 | 383.49 | 2.33 | S3: [89] |  |
| L-231 | `CC1=C(c2c(-c3ccccc3CS(C)=O)[nH]c3ccccc23)c2ccccc21` | C25H21NOS | 383.52 | 6.01 | S2-A: [319] | Kekulé input → aromatic canonical (normal conversion) |
| L-232 | `CC(COCON)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H32N2O6 | 384.47 | 1.57 | S3: [90] |  |
| L-233 | `CC1=C(c2c(-c3ccccc3Br)[nH]c3ccccc23)c2ccccc21` | C23H16BrN | 386.29 | 6.89 | S2-A: [4] |  |
| L-234 | `CC(Br)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H26BrNO4 | 388.30 | 2.85 | S3: [67,76] |  |
| L-235 | `CN(Cc1ccccc1)Cc1ccc(C(=O)Nc2ccc(C(=O)P)cc2)cc1` | C23H23N2O2P | 390.42 | 4.59 | S5: [23] | Kekulé input → aromatic canonical (normal conversion) |
| L-236 | `CN(Cc1ccccc1)Cc1ccc(C(=O)Nc2ccc(C(=O)S)cc2)cc1` | C23H22N2O2S | 390.51 | 4.64 | S5: [22] | Kekulé input → aromatic canonical (normal conversion) |
| L-237 | `CC(=O)N(C)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H24N2O | 392.50 | 6.11 | S2-A: [325,345] | Also written as: `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C(=O)C)C)C5=CC=CC=C15`; `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)C(=O)C)C5=CC=CC=C15`; Kekulé input → aromatic canonical (normal conversion) |
| L-238 | `CC(=O)NC(C)c1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H24N2O | 392.50 | 6.32 | S2-A: [340,358] | Kekulé input → aromatic canonical (normal conversion) |
| L-239 | `CCC(=O)NCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H24N2O | 392.50 | 6.15 | S2-A: [324] | Kekulé input → aromatic canonical (normal conversion) |
| L-240 | `CCN(CC)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H28N2 | 392.55 | 6.97 | S2-A: [339] | Kekulé input → aromatic canonical (normal conversion) |
| L-241 | `CC1=C(c2c(-c3ccccc3C(O)CC(C)C)[nH]c3ccccc23)c2ccccc21` | C28H27NO | 393.53 | 7.21 | S2-A: [356] | Kekulé input → aromatic canonical (normal conversion) |
| L-242 | `CC1=C(c2c(-c3ccccc3CC(O)C(N)=O)[nH]c3ccccc23)c2ccccc21` | C26H22N2O2 | 394.47 | 4.52 | S2-A: [369] | Kekulé input → aromatic canonical (normal conversion) |
| L-243 | `CC1=C(c2c(-c3ccccc3COCC(N)=O)[nH]c3ccccc23)c2ccccc21` | C26H22N2O2 | 394.47 | 5.13 | S2-A: [375] | Kekulé input → aromatic canonical (normal conversion) |
| L-244 | `CNC(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H22N2O2 | 394.47 | 5.98 | S2-A: [400] | Kekulé input → aromatic canonical (normal conversion) |
| L-245 | `COC(=O)NCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H22N2O2 | 394.47 | 5.98 | S2-A: [330] | Kekulé input → aromatic canonical (normal conversion) |
| L-246 | `CCN(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H26N2O | 394.52 | 5.90 | S2-A: [366] | Kekulé input → aromatic canonical (normal conversion) |
| L-247 | `CN(Cc1ccc(C(=O)Nc2ccc(Br)cc2)cc1)c1ccccc1` | C21H19BrN2O | 395.30 | 5.34 | S5: [14] |  |
| L-248 | `CC1=C(c2c(-c3ccccc3CC(O)C(=O)O)[nH]c3ccccc23)c2ccccc21` | C26H21NO3 | 395.46 | 5.12 | S2-A: [367,388] | Kekulé input → aromatic canonical (normal conversion) |
| L-249 | `COC(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C26H21NO3 | 395.46 | 6.41 | S2-A: [381,393,417] | Kekulé input → aromatic canonical (normal conversion) |
| L-250 | `CC1=C(c2c(-c3ccccc3COCC(C)O)[nH]c3ccccc23)c2ccccc21` | C27H25NO2 | 395.50 | 6.02 | S2-A: [362,378] | Kekulé input → aromatic canonical (normal conversion) |
| L-251 | `CC1=C(c2c(-c3ccccc3CN(CO)CO)[nH]c3ccccc23)c2ccccc21` | C26H24N2O2 | 396.49 | 4.83 | S2-A: [364] | Kekulé input → aromatic canonical (normal conversion) |
| L-252 | `CCc1ccccc1C(=O)Nc1ccccc1C(=O)N1CCN(c2ccccc2)C1` | C25H25N3O2 | 399.49 | 4.42 | Doc3: [D] | Doc3 D — typo variant of C (missing piperazine carbon; 5-ring, not 6-ring); doc-claimed MW 426.55 (x2); Kekulé input → aromatic canonical (normal conversion) |
| L-253 | `CC1=C(c2c(-c3ccccc3CS(C)(=O)=O)[nH]c3ccccc23)c2ccccc21` | C25H21NO2S | 399.52 | 5.67 | S2-A: [333] | Kekulé input → aromatic canonical (normal conversion) |
| L-254 | `CC1=C(c2c(-c3ccccc3CBr)[nH]c3ccccc23)c2ccccc21` | C24H18BrN | 400.32 | 7.02 | S2-A: [18,45,103,151,185,205,223,265,285,302] |  |
| L-255 | `CC(COCONO)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H32N2O7 | 400.47 | 1.59 | S3: [97] |  |
| L-256 | `CC(COCOCl)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H30ClNO6 | 403.90 | 2.85 | S3: [91] |  |
| L-257 | `CC(=O)N(C)CCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H26N2O | 406.53 | 6.15 | S2-A: [354] | Kekulé input → aromatic canonical (normal conversion) |
| L-258 | `CCC(=O)N(C)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H26N2O | 406.53 | 6.50 | S2-A: [348,380] | Also written as: `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C(=O)CC)C)C5=CC=CC=C15`; `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)C(=O)CC)C5=CC=CC=C15`; Kekulé input → aromatic canonical (normal conversion) |
| L-259 | `CCN(Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21)C(C)=O` | C28H26N2O | 406.53 | 6.50 | S2-A: [331] | Kekulé input → aromatic canonical (normal conversion) |
| L-260 | `Ic1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C20H13IN2 | 408.24 | 5.57 | S1: [7] | Kekulé input → aromatic canonical (normal conversion) |
| L-261 | `CC(=O)N(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H24N2O2 | 408.50 | 5.43 | S2-A: [368,386,402] | Kekulé input → aromatic canonical (normal conversion) |
| L-262 | `CC(=O)NC(O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H24N2O2 | 408.50 | 5.12 | S2-A: [377] | Kekulé input → aromatic canonical (normal conversion) |
| L-263 | `CC1=C(c2c(-c3ccccc3COC(=O)N(C)C)[nH]c3ccccc23)c2ccccc21` | C27H24N2O2 | 408.50 | 6.33 | S2-A: [390] | Kekulé input → aromatic canonical (normal conversion) |
| L-264 | `CNC(=O)C(O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H24N2O2 | 408.50 | 4.78 | S2-A: [385,412] | Kekulé input → aromatic canonical (normal conversion) |
| L-265 | `CC1=C(c2c(-c3ccccc3CC(O)CN(C)C)[nH]c3ccccc23)c2ccccc21` | C28H28N2O | 408.55 | 5.59 | S2-A: [365] | Kekulé input → aromatic canonical (normal conversion) |
| L-266 | `CC1=C(c2c(-c3ccccc3CN(CO)C(N)=O)[nH]c3ccccc23)c2ccccc21` | C26H23N3O2 | 409.49 | 4.96 | S2-A: [392] | Kekulé input → aromatic canonical (normal conversion) |
| L-267 | `CCOC(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H23NO3 | 409.49 | 6.80 | S2-A: [405,420] | Kekulé input → aromatic canonical (normal conversion) |
| L-268 | `COC(=O)C(O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H23NO3 | 409.49 | 5.20 | S2-A: [382,394,401] | Kekulé input → aromatic canonical (normal conversion) |
| L-269 | `CC1=C(c2c(-c3ccccc3CN(CO)C(=O)O)[nH]c3ccccc23)c2ccccc21` | C26H22N2O3 | 410.47 | 5.56 | S2-A: [376,389] | Kekulé input → aromatic canonical (normal conversion) |
| L-270 | `ICc1ccc(-n2ccnc2-c2cccc3nccnc23)cc1` | C18H13IN4 | 412.23 | 4.42 | Doc1: [CI] | Doc1 key CI; doc-claimed MW 397.20 / LogP 4.5 (doc-claimed, unvalidated); Kekulé input → aromatic canonical (normal conversion) |
| L-271 | `CCc1ccccc1C(=O)Nc1ccccc1C(=O)N1CCN(c2ccccc2)CC1` | C26H27N3O2 | 413.52 | 4.46 | Doc3: [C] | Doc3 C; doc-claimed MW 426.55 (x67); Kekulé input → aromatic canonical (normal conversion) |
| L-272 | `CC(CNBr)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H29BrN2O4 | 417.34 | 2.61 | S3: [79] |  |
| L-273 | `CC(COBr)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H28BrNO5 | 418.33 | 3.03 | S3: [86] |  |
| L-274 | `CC(COCONOF)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H31FN2O7 | 418.46 | 2.02 | S3: [100] |  |
| L-275 | `CC(COCONCl)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H31ClN2O6 | 418.92 | 2.36 | S3: [94] |  |
| L-276 | `c1ccc2c(c1)CC(C1CCCCC1)N1CCC(CC1)c1ccccc1-c1ccccc1-2` | C31H35N | 421.63 | 7.71 | S2-B: [540] | Kekulé input → aromatic canonical (normal conversion) |
| L-277 | `CC(=O)NC(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H22N2O3 | 422.48 | 5.90 | S2-A: [411] | Kekulé input → aromatic canonical (normal conversion) |
| L-278 | `CC1=C(c2c(-c3ccccc3CC(O)C(=O)N(C)C)[nH]c3ccccc23)c2ccccc21` | C28H26N2O2 | 422.53 | 5.12 | S2-A: [374,391,398] | Kekulé input → aromatic canonical (normal conversion) |
| L-279 | `CCC(=O)N(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H26N2O2 | 422.53 | 5.82 | S2-A: [371] | Kekulé input → aromatic canonical (normal conversion) |
| L-280 | `CCCN(Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21)C(=O)O` | C28H26N2O2 | 422.53 | 7.02 | S2-A: [301] | Kekulé input → aromatic canonical (normal conversion) |
| L-281 | `CCN(C)C(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H26N2O2 | 422.53 | 6.72 | S2-A: [428] | Kekulé input → aromatic canonical (normal conversion) |
| L-282 | `CCNC(=O)C(O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H26N2O2 | 422.53 | 5.17 | S2-A: [421] | Kekulé input → aromatic canonical (normal conversion) |
| L-283 | `CC(=O)OC(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H21NO4 | 423.47 | 6.33 | S2-A: [414] | Kekulé input → aromatic canonical (normal conversion) |
| L-284 | `CC(=O)NN(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H25N3O2 | 423.52 | 4.93 | S2-A: [379,397] | Kekulé input → aromatic canonical (normal conversion) |
| L-285 | `CNC(=O)N(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H25N3O2 | 423.52 | 5.22 | S2-A: [407,416] | Kekulé input → aromatic canonical (normal conversion) |
| L-286 | `CC(=O)ON(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H24N2O3 | 424.50 | 5.36 | S2-A: [384] | Kekulé input → aromatic canonical (normal conversion) |
| L-287 | `CC1=C(c2c(-c3ccccc3COCC(O)C(N)=O)[nH]c3ccccc23)c2ccccc21` | C27H24N2O3 | 424.50 | 4.49 | S2-A: [387] | Kekulé input → aromatic canonical (normal conversion) |
| L-288 | `COC(=O)N(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H24N2O3 | 424.50 | 5.65 | S2-A: [395] | Kekulé input → aromatic canonical (normal conversion) |
| L-289 | `CC1=C(c2c(-c3ccccc3COCC(O)C(=O)O)[nH]c3ccccc23)c2ccccc21` | C27H23NO4 | 425.48 | 5.09 | S2-A: [383] | Kekulé input → aromatic canonical (normal conversion) |
| L-290 | `CC1=C(c2c(-c3ccccc3I)[nH]c3ccccc23)c2ccccc21` | C23H16IN | 433.29 | 6.73 | S2-A: [5] | Kekulé input → aromatic canonical (normal conversion) |
| L-291 | `CC(COCONOCl)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H31ClN2O7 | 434.92 | 2.29 | S3: [98] |  |
| L-292 | `CC(I)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C17H26INO4 | 435.30 | 2.89 | S3: [69,77] |  |
| L-293 | `c1ccc(-c2ccccc2C2CCN(C3CCc4ccccc4C4CCCCCC43)C2)cc1` | C32H37N | 435.66 | 7.82 | S2-B: [539] | Kekulé input → aromatic canonical (normal conversion) |
| L-294 | `ICCc1ccccc1-c1nc2ccccc2nc1-c1ccccc1` | C22H17IN2 | 436.30 | 5.94 | S1: [29] | Kekulé input → aromatic canonical (normal conversion) |
| L-295 | `CC(=O)N(C)C(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H24N2O3 | 436.51 | 6.24 | S2-A: [441] | Kekulé input → aromatic canonical (normal conversion) |
| L-296 | `CC(=O)NC(=O)C(O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H24N2O3 | 436.51 | 4.69 | S2-A: [406] | Kekulé input → aromatic canonical (normal conversion) |
| L-297 | `CCC(=O)NC(=O)OCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H24N2O3 | 436.51 | 6.29 | S2-A: [423] | Kekulé input → aromatic canonical (normal conversion) |
| L-298 | `CCN(C)C(=O)C(O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C29H28N2O2 | 436.56 | 5.51 | S2-A: [424] | Kekulé input → aromatic canonical (normal conversion) |
| L-299 | `CC(c1ccccc1)N1CCC(C2Cc3ccccc3-c3ccccc3C3CCN2C3)CC1` | C31H36N2 | 436.64 | 6.54 | S2-B: [538] | Kekulé input → aromatic canonical (normal conversion) |
| L-300 | `CC(=O)OC(=O)C(O)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H23NO4 | 437.50 | 5.12 | S2-A: [409] | Kekulé input → aromatic canonical (normal conversion) |
| L-301 | `CC1=C(c2c(-c3ccccc3CN(CO)C(=O)N(C)C)[nH]c3ccccc23)c2ccccc21` | C28H27N3O2 | 437.54 | 5.56 | S2-A: [399,413] | Kekulé input → aromatic canonical (normal conversion) |
| L-302 | `CCC(=O)NN(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H27N3O2 | 437.54 | 5.32 | S2-A: [404,427] | Kekulé input → aromatic canonical (normal conversion) |
| L-303 | `CCNC(=O)N(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H27N3O2 | 437.54 | 5.61 | S2-A: [425] | Kekulé input → aromatic canonical (normal conversion) |
| L-304 | `CNC(=O)C(O)COCc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C28H26N2O3 | 438.53 | 4.75 | S2-A: [396,426,435] | Kekulé input → aromatic canonical (normal conversion) |
| L-305 | `COC(=O)NN(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C27H25N3O3 | 439.52 | 5.15 | S2-A: [432] | Kekulé input → aromatic canonical (normal conversion) |
| L-306 | `CC1=C(c2c(-c3ccccc3CI)[nH]c3ccccc23)c2ccccc21` | C24H18IN | 447.32 | 7.06 | S2-A: [46,104,152,186,206,224,266,286] | Kekulé input → aromatic canonical (normal conversion) |
| L-307 | `CC(COCOBr)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H30BrNO6 | 448.35 | 3.01 | S3: [92] |  |
| L-308 | `CCN(C)C(=O)N(CO)Cc1ccccc1-c1[nH]c2ccccc2c1C1=C(C)c2ccccc21` | C29H29N3O2 | 451.57 | 5.95 | S2-A: [422] | Kekulé input → aromatic canonical (normal conversion) |
| L-309 | `CC1=C(c2c(-c3ccccc3COCC(O)C(=O)N(C)C)[nH]c3ccccc23)c2ccccc21` | C29H28N2O3 | 452.55 | 5.09 | S2-A: [403] | Kekulé input → aromatic canonical (normal conversion) |
| L-310 | `CN(Cc1ccccc1)Cc1ccc(C(=O)Nc2ccc(I)cc2)cc1` | C22H21IN2O | 456.33 | 5.18 | S5: [15] | Kekulé input → aromatic canonical (normal conversion) |
| L-311 | `CC1=C(c2c(-c3ccccc3CCI)[nH]c3ccccc23)c2ccccc21` | C25H20IN | 461.35 | 7.10 | S2-A: [19] | Kekulé input → aromatic canonical (normal conversion) |
| L-312 | `CC(O)CCOCP(=O)(COC(N)=O)COC(=O)N1CCC(O)(c2nccc(N)n2)C1` | C17H28N5O8P | 461.41 | 0.21 | S7: [1,2–10] | Tenofovir-like phosphonate (S7) — isomeric/phosphonate pair duplicate (see §6); Also written as: `CC(CCOCP(=O)(COC(=O)N)COC(=O)N1CCC(O)(C1)C2=NC=CC(=N2)N)O`; `CC(CCOCP(=O)(COC(=O)N1CCC(O)(C1)C2=NC=CC(=N2)N)COC(=O)N)O`; Kekulé input → aromatic canonical (normal conversion) |
| L-313 | `CC(COCONBr)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H31BrN2O6 | 463.37 | 2.51 | S3: [95] |  |
| L-314 | `CC(COI)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C18H28INO5 | 465.33 | 3.07 | S3: [87] |  |
| L-315 | `CC(COCONOBr)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H31BrN2O7 | 479.37 | 2.44 | S3: [99] |  |
| L-316 | `CC(COCOI)COC(=O)C(C)c1cc(C(O)CNC(C)C)ccc1O` | C19H30INO6 | 495.35 | 3.05 | S3: [93] |  |
| L-317 | `CC(C)(C)C(=O)Nc1ccc(-n2cnc3cc(C(=O)Nc4ccc(OC(F)(F)F)cc4)ccc32)cc1` | C26H23F3N4O3 | 496.49 | 6.16 | Doc3: [G] | Doc3 G (full form); doc-claimed venetoclax parent — MISMATCH vs PubChem venetoclax (§7); Kekulé input → aromatic canonical (normal conversion) |
| L-318 | `c1ccc2c(c1)CC(C1CCCCC1)N1CCC(CC1)c1ccccc1-c1ccccc1-c1ccccc1-2` | C37H39N | 497.73 | 9.37 | S2-B: [VAR 543] | Kekulé input → aromatic canonical (normal conversion); S2 phenyl-chain reconstruction (see Method) |
| L-319 | `c1ccc(-c2ccccc2-c2ccccc2C2CCN(C3CCc4ccccc4C4CCCCCC43)C2)cc1` | C38H41N | 511.75 | 9.49 | S2-B: [VAR 542] | Kekulé input → aromatic canonical (normal conversion); S2 phenyl-chain reconstruction (see Method) |
| L-320 | `CC(c1ccccc1)N1CCC(C2Cc3ccccc3-c3ccccc3-c3ccccc3C3CCN2C3)CC1` | C37H40N2 | 512.74 | 8.21 | S2-B: [VAR 541] | Kekulé input → aromatic canonical (normal conversion); S2 phenyl-chain reconstruction (see Method) |
| L-321 | `CCC(C(=O)NC1CCC(C(C(=O)O)(c2ccccc2)c2ccccc2)CC1)c1ccccc1-c1ccccc1` | C36H37NO3 | 531.70 | 7.59 | S4: [2] | Kekulé input → aromatic canonical (normal conversion) |
| L-322 | `CCC(C(=O)NC1CCC(C(C(=O)O)(c2ccccc2)c2ccccc2)CC1)c1ccc(-c2cccnc2)cc1` | C35H36N2O3 | 532.68 | 6.99 | S4: [104,120,150-151,153,167,179,181,183,185,187,189,191,197,199] | Kekulé input → aromatic canonical (normal conversion) |
| L-323 | `CCC(C(=O)NC1CCC(C(C(=O)O)(c2ccccc2)c2ccccc2)CC1)c1ccc(-c2ccncc2)cc1` | C35H36N2O3 | 532.68 | 6.99 | S4: [131,155,157,161,165,169,175] | Kekulé input → aromatic canonical (normal conversion) |
| L-324 | `CCC(C(=O)NC1CCC(C(c2ccccc2)(c2ccccc2)C(O)O)CC1)c1ccc(-c2ccccc2)cc1` | C36H39NO3 | 533.71 | 6.82 | S4: [100] | Kekulé input → aromatic canonical (normal conversion) |
| L-325 | `CCC(C(=O)NC1CCC(C(c2ccccc2)(c2ccccc2)C(O)O)CC1)c1ccc(-c2cccnc2)cc1` | C35H38N2O3 | 534.70 | 6.21 | S4: [124,193,195] | Kekulé input → aromatic canonical (normal conversion) |
| L-326 | `CCC(C(=O)NC1CCC(C(c2ccccc2)(c2ccccc2)C(O)O)CC1)c1ccc(-c2ccncc2)cc1` | C35H38N2O3 | 534.70 | 6.21 | S4: [102,107,109,122,127,129,134,136,138,140,159,163,171,173] | Kekulé input → aromatic canonical (normal conversion) |
| L-327 | `CC(C)C(C(=O)NC1CCC(C(C(=O)O)(c2ccccc2)c2ccccc2)CC1)c1ccc(-c2ccccc2)cc1` | C37H39NO3 | 545.72 | 7.84 | S4: [1,4] | Doc-claimed atorvastatin-like parent (VAR 4 form) — MISMATCH vs PubChem atorvastatin (§7); Also written as: `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(=O)O)C4=CC=C(C=C4)C5=CC=CC=C5`; `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=C(C=C4)C5=CC=CC=C5`; Kekulé input → aromatic canonical (normal conversion) |
| L-328 | `CC(C)C(C(=O)NC1CCC(C(C(=O)O)(c2ccccc2)c2ccccc2)CC1)c1ccc(-c2cccnc2)cc1` | C36H38N2O3 | 546.71 | 7.23 | S4: [101] | Kekulé input → aromatic canonical (normal conversion) |
| L-329 | `CC(C)C(C(=O)NC1CCC(C(C(=O)O)(c2ccccc2)c2ccccc2)CC1)c1ccccc1-c1ccccn1` | C36H38N2O3 | 546.71 | 7.23 | S4: [103,123] | Kekulé input → aromatic canonical (normal conversion) |
| L-330 | `CC(C)C(C(=O)NC1CCC(C(C(=O)O)(c2ccccc2)c2ccccc2)CC1)c1ccccc1-c1cccnc1` | C36H38N2O3 | 546.71 | 7.23 | S4: [106,108,110,121,126,128,130,133,135,137,139,154,156,158,160,162,164,168,170,172,174,176,178,180,186,188,198] | Kekulé input → aromatic canonical (normal conversion) |
| L-331 | `CC(C)C(C(=O)NC1CCC(C(c2ccccc2)(c2ccccc2)C(O)O)CC1)c1ccc(-c2ccccc2)cc1` | C37H41NO3 | 547.74 | 7.07 | S4: [3] | Kekulé input → aromatic canonical (normal conversion) |
| L-332 | `CC(C)C(C(=O)NC1CCC(C(c2ccccc2)(c2ccccc2)C(O)O)CC1)c1ccc(-c2ccncc2)cc1` | C36H40N2O3 | 548.73 | 6.46 | S4: [105,125,132,152,166] | Kekulé input → aromatic canonical (normal conversion) |
| L-333 | `CC(C)C(C(=O)NC1CCC(C(c2ccccc2)(c2ccccc2)C(O)O)CC1)c1ccccc1-c1cccnc1` | C36H40N2O3 | 548.73 | 6.46 | S4: [182,184,190,192,194,196,200] | Kekulé input → aromatic canonical (normal conversion) |
| L-334 | `c1ccc(-c2ccccc2-c2ccccc2-c2ccccc2C2CCN(C3CCc4ccccc4C4CCCCCC43)C2)cc1` | C44H45N | 587.85 | 11.16 | S2-B: [VAR 545] | Kekulé input → aromatic canonical (normal conversion); S2 phenyl-chain reconstruction (see Method) |
| L-335 | `CC(c1ccccc1)N1CCC(C2Cc3ccccc3-c3ccccc3-c3ccccc3-c3ccccc3C3CCN2C3)CC1` | C43H44N2 | 588.84 | 9.87 | S2-B: [VAR 544] | Kekulé input → aromatic canonical (normal conversion); S2 phenyl-chain reconstruction (see Method) |
| L-336 | `c1ccc2c(c1)CC(C1CCCCC1)N1CCC(CC1)c1ccccc1-c1ccccc1-c1ccccc1-c1ccccc1-c1ccccc1-2` | C49H47N | 649.92 | 12.71 | S2-B: [VAR 546] | Kekulé input → aromatic canonical (normal conversion); S2 phenyl-chain reconstruction (see Method) |

*Table sorted by MW ascending. LogP is RDKit Crippen LogP (recomputed, not document-claimed).*

---

## 4. Structure-less candidate rows

These entries have no valid full-structure SMILES and therefore no row in §3. They are recorded here so they are not silently dropped, and so the do-not-merge rule is visible in the deliverable itself.

| ID | Name | Provenance | Source | What is known | Structure status |
|---|---|---|---|---|---|
| X-01 | DacomiLertib | HYPOTHETICAL / UNVERIFIED | compound-dacomilertib.md (folded in — not re-derived) | Document-claimed MW 645.63, LogP 4.7 (doc-claimed, unvalidated — match no recomputed structure). Base purine fragment MW 120.11. Stripped Modified core C26H25N5O4S MW 503.58 (diagnostic only, NOT the document's structure). | 16/16 full-length strings INVALID as written (formula-style fragments `CF3`/`CH3` fail RDKit parse; see §5). Image structure does not match the stripped core (image has Br + methoxy-bromophenyl; core has neither). No valid full-structure SMILES extractable — do NOT reconstruct one. Name collision with dacomitinib (Vizimpro, real drug) — never present as related. |
| X-02 | AGI-183 (ALS paper) | CANDIDATE — identity collision, DO NOT MERGE with L-162 | compound-agi183.md; ALS paper | Described in the ALS paper as a BCL-XL stabilizer, anti-apoptotic, neuroprotective. No SMILES and no MW in the paper. | No structure on record. Fields stay blank. Distinct from Doc 1 AGI-183 (L-162, Br structure, CRBN-binding FLIP inhibitor, pro-apoptotic, cancer). The two must never be merged, and neither may inherit the other's properties. |

---

## 5. Invalid list (383 strings)

Every distinct input string that failed RDKit parse, grouped by failure reason.
Counts: SYNTAX 236, RING-DIGIT-DUP 130, UNCLOSED-RING 8, AROMATIC-NONRING 7,
KEKULIZE 1, TRUNCATED 1. Total 383.

### 5.1 SYNTAX — 236 strings (formula-style fragments)

The dominant failure class. Bare H (`OCH3`, `NH2`, `OH`, `CH3`, `C2H5`) and bare
digits (`CF3`, `NO2`, `SO2`, `OCHF2`, `OCF3`, `CF2H`, `CO2`, `ClO2`, `Cl2`) are
formula-style fragments, not SMILES: a bare digit is a ring closure and an
unbracketed H is a syntax error. Verified empirically, e.g. `COCH3`,
`C1=CC=C(C=C1)CF3`, `C1=CC=C(C=C1)OH`, `CCNH2` all FAIL in RDKit, while `COC`,
`C(F)(F)F`, `C[N+](=O)[O-]` parse. Same defect class as DacomiLertib's
`CF3`/`CH3` failures (X-01).

**Doc 1 §1.4 (8):** `OCH3`, `CF3`, `OCHF2`, `OCF3`, `NO2`, `CF2H`, `COCH3`,
`OCH2F` — terminal-group fragments, not SMILES. (The broken AGI-405 fragment
`C1=CN=C2C(=N1)C(=CC` is UNCLOSED-RING, §5.3, not SYNTAX.)

**S1 (22):** quinoxaline-side variants carrying bare-H / bare-digit fragments.
Five of these also appear in S3 (and one in S2-A) — see the cross-source note below.

**S3 (16 SYNTAX of 18 invalid):** nine `@H` Block-2 strings
(`CC@HC(=O)O`, `CC@@HC(=O)O`, `CC@HN`, `CC@@HN`, `CC@HO`, `CCC@HC(=O)O`,
`CCC@@HC(=O)O`, `CCC@HN`, `CCC@@HN` — chiral `@H` + implicit-H conflict), the
acetaminophen-like `CC(=O)NC1=CC=C(O)C=C1CF3`, the S3-only quinoxaline variant
with a `ClO2` terminal (`C1=CC=C(C=C1)C2=NC3=CC=CC=C3N=C2C4=CC=CC=C4ClO2`), and
five quinoxaline variants shared with S1 (`CF3`, `CO2`, `NO2`, `OCF3`, `SO2`
terminals). Plus S3 Block-4 VAR 4 (KEKULIZE — see §5.5) and S3 VAR 71 (TRUNCATED — see §5.6). E-inline VAR 4
recovered from the source PDF text layer (`AGI_-Series.pdf`): `CCC@HC(=O)O` —
fails on the chiral `@H` + implicit-H conflict; the §2.9 gap is closed and the
string is INVALID as written.

**S4 (5 SYNTAX of 6 invalid):** four `C@HN` strings
(`C1CC(CN1C(=O)C@@HNC(=O)C@HN)C(=O)Br/Cl/F/O` — the lisinopril-like block; the
`@H` + following `N` makes the chiral centre unparseable) and the VAR 87 cut-off
fragment `C1CC(CN1C(=O)[C@@H` (unclosed bracket). VAR 58 is UNCLOSED-RING (§5.3).

**S5 (38 SYNTAX of 45 invalid):** element-soup strings with bare-H / bare-digit
tails (see §5.4 note and inventory §2.11). The other 7 are AROMATIC-NONRING (§5.4).

**S6 (117 SYNTAX of 123 invalid):** CONHCOCH3-family and other piperidine variants
carrying bare-H `NH`/`OCH3` fragments (including S2 VAR 167: as-written string
with trailing `Y` fails; the Y-stripped intended string also fails —
CONHCOCH3-family invalid strings: 2). The other 6 are UNCLOSED-RING (§5.3).

**S2-A (35):** phenyl-chain variants with bare-H / bare-digit fragments (includes
the `SO2` string shared with S1/S3).

**Doc 3 (1):** fragment F
`(C)C(=O)NC1=CC=C(C=C1)N2C=NC3=C2C=CC(=C3)C(=O)NC4=CC=C(C=C4)OC(F)(F)F` —
fails on the leading `(C)` branch (a branch with no preceding atom), not on the
`OC(F)(F)F` group, which is valid SMILES.

**Cross-source note:** 5 failing strings appear in more than one source section
(all S1 quinoxaline terminal-group variants also listed in S3; the `SO2` one also
in S2-A): `…C4=CC=CC=C4CF3`, `…C4=CC=CC=C4CO2`, `…C4=CC=CC=C4NO2`,
`…C4=CC=CC=C4OCF3`, `…C4=CC=CC=C4SO2`. By-source counts therefore sum to 389,
6 more than the 383 distinct failing strings.

### 5.2 RING-DIGIT-DUP — 130 strings (ring numbers ≥ 10 written as bare digits)

All S2-B phenyl chains with final ring ≥ 10: a bare two-digit ring number (`C10`) is read by RDKit as two closures (1 then 0), so the string cannot parse as written. These are listed compactly as VAR / head / final ring / length + reason — the full strings are regenerable from the §2 reconstruction rule + parameters, and the validation script retains them.

| VAR range | Head | Final ring | Length | Reason |
|---|---|---|---|---|
| 547–561 | A / B / C (cycling) | 10–14 | 96–149 | RING-DIGIT-DUP (final ring ≥ 10) |
| 562–682 | A / B / C (cycling) | 15–34+ | 150–715 | RING-DIGIT-DUP (final ring ≥ 10; later strings also unclosed) |

VAR 576 = 149-char prefix of its ring-14 build (truncated mid-token, ends `…C14=CC`); VAR 634 1st occurrence = 336-char prefix of the complete 715-char build. VAR 649 repeats VAR 641 exactly; VAR 665 repeats VAR 663 exactly (duplicate inputs, not separate invalids).

### 5.3 UNCLOSED-RING — 8 strings

Strings whose ring-closure digit is opened but never closed (no formula fragment
present — these are genuine unclosed rings, not `CF3`/`C2H5`-style subscripts).

| String | Source | Note |
|---|---|---|
| `C1=CN=C2C(=N1)C(=CC` | Doc 1 §1.2 | Broken AGI-405 fragment, truncated mid-string; ring 2 unclosed |
| `C1CC(CN1C(=O)[C@@H](CC2` | S4 VAR 58 | Cut-off fragment; ring 2 unclosed |
| `CC(C)C1CC(CN1)C(=O)NC2` | S6 [18] | Ring 2 unclosed |
| `CC(C)C1CC(CN1)C(=O)OC2C` | S6 [22] | Ring 2 unclosed |
| `CC(C)C1CC(CN1)C(=O)OCC2` | S6 [20] | Ring 2 unclosed |
| `CC(C)C1CC(CN1C)C(=O)NC3` | S6 [24] | Ring 3 unclosed |
| `CC(C)C1CC(CN1C)C(=O)OC2` | S6 [15] | Ring 2 unclosed |
| `CC(C)C1CC(CN1C)C(=O)OC3` | S6 [21] | Ring 3 unclosed |

### 5.4 AROMATIC-NONRING — 7 strings (S5 element-soup)

S5 element-soup strings whose aromatic atoms never form a ring (terminal acyl
groups on Co, Sn, Nb, Os, Pb, Sb, Sc). S5 recovered 67 unique strings in §2.11 text
(22 parse as strings across 19 rows + 3 duplicate extra inputs; 45 invalid) vs the
inventory §2.1 claim of 70 distinct — 3 unaccounted for (§10).

### 5.5 KEKULIZE — 1 string

S3 Block-4 VAR 4: `CC(C)NCC(O)c1cc(O)c(c1)C(C)C` — a 5-membered all-carbon aromatic ring cannot be Kekulé-ized by RDKit (`SanitizeMol` raises "Can't kekulize mol. Unkekulized atoms: 7 8 9 11 12").

### 5.6 TRUNCATED — 1 string (named edge cases)

S3 VAR 71 backticked truncated fragment
`CC(C)NCC(O)c1ccc(O)c(c1)C(C)C(=O)OCC(C` (inventory line 1173; the complete
`…OCC(C)N` form is listed above it in §2.9). Related named truncations recorded
under their primary reasons above: Doc 1 broken AGI-405 fragment (UNCLOSED-RING,
§5.3), S2 VAR 576, S2 VAR 634 1st occurrence (RING-DIGIT-DUP, §5.2), S4 VAR 58
(UNCLOSED-RING, §5.3) / VAR 87 (SYNTAX, §5.1), Doc 3 fragment F (SYNTAX, §5.1).

**Invalid by source (for cross-check):** S1 22, S2-A 35, S2-B 130, S3 18, S4 6, S5 45, S6 123, Doc 1 9, Doc 3 1. Sum 389 — 6 more than the 383 distinct failing strings because 5 strings appear in two or three sources (see the cross-source note in §5.1).

---

## 6. Duplicates (9 pairs)

Nine distinct input strings parse to a canonical structure already listed — same molecule, different written form. Each is a DUPLICATE input, not a separate entry. (Each canonical below has two document writings; the RDKit canonical is a third writing, shown in §3.)

| # | Canonical row | Duplicate input writings (both in the documents) | Source |
|---|---|---|---|
| 1 | L-120 | `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3` and `CN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2)C3=CC=CC=C3` | S5 [1,3] |
| 2 | L-135 | `CCN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3` and `CCN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2)C3=CC=CC=C3` | S5 [2,9] |
| 3 | L-137 | `CN(C1=CC=CC=C1)CC2=CC=C(C=C2)C(=O)NC3=CC=CC=C3C` and `CN(CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2C)C3=CC=CC=C3` | S5 [5,4,7] |
| 4 | L-163 | `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(C)O)C5=CC=CC=C15` and `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4C(O)C)C5=CC=CC=C15` | S2-A [318,337] |
| 5 | L-212 | `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)CC)C5=CC=CC=C15` and `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(CC)C)C5=CC=CC=C15` | S2-A [320,334] |
| 6 | L-237 | `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C(=O)C)C)C5=CC=CC=C15` and `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)C(=O)C)C5=CC=CC=C15` | S2-A [325,345] |
| 7 | L-258 | `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C(=O)CC)C)C5=CC=CC=C15` and `CC1=C(C2=C(NC3=CC=CC=C23)C4=CC=CC=C4CN(C)C(=O)CC)C5=CC=CC=C15` | S2-A [348,380] |
| 8 | L-312 | `CC(CCOCP(=O)(COC(=O)N)COC(=O)N1CCC(O)(C1)C2=NC=CC(=N2)N)O` and `CC(CCOCP(=O)(COC(=O)N1CCC(O)(C1)C2=NC=CC(=N2)N)COC(=O)N)O` (tenofovir-like [1] and [2–10] forms — same canonical) | S7 [1,2–10] |
| 9 | L-327 | `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(=O)O)C4=CC=C(C=C4)C5=CC=CC=C5` and `CC(C)C(C(=O)NC1CCC(CC1)C(C2=CC=CC=C2)(C3=CC=CC=C3)C(O)=O)C4=CC=C(C=C4)C5=CC=CC=C5` (`C(=O)O` vs `C(O)=O` — same canonical) | S4 [1,4] |

---

## 7. PubChem parent checks (PUG REST, 2026-11-07)

One line per claimed parent drug. All seven claimed parents MISMATCH — no claimed parent SMILES in the documents is the real drug. VERIFIED requires a claimed parent matching PubChem; none matched, so there are 0 VERIFIED rows in this library.

| Claimed parent | PubChem CID | PubChem formula | PubChem MW | Claimed structure in the documents | Result |
|---|---|---|---|---|---|
| venetoclax | 49846579 | C45H50ClN7O7S | 868.4 | Doc 3 full form G (L-317) | **MISMATCH** |
| BAM7 | 3101542 | C21H19N5O2S | 405.5 | S2 unsubstituted indole scaffold (no explicit BAM7 parent SMILES stated in Doc 2) | **MISMATCH** |
| S63845 | 122197581 | C39H37ClF4N6O6S | 829.3 | S3 "Drug X" `CC(C)NCC(O)c1ccc(O)c(c1)C(C)C` (salbutamol-like; validated row L-051) | **MISMATCH** |
| riluzole | 5070 | C8H5F3N2OS | 234.20 | S5 benzamide-like parent (L-120) | **MISMATCH** |
| pregabalin | 5486971 | C8H17NO2 | 159.23 | S6 piperidine parent `CC(C)C1CCC(CN1)C(=O)O` (validated row L-022) | **MISMATCH** |
| lisinopril | 5362119 | C21H31N3O5 | 405.5 | S4 lisinopril-like parent (the `C@HN` block strings — all fail to parse, §5.1; no valid lisinopril-like row exists) | **MISMATCH** |
| atorvastatin | 60823 | C33H35FN2O5 | 558.6 | S4 atorvastatin-like parent (VAR 4 form; validated row L-327) | **MISMATCH** |

Technical note: the first PubChem run failed with HTTP 400 because `CID` was in the requested property list (PUG returns CID by default; requesting it as a property is a BadRequest). PUG returns the keys `SMILES` / `ConnectivitySMILES`, not `IsomericSMILES`/`CanonicalSMILES`. Fixed in the script; all 7 lookups then succeeded.

---

## 8. SMARTS pattern results (ref §7, RDKit 2026.09.1)

All 17 patterns parsed in RDKit and run against the 336 validated structures.

| Pattern | SMARTS / definition | Hits | Hit IDs (where listed) |
|---|---|---|---|
| P-01 | phenyl `c1ccccc1` | **316** | — |
| P-02 | carboxylic acid `C(=O)[OH]` | **21** | L-001, L-002, L-007, L-021, L-022, L-023, L-072, L-189, L-204, L-224, L-248, L-269, L-280, L-289, L-321, L-322, L-323, L-327, L-328, L-329, L-330 |
| P-03 | P-01 AND P-02 | **15** | L-072, L-189, L-204, L-224, L-248, L-269, L-280, L-289, L-321, L-322, L-323, L-327, L-328, L-329, L-330 |
| P-04 | sulfonamide | **0** | — |
| P-05 | indole | **105** | — |
| P-06 | chiral Ala-like | **0** | — |
| P-06b | non-chiral Ala-like | **0** | — |
| P-07 | proline-like | **0** | — |
| P-08 | isobutyl `[CH3][CH](C)C` | **50** | — |
| P-11 | `[CH2][CH](C)C` | **84** | — |
| P-12 | P-09 AND P-10 AND P-11 (Phe–Trp–Leu triad) | **4** | L-182, L-211, L-216, L-241 |
| P-20 | phenol | **103** | — |
| P-21 | amide | **96** | — |
| P-22 | halogenophenyl | **21** | — |
| P-23 | primary amine | **41** | — |
| P-24 | hydroxy O | **174** | — |
| P-25 | ether O | **104** | — |
| P-26 | H-pyrrole N | **105** | — |

P-09 = P-01 and P-10 = P-05 (same strings, different biological reading).

**Not grounded / not run (per ref §7.1, §7.6, §9):** Mcl-1-selective, BCL-2-vs-Bcl-xL-selective, survivin, FLIP, and BIM/PUMA-specific patterns, and AGI-183-specific patterns — 2-D SMARTS cannot encode paralog selectivity or these pharmacophores from the available sources.

---

## 9. Validated counts summary (quotable numbers)

- **336 unique validated structures** (HYPOTHETICAL) from **728 distinct input strings** (766 input occurrences) extracted from the inventory's 1,948 SMILES occurrences.
- **383 distinct input strings fail to parse** (INVALID). **9 distinct input strings are duplicates** of an already-listed canonical structure. Check: 336 + 383 + 9 = 728.
- **Provenance: VERIFIED 0, HYPOTHETICAL 336, INVALID 383, DUPLICATE 9.** No row is VERIFIED — no claimed parent drug matches PubChem.
- **MW range of validated structures: 89.09 – 649.92.** Largest row: L-336 (S2-B VAR 546, C49H47N, MW 649.92). The six parsing phenyl chains: VAR 541 512.74 (L-320), VAR 542 511.75 (L-319), VAR 543 497.73 (L-318), VAR 544 588.84 (L-335), VAR 545 587.85 (L-334), VAR 546 649.92 (L-336).
- **Never quote the raw document counts as real:** not "300 variations", not "250 compounds", not "413 entries" — the validated unique count is **336**.
- Kekulé-in → aromatic-out (normal Daylight conversion): **209 rows**. Aromaticity-perception divergences flagged: **0**.
- Longest canonical SMILES in the table: 79 chars (only rings ≤ 9 parse, so no 1,000-char chains survive).

---

## 10. Open items / human review

1. **F / F-alt correction:** inventory §1.4 says the two F writings are the same molecule — RDKit shows ortho- vs para-F isomers (L-095 vs L-094, two rows, same formula/MW C17H11FN4, 290.30). Confirm with a chemist before any downstream use.
2. **Doc 1 claimed MWs disagree with RDKit for all 15 parsing structures** (and 8/23 strings are unparseable as written) — the document's MW/LogP/ΔG/IC50/goodness columns cannot be trusted as computed values. Decide whether any Doc 1 entry should be re-derived with corrected SMILES (e.g. `C(F)(F)F` for CF3, `OC` for OCH3) or left invalid as written.
3. **S2 phenyl chains with final ring ≥ 10 use bare two-digit ring numbers** (`C10` = closures 1+0) — unparseable as written; a `%10`-style correction would be new chemistry, not validation — needs a chemist's decision.
4. **S3 E-inline VAR 4 now recovered** (`CCC@HC(=O)O`) but invalid as written; **S5 inventory claims 70 distinct strings vs 67 present in §2.11 text** (3 unaccounted).
5. **No VERIFIED rows:** no claimed parent drug is the real drug, so nothing in the library is a confirmed known drug. The S2 header error (`ABT-199- BAX Activators (BAM7)`) and Series 004 reuse for two different parent drugs (lisinopril-like, then atorvastatin-like) remain document errors, flagged not corrected.
6. **AGI-183 identity collision:** Doc 1 AGI-183 (L-162) and the ALS-paper AGI-183 (X-02) must stay separate rows; neither may inherit the other's properties.
7. **Aromaticity:** 0 RDKit perception divergences flagged; 209 Kekulé→aromatic conversions are normal. Tautomers kept separate per policy (a) — no normalisation applied.
8. **DacomiLertib (X-01):** no valid full-structure SMILES exists in the source; do not reconstruct one. Any future DacomiLertib work needs a chemist-drawn structure first.
9. **Table rebuild (this pass):** the first-pass §3 table was defective (34 MW mismatches, 33 formula mismatches, 54 LogP mismatches, 22 sort breaks, 36 non-canonical strings, 7 duplicate canonical pairs, 55 spurious rows) and was rebuilt from the validation script's output; every row in this version was re-verified by re-parsing the table with RDKit (see the verification below). The validated count moved 335 → 336 because two genuinely valid input strings were missed by the first extractor — the S3 Drug X parent (intro prose, not a bullet) and S4 [177] (backticked string with a trailing space) — plus the S3 VAR 71 truncated fragment. The distinct-input count is 728 (vs 724 in the first pass): the +4 is +1 Drug X parent, +1 S4 [177], +1 S3 VAR 71 fragment, and +1 unexplained (likely a S2-B VAR 634/576 truncated-prefix counting difference between the two extraction runs). The full input set is enumerated by `validate_library.py`, so 728 is the auditable figure.
10. **S4 lisinopril-like parent has no valid row:** the lisinopril-like block strings (the `C@HN` family, VAR 58/87 fragments) all fail to parse (§5.1), so the claimed lisinopril parent is not a validated structure. Only the atorvastatin-like parent (L-327) survives as a validated row. The §7 lisinopril MISMATCH stands on the claimed string, not on a validated row.

---

*End of validated compound library. Staged locally only — not pushed, deployed, published, or sent.*
