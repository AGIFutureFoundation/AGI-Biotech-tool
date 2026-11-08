# SMILES / SMARTS Reference — Compound Library Canonical Reference

**Status:** LOCAL STAGING ONLY — reference document for the compound-library
validation subpage. Not published, not deployed, not sent anywhere.

**Source manual (read in full, 57 pages):**
`~/workspace/user/files/SMART__Molecular_Language.pdf` — *SMILES, SMARTS and
SMIRKS: The Daylight Chemical Information System Theory Manual* (David
Weininger, Daylight Chemical Information Systems). All 57 pages read:
pp. 1–36 and 40–57 by text extraction; pp. 37–39 are picture pages (figures and
tables) and were read by rendering them to images — their content (SMIRKS §5.4
hydrogen-semantics table, the amide-formation SMIRKS example, the
stereochemistry-inversion SMIRKS examples, and the opening of Chapter 6 on
fingerprints) **was** usable and is cited below. Nothing in the manual was
unreadable.

**Companion source for the pattern set:** the compound catalog's stated
AGI-001–AGI-010 targets (p53/Bax, BIM/PUMA, Mcl-1, cIAP1/2, XIAP,
Bcl-2/Bcl-xL, survivin, FLIP, Mdm2/p53) and the ALS paper's BCL-2/Bcl-xL and
Mcl-1 biology (AGI-183 described there as a BCL-XL stabilizer; AAV6-hSyn-MCL1
as the Mcl-1 arm). The raw SMILES inventory is still being extracted by a
parallel worker — **no catalog structure was available to this writer**, so every
pattern in §7 is designed from the pharmacophore descriptions and is marked
**TO BE VALIDATED** against the RDKit-validated structures once the inventory
lands.

**Scope and honesty lines.** This document is a representation standard, not a
biology claim. It makes no treatment, cure, diagnosis, or medical-device claims,
and it asserts nothing about any compound's activity. Every rule below traces to
a cited section of the manual; anything that could not be grounded is flagged in
§9 rather than filled in by invention.

---

## 1. Reference-standard role

This manual is the compound library's **canonical reference for Daylight
SMILES/SMARTS semantics, as implemented by RDKit** (see §6 for the exact
RDKit-vs-Daylight nuance — the two are *not* byte-identical).

What that means in practice:

- **Valid SMILES** means a string that parses under Daylight semantics
  (§3.2–§3.3): atoms from the organic subset or in brackets, bonds `- = # :`
  (single/double/triple/aromatic, with single and aromatic omissible),
  branches in parentheses, ring closures as digits (or `%nn` above 9),
  disconnected components separated by `.`, and optional isomeric
  specifications (isotope, `/` `\` double-bond direction, `@`/`@@` chirality).
  A string that fails to parse, violates valence, or is flagged "impossible"
  (e.g. `c1cccc1`, §3.4.2) is **not a valid library entry**, whatever its source.
- **Canonical identity** means the library's key for a structure is its
  canonical SMILES produced by **one** tool, consistently — RDKit
  (§6). Two entries with the same canonical SMILES are the same structure;
  two entries whose *input* SMILES merely look alike are not proven identical
  until canonicalized.
- **Search** means SMARTS substructure queries (§4), run against the
  canonicalized structures — never string matching on raw input SMILES.
- **Tautomers, Kekulé/aromatic forms, and partial chirality** are *distinct
  specifications of the same or different structures* under the manual's rules
  (§3.4.2, §3.4.5, §3.3); §8 gives the handling rules for each.

---

## 2. Molecules as graphs (manual Chapter 2)

### 2.1 The valence model — §2.1

Daylight represents a molecule as a **graph: nodes are atoms, edges are
bonds**. Each atom carries atomic number, atomic weight, charge, and number of
attached hydrogens; a chiral centre may additionally carry a chiral
specification. A bond is single, double, triple, or aromatic. The model is a
"fairly standard valence model": it knows normal organic valences, fills in
unspecified hydrogens by counting bonding electrons, detects aromatic and
anti-aromatic ring systems, and warns on unlikely or impossible molecules.

*Why it matters for the library:* the graph — not the string — is the molecule.
Two different SMILES strings that denote the same graph are the same library
entry; the canonicalization step (§3.1) exists precisely to collapse them.
Any validation that compares strings instead of graphs is wrong by
construction.

*Flexibility the model allows (and the validator must accept):*

- hydrogen-suppressed graphs (H as a property of heavy atoms) **or**
  hydrogen-complete graphs (H as explicit atoms);
- aromatic bonds **or** the alternating single/double Kekulé form;
- isotopic information and chirality unspecified, partially specified, or
  completely specified.

### 2.2 Explicit vs derived properties — §2.2

Explicit properties are what completely specify the graph (atoms, bonds, their
properties). Derived properties are computed from the graph:

- **Cycles / SSSR (§2.2.1).** A bond is a ring bond if removing it does not
  split the graph. Ring detection is easy; finding a smallest set of smallest
  rings (SSSR) is surprisingly complex, and more than one valid SSSR can
  exist (e.g. a tetrahedron has four faces but three rings — six valid
  SSSRs). *Library consequence:* ring-membership SMARTS primitives (`R<n>`,
  `r<n>`, §4.1) are defined against SSSR, so a pattern's ring-size match can
  depend on the SSSR choice; treat ring-size queries as approximate and
  verify hits by inspection.
- **Bond type vs bond order (§2.2.2).** Bond *order* (single/double/triple)
  is a formal property; bond *type* (single/double/triple/**aromatic**) is a
  derived property. Daylight uses an **extended Hückel rule** to identify
  aromatic molecules and ions: to qualify as aromatic, **all atoms in a ring
  must be sp² hybridized and the number of available "excess" p-electrons
  must satisfy Hückel's 4N+2 criterion**. The manual stresses this
  aromaticity is a *nomenclature* device, "not intended to imply anything
  about the reactivity, magnetic resonance spectra, heat of formation, or
  odor of substances" (§2.2.2, §3.4.2).
- **Symmetry (§2.2.3).** Detected automatically (as two-dimensional
  rotations); used for canonical labeling, chirality classification, detecting
  degenerate chiral specifications, and eliminating redundant calculation.
  *Library consequence:* symmetry is what makes canonicalization possible —
  symmetrically equivalent atoms must receive equivalent ranks, or the
  "unique" SMILES would not be unique.
- **Canonical labeling (§2.2.4).** A representation built in any atom order
  gets arbitrary labels; a nomenclature system needs a labeling independent
  of the representation's history. Daylight generates such a labeling
  whenever it generates a unique SMILES.
- **Chirality (§2.2.5).** Both an explicit and a derived property: the system
  accepts chiral specifications on input and sometimes rewrites them into a
  different but equivalent form; a "canonical chiral representation" must be
  chosen for a unique SMILES.

### 2.3 Reactions — §2.3 (for the record; the library is molecules, not reactions)

A reaction is a set of molecules in three roles — reactant, product, agent —
with an atom map recording which reactant atoms correspond to which product
atoms. Agents contribute no atoms to products; their atom maps are ignored and
are not part of the lexical (SMILES) definition. The system stores both fully
specified (reaction-graph-like) and information-deficient reactions, but does
**not** analyse a reaction for chemical sensibility. *Library consequence:*
reaction SMILES (`>>`) and atom maps (`:n`) must never appear in a molecule
entry; if the inventory contains them, they are data errors, not structures
(see §8).

### 2.4 Depictions — §2.4

Daylight generates schematic diagrams *ab initio*; correctness and
comprehensibility take precedence over appearance. Not a validation rule, but
relevant to the subpage: any structure diagram shown beside a library entry
must depict the entry's graph, not a different tautomer or valence model.

---

## 3. SMILES encoding rules (manual Chapter 3)

SMILES (Simplified Molecular Input Line Entry System) is a line notation using
printable characters, with no spaces. It contains the same information as an
extended connection table, but as a linguistic construct (§3, introduction).

### 3.1 Canonicalization — §3.1

- **Generic SMILES** describe only the labelled molecular graph (atoms and
  bonds, no chiral or isotopic information). Many valid generic SMILES exist
  for one structure.
- The **unique SMILES** is the one special generic SMILES produced by the
  canonicalization algorithm. "With unique SMILES, the name is universal.
  Anyone in the world who uses unique SMILES to name a molecule will choose
  the exact same name."
- **Isomeric SMILES** add isotopic and chiral specifications. A unique
  isomeric SMILES is an **absolute SMILES**.
- Worked examples (§3.1): `OCC`, `[CH3][CH2][OH]`, `C-C-O`, `C(O)C` all
  canonicalize to `CCO`; `OC(=O)C(Br)(Cl)N`, `ClC(Br)(N)C(=O)O`,
  `O=C(O)C(N)(Br)Cl` all canonicalize to `NC(Cl)(Br)C(=O)O`.

*Why it matters:* the unique SMILES is the library's deduplication key. The
validation pass must canonicalize every entry and flag collisions (two
inventory rows → one canonical SMILES) as duplicates, not as two compounds.

### 3.2 The five generic encoding rules — §3.2

| Rule | Section | What it is | Library relevance |
|---|---|---|---|
| Atoms | §3.2.1 | Atomic symbols; organic subset **B, C, N, O, P, S, F, Cl, Br, I** may be written unbracketed only when attached H conform to the lowest normal valence (B 3, C 4, N 3/5, O 2, P 3/5, S 2/4/6, halogens 1). Aromatic atoms are lower-case (`c` vs `C`). Inside brackets, H count and charge must be specified (default 0 if absent); `[Fe+++]` = `[Fe+3]`. | The parser's first check: unbracketed atoms outside the organic subset, or with non-normal valence, are invalid input. |
| Bonds | §3.2.2 | `-` single, `=` double, `#` triple, `:` aromatic. Adjacent atoms default to single or aromatic (both may be omitted). | A missing bond symbol is **not** "no bond" — it is single-or-aromatic. |
| Branches | §3.2.3 | Parentheses, nestable/stackable; the implicit connection is to the left. | Branch placement changes which atom a substituent attaches to; canonicalization normalizes it away. |
| Ring closures | §3.2.4 | Break one bond per ring; a digit after an atom marks the closure. Digits may be reused once a ring is closed (`O1CCCCC1N1CCCCC1`); above 9, use `%` + two digits (`C2%13%24`). One atom may carry several closures (cubane: `C12C3C4C1C5C4C3C25`). | Ring digits are *pairing* marks, not atom labels. `C1.C1` is ethane (§3.2.5) — a dot-separated pair of ring digits still bonds. |
| Disconnections | §3.2.5 | Components separated by `.`; order arbitrary; no implied charge pairing; net zero charge not required. | Salts, counter-ions, and multi-component entries are one library row with `.`-separated components — the validator must not split them into separate compounds silently, and must not assume a 1:1 salt pairing. |

### 3.3 Isomeric SMILES — §3.3

All isomer specifications are **optional**; absence of a specification means
the attribute is **unspecified**, not that it has a default value. This is what
makes *rigorous partial specification* possible — essential because much of the
world's chemical information concerns incompletely resolved chiralities.

- **Isotopes (§3.3.1).** Mass precedes the symbol inside brackets only:
  `[13C]`, `[2H]O[2H]`; `[C]` is carbon of unspecified mass.
- **Double-bond configuration (§3.3.2).** `/` and `\` are directional bonds
  with meaning only when present on **both** atoms of the double bond
  (`F/C=C/F` = E, `F/C=C\F` = Z; `F\C=C\F` and `F\C=C/F` are equally valid
  writings). SMILES uses **local** chirality (unlike CIP absolute chirality),
  so partial specification is legal: `F/C=C/C=C/C` (complete) vs
  `F/C=C/C=CC` (partial).
- **Tetrahedral centres (§3.3.3).** `@` / `@@` follow the chiral atom's
  symbol. Neighbour order is the order in the SMILES string, viewed from the
  preceding ("from") atom: `@` = following neighbours anticlockwise,
  `@@` = clockwise. If the centre is not the first atom and has an implicit H,
  that H is taken as the first neighbour; if the centre is first, the implicit
  H is the "from" atom. Explicit `[H]` is treated like any other atom. The
  manual's worked example is L-alanine `N[C@@H](C)C(=O)O` and D-alanine
  `N[C@H](C)C(=O)O`. Ring-closure order for a chiral atom is the lexical order
  of the digit **on the chiral atom**, not of the substituent atom
  (`C[C@H]1CCCCO1` ≡ `O1CCCC[C@@H]1C`). Absence of `@`/`@@` on a stereogenic
  atom means chirality **unspecified**, never racemic and never a specific
  enantiomer.
- **General chiral specification (§3.3.4).** Full form: `@` + two-letter
  class + permutation number. `@`/`@@` are shorthand for `@TH1`/`@TH2`;
  `@@@` = `@3` (as `+++` = `+3`). Classes: **TH** tetrahedral (default,
  degree 4; `@TH1`/`@TH2`); **AL** allene-like (default, degree 2;
  `C=C=C` and odd serial double-bond chains; `@AL1`/`@AL2`);
  **SP** square-planar (`@SP1`–`@SP3`, no shorthand, no clockwise concept —
  "U", "4", "Z" listings); **TB** trigonal-bipyramidal (default, degree 5;
  `@TB1`–`@TB20`); **OH** octahedral (default, degree 6; `@OH1`–`@OH30`).
  The system handles reduced chirality (fewer enantiomers by symmetry) and
  degenerate chirality (centre made non-chiral by symmetrical substitution),
  and generates unique isomeric SMILES for any specification.

### 3.4 Conventions — §3.4

- **Hydrogens (§3.4.1).** Three ways: implicit (normal valence, unbracketed
  atoms), explicit by count (in brackets; zero if unspecified), explicit atoms
  (`[H]`). Explicit H is **required** only for: charged H (`[H+]`); H bonded
  to H (`[H][H]`); bridging H (bonded to more than one atom); isotopic H
  (`[2H]`). Propane may be written `[CH3][CH2][CH3]` or `CCC`.
- **Aromaticity (§3.4.2).** Kekulé input is converted to aromatic internally:
  `C1=CC=CC=C1` (cyclohexatriene) is detected as aromatic and becomes
  benzene; `c1ccc1` and `c1ccccccc1` become the correct anti-aromatic
  cyclobutadiene and cyclooctatetraene. The conversion preserves implied sp²
  hybridization, implied H count, and formal charge. **Impossible input is
  flagged:** `c1cccc1` cannot be Kekulé-assigned (one carbon would be sp³
  with two hydrogens) and is an error, not a molecule. Only **C, N, O, P, S,
  As, Se, and `*`** (wildcard) can be aromatic. Exocyclic double bonds do
  not break aromaticity.
- **Aromatic nitrogen (§3.4.3).** All three common types use `n`: pyridine
  `n1ccccc1`, pyridine-N-oxide `O=n1ccccc1 [O-]` / `[n+]1ccccc1`, pyrrole
  `[nH]1cccc1` (pyrrolyl N written `[nH]` to distinguish it from pyridyl N).
  `[H]n1cccc1` and the aliphatic form `N1C=CC=C1` are equivalent inputs.
- **Bonding conventions (§3.4.4).** SMILES does not dictate valence
  conventions: nitromethane as `CN(=O)=O` or `C[N+](=O)[O-]` are both "right"
  models of the same substance (the former preserves symmetry and is
  preferred for database work). *Library consequence:* the validator must
  not reject a valid alternative valence model; it must canonicalize it. (A
  system such as THOR/Merlin retrieves data across valence models.)
- **Tautomers (§3.4.5).** Tautomers are **explicitly specified**; there is
  no "tautomeric bond", "mobile hydrogen", or "mobile charge" in SMILES.
  2-pyridone `O=c1[nH]cccc1` and 2-pyridinol `Oc1ncccc1` are different
  SMILES for different tautomers. Selection of one or all tautomers is the
  user's choice and depends on the application; given one form, most systems
  report data for all known tautomers. *Library consequence:* two tautomers
  are two distinct canonical SMILES and two distinct rows unless the library
  adopts an explicit tautomer-normalization policy (§8).

### 3.5 Reactions — §3.5 (reference only)

Reaction SMILES use `>` as separator with **exactly two** `>` characters
(`reactant > agent > product`; `>>` = no agent; `>>` alone is the empty
reaction). Molecule SMILES never contain `>`. Atom maps are non-negative
integer modifiers, last in the atom expression (`[CH3:2]`), denoting
equivalence classes across reactant/product; they are legal on any atom but
ignored for molecule processing, never appear in unique/molecule SMILES, and
appear only in absolute SMILES for reactions. Atom maps and agent components
are **not** part of the unique SMILES — a reaction datatree root is the unique
SMILES, and may contain multiple specific reactions with different agents and
maps (§3.5, §3.5.1). Map numbers are arbitrary class labels; the system may
renumber them on canonicalization (in practice small dense integers in
canonical atom order). Mapped hydrogens are "special" and are not suppressed
(§3.5.2); otherwise hydrogens in reactions follow molecule rules.

---

## 4. SMARTS — the substructure-search language (manual Chapter 4)

Substructure searching — finding a pattern (subgraph) in a molecule (graph) —
is "one of the most important tasks for computers in chemistry" (§4, intro).
SMARTS specifies substructures with rules that are straightforward extensions
of SMILES: almost all SMILES are valid SMARTS, but the semantics change,
because **SMILES describes a molecule and SMARTS describes a pattern**
(§4.7). Example: the phenol query is `[OH]c1ccccc1`.

Critical semantic difference (§4.7): in SMILES, unbracketed atoms carry
defaults (`O` = water: aliphatic oxygen, zero charge, two hydrogens). In
SMARTS, **unspecified properties are not part of the pattern** — `O` matches
*any* aliphatic oxygen (water, ethanol, acetone, hydroxy and hydronium ions…);
only `[OH2]` restricts the match to water. Likewise the Kekulé pattern
`C1=CC=CC=C1` does **not** match benzene (the SMILES `C1=CC=CC=C1` is
interpreted as the benzene *molecule*), while `c1ccccc1` matches it; the
Kekulé pattern does match the non-aromatic phenylate cation
`C1=CC=CC=[CH+]1`.

### 4.1 Atomic primitives — §4.1

All SMILES atomic symbols are legal; SMARTS adds the primitives below
(`<n>` = digit, `<c>` = chiral class). Note the manual's warning: primitive
`H` has two meanings — `[H]` is a hydrogen atom; `[*H2]` is any atom with
exactly two hydrogens attached. (Pre-4.51 `[H]` meant "any atom with one
attached hydrogen"; §5.4 changed it — see §5 below.)

| Symbol | Name | Matches | Default if `<n>` omitted |
|---|---|---|---|
| `*` | wildcard | any atom | — |
| `a` | aromatic | aromatic atom | — |
| `A` | aliphatic | aliphatic atom | — |
| `D<n>` | degree | `<n>` explicit connections | exactly one |
| `H<n>` | total-H-count | `<n>` attached hydrogens | exactly one |
| `h<n>` | implicit-H-count | `<n>` implicit hydrogens | at least one |
| `R<n>` | ring membership | in `<n>` SSSR rings | any ring atom |
| `r<n>` | ring size | in smallest SSSR ring of size `<n>` | any ring atom |
| `v<n>` | valence | total bond order `<n>` | exactly one |
| `X<n>` | connectivity | `<n>` total connections | exactly one |
| `x<n>` | ring connectivity | `<n>` total ring connections | at least one |
| `-<n>` / `+<n>` | charge | −/＋`<n>` formal charge | −1 / +1 (`--` = −2) |
| `#n` | atomic number | atomic number `<n>` | — |
| `@` / `@@` | chirality | anticlockwise / clockwise, default class | as shown |
| `@<c><n>` | chirality | chiral class `<c>`, permutation `<n>` | — |
| `@<c><n>?` | chiral or unspecified | as specified, or unspecified | — |
| `<n>` | atomic mass | explicit atomic mass | unspecified mass |

Manual examples (§4.1): `[#6]` carbon; `[Ca]` calcium; `[++]` +2 charge;
`[R]` any ring atom; `[D3]` 3 explicit bonds (implicit H not counted);
`[X3]` 3 total bonds (implicit H counted); `[v3]` bond orders totalling 3;
`C[C@H](F)O` matches the stated chirality; `C[C@?H](F)O` matches if chirality
is as specified **or not specified** — the `?` form is the correct tool for
partially-specified library entries.

### 4.2 Bond primitives — §4.2

A missing bond symbol means **"single or aromatic"**.

| Symbol | Matches |
|---|---|
| `-` | single bond (aliphatic) |
| `/` | directional bond "up" |
| `\` | directional bond "down" |
| `/?` / `\?` | directional bond "up/down or unspecified" |
| `=` | double bond |
| `#` | triple bond |
| `:` | aromatic bond |
| `~` | any bond (wildcard) |
| `@` | any ring bond |

Manual examples (§4.2, §4.9): `cc` any attached aromatic carbons; `c:c`
aromatic carbons joined by an aromatic bond; `c-c` aromatic carbons joined by
a single bond (e.g. biphenyl); `*!@*` two atoms joined by a non-ring bond;
`*@;!:*` two atoms joined by a non-aromatic ring bond;
`[C,c]=,#[C,c]` two carbons joined by a double **or** triple bond.

### 4.3 Logical operators — §4.3

Precedence, highest first: `!` (not) → `&` (and, high) → `,` (or) →
`;` (and, low). Adjacent primitives with no operator default to `&`. All
non-simple-primitive atomic expressions must be in brackets. The two ANDs
exist instead of grouping operators.

Manual examples (§4.3): `[CH2]` methylene carbon; `[!C;R]` (not aliphatic
carbon) AND in ring; `[!C;!R0]` same; `[n;H1]` / `[n&H1]` / `[nH1]` all
H-pyrrole nitrogen; `[c,n&H1]` aromatic carbon OR H-pyrrole nitrogen;
`[X3&H0]` 3 total bonds and no H; `[c,n;H1]` (aromatic C or aromatic N) AND
exactly one H; `[F,Cl,Br,I]` the first four halogens; `[35Cl]` chlorine-35.

### 4.4 Recursive SMARTS — §4.4

`$(SMARTS)` defines an atomic environment and is usable as an atomic
primitive, nestable. Example: `C[$(aaO);$(aaaN)]` = methyl carbon ortho to
oxygen **and** meta to nitrogen (all cases) — the recursive form succeeds where
plain `Caa(O)aN` / `Ca(aO)aaN` each cover only one positional case. *Library
use:* environment-qualified patterns (e.g. "aryl carbon ortho to a
hydrogen-bond donor") without enumerating every positional isomer.

### 4.5 Component-level grouping — §4.5

Zero-level parentheses group dot-disconnected fragments: all atoms inside one
set of parentheses must match within a **single** component of the target.
`(C.C)` matches two carbons in the same component; `(C).(C)` requires two
different components. Written for reaction processing (inter- vs
intramolecular queries), but the grouping semantics apply to any
multi-component library entry (salts, co-crystals).

### 4.6 Reaction queries — §4.6

Reaction queries use `>`-separated reactant/agent/product parts matching the
corresponding roles; a plain molecule SMARTS against a reaction target matches
anywhere (role unspecified). Atom maps in queries are optional and can only
*eliminate* hits, never add them; only `[expr:n]` / `[expr:?n]` forms are
allowed (low-precedence AND with the map). Unpaired maps in a reaction query
and maps on molecule queries are ignored. Reaction expressions are not allowed
inside recursive SMARTS.

### 4.7–4.9 SMARTS vs SMILES, efficiency, examples

- §4.7: see the semantic difference above. Also: the historical shortcut
  `Hn1cccc1` is accepted as SMILES for 1H-pyrrole but the SMARTS `Hn1cccc1`
  does **not** match it. Most SMARTS are not valid SMILES (`cOc` matches
  diphenyl ether's ether oxygen but describes no molecule).
- §4.8: SMARTS targets are processed strictly left-to-right. Put uncommon
  atoms/bonds early; in an AND-expression put the less common specification
  early; in an OR-expression put the less common specification last. The
  Daylight 4.x `dt_smarts_opt()` reorders/expands/consolidates automatically.
- §4.9 worked examples (reusable as library query fragments): `O` any
  aliphatic oxygen; `[O;H1]` simple hydroxy oxygen; `[O;D1]` 1-connected
  oxygen; `[O;D2]` etheric oxygen; `[C,c]` any carbon; `[N;R]` aliphatic
  nitrogen in a ring; `[n;H1]` H-pyrrole nitrogen.

---

## 5. SMIRKS and fingerprints (manual Chapters 5–6, for the record)

**SMIRKS (§5)** is the generic-reaction (transform) language, a restricted
hybrid of SMILES and SMARTS: reactant/product must have the same number and
types of mapped atoms with pairwise maps; stoichiometry is 1:1; explicit
hydrogens on one side must appear explicitly and mapped on the other; bond
expressions must be valid SMILES; atomic expressions may be SMARTS only where
bonding does not change. The one detail the validation worker must know:
§5.4 changed `[H]` in SMARTS from "any atom with one attached hydrogen"
(pre-4.51) to "a hydrogen atom" (4.51+), reconciling SMILES/SMARTS for
transforms; `[#1]`, `[H1]`, `[*H]` keep their pre-4.51 meanings. Stereochemistry
in SMIRKS is local, keyed to atom-map labels; transforms involving
stereochemistry should show all four connections to a tetrahedral centre and
all three connections to each alkene carbon. (Rendered pp. 37–39 confirm the
§5.4 hydrogen table, the amide-formation SMIRKS example, and both
stereo-inversion examples.)

**Fingerprints (§6)** are screening devices, not identity: substructure search
is NP-complete in the worst case, so a cheap screen that can say "pattern
**not** in molecule" with 100% confidence (but "pattern in molecule" only with
lower confidence) is used to avoid the expensive search most of the time.
Structural keys assign one bit per pre-defined feature; fingerprints hash
all atom/bond paths up to length 7 into a bitmap with no pre-assigned bit
meanings, and are folded (halved by OR) to tune information density.
*Library consequence:* a fingerprint hit is **not** a substructure hit — it is
a candidate that still needs the real SMARTS match. Fingerprint *absence* is
proof of absence; fingerprint *presence* is not proof of presence. The
difference fingerprint (§6.2.2) is for reaction bond-changes, not library
search.

---

## 6. The RDKit relationship — stated plainly

**RDKit implements Daylight SMILES/SMARTS semantics in principle, but RDKit
output is NOT byte-identical to Daylight output, and the two must never be
compared as strings.**

- **Same principles.** RDKit's canonical SMILES uses the same Morgan-style
  ranking / symmetry-breaking principles as Daylight's canonical labeling
  (§2.2.3–§2.2.4): initial invariants, iterative refinement, symmetry
  classes, then a deterministic traversal. RDKit's SMARTS engine implements
  the §4.1–§4.3 primitives and logical operators, including recursive
  SMARTS (§4.4) and the `@?` chiral-or-unspecified form.
- **Not byte-identical.** RDKit's canonical SMILES is **RDKit's own
  canonicalization** — same family of algorithm, different tie-breaking and
  traversal choices. A Daylight unique SMILES and an RDKit canonical SMILES
  for the same structure will in general be *different strings denoting the
  same graph*. Do not present RDKit output as "the Daylight unique SMILES",
  and do not treat a string mismatch between a Daylight source and an RDKit
  output as a structural difference.
- **Aromaticity divergences.** RDKit's aromaticity model has known
  divergences from Daylight's extended-Hückel rule (§2.2.2, §3.4.2) on edge
  cases — fused and heteroaromatic systems, charged rings, and
  exocyclic-double-bond cases are the usual points of disagreement. A
  structure that Daylight flags aromatic (or impossible, e.g. `c1cccc1`)
  may be perceived differently by RDKit, and vice versa. This is a
  *model* difference, not a data error, and it is exactly why the manual
  warns that its aromaticity is a nomenclature device, not a chemical
  property claim.
- **What the validation worker must do.**
  1. Canonicalize with **ONE** tool, consistently — **RDKit** — for every
     entry, every dedup key, and every query target. Never mix Daylight
     strings and RDKit strings in one comparison.
  2. Never test equality between a Daylight unique SMILES (from any source
     document) and an RDKit canonical SMILES. Compare graphs (RDKit
     `Mol` objects / canonical SMILES produced by the same RDKit version),
     or re-parse the Daylight string through RDKit first and compare the
     RDKit-canonicalized forms.
  3. Record the RDKit version used; canonical SMILES can change between
     RDKit versions, so the version is part of the key's provenance.
  4. For aromaticity-sensitive entries, store **both** the input SMILES and
     the RDKit-canonical SMILES, and flag any entry whose RDKit
     Kekulé/aromatic perception differs from the input form, for human
     review — do not silently "fix" it.
  5. Treat any SMARTS pattern in §7 as RDKit SMARTS: validate each pattern
     string by parsing it in RDKit before running it, and record the
     RDKit version alongside the pattern set.

---

## 7. SMARTS pattern set for the library's substructure-query layer

**Design basis.** The catalog's stated targets only — no catalog structures
were available (the raw SMILES inventory is being extracted by a parallel
worker). Each pattern below is therefore a **pharmacophore-feature pattern**:
it encodes a chemical feature that the named target's binding biology is
described in terms of, using only the manual's SMARTS semantics (§4.1–§4.4).
Patterns are deliberately *feature-level*, not whole-molecule: a BH3-mimetic
ligand is recognised by the *combination* of its features, and 2-D SMARTS
cannot encode the 3-D geometry (helix, groove) that gives a real binder its
selectivity. That limit is stated per pattern, not hidden.

**Status of every pattern: TO BE VALIDATED against the RDKit-validated
structures once the inventory lands.** The validation worker must run each
pattern, record hit/miss per AGI-001–AGI-010 entry, and report any pattern
that hits zero entries (possible over-specificity) or hits every entry
(possible under-specificity). No pattern below is claimed to hit any specific
entry until that run happens.

**How to read the table.** "Should hit" means *if* the entry contains the
stated feature — it is a prediction to test, not a result.

### 7.1 BCL-2 / Bcl-xL and Mcl-1 — BH3-mimetic pharmacophore

The BCL-2 family anti-apoptotic proteins (BCL-2, Bcl-xL, Mcl-1) bind the
amphipathic BH3 α-helix of pro-apoptotic proteins in a hydrophobic groove; a
BH3 mimetic reproduces the helix's hydrophobic side chains and its conserved
aspartate, which salt-bridges to a conserved arginine in the groove. The
patterns below encode those two feature classes.

| ID | SMARTS | What it matches | Should hit (to be validated) | Limits |
|---|---|---|---|---|
| P-01 | `c1ccccc1` | A phenyl (aromatic 6-ring) — the hydrophobic aryl anchor that occupies a hydrophobic pocket of the groove. Manual §4.7's own aromatic-ring example. | Any AGI-00x BH3-mimetic entry carrying a phenyl/aryl group (BCL-2/Bcl-xL and Mcl-1 entries). | Ubiquitous: phenyl is the commonest aryl group in organic chemistry. Sensitive, not specific — a hit means "has a phenyl", nothing more. |
| P-02 | `C(=O)[OH]` | A carboxylic acid — the BH3 aspartate carboxylate mimic (salt bridge to the conserved groove arginine). Built from §4.1 primitives (`C`, `=O`, `[OH]`). | BCL-2/Bcl-xL and Mcl-1 entries designed as Asp mimics. | Also matches any unrelated carboxylic acid (e.g. a solubilising group). Does not distinguish Asp-mimic acids from incidental acids. |
| P-03 | P-01 **AND** P-02 in the same molecule (run both queries, intersect hit sets) | The BH3-mimetic core: hydrophobic aryl **plus** acidic group in one molecule. (Two-pattern intersection, not a single SMARTS — §4.5 component grouping is for dot-disconnected fragments, not this.) | The BCL-2/Bcl-xL and Mcl-1 entries, if they are BH3 mimetics. | Still feature-level: gives no information about the distance/orientation between aryl and acid, which is what makes a real binder. A molecule can satisfy P-03 and not bind. |
| P-04 | `[SX4](=[OX1])(=[OX1])([NX3])` | A sulfonamide group — a common BH3-mimetic linker/scaffold feature. Built from §4.1 primitives (`S` with valence 4, two `=O`, attached `N`). | BCL-2/Bcl-xL entries carrying a sulfonamide linker, if any. | Not all BH3 mimetics have a sulfonamide; absence proves nothing. Also matches unrelated sulfonamides (e.g. antibacterials) if any were in the catalog. |
| P-05 | `c1ccc2[nH]ccc2c1` | An indole ring — a bulky hydrophobic heteroaryl anchor (also the Trp mimic in §7.3). Built from §4.1/§4.2 primitives (`c`, `[nH]` per §3.4.3/§4.3). | Mcl-1 and BCL-2/Bcl-xL entries with an indole anchor, if any. | Not selective for any one BCL-2 family member. Indole is also a common scaffold elsewhere. |

**Could not be grounded — Mcl-1 selectivity.** No SMARTS pattern can be
designed from the manual + the catalog targets that distinguishes an
Mcl-1 binder from a BCL-2/Bcl-xL binder. Selectivity between these paralogs
comes from the shape and residue contacts of the hydrophobic groove, which is
3-D information that 2-D SMARTS cannot encode. P-01–P-05 are therefore
*family-level* patterns. The closest grounded pattern for "Mcl-1-directed" is
P-03 (aryl + acid); its limit is that it is equally consistent with a
BCL-2/Bcl-xL binder. Mcl-1 selectivity must be established from the actual
structures and their source data once the inventory lands — not from a
pattern. Flagged, not invented.

**Could not be grounded — AGI-183.** The ALS paper describes AGI-183 as a
BCL-XL stabilizer, but no structure for AGI-183 exists on disk (see the ALS
deep dive: "one named compound is not a library"). No AGI-183-specific
pattern can be designed until its structure is in the inventory.

### 7.2 XIAP / SMAC — IAP-antagonist (SMAC-mimetic) pharmacophore

SMAC-mimetic / IAP-antagonist entries target the BIR domains of XIAP and
cIAP1/2 with the N-terminal AVPI tetrapeptide motif of SMAC (Ala–Val–Pro–Ile).
The patterns below encode the AVPI N-terminus and the proline residue, using
the manual's own alanine example (§3.3.3: L-alanine `N[C@@H](C)C(=O)O`) as the
grounding for the Ala fragment.

| ID | SMARTS | What it matches | Should hit (to be validated) | Limits |
|---|---|---|---|---|
| P-06 | `[NH2][C@H](C)C(=O)N` | N-terminal alanine-like fragment: free primary amine + chiral methyl-bearing carbon + amide carbonyl — the AVPI Ala1 residue. Chiral form from §3.3.3/§4.1 `@` primitive. | XIAP and cIAP1/2 (SMAC-mimetic) entries, if they carry an Ala-like N-terminus. | `@` vs `@@` depends on atom order in the entry's SMILES; a strict chiral query can miss the enantiomer as written. Run the non-chiral form P-06b first (below), then the chiral form as a strict pass. Also matches any N-terminal Ala in a peptide-like entry, not only SMAC mimetics. |
| P-06b | `[NH2][CH](C)C(=O)N` | Same as P-06 without chirality — the first-pass query. | Same as P-06. | No stereochemical discrimination at all; use only as the screening pass. |
| P-07 | `N1CCCC1C(=O)` | A proline-like 5-membered ring nitrogen with an amide carbonyl — the AVPI Pro3 residue. Built from §3.2.4 ring-closure + §4.1 primitives. | XIAP and cIAP1/2 entries carrying a Pro-like residue. | Proline rings are common in peptides; a hit means "has a proline-like residue", not "is a SMAC mimetic". |
| P-08 | `[CH3][CH](C)C` | An isobutyl-like fragment — the Val/Ile hydrophobic side chains of AVPI (Val2, Ile4). | XIAP / cIAP1/2 entries with Val- or Ile-like side chains. | Extremely generic (leucine/isoleucine/valine side chains and simple alkyl groups all match). Useful only in combination with P-06/P-07. |

### 7.3 p53 / Mdm2 and p53 / Bax

The p53–Mdm2 interaction is the p53 transactivation-domain helix docking
three hydrophobic side chains — Phe19, Trp23, Leu26 — into Mdm2's
hydrophobic cleft. The patterns encode those three side-chain features.

| ID | SMARTS | What it matches | Should hit (to be validated) | Limits |
|---|---|---|---|---|
| P-09 | `c1ccccc1` (same string as P-01; different biological reading) | Phenyl — the Phe19 mimic. | Mdm2/p53 entries carrying a Phe-mimicking aryl group. | Identical to P-01: the pattern cannot know which target it is "for". Target assignment comes from the catalog's annotation, not from the pattern. |
| P-10 | `c1ccc2[nH]ccc2c1` (same string as P-05) | Indole — the Trp23 mimic. | Mdm2/p53 entries carrying a Trp-mimicking indole. | Same string as P-05. A hit is a feature, not a target assignment. |
| P-11 | `[CH2][CH](C)C` | Isobutyl — the Leu26 mimic. | Mdm2/p53 entries carrying a Leu-mimicking isobutyl group. | Generic alkyl fragment; meaningful only with P-09/P-10 co-occurrence. |
| P-12 | P-09 **AND** P-10 **AND** P-11 in the same molecule | The Phe–Trp–Leu hydrophobic triad (feature-level). | Mdm2/p53 entries designed as triad mimetics, if any. | **Cannot encode the helix geometry.** The triad works because the three side chains sit on one face of an α-helix at fixed distances/angles; 2-D SMARTS has no distance or angle. P-12 is a necessary-condition screen, never a sufficient one. |

### 7.4 BIM / PUMA (BH3-only proteins)

BIM and PUMA are themselves BH3-domain proteins — the *ligands* for the
BCL-2-family groove, not a separate pocket. There is no distinct "BIM/PUMA
pharmacophore" to encode: an entry annotated BIM/PUMA is either a BH3-domain
peptide/mimetic (covered by P-01–P-03) or a modulator of BIM/PUMA expression,
for which no structural motif is stated in the catalog targets. **No
BIM/PUMA-specific pattern is designed.** The closest grounded patterns are
P-01–P-03, with the limit that they identify BH3-mimetic *features*, not
BIM/PUMA specificity. Flagged, not invented.

### 7.5 Generic utility patterns (manual-grounded, target-agnostic)

From the manual's own §4.9 examples — useful as sanity checks and as building
blocks, not as pharmacophores.

| ID | SMARTS | What it matches | Use |
|---|---|---|---|
| P-20 | `[OH]c1ccccc1` | Phenol (manual §4, intro example). | Hydroxy-aryl H-bond donor check. |
| P-21 | `C(=O)N` | Amide / peptide bond. | Peptide-like entries (SMAC mimetics, BH3 peptides). |
| P-22 | `[F,Cl,Br,I]c1ccccc1` | Halogen-substituted phenyl (manual §4.3 `[F,Cl,Br,I]` + §4.1). | Halogenated-aryl hydrophobic-pocket filling; also a quick halogen census. |
| P-23 | `[NH2]` | Primary amine (total-H-count primitive, §4.1). | Solubilising basic group; N-terminal Ala check (with P-06). |
| P-24 | `[O;H1]` | Simple hydroxy oxygen (manual §4.9). | Hydroxy census. |
| P-25 | `[O;D2]` | Etheric (2-connected) oxygen (manual §4.9). | Ether/linkage census. |
| P-26 | `[n;H1]` | H-pyrrole nitrogen (manual §4.3/§4.9). | Indole/pyrrole NH check; pairs with P-05/P-10. |

### 7.6 Could not be grounded at all

- **Survivin.** No small-molecule pharmacophore for survivin is stated in
  the catalog targets or the manual. Survivin is a structurally distinct IAP
  (single BIR domain, no RING); its known ligand chemotypes are not
  describable from the sources available. **No survivin pattern designed.**
- **FLIP (c-FLIP).** No pharmacophore is stated in the catalog targets or
  the manual. **No FLIP pattern designed.**
- **BCL-2 vs Bcl-xL selectivity.** As with Mcl-1 (§7.1), 2-D SMARTS cannot
  encode paralog selectivity within the BCL-2 family.
- **Any whole-molecule pattern for a specific AGI-001–AGI-010 entry.**
  Without the inventory structures, whole-molecule SMARTS would be
  invention. The validation worker must derive entry-specific patterns from
  the validated structures, not from this document.

---

## 8. How to use this reference in the validation pass

1. **Valid-parse rule.** Parse every inventory SMILES in RDKit. Reject (do
   not silently repair) any string that fails to parse, violates valence, or
   is flagged impossible under §3.4.2 (e.g. `c1cccc1`). Log the rejected
   string, its source row, and the parser's error. A rejected entry is a
   data-quality ticket, not a compound.
2. **Canonicalization rule.** Canonicalize every accepted entry with RDKit
   (one version, recorded — §6). The RDKit canonical SMILES is the dedup
   key. Two rows → one canonical SMILES = one compound, flagged as a
   duplicate. Never compare a Daylight unique SMILES from a source document
   against an RDKit canonical SMILES for equality.
3. **Kekulé / aromatic handling.** Accept both aromatic and Kekulé input
   (§3.4.2: Kekulé input is detected and converted internally). Store the
   input SMILES *and* the RDKit-canonical SMILES. If RDKit's aromatic
   perception differs from the input form, flag for human review (§6, rule
   4); do not silently rewrite. Remember aromaticity here is a nomenclature
   device (§2.2.2), not a reactivity claim.
4. **Tautomer handling.** Tautomers are explicitly distinct SMILES (§3.4.5):
   do **not** merge tautomers by default. Decide and record one policy
   before the pass: (a) keep each tautomer as its own row, or (b) normalize
   to a single canonical tautomer per compound (RDKit tautomer
   canonicalization) and record the mapping. Either policy is defensible;
   an unrecorded mixture is not. If policy (b) is chosen, the pattern-hit
   table must be generated from the normalized forms.
5. **Chirality handling.** Absence of `@`/`@@` means **unspecified**, never
   racemic and never a specific enantiomer (§3.3). Do not assign chirality
   the inventory does not state. For queries: run the non-chiral form first
   (e.g. P-06b), then the chiral form (P-06) as a strict pass; report both
   hit counts. For double bonds, `/` `\` have meaning only in pairs
   (§3.3.2); a lone directional bond is not a specification. For partial
   specifications, use the `@?` form (§4.1: matches as specified *or*
   unspecified) rather than dropping the chiral centre.
6. **Valence-model handling.** Accept alternative valid valence models
   (§3.4.4: `CN(=O)=O` vs `C[N+](=O)[O-]`); canonicalization, not rejection,
   is the response. Flag only genuinely invalid valence.
7. **SMARTS query workflow.**
   a. Parse each §7 pattern in RDKit first; a pattern that fails to parse
      is a pattern error, not a zero-hit result.
   b. Run patterns against the **RDKit-canonicalized** structures, not the
      raw input strings.
   c. For co-occurrence patterns (P-03, P-12), run the component queries
      separately and intersect the hit sets; record per-component hit counts
      as well as the intersection.
   d. Order patterns with uncommon atoms/bonds first (§4.8) for speed;
      record the RDKit version with the pattern set (§6, rule 5).
   e. Report per-pattern: hits per AGI entry, zero-hit patterns, and
      all-entry patterns — each is a signal about the pattern, not about
      the compounds, until a human reviews it.
   f. Remember §6: a fingerprint screen is not a substructure result. If
      fingerprints are used for speed, a fingerprint hit must still be
      confirmed by the real SMARTS match; a fingerprint miss is proof of
      absence.
8. **What never enters the library.** Reaction SMILES (`>>`), atom maps
   (`:n`), and agent components (§3.5) in a molecule row; SMARTS strings
   presented as SMILES (§4.7: most SMARTS are not valid SMILES); and any
   string copied from a Daylight source without re-parsing through RDKit
   (§6, rule 2).

---

## 9. What could not be grounded (honesty log)

- **Mcl-1-selective, BCL-2-vs-Bcl-xL-selective patterns** — 2-D SMARTS
  cannot encode paralog selectivity; closest grounded patterns are the
  family-level P-01–P-05 (§7.1).
- **Survivin and FLIP patterns** — no pharmacophore stated in the catalog
  targets or the manual (§7.6).
- **BIM/PUMA-specific pattern** — BIM/PUMA are BH3 ligands, not a separate
  pocket; covered only by the BH3-feature patterns P-01–P-03 (§7.4).
- **AGI-183 pattern** — no structure on disk (§7.1).
- **Whole-molecule patterns for AGI-001–AGI-010** — inventory not yet
  available; to be derived by the validation worker from validated
  structures (§7.6).
- **RDKit-vs-Daylight byte identity** — explicitly *not* claimed; see §6.
  The RDKit aromaticity-divergence note is the library's operating
  assumption as directed for this reference; the validation worker should
  confirm it empirically on the inventory's aromatic entries (count
  entries where RDKit perception differs from input form) and record the
  result, rather than treating it as verified fact.
- **Manual pp. 37–39** — picture pages; rendered and read (SMIRKS §5.4
  hydrogen table, amide-formation and stereo-inversion examples, Chapter 6
  opening). No content from those pages was unusable. The two stereo
  diagrams on pp. 38–39 use a "π" glyph for the wildcard substituents in the
  rendering; the accompanying SMIRKS strings (`[* :n]`) are unambiguous
  and are what is cited.

---

## Appendix A — Quick-reference tables (from the manual)

**SMILES at a glance (§3.2):** atoms — organic subset unbracketed, else
`[...]`; bonds `- = # :` (single/aromatic omissible); branches `(...)`;
rings — digit closures, `%nn` above 9; disconnection `.`; no spaces.

**Generic / isomeric / unique / absolute (§3.1):** generic = graph only;
isomeric = + isotope/chiral specs; unique = the canonical generic SMILES;
absolute = the unique isomeric SMILES.

**SMARTS logical operators (§4.3), high → low precedence:**
`!` (not) → `&` (and, high) → `,` (or) → `;` (and, low); adjacent
primitives default to `&`.

**Aromatic atoms (§3.4.2):** C, N, O, P, S, As, Se, `*` only.

**Chiral classes (§3.3.4):** TH (tetrahedral, default degree 4), AL
(allene-like, default degree 2), SP (square-planar, `@SP1–3`, no shorthand),
TB (trigonal-bipyramidal, default degree 5, `@TB1–20`), OH (octahedral,
default degree 6, `@OH1–30`).

## Appendix B — Sources

- Weininger, D. *SMILES, SMARTS and SMIRKS: The Daylight Chemical
  Information System Theory Manual* (Daylight CIS), 57 pp.,
  `~/workspace/user/files/SMART__Molecular_Language.pdf`. Chapters cited:
  2 (molecules/reactions), 3 (SMILES), 4 (SMARTS), 5 (SMIRKS), 6
  (fingerprints). Further reading per the manual: Weininger, D.,
  "SMILES 1. Introduction and Encoding Rules", *J. Chem. Inf. Comput. Sci.*
  1988, 28, 31.
- Catalog targets: AGI-001–AGI-010 target list as stated in the program
  brief (p53/Bax, BIM/PUMA, Mcl-1, cIAP1/2, XIAP, Bcl-2/Bcl-xL, survivin,
  FLIP, Mdm2/p53); ALS paper biology (AGI-183 as BCL-XL stabilizer;
  AAV6-hSyn-MCL1) per `als-research-deep-dive.md` and
  `compound-agi183.md` in this same staging directory.

*No treatment, cure, diagnosis, or medical-device claim is made in this
document. All patterns are structural queries for a research compound
library; a pattern hit is a structural feature match, not evidence of
biological activity.*
