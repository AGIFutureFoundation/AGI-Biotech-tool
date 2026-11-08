# Safety-Screening Brief — Hepatotoxicity Screening by Liver-Stem-Cell Molecular Profiling

**Status:** Published research brief in this repo's `research/` folder.
**Program:** Bio research expansion — safety-screening layer for the whole compound library.
**Subject:** U.S. Patent 8,512,957 B2, "Toxicity Typing Using Liver Stem Cells" (Snodgrass / Vistagen Therapeutics).

## What this brief is

A research-design brief built on a patented method, used as the lab's hepatotoxicity-screening layer. It describes a **method** for detecting and typing toxicity before a compound ever approaches human use. It makes no treatment, cure, diagnosis, or medical-device claim, and it proposes no compound for human use.

**This is a patent, not a paper.** Everything about the method below is patent-reported — what the inventor disclosed and claimed — not validated science. A patent grant means the USPTO found the claims novel, non-obvious, and adequately described as of examination; it is not peer review, not replication, and not evidence that the method works as described in independent hands. The validation the method would still need is spelled out in §6.

## 1. The patent — identity and verified legal status

| Field | Value |
|---|---|
| Patent | U.S. Patent 8,512,957 B2, "Toxicity Typing Using Liver Stem Cells" |
| Inventor | H. Ralph Snodgrass, San Jose, CA (US) |
| Assignee (as granted) | Vistagen Therapeutics, Inc., South San Francisco, CA (US) |
| Application No. | 13/401,623, filed Feb. 21, 2012 |
| Granted | Aug. 20, 2013 |
| Claims | 25 claims, 4 drawing sheets |
| Classifications | C12Q 1/68; C12N 15/74 (Int. Cl.); USPC 435/6.13; 435/6.1; 435/7.21; 435/7.7 |
| Priority chain | Provisional 60/211,606, filed Jun. 14, 2000 → non-provisional 09/881,526, filed Jun. 14, 2001 (abandoned) → continuation 11/445,733, filed Jun. 1, 2006 (granted as U.S. Pat. No. 8,143,009, Mar. 27, 2012) → divisional 13/401,623, filed Feb. 21, 2012 (this patent) |
| Patent term adjustment | 0 days (stated on the front page) |
| Pre-grant publication | US 2012/0220469 A1, Aug. 30, 2012 |

### Legal status — verified

**EXPIRED — fee related, effective 2025-08-20.** Google Patents lists US8512957B2 as **"Expired – Fee Related."** Checked 2026-11-07 (Google Patents page crawled 2026-11-08 00:57 UTC). Source: https://patents.google.com/patent/US8512957B2/en

Why: the 11.5-year maintenance fee was due 2025-02-20 (11.5 years after the 2013-08-20 grant) and was not paid; the 6-month grace period ended 2025-08-20, which is the recorded effective lapse date (USPTO-sourced Legal Events table: 2025-09-22 LAPS, "PATENT EXPIRED FOR FAILURE TO PAY MAINTENANCE FEES"). **Correction 2026-11-07:** an earlier draft of this brief quoted Google's "anticipated expiration 2021-06-14" — that figure is a Google miscalculation from the 2000-06-14 priority date and is WRONG: the patent demonstrably remained in force past that date (8th-year fee paid February 2021; 11.5-year fee reminder mailed April 2025). Do not quote 2021-06-14. **Revival window open:** a US patent expired for nonpayment may be reinstated on petition showing unintentional delay (37 CFR 1.378), generally within 2 years of the lapse — until about August 2027 for this patent. Re-check status before relying on expiry for any product or publication decision. Full record: `patent-status-verification.md` §2.

**Caveats, stated plainly:**
- Google Patents itself disclaims that its legal-status listing "is an assumption and is not a legal conclusion" and that Google "has not performed a legal analysis."
- Expiry of this patent does not mean the underlying territory is free to operate: other patents in the family or in the field (e.g., the parent U.S. Pat. No. 8,143,009 and foreign counterparts) may have different terms and statuses, and freedom-to-operate requires its own clearance. No freedom-to-operate opinion is offered here.
- Before any reliance on expired status (e.g., in a filing, a partnership, or a publication), confirm against the authoritative record in the USPTO Patent Center (linked from the Google Patents page). That confirmation has not been done in this brief.

**Practical consequence for the lab:** because the patent is expired, the lab is not relying on a license to use the *disclosed method as a research design*. The method is treated here as prior-art knowledge and design inspiration. That does not remove the need for the lab's own validation (§6), nor does it authorize use of any proprietary reagents, cell lines, software, or data that the patent references (e.g., Ciphergen SELDI/ProteinChip systems, which are commercial products with their own terms).

## 2. The Snodgrass method — as patent-reported

### The problem it addresses

The patent's background states that drug toxicity to the host system is a rate-limiting step in translating drug candidates from laboratory to clinic, that roughly a third of prospective human therapeutics fail in first-phase human clinical trials because of unexpected toxicity (as stated in the patent), and that existing alternatives — single-reporter cell lines, animal testing, and narrow gene-panel assays — are expensive, slow, miss toxicities, or fail to capture interactions among cell types and tissues. The liver, the patent notes, is where toxicity effects are most frequently and severely manifested because of its detoxification role.

### The core idea

Expose **isolated mammalian liver stem cells (LSCs)** to a chemical composition, detect **alterations in gene or protein expression** relative to untreated controls, and use the resulting **molecular profile** as a fingerprint of that compound's toxicity. By building a reference library of profiles from compounds of *known* toxicity and comparing an unknown compound's profile against it, the type of toxicity can be identified ("typed") and new compositions screened.

The patent's abstract, verbatim in substance: the invention "provides methods and systems for identifying and typing toxicity of chemical compositions, as well as for screening new compositions for toxicity. The invention involves detecting alterations in gene or protein expression and hence establishing molecular profiles in isolated mammalian LSCs contacted with various chemical compositions of known and unknown toxicities, and correlating the molecular profiles with toxicities of the chemical compositions."

### The method, step by step

1. **Isolate liver stem cells (LSCs).** Mammalian liver progenitor/stem cells — human or non-human (rodent, murine, canine, feline, porcine, bovine, caprine, equine, ovine, per the specification). The patent's examples use rat-derived cells: large (~30 µm diameter) acidophilic cells separated by Percoll gradient centrifugation, and progenitor cells isolated per Faris, PCT Publication WO00/03001, with enrichment by antibody/magnetic-bead or FACS sorting for markers such as CK19, CCAM, and dipeptidyl peptidase-4.
2. **Contact with the test composition.** Plate LSCs at high density (e.g., 50,000–100,000 cells/cm² per well) on type I collagen-coated wells and expose to the compound. Include a medium-only control group and, where appropriate, reference compounds of known toxicity.
3. **Expose over time.** The patent's protein-expression example exposes cells for about 10, 20, 30, and 40 days before harvest (long-term culture with differentiation), with cytoplasmic and nuclear lysates also taken at day zero as additional controls.
4. **Build a molecular profile.** Detect alterations in gene expression (e.g., cDNA microarrays) or protein expression (e.g., SELDI mass spectrometry) in the exposed LSCs compared with LSCs in contact with culture medium only.
5. **Compile a reference library.** Repeat the process with two or more compositions of known/predetermined toxicity; identify sets of *commonly altered* genes or proteins for compounds of similar toxicity type; store the profiles (the patent contemplates computer-readable media and a database). Claim 25 specifies a library of at least 20 chemical compositions.
6. **Compare and type.** Compare the unknown compound's profile with the library; where common alterations in protein/gene expression between the unknown's profile and a known-toxicity profile indicate a potential correlation, predict the type of toxicity of the unknown compound.
7. **Screen and select.** Use the prediction to screen new compositions and to select compounds for preclinical animal studies — specifically, per claim 23, selecting compositions of unknown toxicity that show a potential correlation with *less toxic* compounds for preclinical animal studies. Claim 24 covers doing the prediction by high-throughput screening.

### Detection and analysis, as disclosed

- **Gene expression:** cDNA microarrays (e.g., a collection of 15,000 sequence-verified human clones and 8,700 mouse clones), fluorescent cDNA probes (Cy3/Cy5), hybridization, confocal laser scanning; normalization to a panel of ~15 "housekeeping" genes; analysis with packages such as SpotFire and GeneSpring; outlier genes validated by Northern blot or RT-PCR. Each drug tested at least three times on separate LSC cultures; results averaged with mean and SEM. The patent itself notes cDNA microarray technology "is still being validated as a viable technique for providing quantitative data."
- **Protein expression:** Ciphergen SELDI mass spectrometry (MS)-TOF on ProteinChip arrays; lysates fractionated on spin columns (e.g., 30 kD cut-off); internal reference standards subtracted; average fold change and variability reported; typical coefficient of variation under 20% as stated in the patent. Each drug analyzed on at least 3 separate groups of LSCs, on average 6 ProteinChips per test compound.
- **Labels (claim 3):** fluorescent, colorimetric, radioactive, enzyme, enzyme substrate, magnetic, glass, latex bead, colloidal gold, electronic transponder; detection also by immunoactivity assay (claim 4) or mass spectrometry assay (claim 5).
- **Scope of compounds:** therapeutic agents or potential therapeutics, neurotoxins, hepatic toxins, hematopoietic toxins, myotoxins, carcinogens, teratogens, reproductive-organ toxins; also agricultural chemicals, cosmetics/cosmeceuticals, industrial wastes, environmental contaminants, and animal therapeutics.

### Worked examples in the patent

- **Example 2 (protein expression):** troglitazone — described as a diabetes drug with rare but severe liver toxicity, removed from the market — at ~20 µM; erythromycin estolate — a form of erythromycin with known liver toxicity — at ~50 µM; a third group cultured without added drugs as control; medium-only plates as a degradation control. Lysates analyzed by SELDI; profiles plotted as test-minus-control against molecular weight (Figures 1–2).
- **Example 3 (anti-cancer drug screening):** a Table 3 panel of anti-cancer and therapeutic agents with known toxicities and mechanisms (alkylators, anti-metabolites, CdK inhibitors, DNA intercalators, DNA synthesis inhibitors, topoisomerase I/II inhibitors, tubulin inhibitors, immunosuppressants), used to compile gene/protein expression profiles in LSCs and correlate them with clinical outcomes. Toxicity columns cover developmental, gastro-intestinal, cardiovascular, central nervous system, and blood categories.

### What the claims cover (25 claims, summarized)

- **Claim 1** (independent): a first-pass method of predicting the type of toxicity of a chemical composition of unknown toxicity — contact isolated mammalian LSCs; create a molecular profile of protein-expression alterations vs. medium-only control; compare against sets of commonly altered proteins from known-toxicity compounds; predict toxicity where common alterations indicate a potential correlation.
- **Claims 2–5:** detection by label (claim 3 lists label types), immunoactivity assay, mass spectrometry assay.
- **Claims 6–8, 9–12:** human-origin LSCs (claim 6) and non-human mammalian, including rodent, LSCs (claims 9–10), with reference compounds drawn from reproductive-organ toxins/teratogens/carcinogens or from agricultural chemicals/cosmetics/environmental contaminants.
- **Claim 13:** a method of generating a library of molecular profiles (≥2 profiles, computer-readable media).
- **Claim 14** (independent): a systematic method of typing toxicity by comparing a gene-expression profile against the claim-13 library. **Claims 15–22** narrow it by compound type and LSC origin.
- **Claim 23:** screening chemical compositions for liver toxicity preclinical animal studies (predict per claim 14, then select). **Claim 24:** high-throughput screening. **Claim 25:** library of at least 20 chemical compositions.

## 3. Role in this program — the hepatotoxicity-screening layer

**Design decision (proposed plan, not filed fact):** the Snodgrass method is adopted as the lab's **hepatotoxicity-screening layer for the whole compound library, including any psychedelic compounds**. Every compound the lab proposes gets a hepatotoxicity screen design built on this approach before it advances further in the program.

What that means in practice:

- **Universal gate.** No compound — psychedelic or otherwise — advances past the proposal stage without a screen design on file: reference compounds, controls, dose range, exposure window, readout platform, replication, and a pre-stated decision rule.
- **Screening, not clearance.** A screen result is a *signal* that types and ranks toxicity risk. It is not a safety finding, not a substitute for GLP toxicology, and not a basis for human use. A clean screen does not clear a compound; a dirty screen kills or re-routes it.
- **Library logic.** The value of the method is cumulative: each screened compound, with its known-toxicity references, enlarges the lab's own profile library, so later comparisons get sharper. The lab's library is its own data asset, built compound by compound.
- **Psychedelic compounds included, not exempted.** Any psychedelic compound the lab proposes is screened under the same layer, under the same rules, with the same documentation — no exceptions, no fast track.

## 4. Screen design template (per compound)

For every proposed compound, the screen design must state, in writing, before work begins:

| Element | Design requirement |
|---|---|
| Compound | Identity, purity, source, batch; dose range with rationale (anchored to any known exposure data; otherwise a range-finding run first) |
| Test system | LSC source and species (human vs. non-human; justify the choice); isolation and enrichment method; passage/differentiation state; plating density |
| Reference set | At least two known-toxicity reference compounds matched to the toxicity types of concern, plus at least one known non-hepatotoxic comparator; a medium-only control; a vehicle control if a vehicle is used |
| Exposure | Duration and sampling points (the patent's example uses ~10–40 days; the design must justify its window for the compound and the question) |
| Readout | Gene-expression platform, protein-expression platform, or both — named explicitly, with the modern equivalent of the patent's disclosed platforms (see §6) |
| Replication | Minimum three independent LSC cultures per condition, as in the patent; triplicate array hybridizations where microarrays are used; pre-stated handling of outliers |
| Analysis | Normalization method (housekeeping panel or equivalent); statistical comparison vs. controls; fold-change and variability reporting; the comparison rule against the reference library |
| Decision rule | Pre-stated thresholds for advance / repeat with modifications / stop, written before results are seen |
| Records | Full protocol, raw profiles, analysis code/parameters, and the decision taken — filed with the compound's dossier |

## 5. Limits of the method as disclosed

- **In vitro only.** LSC cultures are not a liver, not an organism, and not a human. The patent itself acknowledges that cell lines "may not fully take into account the complex biology of an intact organism or tissue" — its argument is that LSCs do better than single-reporter lines, not that they replace in vivo work.
- **Correlation, not causation.** The method predicts toxicity *type* by profile similarity to known-toxicity compounds. Similarity of expression profiles is a correlation signal; it does not establish mechanism, dose–response in vivo, or clinical risk.
- **Reference-library dependence.** The method is only as good as its library. With a thin or biased reference set, comparisons are meaningless. Claim 25's floor (≥20 compounds) is a starting point, not a validated standard.
- **Platform vintage.** The disclosed platforms — cDNA microarrays with Cy3/Cy5, Ciphergen SELDI/ProteinChip MS-TOF, SpotFire/GeneSpring — are 2000s-era technology. Modern equivalents exist (RNA-seq, LC-MS/MS proteomics), but substituting them is a *new method choice* that needs its own validation, not a drop-in replacement.
- **Long exposures, slow turnaround.** The patent's example exposures run ~10–40 days. This is not a same-day screen; throughput and cost must be planned accordingly (claim 24 notwithstanding).
- **No human-use inference.** Nothing in the patent supports a claim that a screened compound is safe in humans, effective for any condition, or suitable for human administration. The method's claimed endpoint is selection *for preclinical animal studies* — the earliest step, not the last.

## 6. Validation the method itself would need

Because this is a patent and not validated science, the lab must treat the method as a **hypothesis to be validated in-house** before any screen result is trusted for decisions. Required validation work, in order:

1. **Positive/negative control calibration.** Reproduce the patent's logic with known hepatotoxicants (e.g., troglitazone-class and erythromycin-estolate-class references, as disclosed) and known non-hepatotoxic comparators. Pre-state the expected profile direction for each. If the lab cannot reproduce separation between known-toxic and known-benign compounds, the method is not usable here.
2. **Sensitivity and specificity.** Across a panel of compounds with known human liver outcomes, measure how often the screen correctly types toxicity (sensitivity) and how often it clears benign compounds (specificity). Report both with confidence intervals; a screen that flags everything is as useless as one that flags nothing.
3. **Reproducibility.** Same compound, same design, different days, different operators, different LSC batches. Quantify between-run variability; the patent's stated SELDI CV of under 20% is a patent-reported figure, not a lab-measured one.
4. **Cross-platform equivalence.** If the lab uses RNA-seq and/or LC-MS/MS instead of the patent's microarrays and SELDI, demonstrate that the modern platform recovers the same reference separations. Do not assume equivalence.
5. **Species and cell-source bridging.** If the lab uses rodent LSCs for throughput and human LSCs (or human hepatocyte-derived systems) for relevance, show concordance — or state explicitly which system's results govern which decision.
6. **Blinding and pre-registration.** Screen designs, reference sets, and decision rules are written and filed before results are seen. Analysts are blinded to compound identity where feasible. Deviations are logged, not silently corrected.
7. **Concordance with in vivo data.** Where animal data exist for a compound, compare screen predictions against them prospectively and report the hit rate. A screen that never predicts an in vivo finding is decoration.
8. **External replication.** Before any external claim is made about the screen's performance, an independent laboratory or collaborator reproduces the core result on a shared compound set.

**Regulatory note:** even a fully validated screen is an early, non-GLP research tool. IND-enabling toxicology still requires GLP studies in accepted models, under FDA oversight. This screen informs which compounds deserve that investment; it never replaces it.

## 7. Regulatory lines

- Psychedelic compounds are Schedule I controlled substances federally. Screening a compound in LSC culture is laboratory research; it is not treatment, not a therapy, and not an offer of either.
- No compound in this program is proposed for human use. Any future human-use proposal requires its own stated regulatory path (FDA IND, DEA registration, IRB approval, state authorization as applicable) and is out of scope for this brief.
- No claim is made that any psychedelic compound treats, cures, or diagnoses any condition, or that hepatotoxicity screening makes any compound safe for human use.

## 8. Sources and dates

- U.S. Patent 8,512,957 B2, "Toxicity Typing Using Liver Stem Cells," Snodgrass (Vistagen Therapeutics, Inc.), granted Aug. 20, 2013; Appl. No. 13/401,623, filed Feb. 21, 2012. Local file: `~/workspace/user/files/Toxicity_typing_using_liver_stem_cells.pdf` (28 pages; all pages are scanned images — front page, specification pp. 1–2 and 31–40, Figures 1–2, and claims pp. 37–40 were rendered and read, 2026-11-07).
- Legal status verified via Google Patents, https://patents.google.com/patent/US8512957B2/en — "Expired – Fee Related," effective lapse 2025-08-20 (11.5-year maintenance fee unpaid; revival possible to ~Aug 2027); checked 2026-11-07 (page crawled 2026-11-08 00:57 UTC). Google disclaims the status as an assumption, not a legal conclusion. Authoritative confirmation via USPTO Patent Center is still outstanding and is required before any reliance. (Correction 2026-11-07: Google's "anticipated expiration 2021-06-14" is a miscalculation — do not quote it; see patent-status-verification.md §2.)
- Related family member noted in the patent: U.S. Pat. No. 8,143,009 (parent, granted Mar. 27, 2012). Its status was not checked in this brief.
- This brief was staged 2026-11-07. It is a draft for internal program use.

---

*Merged from inspiration-bio-patents.md, 2026-11-07 — inspiration layer; hypotheses + designs, not results.*

# Section 2 — Toxicity screening: the liver-stem-cell molecular-profile idea

**MERGE TARGET: `brief-toxicity-screening.md` (add as an inspiration section; the brief itself is
being written by a parallel worker — this section merges after it lands).**
**Inspired by: Snodgrass US 8,512,957 B2 — "Toxicity typing using liver stem cells" (inventor
H. Ralph Snodgrass; assignee Vistagen Therapeutics, Inc.; granted Aug. 20, 2013; 25 claims, 4
drawing sheets. Filed Feb. 21, 2012 as a division of application 11/445,733 (filed Jun. 1, 2006,
now US 8,143,009), continuation of 09/881,526 (filed Jun. 14, 2001), provisional 60/211,606
(Jun. 14, 2000). Term and current in-force status NOT independently verified — do not assume
expired or in force from the grant date; a USPTO register check is required before any use.)**

## 2.0 Core mechanism (the idea, faithful to the source)

The patent's idea is **toxicity typing by molecular profile in a differentiating liver progenitor
system**. Isolated mammalian **liver stem cells (LSCs)** — pluripotent progenitor cells, preferably
hepatoblasts isolated from the embryonic hepatic diverticulum of the foregut (also isolable from
adult liver as stem-like cells), capable of differentiating into hepatocytes, bile-duct cells,
liver endothelial cells, and Ito cells — are exposed to a chemical composition, and the resulting
**alterations in gene expression or protein expression, relative to control LSCs grown in medium
only, are recorded as that composition's "molecular profile."** The readouts are gene-expression
arrays and, preferably, **mass spectrometry of proteins** (the patent's Figures 1–4 are mass-spec
protein profiles: small/large nuclear proteins and cytoplasmic proteins, test compositions I and
II vs control, with the differences between test and control isolated by subtractive quantitation).
The method's second half is a **reference library**: molecular profiles are compiled for
compositions **with predetermined toxicities** — the patent's Table 1 lists known drugs and
compounds by the tissues/organs in which they exert toxicity (liver, developmental, cardiovascular,
CNS, blood), including thalidomide, methotrexate, valproic acid, acetaminophen, isoniazid,
troglitazone, rosiglitazone, trovafloxacin, clozapine, doxorubicin, and cyclophosphamide, plus
environmental compounds (carbon tetrachloride, cadmium, lead, benzo(a)pyrene, methylmercury,
dioxins, PCBs). A test composition is **typed by comparing its profile to the library**: compounds
with similar toxicities share common alterations — some genes/proteins similarly up-regulated,
others similarly down-regulated — and those shared features become surrogate markers for assessing
the toxicity of a new or untested composition, and for ranking it among known toxic compositions.
The patent also claims: LSCs in array format; integrated systems (array reader + database of
profiles + correlation program, capable of reading more than 500 labels in an hour); dose
bracketing (normal/medium concentration bracketed by twofold or fivefold increases and decreases);
staging the exposure at different points of LSC differentiation; and species-matched controls
(mouse/rat preferred for preclinical correlation, primate/human most preferred for human relevance).
Its stated advantages over single-reporter cell lines, embryonic stem cells, and animal testing are
that LSCs are relatively easy to isolate and expand, avoid some ES-cell ethical/sourcing problems,
model a multi-lineage differentiating system rather than one cell type, and — because LSCs can be
isolated from live individuals (needle or small wedge biopsy) — could in principle support
individual-patient toxicity profiling. The test compositions in the patent's own figures are
**unnamed** ("Test Composition I" / "Test Composition II"), so no compound-specific result can be
quoted from this document.

**What this mechanism suggests for us:** a **pre-animal safety gate** for every compound set we
work with — profile first, rank against known-toxicity references, and only then decide what
deserves scarce animal or human-facing attention. The three directions below build that gate for
our actual compound sets.

## 2.1 Inspired direction — A toxicity-signature screen for the 40 repurposed Alzheimer's drugs (and their pairs)

**Inspired by Snodgrass US 8,512,957 B2 (molecular-profile library + typing by comparison).**

- **Hypothesis (Grade C — no data):** Each of the 40 repurposed drugs in the Pharnext patent —
  and each of the six two-drug combinations in §1.2 — produces a distinct LSC molecular profile,
  and any profile that **clusters with the reference set of known hepatotoxic compounds** (e.g.
  troglitazone, acetaminophen, methotrexate, from the Snodgrass Table 1 category) flags a
  liver-liability candidate **before** any animal work, while profiles clustering with the
  non-toxic/control references clear the compound for the next gate. The screen's value is
  comparative (profile-vs-library), not absolute: a single compound's profile means nothing
  without the reference library beside it.
- **Grounding note — library reality check:** there is **no compound-library data file** in our
  program today. `brief-als.md` establishes that the AGI compound library exists only as ALS
  Researcher ACP job listings, an agent site, and staged articles — no molecule file, no screening
  data on disk — and that no library size or contents may be quoted. This direction is therefore
  designed against an **enumerated, finite set** (the 40 named Pharnext drugs + the 6 pairs), not
  against "every compound in the validated library." A library inventory file must exist before
  any screen can be described as screening "the library."
- **Experimental design:** (a) Build the reference library first: LSCs (species-matched, human
  preferred for human relevance per the patent; rodent as the preclinical bridge) exposed to a
  pre-registered reference panel — known hepatotoxic (troglitazone, acetaminophen), known
  non-hepatotoxic at therapeutic exposure, and vehicle controls — at bracketed doses (twofold /
  fivefold around the expected exposure, per the patent's dosing section); (b) profile by mass
  spectrometry (the patent's preferred readout) and/or gene-expression array; (c) expose LSCs to
  each of the 40 drugs alone and each of the 6 pairs, at the patent-proposed sub-therapeutic
  concentrations and at bracketed multiples; (d) type each test profile by similarity to the
  reference library (pre-registered similarity metric and clustering rule, with blinding); (e)
  include the patent's staging idea: expose at the undifferentiated stage and at a
  differentiation-committed stage, and record whether the profile differs by stage.
- **Falsification test:** the direction is killed if the **reference compounds do not separate**
  — i.e. known hepatotoxic and known non-hepatotoxic references produce profiles that are
  indistinguishable by the pre-registered metric (no clustering) — because then the method cannot
  type toxicity in our hands at all. It is also killed for the pairs if combination profiles are
  **not predictable from, and not distinguishable beyond, the sum of the singles' profiles** in a
  way the metric can resolve (the screen cannot type combinations, only singles). A reference
  library that separates cleanly but flags every test compound as hepatotoxic is a different
  failure — assay oversensitivity — and also kills the screen as designed (recalibration or a
  different readout is required, not a re-interpretation).
- **Evidence grade: C.** The patent's mechanism is Grade A (patent-reported); no LSC profile
  exists for any of our compounds.

## 2.2 Inspired direction — An LSC pre-screen as a safety gate for the ALS / BCL-2 program, using the MCL1-inhibitor failure history as the caution

**Inspired by Snodgrass US 8,512,957 B2 (typing by comparison against predetermined-toxicity
references, including cardiovascular-toxicity categories) read against the ALS paper's MCL1
failure history (brief-cancer-dao.md §2 Strand B).**

- **Hypothesis (Grade C — no data):** The ALS program's BCL-2-family compounds can be
  pre-screened in LSCs for a toxicity-associated signature **before** any in-vivo step, by
  comparing their LSC molecular profiles against reference profiles of compounds with known
  cardiovascular toxicity (the Snodgrass Table 1 cardiovascular category) — because the oncology
  history that motivates the ALS program's tissue-targeted design is a toxicity history: systemic
  MCL1 inhibition failed in cancer trials on on-target cardiotoxicity (AZD5991: high-sensitivity
  troponin T elevated in 54/65 (83%) patients after any dose in a post hoc analysis of stored
  samples vs 14/31 (45%) pre-dose; prospectively reported troponin elevations 8/78 (10.3%);
  response 3/78 (3.9%), all in MDS — corrected framing per verification 2026-11-07). A compound
  whose LSC profile clusters with known cardiotoxic references is deprioritised; one that clusters
  with non-toxic references advances. The LSC screen is a **liver-progenitor** system being asked a
  cardiovascular question — that cross-organ reach is exactly what this direction tests.
- **Experimental design:** (a) Reference panel: LSC profiles for compounds with predetermined
  cardiovascular toxicity and for matched non-cardiotoxic controls, from the Snodgrass Table 1
  categories and from the MCL1-inhibitor record where a compound is obtainable for in-vitro use;
  (b) test profiles for the ALS program's named therapeutic concepts (BCL-XL stabilisation as in
  the ALS paper's AGI-183; MCL1 gain-of-function as in the AAV6-hSyn-MCL1 arm) at bracketed
  doses, in the same LSC system and species as the references; (c) pre-registered similarity
  metric and a pre-set clustering threshold; (d) a positive control for the cross-organ question:
  a compound with known cardiovascular toxicity but no known liver toxicity, to test whether the
  LSC system detects it at all.
- **Falsification test:** the direction is killed if the positive control fails — i.e. LSC
  profiles of known cardiotoxic vs non-cardiotoxic reference compounds **do not separate** by the
  pre-registered metric — because that outcome shows the LSC system cannot serve as a
  cardiac-liability gate in our hands, whatever it can do for liver toxicity. It is also killed if
  the ALS test compounds' profiles are **indistinguishable from vehicle** at all bracketed doses
  while the same compounds are active in their neuronal assays (the LSC system is blind to this
  compound class, not evidence of safety). **A null LSC result is never reported as "safe"** —
  it is reported as "no signal in this system," and the compound still requires its own
  cardiac-specific assessment.
- **Evidence grade: C.** The MCL1 failure figures are **Grade B** (verified 2026-11-07, corrected
  framing); the LSC screen's ability to detect cardiotoxicity is an untested hypothesis. Do not
  present the AZD5991 figures as our data — they are oncology clinical history synthesised in the
  ALS paper.

## 2.3 Inspired direction — Donor-specific LSC toxicity profiles (individual sensitivity)

**Inspired by Snodgrass US 8,512,957 B2 (LSCs isolable from live individuals by needle or wedge
biopsy, "providing a means to enable the development of toxicity profiles for individual patients
or patient populations that have unique drug sensitivities").**

- **Hypothesis (Grade C — no data):** LSCs derived from different donors produce
  **donor-specific** molecular profiles for the same compound — i.e. inter-donor profile variance
  exceeds technical replicate variance — so that a compound's toxicity profile is partly a property
  of the donor, not only of the compound. If true, donor-stratified LSC profiling becomes a
  research tool for understanding variable drug sensitivity; if false, a single-donor LSC line is
  sufficient for screening and donor variation adds nothing.
- **Experimental design:** (a) A multi-donor LSC panel (minimum pre-registered donor count, with
  donor consent, ethics approval, and sourcing documented before any work — this direction may
  not proceed without those); (b) each donor's LSCs exposed to the same compound at the same
  bracketed doses, with technical replicates nested inside each donor; (c) mass-spec protein
  profiles (and/or gene-expression arrays) per the patent's readouts; (d) variance decomposition:
  inter-donor variance vs intra-donor technical variance, pre-registered, for a pre-registered
  compound set (start with two compounds of known, contrasting toxicity from the reference
  library in §2.1); (e) a same-donor, different-batch control to separate donor effects from
  batch effects.
- **Falsification test:** the direction is killed if **inter-donor variance is not greater than
  technical replicate variance** for any tested compound — there is no donor signal to exploit,
  and donor-stratified profiling is dropped. It is also killed if donor differences track
  **batch or passage number** rather than donor identity (the same-donor different-batch control
  separates these) — the signal was an artefact, not biology. Either outcome ends the direction;
  neither outcome licenses a claim about individual patient risk, which would require clinical
  correlation data that do not exist.
- **Evidence grade: C.** The patent's individual-profiling passage is a **proposal in a patent
  specification** (Grade A as patent text, not as evidence); no donor-stratified LSC data exist.
  Governance flag: human LSC sourcing, consent, and ethics approval are preconditions, not
  paperwork to be added later. No patient-facing claim may be made from this direction at any
  stage.
