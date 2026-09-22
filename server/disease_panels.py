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
        'description': ('20 targets in familial and sporadic ALS. Every pdb_count here was resolved live on '
                        '2026-09-22 against RCSB for the cited UniProt accession; the previous values were '
                        'invented and wrong in both directions (SOD1 50->156, VCP 40->144, ANG 15->56, '
                        'HNRNPA1 20->73, but ATXN2 5->1, and MATR3/STMN2/UNC13A claimed 3/2/5 structures '
                        'while RCSB holds none). ALS is an adult disease and the modality that has actually '
                        'worked is antisense, not small molecule, so each evidence record carries a '
                        '"modality" field saying whether this target suits the small-molecule docking this '
                        'platform does. A high pdb_count on an aggregation-prone RNA-binding protein '
                        'usually counts amyloid fibrils and isolated domains, not a pocket. Evidence is in '
                        'ALS_EVIDENCE and re-resolves with scripts/verify_panel_citations.py'),
        'programs': ['ALS Association', 'Project ALS', 'Augie & Rose'],
        'targets': [
            {'symbol': 'SOD1', 'name': 'Superoxide dismutase [Cu-Zn]', 'inheritance': 'AD',
             'prevalence': 'ADULT: 10-20% of familial ALS; most SOD1 carriers present as apparently sporadic disease',
             'mechanism': 'Misfolding/aggregation gain of function, not loss of dismutase activity',
             'pdb_count': 156, 'alphafold': True},
            {'symbol': 'TARDBP', 'name': 'TAR DNA-binding protein 43', 'inheritance': 'AD',
             'prevalence': 'ADULT: TARDBP mutations ~1-7% of fALS, ~1% overall; the "50% sALS" figure was '
                           'TDP-43 pathology, not TARDBP mutation',
             'mechanism': 'Nuclear TDP-43 loss de-represses cryptic exons; cytoplasmic aggregation',
             'pdb_count': 44, 'alphafold': True},
            {'symbol': 'FUS', 'name': 'RNA-binding protein FUS', 'inheritance': 'AD (often de novo)',
             'prevalence': 'ADULT and JUVENILE: ~5% of familial and ~1% of sporadic ALS; the commonest cause '
                           'of juvenile/early-onset ALS',
             'mechanism': 'Cytoplasmic mislocalisation of a prion-like RNA-binding protein; aggregation',
             'pdb_count': 23, 'alphafold': True},
            {'symbol': 'C9orf72', 'name': 'Guanine nucleotide exchange C9orf72', 'inheritance': 'AD',
             'prevalence': 'ADULT: the commonest genetic cause, 30-50% of familial and ~7% of sporadic ALS',
             'mechanism': 'GGGGCC repeat expansion: RNA foci, dipeptide repeats and haploinsufficiency',
             'pdb_count': 4, 'alphafold': True},
            {'symbol': 'TBK1', 'name': 'Serine/threonine-protein kinase TBK1', 'inheritance': 'AD (haploinsufficiency)',
             'prevalence': 'ADULT: loss-of-function variants in ~0.5% of ALS',
             'mechanism': 'Haploinsufficiency of an autophagy/innate-immune kinase; loss, not gain, of activity',
             'pdb_count': 25, 'alphafold': True},
            {'symbol': 'OPTN', 'name': 'Optineurin', 'inheritance': 'AD and AR both reported',
             'prevalence': 'ADULT: ~1% of ALS; recessive exon-5 deletion and Q398X, dominant E478G',
             'mechanism': 'Autophagy receptor; loss of NF-kB and IRF3 inhibition', 'pdb_count': 14,
             'alphafold': True},
            {'symbol': 'VCP', 'name': 'Transitional endoplasmic reticulum ATPase (p97)', 'inheritance': 'AD',
             'prevalence': 'ADULT: ~1% of familial ALS, within multisystem proteinopathy (IBM, Paget, FTD, ALS)',
             'mechanism': 'AAA+ ATPase; disease mutations increase ATPase activity and unfoldase throughput',
             'pdb_count': 144, 'alphafold': True},
            {'symbol': 'SQSTM1', 'name': 'Sequestosome-1 (p62)', 'inheritance': 'AD',
             'prevalence': 'ADULT: 1.6-2.4% of ALS, often with cognitive impairment or FTD',
             'mechanism': 'Autophagy receptor; multi-domain adapter with no catalytic site', 'pdb_count': 26,
             'alphafold': True},
            {'symbol': 'UBQLN2', 'name': 'Ubiquilin-2', 'inheritance': 'X-linked dominant',
             'prevalence': 'ADULT and JUVENILE: rare; causes X-linked ALS and ALS/dementia',
             'mechanism': 'Proteasomal shuttle factor; PXX-region mutations perturb phase separation',
             'pdb_count': 4, 'alphafold': True},
            {'symbol': 'PFN1', 'name': 'Profilin-1', 'inheritance': 'AD',
             'prevalence': 'ADULT: 7 of 274 familial ALS cases in the discovery series',
             'mechanism': 'Actin monomer binding; mutants aggregate and sequester TDP-43', 'pdb_count': 22,
             'alphafold': True},
            {'symbol': 'KIF5A', 'name': 'Kinesin heavy chain isoform 5A', 'inheritance': 'AD',
             'prevalence': 'ADULT: rare; identified by GWAS and rare-variant burden in 20,806 cases',
             'mechanism': 'ALS mutations sit in the C-terminal cargo-binding tail, not the motor domain that '
                          'causes SPG10/CMT2',
             'pdb_count': 4, 'alphafold': True},
            {'symbol': 'NEK1', 'name': 'Serine/threonine-protein kinase Nek1',
             'inheritance': 'Risk variant (loss of function), not Mendelian',
             'prevalence': 'ADULT: risk variants in nearly 3% of ALS cases',
             'mechanism': 'Loss of function affecting DNA damage response, ciliogenesis and microtubule stability',
             'pdb_count': 2, 'alphafold': True},
            {'symbol': 'ATXN2', 'name': 'Ataxin-2',
             'inheritance': 'Risk allele: intermediate polyQ expansion (27-33), not a Mendelian ALS gene',
             'prevalence': 'ADULT: intermediate repeat lengths are a common ALS susceptibility factor',
             'mechanism': 'Intermediate polyQ ataxin-2 enhances TDP-43 toxicity', 'pdb_count': 1,
             'alphafold': True},
            {'symbol': 'MATR3', 'name': 'Matrin-3', 'inheritance': 'AD; ALS attribution contested',
             'prevalence': 'ADULT: primarily distal myopathy with vocal cord weakness (VCPDM); not a common '
                           'cause of familial ALS',
             'mechanism': 'RNA-binding nuclear matrix protein; S85C causes myopathy with little motor neuron '
                          'involvement',
             'pdb_count': 0, 'alphafold': True},
            {'symbol': 'HNRNPA1', 'name': 'Heterogeneous nuclear ribonucleoprotein A1', 'inheritance': 'AD',
             'prevalence': 'ADULT: very rare; the founding report describes one familial ALS case',
             'mechanism': 'Prion-like domain mutation strengthens a steric-zipper motif and accelerates fibrils',
             'pdb_count': 73, 'alphafold': True},
            {'symbol': 'CHCHD10', 'name': 'Coiled-coil-helix-coiled-coil-helix domain-containing protein 10',
             'inheritance': 'AD',
             'prevalence': 'ADULT: rare; S59L found in 1 of 21 pathologically proven FTD-ALS families',
             'mechanism': 'Mitochondrial intermembrane-space protein; mutations cause mtDNA instability',
             'pdb_count': 5, 'alphafold': True},
            {'symbol': 'ANG', 'name': 'Angiogenin', 'inheritance': 'AD',
             'prevalence': 'ADULT: ~2.9% in one Hungarian sporadic cohort, lower elsewhere',
             'mechanism': 'Complete LOSS of ribonucleolytic and nuclear-translocation function - an inhibitor '
                          'would be the wrong direction',
             'pdb_count': 56, 'alphafold': True},
            {'symbol': 'STMN2', 'name': 'Stathmin-2', 'inheritance': 'Not a Mendelian ALS gene',
             'prevalence': 'ADULT: a downstream consequence of TDP-43 loss, not an inherited ALS cause',
             'mechanism': 'TDP-43 loss admits a cryptic exon, truncating stathmin-2 and impairing axonal '
                          'maintenance',
             'pdb_count': 0, 'alphafold': True},
            {'symbol': 'UNC13A', 'name': 'Protein unc-13 homolog A',
             'inheritance': 'GWAS risk polymorphism (rs12608932), not a Mendelian ALS gene',
             'prevalence': 'ADULT: among the strongest common-variant risk loci for ALS and FTD',
             'mechanism': 'Risk alleles potentiate a TDP-43-repressed cryptic exon, depleting UNC13A protein',
             'pdb_count': 0, 'alphafold': True},
            {'symbol': 'SIGMAR1', 'name': 'Sigma non-opioid intracellular receptor 1', 'inheritance': 'AR',
             'prevalence': 'JUVENILE: autosomal recessive juvenile ALS (ALS16); also distal hereditary motor '
                           'neuropathy',
             'mechanism': 'LOSS of sigma-1 receptor function collapses mitochondria-associated ER membranes',
             'pdb_count': 5, 'alphafold': True},
        ]
    },
    'Parkinsons': {
        'name': 'Parkinson\'s Disease',
        'description': ('18 targets. Pediatric relevance is stated in every prevalence field, because MJFF-funded '
                        'Parkinson\'s is overwhelmingly adult: the pediatric intersection is recessive juvenile and '
                        'early-onset parkinsonism plus the treatable dopamine-synthesis disorders of infancy. '
                        'Evidence for each target is in PARKINSONS_EVIDENCE and re-resolves with '
                        'scripts/verify_panel_citations.py'),
        'programs': ['Michael J. Fox Foundation', 'Parkinson\'s Foundation'],
        'targets': [
            {'symbol': 'PRKN', 'name': 'E3 ubiquitin-protein ligase parkin', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: commonest recessive early-onset PD, median onset ~30y, juvenile cases reported',
             'mechanism': 'E3 ubiquitin ligase, mitophagy', 'pdb_count': 21, 'alphafold': True},
            {'symbol': 'PINK1', 'name': 'Serine/threonine-protein kinase PINK1, mitochondrial', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: recessive early-onset PD, rarer than PRKN (1 of 136 UK EOPD probands)',
             'mechanism': 'Mitophagy, mitochondrial quality control', 'pdb_count': 6, 'alphafold': True},
            {'symbol': 'PARK7', 'name': 'Parkinson disease protein 7 (DJ-1)', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: rarest of the three classical recessive early-onset PD genes',
             'mechanism': 'Oxidative stress response, redox-sensitive chaperone', 'pdb_count': 88, 'alphafold': True},
            {'symbol': 'ATP13A2', 'name': 'Polyamine-transporting ATPase 13A2', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: Kufor-Rakeb syndrome, juvenile-onset parkinsonism with gaze palsy',
             'mechanism': 'Lysosomal polyamine transport and ion homeostasis', 'pdb_count': 25, 'alphafold': True},
            {'symbol': 'DNAJC6', 'name': 'Auxilin', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: juvenile parkinsonism-dystonia, onset before 21y, delay from infancy',
             'mechanism': 'Clathrin uncoating co-chaperone, synaptic vesicle recycling', 'pdb_count': 0,
             'alphafold': True},
            {'symbol': 'SYNJ1', 'name': 'Polyphosphatidylinositol phosphatase synaptojanin-1', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: PARK20, early-onset atypical parkinsonism (Arg258Gln families)',
             'mechanism': 'Synaptic phosphoinositide phosphatase, endosomal trafficking', 'pdb_count': 5,
             'alphafold': True},
            {'symbol': 'FBXO7', 'name': 'F-box only protein 7', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: PARK15 parkinsonian-pyramidal disease, juvenile onset with spasticity',
             'mechanism': 'SCF E3 ligase substrate receptor, proteasome and mitophagy regulation', 'pdb_count': 2,
             'alphafold': True},
            {'symbol': 'TH', 'name': 'Tyrosine 3-monooxygenase (tyrosine hydroxylase)', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: TH deficiency, hypokinetic-rigid parkinsonism from 3-6 months of age',
             'mechanism': 'Rate-limiting step of dopamine synthesis', 'pdb_count': 7, 'alphafold': True},
            {'symbol': 'DDC', 'name': 'Aromatic-L-amino-acid decarboxylase (AADC)', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: AADC deficiency in infancy; approved gene therapy in children',
             'mechanism': 'PLP-dependent decarboxylation of L-dopa to dopamine', 'pdb_count': 8, 'alphafold': True},
            {'symbol': 'GCH1', 'name': 'GTP cyclohydrolase 1',
             'inheritance': 'AD (Segawa dopa-responsive dystonia); AR (BH4 deficiency)',
             'prevalence': 'PEDIATRIC: childhood-onset dopa-responsive dystonia with diurnal fluctuation',
             'mechanism': 'Rate-limiting step of tetrahydrobiopterin synthesis, the TH cofactor', 'pdb_count': 11,
             'alphafold': True},
            {'symbol': 'SLC6A3', 'name': 'Sodium-dependent dopamine transporter (DAT)', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: dopamine transporter deficiency syndrome, infantile parkinsonism-dystonia',
             'mechanism': 'Presynaptic dopamine reuptake; loss of function causes misfolding and surface loss',
             'pdb_count': 17, 'alphafold': True},
            {'symbol': 'GBA1', 'name': 'Lysosomal acid glucosylceramidase',
             'inheritance': 'AR (Gaucher disease); heterozygous carriage is an adult PD risk factor',
             'prevalence': 'PEDIATRIC AS GAUCHER ONLY: neuronopathic GD types 2/3 in children; PD risk is adult',
             'mechanism': 'Lysosomal glucosylceramide hydrolysis; loss drives alpha-synuclein accumulation',
             'pdb_count': 58, 'alphafold': True},
            {'symbol': 'SNCA', 'name': 'Alpha-synuclein', 'inheritance': 'AD (missense and locus multiplication)',
             'prevalence': 'ADULT-ONSET, NOT PEDIATRIC: rare dominant PD, median onset ~49y for SNCA/LRRK2/VPS35',
             'mechanism': 'Protein aggregation, neuroinflammation', 'pdb_count': 249, 'alphafold': True},
            {'symbol': 'LRRK2', 'name': 'Leucine-rich repeat serine/threonine-protein kinase 2', 'inheritance': 'AD',
             'prevalence': 'ADULT-ONSET, NOT PEDIATRIC: G2019S is the commonest known cause of familial and sporadic PD',
             'mechanism': 'Kinase signalling, lysosomal and mitochondrial dysfunction', 'pdb_count': 58,
             'alphafold': True},
            {'symbol': 'VPS35', 'name': 'Vacuolar protein sorting-associated protein 35', 'inheritance': 'AD',
             'prevalence': 'ADULT-ONSET, NOT PEDIATRIC: rare dominant PD (D620N)',
             'mechanism': 'Retromer function, endosomal sorting', 'pdb_count': 14, 'alphafold': True},
            {'symbol': 'MAOB', 'name': 'Amine oxidase [flavin-containing] B',
             'inheritance': 'N/A - not a Mendelian PD gene (X-chromosome locus)',
             'prevalence': 'ADULT SYMPTOMATIC DRUG TARGET, NOT PEDIATRIC: selegiline/rasagiline/safinamide',
             'mechanism': 'Dopamine catabolism, ROS generation', 'pdb_count': 57, 'alphafold': True},
            {'symbol': 'COMT', 'name': 'Catechol O-methyltransferase', 'inheritance': 'N/A - drug target',
             'prevalence': 'ADULT SYMPTOMATIC DRUG TARGET, NOT PEDIATRIC: levodopa add-on for motor fluctuations',
             'mechanism': 'Peripheral L-dopa and dopamine O-methylation', 'pdb_count': 12, 'alphafold': True},
            {'symbol': 'DRD2', 'name': 'Dopamine receptor D2', 'inheritance': 'N/A - drug target',
             'prevalence': 'ADULT SYMPTOMATIC DRUG TARGET, NOT PEDIATRIC: dopamine agonists in early and advanced PD',
             'mechanism': 'Postsynaptic dopamine signalling', 'pdb_count': 11, 'alphafold': True},
        ]
    },
    'Shriners': {
        'name': 'Shriners Children\'s Research',
        'description': ('15 targets inside the pediatric orthopaedic and cleft scope: osteogenesis imperfecta, '
                        'skeletal dysplasia, metabolic bone disease, heterotopic ossification, hereditary '
                        'osteochondromas, cleft lip and palate. Every target is pediatric. No verified molecular '
                        'target is carried for burns/scar or spinal cord injury - the previous TGFB1, VEGFA, MMP9, '
                        'RHOA and RTN4 entries had no pediatric, Shriners-scope evidence and were removed rather '
                        'than restated. Evidence is in SHRINERS_EVIDENCE and re-resolves with '
                        'scripts/verify_panel_citations.py'),
        'programs': ['Shriners Children\'s'],
        'targets': [
            {'symbol': 'COL1A1', 'name': 'Collagen alpha-1(I) chain', 'inheritance': 'AD',
             'prevalence': 'PEDIATRIC: classical dominant OI, fractures from infancy; 1200 pathogenic ClinVar records',
             'mechanism': 'Type I collagen alpha-1 chain; not directly druggable, therapy acts on bone turnover',
             'pdb_count': 14, 'alphafold': True},
            {'symbol': 'COL1A2', 'name': 'Collagen alpha-2(I) chain', 'inheritance': 'AD',
             'prevalence': 'PEDIATRIC: classical dominant OI; 536 pathogenic ClinVar records',
             'mechanism': 'Type I collagen alpha-2 chain; no chemical matter (0 potent ligands)', 'pdb_count': 5,
             'alphafold': True},
            {'symbol': 'SERPINF1', 'name': 'Pigment epithelium-derived factor (PEDF)', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: OI type VI, recessive, bisphosphonate-resistant mineralisation defect',
             'mechanism': 'Secreted serpin required for bone mineralisation', 'pdb_count': 3, 'alphafold': True},
            {'symbol': 'CRTAP', 'name': 'Cartilage-associated protein', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: severe recessive OI presenting perinatally',
             'mechanism': 'CRTAP/P3H1/PPIB collagen prolyl 3-hydroxylation complex; no chemical matter',
             'pdb_count': 6, 'alphafold': True},
            {'symbol': 'P3H1', 'name': 'Prolyl 3-hydroxylase 1', 'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: severe recessive OI; the enzyme of the 3-hydroxylation complex',
             'mechanism': '2-oxoglutarate-dependent collagen prolyl 3-hydroxylase', 'pdb_count': 6, 'alphafold': True},
            {'symbol': 'SOST', 'name': 'Sclerostin', 'inheritance': 'AR (sclerosteosis, loss of function)',
             'prevalence': 'PEDIATRIC: lead pharmacological target in OI; setrusumab and romosozumab in pediatric Ph3',
             'mechanism': 'Osteocyte-secreted Wnt antagonist; inhibition increases bone formation', 'pdb_count': 3,
             'alphafold': True},
            {'symbol': 'TNFSF11', 'name': 'TNF ligand superfamily member 11 (RANKL)',
             'inheritance': 'N/A - drug target',
             'prevalence': 'PEDIATRIC: denosumab used in children with OI, with rebound hypercalcaemia as the risk',
             'mechanism': 'Osteoclast differentiation and survival', 'pdb_count': 2, 'alphafold': True},
            {'symbol': 'FGFR3', 'name': 'Fibroblast growth factor receptor 3', 'inheritance': 'AD (gain of function)',
             'prevalence': 'PEDIATRIC: achondroplasia (G380R), birth prevalence 1 in 20000-30000',
             'mechanism': 'Constitutive growth-plate signalling suppresses chondrocyte proliferation',
             'pdb_count': 16, 'alphafold': True},
            {'symbol': 'NPR2', 'name': 'Atrial natriuretic peptide receptor 2 (NPR-B)',
             'inheritance': 'AR (acromesomelic dysplasia Maroteaux type); heterozygotes short stature',
             'prevalence': 'PEDIATRIC: receptor for vosoritide, established in children with achondroplasia',
             'mechanism': 'CNP receptor; cGMP signalling antagonises FGFR3 in the growth plate', 'pdb_count': 0,
             'alphafold': True},
            {'symbol': 'ALPL', 'name': 'Alkaline phosphatase, tissue-nonspecific isozyme',
             'inheritance': 'AR in perinatal/infantile hypophosphatasia; AD in milder childhood and adult forms',
             'prevalence': 'PEDIATRIC: hypophosphatasia; enzyme replacement established in infants and children',
             'mechanism': 'Cell-surface phosphohydrolase; loss leaves pyrophosphate blocking mineralisation',
             'pdb_count': 5, 'alphafold': True},
            {'symbol': 'FGF23', 'name': 'Fibroblast growth factor 23',
             'inheritance': 'AD gain-of-function in ADHR; in XLH it is elevated secondary to PHEX loss, not mutated',
             'prevalence': 'PEDIATRIC: burosumab beat conventional therapy in children aged 1-12 with XLH',
             'mechanism': 'Phosphaturic hormone; excess causes renal phosphate wasting and rickets', 'pdb_count': 6,
             'alphafold': True},
            {'symbol': 'PHEX', 'name': 'Phosphate-regulating neutral endopeptidase PHEX', 'inheritance': 'XD',
             'prevalence': 'PEDIATRIC: X-linked hypophosphataemia, the commonest inherited rickets',
             'mechanism': 'Endopeptidase whose loss raises FGF23; no structure and no chemical matter of its own',
             'pdb_count': 0, 'alphafold': True},
            {'symbol': 'ACVR1', 'name': 'Activin receptor type-1 (ALK2)', 'inheritance': 'AD (recurrent R206H)',
             'prevalence': 'PEDIATRIC: fibrodysplasia ossificans progressiva, flare-ups from the first decade',
             'mechanism': 'Mutant ALK2 responds to activin A, driving BMP signalling and heterotopic bone',
             'pdb_count': 85, 'alphafold': True},
            {'symbol': 'EXT1', 'name': 'Exostosin-1', 'inheritance': 'AD',
             'prevalence': 'PEDIATRIC: hereditary multiple osteochondromas, prevalence ~1:50,000',
             'mechanism': 'Heparan sulfate co-polymerase; loss deregulates growth-plate chondrocytes',
             'pdb_count': 6, 'alphafold': True},
            {'symbol': 'IRF6', 'name': 'Interferon regulatory factor 6', 'inheritance': 'AD',
             'prevalence': 'PEDIATRIC: Van der Woude syndrome, commonest syndromic cleft lip/palate',
             'mechanism': 'Transcription factor for periderm and palatal epithelium; no tractable chemistry today',
             'pdb_count': 0, 'alphafold': True},
        ]
    },
    'StJude': {
        'name': 'St. Jude Pediatric Oncology',
        'description': '15 targets for the childhood cancers St. Jude treats; every identifier cited for '
                       'them is re-resolvable with scripts/verify_panel_citations.py',
        'programs': ['St. Jude Children\'s Research Hospital'],
        'targets': [
            # --- leukaemia -------------------------------------------------------------------
            {'symbol': 'MEN1', 'name': 'Menin', 'inheritance': 'Somatic (fusion-driven dependency)',
             'prevalence': 'KMT2A rearranged in 70-80% of infant acute leukaemia',
             'mechanism': 'Menin-KMT2A scaffold; druggable surrogate for an undruggable fusion',
             'pdb_count': 69, 'alphafold': True},
            {'symbol': 'FLT3', 'name': 'Receptor-type tyrosine-protein kinase FLT3', 'inheritance': 'Somatic',
             'prevalence': 'FLT3-ITD in 15.4% of childhood AML (91-patient series)',
             'mechanism': 'Constitutive receptor tyrosine kinase signalling',
             'pdb_count': 11, 'alphafold': True},
            {'symbol': 'JAK2', 'name': 'Tyrosine-protein kinase JAK2', 'inheritance': 'Somatic',
             'prevalence': 'Ph-like B-ALL is 10-15% of childhood ALL; JAK2/EPOR rearrangements 8.8% of high-risk B-ALL',
             'mechanism': 'Cytokine-receptor (CRLF2/EPOR) driven JAK-STAT activation',
             'pdb_count': 171, 'alphafold': True},
            # --- neuroblastoma ---------------------------------------------------------------
            {'symbol': 'ALK', 'name': 'ALK tyrosine kinase receptor', 'inheritance': 'Somatic; germline in familial cases',
             'prevalence': '10.5% of neuroblastoma at diagnosis; 21.5% of high-risk tumours',
             'mechanism': 'Activating kinase-domain mutation or amplification',
             'pdb_count': 80, 'alphafold': True},
            {'symbol': 'MYCN', 'name': 'N-myc proto-oncogene protein', 'inheritance': 'Somatic amplification',
             'prevalence': '18.1% of neuroblastoma (COG cohort, n=4672)',
             'mechanism': 'Amplified transcription factor; undruggable - no enzymatic site, intrinsically disordered',
             'pdb_count': 2, 'alphafold': True},
            {'symbol': 'AURKA', 'name': 'Aurora kinase A', 'inheritance': 'N/A (acquired dependency)',
             'prevalence': 'Dependency of MYCN-amplified neuroblastoma (18.1% of cases)',
             'mechanism': 'Binds and stabilises N-Myc; inhibitors destabilise the complex',
             'pdb_count': 202, 'alphafold': True},
            # --- CNS tumours -----------------------------------------------------------------
            {'symbol': 'SMO', 'name': 'Protein smoothened', 'inheritance': 'Somatic',
             'prevalence': 'SHH subgroup is ~25% of medulloblastoma',
             'mechanism': 'Hedgehog signal transducer; pediatric use limited by growth-plate fusion',
             'pdb_count': 15, 'alphafold': True},
            {'symbol': 'BRAF', 'name': 'Serine/threonine-protein kinase B-raf', 'inheritance': 'Somatic',
             'prevalence': 'KIAA1549-BRAF fusion 45% and V600E 7% of pediatric low-grade glioma',
             'mechanism': 'MAPK activation by fusion or V600E substitution',
             'pdb_count': 135, 'alphafold': True},
            {'symbol': 'ACVR1', 'name': 'Activin receptor type-1 (ALK2)', 'inheritance': 'Somatic',
             'prevalence': '25% of diffuse intrinsic pontine glioma',
             'mechanism': 'Gain-of-function serine/threonine kinase; no pediatric trial of an ALK2 inhibitor yet',
             'pdb_count': 85, 'alphafold': True},
            {'symbol': 'H3-3A', 'name': 'Histone H3.3 (K27M oncohistone)', 'inheritance': 'Somatic',
             'prevalence': 'H3 K27M in up to 80% of pediatric diffuse midline glioma',
             'mechanism': 'Oncohistone poisoning PRC2; undruggable - the lesion is a histone substitution',
             'pdb_count': 104, 'alphafold': True},
            {'symbol': 'EZH2', 'name': 'Histone-lysine N-methyltransferase EZH2', 'inheritance': 'N/A (synthetic dependency)',
             'prevalence': 'SMARCB1/INI1 biallelic loss in ~70% of primary rhabdoid tumours (AT/RT)',
             'mechanism': 'PRC2 catalytic subunit; dependency created by SMARCB1 loss',
             'pdb_count': 41, 'alphafold': True},
            # --- extracranial solid tumours ----------------------------------------------------
            {'symbol': 'FLI1', 'name': 'FLI1, as the EWSR1::FLI1 fusion', 'inheritance': 'Somatic fusion',
             'prevalence': '85% of Ewing sarcoma',
             'mechanism': 'Chimeric transcription factor; undruggable - no pocket, TK216 acts on microtubules',
             'pdb_count': 14, 'alphafold': True},
            {'symbol': 'PAX3', 'name': 'PAX3, as the PAX3::FOXO1 fusion', 'inheritance': 'Somatic fusion',
             'prevalence': 'PAX3::FOXO1 in 52% of alveolar rhabdomyosarcoma',
             'mechanism': 'Chimeric transcription factor; undruggable - no ChEMBL target, one PDB entry',
             'pdb_count': 1, 'alphafold': True},
            {'symbol': 'CTNNB1', 'name': 'Catenin beta-1', 'inheritance': 'Somatic',
             'prevalence': 'CTNNB1 mutation in 75% of hepatoblastoma',
             'mechanism': 'Wnt effector; undruggable protein-protein interface, no annotated drug',
             'pdb_count': 50, 'alphafold': True},
            {'symbol': 'RB1', 'name': 'Retinoblastoma-associated protein', 'inheritance': 'AD germline plus somatic second hit',
             'prevalence': 'Germline RB1 loss in all bilateral retinoblastoma; MYCN-amplified RB1-proficient 1.5%',
             'mechanism': 'Tumour-suppressor loss; undruggable by inhibition - nothing to inhibit',
             'pdb_count': 19, 'alphafold': True},
        ]
    }
}

# Evidence behind every StJude target. Each identifier was resolved against the live service on
# 2026-09-22 and is re-resolvable by scripts/verify_panel_citations.py, which fails on any
# identifier that does not resolve, any quote no longer present in its abstract, any drug whose
# ChEMBL mechanism no longer points at the target, any trial that does not enrol children, and any
# structure or ligand count the panel overstates.
#
# Fields:
#   uniprot / pdb_ids / alphafold_model  - protein identity and structural tractability
#   chembl_target / potent_ligands       - chemical matter (activities with pChEMBL >= 6);
#                                          chembl_target None asserts ChEMBL has no such target
#   drugs                                - ChEMBL molecules whose curated mechanism hits this target
#   trials                               - ClinicalTrials.gov studies that enrol children
#   claims                               - a PMID plus a verbatim phrase from its abstract
#   tractability / unmet_need / caveat   - the judgement, stated so it can be argued with
STJUDE_EVIDENCE = {
    'MEN1': {
        'indication': 'KMT2A-rearranged infant ALL and AML',
        'uniprot': 'O00255', 'pdb_ids': ['9WKU', '9WKV', '9WKW'], 'alphafold_model': 'AF-O00255-F1',
        'chembl_target': 'CHEMBL1615381', 'potent_ligands': 499,
        'drugs': [{'chembl_id': 'CHEMBL6068395', 'name': 'revumenib'}],
        'trials': [{'nct_id': 'NCT04065399', 'note': 'AUGMENT-101 phase 1/2, enrols from 30 days of age'},
                   {'nct_id': 'NCT05761171', 'note': 'phase 2, children only, revumenib plus chemotherapy'}],
        'claims': [{'pmid': '7885037', 'quote': 'high frequency (70-80%) of ALL-1'},
                   {'pmid': '37099340', 'quote': '3-year event-free survival below 40%'},
                   {'pmid': '39121437', 'quote': 'CR + CRh rate was 22.8%'},
                   {'pmid': '40441466', 'quote': 'leading to FDA approval in November 2024'}],
        'tractability': 'tractable',
        'unmet_need': 'moderate - revumenib is approved for KMT2A-rearranged acute leukaemia, but '
                      'remission rates are partial and infants remain the worst-outcome group in ALL',
        'caveat': 'the driver (the KMT2A fusion) is itself undruggable; menin is the druggable '
                  'cofactor it depends on',
    },
    'FLT3': {
        'indication': 'Pediatric acute myeloid leukaemia',
        'uniprot': 'P36888', 'pdb_ids': ['8XB1', '7ZV9', '7QDP'], 'alphafold_model': 'AF-P36888-F1',
        'chembl_target': 'CHEMBL1974', 'potent_ligands': 5282,
        'drugs': [{'chembl_id': 'CHEMBL3301622', 'name': 'gilteritinib'}],
        'trials': [{'nct_id': 'NCT04240002', 'note': 'gilteritinib plus chemotherapy in children; terminated'},
                   {'nct_id': 'NCT04293562', 'note': 'COG AAML1831 phase 3 with a gilteritinib arm, from 6 months'}],
        'claims': [{'pmid': '12750701', 'quote': '(14 of 91 patients, 15.4%)'}],
        'tractability': 'tractable',
        'unmet_need': 'low-to-moderate - chemically crowded; no FLT3 inhibitor is approved for '
                      'children, but several are in pediatric trials',
        'caveat': 'the 15.4% figure is one 91-patient series; other pediatric cohorts report ~10%',
    },
    'JAK2': {
        'indication': 'Philadelphia-chromosome-like B-cell ALL',
        'uniprot': 'O60674', 'pdb_ids': ['29RX', '29RY', '9T1U'], 'alphafold_model': 'AF-O60674-F1',
        'chembl_target': 'CHEMBL2971', 'potent_ligands': 15662,
        'drugs': [{'chembl_id': 'CHEMBL1795071', 'name': 'ruxolitinib'}],
        'trials': [{'nct_id': 'NCT02723994', 'note': 'COG AALL1521 phase 2, ruxolitinib plus chemotherapy in children'}],
        'claims': [{'pmid': '29050694', 'quote': 'ranging from 10-15% of children'},
                   {'pmid': '28408464', 'quote': 'EPOR rearrangements or JAK2 fusions in 8.8%'}],
        'tractability': 'tractable',
        'unmet_need': 'moderate - JAK inhibitors are approved for myelofibrosis, not for Ph-like ALL, '
                      'and single-agent activity in ALL has been limited',
        'caveat': 'children carry JAK2 fusions rather than the JAK2 V617F that ruxolitinib was built '
                  'against; fusion-specific pharmacology is not established',
    },
    'ALK': {
        'indication': 'High-risk neuroblastoma',
        'uniprot': 'Q9UM73', 'pdb_ids': ['9XZG', '9G5I', '9GBE'], 'alphafold_model': 'AF-Q9UM73-F1',
        'chembl_target': 'CHEMBL4247', 'potent_ligands': 3525,
        'drugs': [{'chembl_id': 'CHEMBL3286830', 'name': 'lorlatinib'},
                  {'chembl_id': 'CHEMBL601719', 'name': 'crizotinib'}],
        'trials': [{'nct_id': 'NCT03126916', 'note': 'COG ANBL1531 phase 3 with a lorlatinib arm, from 365 days'},
                   {'nct_id': 'NCT00939770', 'note': 'COG phase 1/2 crizotinib in children'}],
        'claims': [{'pmid': '36807339', 'quote': 'ALK point mutations occurred in 10.5% of all cases'},
                   {'pmid': '40036726', 'quote': 'ALK-activating mutations occurred in 21.5% of tumors'},
                   {'pmid': '37012551', 'quote': 'for <18 years was 30%'}],
        'tractability': 'tractable',
        'unmet_need': 'high - no ALK inhibitor is approved for neuroblastoma; single-agent lorlatinib '
                      'response in children was 30% and resistance emerges through RAS-MAPK',
        'caveat': 'neuroblastoma carries ALK point mutations, not the EML4-ALK fusion these drugs '
                  'were optimised against; R1275Q and F1174L differ in inhibitor sensitivity',
    },
    'MYCN': {
        'indication': 'MYCN-amplified neuroblastoma',
        'uniprot': 'P04198', 'pdb_ids': ['7ZTL', '5G1X'], 'alphafold_model': 'AF-P04198-F1',
        'chembl_target': 'CHEMBL4523165', 'potent_ligands': 0,
        'drugs': [],
        'trials': [],
        'claims': [{'pmid': '28696504', 'quote': '845 (18.1%) had MNA'},
                   {'pmid': '42233780', 'quote': 'lack of enzymatic activity and intrinsically disordered nature'}],
        'tractability': 'undruggable by direct inhibition',
        'unmet_need': 'very high - the dominant driver of high-risk neuroblastoma, with no direct '
                      'chemical matter at all',
        'caveat': 'ChEMBL holds zero activities at pChEMBL >= 6 for this target and both PDB entries '
                  'are complexes with partner proteins, not ligandable MYCN; route in through AURKA',
    },
    'AURKA': {
        'indication': 'MYCN-amplified neuroblastoma (indirect route to MYCN)',
        'uniprot': 'O14965', 'pdb_ids': ['9RVK', '9S0K', '9S0W'], 'alphafold_model': 'AF-O14965-F1',
        'chembl_target': 'CHEMBL4722', 'potent_ligands': 3340,
        'drugs': [{'chembl_id': 'CHEMBL483158', 'name': 'alisertib'}],
        'trials': [{'nct_id': 'NCT01601535', 'note': 'alisertib with irinotecan/temozolomide, phase 1/2, from 12 months'},
                   {'nct_id': 'NCT01154816', 'note': 'COG phase 2 alisertib in children'}],
        'claims': [{'pmid': '27837025', 'quote': 'is stabilized in neuroblastoma by the protein kinase Aurora-A'},
                   {'pmid': '34884931', 'quote': 'prevents N-Myc degradation by directly binding'}],
        'tractability': 'tractable',
        'unmet_need': 'high - alisertib was never approved, and conformation-selective, '
                      'N-Myc-destabilising chemistry is still open',
        'caveat': 'kinase inhibition alone is not the wanted mechanism; the useful compounds are '
                  'those forcing an Aurora-A conformation incompatible with N-Myc binding',
    },
    'SMO': {
        'indication': 'SHH-subgroup medulloblastoma',
        'uniprot': 'Q99835', 'pdb_ids': ['7ZI0', '6XBJ', '6XBK'], 'alphafold_model': 'AF-Q99835-F1',
        'chembl_target': 'CHEMBL5971', 'potent_ligands': 764,
        'drugs': [{'chembl_id': 'CHEMBL473417', 'name': 'vismodegib'},
                  {'chembl_id': 'CHEMBL3137317', 'name': 'sonidegib'}],
        'trials': [{'nct_id': 'NCT01239316', 'note': 'phase 2 vismodegib in children with recurrent medulloblastoma'},
                   {'nct_id': 'NCT01125800', 'note': 'phase 1/2 sonidegib (LDE225) in children'}],
        'claims': [{'pmid': '32112900', 'quote': 'accounts for approximately 25% of the cases'},
                   {'pmid': '29050204', 'quote': 'developed widespread growth plate fusions'}],
        'tractability': 'tractable but pediatric-toxicity-limited',
        'unmet_need': 'moderate - two SMO inhibitors are approved, but irreversible growth-plate '
                      'fusion makes them unusable in growing children',
        'caveat': 'the open problem is not potency but a molecule or route that spares the growth '
                  'plate; a skeletally sparing SMO ligand, or a node downstream of SMO',
    },
    'BRAF': {
        'indication': 'Pediatric low-grade glioma',
        'uniprot': 'P15056', 'pdb_ids': ['9TWB', '9RTQ', '9RTR'], 'alphafold_model': 'AF-P15056-F1',
        'chembl_target': 'CHEMBL5145', 'potent_ligands': 8619,
        'drugs': [{'chembl_id': 'CHEMBL3348923', 'name': 'tovorafenib'},
                  {'chembl_id': 'CHEMBL2105729', 'name': 'dabrafenib'}],
        'trials': [{'nct_id': 'NCT05566795', 'note': 'FIREFLY-2 phase 3 tovorafenib versus chemotherapy in children'},
                   {'nct_id': 'NCT04775485', 'note': 'FIREFLY-1 phase 2 tovorafenib in children and young adults'}],
        'claims': [{'pmid': '24532263', 'quote': 'KIAA1549-BRAF fusion transcript in 45 % of the samples'},
                   {'pmid': '24532263', 'quote': 'BRAF V600E and BRAFins598T mutations were detected in 7 and 1 %'}],
        'tractability': 'tractable',
        'unmet_need': 'low - the most crowded target on this panel; type II RAF inhibitors are '
                      'already in pediatric use',
        'caveat': 'type I (V600E-selective) inhibitors paradoxically activate MAPK in fusion-driven '
                  'tumours, so fusion and point-mutant disease need different chemistry',
    },
    'ACVR1': {
        'indication': 'Diffuse intrinsic pontine glioma / diffuse midline glioma',
        'uniprot': 'Q04771', 'pdb_ids': ['9RDA', '9N4K', '9L04'], 'alphafold_model': 'AF-Q04771-F1',
        'chembl_target': 'CHEMBL5903', 'potent_ligands': 1627,
        'drugs': [{'chembl_id': 'CHEMBL6068336', 'name': 'momelotinib'}],
        'trials': [],
        'claims': [{'pmid': '26374787', 'quote': 'ACVR1 mutations in 25% of diffuse intrinsic pontine gliomas'},
                   {'pmid': '31098401', 'quote': 'preclinical efficacy of two distinct chemotypes of ALK2 inhibitor'}],
        'tractability': 'tractable',
        'unmet_need': 'highest on this panel - a kinase with 85 PDB entries and 1627 potent ChEMBL '
                      'ligands drives a uniformly fatal tumour, and a CT.gov search for an ALK2 '
                      'inhibitor in DIPG returns zero studies',
        'caveat': 'momelotinib is ChEMBL-annotated as an ACVR1 inhibitor and approved for '
                  'myelofibrosis, not for glioma; brain penetration and ALK2 selectivity are the '
                  'unsolved problems and the brain-penetrant tools (LDN-193189, LDN-214117) are '
                  'preclinical only',
    },
    'H3-3A': {
        'indication': 'H3 K27M-altered diffuse midline glioma',
        'uniprot': 'P84243', 'pdb_ids': ['43IF', '9UXW', '9UZ9'], 'alphafold_model': 'AF-P84243-F1',
        'chembl_target': 'CHEMBL5724667', 'potent_ligands': 0,
        'drugs': [],
        'trials': [{'nct_id': 'NCT03416530', 'note': 'ONC201 (dordaviprone) in pediatric H3 K27M glioma; the drug '
                                                     'does not bind histone H3'}],
        'claims': [{'pmid': '30647848', 'quote': 'Up to 80% of pediatric diffuse midline gliomas harbor a histone H3 mutation'},
                   {'pmid': '26374787', 'quote': 'K27M H3.3/H3.1 mutations in 80%'}],
        'tractability': 'undruggable',
        'unmet_need': 'very high, but not addressable at this node',
        'caveat': 'the lesion is a single substitution in a histone that poisons PRC2; ChEMBL holds '
                  'no potent ligand and there is nothing to occupy. Work the consequences (PRC2, '
                  'ACVR1, ClpP) rather than the histone',
    },
    'EZH2': {
        'indication': 'Atypical teratoid/rhabdoid tumour and other SMARCB1-deficient tumours',
        'uniprot': 'Q15910', 'pdb_ids': ['9KOF', '9KOG', '9KOH'], 'alphafold_model': 'AF-Q15910-F1',
        'chembl_target': 'CHEMBL2189110', 'potent_ligands': 1976,
        'drugs': [{'chembl_id': 'CHEMBL4594260', 'name': 'tazemetostat'}],
        'trials': [{'nct_id': 'NCT02601937', 'note': 'phase 1 tazemetostat, children only, INI1-negative tumours'},
                   {'nct_id': 'NCT03213665', 'note': 'NCI-COG phase 2 tazemetostat in relapsed solid tumours'}],
        'claims': [{'pmid': '16459991', 'quote': 'is observed in approximately 70% of primary tumors'},
                   {'pmid': '37541451', 'quote': 'aberrant EZH2 expression and/or activity emerged as a druggable vulnerability'}],
        'tractability': 'tractable',
        'unmet_need': 'high - tazemetostat is approved for epithelioid sarcoma, not for AT/RT, and '
                      'responses in rhabdoid tumours have been variable',
        'caveat': 'the 70% SMARCB1 figure is from a 2006 review and modern series place biallelic '
                  'inactivation higher; EZH2 is a dependency created by SMARCB1 loss, not a mutated '
                  'driver',
    },
    'FLI1': {
        'indication': 'Ewing sarcoma (EWSR1::FLI1)',
        'uniprot': 'Q01543', 'pdb_ids': ['9CP6', '9MWY', '9MX8'], 'alphafold_model': 'AF-Q01543-F1',
        'chembl_target': 'CHEMBL5465299', 'potent_ligands': 0,
        'drugs': [],
        'trials': [{'nct_id': 'NCT02657005', 'note': 'TK216, developed as a direct EWSR1::FLI1 inhibitor; terminated'}],
        'claims': [{'pmid': '29977059', 'quote': 'the most common fusion being EWSR1-FLI1 (85% of cases)'},
                   {'pmid': '35803262', 'quote': 'TK216 acts as an MT destabilizing agent'}],
        'tractability': 'undruggable by direct inhibition',
        'unmet_need': 'very high - the defining lesion of Ewing sarcoma, with no validated direct '
                      'chemical matter',
        'caveat': 'the one clinical compound advertised as a direct inhibitor, TK216, was shown to '
                  'destabilise microtubules instead; ChEMBL holds zero potent FLI1 ligands. Do not '
                  'plan a screening campaign here without new biology',
    },
    'PAX3': {
        'indication': 'Fusion-positive alveolar rhabdomyosarcoma (PAX3::FOXO1)',
        'uniprot': 'P23760', 'pdb_ids': ['3CMY'], 'alphafold_model': 'AF-P23760-F1',
        'chembl_target': None, 'potent_ligands': 0,
        'drugs': [],
        'trials': [{'nct_id': 'NCT01626170', 'note': 'correlative biology study in fusion-positive RMS, not a '
                                                     'therapeutic trial of a PAX3::FOXO1 agent'}],
        'claims': [{'pmid': '22089931', 'quote': 'Fifty-two percent of the samples exhibited a PAX3-FOXO1 fusion'},
                   {'pmid': '39781573', 'quote': 'specific fusion was found in 330 (90%)'}],
        'tractability': 'undruggable',
        'unmet_need': 'very high - fusion-positive alveolar RMS has the worst outcome in the disease '
                      'and no targeted option',
        'caveat': 'ChEMBL has no single-protein target for P23760 at all and the PDB has one entry; '
                  'this is the least tractable node on the panel, listed for honesty rather than as '
                  'a place to start',
    },
    'CTNNB1': {
        'indication': 'Hepatoblastoma (and WNT-subgroup medulloblastoma)',
        'uniprot': 'P35222', 'pdb_ids': ['9I8K', '9I8W', '9I8X'], 'alphafold_model': 'AF-P35222-F1',
        'chembl_target': 'CHEMBL5866', 'potent_ligands': 92,
        'drugs': [],
        'trials': [],
        'claims': [{'pmid': '11666046', 'quote': 'Twelve tumours (75%) revealed pathogenic BCM'},
                   {'pmid': '39643250', 'quote': 'due to challenges such as the lack of crystal structures'}],
        'tractability': 'undruggable at present (protein-protein interface)',
        'unmet_need': 'moderate - most children with hepatoblastoma are cured by chemotherapy and '
                      'surgery, so the need is the refractory minority',
        'caveat': 'ChEMBL holds 92 potent activities but not one mechanism-annotated drug, and a '
                  'CT.gov search for a beta-catenin agent in hepatoblastoma returns zero studies',
    },
    'RB1': {
        'indication': 'Retinoblastoma',
        'uniprot': 'P06400', 'pdb_ids': ['9DGK', '9DHC', '9DHF'], 'alphafold_model': 'AF-P06400-F1',
        'chembl_target': 'CHEMBL5288', 'potent_ligands': 6,
        'drugs': [],
        'trials': [],
        'claims': [{'pmid': '32139107', 'quote': 'Germline mutation or deletion of the RB1 gene was identified in all children with bilateral retinoblastoma'},
                   {'pmid': '36245757', 'quote': '1.5% of tumors demonstrate high-level amplification'}],
        'tractability': 'not a small-molecule target',
        'unmet_need': 'high for metastatic disease, but the need is a synthetic-lethal partner, not '
                      'an RB1 ligand',
        'caveat': 'RB1 is lost, not activated - there is nothing to inhibit. It is on the panel '
                  'because a pediatric oncology panel that silently omitted retinoblastoma would be '
                  'misleading',
    },
}


def get_target_evidence(symbol: str) -> Dict:
    """Evidence record for a StJude panel target, or None."""
    return STJUDE_EVIDENCE.get(symbol)


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


# Evidence behind every Parkinsons and Shriners target, in the same form as STJUDE_EVIDENCE, so that
# scripts/verify_panel_citations.py re-resolves all of it: UniProt, PDB, AlphaFold, ChEMBL target and
# ligand counts, ChEMBL drugs and their curated mechanisms, ClinicalTrials.gov studies that enrol
# children, and a verbatim quote from each cited abstract. Resolved live on 2026-09-22.
#
# pediatric_onset is the field this panel exists to state honestly: True where the gene causes disease
# presenting in infancy, childhood or adolescence, False where the target is adult-onset or an adult
# symptomatic drug target. A False entry must not be counted towards a paediatric programme.
PARKINSONS_EVIDENCE = {
    'PRKN': {
        'indication': 'Autosomal recessive early-onset Parkinson disease', 'pediatric_onset': True,
        'uniprot': 'O60260', 'pdb_ids': ['8WZN', '8IK6'], 'alphafold_model': 'AF-O60260-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '29644727', 'quote': 'median age at onset of ∼30 years'},
                   {'pmid': '22956510', 'quote': 'develop symptoms before age 45'}],
        'tractability': 'poor - 21 structures but no ChEMBL target and no potent ligand; the route is '
                        'structure-guided allosteric activation of the RING-HECT mechanism',
        'unmet_need': 'high - no disease-modifying therapy for recessive early-onset PD',
        'caveat': 'the MDSGene median onset of ~30 years covers PRKN, PINK1 and DJ-1 together; '
                  'individual juvenile cases are reported but this is adolescent-to-young-adult '
                  'disease, not infancy',
    },
    'PINK1': {
        'indication': 'Autosomal recessive early-onset Parkinson disease', 'pediatric_onset': True,
        'uniprot': 'Q9BXM7', 'pdb_ids': ['9KMR', '9KQN'], 'alphafold_model': 'AF-Q9BXM7-F1',
        'chembl_target': 'CHEMBL3337330', 'potent_ligands': 5, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '22956510', 'quote': 'The rate of mutations overall was 5.1%'}],
        'tractability': 'moderate - a kinase with human structures, but only 5 activities at '
                        'pChEMBL >= 6; kinase activators are harder than inhibitors',
        'unmet_need': 'high - no disease-modifying therapy',
        'caveat': 'the 5.1% is the pooled mutation rate across PRKN, PINK1, DJ-1 and LRRK2 in one '
                  '136-proband UK cohort, not a PINK1-specific prevalence',
    },
    'PARK7': {
        'indication': 'Autosomal recessive early-onset Parkinson disease (DJ-1)', 'pediatric_onset': True,
        'uniprot': 'Q99497', 'pdb_ids': ['9K7Q', '9YGX'], 'alphafold_model': 'AF-Q99497-F1',
        'chembl_target': 'CHEMBL5169188', 'potent_ligands': 25, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '29644727', 'quote': 'recessively inherited PD'}],
        'tractability': 'moderate - the best-resolved of the recessive three (88 structures, '
                        'AlphaFold pLDDT 98) with a small ligand set',
        'unmet_need': 'high - rarest of the three recessive genes and no therapy',
        'caveat': 'DJ-1 is the rarest cause; a programme built on it would need international '
                  'recruitment to find patients',
    },
    'ATP13A2': {
        'indication': 'Kufor-Rakeb syndrome (PARK9), juvenile-onset parkinsonism', 'pediatric_onset': True,
        'uniprot': 'Q9NQ11', 'pdb_ids': ['8IEK', '8IEM'], 'alphafold_model': 'AF-Q9NQ11-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '21542062',
                    'quote': 'rare form of autosomal recessive juvenile or early-onset, levodopa responsive parkinsonism'}],
        'tractability': 'poor-to-moderate - cryo-EM structures of the transporter exist but ChEMBL '
                        'has no target for the accession, so there is no chemical starting point',
        'unmet_need': 'high - levodopa responsive at first, then progressive with dementia',
        'caveat': 'loss-of-function transporter: the therapeutic direction is restoring function '
                  '(chaperone or gene therapy), which small-molecule screening does not address',
    },
    'DNAJC6': {
        'indication': 'Juvenile parkinsonism-dystonia (PARK19)', 'pediatric_onset': True,
        'uniprot': 'O75061', 'pdb_ids': [], 'alphafold_model': 'AF-O75061-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '32472658', 'quote': 'before the age of 21 years'},
                   {'pmid': '32472658', 'quote': 'All presented with neurodevelopmental delay in infancy'}],
        'tractability': 'poor - zero experimental structures for O75061, AlphaFold mean pLDDT 62.9, '
                        'no ChEMBL target; the published route is gene therapy, not chemistry',
        'unmet_need': 'high - childhood onset, rapidly progressive, no therapy',
        'caveat': 'the least tractable target in this panel; included for its clarity as pediatric '
                  'disease, not as a screening target',
    },
    'SYNJ1': {
        'indication': 'PARK20 early-onset atypical parkinsonism', 'pediatric_onset': True,
        'uniprot': 'O43426', 'pdb_ids': ['7A0V', '2VJ0'], 'alphafold_model': 'AF-O43426-F1',
        'chembl_target': 'CHEMBL4523136', 'potent_ligands': 2, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '24816432', 'quote': 'autosomal recessive, early-onset atypical parkinsonism (PARK20)'}],
        'tractability': 'poor - partial-domain structures only and 2 potent ligands',
        'unmet_need': 'high - atypical phenotype with seizures and poor levodopa response',
        'caveat': 'onset in the published families was in the second-to-third decade, so adolescent '
                  'rather than infantile',
    },
    'FBXO7': {
        'indication': 'PARK15 parkinsonian-pyramidal disease', 'pediatric_onset': True,
        'uniprot': 'Q9Y3I1', 'pdb_ids': ['4L9C', '4L9H'], 'alphafold_model': 'AF-Q9Y3I1-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '23318512', 'quote': 'differs from typical Parkinson disease chiefly by juvenile onset'}],
        'tractability': 'poor - two domain structures, no ChEMBL target',
        'unmet_need': 'high - juvenile onset with spasticity and no therapy',
        'caveat': 'very few families reported worldwide',
    },
    'TH': {
        'indication': 'Tyrosine hydroxylase deficiency (infantile parkinsonism)', 'pediatric_onset': True,
        'uniprot': 'P07101', 'pdb_ids': ['7PIM', '6ZN2'], 'alphafold_model': 'AF-P07101-F1',
        'chembl_target': 'CHEMBL1969', 'potent_ligands': 3, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '11134401', 'quote': 'hypokinetic-rigid parkinsonian syndrome with symptoms in early infancy'}],
        'tractability': 'moderate - human structures exist, but the only curated chemistry is the '
                        'inhibitor metyrosine; the need is stabilisation of mutant enzyme',
        'unmet_need': 'moderate - the mild form responds to L-dopa; the severe encephalopathic form '
                      'is dopa-refractory and untreated',
        'caveat': 'treating the deficiency means restoring enzyme activity, so the 3 potent ligands '
                  'in ChEMBL point the wrong way',
    },
    'DDC': {
        'indication': 'AADC deficiency', 'pediatric_onset': True,
        'uniprot': 'P20711', 'pdb_ids': ['9GNS', '9HRH'], 'alphafold_model': 'AF-P20711-F1',
        'chembl_target': 'CHEMBL1843', 'potent_ligands': 2, 'drugs': [],
        'trials': [{'nct_id': 'NCT04903288', 'note': 'eladocagene exuparvovec delivery study in children'}],
        'claims': [{'pmid': '42563827',
                    'quote': 'rare, severe neurological disorder caused by pathogenic variants in the dopa decarboxylase (DDC) gene'},
                   {'pmid': '41212308',
                    'quote': 'gene therapy with eladocagene exuparvovec for aromatic L-amino acid decarboxylase (AADC) deficiency in pediatric patients'}],
        'tractability': 'proven, but not by chemistry - eladocagene exuparvovec (CHEMBL4298189) is an '
                        'approved intraputaminal gene therapy for children',
        'unmet_need': 'moderate - a disease-modifying therapy exists; access, delivery and timing are '
                      'the open problems',
        'caveat': 'eladocagene exuparvovec is deliberately not listed under drugs: its ChEMBL '
                  'mechanism record points at a gene target (CHEMBL5303723), not at the P20711 '
                  'protein, so a drug-to-target check on it would fail',
    },
    'GCH1': {
        'indication': 'Dopa-responsive dystonia (Segawa disease) and BH4 deficiency', 'pediatric_onset': True,
        'uniprot': 'P30793', 'pdb_ids': ['7ALQ', '7ALA'], 'alphafold_model': 'AF-P30793-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [],
        'trials': [{'nct_id': 'NCT00355264', 'note': 'sapropterin in BH4 deficiency, enrols children'},
                   {'nct_id': 'NCT03519711', 'note': 'PTC923 in primary BH4 deficiency, enrols children'}],
        'claims': [{'pmid': '26100751', 'quote': 'Autosomal dominant GTP cyclohydrolase 1 deficiency, also known as Segawa disease'}],
        'tractability': 'not a small-molecule target - the therapy is cofactor replacement (BH4) '
                        'and levodopa, and ChEMBL has no target for P30793',
        'unmet_need': 'low - childhood-onset and highly treatable; the unmet need is diagnostic delay',
        'caveat': 'included as the treatable end of the pediatric spectrum; a screening programme '
                  'against GCH1 itself would be misdirected',
    },
    'SLC6A3': {
        'indication': 'Dopamine transporter deficiency syndrome (infantile parkinsonism-dystonia)',
        'pediatric_onset': True,
        'uniprot': 'Q01959', 'pdb_ids': ['9JKH', '9JKJ'], 'alphafold_model': 'AF-Q01959-F1',
        'chembl_target': 'CHEMBL238', 'potent_ligands': 3419, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '37443770',
                    'quote': 'ultrarare childhood movement disorder caused by biallelic loss-of-function mutations in the SLC6A3 gene'}],
        'tractability': 'good - human transporter structures and 3419 potent ligands; '
                        'pharmacochaperone rescue of mutant DAT is an active published approach',
        'unmet_need': 'high - presents in infancy, no disease-modifying therapy',
        'caveat': 'the large ligand set is psychostimulant chemistry aimed at inhibiting DAT; '
                  'rescuing folding of a loss-of-function mutant is a different problem',
    },
    'GBA1': {
        'indication': 'Neuronopathic Gaucher disease (pediatric) and adult PD risk', 'pediatric_onset': True,
        'uniprot': 'P04062', 'pdb_ids': ['9ENA', '9FJF'], 'alphafold_model': 'AF-P04062-F1',
        'chembl_target': 'CHEMBL2179', 'potent_ligands': 707, 'drugs': [],
        'trials': [{'nct_id': 'NCT07285369', 'note': 'high-dose ambroxol in pediatric Gaucher disease type 3'},
                   {'nct_id': 'NCT03519646', 'note': 'eliglustat in Gaucher disease type IIIB, enrols children'}],
        'claims': [{'pmid': '40542647', 'quote': 'chronic neuronopathic form caused by biallelic pathogenic variants in GBA1'}],
        'tractability': 'good - well-structured enzyme with 707 potent ligands and clinical '
                        'chaperone precedent',
        'unmet_need': 'high for neuronopathic Gaucher - the cited cohort names disease-modifying '
                      'neurological therapy as the greatest unmet need',
        'caveat': 'PEDIATRIC ONLY AS GAUCHER DISEASE. Heterozygous GBA1 raises adult PD risk; it does '
                  'not cause pediatric Parkinson\'s, and counting this target towards a pediatric PD '
                  'programme would be a category error',
    },
    'SNCA': {
        'indication': 'Autosomal dominant Parkinson disease', 'pediatric_onset': False,
        'uniprot': 'P37840', 'pdb_ids': ['34AF', '34AH'], 'alphafold_model': 'AF-P37840-F1',
        'chembl_target': 'CHEMBL6152', 'potent_ligands': 320,
        'drugs': [{'chembl_id': 'CHEMBL4298077', 'name': 'prasinezumab'}], 'trials': [],
        'claims': [{'pmid': '30357936', 'quote': 'later onset of disease'}],
        'tractability': 'moderate - an intrinsically disordered protein; the clinical assets are '
                        'antibodies, not small molecules',
        'unmet_need': 'high in adult PD, none in children',
        'caveat': 'ADULT-ONSET. Prasinezumab and cinpanemab were tested in adults; no pediatric trial '
                  'exists and none should be inferred',
    },
    'LRRK2': {
        'indication': 'Autosomal dominant Parkinson disease', 'pediatric_onset': False,
        'uniprot': 'Q5S007', 'pdb_ids': ['9Y7A', '9YBL'], 'alphafold_model': 'AF-Q5S007-F1',
        'chembl_target': 'CHEMBL1075104', 'potent_ligands': 5099, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '19945904', 'quote': "most frequent known cause of familial and sporadic Parkinson's disease"}],
        'tractability': 'good - the richest chemistry in this panel (5099 potent ligands) and '
                        'clinical-stage kinase inhibitors',
        'unmet_need': 'high in adult PD, none in children',
        'caveat': 'ADULT-ONSET, median ~49 years. G2019S frequency is strongly population-dependent '
                  '(from none to 35.7% of sporadic cases in North-African Arab cohorts), so a single '
                  'headline percentage would be wrong',
    },
    'VPS35': {
        'indication': 'Autosomal dominant Parkinson disease (D620N)', 'pediatric_onset': False,
        'uniprot': 'Q96QK1', 'pdb_ids': ['9Q8M', '8R02'], 'alphafold_model': 'AF-Q96QK1-F1',
        'chembl_target': 'CHEMBL2216744', 'potent_ligands': 2, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '30357936', 'quote': 'three autosomal-dominant PD forms'}],
        'tractability': 'poor - a large protein-protein interface with 2 potent ligands',
        'unmet_need': 'high in adult PD, none in children',
        'caveat': 'ADULT-ONSET and rare; retromer stabilisers remain preclinical',
    },
    'MAOB': {
        'indication': 'Adult symptomatic Parkinson therapy', 'pediatric_onset': False,
        'uniprot': 'P27338', 'pdb_ids': ['9R2J', '9R3J'], 'alphafold_model': 'AF-P27338-F1',
        'chembl_target': 'CHEMBL2039', 'potent_ligands': 3050,
        'drugs': [{'chembl_id': 'CHEMBL972', 'name': 'selegiline'}], 'trials': [],
        'claims': [{'pmid': '35107654', 'quote': 'MAO-B inhibitors are a significant therapeutic option'}],
        'tractability': 'solved - approved inhibitors and 3050 potent ligands',
        'unmet_need': 'low - symptomatic benefit only, and the field is crowded',
        'caveat': 'ADULT symptomatic therapy. The earlier panel called MAOB an X-linked PD risk locus; '
                  'that Mendelian claim is not supported, and the ClinVar hits for this gene largely '
                  'reflect contiguous Xp11 deletions',
    },
    'COMT': {
        'indication': 'Adult symptomatic Parkinson therapy (levodopa add-on)', 'pediatric_onset': False,
        'uniprot': 'P21964', 'pdb_ids': ['6I3C', '5LSA'], 'alphafold_model': 'AF-P21964-F1',
        'chembl_target': 'CHEMBL2023', 'potent_ligands': 117,
        'drugs': [{'chembl_id': 'CHEMBL953', 'name': 'entacapone'}], 'trials': [],
        'claims': [{'pmid': '35217995', 'quote': 'recommended first-line levodopa add-on therapies'}],
        'tractability': 'solved - entacapone, opicapone and tolcapone are approved',
        'unmet_need': 'low - an adjunct for motor fluctuations in advanced adult disease',
        'caveat': 'ADULT adjunct. Previously labelled a PD risk locus; the Val158Met polymorphism is '
                  'a modifier at most, and ClinVar counts here are dominated by 22q11.2 deletions',
    },
    'DRD2': {
        'indication': 'Adult symptomatic Parkinson therapy (dopamine agonists)', 'pediatric_onset': False,
        'uniprot': 'P14416', 'pdb_ids': ['9BS9', '8TZQ'], 'alphafold_model': 'AF-P14416-F1',
        'chembl_target': 'CHEMBL217', 'potent_ligands': 11896,
        'drugs': [{'chembl_id': 'CHEMBL1303', 'name': 'rotigotine'}], 'trials': [],
        'claims': [{'pmid': '37396766', 'quote': 'monotherapy or as an adjunctive therapy to levodopa'}],
        'tractability': 'solved - many approved agonists and 11896 potent ligands',
        'unmet_need': 'low - symptomatic, with impulse-control and somnolence liabilities',
        'caveat': 'ADULT symptomatic therapy; no pediatric parkinsonism indication',
    },
}

SHRINERS_EVIDENCE = {
    'COL1A1': {
        'indication': 'Osteogenesis imperfecta, classical dominant', 'pediatric_onset': True,
        'uniprot': 'P02452', 'pdb_ids': ['8YV3', '5K31'], 'alphafold_model': 'AF-P02452-F1',
        'chembl_target': 'CHEMBL3030', 'potent_ligands': 0, 'drugs': [],
        'trials': [{'nct_id': 'NCT05768854', 'note': 'setrusumab vs bisphosphonates, pediatric phase 3'},
                   {'nct_id': 'NCT05972551', 'note': 'romosozumab vs bisphosphonates in children'}],
        'claims': [{'pmid': '34007986', 'quote': 'Previously known to be caused by defects in type I collagen'}],
        'tractability': 'not directly druggable - a triple helix with no pocket (AlphaFold mean '
                        'pLDDT 52.7) and 0 potent ligands; therapy acts downstream on bone turnover',
        'unmet_need': 'high - bisphosphonates reduce fracture rate without correcting the collagen defect',
        'caveat': 'pdb_count is misleading on its own: most of the 14 RCSB entries for P02452 are '
                  'short synthetic collagen peptides or fusion tags (7E7B is a vaccine trimer), and '
                  'only 5K31 (procollagen C-propeptide) and 8YV3 are the protein itself',
    },
    'COL1A2': {
        'indication': 'Osteogenesis imperfecta, classical dominant', 'pediatric_onset': True,
        'uniprot': 'P08123', 'pdb_ids': ['8YV3'], 'alphafold_model': 'AF-P08123-F1',
        'chembl_target': 'CHEMBL2685', 'potent_ligands': 0, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '34007986',
                    'quote': 'defects in collagen folding, posttranslational modification and processing'}],
        'tractability': 'not directly druggable - 0 potent ligands',
        'unmet_need': 'high - same as COL1A1',
        'caveat': '8YV3 is the only one of the 5 entries carrying P08123 that is a type I collagen '
                  'structure; the rest are guest peptides in type II/IX scaffolds',
    },
    'SERPINF1': {
        'indication': 'Osteogenesis imperfecta type VI', 'pediatric_onset': True,
        'uniprot': 'P36955', 'pdb_ids': ['9J3P', '1IMV'], 'alphafold_model': 'AF-P36955-F1',
        'chembl_target': 'CHEMBL4295753', 'potent_ligands': 0, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '27796462', 'quote': 'a distinct, extremely rare autosomal recessive form of type VI OI'},
                   {'pmid': '25257953', 'quote': 'mutations in SERPINF1 were identified as the molecular cause of OI type VI'}],
        'tractability': 'poor as chemistry - a secreted serpin with 0 potent ligands; protein or '
                        'gene replacement is the logical route',
        'unmet_need': 'high - OI VI responds poorly to bisphosphonates, which is why denosumab was '
                      'tried in these children specifically',
        'caveat': 'the denosumab experience in OI VI is small case series, not controlled trials',
    },
    'CRTAP': {
        'indication': 'Severe recessive osteogenesis imperfecta', 'pediatric_onset': True,
        'uniprot': 'O75718', 'pdb_ids': ['8K0E', '8K0I'], 'alphafold_model': 'AF-O75718-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '25257953',
                    'quote': 'recessive forms of OI have been identified, mostly affecting posttranslational modification of collagen'}],
        'tractability': 'poor - cryo-EM structures of the 3-hydroxylation complex exist, but ChEMBL '
                        'has no target for the accession',
        'unmet_need': 'high - perinatal-lethal to severe disease with no specific therapy',
        'caveat': 'a scaffolding subunit, not an enzyme: included for structural biology, not screening',
    },
    'P3H1': {
        'indication': 'Severe recessive osteogenesis imperfecta', 'pediatric_onset': True,
        'uniprot': 'Q32P28', 'pdb_ids': ['8K0E', '8K0F'], 'alphafold_model': 'AF-Q32P28-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [], 'trials': [],
        'claims': [{'pmid': '34007986', 'quote': 'a collagen-related disorder caused by defects in collagen folding'}],
        'tractability': 'poor today - the only enzyme of the complex, so the most plausible future '
                        'entry point, but ChEMBL has no target for Q32P28',
        'unmet_need': 'high - same recessive OI population as CRTAP',
        'caveat': 'loss of function: an inhibitor would be the wrong direction, and no activator '
                  'chemistry exists',
    },
    'SOST': {
        'indication': 'Osteogenesis imperfecta, anti-sclerostin therapy', 'pediatric_onset': True,
        'uniprot': 'Q9BQB4', 'pdb_ids': ['6L6R', '3SOV'], 'alphafold_model': 'AF-Q9BQB4-F1',
        'chembl_target': 'CHEMBL3580487', 'potent_ligands': 28,
        'drugs': [{'chembl_id': 'CHEMBL4297918', 'name': 'setrusumab'},
                  {'chembl_id': 'CHEMBL2107874', 'name': 'romosozumab'}],
        'trials': [{'nct_id': 'NCT05125809', 'note': 'setrusumab vs placebo, phase 2/3, children and adults'},
                   {'nct_id': 'NCT05768854', 'note': 'setrusumab vs bisphosphonates, pediatric phase 3'},
                   {'nct_id': 'NCT05972551', 'note': 'romosozumab vs bisphosphonates in children, phase 3'}],
        'claims': [{'pmid': '28370407', 'quote': 'anti-sclerostin antibody, in adults with moderate osteogenesis imperfecta'}],
        'tractability': 'proven - two antibodies in pediatric phase 3, one of them approved in adults',
        'unmet_need': 'moderate - the strongest pediatric OI programme in flight, so the gap is '
                      'narrowing rather than open',
        'caveat': 'human validation comes from sclerosteosis, a recessive high-bone-mass disorder; '
                  'the cited phase 2a was in adults, and the pediatric evidence is trials still '
                  'reading out, not published outcomes',
    },
    'TNFSF11': {
        'indication': 'RANKL blockade in pediatric bone disease', 'pediatric_onset': True,
        'uniprot': 'O14788', 'pdb_ids': ['5BNQ', '3URF'], 'alphafold_model': 'AF-O14788-F1',
        'chembl_target': 'CHEMBL2364162', 'potent_ligands': 3,
        'drugs': [{'chembl_id': 'CHEMBL1237023', 'name': 'denosumab'}],
        'trials': [{'nct_id': 'NCT01799798', 'note': 'denosumab pilot in children with OI, completed'},
                   {'nct_id': 'NCT02352753', 'note': 'phase 3 denosumab in children with OI, terminated'}],
        'claims': [{'pmid': '37401056', 'quote': 'pediatric skeletal conditions such as OI'},
                   {'pmid': '25257953', 'quote': 'increased bone resorption'}],
        'tractability': 'proven - denosumab is approved (in adults) and used off-label in children',
        'unmet_need': 'moderate - effective but with a specific pediatric hazard',
        'caveat': 'both pediatric OI phase 3 programmes (NCT02352753, NCT03638128) were terminated '
                  'and rebound hypercalcaemia after withdrawal is the known risk in children',
    },
    'FGFR3': {
        'indication': 'Achondroplasia and hypochondroplasia', 'pediatric_onset': True,
        'uniprot': 'P22607', 'pdb_ids': ['9EKO', '9VMB'], 'alphafold_model': 'AF-P22607-F1',
        'chembl_target': 'CHEMBL2742', 'potent_ligands': 3580,
        'drugs': [{'chembl_id': 'CHEMBL1834657', 'name': 'infigratinib'}],
        'trials': [{'nct_id': 'NCT04265651', 'note': 'infigratinib phase 2 in children'},
                   {'nct_id': 'NCT06164951', 'note': 'infigratinib phase 3 in children and adolescents'},
                   {'nct_id': 'NCT07169279', 'note': 'infigratinib in children under 3'}],
        'claims': [{'pmid': '24365319', 'quote': 'birth prevalence of 1 in 20000-30000 live-born infants'},
                   {'pmid': '24365319', 'quote': 'caused, in virtually all of the cases, by a G380R mutation'}],
        'tractability': 'good - 3580 potent ligands and a clinical-stage pediatric inhibitor',
        'unmet_need': 'moderate - vosoritide is approved, so a second mechanism must beat it',
        'caveat': 'FGFR3 inhibitors come from oncology; using a kinase inhibitor in growing children '
                  'is a dose and safety problem, which is why the pediatric trials use low doses',
    },
    'NPR2': {
        'indication': 'Growth-plate cGMP signalling; vosoritide receptor', 'pediatric_onset': True,
        'uniprot': 'P20594', 'pdb_ids': [], 'alphafold_model': 'AF-P20594-F1',
        'chembl_target': 'CHEMBL1795', 'potent_ligands': 0,
        'drugs': [{'chembl_id': 'CHEMBL3707276', 'name': 'vosoritide'}],
        'trials': [{'nct_id': 'NCT02055157', 'note': 'vosoritide phase 2 in children with achondroplasia'},
                   {'nct_id': 'NCT03583697', 'note': 'vosoritide in infants and young children'}],
        'claims': [{'pmid': '34162036',
                    'quote': 'autosomal recessive skeletal dysplasia caused by biallelic loss of function variations of NPR2'},
                   {'pmid': '32720985', 'quote': 'heterozygous mutations may account for 2% to 6% of idiopathic short stature'},
                   {'pmid': '32891212', 'quote': 'There are no effective therapies for achondroplasia'}],
        'tractability': 'peptide-only - an approved CNP analogue, but zero experimental structures '
                        'for P20594 and 0 potent small-molecule ligands',
        'unmet_need': 'moderate - daily injection; an oral or long-acting agonist is the open problem',
        'caveat': 'the previous entry claimed 15 PDB structures; RCSB has none for this accession',
    },
    'ALPL': {
        'indication': 'Hypophosphatasia', 'pediatric_onset': True,
        'uniprot': 'P05186', 'pdb_ids': ['9SH5', '7YIX'], 'alphafold_model': 'AF-P05186-F1',
        'chembl_target': 'CHEMBL5979', 'potent_ligands': 383, 'drugs': [],
        'trials': [{'nct_id': 'NCT01176266', 'note': 'asfotase alfa in infants and children up to 5 years'},
                   {'nct_id': 'NCT06079281', 'note': 'ALXN1850 phase 3, adolescents and adults'}],
        'claims': [{'pmid': '26893260',
                    'quote': 'loss-of-function mutations within the gene that encodes the tissue-nonspecific isoenzyme'}],
        'tractability': 'proven by enzyme replacement - asfotase alfa is approved; the 383 potent '
                        'ligands in ChEMBL are inhibitors and point the wrong way',
        'unmet_need': 'moderate - replacement works but is lifelong, injected and immunogenic',
        'caveat': 'inheritance corrected: perinatal/infantile disease is recessive, milder childhood '
                  'and adult forms can be dominant, so the previous AR-only label was wrong',
    },
    'FGF23': {
        'indication': 'X-linked hypophosphataemia and ADHR', 'pediatric_onset': True,
        'uniprot': 'Q9GZV9', 'pdb_ids': ['7YSW', '7YSU'], 'alphafold_model': 'AF-Q9GZV9-F1',
        'chembl_target': 'CHEMBL3713913', 'potent_ligands': 5,
        'drugs': [{'chembl_id': 'CHEMBL3707326', 'name': 'burosumab'}],
        'trials': [{'nct_id': 'NCT03233126', 'note': 'burosumab phase 3 in children with XLH'},
                   {'nct_id': 'NCT02750618', 'note': 'burosumab in children from 1 to 4 years'}],
        'claims': [{'pmid': '31104833', 'quote': 'burosumab, a fully human monoclonal antibody against FGF23'}],
        'tractability': 'proven - an approved antibody with pediatric labelling',
        'unmet_need': 'low-to-moderate - burosumab works; cost and access are the constraints',
        'caveat': 'the previous entry attributed X-linked hypophosphataemia to FGF23 itself. XLH is '
                  'caused by PHEX; FGF23 gain-of-function causes the autosomal dominant form, and in '
                  'XLH FGF23 is the elevated effector, not the mutated gene',
    },
    'PHEX': {
        'indication': 'X-linked hypophosphataemia', 'pediatric_onset': True,
        'uniprot': 'P78562', 'pdb_ids': [], 'alphafold_model': 'AF-P78562-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [],
        'trials': [{'nct_id': 'NCT03233126', 'note': 'burosumab phase 3 in children with XLH (PHEX confirmed)'}],
        'claims': [{'pmid': '39814982', 'quote': 'rare metabolic bone disorder caused by pathogenic variants in the PHEX gene'},
                   {'pmid': '39814982',
                    'quote': 'increased synthesis of the bone-derived phosphaturic hormone fibroblast growth factor 23'}],
        'tractability': 'none directly - zero experimental structures for P78562 and no ChEMBL '
                        'target; the tractable node is FGF23 downstream',
        'unmet_need': 'covered downstream by burosumab',
        'caveat': 'the previous entry claimed 10 PDB structures; RCSB has none. Carried as the '
                  'causal gene for diagnosis, not as a drug target',
    },
    'ACVR1': {
        'indication': 'Fibrodysplasia ossificans progressiva', 'pediatric_onset': True,
        'uniprot': 'Q04771', 'pdb_ids': ['9RDA', '9L04'], 'alphafold_model': 'AF-Q04771-F1',
        'chembl_target': 'CHEMBL5903', 'potent_ligands': 1627, 'drugs': [],
        'trials': [{'nct_id': 'NCT03312634', 'note': 'MOVE phase 3 palovarotene, from age 4'},
                   {'nct_id': 'NCT05027802', 'note': 'palovarotene rollover, children and adults'},
                   {'nct_id': 'NCT07559513', 'note': 'garetosmab in children with FOP'}],
        'claims': [{'pmid': '36583535',
                    'quote': 'ultra-rare, severely disabling genetic disorder of progressive heterotopic ossification'}],
        'tractability': 'good - 85 structures including R206H mutant and ALK2-inhibitor co-crystals, '
                        'and 1627 potent ligands',
        'unmet_need': 'high - palovarotene reduces new heterotopic ossification but carries growth-'
                      'plate closure risk in skeletally immature children',
        'caveat': 'palovarotene is deliberately not listed under drugs: it is an RARgamma agonist, so '
                  'its ChEMBL mechanism does not point at ALK2. The ALK2 inhibitors ChEMBL links to '
                  'this target are oncology JAK-family drugs, not FOP therapies',
    },
    'EXT1': {
        'indication': 'Hereditary multiple osteochondromas', 'pediatric_onset': True,
        'uniprot': 'Q16394', 'pdb_ids': ['7ZAY', '7SCH'], 'alphafold_model': 'AF-Q16394-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [],
        'trials': [{'nct_id': 'NCT07556874', 'note': 'surgical burden in multiple osteochondromas, enrols children'}],
        'claims': [{'pmid': '18271966', 'quote': 'The prevalence is estimated at 1:50,000'}],
        'tractability': 'poor - structures of the EXT1/EXT2 glycosyltransferase exist but ChEMBL has '
                        'no target and there is no chemical matter',
        'unmet_need': 'high - management is repeated surgery through childhood; no medical therapy',
        'caveat': 'an unmet-need entry, not a screening-ready target; loss of function again means '
                  'inhibition is the wrong direction',
    },
    'IRF6': {
        'indication': 'Van der Woude syndrome and orofacial clefting', 'pediatric_onset': True,
        'uniprot': 'O14896', 'pdb_ids': [], 'alphafold_model': 'AF-O14896-F1',
        'chembl_target': None, 'potent_ligands': 0, 'drugs': [],
        'trials': [{'nct_id': 'NCT06284434', 'note': 'alveolar bone graft analgesia in cleft patients, enrols children'}],
        'claims': [{'pmid': '32558391', 'quote': 'Mutations in the IRF6 gene account for 70% of cases'}],
        'tractability': 'none - a transcription factor with zero experimental structures for O14896 '
                        'and no ChEMBL target',
        'unmet_need': 'the care pathway is surgical; the genetics informs counselling and recurrence '
                      'risk, not pharmacology',
        'caveat': 'the previous entry claimed 8 PDB structures; RCSB has none. The 70% figure is the '
                  'share of Van der Woude syndrome, not of all clefts - VWS is about 2% of clefts',
    },
}


# ---------------------------------------------------------------------------------------- ALS
# Re-derived live on 2026-09-22 (RCSB, UniProt, AlphaFold, ChEMBL, ClinVar, PubMed, CT.gov) after
# every pdb_count in the old ALS panel turned out to be invented. Two symbols were wrong as well:
# TDP43 is not a gene name (UniProt calls Q13148 TARDBP) and C9ORF72 is spelled C9orf72.
#
# Two findings shape the whole panel:
#   * ChEMBL curates no drug mechanism against any of these accessions except SIGMAR1. Tofersen,
#     the one approved ALS gene-targeted drug, points at CHEMBL3833461 "SOD1 mRNA" - a NUCLEIC-ACID
#     target carrying ENSG00000142168, not the protein P00441. The modality that works in ALS acts
#     on the transcript, so a protein-target docking platform cannot claim it.
#   * On the aggregation-prone RNA-binding proteins a large pdb_count counts amyloid fibrils and
#     isolated domains. Every record states this in 'modality' rather than letting the number imply
#     a pocket.
ALS_EVIDENCE = {
    'SOD1': {
        'indication': 'SOD1-ALS, the prototypical familial form',
        'uniprot': 'P00441', 'pdb_ids': ['9XJ0', '9IYD', '9LI1'], 'alphafold_model': 'AF-P00441-F1',
        'chembl_target': 'CHEMBL2354', 'potent_ligands': 8, 'clinvar_pathogenic': 138,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '23286750',
                    'quote': 'Causative superoxide dismutase-1 (SOD1) mutations are identified in 10-20% of FALS'},
                   {'pmid': '34247168',
                    'quote': 'the majority of SOD1 and C9orf72 ALS cases may be found among those with sALS'}],
        'modality': 'antisense, not small molecule - tofersen is approved for SOD1-ALS and acts on the '
                    'mRNA; its ChEMBL mechanism target is "SOD1 mRNA", not P00441',
        'tractability': 'poor for docking despite 156 structures - a small metalloenzyme with no '
                        'inhibitable pocket and only 8 activities at pChEMBL >= 6',
        'unmet_need': 'moderate - tofersen is approved, but it is intrathecal, genotype-restricted and '
                      'does not help the 98% of ALS that is not SOD1',
        'caveat': 'the old panel claimed 50 structures; RCSB holds 156 for P00441, and the recent ones '
                  '(9IYD, 9LI1) are G93A amyloid filaments, not ligand complexes. The therapeutic aim is '
                  'to remove the protein, so a binder would have to stabilise the native fold, not block '
                  'an active site. No tofersen trial can be cited here: VALOR and ATLAS are adults only',
        'trials_note': 'NCT02623699 (VALOR) and NCT04856982 (ATLAS) are real tofersen trials but list '
                       'stdAges ADULT/OLDER_ADULT, so they are deliberately not cited',
    },
    'TARDBP': {
        'indication': 'TARDBP-ALS, and TDP-43 proteinopathy in ALS generally',
        'uniprot': 'Q13148', 'pdb_ids': ['9FOF', '8QX9', '8QXB'], 'alphafold_model': 'AF-Q13148-F1',
        'chembl_target': 'CHEMBL2362981', 'potent_ligands': 5, 'clinvar_pathogenic': 48,
        'drugs': [],
        'trials': [{'nct_id': 'NCT07743268',
                    'note': 'nL-TARDB-006, personalised antisense oligonucleotide for TARDBP ALS'}],
        'claims': [{'pmid': '19224587',
                    'quote': 'the major protein of the ubiquitinated inclusions (UBIs) found in affected motor neurons'},
                   {'pmid': '35239007',
                    'quote': 'the TARDBP-mutant frequency in the Chinese population was 1.4% (83/5998), with 0.8% (46/5470) in sALS and 7.0% (37/528) in fALS'}],
        'modality': 'antisense or splicing correction, not small molecule - the cited trial is a '
                    'personalised ASO, and the tractable downstream event is cryptic-exon repression',
        'tractability': 'poor - an intrinsically disordered RNA-binding protein (AlphaFold mean pLDDT '
                        '65.2) with 5 potent ligands',
        'unmet_need': 'very high - TDP-43 pathology is present in almost all ALS, and nothing on the '
                      'market addresses it',
        'caveat': 'the old panel said "5% fALS, 50% sALS": the 50% conflated TDP-43 PATHOLOGY with '
                  'TARDBP MUTATION, which is ~1% of ALS. Of the 44 RCSB entries (not 15), the newest '
                  'are amyloid filaments (8QX9, 9FOF) - fibril cores, not druggable pockets',
    },
    'FUS': {
        'indication': 'FUS-ALS, including juvenile and early-onset disease',
        'uniprot': 'P35637', 'pdb_ids': ['7VQQ', '7CYL', '6KJ1'], 'alphafold_model': 'AF-P35637-F1',
        'chembl_target': 'CHEMBL5724679', 'potent_ligands': 4, 'clinvar_pathogenic': 47,
        'drugs': [],
        'trials': [{'nct_id': 'NCT04768972',
                    'note': 'FUSION phase 1-3 of ION363 (jacifusen), a FUS-targeting antisense oligonucleotide'}],
        'claims': [{'pmid': '26362943',
                    'quote': 'mutations in fused in sarcoma (FUS) can be identified in just around 5% of familial and 1% of overall sporadic cases'},
                   {'pmid': '23046859',
                    'quote': 'de novo FUS mutations are associated with juvenile-onset SALS'}],
        'modality': 'antisense - ION363 is in phase 3 and is the only ALS trial on this panel that '
                    'enrols children; small-molecule work on FUS has produced 4 potent ligands',
        'tractability': 'poor - the most disordered protein on the panel (AlphaFold mean pLDDT 53.6)',
        'unmet_need': 'high - FUS-ALS is aggressive and strikes the young; jacifusen is not yet approved',
        'caveat': 'of the 23 entries (not 20), 7VQQ and 6XFM are low-complexity-domain amyloid fibrils '
                  'and 6KJ1 is a six-residue peptide (FUS 37-42); 7CYL is the PY-NLS bound to '
                  'karyopherin-beta2, which is the one interface with any pocket-like character',
    },
    'C9orf72': {
        'indication': 'C9orf72 repeat-expansion ALS/FTD, the commonest genetic cause',
        'uniprot': 'Q96LT7', 'pdb_ids': ['7O2W', '7MGE', '6LT0'], 'alphafold_model': 'AF-Q96LT7-F1',
        'chembl_target': None, 'potent_ligands': 0, 'clinvar_pathogenic': 71,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '32526057',
                    'quote': 'responsible for 30%-50% of familial ALS and 7% of sporadic ALS'},
                   {'pmid': '36650645',
                    'quote': 'In 302 patients with SALS, 27 (8.9%) patients with a C9orf72 HRE mutation were detected'}],
        'modality': 'not a small-molecule protein target at all - the lesion is an intronic GGGGCC '
                    'expansion; the tractable objects are the repeat RNA and its dipeptide products',
        'tractability': 'none as a protein - ChEMBL has no single-protein target for Q96LT7',
        'unmet_need': 'very high - the largest genetic subgroup in ALS, and the Biogen ASO programme '
                      'against it did not succeed',
        'caveat': 'all 4 RCSB entries (the old panel said 5) are cryo-EM structures of the '
                  'C9orf72-SMCR8-WDR41 GEF/GAP complex, so they inform biology, not docking. Symbol '
                  'corrected from C9ORF72: UniProt spells the gene C9orf72 and the verifier matches exactly',
    },
    'TBK1': {
        'indication': 'TBK1 haploinsufficiency ALS/FTD',
        'uniprot': 'Q9UHD2', 'pdb_ids': ['6RSU', '6RSR', '6O8B'], 'alphafold_model': 'AF-Q9UHD2-F1',
        'chembl_target': 'CHEMBL5408', 'potent_ligands': 1999, 'clinvar_pathogenic': 77,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '25803835',
                    'quote': 'haploinsufficiency of TBK1 causes ALS and fronto-temporal dementia'},
                   {'pmid': '37422901', 'quote': 'The frequency of TBK1 LoF variants in ALS was 0.5%'}],
        'modality': 'small molecule is chemically feasible but points the wrong way - the disease is '
                    'LOSS of TBK1, and all 1999 potent ligands are inhibitors',
        'tractability': 'chemically tractable, biologically inverted - a well-structured kinase '
                        '(pLDDT 89.7) with real inhibitor co-crystals (6RSU, 6RSR)',
        'unmet_need': 'high - restoring a haploinsufficient kinase needs an activator or a stabiliser, '
                      'and no such chemistry exists',
        'caveat': 'the old count of 30 exceeded the live count of 25, so it would have failed the '
                  'verifier outright. The abundant chemistry here is oncology/inflammation inhibitor '
                  'matter and is actively misleading for an ALS programme',
    },
    'OPTN': {
        'indication': 'Optineurin ALS',
        'uniprot': 'Q96CV9', 'pdb_ids': ['9M0O', '9B0B', '9IKQ'], 'alphafold_model': 'AF-Q96CV9-F1',
        'chembl_target': None, 'potent_ligands': 0, 'clinvar_pathogenic': 74,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '20428114',
                    'quote': 'a homozygous deletion of exon 5, a homozygous Q398X nonsense mutation and a heterozygous E478G missense mutation'}],
        'modality': 'poorly suited to small molecule - an adapter that works by protein-protein '
                    'interaction, with no catalytic site and no ChEMBL target',
        'tractability': 'none today - ChEMBL has no single-protein target for Q96CV9',
        'unmet_need': 'high - loss-of-function autophagy-receptor disease with no pharmacology',
        'caveat': 'the live count is 14, not 10, but every entry is a short fragment bound to a partner '
                  '(LZD with Rab8a, the NZF/HOIP interface), so the number reflects interaction '
                  'biology. Inheritance corrected: both recessive (exon-5 deletion, Q398X) and '
                  'dominant (E478G) forms are documented in the founding paper',
    },
    'VCP': {
        'indication': 'VCP multisystem proteinopathy with ALS (IBMPFD)',
        'uniprot': 'P55072', 'pdb_ids': ['9OHN', '9Y05', '9Y03'], 'alphafold_model': 'AF-P55072-F1',
        'chembl_target': 'CHEMBL1075145', 'potent_ligands': 436, 'clinvar_pathogenic': 89,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '29754758',
                    'quote': 'Over fifty missense mutations in the gene coding for valosin-containing protein (VCP) are associated with a unique autosomal dominant adult-onset progressive disease'}],
        'modality': 'genuinely small-molecule tractable - the best-suited target on this panel, with '
                    'ATP-competitive and allosteric inhibitors co-crystallised against disease mutants',
        'tractability': 'tractable - 144 structures including inhibitor complexes (9OHN with GND-135, '
                        '9Y05 with CB-5083) and 436 activities at pChEMBL >= 6',
        'unmet_need': 'moderate - CB-5083 reached phase 1 in oncology and was discontinued for '
                      'off-target toxicity; no VCP compound has been taken into ALS',
        'caveat': 'the old count of 40 understated a live 144. The direction of effect is unsettled: '
                  'disease mutants are hyperactive, so inhibition is arguable, but VCP is essential in '
                  'every cell and the therapeutic window is the whole problem',
    },
    'SQSTM1': {
        'indication': 'SQSTM1/p62 ALS, often with FTD',
        'uniprot': 'Q13501', 'pdb_ids': ['9HGE', '9H1J', '7R1O'], 'alphafold_model': 'AF-Q13501-F1',
        'chembl_target': 'CHEMBL4295816', 'potent_ligands': 2, 'clinvar_pathogenic': 62,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '39122262',
                    'quote': 'we identified 32 patients with 25 different SQSTM1 variants with a mutant frequency of 1.6%'}],
        'modality': 'poorly suited to small molecule - a multi-domain autophagy adapter whose function '
                    'is oligomerisation and cargo binding, not catalysis',
        'tractability': 'poor - 2 potent ligands; 7R1O (ZZ domain with dusquetide) is the only '
                        'ligand-bound entry',
        'unmet_need': 'high - no pharmacology, and the same gene also causes Paget disease of bone',
        'caveat': 'the live count is 26 rather than 15, but 9HGE and 6TGY are PB1-domain filaments and '
                  '9H1J is a UBA domain bound to a nanobody: isolated domains, not a whole protein '
                  'with a site',
    },
    'UBQLN2': {
        'indication': 'X-linked ALS and ALS/dementia',
        'uniprot': 'Q9UHD9', 'pdb_ids': ['7F7X', '6MUN', '1J8C'], 'alphafold_model': 'AF-Q9UHD9-F1',
        'chembl_target': 'CHEMBL6067354', 'potent_ligands': 0, 'clinvar_pathogenic': 123,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '21857683',
                    'quote': 'mutations in UBQLN2, which encodes the ubiquitin-like protein ubiquilin 2, cause dominantly inherited, chromosome-X-linked ALS and ALS/dementia'}],
        'modality': 'poorly suited to small molecule - the disease mechanism runs through liquid-liquid '
                    'phase separation and proteasome shuttling, neither of which presents a pocket',
        'tractability': 'none - ChEMBL has a target for Q9UHD9 but zero activities at pChEMBL >= 6',
        'unmet_need': 'high - rare, aggressive, X-linked, and pharmacologically untouched',
        'caveat': 'the old panel claimed 8 structures; RCSB has 4, and all four are NMR structures of '
                  'the isolated UBA or UBL domain bound to a partner. Most disease mutations lie in the '
                  'PXX region, which none of them covers',
    },
    'PFN1': {
        'indication': 'Profilin-1 familial ALS',
        'uniprot': 'P07737', 'pdb_ids': ['9AZP', '8RTY', '8BJH'], 'alphafold_model': 'AF-P07737-F1',
        'chembl_target': 'CHEMBL6066975', 'potent_ligands': 0, 'clinvar_pathogenic': 30,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '22801503',
                    'quote': 'Further sequence analysis identified 4 mutations in 7 out of 274 FALS cases'}],
        'modality': 'poorly suited to small molecule - a 140-residue actin-monomer binder acting '
                    'through protein-protein interaction, with a toxic gain of function',
        'tractability': 'none - 0 activities at pChEMBL >= 6 despite a well-folded protein (pLDDT 95.6)',
        'unmet_need': 'high - no chemical matter at all',
        'caveat': 'the old count of 25 overstated a live 22 and would have failed the verifier. The 22 '
                  'also flatter the target: 9AZP and 8RTY are F-actin assemblies in which profilin is '
                  'one component, and 8BJH/8BJI/8BJJ are Vibrio ExoY toxin chimeras carrying a '
                  'proline-rich motif, not human PFN1 as a drug target',
    },
    'KIF5A': {
        'indication': 'KIF5A ALS',
        'uniprot': 'Q12840', 'pdb_ids': ['9T17', '4UXT'], 'alphafold_model': 'AF-Q12840-F1',
        'chembl_target': 'CHEMBL5295', 'potent_ligands': 0, 'clinvar_pathogenic': 60,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '29566793',
                    'quote': 'ALS-associated mutations are primarily located at the C-terminal cargo-binding tail domain'}],
        'modality': 'poorly suited to small molecule - the ALS lesion is exon-27 skipping producing a '
                    'mutant tail, which is a splicing problem, not a binding-site problem',
        'tractability': 'none - 0 potent ligands',
        'unmet_need': 'high - a toxic gain of function from a novel C-terminus',
        'caveat': 'the old panel claimed 10 structures; RCSB has 4, and all four are MOTOR-domain '
                  'reconstructions on microtubules. None covers the C-terminal cargo-binding tail where '
                  'the ALS mutations are, so the structural coverage is of the wrong end of the protein',
    },
    'NEK1': {
        'indication': 'NEK1 loss-of-function ALS risk',
        'uniprot': 'Q96PY6', 'pdb_ids': ['4B9D', '4APC'], 'alphafold_model': 'AF-Q96PY6-F1',
        'chembl_target': 'CHEMBL5855', 'potent_ligands': 262, 'clinvar_pathogenic': 121,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '27455347', 'quote': 'we observed NEK1 risk variants in nearly 3% of ALS cases'}],
        'modality': 'small molecule is chemically feasible but points the wrong way - the ALS mechanism '
                    'is loss of function and the available chemistry is inhibitors',
        'tractability': 'chemically tractable, biologically inverted - 262 potent ligands and a kinase '
                        'domain co-crystal (4B9D)',
        'unmet_need': 'high - a common risk gene with no therapeutic hypothesis that inhibition serves',
        'caveat': 'the old count of 8 overstated a live 2, and both entries are the isolated kinase '
                  'domain from 2012. Inheritance corrected: NEK1 is a loss-of-function RISK gene found '
                  'in ~3% of cases, not an autosomal-dominant cause in <1% as the panel claimed',
    },
    'ATXN2': {
        'indication': 'ATXN2 intermediate-repeat ALS risk',
        'uniprot': 'Q99700', 'pdb_ids': ['3KTR'], 'alphafold_model': 'AF-Q99700-F1',
        'chembl_target': 'CHEMBL1795085', 'potent_ligands': 160, 'clinvar_pathogenic': 10,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '20740007',
                    'quote': 'intermediate-length polyQ expansions (27-33 glutamines) in ATXN2 were significantly associated with ALS'}],
        'modality': 'antisense - lowering ataxin-2 is the tested idea (BIIB105); the protein itself '
                    'offers nothing to dock against',
        'tractability': 'none - 1 structure, and AlphaFold mean pLDDT 45.8 marks it as almost entirely '
                        'disordered',
        'unmet_need': 'high - a common modifier with a clear lowering hypothesis and no small-molecule route',
        'caveat': 'the old count of 5 overstated a live 1, and 3KTR is ataxin-2 RECOGNISED BY '
                  'poly(A)-binding protein - a peptide in someone else\'s groove, not a pocket of its '
                  'own. The 160 ChEMBL activities are assay-panel counts, not an ataxin-2 hit series. '
                  'Inheritance corrected: a repeat-length risk allele, not a dominant Mendelian gene',
    },
    'MATR3': {
        'indication': 'MATR3 disease: distal myopathy with vocal cord weakness, with contested ALS attribution',
        'uniprot': 'P43243', 'pdb_ids': [], 'alphafold_model': 'AF-P43243-F1',
        'chembl_target': 'CHEMBL5724643', 'potent_ligands': 3, 'clinvar_pathogenic': 15,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '25523636',
                    'quote': 'MATR3 mutations are not a common cause of ALS in Australian familial cases'},
                   {'pmid': '25154462',
                    'quote': 'There were no clinical, electrophysiological, or histopathological signs of lower motor neuron involvement'}],
        'modality': 'not suited to small molecule - a disordered nuclear-matrix RNA-binding protein '
                    'with no experimental structure at all',
        'tractability': 'none - ZERO RCSB entries for P43243 and 3 potent ligands',
        'unmet_need': 'unclear, because the ALS attribution itself is unsettled',
        'caveat': 'the old panel claimed 3 structures; RCSB holds NONE. This is the weakest ALS claim '
                  'on the panel and is kept only because the negative evidence is itself citable: an '
                  'Australian familial series found no MATR3 mutations, and the 16-patient S85C cohort '
                  'showed no lower motor neuron involvement. Treat as myopathy first, ALS second',
    },
    'HNRNPA1': {
        'indication': 'hnRNPA1 multisystem proteinopathy with ALS',
        'uniprot': 'P09651', 'pdb_ids': ['9VVA', '9HQ9', '9GKF'], 'alphafold_model': 'AF-P09651-F1',
        'chembl_target': 'CHEMBL1955709', 'potent_ligands': 1, 'clinvar_pathogenic': 10,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '23455423', 'quote': 'in one case of familial amyotrophic lateral sclerosis'}],
        'modality': 'poorly suited to small molecule - the pathogenic event is a steric-zipper '
                    'fibrillisation in a prion-like domain, which is not a ligandable site',
        'tractability': 'poor - 1 activity at pChEMBL >= 6 despite 73 structures',
        'unmet_need': 'low as an ALS target - the human genetic evidence is a single familial case',
        'caveat': 'the 73 entries (the old panel said 20) are the single most misleading number in this '
                  'panel: most are "UP1", the isolated tandem-RRM fragment, many of them fragment '
                  'soaks from one screening campaign (9HQ9 and 9HQJ are Enamine library compounds '
                  'against RNA binding, not ALS). 9GKF is an amyloid fibril. None addresses the '
                  'prion-like domain where the disease mutations sit',
    },
    'CHCHD10': {
        'indication': 'CHCHD10 mitochondrial ALS/FTD',
        'uniprot': 'Q8WYQ3', 'pdb_ids': ['9CWW', '9OYS', '9OYQ'], 'alphafold_model': 'AF-Q8WYQ3-F1',
        'chembl_target': None, 'potent_ligands': 0, 'clinvar_pathogenic': 53,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '24934289',
                    'quote': 'We identified the same missense p.Ser59Leu mutation in one of these families'}],
        'modality': 'not suited to small molecule - a small intermembrane-space protein with no ChEMBL '
                    'target and no globular structure to dock into',
        'tractability': 'none - ChEMBL has no single-protein target for Q8WYQ3',
        'unmet_need': 'high but very rare',
        'caveat': 'the live count is 5 rather than 2, but ALL FIVE are cryo-EM amyloid fibrils of the '
                  'N-terminal fragment (including the S59L fibril, 9OYS). A pdb_count of 5 here means '
                  'five fibril polymorphs and zero druggable folds',
    },
    'ANG': {
        'indication': 'Angiogenin loss-of-function ALS',
        'uniprot': 'P03950', 'pdb_ids': ['9BDL', '8OO3'], 'alphafold_model': 'AF-P03950-F1',
        'chembl_target': 'CHEMBL5829', 'potent_ligands': 0, 'clinvar_pathogenic': 29,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '17886298',
                    'quote': 'Functional assays show that these ANG mutations result in complete loss of function'},
                   {'pmid': '31025543', 'quote': 'the observed frequency of ANG mutations was 2.9%'}],
        'modality': 'protein replacement, not small molecule - the mechanism is complete loss of '
                    'ribonucleolytic and nuclear-translocation activity, and ANG itself was '
                    'neuroprotective when administered to SOD1 mice',
        'tractability': 'none for inhibition - 0 potent ligands, and inhibiting a protein whose loss '
                        'causes the disease is the wrong direction',
        'unmet_need': 'moderate - a clear loss-of-function mechanism with an obvious replacement route '
                      'that nobody has taken to the clinic',
        'caveat': 'the old count of 15 badly understated a live 56, but the 56 are not ALS chemistry: '
                  '9BDL/9BDN are 80S ribosome complexes and 8OO3 is a cisplatin adduct from a '
                  'metallodrug study. Mechanism corrected from "stress response, angiogenesis" to '
                  'explicit loss of function',
    },
    'STMN2': {
        'indication': 'Stathmin-2 depletion downstream of TDP-43 loss',
        'uniprot': 'Q93045', 'pdb_ids': [], 'alphafold_model': 'AF-Q93045-F1',
        'chembl_target': 'CHEMBL6067366', 'potent_ligands': 2, 'clinvar_pathogenic': 33,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '41996987',
                    'quote': 'aberrant inclusion of cryptic exons in essential neuronal genes, such as STMN2 (Stathmin 2) and UNC13A (Unc-13 Homolog A)'}],
        'modality': 'splicing correction or gene replacement, not small molecule - the goal is to '
                    'RESTORE full-length stathmin-2, which a docking campaign cannot do',
        'tractability': 'none - ZERO RCSB entries for Q93045 and 2 potent ligands',
        'unmet_need': 'high - one of the most promising mechanistic handles in sporadic ALS',
        'caveat': 'the old panel claimed 2 structures; RCSB holds NONE, and the inheritance claim of '
                  '"AD, <1% fALS" was wrong in kind: STMN2 is not a Mendelian ALS gene. It is a '
                  'consequence of TDP-43 loss, which is why it appears in nearly all ALS rather than a '
                  'fraction of it',
    },
    'UNC13A': {
        'indication': 'UNC13A risk polymorphism and cryptic-exon depletion',
        'uniprot': 'Q9UPW8', 'pdb_ids': [], 'alphafold_model': 'AF-Q9UPW8-F1',
        'chembl_target': None, 'potent_ligands': 0, 'clinvar_pathogenic': 17,
        'drugs': [], 'trials': [],
        'claims': [{'pmid': '35197628',
                    'quote': 'Two common intronic UNC13A polymorphisms strongly associated with amyotrophic lateral sclerosis and frontotemporal dementia risk overlap with TDP-43 binding sites'},
                   {'pmid': '36737245',
                    'quote': 'a polymorphism (rs12608932) in the UNC13A gene is associated with risk for both ALS and frontotemporal dementia (FTD)'}],
        'modality': 'splicing correction, not small molecule - the lesion is an intronic variant that '
                    'potentiates a cryptic exon; ASOs blocking that exon are the route under study',
        'tractability': 'none - ZERO RCSB entries for Q9UPW8 and no ChEMBL target',
        'unmet_need': 'high - among the strongest common-variant risk loci in ALS',
        'caveat': 'the old panel claimed 5 structures; RCSB holds NONE. Inheritance corrected from "AD, '
                  '<1% fALS": UNC13A is a GWAS risk polymorphism carried by a large fraction of the '
                  'population, not a dominant Mendelian gene, and it acts by modifying TDP-43-dependent '
                  'mis-splicing',
    },
    'SIGMAR1': {
        'indication': 'Autosomal recessive juvenile ALS (ALS16)',
        'uniprot': 'Q99720', 'pdb_ids': ['6DJZ', '6DK1', '5HK1'], 'alphafold_model': 'AF-Q99720-F1',
        'chembl_target': 'CHEMBL287', 'potent_ligands': 3769, 'clinvar_pathogenic': 80,
        'drugs': [{'chembl_id': 'CHEMBL1256818', 'name': 'dextromethorphan'}],
        'trials': [],
        'claims': [{'pmid': '21842496',
                    'quote': 'we describe a consanguineous family segregating juvenile ALS in an autosomal recessive pattern'},
                   {'pmid': '27821430', 'quote': 'a loss of Sig1R function is causative for ALS16'}],
        'modality': 'the ONE target on this panel genuinely suited to small-molecule work - a folded '
                    'membrane receptor with ligand co-crystals and a deep chemical literature; but the '
                    'ALS mechanism is loss of function, so an agonist or chaperone-stabiliser is '
                    'wanted, not an inhibitor',
        'tractability': 'tractable - 5 structures, every one ligand-bound (6DJZ haloperidol, 6DK1 '
                        '(+)-pentazocine, 5HK1 PD144418), and 3769 activities at pChEMBL >= 6',
        'unmet_need': 'moderate - abundant S1R chemistry exists, but essentially none of it was '
                      'developed for or tested in ALS16',
        'caveat': 'the drug cited is NOT an ALS drug: dextromethorphan is a cough suppressant whose '
                  'ChEMBL mechanism happens to be curated against CHEMBL287. It is listed to show that '
                  'S1R has real, verifiable pharmacology, not to imply an ALS indication. The other '
                  'curated mechanisms at this target are pentazocine, carbetapentane and fenfluramine '
                  '- equally unrelated to ALS. Pridopidine, widely described as an S1R agonist and '
                  'trialled in ALS, is NOT citable here: ChEMBL curates its mechanism as a dopamine D2 '
                  'receptor modulator, with no link to Q99720. The old count of 8 overstated a live 5',
    },
}
