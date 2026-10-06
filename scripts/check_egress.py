#!/usr/bin/env python3
"""Every host this app can talk to, declared, and checked against the source.

The README promises that nothing leaves the machine except public database
lookups you trigger. That is the kind of claim a nonprofit's IT review, a
hospital's security questionnaire or a company's vendor assessment will ask you
to evidence, and "we looked and it seemed fine" is not evidence. It is also the
kind of claim that quietly stops being true: one CDN added for a font, one
analytics snippet, one telemetry ping, and the sentence in the README is a lie
nobody told deliberately.

So the hosts are declared here, and this script fails if the source contains one
that is not. A new endpoint cannot be merged without someone writing down what
it is for and what is sent to it.

    .venv/bin/python scripts/check_egress.py              # fail on anything undeclared
    .venv/bin/python scripts/check_egress.py --markdown   # the table for the docs

WHAT THIS CHECKS: hosts that appear as literal URLs in js/ and server/.

WHAT IT CANNOT CHECK: a URL assembled at runtime from parts, a host supplied by
the user, or anything a third-party script fetches once loaded. The last is the
real limit -- three.js is loaded from a CDN, and from that point the page is
trusting that CDN's contents. Declaring the host does not audit what it serves.
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# When each host is contacted. This distinction is what a reviewer actually
# cares about: "on boot" means merely opening the page tells that host you exist.
BOOT = "on load"
TRIGGERED = "only when you ask"
NEVER_AUTO = "only if you configure it"

# A URL in the source is not the same as a request. server/biotech_database_
# integration.py is a catalogue: it DESCRIBES 40-odd public databases, with a
# homepage URL for each, and contains no HTTP call at all -- one entry is
# annotated "No public API; not integrable". Lumping those in with endpoints
# that actually receive data would make the inventory look alarming and,
# worse, untrustworthy: a reviewer who checks one and finds it is never called
# stops believing the rest of the table.
CATALOGUE = "never contacted (listed in a directory only)"

#: host -> (when, what it is for, what is sent)
DECLARED = {
    # --- third-party code, fetched before anything else runs -----------------
    "cdn.jsdelivr.net": (
        BOOT, "three.js and its loaders (the 3D engine)",
        "Your IP and the requested file path. This is the one host contacted "
        "before you do anything, and it is the weakest point in the 'runs "
        "locally' claim: the page trusts whatever this CDN serves. Vendor the "
        "library to remove it."),

    # --- public biomedical databases, on demand ------------------------------
    "files.rcsb.org": (TRIGGERED, "PDB structure files", "The PDB id you asked for."),
    "data.rcsb.org": (TRIGGERED, "PDB entry metadata", "The PDB id you asked for."),
    "search.rcsb.org": (TRIGGERED, "PDB search", "Your search terms."),
    "alphafold.ebi.ac.uk": (TRIGGERED, "AlphaFold predicted structures", "A UniProt accession."),
    "www.ebi.ac.uk": (TRIGGERED, "ChEMBL, InterPro, PDBe and other EBI services",
                      "Identifiers and search terms."),
    "rest.uniprot.org": (TRIGGERED, "protein metadata", "A gene name or accession."),
    "pubchem.ncbi.nlm.nih.gov": (TRIGGERED, "compound identity, vendors, similarity",
                                 "A SMILES string, InChIKey, name or CID."),
    "clinicaltrials.gov": (TRIGGERED, "trial records", "An NCT number or search terms."),
    "api.fda.gov": (TRIGGERED, "drug label and adverse event data", "A drug name."),
    "string-db.org": (TRIGGERED, "protein interaction networks", "A protein identifier."),
    "reactome.org": (TRIGGERED, "pathway membership", "A protein identifier."),
    "rest.kegg.jp": (TRIGGERED, "pathway data", "A gene or pathway identifier."),
    "www.proteinatlas.org": (TRIGGERED, "expression data", "A gene name."),
    "pharos-api.ncats.io": (TRIGGERED, "target development level", "A target identifier."),
    "mygene.info": (TRIGGERED, "gene identifier resolution", "A gene name."),
    "search.foldseek.com": (TRIGGERED, "structural similarity search",
                            "The structure you are looking at, as coordinates."),
    "patents.google.com": (TRIGGERED, "patent lookup links", "Opened in a new tab; not fetched."),
    "api.platform.opentargets.org": (TRIGGERED, "target-disease evidence", "A target identifier."),
    "www.w3.org": (TRIGGERED, "XML namespace URIs in SVG output", "Nothing; never fetched."),

    # --- assets --------------------------------------------------------------
    "api.polyhaven.com": (TRIGGERED, "environment/texture catalogue listing",
                          "Nothing but the request itself; sent only when you search "
                          "the environment picker."),
    "dl.polyhaven.org": (TRIGGERED, "the environment file you picked",
                         "The asset name you selected."),

    # --- optional blockchain features, off unless you turn them on -----------
    "rpc.monad.xyz": (NEVER_AUTO, "reading an anchor back from Monad mainnet",
                      "A transaction hash. Only when you verify an anchor."),
    "rpc.testnet.monad.xyz": (NEVER_AUTO, "reading an anchor back from Monad testnet",
                              "A transaction hash. Only when you verify an anchor."),
    "monadscan.com": (NEVER_AUTO, "explorer links", "Opened in a new tab; not fetched."),
    "testnet.monadscan.com": (NEVER_AUTO, "explorer links", "Opened in a new tab; not fetched."),
    "docs.monad.xyz": (NEVER_AUTO, "documentation link recorded in chain_anchor",
                       "Nothing; a citation, never fetched."),
    "chainlist.org": (NEVER_AUTO, "documentation link recorded in chain_anchor",
                      "Nothing; a citation, never fetched."),
    "mcule.com": (NEVER_AUTO, "compound pricing",
                  "A structure identifier. Requires MCULE_API_KEY; unset means never contacted."),
    "cartblanche22.docking.org": (NEVER_AUTO, "ZINC purchasability",
                                  "A structure identifier. Rejected as a price source."),
    "api.molport.com": (NEVER_AUTO, "documented as a price source that was not used",
                        "Nothing; recorded as evidence, never called."),
    "api.chem-space.com": (NEVER_AUTO, "documented as a price source that was not used",
                           "Nothing; recorded as evidence, never called."),

    # --- LLM providers: only reachable if you point LLM_BASE_URL at one -------
    "api.z.ai": (NEVER_AUTO, "GLM models, if you set LLM_BASE_URL to it",
                 "Whatever prompt an agent module sends, which may include target names, "
                 "compound identifiers and run context. Nothing is sent unless LLM_API_KEY "
                 "and LLM_BASE_URL are both set; these hosts appear in server/llm_provider.py "
                 "as documented examples, not as defaults."),
    "api.openai.com": (NEVER_AUTO, "OpenAI models, if you set LLM_BASE_URL to it",
                       "As above. Listed as a known OpenAI-compatible base; never a default."),

    # --- additional endpoints that are genuinely called ----------------------
    "eutils.ncbi.nlm.nih.gov": (TRIGGERED, "PubMed search and record fetch (E-utilities)",
                                "Your search terms or a PMID."),
    "pubmed.ncbi.nlm.nih.gov": (TRIGGERED, "PubMed record lookup", "A PMID."),
    "www.ncbi.nlm.nih.gov": (TRIGGERED, "NCBI record lookup", "An identifier."),
    "www.uniprot.org": (TRIGGERED, "UniProt lookup (legacy host)", "A gene name or accession."),
    "www.rcsb.org": (TRIGGERED, "PDB entry lookup", "A PDB id."),
    "models.rcsb.org": (TRIGGERED, "computed structure models", "A model identifier."),
    "gnomad.broadinstitute.org": (TRIGGERED, "population variant frequencies", "A gene or variant."),
    "mychem.info": (TRIGGERED, "chemical identifier resolution", "A compound identifier."),
    "bindingdb.org": (TRIGGERED, "binding affinity data", "A target or compound identifier."),
    "europepmc.org": (TRIGGERED, "literature search", "Your search terms."),
    "doi.org": (TRIGGERED, "citation links", "Opened in a new tab; not fetched."),

    # --- catalogue entries: described, never called --------------------------
    "arxiv.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "www.biorxiv.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "www.medrxiv.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "www.semanticscholar.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "www.crossref.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "scholar.google.com": (CATALOGUE,
                           "listed in the directory and marked 'no public API; not integrable'",
                           "Nothing."),
    "geneontology.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "thebiogrid.org": (CATALOGUE, "listed in the directory; would need BIOGRID_ACCESS_KEY",
                       "Nothing."),
    "gtexportal.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "www.ensembl.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "www.kegg.jp": (CATALOGUE, "listed in the database directory", "Nothing."),
    "www.surechembl.org": (CATALOGUE, "listed in the database directory", "Nothing."),
    "open.fda.gov": (CATALOGUE, "listed in the database directory", "Nothing."),
    "platform.opentargets.org": (CATALOGUE, "listed in the directory; the API host is "
                                 "api.platform.opentargets.org", "Nothing."),
    "pumpscience.gitbook.io": (CATALOGUE, "cited as a source in the validation write-up",
                               "Nothing; a citation."),
    "nanda.media.mit.edu": (CATALOGUE,
                            "a JSON-LD @context URI in the AgentFacts document, like the w3.org one "
                            "beside it", "Nothing. server/agent_protocols.py contains no HTTP call; "
                            "the URI is a namespace identifier embedded in a dict, not a request."),
    "agifuturefoundation.org": (CATALOGUE,
                                "the provider URL and contact inside the AgentFacts document",
                                "Nothing; it is published metadata about who runs this node, never "
                                "fetched."),
}

URL = re.compile(r"""https?://([A-Za-z0-9.\-]+\.[A-Za-z]{2,})""")

SKIP_DIRS = {"node_modules", ".venv", ".git", "__pycache__", "assets", ".pytest_cache"}
SCAN_DIRS = ("js", "server", "scripts")
SCAN_EXT = (".js", ".mjs", ".py", ".html")


def sources():
    for name in (*SCAN_DIRS, "."):
        base = os.path.join(ROOT, name)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for filename in filenames:
                if filename.endswith(SCAN_EXT):
                    yield os.path.join(dirpath, filename)
            if name == ".":
                break          # top level only, to catch index.html / home.html


def found_hosts():
    hits = {}
    for path in sources():
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue
        for host in URL.findall(text):
            hits.setdefault(host, set()).add(os.path.relpath(path, ROOT))
    return hits


def markdown(hits):
    lines = ["| Host | When | What for | What is sent |",
             "| --- | --- | --- | --- |"]
    for host in sorted(DECLARED):
        when, purpose, sent = DECLARED[host]
        seen = "" if host in hits else " *(declared, not currently referenced)*"
        lines.append(f"| `{host}`{seen} | {when} | {purpose} | {sent} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--markdown", action="store_true",
                        help="print the egress table for the documentation")
    args = parser.parse_args()

    hits = found_hosts()

    if args.markdown:
        print(markdown(hits))
        return 0

    undeclared = {h: sorted(f) for h, f in hits.items() if h not in DECLARED}
    stale = [h for h in DECLARED if h not in hits]

    print(f"scanned {len(list(sources()))} files")
    print(f"declared hosts : {len(DECLARED)}")
    print(f"found in source: {len(hits)}")

    boot = [h for h, (when, _, _) in DECLARED.items() if when == BOOT and h in hits]
    print(f"\ncontacted on load (before you do anything): {len(boot)}")
    for host in sorted(boot):
        print(f"  {host}")

    if stale:
        print(f"\ndeclared but not referenced ({len(stale)}) -- harmless, possibly removable:")
        for host in sorted(stale):
            print(f"  {host}")

    if undeclared:
        print(f"\nUNDECLARED HOSTS ({len(undeclared)}):")
        for host, files in sorted(undeclared.items()):
            print(f"  {host}")
            for path in files[:3]:
                print(f"      {path}")
        print("\nEach of these can receive data from a user of this app, and none is "
              "written down. Add it to DECLARED in this script with what it is for and "
              "what is sent to it, or remove the call.")
        return 1

    print("\nno undeclared hosts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
