"""Pull SMILES strings (and the compound IDs next to them) out of free text.

Used by the server's /api/extract endpoint and by scripts/extract_compounds.py.
The same heuristics are mirrored in js/compounds.js for browser-only use.

Handles the quirks seen in exported compound sheets:
  * SMILES wrapped across lines by the PDF layout (re-joined and re-validated),
  * an index number glued to the front of a SMILES ("150CN1CC2=..." -> #150),
  * IDs written as "AGI 001", "AGI-Compound-12", "Compound #7" or a leading "001.".
Every candidate is validated with RDKit; nothing unparseable is kept.
"""
import re

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

TOKEN = re.compile(r"[A-Za-z0-9@+\-\[\]\(\)=#$/\\%.]{5,}")
ID_PATTERNS = [
    re.compile(r"\bAGI[\s\-_#:]*(?:Synthetic\s+)?(?:Compound|Cmpd|Cpd)?[\s\-_#:]*(\d{1,4})\b", re.I),
    re.compile(r"\b(?:Compound|Cmpd|Cpd)[\s\-_#:]*(\d{1,4})\b", re.I),
    re.compile(r"^\s*(\d{1,4})[.):\-\s]"),
]
SMILES_CHARS = set("BCNOPSFIHclnospbr[]()=#@+-\\/%.0123456789aegiKLMRTZuVWXYAdmfkt")


def _mol(s):
    if len(s) < 5 or not any(ch in s for ch in "CcNnOo"):
        return None
    if s.isalpha() and s[0].isupper() and s[1:].islower():  # an ordinary word like "Compound"
        return None
    m = Chem.MolFromSmiles(s)
    if m is None or m.GetNumHeavyAtoms() < 6:
        return None
    # A real structure has carbon and at least one bond-forming feature beyond a plain chain of letters.
    if not any(a.GetSymbol() == "C" for a in m.GetAtoms()):
        return None
    return m


def _looks_like_smiles_line(line):
    return any(_mol(t.group(0)) for t in TOKEN.finditer(line))


def _find_id(lines, i, prefix_digits):
    if prefix_digits:  # "150CN1CC..." - the glued number is the compound index
        return int(prefix_digits)
    for pat in ID_PATTERNS:  # same line first
        mm = pat.search(lines[i])
        if mm:
            return int(mm.group(1))
    for j in range(i - 1, max(-1, i - 3), -1):  # then a header line directly above
        if _looks_like_smiles_line(lines[j]):
            break
        for pat in ID_PATTERNS:
            mm = pat.search(lines[j])
            if mm:
                return int(mm.group(1))
    return None


SMILES_SHAPE = re.compile(r"^(?=.*[CNOS])(?=.*[0-9=(\[])[A-Za-z0-9@+\-\[\]\(\)=#$/\\%.]{8,}$")


def extract(text, source="", rejects=None):
    """Return a list of {id, smiles, canonical, label, source} dicts, de-duplicated.

    If `rejects` is a list, SMILES-shaped strings RDKit could not parse are appended to it
    so a chemist can fix them by hand instead of losing them silently.
    """
    lines = [l.rstrip() for l in text.replace("\r", "\n").split("\n")]
    found, seen = [], set()
    for i, line in enumerate(lines):
        for tm in TOKEN.finditer(line):
            tok = tm.group(0).strip(".,;")
            prefix = ""
            lead = re.match(r"^(\d{1,4})(?=[A-Z\[])", tok)
            if lead:  # "150CN1CC..." -> index 150 + SMILES
                prefix, tok = lead.group(1), tok[len(lead.group(1)):]
            mol = _mol(tok)
            cand = tok
            k = i
            # Re-join a SMILES the PDF layout wrapped over several lines.
            while (mol is None or tm.end() >= len(line.rstrip()) - 1) and k + 1 < len(lines) and k - i < 3:
                nxt = lines[k + 1].strip().split(" ")[0] if lines[k + 1].strip() else ""
                if not nxt or not set(nxt) <= SMILES_CHARS:
                    break
                joined = _mol(cand + nxt)
                if joined is None and mol is not None:
                    break
                if joined is not None:
                    mol, cand = joined, cand + nxt
                else:
                    cand = cand + nxt
                k += 1
            if mol is None:
                if (rejects is not None and SMILES_SHAPE.match(tok) and any(c in tok for c in "=([")
                        and sum(tok.count(c) for c in "CNOSc") >= 4):
                    rejects.append({"id": _find_id(lines, i, prefix), "raw": tok, "source": source})
                continue
            can = Chem.MolToSmiles(mol)
            if can in seen:
                continue
            seen.add(can)
            label = line[: tm.start()].strip(" :-\t")[:80]
            found.append({"id": _find_id(lines, i, prefix), "smiles": cand, "canonical": can,
                          "label": label, "source": source})
    return found
