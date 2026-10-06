"""Score assembled pyrene compounds against a real receptor structure.

This replaces, for the targets it covers, the hand-set warhead constants in
``pyrene_apoptotic_discovery._calculate_binding_energy``. The chain is:

    warhead names -> pyrene_structures.assemble()  (a real molecule)
                  -> pyrene_structures.conformer() (MMFF-optimised 3D)
                  -> molblock -> vina_score.AtomSet
                  -> vina_score.dock_ligand() in a real pocket of a real PDB entry
                  -> vina_score.vina_score() of the best pose

WHAT THE NUMBER IS
    ``vina_like_score``: a unitless relative ranking score, lower is better,
    computed from the actual atomic coordinates of the assembled compound and
    of the receptor, using the AutoDock Vina functional form and weights ported
    from js/dock.js (see server/vina_score.py).

WHAT THE NUMBER IS NOT
    It is NOT a binding free energy and NOT kcal/mol. js/dock.js says of itself
    that it is "not a validated replacement for Vina/Glide. Treat scores as
    relative rankings"; this Python path claims exactly as much and no more. It
    is comparable between compounds docked into the same receptor with the same
    settings, and not comparable to a measured Kd, IC50 or dG, nor across
    receptors, nor to scores from real Vina.

FAILURE IS VISIBLE
    No target receptor, no network and no cached PDB, an unassemblable warhead
    pair, a failed conformer embed, or a pocket with no bound ligand to define
    a site all raise ``ScoringError``. Nothing here ever falls back to the old
    constants -- that fallback is exactly the thing being removed, and a silent
    return to it would be indistinguishable from a real score.
"""

from __future__ import annotations

import os
import pathlib
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from vina_score import (AtomSet, Ligand, ProteinGrid, ScoringError, dock_ligand,
                        parse_molblock, parse_pdb, vina_score)

# Advertised loudly so no consumer can print this number next to "kcal/mol".
SCORE_UNITS = None
SCORE_NAME = "vina_like_score"
SCORE_CAVEAT = (
    "Unitless relative ranking score (lower is better) from the AutoDock Vina "
    "functional form ported from js/dock.js. Not kcal/mol, not a binding free "
    "energy, not comparable across receptors or to measured affinities."
)

RCSB_DOWNLOAD = "https://files.rcsb.org/download/{pdb_id}.pdb"
USER_AGENT = "agi-bioxr/1.0 (mailto:{})".format(
    os.environ.get("NCBI_EMAIL", "x@agifuturefoundation.org"))


@dataclass(frozen=True)
class ReceptorSite:
    """A PDB entry plus the co-crystallised ligand that defines the pocket."""
    pdb_id: str
    site_ligand: str   # HET residue name whose centroid is the docking box centre
    chain: str
    note: str


# Curated because guessing a receptor is how a docking pipeline quietly scores
# the wrong protein. Each entry below was resolved live against RCSB while this
# module was written: the title was read and the HET record for `site_ligand`
# confirmed present. A target that is not in this table raises rather than
# defaulting to something plausible.
TARGET_RECEPTORS: Dict[str, ReceptorSite] = {
    "BCL2": ReceptorSite(
        pdb_id="6O0K", site_ligand="LBM", chain="A",
        note="CRYSTAL STRUCTURE OF BCL-2 WITH VENETOCLAX; the BH3 groove is "
             "defined by the bound venetoclax (LBM)."),
    "BCL-xL": ReceptorSite(
        pdb_id="4LVT", site_ligand="1XJ", chain="A",
        note="BCL_2-NAVITOCLAX (ABT-263) COMPLEX; BH3 groove defined by 1XJ."),
    "XIAP": ReceptorSite(
        pdb_id="5C7A", site_ligand="4YE", chain="A",
        note="Fragment-based drug discovery targeting inhibitor of apoptosis "
             "protein; BIR-domain site defined by the bound fragment 4YE."),
    "caspase-3": ReceptorSite(
        pdb_id="1NME", site_ligand="158", chain="A",
        note="Structure of Casp-3 with tethered salicylate; active site defined "
             "by the bound inhibitor 158."),
}

# Deliberately absent: FAS. The repo's FAS entries are death-domain complexes
# with no small-molecule site, so there is no pocket to dock into. Asking for a
# FAS score raises; it does not quietly return a constant.


def cache_dir() -> pathlib.Path:
    """Where downloaded PDB entries are kept between runs."""
    env = os.environ.get("AGI_BIOXR_PDB_CACHE")
    if env:
        return pathlib.Path(env)
    home = pathlib.Path.home()
    base = home / ".cache" if home.is_dir() else pathlib.Path(tempfile.gettempdir())
    return base / "agi-bioxr" / "pdb"


def fetch_pdb(pdb_id: str, allow_network: bool = True) -> str:
    """PDB entry text, from the on-disk cache or RCSB. Raises if neither works."""
    pdb_id = pdb_id.upper()
    path = cache_dir() / f"{pdb_id}.pdb"
    if path.is_file() and path.stat().st_size > 0:
        return path.read_text()
    if not allow_network:
        raise ScoringError(
            f"{pdb_id} is not in the PDB cache ({path}) and network access was "
            "not permitted, so no receptor is available.")
    url = RCSB_DOWNLOAD.format(pdb_id=pdb_id)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        raise ScoringError(f"could not fetch {pdb_id} from RCSB ({url}): {exc}") from exc
    if "ATOM  " not in text:
        raise ScoringError(f"{url} returned no ATOM records")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    except OSError:
        pass  # an unwritable cache slows things down; it does not change the score
    return text


class Receptor:
    """A parsed receptor plus the pocket centre the ligand is docked into."""

    def __init__(self, target: str, site: ReceptorSite, structure: AtomSet,
                 center: np.ndarray, site_atoms: List[int]):
        self.target = target
        self.site = site
        self.structure = structure
        self.center = center
        self.site_atoms = site_atoms
        # The co-crystallised ligand defines the site; it must not also act as
        # receptor, or every compound would be scored against it.
        structure.exclude_atoms(site_atoms)
        self.grid = ProteinGrid(structure)

    @property
    def provenance(self) -> Dict:
        return {
            "target": self.target,
            "pdb_id": self.site.pdb_id,
            "pdb_url": f"https://www.rcsb.org/structure/{self.site.pdb_id}",
            "site_defined_by": f"co-crystallised ligand {self.site.site_ligand} "
                               f"(chain {self.site.chain}), excluded from the receptor",
            "site_center": [round(float(v), 3) for v in self.center],
            "receptor_atoms_scored": int(len(self.grid.atoms)),
            "entry_note": self.site.note,
        }


def receptor_for(target: str, allow_network: bool = True) -> Receptor:
    """Load the curated receptor for `target`. Raises for anything unhandled."""
    site = TARGET_RECEPTORS.get(target)
    if site is None:
        raise ScoringError(
            f"no receptor structure is curated for target {target!r}; known targets: "
            f"{sorted(TARGET_RECEPTORS)}. Refusing to score against a guessed "
            "structure -- add an entry to TARGET_RECEPTORS with a verified PDB id.")
    st = parse_pdb(fetch_pdb(site.pdb_id, allow_network=allow_network),
                   name=f"{target}/{site.pdb_id}")
    atoms = [i for i in range(st.n)
             if st.res_name[i] == site.site_ligand and st.chain[i] == site.chain]
    if not atoms:
        raise ScoringError(
            f"{site.pdb_id} chain {site.chain} has no {site.site_ligand} residue, so "
            "the docking site cannot be located; the entry may have been revised.")
    center = st.pos[atoms].astype(np.float64).mean(axis=0)
    return Receptor(target, site, st, center, atoms)


def ligand_from_mol(mol, name: str = "ligand") -> Ligand:
    """RDKit mol with a 3D conformer -> a scoring-side ligand.

    Goes through a molblock on purpose: that is the exact path the JS reference
    implementation takes, so the port-equivalence test covers this conversion
    too rather than leaving it unverified.
    """
    from rdkit import Chem  # imported here so vina_score stays rdkit-free

    if mol is None:
        raise ScoringError(f"{name}: no molecule to score")
    if mol.GetNumConformers() == 0:
        raise ScoringError(f"{name}: molecule has no 3D conformer; embed one first")
    block = Chem.MolToMolBlock(mol)
    if "V3000" in block.split("\n")[3]:
        raise ScoringError(f"{name}: molecule is too large for a V2000 molblock")
    return Ligand(parse_molblock(block, name=name))


@dataclass
class DockingResult:
    """One scored compound. Every field is computed; none is synthetic."""
    # The structure the score was computed on. A score whose molecule cannot be
    # identified is the untraceable number this module exists to replace, and
    # callers need it to record what was actually docked.
    smiles: str
    vina_like_score: float
    terms: Dict[str, float]
    raw_terms: Dict[str, float]
    ligand_efficiency: float
    rotatable_bonds: int
    heavy_atoms: int
    hbonds: int
    contact_residues: List[int]
    poses_kept: int
    receptor: Dict
    settings: Dict

    def as_record(self) -> Dict:
        return {
            "score_name": SCORE_NAME,
            "smiles": self.smiles,
            "score": round(self.vina_like_score, 4),
            "units": SCORE_UNITS,
            "caveat": SCORE_CAVEAT,
            "terms": {k: round(v, 4) for k, v in self.terms.items()},
            "raw_terms": {k: round(v, 4) for k, v in self.raw_terms.items()},
            "ligand_efficiency": round(self.ligand_efficiency, 4),
            "rotatable_bonds": self.rotatable_bonds,
            "heavy_atoms": self.heavy_atoms,
            "hbonds": self.hbonds,
            "contact_residues": len(self.contact_residues),
            "poses_kept": self.poses_kept,
            "receptor": self.receptor,
            "settings": self.settings,
            "provenance": (
                "COMPUTED: AutoDock Vina functional form (Trott & Olson 2010) ported "
                "from js/dock.js, evaluated on an MMFF-optimised 3D conformer docked "
                "by seeded Monte Carlo into a real PDB pocket. " + SCORE_CAVEAT),
        }


def score_molecule(mol, target: str, receptor: Optional[Receptor] = None,
                   runs: int = 4, steps: int = 600, box: float = 8.0,
                   seed: int = 0xC0FFEE, allow_network: bool = True,
                   name: str = "ligand") -> DockingResult:
    """Dock `mol` into `target`'s pocket and score the best pose.

    A search rather than a single placed pose: a one-shot score of an arbitrary
    placement mostly measures the placement, so two compounds would be ranked by
    how their MMFF conformer happened to land. The Monte Carlo search is the same
    algorithm js/dock.js uses, with a seeded RNG so a compound reproduces its own
    score. Defaults are small (4 runs x 600 steps) to keep enumeration usable;
    they are not enough sampling to call any pose converged, which is one more
    reason the output is a ranking and not an affinity.
    """
    from rdkit import Chem  # local, so vina_score stays rdkit-free

    rec = receptor or receptor_for(target, allow_network=allow_network)
    lig = ligand_from_mol(mol, name=name)
    poses = dock_ligand(rec.grid, lig, rec.center, runs=runs, steps=steps,
                        box=box, seed=seed)
    if not poses:
        raise ScoringError(f"{name}: docking into {rec.site.pdb_id} produced no pose")
    best = min(poses, key=lambda p: p.score)
    d = vina_score(rec.grid, lig, best.coords, details=True)
    return DockingResult(
        smiles=Chem.MolToSmiles(mol),
        vina_like_score=float(d["total"]),
        terms=dict(d["terms"]),
        raw_terms=dict(d["raw"]),
        ligand_efficiency=float(d["ligandEfficiency"]),
        rotatable_bonds=int(d["nrot"]),
        heavy_atoms=int(len(lig.heavy)),
        hbonds=len(d["hbonds"]),
        contact_residues=list(d["contactResidues"]),
        poses_kept=len(poses),
        receptor=rec.provenance,
        settings={"runs": runs, "steps": steps, "box": box, "seed": seed,
                  "search": "seeded Monte Carlo (port of dockLigand in js/dock.js)"},
    )


class PyreneVinaScorer:
    """Scores warhead pairs by assembling the compound and docking it.

    Held by ``PyreneSeries3Generator`` when structural scoring is switched on.
    One receptor is loaded per target and reused, so a library of compounds
    costs one PDB fetch and one parse.
    """

    def __init__(self, runs: int = 4, steps: int = 600, box: float = 8.0,
                 seed: int = 0xC0FFEE, allow_network: bool = True):
        self.runs, self.steps, self.box, self.seed = runs, steps, box, seed
        self.allow_network = allow_network
        self._receptors: Dict[str, Receptor] = {}

    def receptor(self, target: str) -> Receptor:
        if target not in self._receptors:
            self._receptors[target] = receptor_for(
                target, allow_network=self.allow_network)
        return self._receptors[target]

    def supports(self, target: str) -> bool:
        return target in TARGET_RECEPTORS

    def score_warheads(self, warhead_1: str, warhead_2: Optional[str],
                       target: str, name: str = "compound") -> DockingResult:
        import pyrene_structures as ps

        mol = ps.assemble(warhead_1, warhead_2)
        if mol is None:
            raise ScoringError(
                f"{name}: cannot assemble pyrene with warheads "
                f"{warhead_1!r}/{warhead_2!r}; no structure, so no score.")
        conf = ps.conformer(mol)
        if conf is None:
            raise ScoringError(
                f"{name}: 3D embedding failed for {warhead_1}/{warhead_2}; "
                "no conformer, so no score.")
        return score_molecule(conf, target, receptor=self.receptor(target),
                              runs=self.runs, steps=self.steps, box=self.box,
                              seed=self.seed, allow_network=self.allow_network,
                              name=name)
