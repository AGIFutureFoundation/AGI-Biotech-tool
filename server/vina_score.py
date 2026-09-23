"""A Python port of the Vina-like empirical scoring function in ``js/dock.js``.

Why a port rather than a wrapper: AutoDock Vina and Open Babel are not installed
(``which vina obabel`` finds nothing), so there was no Python docking at all.
``js/dock.js`` already implements the AutoDock Vina functional form (Trott &
Olson 2010) over real atomic coordinates and has been reviewed; porting it keeps
one source of truth for the terms and weights and adds no system dependency.

WHAT THIS IS
    A relative ranking score computed from real 3D coordinates: the five Vina
    interaction terms (gauss1, gauss2, repulsion, hydrophobic, hbond) with
    Vina's published weights, divided by the rotatable-bond flexibility factor.

WHAT THIS IS NOT
    A calibrated binding free energy. ``js/dock.js`` says of itself that it is
    "not a validated replacement for Vina/Glide. Treat scores as relative
    rankings." This port inherits that statement exactly and must not claim
    more. The number has NO UNITS -- in particular it is not kcal/mol. Vina's
    published weights were fitted against a real scoring pipeline (its own atom
    typing, desolvation handling, conformer treatment and optimiser); reusing
    the weights without that pipeline reproduces the functional form, not the
    calibration. Call the output what it is: ``vina_like_score``.

Everything here is computed from coordinates, so nothing in this module is a
SyntheticValue. A score that cannot be computed raises rather than falling back.

The port is verified against the JavaScript term by term -- see
``tests/test_vina_score_port.py``, which runs both implementations over the same
receptor PDB and the same ligand molblock and compares every term.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------- element data
# From js/elements.js -- covalent radii, used only for bond perception.
_COV = {
    "H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "P": 1.07, "S": 1.05,
    "CL": 1.02, "BR": 1.20, "I": 1.39, "B": 0.84, "SE": 1.20, "NA": 1.66,
    "MG": 1.41, "K": 2.03, "CA": 1.76, "MN": 1.39, "FE": 1.32, "CO": 1.26,
    "NI": 1.24, "CU": 1.32, "ZN": 1.22, "SI": 1.11,
}
_COV_DEFAULT = 0.8


def cov_radius(symbol: str) -> float:
    return _COV.get((symbol or "C").upper(), _COV_DEFAULT)


AA3 = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
    "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "MSE", "HID",
    "HIE", "HIP", "CYX", "SEC", "PYL",
}
NUC = {"A", "C", "G", "U", "T", "DA", "DC", "DG", "DT", "DU", "I", "DI"}
WATER = {"HOH", "WAT", "DOD", "H2O", "TIP", "TIP3", "SOL"}
IONS = {"NA", "CL", "K", "MG", "CA", "ZN", "MN", "FE", "FE2", "CU", "CU1", "NI",
        "CO", "CD", "IOD", "BR"}

# ------------------------------------------------- scoring constants (dock.js)
# const XS = { C: 1.9, ... }; const xs = (e) => XS[e] || 1.2;
XS = {"C": 1.9, "N": 1.8, "O": 1.7, "S": 2.0, "P": 2.1, "F": 1.5, "CL": 1.8,
      "BR": 2.0, "I": 2.2, "SE": 2.1}
XS_DEFAULT = 1.2


def xs(element: str) -> float:
    """Vina-style interaction radius. Matches `xs` in js/dock.js exactly."""
    return XS.get(element, XS_DEFAULT)


# const W = { g1: -0.0356, g2: -0.00516, rep: 0.84, hyd: -0.0351, hb: -0.587, rot: 0.0585 };
W_GAUSS1 = -0.0356
W_GAUSS2 = -0.00516
W_REPULSION = 0.84
W_HYDROPHOBIC = -0.0351
W_HBOND = -0.587
W_ROT = 0.0585
CUT = 8.0  # const CUT = 8;


class ScoringError(RuntimeError):
    """A real score could not be computed. Never swallow this into a fallback."""


# ---------------------------------------------------------------- atom set
@dataclass
class Residue:
    key: str
    chain: str
    res_seq: int
    res_name: str
    start: int
    end: int
    polymer: bool
    water: bool
    ion: bool
    idx: int


class AtomSet:
    """Port of the parts of ``js/structure.js``'s ``Structure`` that scoring uses.

    Secondary structure, rendering and trajectory handling are deliberately not
    ported: the score never reads them.
    """

    def __init__(self, atoms: List[dict], bonds=None, conect=None,
                 kind: str = "macromolecule", name: str = "structure",
                 hcount: Optional[Sequence[int]] = None):
        self.name = name
        self.kind = kind
        self.n = n = len(atoms)
        if n == 0:
            raise ScoringError(f"{name}: structure has no atoms")
        # float32 positions, matching the JS Float32Array, so the two
        # implementations see bit-identical coordinates.
        self.pos = np.zeros((n, 3), dtype=np.float32)
        self.element: List[str] = [""] * n
        self.atom_name: List[str] = [""] * n
        self.res_name: List[str] = [""] * n
        self.chain: List[str] = [""] * n
        self.res_seq = np.zeros(n, dtype=np.int32)
        self.het = np.zeros(n, dtype=np.uint8)
        for i, a in enumerate(atoms):
            self.pos[i] = (a["x"], a["y"], a["z"])
            self.element[i] = a["element"]
            self.atom_name[i] = a.get("name") or a["element"]
            self.res_name[i] = a.get("res_name") or "LIG"
            self.chain[i] = a.get("chain") or "A"
            self.res_seq[i] = a.get("res_seq") or 1
            self.het[i] = 1 if a.get("het") else 0
        self.hcount = list(hcount) if hcount is not None else None
        self.excluded: Optional[np.ndarray] = None
        self.bonds = list(bonds) if bonds is not None else perceive_bonds(self, conect)
        self._build_residues()
        self._build_neighbors()
        self._type_atoms()

    @property
    def is_small(self) -> bool:
        return self.kind == "small"

    # ---- buildResidues()
    def _build_residues(self):
        self.residues: List[Residue] = []
        cur = None
        for i in range(self.n):
            key = f"{self.chain[i]}:{self.res_seq[i]}:{self.res_name[i]}"
            if cur is None or cur.key != key:
                rn = self.res_name[i]
                cur = Residue(key=key, chain=self.chain[i], res_seq=int(self.res_seq[i]),
                              res_name=rn, start=i, end=i,
                              polymer=(rn in AA3) or (rn in NUC),
                              water=rn in WATER, ion=rn in IONS,
                              idx=len(self.residues))
                self.residues.append(cur)
            cur.end = i
        self.atom_res = np.zeros(self.n, dtype=np.int32)
        for r in self.residues:
            self.atom_res[r.start:r.end + 1] = r.idx
        # Co-crystallised ligands: non-polymer, non-water, non-ion, >= 5 atoms.
        self.ligands = [
            {"res_name": r.res_name, "chain": r.chain, "res_seq": r.res_seq,
             "atoms": list(range(r.start, r.end + 1))}
            for r in self.residues
            if not r.polymer and not r.water and not r.ion and (r.end - r.start) >= 4
        ]

    # ---- buildNeighbors()
    def _build_neighbors(self):
        self.nbr: List[List[int]] = [[] for _ in range(self.n)]
        self._bond_order: Dict[Tuple[int, int], int] = {}
        for (i, j, o) in self.bonds:
            self.nbr[i].append(j)
            self.nbr[j].append(i)
            self._bond_order[(i, j) if i < j else (j, i)] = o

    def bond_order(self, i, j) -> int:
        if i is None or j is None:
            return 1  # JS: map.get(NaN) -> undefined -> || 1
        return self._bond_order.get((i, j) if i < j else (j, i), 1)

    # ---- typeAtoms()
    def _type_atoms(self):
        n = self.n
        self.hydrophobic = np.zeros(n, dtype=np.uint8)
        self.donor = np.zeros(n, dtype=np.uint8)
        self.acceptor = np.zeros(n, dtype=np.uint8)
        any_h = ("H" in self.element) or (self.hcount is not None)
        heavy = []
        for i in range(n):
            e = self.element[i]
            if e == "H":
                continue
            heavy.append(i)
            nb = self.nbr[i]
            if e == "C":
                self.hydrophobic[i] = 1 if all(
                    self.element[j] != "N" and self.element[j] != "O" for j in nb) else 0
            elif e in ("F", "CL", "BR", "I"):
                self.hydrophobic[i] = 1
            elif e in ("N", "O"):
                has_h = any(self.element[j] == "H" for j in nb) or bool(
                    self.hcount is not None and self.hcount[i] > 0)
                heavy_deg = sum(1 for j in nb if self.element[j] != "H")
                if e == "O":
                    self.acceptor[i] = 1
                    first = nb[0] if nb else None
                    self.donor[i] = 1 if (
                        has_h or (not any_h and heavy_deg == 1
                                  and self.bond_order(i, first) == 1
                                  and not self._is_carboxyl_o(i))) else 0
                else:
                    aromatic_like = any(self.bond_order(i, j) >= 2 for j in nb)
                    self.donor[i] = 1 if (
                        has_h or (not any_h and heavy_deg <= 2
                                  and not (aromatic_like and heavy_deg == 2))) else 0
                    self.acceptor[i] = 1 if (
                        (heavy_deg < 3 and not has_h) or (not any_h and aromatic_like)) else 0
        if not self.is_small:
            self._type_protein()
        self.heavy = np.asarray(heavy, dtype=np.int32)

    def _is_carboxyl_o(self, i) -> bool:
        nb = self.nbr[i]
        if not nb:
            return False
        c = nb[0]
        return self.element[c] == "C" and any(
            j != i and self.element[j] == "O" and self.bond_order(c, j) == 2
            for j in self.nbr[c])

    def _type_protein(self):
        D = {"N", "OG", "OG1", "OH", "ND2", "NE2", "ND1", "NZ", "NE", "NH1", "NH2", "NE1"}
        A = {"O", "OXT", "OG", "OG1", "OH", "OD1", "OD2", "OE1", "OE2", "ND1", "NE2"}
        for i in range(self.n):
            if self.het[i]:
                continue
            an, rn = self.atom_name[i], self.res_name[i]
            if self.element[i] in ("N", "O"):
                self.donor[i] = 1 if an in D else 0
                self.acceptor[i] = 1 if an in A else 0
                if rn == "GLN" and an == "NE2":
                    self.acceptor[i] = 0
                if an == "N" and rn == "PRO":
                    self.donor[i] = 0

    def exclude_atoms(self, indices):
        if self.excluded is None:
            self.excluded = np.zeros(self.n, dtype=np.uint8)
        for i in indices:
            self.excluded[i] = 1

    def center(self, atoms=None) -> np.ndarray:
        idx = list(range(self.n)) if atoms is None else list(atoms)
        return self.pos[idx].mean(axis=0).astype(np.float64)


# ---------------------------------------------------------------- bond perception
def perceive_bonds(st: "AtomSet", conect=None) -> List[Tuple[int, int, int]]:
    """Distance-based bonding. Port of ``perceiveBonds`` in js/structure.js."""
    n, P, cell = st.n, st.pos, 3.0
    grid: Dict[Tuple[int, int, int], List[int]] = {}
    for i in range(n):
        k = (math.floor(P[i][0] / cell), math.floor(P[i][1] / cell), math.floor(P[i][2] / cell))
        grid.setdefault(k, []).append(i)
    bonds: List[Tuple[int, int, int]] = []
    seen = set()
    if conect:
        for a, b in conect:
            k = (a, b) if a < b else (b, a)
            if k in seen:
                continue
            seen.add(k)
            bonds.append((a, b, 1))
    for i in range(n):
        cx = math.floor(P[i][0] / cell)
        cy = math.floor(P[i][1] / cell)
        cz = math.floor(P[i][2] / cell)
        ri = cov_radius(st.element[i])
        hi = st.element[i] == "H"
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for j in grid.get((cx + dx, cy + dy, cz + dz), ()):
                        if j <= i:
                            continue
                        if hi and st.element[j] == "H":
                            continue
                        if st.het[i] != st.het[j] and st.res_name[i] != st.res_name[j]:
                            continue  # no protein-ligand bonds
                        d = P[i].astype(np.float64) - P[j].astype(np.float64)
                        d2 = float(d @ d)
                        mx = ri + cov_radius(st.element[j]) + 0.4
                        if 0.16 < d2 < mx * mx:
                            k = (i, j)
                            if k in seen:
                                continue
                            seen.add(k)
                            bonds.append((i, j, 1))
    return bonds


# ---------------------------------------------------------------- parsers
def _norm_el(e: str, name: str) -> str:
    s = (e or "").strip()
    if not s:
        s = "".join(ch for ch in (name or "") if ch.isalpha())
        two = s[:2].upper()
        s = two if two in {"CL", "BR", "FE", "ZN", "MG", "NA", "MN", "CU", "CA", "SE"} \
            and len(name.strip()) <= 2 else s[:1]
    return s.upper()


def parse_pdb(text: str, name: str = "receptor") -> AtomSet:
    """Port of ``parsePDB``. First model only; altloc blank or A only."""
    atoms, serial_map, conect_raw = [], {}, []
    model = 0
    for line in text.split("\n"):
        line = line.rstrip("\r")
        rec = line[:6]
        if rec == "MODEL ":
            model += 1
            if model > 1:
                break
            continue
        if rec == "ENDMDL" and atoms:
            break
        if rec in ("ATOM  ", "HETATM"):
            alt = line[16] if len(line) > 16 else " "
            if alt not in (" ", "A"):
                continue
            try:
                atoms_i = {
                    "name": line[12:16].strip(),
                    "res_name": line[17:20].strip(),
                    "chain": (line[21] if len(line) > 21 else "A").strip() or "A",
                    "res_seq": int(float(line[22:26])),
                    "x": float(line[30:38]), "y": float(line[38:46]), "z": float(line[46:54]),
                    "element": _norm_el(line[76:78], line[12:14]),
                    "het": rec == "HETATM",
                }
            except ValueError:
                continue
            serial_map[int(line[6:11])] = len(atoms)
            atoms.append(atoms_i)
        elif rec == "CONECT":
            try:
                a = int(line[6:11])
            except ValueError:
                continue
            for c in range(11, 31, 5):
                chunk = line[c:c + 5].strip()
                if chunk.isdigit() and int(chunk):
                    conect_raw.append((a, int(chunk)))
    if not atoms:
        raise ScoringError(f"{name}: no ATOM/HETATM records parsed")
    conect = [(serial_map[a], serial_map[b]) for a, b in conect_raw
              if a in serial_map and b in serial_map
              and atoms[serial_map[a]]["het"] and atoms[serial_map[b]]["het"]]
    for a in atoms:  # MSE-style HETATM for standard residues behaves as polymer
        if a["het"] and a["res_name"] in AA3:
            a["het"] = False
    return AtomSet(atoms, conect=conect or None, kind="macromolecule", name=name)


def parse_molblock(text: str, name: str = "ligand") -> AtomSet:
    """Port of ``parseMolblock`` (V2000 branch). Aromatic bond order 4 -> 2."""
    lines = text.split("\n")
    lines = [l.rstrip("\r") for l in lines]
    if len(lines) < 4:
        raise ScoringError(f"{name}: molblock too short")
    counts = lines[3]
    if "V3000" in counts:
        raise ScoringError(f"{name}: V3000 molblocks are not supported by this port")
    na, nb = int(counts[0:3]), int(counts[3:6])
    atoms, bonds, counters = [], [], {}
    for i in range(na):
        l = lines[4 + i]
        e = l[31:34].strip().upper()
        counters[e] = counters.get(e, 0) + 1
        atoms.append({"x": float(l[0:10]), "y": float(l[10:20]), "z": float(l[20:30]),
                      "element": e, "name": f"{e}{counters[e]}",
                      "res_name": "LIG", "chain": "L", "res_seq": 1, "het": True})
    for i in range(nb):
        l = lines[4 + na + i]
        order = int(l[6:9])
        bonds.append((int(l[0:3]) - 1, int(l[3:6]) - 1, 2 if order == 4 else min(order, 3)))
    return AtomSet(atoms, bonds=bonds, kind="small", name=name)


# ---------------------------------------------------------------- receptor grid
class ProteinGrid:
    """Receptor atom set for scoring: heavy, non-water, non-excluded atoms.

    ``js/dock.js`` uses a uniform hash grid to find atoms within CUT of a query
    point. Here the same atoms are held as numpy arrays and the CUT mask is
    applied directly; the selected pair set is identical (strict ``d2 < CUT^2``),
    which is what matters for equivalence.
    """

    def __init__(self, st: AtomSet, indices: Optional[np.ndarray] = None):
        self.st = st
        if indices is None:
            indices = np.asarray([
                i for i in st.heavy
                if not st.residues[int(st.atom_res[i])].water
                and not (st.excluded is not None and st.excluded[i])
            ], dtype=np.int32)
        self.atoms = indices
        if len(self.atoms) == 0:
            raise ScoringError(f"{st.name}: receptor has no scorable heavy atoms")
        self.pos = st.pos[self.atoms].astype(np.float64)
        self.radius = np.asarray([xs(st.element[i]) for i in self.atoms], dtype=np.float64)
        self.hydrophobic = st.hydrophobic[self.atoms].astype(bool)
        self.donor = st.donor[self.atoms].astype(bool)
        self.acceptor = st.acceptor[self.atoms].astype(bool)

    def within(self, center, radius: float) -> "ProteinGrid":
        """A sub-grid holding every atom within `radius` of `center`.

        Used only as a speed-up: callers must pass a radius large enough that
        no atom within CUT of any scored ligand atom is dropped.
        """
        c = np.asarray(center, dtype=np.float64)
        keep = np.linalg.norm(self.pos - c, axis=1) <= radius
        return ProteinGrid(self.st, self.atoms[keep])


class Ligand:
    """Scoring-side view of a ligand AtomSet (typed arrays for the heavy atoms)."""

    def __init__(self, st: AtomSet):
        self.st = st
        self.heavy = st.heavy
        if len(self.heavy) == 0:
            raise ScoringError(f"{st.name}: ligand has no heavy atoms")
        self.radius = np.asarray([xs(st.element[i]) for i in self.heavy], dtype=np.float64)
        self.hydrophobic = st.hydrophobic[self.heavy].astype(bool)
        self.donor = st.donor[self.heavy].astype(bool)
        self.acceptor = st.acceptor[self.heavy].astype(bool)
        self.n = st.n
        self.pos = st.pos.astype(np.float32)
        self._nrot: Optional[int] = None

    @property
    def nrot(self) -> int:
        if self._nrot is None:
            self._nrot = len(rotatable_bonds(self.st))
        return self._nrot


# ---------------------------------------------------------------- the score
def vina_score(grid: ProteinGrid, lig: Ligand, coords=None, details: bool = False,
               nrot: Optional[int] = None):
    """Port of ``vinaScore`` in js/dock.js. Returns a unitless ranking score.

    `coords` is an (n, 3) array in the ligand's atom order; defaults to the
    ligand's own conformer. Lower is better, as in Vina.
    """
    L = lig.pos if coords is None else np.asarray(coords, dtype=np.float32)
    if L.shape != (lig.n, 3):
        raise ScoringError(f"coordinate array {L.shape} does not match ligand of {lig.n} atoms")
    LH = L[lig.heavy].astype(np.float64)

    # Pairwise ligand-heavy x receptor distances, masked at CUT (strict <).
    diff = LH[:, None, :] - grid.pos[None, :, :]
    d2 = np.einsum("ijk,ijk->ij", diff, diff)
    mask = d2 < CUT * CUT
    if not mask.any():
        # No receptor atom within 8 A: every term is zero. That is a real
        # result (a ligand parked outside the protein), not an error.
        r = np.zeros(0)
        d = np.zeros(0)
        pair_l = np.zeros(0, dtype=int)
        pair_p = np.zeros(0, dtype=int)
    else:
        pair_l, pair_p = np.nonzero(mask)
        r = np.sqrt(d2[pair_l, pair_p])
        d = r - lig.radius[pair_l] - grid.radius[pair_p]

    g1 = float(np.exp(-((d / 0.5) ** 2)).sum())
    g2 = float(np.exp(-(((d - 3.0) / 2.0) ** 2)).sum())
    neg = d < 0
    rep = float((d[neg] ** 2).sum())

    hyd_pairs = lig.hydrophobic[pair_l] & grid.hydrophobic[pair_p]
    dh = d[hyd_pairs]
    hyd = float(np.where(dh < 0.5, 1.0, np.where(dh < 1.5, 1.5 - dh, 0.0)).sum())

    hb_pairs = ((lig.donor[pair_l] & grid.acceptor[pair_p])
                | (lig.acceptor[pair_l] & grid.donor[pair_p]))
    db = d[hb_pairs]
    hvals = np.where(db < -0.7, 1.0, np.where(db < 0.0, -db / 0.7, 0.0))
    hb = float(hvals.sum())

    nr = lig.nrot if nrot is None else nrot
    inter = (W_GAUSS1 * g1 + W_GAUSS2 * g2 + W_REPULSION * rep
             + W_HYDROPHOBIC * hyd + W_HBOND * hb)
    total = inter / (1 + W_ROT * nr)
    if not details:
        return total

    hb_idx = np.nonzero(hb_pairs)[0]
    hbonds = [{"lig": int(lig.heavy[pair_l[k]]),
               "prot": int(grid.atoms[pair_p[k]]),
               "r": float(r[k])}
              for k, h in zip(hb_idx, hvals) if h > 0.3]
    contact_residues = sorted({int(grid.st.atom_res[grid.atoms[pair_p[k]]])
                               for k in np.nonzero(r < 4.0)[0]})
    return {
        "total": total,
        "inter": inter,
        "terms": {
            "gauss1": W_GAUSS1 * g1,
            "gauss2": W_GAUSS2 * g2,
            "repulsion": W_REPULSION * rep,
            "hydrophobic": W_HYDROPHOBIC * hyd,
            "hbond": W_HBOND * hb,
        },
        "raw": {"gauss1": g1, "gauss2": g2, "repulsion": rep,
                "hydrophobic": hyd, "hbond": hb},
        "hbonds": hbonds,
        "contactResidues": contact_residues,
        "nrot": nr,
        "ligandEfficiency": total / len(lig.heavy),
    }


# ---------------------------------------------------------------- torsions
def _ring_bonds(st: AtomSet):
    """Port of ``ringBonds``: a bond is in a ring if its atoms stay connected
    without it."""
    out = set()
    for (i, j, _o) in st.bonds:
        seen, q, found = {i}, [i], False
        while q and not found:
            u = q.pop(0)
            for v in st.nbr[u]:
                if u == i and v == j:
                    continue
                if v == j:
                    found = True
                    break
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        if found:
            out.add((i, j) if i < j else (j, i))
    return out


def rotatable_bonds(st: AtomSet) -> List[dict]:
    """Port of ``rotatableBonds``: single, acyclic, non-terminal, non-amide."""
    rot = []
    in_ring = _ring_bonds(st)
    n = st.n
    for (i, j, o) in st.bonds:
        if o != 1 or ((i, j) if i < j else (j, i)) in in_ring:
            continue
        hi = sum(1 for x in st.nbr[i] if st.element[x] != "H")
        hj = sum(1 for x in st.nbr[j] if st.element[x] != "H")
        if hi < 2 or hj < 2:
            continue

        def amide(a, b):
            return (st.element[a] == "C" and st.element[b] == "N"
                    and any(st.element[x] == "O" and st.bond_order(a, x) == 2
                            for x in st.nbr[a]))

        if amide(i, j) or amide(j, i):
            continue
        side = {j}
        stack = [j]
        while stack:
            u = stack.pop()
            for v in st.nbr[u]:
                if v != i and v not in side:
                    side.add(v)
                    stack.append(v)
        if i in side:
            continue
        if len(side) <= n / 2:
            moving, a, b = sorted(side), i, j
        else:
            moving, a, b = [x for x in range(n) if x not in side], j, i
        rot.append({"a": a, "b": b, "moving": np.asarray(moving, dtype=np.int32)})
    return rot


# ---------------------------------------------------------------- MC docking
def _rotate_about(L, atoms, anchor, axis, ang):
    c, s = math.cos(ang), math.sin(ang)
    t = 1 - c
    ux, uy, uz = axis
    R = np.array([
        [t * ux * ux + c, t * ux * uy - s * uz, t * ux * uz + s * uy],
        [t * ux * uy + s * uz, t * uy * uy + c, t * uy * uz - s * ux],
        [t * ux * uz - s * uy, t * uy * uz + s * ux, t * uz * uz + c],
    ], dtype=np.float64)
    v = L[atoms].astype(np.float64) - np.asarray(anchor, dtype=np.float64)
    L[atoms] = (v @ R.T + np.asarray(anchor, dtype=np.float64)).astype(L.dtype)


def _random_unit(rng):
    z = rng.random() * 2 - 1
    t = rng.random() * math.pi * 2
    r = math.sqrt(1 - z * z)
    return np.array([r * math.cos(t), r * math.sin(t), z])


def _box_penalty(L, center, box):
    o = np.abs(L.astype(np.float64) - np.asarray(center, dtype=np.float64)) - box
    return float((np.where(o > 0, o, 0.0) ** 2).sum())


def _rmsd(A, B):
    return float(np.sqrt(((A.astype(np.float64) - B.astype(np.float64)) ** 2).sum() / len(A)))


@dataclass
class Pose:
    coords: np.ndarray
    score: float
    details: dict = field(default_factory=dict)


def dock_ligand(grid: ProteinGrid, lig: Ligand, center, runs: int = 4, steps: int = 600,
                box: float = 8.0, seed: int = 0xC0FFEE) -> List[Pose]:
    """Port of ``dockLigand``: simulated-annealing Monte Carlo over rigid-body
    moves plus torsion moves, keeping distinct poses.

    Seeded: the JS uses ``Math.random()`` (the MC sampler, which is how docking
    works); here the stream is a seeded numpy Generator so a given compound and
    receptor reproduce the same poses. Same algorithm, reproducible draws.
    """
    rng = np.random.default_rng(seed)
    rot = rotatable_bonds(lig.st)
    nrot = len(rot)
    n = lig.n
    all_atoms = np.arange(n)
    base = lig.pos.astype(np.float32).copy()
    base -= base.mean(axis=0, dtype=np.float64).astype(np.float32)
    center = np.asarray(center, dtype=np.float64)

    # Trim the receptor once to what can possibly be within CUT of any pose.
    reach = box * math.sqrt(3) + float(np.abs(base).sum(axis=1).max()) + CUT + 1.0
    local = grid.within(center, reach)

    def energy(L):
        return (vina_score(local, lig, L, nrot=nrot) + _box_penalty(L, center, box))

    poses: List[Pose] = []
    for _run in range(runs):
        L = base.copy()
        u = _random_unit(rng)
        _rotate_about(L, all_atoms, (0, 0, 0), u, rng.random() * math.pi * 2)
        for b in rot:
            ax = _axis(L, b)
            _rotate_about(L, b["moving"], L[b["a"]], ax, rng.random() * math.pi * 2)
        off = _random_unit(rng) * (rng.random() * box * 0.4)
        L += (center + off).astype(np.float32)
        e = energy(L)
        best, best_e = L.copy(), e
        for s in range(steps):
            temp = 1.2 * (1 - s / steps) + 0.05
            trial = L.copy()
            mv = rng.random()
            if mv < 0.4:
                trial += (_random_unit(rng) * (rng.random() * 1.0)).astype(np.float32)
            elif mv < 0.75 or not rot:
                c = trial.mean(axis=0, dtype=np.float64)
                _rotate_about(trial, all_atoms, c, _random_unit(rng), (rng.random() - 0.5) * 0.6)
            else:
                b = rot[int(rng.integers(len(rot)))]
                _rotate_about(trial, b["moving"], trial[b["a"]], _axis(trial, b),
                              (rng.random() - 0.5) * 2.0)
            et = energy(trial)
            if et < e or rng.random() < math.exp(min(0.0, -(et - e) / temp)):
                L = trial
                e = et
                if e < best_e:
                    best_e, best = e, L.copy()
        poses.append(Pose(coords=best, score=vina_score(local, lig, best, nrot=nrot)))
        poses.sort(key=lambda p: p.score)

    uniq: List[Pose] = []
    for p in poses:
        if not any(_rmsd(p.coords, q.coords) < 1.5 for q in uniq):
            uniq.append(p)
    good = [p for p in uniq if p.score < 0]
    return good if good else uniq[:1]


def _axis(L, b):
    v = L[b["b"]].astype(np.float64) - L[b["a"]].astype(np.float64)
    l = float(np.linalg.norm(v)) or 1.0
    return v / l
