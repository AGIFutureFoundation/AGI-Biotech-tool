#!/usr/bin/env python3
"""Seed the compound library with known reference drugs so the demo has something to screen.

These are public, approved or clinical-stage molecules relevant to the target programmes, pulled from
PubChem by name and profiled with RDKit. They are labelled REF-nnn and tagged "reference", so they are
never confused with the AGI compound collection. Import your own compounds with
scripts/extract_compounds.py and they sit alongside these with AGI ids.

    .venv/bin/python scripts/seed_demo_library.py          # add reference set
    .venv/bin/python scripts/seed_demo_library.py --fresh  # replace the library with it
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_compounds import profile  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "agi_compounds.json")

# name -> what it is, so the library rows read sensibly.
REFERENCE = {
    "riluzole": "ALS, approved (glutamate release inhibitor)",
    "edaravone": "ALS, approved (free-radical scavenger)",
    "dexpramipexole": "ALS, clinical",
    "masitinib": "ALS, clinical (kinase inhibitor)",
    "levosimendan": "ALS respiratory function, clinical",
    "selegiline": "Parkinson's, approved (MAO-B inhibitor)",
    "rasagiline": "Parkinson's, approved (MAO-B inhibitor)",
    "safinamide": "Parkinson's, approved (MAO-B inhibitor)",
    "levodopa": "Parkinson's, approved (dopamine precursor)",
    "pramipexole": "Parkinson's, approved (dopamine agonist)",
    "ropinirole": "Parkinson's, approved (dopamine agonist)",
    "entacapone": "Parkinson's, approved (COMT inhibitor)",
    "opicapone": "Parkinson's, approved (COMT inhibitor)",
    "istradefylline": "Parkinson's, approved (adenosine A2A antagonist)",
    "ambroxol": "GBA1-Parkinson's, clinical (chaperone)",
    "venglustat": "GBA1-Parkinson's, clinical",
    "navitoclax": "BCL-XL / BCL-2 inhibitor, clinical",
    "venetoclax": "BCL-2 inhibitor, approved",
    "obatoclax": "BCL-2 family inhibitor, clinical",
    "omaveloxolone": "Friedreich's ataxia, approved",
    "trofinetide": "Rett syndrome, approved",
    "risdiplam": "Spinal muscular atrophy, approved",
    "infigratinib": "Achondroplasia / FGFR3, clinical",
    "alendronate": "Osteogenesis imperfecta, approved (bisphosphonate)",
    "zoledronic acid": "Osteogenesis imperfecta, approved (bisphosphonate)",
    "pirfenidone": "Fibrosis and burn scarring, approved",
    "fasudil": "Rho kinase inhibitor, ALS and spinal cord injury clinical",
    "tauroursodeoxycholic acid": "ALS, clinical",
    "memantine": "Neuroprotection, approved",
    "donepezil": "Alzheimer's, approved",
}

PC = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


def fetch(name):
    url = f"{PC}/compound/name/{urllib.parse.quote(name)}/property/Title,SMILES,ConnectivitySMILES,InChIKey/JSON"
    req = urllib.request.Request(url, headers={"User-Agent": "biodao-blockchain/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        p = json.load(r)["PropertyTable"]["Properties"][0]
    return {"cid": p["CID"], "title": p.get("Title", name),
            "smiles": p.get("SMILES") or p.get("ConnectivitySMILES")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true")
    a = ap.parse_args()

    library, rejects = {}, []
    if os.path.exists(OUT) and not a.fresh:
        old = json.load(open(OUT))
        for c in old.get("compounds", []):
            library[c["canonical"]] = c
        rejects = old.get("rejects", [])

    n = 0
    for name, note in REFERENCE.items():
        try:
            hit = fetch(name)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {name}: {e}")
            continue
        prof = profile(hit["smiles"])
        if not prof:
            print(f"  ! {name}: RDKit could not parse the PubChem structure")
            continue
        from rdkit import Chem
        canon = Chem.MolToSmiles(Chem.MolFromSmiles(hit["smiles"]))
        if canon in library:
            continue
        n += 1
        library[canon] = {"agiId": f"REF-{n:03d}", "smiles": hit["smiles"], "canonical": canon,
                          "label": f"{hit['title']} — {note}", "sources": ["PubChem reference set"],
                          "tags": ["reference"], "notes": note, "profile": prof,
                          "known": {"exact": [{"cid": hit["cid"], "title": hit["title"]}], "nearest": []}}
        print(f"  REF-{n:03d} {hit['title']:28} MW {prof['desc']['mw']:6.1f}  CNS {prof['rules']['cnsMpo5']}")
        time.sleep(0.2)  # PubChem asks for no more than 5 requests a second

    compounds = sorted(library.values(), key=lambda c: c.get("agiId") or "zz")
    json.dump({"compounds": compounds, "rejects": rejects}, open(OUT, "w"), indent=1)
    print(f"\nwrote {len(compounds)} compounds -> {OUT}")


if __name__ == "__main__":
    main()
