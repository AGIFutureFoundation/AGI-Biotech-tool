# Data Sources

Twenty-one public databases, all free, none requiring a key. This page lists every host the client will
ever contact, because "what does this send where" is a fair question to ask of a research tool.

## Structures and folds

| Source | Used for |
| --- | --- |
| `files.rcsb.org`, `data.rcsb.org`, `models.rcsb.org`, `search.rcsb.org` | Experimental structures, metadata, computed models, text and shape search |
| `alphafold.ebi.ac.uk` | AlphaFold models with per-residue pLDDT confidence |
| `search.foldseek.com` | Structural similarity search across AlphaFold DB and the PDB |

## Genes, proteins and expression

| Source | Used for |
| --- | --- |
| `rest.uniprot.org` | Canonical sequence, domains, isoforms, cross-references |
| `mygene.info` | Gene symbol resolution across naming conventions |
| `www.proteinatlas.org` | Tissue and cell-type expression |
| `www.ebi.ac.uk` | InterPro domains and related EBI services |

## Variants

| Source | Used for |
| --- | --- |
| `gnomad.broadinstitute.org` | Population allele frequencies |

AlphaMissense pathogenicity scores are used for the `colour by missense` view; a residue with no score is
drawn as having no score, not as benign.

## Pathways and interactions

| Source | Used for |
| --- | --- |
| `reactome.org` | Curated pathways |
| `rest.kegg.jp` | Pathway maps |
| `string-db.org` | Protein-protein interaction networks |

## Chemistry

| Source | Used for |
| --- | --- |
| `pubchem.ncbi.nlm.nih.gov` | Compound identity, SMILES, properties, synonyms |
| `mychem.info` | Cross-referenced chemical annotation |
| `bindingdb.org` | Measured binding affinities — real numbers, with units, unlike the docking score |

## Targets, drugs and trials

| Source | Used for |
| --- | --- |
| `api.platform.opentargets.org` | Target-disease association evidence |
| `pharos-api.ncats.io` | NIH target development level, the "how druggable is this" question |
| `clinicaltrials.gov` | Registered trials for the loaded target |
| `api.fda.gov` | openFDA approvals and adverse event reports |

## How requests are made

**On page load, exactly one host is contacted:** the CDN serving three.js at its pinned version. Nothing
else is fetched until you ask for something that needs it.

Databases that refuse cross-origin requests are reached through `/api/proxy` on the local server, which
has an **allowlist**. A host not on the list is refused, not forwarded. `make egress` walks the source and
fails if any outbound host appears in code without being declared — so this page cannot silently fall out
of date with what the code actually calls.

Nothing about your session, your compounds, or your structures is sent anywhere except to the database
being queried, and the queries are the obvious ones: a gene symbol, a PDB identifier, a SMILES string.
There is no analytics, no telemetry, and no account.

## When a source is unavailable

A failed lookup is reported as a failed lookup. The panel says the source could not be reached; it does not
fall back to a cached guess and present it as current, and it does not fill the gap with a plausible
number. An empty field means nobody knows, or nobody could be asked.

## Verifying this page

```bash
make egress        # every outbound host in the source is declared
make reachable     # no orphaned module
```

See [Known Limits](Known-Limits) for what happens to all of this with no network at all.
