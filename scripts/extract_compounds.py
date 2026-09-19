#!/usr/bin/env python3
"""Pull the AGI compound collection out of PDFs / spreadsheets into data/agi_compounds.json.

Run it on the compound sheets, the SMILES agent list, patents - anything with SMILES in the text:

    .venv/bin/python scripts/extract_compounds.py ~/Downloads/"AGI Compounds 001-375.pdf" \
                                                  ~/Downloads/"AGI Corp - SMILES AGENT list.pdf"
    .venv/bin/python scripts/extract_compounds.py ~/Downloads/*.pdf --prefix AGI

Each compound is de-duplicated on its canonical SMILES, given an AGI id (from the text when the sheet
states one, otherwise numbered in sequence), and profiled: molecular weight, cLogP, TPSA, H-bond counts,
rotatable bonds, Lipinski violations and a 5-parameter CNS score for brain penetration.

Strings that look like SMILES but do not parse are kept in a "rejects" list rather than dropped, so a
chemist can repair them. The app shows them under "Needs a human eye".

Apple Pages files must be exported to PDF first (File > Export To > PDF).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "server"))

from chem_extract import extract  # noqa: E402
from rdkit import Chem, RDLogger  # noqa: E402
from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors  # noqa: E402

RDLogger.DisableLog("rdApp.*")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "agi_compounds.json")


def read_text(path):
    low = path.lower()
    if low.endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    if low.endswith((".pages", ".numbers", ".key")):
        raise SystemExit(f"{os.path.basename(path)}: export it to PDF from Pages first (File > Export To > PDF).")
    if low.endswith(".sdf"):
        blocks = open(path, errors="replace").read().split("$$$$")
        out = []
        for b in blocks:
            m = Chem.MolFromMolBlock(b)
            if m:
                out.append(f"{b.splitlines()[0].strip()} {Chem.MolToSmiles(m)}")
        return "\n".join(out)
    return open(path, errors="replace").read()


def cns_mpo(mw, clogp, tpsa, hbd):
    def lin(x, good, bad):
        return 1.0 if x <= good else 0.0 if x >= bad else 1 - (x - good) / (bad - good)
    t = 0.0 if tpsa < 20 else (tpsa - 20) / 20 if tpsa < 40 else 1.0 if tpsa <= 90 else 0.0 if tpsa >= 120 else 1 - (tpsa - 90) / 30
    return lin(clogp, 3, 5) + lin(clogp, 2, 4) + lin(mw, 360, 500) + t + lin(hbd, 0.5, 3.5)


def profile(smiles):
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None
    mw, clogp = Descriptors.MolWt(m), Crippen.MolLogP(m)
    tpsa, hbd, hba = rdMolDescriptors.CalcTPSA(m), rdMolDescriptors.CalcNumHBD(m), rdMolDescriptors.CalcNumHBA(m)
    viol = sum([mw > 500, clogp > 5, hbd > 5, hba > 10])
    desc = {"mw": round(mw, 2), "clogp": round(clogp, 2), "tpsa": round(tpsa, 1), "hbd": hbd, "hba": hba,
            "rotb": rdMolDescriptors.CalcNumRotatableBonds(m), "heavy": m.GetNumHeavyAtoms(),
            "rings": rdMolDescriptors.CalcNumRings(m), "aromRings": rdMolDescriptors.CalcNumAromaticRings(m),
            "fsp3": round(rdMolDescriptors.CalcFractionCSP3(m), 3),
            "stereo": rdMolDescriptors.CalcNumAtomStereoCenters(m)}
    rules = {"lipinskiViolations": viol, "veber": desc["rotb"] <= 10 and tpsa <= 140,
             "cnsMpo5": round(cns_mpo(mw, clogp, tpsa, hbd), 2),
             "bbbLikely": tpsa < 90 and mw < 450 and hbd <= 3 and 0.5 < clogp < 5}
    return {"desc": desc, "rules": rules, "inchikey": Chem.MolToInchiKey(m)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--prefix", default="AGI", help="compound id prefix (default AGI)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--fresh", action="store_true", help="ignore any existing library and start over")
    a = ap.parse_args()

    library, rejects = {}, []
    if os.path.exists(a.out) and not a.fresh:
        old = json.load(open(a.out))
        for c in old.get("compounds", []):
            library[c["canonical"]] = c
        rejects = old.get("rejects", [])
        print(f"loaded {len(library)} existing compounds")

    for path in a.files:
        name = os.path.basename(path)
        try:
            text = read_text(path)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {name}: {e}")
            continue
        if not text.strip():
            print(f"  ! {name}: no text layer (scanned images). Structures drawn as pictures need optical "
                  f"structure recognition, e.g. DECIMER, before they can be imported.")
            continue
        rej = []
        found = extract(text, name, rej)
        new = 0
        for c in found:
            key = c["canonical"]
            if key in library:
                srcs = set(library[key].get("sources", []))
                srcs.add(name)
                library[key]["sources"] = sorted(srcs)
                continue
            entry = {"agiId": f"{a.prefix}-{c['id']:03d}" if c["id"] is not None else None,
                     "smiles": c["smiles"], "canonical": key, "label": c["label"], "sources": [name],
                     "tags": [], "notes": "", "profile": profile(key)}
            library[key] = entry
            new += 1
        rejects += rej
        print(f"  {name}: {len(found)} structures ({new} new), {len(rej)} unparsed")

    compounds = list(library.values())
    used = {int(c["agiId"].split("-")[-1]) for c in compounds if c.get("agiId")}
    nxt = max(used) + 1 if used else 1
    for c in compounds:
        if not c.get("agiId"):
            while nxt in used:
                nxt += 1
            c["agiId"] = f"{a.prefix}-{nxt:03d}"
            used.add(nxt)
    compounds.sort(key=lambda c: int(c["agiId"].split("-")[-1]))

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"compounds": compounds, "rejects": rejects}, open(a.out, "w"), indent=1)
    cns = [c for c in compounds if c.get("profile") and c["profile"]["rules"]["bbbLikely"]]
    clean = [c for c in compounds if c.get("profile") and c["profile"]["rules"]["lipinskiViolations"] == 0]
    print(f"\nwrote {len(compounds)} compounds -> {a.out}")
    print(f"  {len(clean)} pass Lipinski cleanly, {len(cns)} look brain-penetrant, {len(rejects)} need review")
    print("Open the app and they are already in the AGI library tab.")


if __name__ == "__main__":
    main()
