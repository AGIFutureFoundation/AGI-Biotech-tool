#!/usr/bin/env python3
"""Build a deduplicated compound inventory from source documents.

Canonicalises every structure through RDKit before deduping, so the same
molecule written two ways collapses to one entry -- which is how the AGI
catalogue turned out to hold 12 unique structures across 425 identifiers.

Shorthand repair runs on anything RDKit rejects, recovering the OCH3/CF3/NO2
style substituents that source documents write by hand.

Writes after every file so a long run over large PDFs keeps partial progress.

    .venv/bin/python scripts/build_compound_inventory.py ~/Downloads/*.pdf
    .venv/bin/python scripts/build_compound_inventory.py --out data/inv.json FILE...
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors

import document_ingest as di
from chem_extract import extract
from smiles_repair import repair

RDLogger.DisableLog("rdApp.*")


def descriptors(mol):
    mw, clogp = Descriptors.MolWt(mol), Descriptors.MolLogP(mol)
    hbd, hba = Descriptors.NumHDonors(mol), Descriptors.NumHAcceptors(mol)
    return {
        "mw": round(mw, 2),
        "clogp": round(clogp, 2),
        "tpsa": round(Descriptors.TPSA(mol), 2),
        "hbd": hbd,
        "hba": hba,
        "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
        "heavy_atoms": mol.GetNumHeavyAtoms(),
        # Lipinski allows one violation.
        "lipinski_violations": sum([mw > 500, clogp > 5, hbd > 5, hba > 10]),
    }


def harvest(path, inventory, stats):
    """Extract, repair and canonicalise every structure in one document."""
    text = di.ingest(path, smiles=False)["text"]
    rejects = []
    source = os.path.basename(path)

    for compound in extract(text, source=source, rejects=rejects):
        raw = compound.get("smiles") if isinstance(compound, dict) else getattr(compound, "smiles", None)
        add(raw, raw, source, compound, inventory, stats, "extracted")

    for reject in rejects:
        # Rejects arrive as {'id', 'raw', 'source'}; the id is the catalogue
        # number, worth keeping on anything repair recovers.
        raw = reject["raw"] if isinstance(reject, dict) else str(reject)
        fixed, notes = repair(raw)
        if fixed:
            carrier = {"id": reject.get("id")} if isinstance(reject, dict) else None
            add(fixed, raw, source, carrier, inventory, stats, "repaired", notes)


def add(smiles, raw, source, compound, inventory, stats, origin, notes=None):
    mol = Chem.MolFromSmiles(smiles) if smiles else None
    if mol is None:
        stats["unparseable"] += 1
        return

    canonical = Chem.MolToSmiles(mol)
    stats[origin] += 1

    if canonical in inventory:
        entry = inventory[canonical]
        entry["occurrences"] += 1
        if source not in entry["sources"]:
            entry["sources"].append(source)
        stats["duplicate"] += 1
        return

    cid = compound.get("id") if isinstance(compound, dict) else None
    inventory[canonical] = {
        "canonical_smiles": canonical,
        "as_written": raw,
        "compound_id": cid,
        "origin": origin,
        "repairs": notes or [],
        "sources": [source],
        "occurrences": 1,
        **descriptors(mol),
    }


def write(out, inventory, stats, done):
    payload = {
        "unique_structures": len(inventory),
        "stats": stats,
        "files_processed": done,
        "compounds": sorted(inventory.values(), key=lambda c: -c["occurrences"]),
    }
    with open(out, "w") as fh:
        json.dump(payload, fh, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="data/extracted_compound_inventory.json")
    args = ap.parse_args()

    inventory, done = {}, []
    stats = dict(extracted=0, repaired=0, duplicate=0, unparseable=0)

    for path in args.files:
        if not os.path.exists(path):
            print(f"  missing  {path}", flush=True)
            continue
        started = time.time()
        try:
            harvest(path, inventory, stats)
        except Exception as exc:
            print(f"  ERROR    {os.path.basename(path)}: {type(exc).__name__}: {exc}", flush=True)
            continue
        done.append(os.path.basename(path))
        write(args.out, inventory, stats, done)
        print(f"  ok       {os.path.basename(path)[:44]:<46} "
              f"unique={len(inventory):<6} {time.time()-started:.0f}s", flush=True)

    print(f"\nunique structures : {len(inventory)}")
    print(f"stats             : {stats}")
    print(f"written           : {args.out}")


if __name__ == "__main__":
    main()
