"""AGI Compounds Pyrene Ring Series - Apoptotic Drug Discovery.

Specialized module for:
- Pyrene ring series categorization (Series 1-5)
- Warhead library for targeted modifications
- Apoptotic/anti-apoptotic mechanism design
- Pediatric safety optimization
- High-value target discovery
- Dynamic molecular adaptation

POTENCY NOW HAS TWO MODES, and every compound says which one produced it:

  * structural (real): pass a scorer -- ``PyreneSeries3Generator(
    structural_scorer=PyreneVinaScorer())`` -- and each compound is assembled
    into an actual molecule (server/pyrene_structures.py), given an MMFF 3D
    conformer, docked by seeded Monte Carlo into a real PDB pocket and scored
    with the AutoDock Vina functional form ported from js/dock.js. The result
    is ``vina_like_score``: a UNITLESS relative ranking, lower is better. It is
    not kcal/mol and not a binding free energy. If it cannot be produced -- no
    curated receptor for the target, no network and no cached PDB, an
    unassemblable warhead pair, a failed embed -- generation RAISES. It never
    falls back to the constants, because a silent fallback would be
    indistinguishable from a real score.

  * heuristic (default, synthetic): with no scorer, potency is still -8.5 minus
    hand-set per-warhead constants clamped at -11.5. That number is on no
    scale at all; it stays a SyntheticValue (prints "[SYNTHETIC]").

STUB NOTICE: safety, selectivity, accessibility and the "MD" batch remain
heuristics over hand-set warhead constants, emitted as SyntheticValue in
records whose `provenance` field says so. Warhead enumeration and mechanism
mapping are real logic.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from synthetic_provenance import SyntheticValue, provenance, stamp

# Name for the structural score, kept in one place so nothing downstream has to
# invent a label (and so nothing can quietly write "kcal/mol" next to it).
STRUCTURAL_MODEL = (
    "vina_like_score: unitless relative ranking from the AutoDock Vina "
    "functional form (Trott & Olson 2010) ported from js/dock.js, computed on a "
    "docked 3D conformer against a real PDB receptor. Lower is better. NOT "
    "kcal/mol, NOT a binding free energy, not comparable across receptors.")
HEURISTIC_MODEL = provenance(
    "no docking ran; potency is -8.5 minus hand-set warhead constants, on no scale.")

@dataclass
class PyreneSeries:
    """Pyrene ring series classification."""
    series_id: str  # Series 1-5
    name: str
    base_structure: str  # SMILES
    rings: int  # Number of aromatic rings
    warheads: List[str]  # Available warhead modifications
    binding_affinity_range: Tuple[float, float]  # hand-set design target, kcal/mol-like scale; not measured
    apoptotic_mechanism: str
    pediatric_safety: float  # hand-set 0-1 design assumption; not measured
    target_class: str

class ApoptosisType(Enum):
    """Types of apoptotic mechanisms."""
    INTRINSIC = "intrinsic"  # Mitochondrial pathway
    EXTRINSIC = "extrinsic"  # Death receptor pathway
    GRANZYME = "granzyme"  # Cytotoxic T-cell pathway
    HYBRID = "hybrid"  # Combined mechanisms
    ANTI_APOPTOTIC = "anti_apoptotic"  # Prevents programmed cell death

class WarheadType(Enum):
    """Chemical warhead types for targeted modification."""
    ELECTROPHILE = "electrophile"  # Michael acceptor
    METAL_CHELATOR = "metal_chelator"  # Metal binding
    HYDROGEN_BOND = "hydrogen_bond"  # H-bond donor/acceptor
    HYDROPHOBIC = "hydrophobic"  # Lipophilic patch
    BIOISOSTERE = "bioisostere"  # Chemically equivalent
    LINKER = "linker"  # Connection point
    TARGETING = "targeting"  # Cell/tissue specific

@dataclass
class PyreneCompound:
    """Designed pyrene-based compound."""
    compound_id: str
    series: str  # Series 1-5
    base_pyrene: str  # SMILES
    warhead_1: str  # First modification
    warhead_2: Optional[str]  # Second modification
    warhead_types: List[WarheadType]
    apoptotic_mechanism: ApoptosisType
    target_protein: str
    target_indication: str
    pediatric_safety_score: float  # SyntheticValue, 0-1 heuristic over hand-set warhead constants
    predicted_potency: float  # see `binding_model`: real vina_like_score, or a SyntheticValue constant
    synthetic_accessibility: float  # SyntheticValue, 0-1 (easy to hard) heuristic
    selectivity_score: float  # SyntheticValue, 0.6-1.0 heuristic
    combination_partners: List[str]  # Known drugs to combine with
    # Structural scoring, populated only when a scorer was supplied.
    vina_like_score: Optional[float] = None  # unitless ranking; None when unscored
    smiles: Optional[str] = None             # the molecule that was actually scored
    binding_record: Optional[Dict] = None    # terms, receptor, pose settings
    binding_model: str = HEURISTIC_MODEL     # which of the two modes produced potency
    provenance: str = provenance(
        "no docking, MD or safety model was run; scores are heuristics over hand-set warhead constants.",
        "pediatric_safety_score", "predicted_potency", "synthetic_accessibility", "selectivity_score")

    @property
    def potency_is_computed(self) -> bool:
        """True when `predicted_potency` came from a structure, not a constant."""
        return self.vina_like_score is not None

class PyreneSeries3Generator:
    """Generates Series 3 pyrene compounds with apoptotic design.

    Args:
        structural_scorer: a ``pyrene_docking.PyreneVinaScorer`` (or anything with
            the same ``score_warheads`` interface). Supplied, every compound is
            assembled, docked and scored from its real 3D structure, and any
            compound that cannot be scored raises. Omitted, potency falls back to
            the hand-set constants -- which is a labelled, opt-out default, not a
            silent rescue after a failure.
    """

    def __init__(self, structural_scorer=None):
        self.structural_scorer = structural_scorer
        self.series_definitions = self._initialize_series()
        self.warhead_library = self._initialize_warheads()
        self.apoptosis_mechanisms = self._initialize_apoptosis()
        self.pediatric_safety_database = self._load_pediatric_safety()
        self.generated_compounds = []

    def _initialize_series(self) -> Dict[str, PyreneSeries]:
        """Initialize pyrene series definitions."""
        return {
            'series_3': PyreneSeries(
                series_id='series_3',
                name='Pyrene-3 Platform',
                base_structure='C1=CC=C2C(=C1)C=CC3=CC=CC=C32',  # Pyrene core
                rings=4,
                warheads=[
                    'acrylamide',  # Michael acceptor for cysteine
                    'isothiazole',  # Warhead for serine
                    'vinylsulfonamide',  # Thiol-reactive
                    'cyanoketone',  # Ketone warhead
                ],
                binding_affinity_range=(-10.5, -7.2),
                apoptotic_mechanism='intrinsic_mitochondrial',
                pediatric_safety=0.92,
                target_class='anti-apoptotic_proteins',
            ),
            'series_1': PyreneSeries(
                series_id='series_1',
                name='Pyrene-1 Classic',
                base_structure='c1ccc2cc3ccccc3cc2c1',
                rings=3,
                warheads=['hydroxyl', 'amine', 'carboxylic_acid'],
                binding_affinity_range=(-9.5, -6.5),
                apoptotic_mechanism='extrinsic',
                pediatric_safety=0.85,
                target_class='death_receptors',
            ),
        }

    def _initialize_warheads(self) -> Dict[str, Dict]:
        """Initialize warhead library with properties."""
        return {
            # Electrophilic warheads
            'acrylamide': {
                'type': WarheadType.ELECTROPHILE,
                'smarts': 'C=CC(=O)N',
                'targets': ['cysteine', 'lysine'],
                'potency_boost': 1.5,  # hand-set heuristic weight, not a measured shift
                'selectivity_risk': 0.2,
                'pediatric_safety': 0.88,
            },
            'vinylsulfonamide': {
                'type': WarheadType.ELECTROPHILE,
                'smarts': 'C=CS(=O)(=O)N',
                'targets': ['cysteine'],
                'potency_boost': 1.8,
                'selectivity_risk': 0.15,
                'pediatric_safety': 0.90,
            },
            'cyanoketone': {
                'type': WarheadType.ELECTROPHILE,
                'smarts': 'C(=O)C#N',
                'targets': ['lysine', 'arginine'],
                'potency_boost': 1.3,
                'selectivity_risk': 0.25,
                'pediatric_safety': 0.85,
            },

            # Metal chelators
            'hydroxamate': {
                'type': WarheadType.METAL_CHELATOR,
                'smarts': 'C(=O)NO',
                'targets': ['zinc', 'iron'],
                'potency_boost': 2.0,
                'selectivity_risk': 0.30,
                'pediatric_safety': 0.80,
            },
            'catechol': {
                'type': WarheadType.METAL_CHELATOR,
                'smarts': 'Oc1ccccc1O',
                'targets': ['zinc', 'copper'],
                'potency_boost': 1.7,
                'selectivity_risk': 0.35,
                'pediatric_safety': 0.75,
            },

            # H-bond warheads
            'amide': {
                'type': WarheadType.HYDROGEN_BOND,
                'smarts': 'C(=O)N',
                'targets': ['backbone', 'side_chains'],
                'potency_boost': 0.8,
                'selectivity_risk': 0.10,
                'pediatric_safety': 0.95,
            },
            'urea': {
                'type': WarheadType.HYDROGEN_BOND,
                'smarts': 'NC(=O)N',
                'targets': ['backbone', 'carboxylic_acid'],
                'potency_boost': 1.0,
                'selectivity_risk': 0.12,
                'pediatric_safety': 0.93,
            },

            # Hydrophobic patches
            'trifluoromethyl': {
                'type': WarheadType.HYDROPHOBIC,
                'smarts': 'CF3',
                'targets': ['lipophilic_pocket'],
                'potency_boost': 0.6,
                'selectivity_risk': 0.05,
                'pediatric_safety': 0.97,
            },
            'phenyl': {
                'type': WarheadType.HYDROPHOBIC,
                'smarts': 'c1ccccc1',
                'targets': ['aromatic_pocket'],
                'potency_boost': 0.7,
                'selectivity_risk': 0.08,
                'pediatric_safety': 0.94,
            },

            # Targeting warheads
            'folate': {
                'type': WarheadType.TARGETING,
                'smarts': 'Nc1nc(N)nc2[nH]cnc12',
                'targets': ['folate_receptor'],
                'potency_boost': 0.5,
                'selectivity_risk': 0.02,
                'pediatric_safety': 0.89,
                'notes': 'Pediatric cancer targeting',
            },
            'glucose': {
                'type': WarheadType.TARGETING,
                'smarts': 'OC[C@H]1O[C@H](O)[C@H](O)[C@H]1O',
                'targets': ['glucose_transporter'],
                'potency_boost': 0.4,
                'selectivity_risk': 0.03,
                'pediatric_safety': 0.98,
                'notes': 'Metabolic tumor targeting',
            },
        }

    def _initialize_apoptosis(self) -> Dict[str, Dict]:
        """Initialize apoptotic mechanism database."""
        return {
            'bcl2_inhibition': {
                'type': ApoptosisType.INTRINSIC,
                'mechanism': 'BCL2/BCL-xL inhibitor - mitochondrial release of cytochrome c',
                'target_proteins': ['BCL2', 'BCL-xL', 'MCL1'],
                'upstream_activators': ['BAX', 'BAK', 'BID'],
                'diseases': ['lymphoma', 'leukemia', 'solid_tumors'],
                'pediatric_relevance': 0.95,
                'synergy_partners': ['ABT-737', 'Venetoclax'],
            },
            'death_receptor': {
                'type': ApoptosisType.EXTRINSIC,
                'mechanism': 'FAS/TNF receptor activation - DISC formation',
                'target_proteins': ['FAS', 'TNFR1', 'TRAIL_receptors'],
                'downstream_caspases': ['caspase-8', 'caspase-3'],
                'diseases': ['leukemia', 'lymphoma', 'carcinoma'],
                'pediatric_relevance': 0.88,
                'synergy_partners': ['anti-FAS', 'TRAIL_agonists'],
            },
            'iam_suppression': {
                'type': ApoptosisType.ANTI_APOPTOTIC,
                'mechanism': 'Inhibitor of apoptosis (IAP) antagonism - SMAC mimetics',
                'target_proteins': ['XIAP', 'cIAP1', 'cIAP2', 'survivin'],
                'downstream_effects': ['caspase activation', 'apoptosis'],
                'diseases': ['cancer', 'infection', 'inflammation'],
                'pediatric_relevance': 0.92,
                'synergy_partners': ['TNF-alpha', 'birinapant'],
            },
            'granzyme_b': {
                'type': ApoptosisType.GRANZYME,
                'mechanism': 'Cytotoxic T-lymphocyte granule pathway',
                'target_proteins': ['granzyme_B', 'perforin'],
                'downstream_effects': ['mitochondrial_disruption', 'apoptosis'],
                'diseases': ['cancer', 'viral_infection'],
                'pediatric_relevance': 0.90,
                'synergy_partners': ['checkpoint_inhibitors', 'CAR-T'],
            },
            'caspase_activation': {
                'type': ApoptosisType.HYBRID,
                'mechanism': 'Direct caspase-3/7 activation - executioner phase',
                'target_proteins': ['caspase-3', 'caspase-7', 'caspase-9'],
                'downstream_effects': ['PARP_cleavage', 'DNA_fragmentation'],
                'diseases': ['all_cancers', 'chronic_diseases'],
                'pediatric_relevance': 0.93,
                'synergy_partners': ['broad_spectrum', 'many_combinations'],
            },
            'autophagy_trigger': {
                'type': ApoptosisType.HYBRID,
                'mechanism': 'Autophagic cell death - self-digestion pathway',
                'target_proteins': ['mTOR', 'ATG_genes', 'beclin1'],
                'downstream_effects': ['lysosomal_degradation', 'cell_death'],
                'diseases': ['resistant_tumors', 'neurodegenerative'],
                'pediatric_relevance': 0.85,
                'synergy_partners': ['mTOR_inhibitors', 'PI3K_inhibitors'],
            },
        }

    def _load_pediatric_safety(self) -> Dict:
        """Load pediatric-specific safety database."""
        return {
            'dose_scaling': {
                'methodology': 'mg/kg body weight',
                'age_groups': {
                    'neonatal': '0-28 days',
                    'infant': '29 days-2 years',
                    'toddler': '2-6 years',
                    'child': '6-12 years',
                    'adolescent': '12-18 years',
                },
                'scaling_factors': {
                    'neonatal': 0.5,
                    'infant': 0.6,
                    'toddler': 0.8,
                    'child': 0.9,
                    'adolescent': 1.0,
                }
            },
            'organ_sensitivities': {
                'liver': 0.95,  # Immature metabolism
                'kidney': 0.88,  # Developing filtration
                'brain': 0.92,  # BBB still forming
                'bone': 0.85,   # Growth plates active
                'heart': 0.90,   # Developing conduction
            },
            'toxicity_thresholds': {
                'hepatotoxicity': 'max_ALT_3xULN',
                'nephrotoxicity': 'max_creatinine_1.5xbaseline',
                'cardiotoxicity': 'EF_drop_>10%',
                'neurotoxicity': 'peripheral_neuropathy_grade_2',
            },
            'contraindicated_warheads': [
                'excessive_electrophiles',  # Protein binding
                'high_lipophilicity',        # Accumulation risk
                'metal_chelators_excess',    # Developmental impact
                'dna_damaging',              # Leukemia risk
            ],
        }

    def generate_series3_compounds(
        self,
        target_protein: str,
        target_indication: str,
        num_compounds: int = 20,
        apoptotic_mechanism: Optional[ApoptosisType] = None,
        offset: int = 0,
        prefer: Optional[List[str]] = None,
    ) -> List[PyreneCompound]:
        """Generate Series 3 pyrene compounds with optimizations.

        Args:
            target_protein: e.g., 'BCL2', 'FAS', 'XIAP'
            target_indication: e.g., 'pediatric_lymphoma'
            num_compounds: Number of compounds to generate
            apoptotic_mechanism: Specific apoptotic pathway
            offset: Start position in the pair enumeration. Successive evolution
                cycles pass a rising offset so each explores unseen chemistry.
            prefer: Warheads to prioritize ahead of the target defaults, used to
                bias generation toward warheads found in earlier top performers.

        Returns:
            List of designed PyreneCompound objects
        """

        compounds = []
        series_def = self.series_definitions['series_3']

        for i, (warhead_1, warhead_2) in enumerate(
            self._warhead_pairs(target_protein, num_compounds, offset, prefer)
        ):
            # Determine apoptotic mechanism
            mechanism = apoptotic_mechanism or self._select_mechanism(target_protein)

            compound_id = f"AGI-PYRENE3-{offset+i+1:04d}"

            # Potency: a real structure-derived score when a scorer is attached,
            # the hand-set constant otherwise. `structural` is None in the
            # second case, which is what marks the compound as unscored.
            structural = self._structural_score(
                warhead_1, warhead_2, target_protein, compound_id)
            if structural is None:
                predicted_potency = self._calculate_binding_energy(
                    warhead_1, warhead_2, target_protein
                )
            else:
                predicted_potency = structural["score"]

            pediatric_safety = self._calculate_pediatric_safety(
                warhead_1, warhead_2, target_indication
            )

            selectivity = self._calculate_selectivity(
                warhead_1, warhead_2, target_protein
            )

            synthetic_accessibility = self._estimate_synthetic_accessibility(
                warhead_1, warhead_2
            )

            # Get combination partners
            partners = self._find_synergy_partners(
                target_protein, mechanism, target_indication
            )

            compound = PyreneCompound(
                compound_id=compound_id,
                series='series_3',
                base_pyrene=series_def.base_structure,
                warhead_1=warhead_1,
                warhead_2=warhead_2,
                warhead_types=[
                    self.warhead_library[warhead_1]['type'],
                    self.warhead_library[warhead_2]['type'],
                ],
                apoptotic_mechanism=mechanism,
                target_protein=target_protein,
                target_indication=target_indication,
                pediatric_safety_score=pediatric_safety,
                predicted_potency=predicted_potency,
                synthetic_accessibility=synthetic_accessibility,
                selectivity_score=selectivity,
                combination_partners=partners,
                vina_like_score=None if structural is None else structural["score"],
                smiles=None if structural is None else structural["smiles"],
                binding_record=None if structural is None else structural["record"],
                binding_model=HEURISTIC_MODEL if structural is None else STRUCTURAL_MODEL,
                provenance=self._compound_provenance(structural),
            )

            compounds.append(compound)
            self.generated_compounds.append(compound)

        return compounds

    def _target_preferences(self, target: str) -> List[str]:
        """Warheads with a mechanistic rationale for this target."""

        warhead_preferences = {
            'BCL2': ['acrylamide', 'vinylsulfonamide'],  # Cysteine-reactive
            'FAS': ['hydroxamate', 'cyanoketone'],  # Metal coordination
            'XIAP': ['acrylamide', 'amide'],  # Broad electrophile
            'caspase-3': ['cyanoketone', 'vinylsulfonamide'],  # Active site
        }

        return warhead_preferences.get(target, list(self.warhead_library.keys())[:3])

    def _warhead_pairs(
        self,
        target: str,
        count: int,
        offset: int = 0,
        prefer: Optional[List[str]] = None,
    ) -> List[Tuple[str, str]]:
        """Enumerate distinct warhead pairs, target-preferred combinations first.

        Deterministic so a given request reproduces the same library, but it walks
        the full combinatorial space instead of returning one pair repeatedly.
        """

        preferred = list(prefer or []) + [
            w for w in self._target_preferences(target) if w not in (prefer or [])
        ]
        ordered = preferred + [w for w in self.warhead_library if w not in preferred]

        pairs = [(a, b) for a in ordered for b in ordered if a != b]
        # Stable sort keeps `ordered` priority inside each tier: both-preferred,
        # then one-preferred, then neither.
        pairs.sort(key=lambda p: (p[0] not in preferred) + (p[1] not in preferred))

        return [pairs[(offset + i) % len(pairs)] for i in range(count)]

    def _select_mechanism(self, target: str) -> ApoptosisType:
        """Select apoptotic mechanism for target."""

        mechanism_map = {
            'BCL2': ApoptosisType.INTRINSIC,
            'BCL-xL': ApoptosisType.INTRINSIC,
            'FAS': ApoptosisType.EXTRINSIC,
            'TNFR1': ApoptosisType.EXTRINSIC,
            'XIAP': ApoptosisType.ANTI_APOPTOTIC,
            'survivin': ApoptosisType.ANTI_APOPTOTIC,
            'caspase-3': ApoptosisType.HYBRID,
        }

        return mechanism_map.get(target, ApoptosisType.INTRINSIC)

    def _structural_score(
        self,
        warhead_1: str,
        warhead_2: Optional[str],
        target: str,
        compound_id: str,
    ) -> Optional[Dict]:
        """Assemble, dock and score the compound. None only when no scorer is set.

        Any *failure* with a scorer set propagates. That is deliberate: the one
        thing this module must never do again is emit a number that looks like a
        binding energy but came from a lookup table, and a fallback here would
        reintroduce exactly that, silently.
        """

        scorer = self.structural_scorer
        if scorer is None:
            return None

        result = scorer.score_warheads(warhead_1, warhead_2, target, name=compound_id)
        return {
            "score": float(result.vina_like_score),
            "smiles": result.smiles,
            "record": result.as_record(),
        }

    @staticmethod
    def _compound_provenance(structural: Optional[Dict]) -> str:
        if structural is None:
            return provenance(
                "no docking, MD or safety model was run; scores are heuristics over "
                "hand-set warhead constants.",
                "pediatric_safety_score", "predicted_potency",
                "synthetic_accessibility", "selectivity_score")
        # Potency is computed now; everything else here is still a constant, so
        # the marker has to stay on those fields and only those.
        return (
            "COMPUTED predicted_potency/vina_like_score: " + STRUCTURAL_MODEL + " "
            + provenance(
                "no safety, selectivity or accessibility model was run.",
                "pediatric_safety_score", "synthetic_accessibility", "selectivity_score"))

    def _calculate_binding_energy(
        self,
        warhead_1: str,
        warhead_2: str,
        target: str,
    ) -> float:
        """Placeholder potency: -8.5 minus hand-set warhead constants, clamped
        at -11.5. No docking; the number is not kcal/mol.

        Reachable only when no ``structural_scorer`` was supplied. It is NOT a
        fallback: a scorer that fails raises instead of landing here.
        """

        energy = -8.5
        energy -= self.warhead_library[warhead_1]['potency_boost']
        if warhead_2:
            energy -= self.warhead_library[warhead_2]['potency_boost'] * 0.6

        if 'BCL' in target:
            energy -= 0.5

        return SyntheticValue(max(energy, -11.5))

    def _calculate_pediatric_safety(
        self,
        warhead_1: str,
        warhead_2: str,
        indication: str,
    ) -> float:
        """Heuristic 0-1 safety score over hand-set warhead constants; no model."""

        safety = 0.9  # Start high

        # Warhead penalties
        safety *= self.warhead_library[warhead_1]['pediatric_safety']
        if warhead_2:
            safety *= self.warhead_library[warhead_2]['pediatric_safety']

        # Indication-specific
        if 'pediatric' in indication.lower():
            safety *= 1.05  # Boost if specifically designed

        if 'cancer' in indication.lower():
            safety *= 0.95  # Slightly lower for cancer

        return SyntheticValue(min(safety, 1.0))

    def _calculate_selectivity(
        self,
        warhead_1: str,
        warhead_2: str,
        target: str,
    ) -> float:
        """Selectivity score, higher is better: 1.0 minus accumulated off-target risk.

        Consumers rank on this ascending (the composite score weights it +0.20).
        Note the floor below clamps the real range to 0.6-1.0, not 0-1, so the
        documented "selectivity >= 0.80" gate is weaker than it reads.
        """

        selectivity = 1.0

        # Account for off-target risk
        selectivity -= self.warhead_library[warhead_1]['selectivity_risk']
        if warhead_2:
            selectivity -= self.warhead_library[warhead_2]['selectivity_risk'] * 0.5

        return SyntheticValue(max(selectivity, 0.6))

    def _estimate_synthetic_accessibility(
        self,
        warhead_1: str,
        warhead_2: str,
    ) -> float:
        """Estimate synthetic accessibility (0=easy, 1=hard)."""

        # Pyrene core is moderately complex
        accessibility = 0.6

        # Common warheads are easier
        easy_warheads = ['amide', 'urea', 'phenyl', 'trifluoromethyl']

        if warhead_1 in easy_warheads:
            accessibility -= 0.1

        if warhead_2 and warhead_2 in easy_warheads:
            accessibility -= 0.05

        return SyntheticValue(max(accessibility, 0.3))

    def _find_synergy_partners(
        self,
        target: str,
        mechanism: ApoptosisType,
        indication: str,
    ) -> List[str]:
        """Find known drugs to combine with."""

        synergy_map = {
            ApoptosisType.INTRINSIC: [
                'Venetoclax',  # BCL2 inhibitor
                'ABT-263',     # BCL2/BCL-xL inhibitor
                'dexamethasone',  # BCL2 expression
            ],
            ApoptosisType.EXTRINSIC: [
                'TRAIL',       # Death receptor ligand
                'anti-FAS',    # FAS agonist
                'TNF-alpha',   # TNFR activation
            ],
            ApoptosisType.ANTI_APOPTOTIC: [
                'birinapant',  # SMAC mimetic
                'TNF-alpha',   # Sensitizer
                'checkpoint_inhibitors',
            ],
            ApoptosisType.HYBRID: [
                'pan_caspase_inhibitors',
                'mitochondrial_disruptors',
                'autophagy_modulators',
            ],
        }

        partners = synergy_map.get(mechanism, [])

        # Add pediatric-specific combinations
        if 'pediatric' in indication.lower():
            partners.extend(['doxorubicin', 'etoposide', 'cyclophosphamide'])

        return partners[:3]  # Top 3 partners

    def batch_molecular_dynamics(
        self,
        compounds: List[PyreneCompound],
        target_structure: str,
        duration_ns: int = 100,
    ) -> Dict:
        """MD STUB: no simulation runs and `target_structure` is never opened.
        Stability is a warhead-type heuristic; every number is synthetic."""

        results = {
            'compounds_simulated': len(compounds),
            'duration_ns': duration_ns,
            'refined_compounds': [],
        }

        for compound in compounds:
            stability = self._calculate_md_stability(compound)
            refined_affinity = compound.predicted_potency - stability * 0.5

            results['refined_compounds'].append(stamp({
                'compound_id': compound.compound_id,
                'original_affinity': compound.predicted_potency,
                'refined_affinity': refined_affinity,
                'stability_score': stability,
                'recommended': refined_affinity < -9.0,
            }, "no MD was run.", "recommended"))

        return stamp(results, "no MD was run; duration_ns is the request, not a simulation.")

    def _calculate_md_stability(self, compound: PyreneCompound) -> float:
        """Warhead-type heuristic standing in for MD stability."""

        # More electrophilic warheads = higher stability
        stability = 0.5

        if compound.warhead_types:
            for wtype in compound.warhead_types:
                if wtype == WarheadType.ELECTROPHILE:
                    stability += 0.2
                elif wtype == WarheadType.HYDROGEN_BOND:
                    stability += 0.15
                elif wtype == WarheadType.HYDROPHOBIC:
                    stability += 0.1

        return SyntheticValue(min(stability, 1.0))

    def get_compound_summary(self, compound: PyreneCompound) -> Dict:
        """Summary of a designed compound; heuristic scores are marked synthetic.

        The potency line names its own model, so a reader never has to guess
        whether the number came from a structure or from a lookup table -- and
        the structural one carries no units, because it has none.
        """

        if compound.potency_is_computed:
            potency = (f"{compound.vina_like_score:.2f} "
                       "(vina_like_score, unitless ranking; not kcal/mol)")
        else:
            potency = f"{compound.predicted_potency:.2f} (heuristic, not kcal/mol)"

        return stamp({
            'compound_id': compound.compound_id,
            'potency': potency,
            'binding_model': compound.binding_model,
            'smiles': compound.smiles,
            'series': compound.series,
            'target': compound.target_protein,
            'indication': compound.target_indication,
            'apoptotic_mechanism': compound.apoptotic_mechanism.value,
            'warheads': [compound.warhead_1, compound.warhead_2],
            'warhead_types': [t.value for t in compound.warhead_types],
            'predicted_potency': potency,
            'pediatric_safety': f"{compound.pediatric_safety_score:.2%}",
            'selectivity': f"{compound.selectivity_score:.2%}",
            'synthetic_difficulty': f"{compound.synthetic_accessibility:.1f}/1.0",
            'synergy_partners': compound.combination_partners,
            'next_step': 'Molecular Dynamics validation',
        }, "heuristic scores over hand-set warhead constants; no docking or safety model was run.")
