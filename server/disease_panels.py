"""Disease-specific target panels for foundation research programs.

Pre-curated lists of validated targets for:
- ALS (Amyotrophic Lateral Sclerosis)
- Parkinson's Disease
- Shriners Children's (Osteogenesis Imperfecta, Skeletal Dysplasia)
"""
from typing import Dict, List

DISEASE_PANELS = {
    'ALS': {
        'name': 'Amyotrophic Lateral Sclerosis',
        'description': '20 targets associated with familial and sporadic ALS',
        'programs': ['ALS Association', 'Project ALS', 'Augie & Rose'],
        'targets': [
            {'symbol': 'SOD1', 'name': 'Superoxide Dismutase 1', 'inheritance': 'AD', 'prevalence': '20% fALS', 
             'mechanism': 'Protein misfolding', 'pdb_count': 50, 'alphafold': True},
            {'symbol': 'TDP43', 'name': 'TAR DNA-binding protein 43', 'inheritance': 'AD/AR', 'prevalence': '5% fALS, 50% sALS',
             'mechanism': 'RNA processing, neuronal aggregation', 'pdb_count': 15, 'alphafold': True},
            {'symbol': 'FUS', 'name': 'Fused in Sarcoma', 'inheritance': 'AD', 'prevalence': '5% fALS',
             'mechanism': 'RNA binding, aggregation', 'pdb_count': 20, 'alphafold': True},
            {'symbol': 'C9ORF72', 'name': 'Chromosome 9 Open Reading Frame 72', 'inheritance': 'AD', 'prevalence': '25% fALS',
             'mechanism': 'GGGGCC repeat expansion', 'pdb_count': 5, 'alphafold': True},
            {'symbol': 'TBK1', 'name': 'TANK-binding kinase 1', 'inheritance': 'AD', 'prevalence': '1-2% fALS',
             'mechanism': 'Autophagy impairment', 'pdb_count': 30, 'alphafold': True},
            {'symbol': 'OPTN', 'name': 'Optineurin', 'inheritance': 'AD/AR', 'prevalence': '1% fALS',
             'mechanism': 'Autophagy, NF-κB signaling', 'pdb_count': 10, 'alphafold': True},
            {'symbol': 'VCP', 'name': 'Valosin-containing protein', 'inheritance': 'AD', 'prevalence': '1% fALS',
             'mechanism': 'AAA-ATPase, protein degradation', 'pdb_count': 40, 'alphafold': True},
            {'symbol': 'SQSTM1', 'name': 'Sequestosome-1 (p62)', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'Autophagy adapter', 'pdb_count': 15, 'alphafold': True},
            {'symbol': 'UBQLN2', 'name': 'Ubiquilin-2', 'inheritance': 'XD', 'prevalence': '<1% fALS',
             'mechanism': 'UPS pathway', 'pdb_count': 8, 'alphafold': True},
            {'symbol': 'PFN1', 'name': 'Profilin 1', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'Actin dynamics', 'pdb_count': 25, 'alphafold': True},
            {'symbol': 'KIF5A', 'name': 'Kinesin Family Member 5A', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'Axonal transport', 'pdb_count': 10, 'alphafold': True},
            {'symbol': 'NEK1', 'name': 'NIMA-related kinase 1', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'Cell cycle, autophagy', 'pdb_count': 8, 'alphafold': True},
            {'symbol': 'ATXN2', 'name': 'Ataxin-2', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'RNA binding', 'pdb_count': 5, 'alphafold': True},
            {'symbol': 'MATR3', 'name': 'Matrin-3', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'RNA splicing', 'pdb_count': 3, 'alphafold': True},
            {'symbol': 'HNRNPA1', 'name': 'Heterogeneous nuclear ribonucleoprotein A1', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'RNA binding', 'pdb_count': 20, 'alphafold': True},
            {'symbol': 'CHCHD10', 'name': 'Coiled-coil-helix-coiled-coil-helix domain containing 10', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'Mitochondrial dynamics', 'pdb_count': 2, 'alphafold': True},
            {'symbol': 'ANG', 'name': 'Angiogenin', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'Stress response, angiogenesis', 'pdb_count': 15, 'alphafold': True},
            {'symbol': 'STMN2', 'name': 'Stathmin-2', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'Microtubule dynamics', 'pdb_count': 2, 'alphafold': True},
            {'symbol': 'UNC13A', 'name': 'Unc-13 homolog A', 'inheritance': 'AD', 'prevalence': '<1% fALS',
             'mechanism': 'Synaptic release', 'pdb_count': 5, 'alphafold': True},
            {'symbol': 'SIGMAR1', 'name': 'Sigma non-opioid intracellular receptor 1', 'inheritance': 'AR', 'prevalence': '<1% fALS',
             'mechanism': 'ER chaperone', 'pdb_count': 8, 'alphafold': True},
        ]
    },
    'Parkinsons': {
        'name': 'Parkinson\'s Disease',
        'description': '13 targets associated with early-onset and sporadic Parkinson\'s',
        'programs': ['Michael J. Fox Foundation', 'Parkinson\'s Foundation'],
        'targets': [
            {'symbol': 'SNCA', 'name': 'Alpha-synuclein', 'inheritance': 'AD', 'prevalence': '5-10% fPD',
             'mechanism': 'Protein aggregation, neuroinflammation', 'pdb_count': 80, 'alphafold': True},
            {'symbol': 'LRRK2', 'name': 'Leucine-rich repeat kinase 2', 'inheritance': 'AD', 'prevalence': '5-10% fPD, 1% sPD',
             'mechanism': 'Kinase signaling, mitochondrial dysfunction', 'pdb_count': 40, 'alphafold': True},
            {'symbol': 'GBA1', 'name': 'Glucosidase beta acid 1', 'inheritance': 'AR (homozygous)', 'prevalence': '7-10% sPD',
             'mechanism': 'Lysosomal dysfunction, α-syn accumulation', 'pdb_count': 25, 'alphafold': True},
            {'symbol': 'PINK1', 'name': 'PTEN-induced kinase 1', 'inheritance': 'AR', 'prevalence': '3% fPD',
             'mechanism': 'Mitophagy, mitochondrial quality control', 'pdb_count': 10, 'alphafold': True},
            {'symbol': 'PRKN', 'name': 'Parkin', 'inheritance': 'AR', 'prevalence': '5% fPD',
             'mechanism': 'E3 ubiquitin ligase, mitophagy', 'pdb_count': 30, 'alphafold': True},
            {'symbol': 'PARK7', 'name': 'DJ-1', 'inheritance': 'AR', 'prevalence': '1% fPD',
             'mechanism': 'Oxidative stress response', 'pdb_count': 35, 'alphafold': True},
            {'symbol': 'VPS35', 'name': 'Vacuolar protein sorting 35', 'inheritance': 'AD', 'prevalence': '<1% fPD',
             'mechanism': 'Retromer function, endosomal sorting', 'pdb_count': 15, 'alphafold': True},
            {'symbol': 'MAOB', 'name': 'Monoamine oxidase B', 'inheritance': 'XL', 'prevalence': 'Risk locus',
             'mechanism': 'Dopamine catabolism, ROS generation', 'pdb_count': 35, 'alphafold': True},
            {'symbol': 'COMT', 'name': 'Catechol-O-methyltransferase', 'inheritance': 'N/A', 'prevalence': 'Risk locus',
             'mechanism': 'Dopamine degradation', 'pdb_count': 20, 'alphafold': True},
            {'symbol': 'DRD2', 'name': 'Dopamine receptor D2', 'inheritance': 'N/A', 'prevalence': 'Therapeutic target',
             'mechanism': 'Dopamine signaling', 'pdb_count': 60, 'alphafold': True},
            {'symbol': 'TH', 'name': 'Tyrosine hydroxylase', 'inheritance': 'N/A', 'prevalence': 'Neurodegeneration marker',
             'mechanism': 'Dopamine synthesis', 'pdb_count': 45, 'alphafold': True},
            {'symbol': 'UCHL1', 'name': 'Ubiquitin C-terminal hydrolase L1', 'inheritance': 'N/A', 'prevalence': '<1% fPD',
             'mechanism': 'Ubiquitin processing', 'pdb_count': 15, 'alphafold': True},
            {'symbol': 'ATP13A2', 'name': 'ATPase 13A2', 'inheritance': 'AR', 'prevalence': '<1% fPD',
             'mechanism': 'Lysosomal ion homeostasis', 'pdb_count': 5, 'alphafold': True},
        ]
    },
    'Shriners': {
        'name': 'Shriners Children\'s Research',
        'description': '15 targets for osteogenesis imperfecta, skeletal dysplasia, and burn care',
        'programs': ['Shriners Children\'s'],
        'targets': [
            {'symbol': 'COL1A1', 'name': 'Collagen type I alpha 1', 'inheritance': 'AD', 'prevalence': '50% OI',
             'mechanism': 'Structural protein, type I collagen synthesis', 'pdb_count': 120, 'alphafold': True},
            {'symbol': 'COL1A2', 'name': 'Collagen type I alpha 2', 'inheritance': 'AD', 'prevalence': '50% OI',
             'mechanism': 'Structural protein, type I collagen synthesis', 'pdb_count': 100, 'alphafold': True},
            {'symbol': 'SOST', 'name': 'Sclerostin', 'inheritance': 'AD/AR', 'prevalence': 'Sclerosteosis',
             'mechanism': 'Wnt signaling antagonist', 'pdb_count': 45, 'alphafold': True},
            {'symbol': 'TNFSF11', 'name': 'TNF superfamily member 11 (RANKL)', 'inheritance': 'N/A', 'prevalence': 'Osteoimmunology',
             'mechanism': 'Osteoclast differentiation', 'pdb_count': 50, 'alphafold': True},
            {'symbol': 'FGFR3', 'name': 'Fibroblast growth factor receptor 3', 'inheritance': 'AD', 'prevalence': 'Achondroplasia, hypochondroplasia',
             'mechanism': 'Growth plate signaling', 'pdb_count': 70, 'alphafold': True},
            {'symbol': 'NPR2', 'name': 'Natriuretic peptide receptor 2', 'inheritance': 'AR', 'prevalence': 'Short stature',
             'mechanism': 'cGMP signaling in growth plate', 'pdb_count': 15, 'alphafold': True},
            {'symbol': 'ALPL', 'name': 'Alkaline phosphatase', 'inheritance': 'AR', 'prevalence': 'Hypophosphatasia',
             'mechanism': 'Bone mineralization', 'pdb_count': 40, 'alphafold': True},
            {'symbol': 'FGF23', 'name': 'Fibroblast growth factor 23', 'inheritance': 'AD', 'prevalence': 'X-linked hypophosphatemia',
             'mechanism': 'Phosphate homeostasis', 'pdb_count': 20, 'alphafold': True},
            {'symbol': 'PHEX', 'name': 'Phosphate-regulating neutral endopeptidase', 'inheritance': 'XD', 'prevalence': 'X-linked hypophosphatemia',
             'mechanism': 'FGF23 regulation', 'pdb_count': 10, 'alphafold': True},
            {'symbol': 'IRF6', 'name': 'Interferon regulatory factor 6', 'inheritance': 'AD', 'prevalence': 'Cleft lip/palate',
             'mechanism': 'Epithelial development', 'pdb_count': 8, 'alphafold': True},
            {'symbol': 'TGFB1', 'name': 'Transforming growth factor beta 1', 'inheritance': 'N/A', 'prevalence': 'Fibrosis, inflammation',
             'mechanism': 'Growth factor signaling', 'pdb_count': 200, 'alphafold': True},
            {'symbol': 'VEGFA', 'name': 'Vascular endothelial growth factor A', 'inheritance': 'N/A', 'prevalence': 'Angiogenesis, wound healing',
             'mechanism': 'Vascular development', 'pdb_count': 150, 'alphafold': True},
            {'symbol': 'MMP9', 'name': 'Matrix metallopeptidase 9', 'inheritance': 'N/A', 'prevalence': 'Tissue remodeling, wound healing',
             'mechanism': 'ECM degradation', 'pdb_count': 80, 'alphafold': True},
            {'symbol': 'RTN4', 'name': 'Reticulon-4 (Nogo)', 'inheritance': 'N/A', 'prevalence': 'Neuroprotection, spinal cord injury',
             'mechanism': 'Axonal growth inhibition', 'pdb_count': 15, 'alphafold': True},
            {'symbol': 'RHOA', 'name': 'Ras homolog family member A', 'inheritance': 'N/A', 'prevalence': 'Cell contractility, wound healing',
             'mechanism': 'Rho signaling', 'pdb_count': 40, 'alphafold': True},
        ]
    }
}

def get_panel(disease: str) -> Dict:
    """Get a disease panel by name."""
    return DISEASE_PANELS.get(disease)

def list_panels() -> List[str]:
    """List all available disease panels."""
    return list(DISEASE_PANELS.keys())

def get_targets_by_program(program: str) -> List[Dict]:
    """Get targets associated with a specific program/foundation."""
    targets = []
    for panel in DISEASE_PANELS.values():
        if program in panel.get('programs', []):
            targets.extend(panel['targets'])
    return targets

def get_top_targets_by_prevalence(disease: str, top_n: int = 5) -> List[Dict]:
    """Get the most prevalent targets in a disease."""
    panel = get_panel(disease)
    if not panel:
        return []
    
    # Sort by estimated prevalence (simplified)
    targets = sorted(panel['targets'], 
                    key=lambda t: (t['prevalence'].split('%')[0] if '%' in t['prevalence'] else '0'),
                    reverse=True)
    return targets[:top_n]
