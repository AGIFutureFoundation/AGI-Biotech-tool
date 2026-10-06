"""Repair condensed organic shorthand written inside SMILES strings.

Compound catalogues exported from documents often carry substituents in the
shorthand a chemist writes by hand -- OCH3, CF3, NO2 -- rather than in SMILES
atom notation. RDKit rejects those, so a catalogue of real chemistry can parse
at a few percent. Expanding the shorthand recovers the intended structure.

Two rules keep this safe to run over scientific data:

  * A string that already parses is never touched. `C(CN)` is valid SMILES
    (carbon-nitrogen) even when the author probably meant a nitrile, so
    rewriting it would silently change the molecule. Those are reported as
    ambiguous instead of repaired.
  * A repair is only accepted when the original failed to parse AND the result
    parses. Every accepted repair records the substitutions applied so the
    change is reviewable rather than invisible.
"""
import re

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

# Unambiguous expansions. Longest keys are applied first so OCHF2 is not
# consumed by a shorter prefix.
EXPANSIONS = {
    "OCH3": "OC",
    "OCF3": "OC(F)(F)F",
    "OCHF2": "OC(F)F",
    "OCH2CH3": "OCC",
    "SCH3": "SC",
    "NHCH3": "NC",
    "N(CH3)2": "N(C)C",
    "CH3": "C",
    "CF3": "C(F)(F)F",
    "CHF2": "C(F)F",
    "CF2CF3": "C(F)(F)C(F)(F)F",
    "NO2": "[N+](=O)[O-]",
    "SO2NH2": "S(=O)(=O)N",
    "SO2CH3": "S(=O)(=O)C",
    "COOH": "C(=O)O",
    "CONH2": "C(=O)N",
    "COCH3": "C(=O)C",
    "OH": "O",
    "NH2": "N",
    "CN": None,  # valid as written but means C-N, not nitrile -- never rewrite
    "tert-butyl": "C(C)(C)C",
    "cyclohexyl": "C1CCCCC1",
    "cyclopentyl": "C1CCCC1",
    "cyclopropyl": "C1CC1",
    "norbornyl": "C1CC2CCC1C2",
    "phenyl": "c1ccccc1",
}

AMBIGUOUS = {k for k, v in EXPANSIONS.items() if v is None}
_ORDERED = sorted((k for k in EXPANSIONS if EXPANSIONS[k]), key=len, reverse=True)
# Shorthand only ever appears as a whole branch: "(OCH3)" or a trailing group.
_BRANCH = re.compile(r"\(([^()]+)\)")


def valid(smiles):
    return smiles is not None and Chem.MolFromSmiles(smiles) is not None


def repair(smiles):
    """Return (repaired_smiles, notes). `repaired_smiles` is None if unfixable.

    notes lists what happened: applied substitutions, or why it was declined.
    """
    if not smiles:
        return None, ["empty"]

    if valid(smiles):
        found = [t for t in AMBIGUOUS if f"({t})" in smiles]
        return None, [f"already valid; ambiguous shorthand present: {t}" for t in found] or ["already valid"]

    applied = []

    def sub_branch(m):
        body = m.group(1)
        for token in _ORDERED:
            if body == token:
                applied.append(f"{token} -> {EXPANSIONS[token]}")
                return f"({EXPANSIONS[token]})"
        return m.group(0)

    out = _BRANCH.sub(sub_branch, smiles)

    # Trailing shorthand with no parentheses, e.g. "...C=C4CF3".
    for token in _ORDERED:
        if out.endswith(token):
            out = out[: -len(token)] + EXPANSIONS[token]
            applied.append(f"trailing {token} -> {EXPANSIONS[token]}")
            break

    if not applied:
        return None, ["no known shorthand found"]
    if not valid(out):
        return None, [f"expanded {len(applied)} token(s) but still unparseable"]

    return Chem.MolToSmiles(Chem.MolFromSmiles(out)), applied


def repair_many(smiles_list):
    """Repair a batch. Returns (results, stats)."""
    results, stats = [], {"already_valid": 0, "repaired": 0, "unfixable": 0, "ambiguous": 0}

    for s in smiles_list:
        fixed, notes = repair(s)
        if fixed:
            stats["repaired"] += 1
            results.append({"original": s, "repaired": fixed, "substitutions": notes})
        elif notes and notes[0].startswith("already valid"):
            stats["already_valid"] += 1
            if len(notes) > 1 or "ambiguous" in notes[0]:
                stats["ambiguous"] += 1
        else:
            stats["unfixable"] += 1

    return results, stats
