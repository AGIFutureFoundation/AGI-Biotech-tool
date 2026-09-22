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
        'description': ('18 targets, each labelled for pediatric relevance. pediatric=True means the gene causes '
                        'disease presenting in infancy, childhood or adolescence; pediatric=False means the target '
                        'is adult-onset or an adult symptomatic drug target and does NOT support a pediatric '
                        'programme. Counts (pdb_count, clinvar_pathogenic) were resolved live on 2026-09-22 via '
                        'server/db_clients.py (RCSB, ClinVar); pdb_count is entries carrying the cited UniProt '
                        'accession, clinvar_pathogenic is the ClinVar count for "<gene>[gene] AND '
                        'clinsig_pathogenic[filter]".'),
        'programs': ['Michael J. Fox Foundation', 'Parkinson\'s Foundation'],
        'targets': [
            # --- recessive juvenile / early-onset parkinsonism (pediatric or adolescent onset) ---
            {'symbol': 'PRKN', 'name': 'E3 ubiquitin-protein ligase parkin', 'inheritance': 'AR',
             'prevalence': 'Commonest recessive early-onset PD; median age at onset ~30 y across PRKN/PINK1/DJ-1 '
                           '(MDSGene, PMID 29644727); 5/136 UK early-onset probands (PMID 22956510)',
             'mechanism': 'E3 ubiquitin ligase, mitophagy', 'pdb_count': 21, 'alphafold': True,
             'uniprot': 'O60260', 'pdb_ids': ['8WZN', '8IK6'], 'chembl_target': None, 'clinvar_pathogenic': 183,
             'pediatric': True,
             'pediatric_note': 'Juvenile/early-onset onset; onset before 21 y reported. No chemical matter: no ChEMBL '
                               'single-protein target, tractability is structure-guided allosteric activation only.',
             'pmids': ['29644727', '22956510'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'PINK1', 'name': 'Serine/threonine-protein kinase PINK1, mitochondrial', 'inheritance': 'AR',
             'prevalence': 'Recessive early-onset PD, rarer than PRKN (1/136 UK early-onset probands, PMID 22956510; '
                           'MDSGene PMID 29644727)',
             'mechanism': 'Mitophagy, mitochondrial quality control', 'pdb_count': 6, 'alphafold': True,
             'uniprot': 'Q9BXM7', 'pdb_ids': ['9KMR', '9KQN'], 'chembl_target': 'CHEMBL3337330',
             'clinvar_pathogenic': 47, 'pediatric': True,
             'pediatric_note': 'Adolescent/young-adult onset; kinase fold with human structures and a ChEMBL target, '
                               'but only 8 activities with pChEMBL - chemical matter is thin.',
             'pmids': ['22956510', '29644727'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'PARK7', 'name': 'Parkinson disease protein 7 (DJ-1)', 'inheritance': 'AR',
             'prevalence': 'Rarest of the three classical recessive early-onset PD genes (MDSGene, PMID 29644727)',
             'mechanism': 'Oxidative stress response, redox-sensitive chaperone', 'pdb_count': 88, 'alphafold': True,
             'uniprot': 'Q99497', 'pdb_ids': ['9K7Q', '9YGX'], 'chembl_target': 'CHEMBL5169188',
             'clinvar_pathogenic': 55, 'pediatric': True,
             'pediatric_note': 'Early-onset (median ~30 y for the recessive group); best-resolved structure of the '
                               'three (88 PDB entries, AlphaFold pLDDT 98).',
             'pmids': ['29644727'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'ATP13A2', 'name': 'Polyamine-transporting ATPase 13A2', 'inheritance': 'AR',
             'prevalence': 'Kufor-Rakeb syndrome; juvenile-onset parkinsonism with pyramidal signs and supranuclear '
                           'gaze palsy (PMID 21542062, 40799219)',
             'mechanism': 'Lysosomal polyamine transport, lysosomal ion homeostasis', 'pdb_count': 25,
             'alphafold': True, 'uniprot': 'Q9NQ11', 'pdb_ids': ['8IEK', '8IEM'], 'chembl_target': None,
             'clinvar_pathogenic': 83, 'pediatric': True,
             'pediatric_note': 'Teenage onset is the defining feature of Kufor-Rakeb. Cryo-EM structures exist; no '
                               'ChEMBL target, so no small-molecule starting points.',
             'pmids': ['21542062', '40799219'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'DNAJC6', 'name': 'Auxilin', 'inheritance': 'AR',
             'prevalence': 'Juvenile parkinsonism-dystonia; 6 patients with homozygous nonsense variants in a cohort '
                           'of 25 children with juvenile parkinsonism (PMID 32472658)',
             'mechanism': 'Clathrin uncoating co-chaperone; synaptic vesicle recycling', 'pdb_count': 0,
             'alphafold': True, 'uniprot': 'O75061', 'pdb_ids': [], 'chembl_target': None, 'clinvar_pathogenic': 30,
             'pediatric': True,
             'pediatric_note': 'Onset in infancy/childhood with neurodevelopmental delay. Least tractable target here: '
                               'zero experimental structures for O75061 and AlphaFold mean pLDDT 62.9. Gene therapy, '
                               'not small molecules, is the stated route (PMID 38242634).',
             'pmids': ['32472658', '38242634'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'SYNJ1', 'name': 'Polyphosphatidylinositol phosphatase synaptojanin-1', 'inheritance': 'AR',
             'prevalence': 'PARK20; homozygous Arg258Gln families with early-onset parkinsonism (PMID 24816432, '
                           '29515184)',
             'mechanism': 'Synaptic phosphoinositide phosphatase; endosomal trafficking', 'pdb_count': 5,
             'alphafold': True, 'uniprot': 'O43426', 'pdb_ids': ['7A0V', '2VJ0'], 'chembl_target': 'CHEMBL4523136',
             'clinvar_pathogenic': 103, 'pediatric': True,
             'pediatric_note': 'Juvenile to young-adult onset; phenotype spans atypical juvenile parkinsonism with '
                               'seizures. Only partial-domain structures and 2 pChEMBL activities.',
             'pmids': ['24816432', '29515184'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'FBXO7', 'name': 'F-box only protein 7', 'inheritance': 'AR',
             'prevalence': 'PARK15 parkinsonian-pyramidal syndrome, juvenile onset (PMID 23318512, 30454685)',
             'mechanism': 'SCF E3 ligase substrate receptor; proteasome and mitophagy regulation', 'pdb_count': 2,
             'alphafold': True, 'uniprot': 'Q9Y3I1', 'pdb_ids': ['4L9C', '4L9H'], 'chembl_target': None,
             'clinvar_pathogenic': 57, 'pediatric': True,
             'pediatric_note': 'Juvenile onset. Two domain structures only, no ChEMBL target; tractability is poor.',
             'pmids': ['23318512', '30454685'], 'nct_ids': [], 'verified': '2026-09-22'},
            # --- treatable dopamine-synthesis / handling disorders presenting in infancy ---
            {'symbol': 'TH', 'name': 'Tyrosine 3-monooxygenase (tyrosine hydroxylase)', 'inheritance': 'AR',
             'prevalence': 'TH deficiency: infantile hypokinetic-rigid parkinsonism / dopa-responsive dystonia '
                           '(PMID 20301610, 11134401)',
             'mechanism': 'Rate-limiting step of dopamine synthesis', 'pdb_count': 7, 'alphafold': True,
             'uniprot': 'P07101', 'pdb_ids': ['7PIM', '6ZN2'], 'chembl_target': 'CHEMBL1969',
             'clinvar_pathogenic': 112, 'pediatric': True,
             'pediatric_note': 'Presents in infancy and is treatable with L-dopa; the severe form is dopa-refractory '
                               '(PMID 12891655), which is the unmet need. Approved chemistry targets the enzyme only '
                               'as an inhibitor (metyrosine, CHEMBL1200862); stabilisers/chaperones are the gap.',
             'pmids': ['20301610', '11134401', '12891655'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'DDC', 'name': 'Aromatic-L-amino-acid decarboxylase (AADC)', 'inheritance': 'AR',
             'prevalence': 'AADC deficiency: infantile hypotonia, oculogyric crises, dopamine/serotonin deficiency '
                           '(PMID 37824694)',
             'mechanism': 'PLP-dependent decarboxylation of L-dopa to dopamine', 'pdb_count': 8, 'alphafold': True,
             'uniprot': 'P20711', 'pdb_ids': ['9GNS', '9HRH'], 'chembl_target': 'CHEMBL1843',
             'clinvar_pathogenic': 81, 'pediatric': True,
             'pediatric_note': 'The strongest pediatric precedent in this panel: eladocagene exuparvovec '
                               '(CHEMBL4298189) is an approved intraputaminal gene therapy for children, with active '
                               'delivery studies (NCT04903288, PMID 41212308).',
             'pmids': ['37824694', '41212308'], 'nct_ids': ['NCT04903288'], 'verified': '2026-09-22'},
            {'symbol': 'GCH1', 'name': 'GTP cyclohydrolase 1', 'inheritance': 'AD (Segawa DRD); AR (BH4 deficiency)',
             'prevalence': 'Dopa-responsive dystonia with diurnal fluctuation, childhood onset (PMID 20301681, '
                           '26100751, 21094587)',
             'mechanism': 'First and rate-limiting step of tetrahydrobiopterin (BH4) synthesis, the TH cofactor',
             'pdb_count': 11, 'alphafold': True, 'uniprot': 'P30793', 'pdb_ids': ['7ALQ', '7ALA'],
             'chembl_target': None, 'clinvar_pathogenic': 114, 'pediatric': True,
             'pediatric_note': 'Childhood-onset and highly treatable; BH4 replacement is trialled in children with '
                               'BH4 deficiencies (NCT00355264, NCT03519711). Cofactor replacement, not GCH1 '
                               'inhibition, is the therapeutic route - no ChEMBL target for P30793.',
             'pmids': ['20301681', '26100751', '21094587'], 'nct_ids': ['NCT00355264', 'NCT03519711'],
             'verified': '2026-09-22'},
            {'symbol': 'SLC6A3', 'name': 'Sodium-dependent dopamine transporter (DAT)', 'inheritance': 'AR',
             'prevalence': 'Dopamine transporter deficiency syndrome (DTDS): infantile parkinsonism-dystonia; ~31 '
                           'published cases as of 2023 (PMID 37443770)',
             'mechanism': 'Presynaptic dopamine reuptake; loss of function causes misfolding and surface loss',
             'pdb_count': 17, 'alphafold': True, 'uniprot': 'Q01959', 'pdb_ids': ['9JKH', '9JKJ'],
             'chembl_target': 'CHEMBL238', 'clinvar_pathogenic': 144, 'pediatric': True,
             'pediatric_note': 'Presents in infancy. Most tractable pediatric target here: human DAT structures plus '
                               '5298 pChEMBL activities, and pharmacochaperone rescue of mutant DAT is an active '
                               'approach (PMID 37443770, 35614973).',
             'pmids': ['37443770', '35614973', '32077500'], 'nct_ids': [], 'verified': '2026-09-22'},
            # --- lysosomal: pediatric disease is Gaucher, NOT pediatric Parkinson's ---
            {'symbol': 'GBA1', 'name': 'Lysosomal acid glucosylceramidase',
             'inheritance': 'AR (Gaucher disease); heterozygous carriage is an adult PD risk factor',
             'prevalence': 'Neuronopathic Gaucher disease types 2/3 present in infancy and childhood (PMID 40542647); '
                           'PD risk in heterozygotes is adult-onset',
             'mechanism': 'Lysosomal glucosylceramide hydrolysis; loss of function drives α-synuclein accumulation',
             'pdb_count': 58, 'alphafold': True, 'uniprot': 'P04062', 'pdb_ids': ['9ENA', '9FJF'],
             'chembl_target': 'CHEMBL2179', 'clinvar_pathogenic': 152, 'pediatric': True,
             'pediatric_note': 'Pediatric ONLY as Gaucher disease, not as pediatric Parkinson\'s. Children with type '
                               '2/3 GD are the trial population (high-dose ambroxol NCT07285369, eliglustat '
                               'NCT03519646). Well-structured with 1919 pChEMBL activities and a Ph2 chaperone '
                               '(afegostat, CHEMBL206468).',
             'pmids': ['40542647', '39116528'], 'nct_ids': ['NCT07285369', 'NCT03519646'], 'verified': '2026-09-22'},
            # --- adult-onset genetic PD: NOT pediatric ---
            {'symbol': 'SNCA', 'name': 'Alpha-synuclein', 'inheritance': 'AD (missense and locus multiplication)',
             'prevalence': 'Rare cause of dominant PD; median age at onset ~49 y for SNCA/LRRK2/VPS35 combined '
                           '(MDSGene, PMID 30357936)',
             'mechanism': 'Protein aggregation, neuroinflammation', 'pdb_count': 249, 'alphafold': True,
             'uniprot': 'P37840', 'pdb_ids': ['34AF', '34AH'], 'chembl_target': 'CHEMBL6152',
             'clinvar_pathogenic': 35, 'pediatric': False,
             'pediatric_note': 'ADULT-ONSET. Do not count towards a pediatric programme. Clinical assets '
                               '(prasinezumab CHEMBL4298077, Ph3; cinpanemab CHEMBL3833330) were tested in adults '
                               '(PMID 35921451).',
             'pmids': ['30357936', '35921451'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'LRRK2', 'name': 'Leucine-rich repeat serine/threonine-protein kinase 2', 'inheritance': 'AD',
             'prevalence': 'G2019S is the commonest known cause of familial and sporadic PD; frequency varies by '
                           'population from 0 to 35.7% sporadic / 42% familial in North-African Arab cohorts '
                           '(systematic review, PMID 19945904)',
             'mechanism': 'Kinase signalling, lysosomal and mitochondrial dysfunction', 'pdb_count': 58,
             'alphafold': True, 'uniprot': 'Q5S007', 'pdb_ids': ['9Y7A', '9YBL'], 'chembl_target': 'CHEMBL1075104',
             'clinvar_pathogenic': 15, 'pediatric': False,
             'pediatric_note': 'ADULT-ONSET (MDSGene median ~49 y, PMID 30357936). Richest chemistry in the panel '
                               '(5682 pChEMBL activities) but no pediatric indication.',
             'pmids': ['19945904', '30357936'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'VPS35', 'name': 'Vacuolar protein sorting-associated protein 35', 'inheritance': 'AD',
             'prevalence': 'Rare dominant PD (D620N); part of the MDSGene dominant series, median onset ~49 y '
                           '(PMID 30357936)',
             'mechanism': 'Retromer function, endosomal sorting', 'pdb_count': 14, 'alphafold': True,
             'uniprot': 'Q96QK1', 'pdb_ids': ['9Q8M', '8R02'], 'chembl_target': 'CHEMBL2216744',
             'clinvar_pathogenic': 14, 'pediatric': False,
             'pediatric_note': 'ADULT-ONSET. No pediatric phenotype found; 6 pChEMBL activities only.',
             'pmids': ['30357936'], 'nct_ids': [], 'verified': '2026-09-22'},
            # --- symptomatic drug targets, adult practice ---
            {'symbol': 'MAOB', 'name': 'Amine oxidase [flavin-containing] B',
             'inheritance': 'N/A - not a Mendelian PD gene (X-linked locus)',
             'prevalence': 'Symptomatic drug target, adult PD (selegiline CHEMBL972, approved)',
             'mechanism': 'Dopamine catabolism, ROS generation', 'pdb_count': 57, 'alphafold': True,
             'uniprot': 'P27338', 'pdb_ids': ['9R2J', '9R3J'], 'chembl_target': 'CHEMBL2039',
             'clinvar_pathogenic': 147, 'pediatric': False,
             'pediatric_note': 'ADULT symptomatic therapy. The previous entry called this an X-linked PD risk locus; '
                               'no such Mendelian inheritance is supported. ClinVar hits for MAOB largely reflect '
                               'contiguous Xp11 deletions, not PD alleles.',
             'pmids': ['35107654'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'COMT', 'name': 'Catechol O-methyltransferase', 'inheritance': 'N/A - drug target',
             'prevalence': 'Adjunct drug target in adult PD (entacapone CHEMBL953, opicapone CHEMBL1089318, approved)',
             'mechanism': 'Peripheral L-dopa/dopamine O-methylation', 'pdb_count': 12, 'alphafold': True,
             'uniprot': 'P21964', 'pdb_ids': ['6I3C', '5LSA'], 'chembl_target': 'CHEMBL2023',
             'clinvar_pathogenic': 379, 'pediatric': False,
             'pediatric_note': 'ADULT symptomatic adjunct. Previously labelled a PD "risk locus"; the Val158Met '
                               'association is a modifier at best and is not a PD cause. ClinVar counts here are '
                               'dominated by 22q11.2 deletions spanning COMT.',
             'pmids': ['35217995'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'DRD2', 'name': 'Dopamine receptor D2', 'inheritance': 'N/A - drug target',
             'prevalence': 'Symptomatic drug target, adult PD (rotigotine CHEMBL1303 and other approved agonists)',
             'mechanism': 'Postsynaptic dopamine signalling', 'pdb_count': 11, 'alphafold': True,
             'uniprot': 'P14416', 'pdb_ids': ['9BS9', '8TZQ'], 'chembl_target': 'CHEMBL217',
             'clinvar_pathogenic': 16, 'pediatric': False,
             'pediatric_note': 'ADULT symptomatic therapy; 15078 pChEMBL activities but no pediatric parkinsonism '
                               'indication.',
             'pmids': ['37396766'], 'nct_ids': [], 'verified': '2026-09-22'},
        ]
    },
    'Shriners': {
        'name': 'Shriners Children\'s Research',
        'description': ('15 targets in the pediatric orthopaedic and cleft scope: osteogenesis imperfecta, skeletal '
                        'dysplasia, metabolic bone disease, heterotopic ossification, hereditary osteochondromas and '
                        'cleft lip/palate. Every entry cites a re-resolvable UniProt accession, live PDB/ClinVar '
                        'counts (RCSB, ClinVar via server/db_clients.py, 2026-09-22) and at least one PubMed or '
                        'ClinicalTrials.gov record; pediatric=True means children are the treated or trial '
                        'population. No verified molecular target is carried for burns/scar or spinal cord injury - '
                        'see the removed-target note in the repo history rather than assuming coverage.'),
        'programs': ['Shriners Children\'s'],
        'targets': [
            # --- osteogenesis imperfecta: collagen I and its folding machinery ---
            {'symbol': 'COL1A1', 'name': 'Collagen alpha-1(I) chain', 'inheritance': 'AD',
             'prevalence': 'Classical dominant OI; defects in type I collagen are the classical cause of OI '
                           '(PMID 34007986). 1200 pathogenic ClinVar records',
             'mechanism': 'Type I collagen alpha-1 chain; structural protein of bone matrix', 'pdb_count': 14,
             'alphafold': True, 'uniprot': 'P02452', 'pdb_ids': ['8YV3', '5K31'], 'chembl_target': 'CHEMBL3030',
             'clinvar_pathogenic': 1200, 'pediatric': True,
             'pediatric_note': 'Fractures from infancy; children are the treated population (setrusumab and '
                               'romosozumab pediatric Ph3, NCT05768854, NCT05972551). Not directly druggable: the '
                               'triple helix has no pocket (AlphaFold mean pLDDT 52.7) - therapy acts downstream on '
                               'bone turnover. Caveat on pdb_count: of the 14 RCSB entries carrying P02452 most are '
                               'short synthetic collagen peptides or fusion constructs (e.g. the collagen '
                               'trimerisation tag in 7E7B); only 5K31 (procollagen I C-propeptide) and 8YV3 are '
                               'structures of the protein itself.',
             'pmids': ['34007986'], 'nct_ids': ['NCT05768854'], 'verified': '2026-09-22'},
            {'symbol': 'COL1A2', 'name': 'Collagen alpha-2(I) chain', 'inheritance': 'AD',
             'prevalence': 'Classical dominant OI, second type I collagen chain (PMID 34007986). 536 pathogenic '
                           'ClinVar records',
             'mechanism': 'Type I collagen alpha-2 chain; structural protein of bone matrix', 'pdb_count': 5,
             'alphafold': True, 'uniprot': 'P08123', 'pdb_ids': ['8YV3'], 'chembl_target': 'CHEMBL2685',
             'clinvar_pathogenic': 536, 'pediatric': True,
             'pediatric_note': 'As COL1A1: pediatric disease, no direct chemical tractability (0 pChEMBL activities). '
                               'Caveat on pdb_count: 8YV3 is the only entry of the 5 carrying P08123 that is a type I '
                               'collagen structure; the others are guest peptides in type II/IX collagen scaffolds.',
             'pmids': ['34007986'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'SERPINF1', 'name': 'Pigment epithelium-derived factor (PEDF)', 'inheritance': 'AR',
             'prevalence': 'OI type VI, recessive, with mineralisation defect (PMID 27796462, 34007986). 117 '
                           'pathogenic ClinVar records',
             'mechanism': 'Secreted serpin required for normal bone mineralisation', 'pdb_count': 3, 'alphafold': True,
             'uniprot': 'P36955', 'pdb_ids': ['9J3P', '1IMV'], 'chembl_target': 'CHEMBL4295753',
             'clinvar_pathogenic': 117, 'pediatric': True,
             'pediatric_note': 'OI type VI children respond poorly to bisphosphonates; denosumab was used in children '
                               'with OI VI specifically (PMID 22947550, 25257953). Protein-replacement rather than '
                               'small-molecule logic: 0 pChEMBL activities.',
             'pmids': ['27796462', '22947550', '25257953'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'CRTAP', 'name': 'Cartilage-associated protein', 'inheritance': 'AR',
             'prevalence': 'Recessive OI (collagen prolyl 3-hydroxylation complex) (PMID 34007986). 81 pathogenic '
                           'ClinVar records',
             'mechanism': 'Component of the CRTAP/P3H1/PPIB collagen prolyl 3-hydroxylation complex', 'pdb_count': 6,
             'alphafold': True, 'uniprot': 'O75718', 'pdb_ids': ['8K0E', '8K0I'], 'chembl_target': None,
             'clinvar_pathogenic': 81, 'pediatric': True,
             'pediatric_note': 'Severe recessive OI presenting perinatally. Cryo-EM structures of the complex exist '
                               '(8K0E), but there is no ChEMBL target and no chemical matter - included as a '
                               'structural-biology entry, not a screening target.',
             'pmids': ['34007986'], 'nct_ids': [], 'verified': '2026-09-22'},
            {'symbol': 'P3H1', 'name': 'Prolyl 3-hydroxylase 1', 'inheritance': 'AR',
             'prevalence': 'Recessive OI, partner of CRTAP (PMID 34007986). 111 pathogenic ClinVar records',
             'mechanism': '2-oxoglutarate-dependent collagen prolyl 3-hydroxylase', 'pdb_count': 6, 'alphafold': True,
             'uniprot': 'Q32P28', 'pdb_ids': ['8K0E', '8K0F'], 'chembl_target': None, 'clinvar_pathogenic': 111,
             'pediatric': True,
             'pediatric_note': 'Severe recessive OI. The only enzyme in the complex, so the most plausible chemistry '
                               'entry point of the three, but no ChEMBL target exists today.',
             'pmids': ['34007986'], 'nct_ids': [], 'verified': '2026-09-22'},
            # --- bone-turnover targets with pediatric trials ---
            {'symbol': 'SOST', 'name': 'Sclerostin', 'inheritance': 'AR (sclerosteosis, loss of function)',
             'prevalence': 'Human genetics of high bone mass; now the lead pharmacological target in pediatric OI',
             'mechanism': 'Osteocyte-secreted Wnt antagonist; inhibition increases bone formation', 'pdb_count': 3,
             'alphafold': True, 'uniprot': 'Q9BQB4', 'pdb_ids': ['6L6R', '3SOV'], 'chembl_target': 'CHEMBL3580487',
             'clinvar_pathogenic': 14, 'pediatric': True,
             'pediatric_note': 'Strongest pediatric evidence in the panel: setrusumab (CHEMBL4297918) Ph3 in children '
                               'with OI (NCT05768854, NCT05125809, NCT06636071) and romosozumab (CHEMBL2107874, '
                               'approved) Ph3 in children (NCT05972551), after the adult Ph2a (PMID 28370407). '
                               'Inheritance corrected from AD/AR: sclerosteosis is recessive.',
             'pmids': ['28370407'], 'nct_ids': ['NCT05125809', 'NCT05768854', 'NCT05972551'],
             'verified': '2026-09-22'},
            {'symbol': 'TNFSF11', 'name': 'TNF ligand superfamily member 11 (RANKL)', 'inheritance': 'N/A - drug target',
             'prevalence': 'Osteoclast-driven bone loss; denosumab (CHEMBL1237023) is approved and used off-label in '
                           'pediatric bone disease (PMID 28643220, 37035391)',
             'mechanism': 'Osteoclast differentiation and survival', 'pdb_count': 2, 'alphafold': True,
             'uniprot': 'O14788', 'pdb_ids': ['5BNQ', '3URF'], 'chembl_target': 'CHEMBL2364162',
             'clinvar_pathogenic': 53, 'pediatric': True,
             'pediatric_note': 'Pediatric OI trials exist but are cautionary: NCT01799798 (Ph2, children) completed '
                               'while NCT02352753 and NCT03638128 were terminated, and rebound hypercalcaemia is the '
                               'known pediatric risk (PMID 37401056).',
             'pmids': ['25257953', '37401056', '28643220'], 'nct_ids': ['NCT01799798', 'NCT02352753'],
             'verified': '2026-09-22'},
            # --- growth-plate skeletal dysplasia ---
            {'symbol': 'FGFR3', 'name': 'Fibroblast growth factor receptor 3', 'inheritance': 'AD (gain of function)',
             'prevalence': 'Achondroplasia (recurrent G380R) and hypochondroplasia (PMID 20301331, 20301650)',
             'mechanism': 'Constitutive growth-plate FGFR3 signalling suppresses chondrocyte proliferation',
             'pdb_count': 16, 'alphafold': True, 'uniprot': 'P22607', 'pdb_ids': ['9EKO', '9VMB'],
             'chembl_target': 'CHEMBL2742', 'clinvar_pathogenic': 194, 'pediatric': True,
             'pediatric_note': 'Pediatric by definition and chemically the most tractable skeletal target here (3966 '
                               'pChEMBL activities). Low-dose infigratinib (CHEMBL1834657) ran Ph2 and Ph3 in '
                               'children (NCT04265651, NCT06164951) with an under-3 study open (NCT07169279).',
             'pmids': ['20301331', '20301650'], 'nct_ids': ['NCT04265651', 'NCT06164951'], 'verified': '2026-09-22'},
            {'symbol': 'NPR2', 'name': 'Atrial natriuretic peptide receptor 2 (NPR-B)',
             'inheritance': 'AR (acromesomelic dysplasia Maroteaux type); heterozygotes have short stature',
             'prevalence': 'Biallelic NPR2 causes acromesomelic dysplasia (PMID 34162036); heterozygous variants '
                           'cause progressive short stature (PMID 32720985)',
             'mechanism': 'CNP receptor; cGMP signalling that antagonises FGFR3 in the growth plate', 'pdb_count': 0,
             'alphafold': True, 'uniprot': 'P20594', 'pdb_ids': [], 'chembl_target': 'CHEMBL1795',
             'clinvar_pathogenic': 131, 'pediatric': True,
             'pediatric_note': 'The receptor for vosoritide (CHEMBL3707276, approved), which was established in '
                               'children with achondroplasia (Ph3 PMID 32891212; infants/young children '
                               'NCT03583697, PMID 37984383). Corrected: there are zero experimental structures for '
                               'P20594 (previous entry claimed 15), and the ligand is a peptide, not a small '
                               'molecule (0 pChEMBL activities).',
             'pmids': ['32891212', '37984383', '34162036', '32720985'],
             'nct_ids': ['NCT02055157', 'NCT03583697'], 'verified': '2026-09-22'},
            # --- metabolic bone disease ---
            {'symbol': 'ALPL', 'name': 'Alkaline phosphatase, tissue-nonspecific isozyme',
             'inheritance': 'AR in perinatal/infantile hypophosphatasia; AD in milder childhood and adult forms',
             'prevalence': 'Hypophosphatasia: rickets, premature tooth loss, pyridoxine-responsive seizures in '
                           'infants (PMID 26893260, 20301329). 333 pathogenic ClinVar records',
             'mechanism': 'Cell-surface phosphohydrolase; loss of function leaves inorganic pyrophosphate to block '
                          'mineralisation', 'pdb_count': 5, 'alphafold': True, 'uniprot': 'P05186',
             'pdb_ids': ['9SH5', '7YIX'], 'chembl_target': 'CHEMBL5979', 'clinvar_pathogenic': 333, 'pediatric': True,
             'pediatric_note': 'Enzyme replacement (asfotase alfa) was established in infants and children '
                               '(NCT01176266, <=5 years), with a next-generation enzyme in Ph3 (NCT06079281). '
                               'Inheritance corrected from AR-only. 1138 pChEMBL activities exist but are mostly '
                               'inhibitors - the therapeutic direction is replacement.',
             'pmids': ['26893260', '20301329', '28888853'], 'nct_ids': ['NCT01176266', 'NCT06079281'],
             'verified': '2026-09-22'},
            {'symbol': 'FGF23', 'name': 'Fibroblast growth factor 23',
             'inheritance': 'AD gain-of-function causes autosomal dominant hypophosphataemic rickets; in XLH FGF23 is '
                            'elevated secondary to PHEX loss, not mutated',
             'prevalence': 'Therapeutic target in X-linked hypophosphataemia and ADHR (PMID 31104833, 22319799)',
             'mechanism': 'Phosphaturic hormone; excess causes renal phosphate wasting and rickets', 'pdb_count': 6,
             'alphafold': True, 'uniprot': 'Q9GZV9', 'pdb_ids': ['7YSW', '7YSU'], 'chembl_target': 'CHEMBL3713913',
             'clinvar_pathogenic': 64, 'pediatric': True,
             'pediatric_note': 'Burosumab (CHEMBL3707326, approved) beat conventional therapy in children aged 1-12 '
                               'with XLH (Ph3 NCT03233126, PMID 31104833) and was studied from age 1 (NCT02750618). '
                               'Corrected: the previous entry attributed X-linked hypophosphataemia to FGF23; the '
                               'XLH gene is PHEX.',
             'pmids': ['31104833', '22319799'], 'nct_ids': ['NCT03233126', 'NCT02750618'], 'verified': '2026-09-22'},
            {'symbol': 'PHEX', 'name': 'Phosphate-regulating neutral endopeptidase PHEX', 'inheritance': 'XD',
             'prevalence': 'X-linked hypophosphataemia, the commonest inherited rickets (PMID 22319799, 39814982). '
                           '987 pathogenic ClinVar records',
             'mechanism': 'Endopeptidase whose loss raises circulating FGF23', 'pdb_count': 0, 'alphafold': True,
             'uniprot': 'P78562', 'pdb_ids': [], 'chembl_target': None, 'clinvar_pathogenic': 987, 'pediatric': True,
             'pediatric_note': 'Pediatric diagnosis (rickets, bowing, growth impairment). Corrected: zero '
                               'experimental structures for P78562 (previous entry claimed 10) and no ChEMBL target; '
                               'the tractable node is FGF23 downstream, which is why burosumab exists and PHEX '
                               'itself has no direct programme.',
             'pmids': ['22319799', '39814982'], 'nct_ids': ['NCT03233126'], 'verified': '2026-09-22'},
            # --- heterotopic ossification and osteochondromas ---
            {'symbol': 'ACVR1', 'name': 'Activin receptor type-1 (ALK2)', 'inheritance': 'AD (recurrent R206H)',
             'prevalence': 'Fibrodysplasia ossificans progressiva; ultra-rare, disabling progressive heterotopic '
                           'ossification (PMID 32525643, 36583535)',
             'mechanism': 'Mutant ALK2 gains responsiveness to activin A, driving BMP signalling and heterotopic bone',
             'pdb_count': 85, 'alphafold': True, 'uniprot': 'Q04771', 'pdb_ids': ['9RDA', '9L04'],
             'chembl_target': 'CHEMBL5903', 'clinvar_pathogenic': 23, 'pediatric': True,
             'pediatric_note': 'New target. FOP flare-ups begin in the first decade; the Ph3 MOVE trial dosed '
                               'patients from age 4 (NCT03312634, PMID 36583535) with a pediatric rollover '
                               '(NCT05027802) and a garetosmab study in children (NCT07559513). Genuinely tractable: '
                               '85 PDB entries and 1857 pChEMBL activities on the kinase domain, though approved '
                               'ALK2 inhibitors so far are oncology JAK-family drugs, not FOP drugs.',
             'pmids': ['32525643', '36583535', '26896819'],
             'nct_ids': ['NCT03312634', 'NCT05027802', 'NCT07559513'], 'verified': '2026-09-22'},
            {'symbol': 'EXT1', 'name': 'Exostosin-1', 'inheritance': 'AD',
             'prevalence': 'Hereditary multiple osteochondromas, prevalence ~1:50,000; osteochondromas develop and '
                           'grow through the first decade (PMID 18271966, 20301413). 564 pathogenic ClinVar records',
             'mechanism': 'Heparan sulfate co-polymerase; loss of function deregulates growth-plate chondrocytes',
             'pdb_count': 6, 'alphafold': True, 'uniprot': 'Q16394', 'pdb_ids': ['7ZAY', '7SCH'],
             'chembl_target': None, 'clinvar_pathogenic': 564, 'pediatric': True,
             'pediatric_note': 'New target, and squarely pediatric orthopaedic surgical burden (forearm deformity, '
                               'repeat resections; NCT07556874 catalogues the surgery). Honest tractability caveat: '
                               'EXT1/EXT2 structures exist but there is no ChEMBL target and no chemical matter, so '
                               'this is an unmet-need entry, not a ready screening target.',
             'pmids': ['18271966', '20301413'], 'nct_ids': ['NCT07556874'], 'verified': '2026-09-22'},
            # --- craniofacial ---
            {'symbol': 'IRF6', 'name': 'Interferon regulatory factor 6', 'inheritance': 'AD',
             'prevalence': 'Van der Woude syndrome, the commonest syndromic form of cleft lip/palate (PMID 32558391). '
                           '109 pathogenic ClinVar records',
             'mechanism': 'Transcription factor governing periderm and palatal epithelial differentiation',
             'pdb_count': 0, 'alphafold': True, 'uniprot': 'O14896', 'pdb_ids': [], 'chembl_target': None,
             'clinvar_pathogenic': 109, 'pediatric': True,
             'pediatric_note': 'Pediatric by definition; surgical care, not pharmacology, is the standard of care '
                               '(cleft trials in the panel scope are surgical/speech, e.g. NCT06284434). Corrected: '
                               'zero experimental structures for O14896 (previous entry claimed 8) and no ChEMBL '
                               'target - a transcription factor with no tractable chemistry today.',
             'pmids': ['32558391'], 'nct_ids': [], 'verified': '2026-09-22'},
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
