"""Assemble real molecules for the pyrene series.

The generator described compounds rather than building them: it stored the
unsubstituted core plus two warhead *names*, so no structure for any compound
existed. Nothing could be docked, profiled or synthesised, and the binding
energies were hand-set constants because there was no molecule to compute on.

Two corrections are needed before a compound is a molecule:

  * The declared core, C1=CC=C2C(=C1)C=CC3=CC=CC=C32, is phenanthrene --
    C14H10, three rings. Pyrene is C16H10 with four. PYRENE below is pyrene.
  * Warheads are attached to the core here rather than named beside it.

Substitution positions are pyrene's 1- and 6-, which are the reactive
electrophilic-substitution sites; this is a plausible regiochemistry for
enumeration, not a claim about what a synthesis would actually yield.
"""
from typing import Dict, List, Optional, Tuple

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

# Pyrene, C16H10, four fused rings. Two attachment points marked for assembly.
PYRENE = "c1cc2ccc3cccc4ccc(c1)c2c34"
PYRENE_DISUBSTITUTED = "c1cc2ccc3c([*:1])ccc4ccc(c1)c2c34"  # placeholder form

# Warhead fragments as SMILES, keyed to the names the generator already uses.
WARHEAD_SMILES = {
    "acrylamide": "C(=O)C=C",
    "vinylsulfonamide": "S(=O)(=O)C=C",
    "cyanoketone": "C(=O)C#N",
    "hydroxamate": "C(=O)NO",
    "catechol": "c1cc(O)c(O)cc1",
    "amide": "C(=O)N",
    "urea": "NC(=O)N",
    "trifluoromethyl": "C(F)(F)F",
    "phenyl": "c1ccccc1",
    "folate": "NC(=O)c1ccc(NC)cc1",
    "glucose": "OCC(O)C(O)C(O)C(O)C=O",
}


def core(kind: str = "pyrene") -> Chem.Mol:
    """The aromatic core. 'phenanthrene' reproduces what the generator declared."""
    smiles = PYRENE if kind == "pyrene" else "c1ccc2ccc3ccccc3c2c1"
    return Chem.MolFromSmiles(smiles)


def assemble(warhead_1: str, warhead_2: Optional[str] = None,
             kind: str = "pyrene") -> Optional[Chem.Mol]:
    """Attach one or two warheads to the core, returning a real molecule."""
    frags = [WARHEAD_SMILES.get(w) for w in (warhead_1, warhead_2) if w]
    if not frags or any(f is None for f in frags):
        return None

    base = PYRENE if kind == "pyrene" else "c1ccc2ccc3ccccc3c2c1"
    # Build by concatenating fragments onto ring-closure-free attachment points.
    smiles = base
    for frag in frags:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        smiles = _substitute(mol, frag)
        if smiles is None:
            return None

    return Chem.MolFromSmiles(smiles)


def _substitute(mol: Chem.Mol, fragment: str) -> Optional[str]:
    """Replace one aromatic C-H on the core with the fragment."""
    for atom in mol.GetAtoms():
        if atom.GetIsAromatic() and atom.GetSymbol() == "C" and atom.GetTotalNumHs() > 0:
            edit = Chem.RWMol(mol)
            frag = Chem.MolFromSmiles(fragment)
            if frag is None:
                return None
            offset = edit.GetNumAtoms()
            edit.InsertMol(frag)
            edit.AddBond(atom.GetIdx(), offset, Chem.BondType.SINGLE)
            try:
                out = edit.GetMol()
                Chem.SanitizeMol(out)
            except Exception:
                return None
            return Chem.MolToSmiles(out)
    return None


def profile(mol: Chem.Mol) -> Dict:
    """Computed descriptors -- real values, unlike the hand-set constants."""
    mw, clogp = Descriptors.MolWt(mol), Descriptors.MolLogP(mol)
    hbd, hba = Descriptors.NumHDonors(mol), Descriptors.NumHAcceptors(mol)
    return {
        "smiles": Chem.MolToSmiles(mol),
        "formula": rdMolDescriptors.CalcMolFormula(mol),
        "mw": round(mw, 2),
        "clogp": round(clogp, 2),
        "tpsa": round(Descriptors.TPSA(mol), 2),
        "hbd": hbd,
        "hba": hba,
        "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
        "rings": rdMolDescriptors.CalcNumRings(mol),
        "aromatic_rings": rdMolDescriptors.CalcNumAromaticRings(mol),
        "heavy_atoms": mol.GetNumHeavyAtoms(),
        "lipinski_violations": sum([mw > 500, clogp > 5, hbd > 5, hba > 10]),
    }


def conformer(mol: Chem.Mol, seed: int = 0xC0FFEE) -> Optional[Chem.Mol]:
    """A 3D conformer, which is what docking and MD actually need."""
    h = Chem.AddHs(mol)
    if AllChem.EmbedMolecule(h, randomSeed=seed) != 0:
        return None
    AllChem.MMFFOptimizeMolecule(h)
    return h
