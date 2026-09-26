# biodao.blockchain

*powered by AGI Corp*

A molecular workspace for drug discovery that runs in a headset or an ordinary browser, in the spirit of
Nanome: pick up a protein, drop a compound into its pocket, pull the compound around while the physics
runs, and score the fit as you go. It is wired to live public databases and to your own AGI compound
collection, and it focuses on neurogenetic disease targets: ALS, Parkinson's, and the skeletal,
neuromuscular and burn-injury conditions Shriners Children's treats.

Everything runs locally. Nothing is uploaded, and no account or API key is needed to use it.

The precise version, because a claim like that is worth being able to check: **exactly one host is
contacted when the page loads** — `cdn.jsdelivr.net`, for the 3D engine. Everything else happens only
when you ask for it: a structure lookup, an environment, a literature search. Sign-in, payments and
on-chain anchoring are optional features that contact nothing unless you turn them on.

Every endpoint is declared, with what it is for and what is sent to it, and the build fails if one
appears that is not:

```bash
make egress          # or: .venv/bin/python scripts/check_egress.py --markdown
```

---

## Watch it first

`docs/biodao-walkthrough.mp4` is a two-minute walkthrough the app renders of itself, with every number on
screen coming from a real run. `docs/DEMO.md` has the demo running order and the talking points.

## Quick start

```bash
cd ~/Projects/agi-bioxr && .venv/bin/python server/server.py
```

Then open <http://localhost:8000>. The app loads SOD1 (the first ALS gene) so there is something to look
at immediately.

If the environment is not built yet:

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

To try the headset interface without a headset, open <http://localhost:8000/?emulate=quest3>. That loads a
WebXR emulator so "Enter VR" works on the desktop.

### In a real headset

Quest 3, Quest Pro and Vision Pro all work through their own browsers. WebXR needs a secure origin, so
either serve over HTTPS or tunnel the port.

**Over Wi-Fi (any headset):** start with a self-signed certificate and accept the browser warning once.

```bash
.venv/bin/python server/server.py --https --port 8443
```

**Over USB (Quest only, no certificate warning):**

```bash
adb reverse tcp:8000 tcp:8000
```

Then open `http://localhost:8000` inside the headset.

**Controls in the headset:** grip to move the molecule, both grips to scale and rotate it, trigger to pick
an atom or press a wrist-menu button. While dynamics are running, pulling the trigger on the ligand drags
it through the pocket and the structure pushes back. The wrist menu carries dynamics, docking, pockets,
style, colour and compound stepping, so you never need the desktop panels.

---

## Loading your compound collection

Your AGI compound PDFs live in Downloads and iCloud, where macOS blocks background access. Two ways in,
both of which sidestep that:

**In the browser.** Open the AGI library tab and drop the PDFs on the import box, or click Import. The
browser reads files you choose yourself, so no permission prompt is involved. PDFs, CSV, TSV, SMILES
lists, SDF and JSON all work.

**On the command line.**

```bash
.venv/bin/python scripts/extract_compounds.py ~/Downloads/"AGI Compounds 001-375.pdf" ~/Downloads/"AGI Corp - SMILES AGENT list.pdf"
```

The extractor handles the awkward parts of exported compound sheets: SMILES broken across two lines are
re-joined and re-validated, an index number glued to the front of a structure (`150CN1CC2=...`) is read as
the compound number, and IDs written as "AGI 001", "AGI-Compound-12" or a leading "001." are all
recognised. Every structure is validated with RDKit. Anything that looks like a SMILES but will not parse
is kept in a review list rather than silently dropped, and shown in the app under "Needs a human eye".

Apple Pages files cannot be read directly. In Pages choose File, then Export To, then PDF, and import that.

Scanned PDFs with no text layer hold pictures of structures rather than text. Those need optical chemical
structure recognition (DECIMER or OSRA) before anything can import them; the app tells you when it sees one.

Once imported, the library gives you: 2D depictions, molecular weight, cLogP, TPSA, hydrogen-bond counts,
rotatable bonds, Lipinski violations and a CNS score for likely brain penetration; substructure search with
one-click scaffold presets (purine, pyrimidine, benzothiazole, quinazoline and more); a novelty check that
asks PubChem whether a compound is already known and what the nearest known compounds are; and export to
CSV or JSON.

---

## What it does

**Structures.** Experimental structures stream from the Protein Data Bank, predicted ones from the
AlphaFold database, which covers essentially every human protein. Search accepts a gene name, a PDB id, a
UniProt accession, a disease or a SMILES string.

**Sixty curated targets**, every one verified against UniProt when the target file was built, grouped into
five programmes:

| Programme | Count | Examples |
| --- | --- | --- |
| ALS | 20 | SOD1, TDP-43, FUS, C9orf72, TBK1, VCP, STMN2 |
| Parkinson's | 13 | LRRK2, GBA1, alpha-synuclein, PINK1, parkin, MAO-B |
| Other neurogenetic | 10 | Huntingtin, SMN1, frataxin, MECP2, tau, dystrophin |
| Shriners Children's | 15 | Type I collagen, sclerostin, FGFR3, alkaline phosphatase, FGF23, Nogo-A |
| Apoptosis | 2 | BCL-XL, BCL-2 |

Rebuild or extend that list by editing `scripts/targets_seed.py` and running
`.venv/bin/python scripts/build_targets.py`. Any gene whose accession does not match is reported and
dropped rather than guessed at.

**Disease explorer.** Ask Open Targets which targets are associated with a disease and load any of them.
Amyotrophic lateral sclerosis alone returns over six thousand ranked associations.

**Evidence in one click.** The Evidence tab gathers, for the loaded target: InterPro domains, Reactome
pathways, STRING interaction partners, Human Protein Atlas expression, gnomAD population constraint,
Pharos development level, a gene summary from NCBI, ClinicalTrials.gov trials and Europe PMC literature.
Partners and trials are clickable, so a target opens its neighbours.

**Provenance ledger.** Every docking run, screen, simulation, import and evidence sweep is written into a
SHA-256 hash chain, each record covering the one before it. Verify re-hashes the chain and names the first
record that does not match; Export writes it out so the head hash can be anchored on-chain or in a DAO
proposal. It is a local hash chain, not a blockchain: nothing is broadcast and no consensus is involved.

**Known drugs.** For the loaded target, the app lists clinical drugs and candidates from Open Targets with
mechanism and trial stage, plus potent measured actives from ChEMBL. Click any of them and its 3D
structure comes from PubChem, ready to dock beside your own compound.

**Similar folds.** One button runs a Foldseek search of the current fold against the entire AlphaFold
database and the PDB, and every hit is clickable. Searching SOD1 returns a thousand AlphaFold relatives and
two hundred PDB entries, including SOD1 mutants and an ALS drug-candidate complex, in about twenty seconds.

**Variant effects.** For AlphaFold models the app pulls AlphaMissense scores and can colour the fold by how
damaging mutation at each position is. On SOD1 the known ALS hotspots stand out clearly: H46 scores 0.98
and A4 scores 0.89 against a 0.64 average.

**Interaction analysis.** After any pose, one click classifies every contact residue by residue: hydrogen
bonds, salt bridges, aromatic stacking (parallel and T-shaped), halogen bonds and hydrophobic contacts.
Aromatic rings are found geometrically when a ligand comes from a crystal and carries no cheminformatics
record. For AlphaFold models it also asks whether the pocket lining sits where mutations are poorly
tolerated, using AlphaMissense, and reports the enrichment against the rest of the protein.

**Selectivity.** Dock the same compound against related targets with identical settings and compare. A
compound that scores far better on its intended target than on its relatives is the one worth pursuing.

**Environments.** Load any glTF or GLB scene as a backdrop: Sketchfab downloads, Unreal's "Export All",
Unity glTF exports, or photogrammetry. Exports arrive at wildly different scales, so anything implausible
is normalised (a 2 m yacht becomes 40 m) and stood on the floor, with a manual override. Lighting comes
from Poly Haven's CC0 library. Heavy scenes get distance culling that follows the viewer, and in a headset
the backdrop is staged rather than walked. FBX, USD and .blend must be converted to glTF first.

**Voice, hands and agents.** Every panel action is also a named tool with a typed schema, so the same
nineteen operations can be typed as a sentence, spoken aloud, or called by an external agent over MCP
(`server/mcp_server.py`). In a headset, hand tracking replaces controllers: pinch to grab, two pinches to
scale, point to steer, swipe for the next compound, palm up for the menu.

**Pockets and docking.** Pocket detection finds and ranks cavities by volume and how buried they are, with
their lining residues. Docking is a flexible Monte Carlo search with rotatable bonds, scored by a
Vina-style empirical function, and it reports the score breakdown, hydrogen bonds, contact residues and
ligand efficiency. Hydrogen bonds are drawn in the 3D view.

**Virtual screening.** Dock the whole library against the current site and rank it. Scores are stored per
compound and the list sorts by them.

**Molecular dynamics, two kinds.**

- *Interactive*, in the browser at frame rate: the ligand is flexible all-atom, the protein moves on an
  elastic network model, and the two push on each other. You can grab the ligand and pull. About 23
  picoseconds of simulated time per second, and a 8,778-atom structure with a fully flexible backbone
  costs 7.4 ms per frame, which leaves headroom above headset frame rates.
- *All-atom*, on the local server: OpenMM with the Amber14 force field and GBn2 implicit solvent, using
  PDBFixer to repair the structure first. It reached 27 ns/day on this Mac's GPU. The finished trajectory
  plays back in the viewer.

**Shared sessions.** Several people can join a room and see the same molecules, each other's heads and
hands, and each other's structure and compound changes.

**Measurement.** Click two atoms for a distance, three for an angle, drawn in place.

---

## AlphaFold 3

AlphaFold 3 has no public programming interface. AlphaFold Server is a web application, and the model
weights are released by Google DeepMind for non-commercial use on request. So the app automates the two
parts that can be automated: it writes job files and reads results back.

- **Export AF3 job** writes the local AlphaFold 3 input format, protein chains plus your compound as a
  ligand SMILES. Run it with your own AF3 install.
- **Export AlphaFold Server job** writes the server's format. That service only accepts ligands from its
  own fixed list, so a custom SMILES is left out and the app says so.
- **Import AF3 result** reads the predicted structure back in, shows its confidence, and puts any predicted
  ligand in the same workspace as your docked pose for comparison. Predictions from Boltz or Chai load the
  same way.

## The databases

All free, none needing an account or key:

| Source | What it gives |
| --- | --- |
| RCSB PDB | experimental structures, ligands with bond orders, full-text and sequence search |
| AlphaFold DB | predicted structures for essentially every human protein, plus AlphaMissense |
| UniProt | sequences, accessions, gene names |
| Open Targets | disease-target associations, clinical drugs and candidates |
| ChEMBL | measured bioactivities and similarity search |
| PubChem | 100M+ known compounds, 3D conformers, similarity, exact-match novelty checks |
| Foldseek | structure search against AlphaFold DB and the whole PDB |
| InterPro | domains and families |
| Reactome | curated pathways |
| STRING | functional interaction partners |
| Human Protein Atlas | tissue and subcellular expression |
| gnomAD | population constraint (pLI, observed/expected loss of function) |
| Pharos / NCATS | target development level and druggability |
| ClinicalTrials.gov | trials by condition or intervention |
| Europe PMC | open literature, including preprints |
| openFDA | adverse event counts and label text for approved drugs |
| BioThings (MyGene, MyChem) | aggregated gene and chemical annotation |
| UniChem, KEGG, BindingDB, PDBe | cross-references, pathways, affinities, residue mappings |

A few of these send no CORS headers, so the browser cannot call them directly. The local server carries a
read-only proxy with a fixed allowlist of those hosts, and the app falls back to it automatically. Without
the server running, those specific sources are the ones that go quiet.

## Google datasets

The AlphaFold database is Google DeepMind's, and the app reads it live, including AlphaMissense. Open
Targets, also published as a Google BigQuery dataset, drives the disease and drug panels through its API.

The session tab has a direct BigQuery panel for the AlphaFold metadata table covering all 214 million
predicted structures. It stays switched off until you install the client and authenticate, and it is the
one feature here that has not been run end to end, because it needs your own Google Cloud project:

```bash
.venv/bin/pip install google-cloud-bigquery && gcloud auth application-default login
```

---

## How far to trust the numbers

Docking scores are a re-implementation of the AutoDock Vina scoring function for interactive use, not a
validated replacement for Vina or Glide. Treat them as a ranking, not a binding affinity.

There is now a benchmark rather than an anecdote. `node evals/redock.mjs` strips a ligand out of the
crystal structure it was solved in, docks it back blind, and measures the distance to the experimental pose:

| Complex | Top pose | Crystal score | Docked score | Result |
| --- | --- | --- | --- | --- |
| MAO-B with safinamide | 1.20 Å | −9.62 | −10.01 | pass |
| Oestrogen receptor with 4-hydroxytamoxifen | 1.24 Å | −9.24 | −10.13 | pass |
| Thrombin with an inhibitor | 3.83 Å | −11.03 | −8.34 | fail |
| BCL-XL with ABT-737 | 4.04 Å | −9.96 | −6.92 | fail |

**Two of four within 2 Å, median 2.54 Å.** The two failures are a large flexible ligand and a deep
charged pocket, which is where an empirical score and a short search struggle. Use the scores to triage a
library, not to predict affinity, and re-run this benchmark whenever the scoring function changes.

The interactive dynamics are deliberately coarse: harmonic bonds and angles rather than a published force
field, an elastic network for the protein, no explicit water and no electrostatics. It is for feeling how a
ligand sits and moves, not for computing free energies. Use the OpenMM backend for physics you would
publish, and note that it simulates the protein alone, since parameterising an arbitrary ligand needs
GAFF or OpenFF, which are not installed here.

Browser-side 3D structure generation relaxes a 2D depiction and does not enforce stereochemistry. When the
server is running, RDKit's proper conformer generator is used instead, and the ligand card says which one
produced the structure.

Pocket detection, drug-likeness rules and the CNS score are heuristics. The CNS score omits the pKa term of
the published six-parameter version, because pKa is not computed here.

---

## Layout

```
index.html              the app shell
css/app.css             styling
js/main.js              application: loading, docking, dynamics, screening, UI wiring
js/structure.js         PDB, mmCIF and SDF parsers, bonds, secondary structure, atom typing
js/render.js            three.js representations: cartoon, ball-and-stick, sticks, spacefill
js/md.js                interactive dynamics: ligand force field, elastic network, steering
js/dock.js              scoring function, pocket detection, Monte Carlo docking
js/chem.js              RDKit: descriptors, fingerprints, depiction, 3D embedding
js/compounds.js         the AGI library: import, search, profiling, export
js/api.js               data sources: PDB, AlphaFold, UniProt, Open Targets, PubChem, ChEMBL, Foldseek
js/af3.js               AlphaFold 3 job export and result import
js/xr.js                WebXR: controllers, gestures, wrist menu
js/collab.js            shared sessions
server/server.py        local server: 3D embedding, OpenMM, PDF extraction, rooms, BigQuery
server/chem_extract.py  SMILES extraction from document text
scripts/build_targets.py   rebuild data/targets.json from verified sources
scripts/extract_compounds.py  batch-import compound files
data/targets.json       the 60 curated targets, with sequences for AlphaFold 3 export
data/agi_compounds.json your compound library
```

## Keyboard

Space toggles dynamics, `d` docks, `p` finds pockets, `f` re-frames the view, `n` loads the next compound.

## If something does not work

The server prints which engines it found on startup. Without it the app still runs: chemistry falls back to
the browser, and 3D embedding, all-atom dynamics, server-side PDF reading and shared sessions switch off.

Public databases go down from time to time. ChEMBL in particular returns server errors for spells; the app
reports it and carries on. Everything else has no hard dependency on any single source.

## License

Proprietary. Copyright (c) 2026 AGI Corp / AGI Future Foundation, all rights reserved — see
[LICENSE](LICENSE). No right to use, copy, modify or distribute is granted without a separate written
agreement. Third-party dependencies keep their own licenses, and data retrieved from public databases is
governed by those databases' terms.

This is a research tool. It emits computational predictions and heuristics, and values it labels
`[SYNTHETIC]` are placeholders rather than measurements. Nothing it produces is a clinical, diagnostic or
dosing recommendation.
