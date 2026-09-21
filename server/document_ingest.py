"""Read a source document of any supported format into text plus structured records.

One entry point - ingest(path) - returns the same shape for every format, so callers never
branch on file type. Text-bearing formats (PDF, DOCX, XLSX, CSV/TSV, HTML, XML, JSON, text)
hand their text to chem_extract.extract(); chemistry-native formats (SDF, MOL, MOL2, SMI, PDB)
take their structures straight from RDKit instead of round-tripping through the text regex.

Every optional library is imported lazily: a missing one costs that single format, which
reports itself unavailable in the result's warnings, and nothing else.
"""
import csv
import importlib
import json
import os
import re
import zipfile

CHEM_FORMATS = ("sdf", "mol", "mol2", "smi", "pdb")
# format -> import name of the library that unlocks it (absent = standard library only)
_LIBS = {"pdf": "pypdf", "docx": "docx", "xlsx": "openpyxl", "html": "bs4", "xml": "lxml",
         "sdf": "rdkit", "mol": "rdkit", "mol2": "rdkit", "smi": "rdkit", "pdb": "rdkit"}
_PIP = {"pypdf": "pypdf", "docx": "python-docx", "openpyxl": "openpyxl", "bs4": "beautifulsoup4",
        "lxml": "lxml", "rdkit": "rdkit"}
# Crystallisation additives and ions, not drug-like ligands (same list scripts/build_targets.py filters on).
ADDITIVES = set("""HOH GOL EDO SO4 PO4 ACT CL NA MG ZN CA K MN CU CU1 FE FE2 NI CO CD IOD BR PEG PGE
DMS MPD TRS EPE MES BME FMT NO3 IMD ACY PG4 1PE P6G 2PE NH4 SCN CIT TAR MLI BU3 ACE NAG MAN BMA FUC GAL
HEM FAD NAD NAP NDP ADP ATP ANP GDP GTP SAH SAM UNX UNL PE8 CXS LDA BOG HEZ BTB""".split())
_EXT = {"pdf": "pdf", "docx": "docx", "xlsx": "xlsx", "xlsm": "xlsx", "csv": "csv", "tsv": "tsv",
        "tab": "tsv", "htm": "html", "html": "html", "xhtml": "html", "xml": "xml", "json": "json",
        "md": "markdown", "markdown": "markdown", "txt": "text", "text": "text", "sdf": "sdf",
        "sd": "sdf", "mol": "mol", "mol2": "mol2", "smi": "smi", "smiles": "smi", "pdb": "pdb", "ent": "pdb"}
_COORD = ("ATOM  ", "HETATM", "ANISOU", "TER   ", "CONECT", "SEQRES", "MASTER", "END")
_PDB_REC = re.compile(r"^(HEADER|TITLE |COMPND|ATOM  |HETATM|CRYST1|SEQRES|MODEL |EXPDTA|REMARK)")
_COUNTS = re.compile(r"^\s{0,3}\d+\s+\d+.*V[23]000\s*$")


def _imp(name):
    try:
        return importlib.import_module(name)
    except Exception:  # noqa: BLE001
        return None


def available():
    """Return {format: True} / {format: "install <pkg>"} for every supported format."""
    out = {}
    for fmt in _READERS:
        lib = _LIBS.get(fmt)
        out[fmt] = True if not lib or _imp(lib) else f"install {_PIP[lib]}"
    return out


def detect(path):
    """Return (format, warning). Sniffs content first; the extension only breaks ties."""
    ext = _EXT.get(os.path.splitext(path)[1].lower().lstrip("."))
    with open(path, "rb") as f:
        head = f.read(8192)
    sniffed = None
    if head[:5] == b"%PDF-":
        sniffed = "pdf"
    elif head[:4] == b"PK\x03\x04":
        try:
            names = zipfile.ZipFile(path).namelist()
        except Exception:  # noqa: BLE001
            names = []
        sniffed = "docx" if any(n.startswith("word/") for n in names) else \
                  "xlsx" if any(n.startswith("xl/") for n in names) else "zip"
    elif head[:2] == b"\xd0\xcf":
        sniffed = "ole"  # legacy .doc/.xls
    else:
        txt = head.decode("utf-8", "replace")
        s = txt.lstrip()
        low = s[:500].lower()
        lines = txt.splitlines()
        if "@<TRIPOS>" in txt:
            sniffed = "mol2"
        elif any(_PDB_REC.match(l) for l in lines[:60]):
            sniffed = "pdb"
        elif "$$$$" in txt or "M  END" in txt or any(_COUNTS.match(l) for l in lines[2:5]):
            sniffed = "mol" if ext == "mol" else "sdf"
        elif low.startswith("<?xml") or s.startswith("<"):
            sniffed = "html" if ("<html" in low or "<!doctype html" in low) else "xml"
        elif s[:1] in "{[":
            sniffed = "json"
    if sniffed in (None, "zip", "ole"):
        if sniffed == "ole":
            return "unsupported", f"{os.path.basename(path)}: legacy binary Office file, save it as .docx/.xlsx first"
        if sniffed == "zip" and not ext:
            return "unsupported", f"{os.path.basename(path)}: zip archive, not a document"
        return ext or "text", None if ext else f"{os.path.basename(path)}: unknown extension, read as plain text"
    if ext and ext != sniffed and not (ext in ("markdown", "text", "csv", "tsv", "smi") and sniffed in ("text", "json")):
        return sniffed, f"extension says .{os.path.splitext(path)[1].lstrip('.')} but the content is {sniffed}"
    return sniffed, None


def _result(path, fmt):
    return {"path": os.path.abspath(path), "format": fmt, "text": "", "records": [],
            "compounds": [], "rejects": [], "warnings": [], "meta": {}}


def _text(path):
    return open(path, errors="replace").read()


def _cells(header, row):
    return {(h if h else f"col{i + 1}"): v for i, (h, v) in enumerate(zip(header, row))}


def _rows_text(rows):
    return "\n".join("\t".join("" if c is None else str(c) for c in r) for r in rows)


# --------------------------------------------------------------------------- text-bearing formats

def _read_pdf(path, res):
    from pypdf import PdfReader
    pages = [(p.extract_text() or "") for p in PdfReader(path).pages]
    res["text"] = "\n".join(pages)
    res["meta"] = {"pages": len(pages)}
    if not res["text"].strip():
        res["warnings"].append("no text layer: this PDF is scanned images. Structures drawn as pictures "
                               "need optical structure recognition (e.g. DECIMER) first.")


def _read_docx(path, res):
    import docx
    doc = docx.Document(path)
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for ti, table in enumerate(doc.tables):
        rows = [[c.text.strip() for c in r.cells] for r in table.rows]
        if not rows:
            continue
        parts.append(_rows_text(rows))
        header = rows[0]
        for ri, row in enumerate(rows[1:], 1):
            res["records"].append({"kind": "row", "table": ti, "row": ri, "cells": _cells(header, row)})
    res["text"] = "\n".join(parts)
    res["meta"] = {"paragraphs": len(doc.paragraphs), "tables": len(doc.tables)}


def _read_xlsx(path, res):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    parts = []
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        rows = [r for r in rows if any(c is not None and str(c).strip() for c in r)]
        if not rows:
            continue
        parts.append(f"# {ws.title}\n" + _rows_text(rows))
        header = ["" if c is None else str(c).strip() for c in rows[0]]
        for ri, row in enumerate(rows[1:], 2):
            res["records"].append({"kind": "row", "sheet": ws.title, "row": ri, "cells": _cells(header, row)})
    res["text"] = "\n".join(parts)
    res["meta"] = {"sheets": [ws.title for ws in wb.worksheets]}
    wb.close()


def _read_sep(path, res):
    raw = _text(path)
    default = "\t" if res["format"] == "tsv" else ","
    try:
        delim = csv.Sniffer().sniff(raw[:8192], delimiters=",\t;|").delimiter
    except Exception:  # noqa: BLE001
        delim = default
        res["warnings"].append(f"delimiter sniffing failed, assumed {'tab' if delim == chr(9) else repr(delim)}")
    rows = [r for r in csv.reader(raw.splitlines(), delimiter=delim) if any(c.strip() for c in r)]
    if rows:
        header = [c.strip() for c in rows[0]]
        for ri, row in enumerate(rows[1:], 2):
            res["records"].append({"kind": "row", "row": ri, "cells": _cells(header, row)})
    res["text"] = _rows_text(rows)
    res["meta"] = {"delimiter": delim, "rows": len(rows)}


def _read_html(path, res):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(_text(path), "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for ti, table in enumerate(soup.find_all("table")):
        rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])] for tr in table.find_all("tr")]
        rows = [r for r in rows if r]
        if len(rows) < 2:
            continue
        for ri, row in enumerate(rows[1:], 1):
            res["records"].append({"kind": "row", "table": ti, "row": ri, "cells": _cells(rows[0], row)})
    res["text"] = re.sub(r"\n{3,}", "\n\n", soup.get_text("\n", strip=True))
    res["meta"] = {"title": soup.title.get_text(strip=True) if soup.title else None}


def _read_xml(path, res):
    from lxml import etree
    root = etree.parse(path, etree.XMLParser(recover=True, resolve_entities=False, no_network=True)).getroot()
    parts = []
    for el in root.iter():
        txt = (el.text or "").strip()
        if txt:
            tag = etree.QName(el).localname
            parts.append(f"{tag}: {txt}")
            res["records"].append({"kind": "element", "tag": tag, "text": txt, "attrib": dict(el.attrib)})
    res["text"] = "\n".join(parts)
    res["meta"] = {"root": etree.QName(root).localname, "elements": sum(1 for _ in root.iter())}


def _read_json(path, res):
    data = json.load(open(path, errors="replace"))
    res["records"] = [{"kind": "item", "index": i, "value": v} for i, v in enumerate(data)] \
        if isinstance(data, list) else [{"kind": "item", "index": 0, "value": data}]
    res["text"] = json.dumps(data, indent=1, default=str)
    res["meta"] = {"type": type(data).__name__}


def _read_text(path, res):
    res["text"] = _text(path)
    res["meta"] = {"lines": res["text"].count("\n") + 1}


# --------------------------------------------------------------------------- chemistry-native formats

def _compound(mol, idx, label, source, Chem):
    smi, _ = _smiles(mol, Chem)
    return {"id": idx, "smiles": smi, "canonical": smi, "label": label, "source": source}


def _smiles(mol, Chem):
    """(smiles, sanitized). Docking-tool mol2 and PDB ligands often carry no usable bond orders,
    so an unsanitizable structure still yields connectivity rather than nothing."""
    try:
        Chem.SanitizeMol(mol)
        return Chem.MolToSmiles(mol), True
    except Exception:  # noqa: BLE001
        try:
            return Chem.MolToSmiles(mol, canonical=False), False
        except Exception:  # noqa: BLE001
            return None, False


def _add_mols(res, mols, source, Chem):
    """mols is an iterable of (index, label, mol, props); fills compounds/records/text."""
    parts, seen = [], set()
    for idx, label, mol, props in mols:
        c = _compound(mol, idx, label, source, Chem)
        parts.append(f"{label or idx} {c['smiles']}" + "".join(f"\n  {k}: {v}" for k, v in props.items()))
        res["records"].append({"kind": "molecule", "index": idx, "name": label,
                               "smiles": c["smiles"], "props": props})
        if c["canonical"] and c["canonical"] not in seen:
            seen.add(c["canonical"])
            res["compounds"].append(c)
    res["text"] = "\n".join(parts)
    res["meta"]["molecules"] = len(res["records"])


def _read_sdf(path, res):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    src, mols, bad = os.path.basename(path), [], 0
    supplier = Chem.SDMolSupplier(path, sanitize=True, removeHs=False)
    for i, mol in enumerate(supplier, 1):
        if mol is None:
            bad += 1
            continue
        props = mol.GetPropsAsDict(includePrivate=False, includeComputed=False)
        mols.append((i, mol.GetProp("_Name").strip() if mol.HasProp("_Name") else "", mol, props))
    _add_mols(res, mols, src, Chem)
    if bad:
        res["warnings"].append(f"{bad} record(s) RDKit could not parse")


def _read_mol(path, res):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    mol = Chem.MolFromMolFile(path, sanitize=True, removeHs=False)
    if mol is None:
        res["warnings"].append("RDKit could not parse this molfile")
        res["text"] = _text(path)
        return
    name = mol.GetProp("_Name").strip() if mol.HasProp("_Name") else ""
    _add_mols(res, [(1, name, mol, {})], os.path.basename(path), Chem)


def _read_mol2(path, res):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    blocks = [b for b in _text(path).split("@<TRIPOS>MOLECULE") if b.strip()]
    mols, bad, loose = [], 0, 0
    for i, b in enumerate(blocks, 1):
        block = "@<TRIPOS>MOLECULE" + b
        mol = Chem.MolFromMol2Block(block, sanitize=True, removeHs=False)
        props = {}
        if mol is None:
            mol = Chem.MolFromMol2Block(block, sanitize=False, removeHs=False)
            if mol is None:
                bad += 1
                continue
            loose += 1
            props = {"sanitized": False}
        mols.append((i, b.strip().splitlines()[0].strip(), mol, props))
    _add_mols(res, mols, os.path.basename(path), Chem)
    if bad:
        res["warnings"].append(f"{bad} mol2 block(s) RDKit could not parse")
    if loose:
        res["warnings"].append(f"{loose} mol2 block(s) failed sanitization; connectivity only, bond orders unreliable")


def _read_smi(path, res):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    mols, bad = [], []
    for i, line in enumerate(_text(path).splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(None, 1)
        if fields[0].lower() in ("smiles", "structure") and i == 1:
            continue
        mol = Chem.MolFromSmiles(fields[0])
        if mol is None:
            bad.append({"id": i, "raw": fields[0], "source": os.path.basename(path)})
            continue
        mols.append((i, fields[1].strip() if len(fields) > 1 else "", mol, {}))
    _add_mols(res, mols, os.path.basename(path), Chem)
    res["rejects"] = bad
    if bad:
        res["warnings"].append(f"{len(bad)} line(s) did not parse as SMILES")


def _read_pdb(path, res):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    lines = _text(path).splitlines()
    chains, ligands, atoms = {}, {}, 0
    for l in lines:
        if l[:6] not in ("ATOM  ", "HETATM"):
            continue
        atoms += 1
        resn, chain, seq = l[17:20].strip(), l[21:22].strip() or "_", l[22:27].strip()
        c = chains.setdefault(chain, {"id": chain, "atoms": 0, "residues": set()})
        c["atoms"] += 1
        c["residues"].add(seq)
        if l[:6] == "HETATM" and resn not in ADDITIVES:
            ligands.setdefault((resn, chain, seq), []).append(l)
    res["meta"] = {"atoms": atoms, "chains": [{"id": c["id"], "atoms": c["atoms"], "residues": len(c["residues"])}
                                              for c in chains.values()]}
    header = next((l for l in lines if l.startswith("HEADER")), "")
    pdb_id = header[62:66].strip() or None
    title = " ".join(l[10:80].strip() for l in lines if l.startswith("TITLE"))
    res["records"].append({"kind": "protein", "pdbId": pdb_id, "title": title,
                           "chains": res["meta"]["chains"], "atoms": atoms,
                           "ligands": sorted({k[0] for k in ligands})})
    for (resn, chain, seq), block in ligands.items():
        mol = Chem.MolFromPDBBlock("\n".join(block) + "\nEND", sanitize=False, removeHs=False)
        smi, ok = _smiles(mol, Chem) if mol is not None else (None, False)
        res["records"].append({"kind": "ligand", "resName": resn, "chain": chain, "resSeq": seq,
                               "atoms": len(block), "smiles": smi, "sanitized": ok,
                               "note": "bond orders inferred from geometry; match against a "
                                       "reference structure before using as a compound"})
        if smi:
            res["compounds"].append({"id": None, "smiles": smi, "canonical": smi,
                                     "label": f"{resn} {chain}{seq}", "source": os.path.basename(path)})
        else:
            res["warnings"].append(f"ligand {resn} {chain}{seq}: RDKit could not build a structure")
    res["text"] = "\n".join(l for l in lines if not l.startswith(_COORD))


_READERS = {"pdf": _read_pdf, "docx": _read_docx, "xlsx": _read_xlsx, "csv": _read_sep, "tsv": _read_sep,
            "html": _read_html, "xml": _read_xml, "json": _read_json, "markdown": _read_text,
            "text": _read_text, "sdf": _read_sdf, "mol": _read_mol, "mol2": _read_mol2,
            "smi": _read_smi, "pdb": _read_pdb}


def _extract_text_smiles(res):
    import sys
    if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from chem_extract import extract
    except ImportError:
        res["warnings"].append("SMILES extraction unavailable: install rdkit")
        return
    rejects = []
    res["compounds"] = extract(res["text"], os.path.basename(res["path"]), rejects)
    res["rejects"] = rejects


def ingest(path, smiles=True):
    """Read one file. Returns {path, format, text, records, compounds, rejects, warnings, meta}.

    Never raises for a readable path: an unsupported format, a missing library or a parse failure
    comes back as a warning on an otherwise empty result.
    """
    fmt, note = detect(path)
    res = _result(path, fmt)
    if note:
        res["warnings"].append(note)
    reader = _READERS.get(fmt)
    if reader is None:
        res["warnings"].append(f"{fmt}: unsupported format")
        return res
    lib = _LIBS.get(fmt)
    if lib and _imp(lib) is None:
        res["warnings"].append(f".{fmt} unavailable: install {_PIP[lib]}")
        return res
    try:
        reader(path, res)
    except Exception as e:  # noqa: BLE001
        res["warnings"].append(f"{fmt}: {e}")
    if smiles and fmt not in CHEM_FORMATS and res["text"].strip():
        _extract_text_smiles(res)
    return res


def ingest_many(paths, smiles=True):
    """Ingest several files; unreadable paths come back as results carrying a warning."""
    out = []
    for p in paths:
        try:
            out.append(ingest(p, smiles))
        except OSError as e:
            r = _result(p, "unreadable")
            r["warnings"].append(str(e))
            out.append(r)
    return out


def main():
    import argparse
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description="Read documents into text + structures")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--formats", action="store_true", help="list supported formats and exit")
    ap.add_argument("--json", action="store_true", help="dump full results as JSON")
    a = ap.parse_args()
    if a.formats or not a.files:
        for fmt, ok in sorted(available().items()):
            print(f"  {fmt:9} {'ok' if ok is True else ok}")
        return
    results = ingest_many(a.files)
    if a.json:
        print(json.dumps(results, indent=1, default=str))
        return
    for r in results:
        print(f"{os.path.basename(r['path'])}: {r['format']} - {len(r['text'])} chars, "
              f"{len(r['records'])} records, {len(r['compounds'])} structures, {len(r['rejects'])} unparsed")
        for c in r["compounds"][:5]:
            print(f"    {c['label'] or c['id'] or '-'}: {c['canonical']}")
        for w in r["warnings"]:
            print(f"    ! {w}")


if __name__ == "__main__":
    main()
