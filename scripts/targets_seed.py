"""Curated high-value targets for the AGI BioXR workspace.

Every row is checked against the live UniProt API by build_targets.py; a row whose
gene symbol does not match its accession is dropped and reported, never guessed.

Columns: symbol, uniprot accession, program, disease focus, why it matters.
"""

SEED = [
    # ---------------- ALS / motor neuron disease ----------------
    ("SOD1", "P00441", "ALS", "Familial ALS (ALS1)", "Toxic gain-of-function misfolding; tofersen (ASO) approved for SOD1-ALS."),
    ("TARDBP", "Q13148", "ALS", "ALS / FTD (TDP-43 proteinopathy)", "TDP-43 aggregates in ~97% of ALS cases; RRM domains are druggable RNA-binding surfaces."),
    ("FUS", "P35637", "ALS", "Juvenile / familial ALS (ALS6)", "Phase-separation driver; mutations cause aggressive juvenile ALS."),
    ("C9orf72", "Q96LT7", "ALS", "C9-ALS / FTD", "Most common genetic cause of ALS; G4C2 repeat expansion and DPR toxicity."),
    ("TBK1", "Q9UHD2", "ALS", "ALS / FTD", "Kinase in autophagy and innate immunity; haploinsufficiency causes ALS."),
    ("OPTN", "Q96CV9", "ALS", "ALS12", "Autophagy receptor partnering TBK1 in mitophagy."),
    ("VCP", "P55072", "ALS", "ALS14 / IBMPFD", "AAA+ ATPase (p97) with multiple small-molecule inhibitor series."),
    ("SQSTM1", "Q13501", "ALS", "ALS / FTD", "p62 autophagy adaptor; clears ubiquitinated aggregates."),
    ("UBQLN2", "Q9UHD9", "ALS", "X-linked ALS15", "Proteasome shuttle factor; mutations impair proteostasis."),
    ("PFN1", "P07737", "ALS", "ALS18", "Actin-binding protein; mutant forms aggregate."),
    ("KIF5A", "Q12840", "ALS", "ALS25", "Axonal transport kinesin; C-terminal splice mutations."),
    ("NEK1", "Q96PY6", "ALS", "ALS24", "Kinase in DNA damage response and cilia."),
    ("ATXN2", "Q99700", "ALS", "ALS13 risk", "Intermediate polyQ expansions raise ALS risk; ASO lowering in trials."),
    ("MATR3", "P43243", "ALS", "ALS21", "Nuclear matrix RNA-binding protein."),
    ("HNRNPA1", "P09651", "ALS", "ALS20 / multisystem proteinopathy", "Prion-like domain mutations drive fibrillization."),
    ("CHCHD10", "Q8WYQ3", "ALS", "FTD-ALS2", "Mitochondrial cristae protein."),
    ("ANG", "P03950", "ALS", "ALS9", "Angiogenin RNase; loss-of-function variants."),
    ("STMN2", "Q93045", "ALS", "TDP-43 loss-of-function readout", "Cryptic-exon target of TDP-43; restoring STMN2 is an active therapeutic strategy."),
    ("UNC13A", "Q9UPW8", "ALS", "ALS / FTD risk", "Synaptic protein mis-spliced when TDP-43 is lost."),
    ("SIGMAR1", "Q99720", "ALS", "ALS16 / juvenile ALS", "ER chaperone receptor with many small-molecule ligands."),
    # ---------------- Parkinson's disease ----------------
    ("SNCA", "P37840", "Parkinson's", "PD / Lewy body dementia", "Alpha-synuclein aggregation is the hallmark of PD."),
    ("LRRK2", "Q5S007", "Parkinson's", "PARK8 familial and sporadic PD", "Kinase; G2019S gain of function; clinical-stage inhibitors."),
    ("GBA1", "P04062", "Parkinson's", "GBA-PD / Gaucher", "Glucocerebrosidase; strongest common genetic PD risk factor; chaperone targets."),
    ("PINK1", "Q9BXM7", "Parkinson's", "PARK6 early-onset PD", "Mitophagy kinase; activators under development."),
    ("PRKN", "O60260", "Parkinson's", "PARK2 early-onset PD", "E3 ubiquitin ligase in mitophagy; activator programs."),
    ("PARK7", "Q99497", "Parkinson's", "PARK7 early-onset PD", "DJ-1 oxidative-stress sensor."),
    ("VPS35", "Q96QK1", "Parkinson's", "PARK17", "Retromer core; D620N stabilization strategies."),
    ("MAOB", "P27338", "Parkinson's", "Symptomatic PD therapy", "Approved target: selegiline, rasagiline, safinamide."),
    ("COMT", "P21964", "Parkinson's", "Symptomatic PD therapy", "Approved target: entacapone, opicapone, tolcapone."),
    ("DRD2", "P14416", "Parkinson's", "Symptomatic PD therapy", "Dopamine agonists: pramipexole, ropinirole."),
    ("TH", "P07101", "Parkinson's", "Dopamine synthesis", "Rate-limiting enzyme in dopamine biosynthesis."),
    ("UCHL1", "P09936", "Parkinson's", "PARK5", "Deubiquitinase in neuronal proteostasis."),
    ("ATP13A2", "Q9NQ11", "Parkinson's", "PARK9 Kufor-Rakeb", "Lysosomal polyamine transporter."),
    # ---------------- Other neurogenetic disorders ----------------
    ("HTT", "P42858", "Neurogenetic", "Huntington's disease", "PolyQ expansion; lowering and splicing modulators."),
    ("SMN1", "Q16637", "Neurogenetic", "Spinal muscular atrophy", "Nusinersen, risdiplam, onasemnogene all act on SMN."),
    ("FXN", "Q16595", "Neurogenetic", "Friedreich's ataxia", "Frataxin deficiency; omaveloxolone approved."),
    ("MECP2", "P51608", "Neurogenetic", "Rett syndrome", "Trofinetide approved; gene therapies in trials."),
    ("MAPT", "P10636", "Neurogenetic", "FTD / tauopathies / PD risk", "Tau aggregation; ASO and antibody programs."),
    ("APP", "P05067", "Neurogenetic", "Alzheimer's disease", "Amyloid precursor; antibody therapies approved."),
    ("BACE1", "P56817", "Neurogenetic", "Alzheimer's disease", "Protease with deep small-molecule SAR history."),
    ("PSEN1", "P49768", "Neurogenetic", "Early-onset Alzheimer's", "Gamma-secretase catalytic subunit."),
    ("ATXN3", "P54252", "Neurogenetic", "Spinocerebellar ataxia 3", "PolyQ deubiquitinase."),
    ("DMD", "P11532", "Neurogenetic", "Duchenne muscular dystrophy", "Exon-skipping ASOs and micro-dystrophin gene therapy."),
    # ---------------- Shriners Children's focus areas ----------------
    ("COL1A1", "P02452", "Shriners Children's", "Osteogenesis imperfecta", "Type I collagen alpha-1; majority of OI cases."),
    ("COL1A2", "P08123", "Shriners Children's", "Osteogenesis imperfecta", "Type I collagen alpha-2."),
    ("SOST", "Q9BQB4", "Shriners Children's", "Osteogenesis imperfecta / bone mass", "Sclerostin; setrusumab in OI trials, romosozumab approved."),
    ("TNFSF11", "O14788", "Shriners Children's", "Bone resorption / OI", "RANKL; denosumab target."),
    ("FGFR3", "P22607", "Shriners Children's", "Achondroplasia", "Gain-of-function FGFR3; infigratinib in trials."),
    ("NPR2", "P20594", "Shriners Children's", "Achondroplasia / short stature", "Vosoritide acts through NPR2 signaling."),
    ("ALPL", "P05186", "Shriners Children's", "Hypophosphatasia", "Asfotase alfa enzyme replacement."),
    ("FGF23", "Q9GZV9", "Shriners Children's", "X-linked hypophosphatemic rickets", "Burosumab target."),
    ("PHEX", "P78562", "Shriners Children's", "X-linked hypophosphatemic rickets", "Loss of PHEX elevates FGF23."),
    ("IRF6", "O14896", "Shriners Children's", "Cleft lip and palate (Van der Woude)", "Most common syndromic cleft gene."),
    ("TGFB1", "P01137", "Shriners Children's", "Burn scarring / fibrosis", "Master regulator of hypertrophic scar formation."),
    ("VEGFA", "P15692", "Shriners Children's", "Burn wound healing", "Angiogenesis in wound repair."),
    ("MMP9", "P14780", "Shriners Children's", "Burn and chronic wounds", "Matrix remodeling protease."),
    ("RTN4", "Q9NQC3", "Shriners Children's", "Spinal cord injury", "Nogo-A; anti-Nogo antibodies in SCI trials."),
    ("RHOA", "P61586", "Shriners Children's", "Spinal cord injury", "Axon-regrowth inhibition pathway."),
    # ---------------- Apoptosis (BCL-XL file) ----------------
    ("BCL2L1", "Q07817", "Apoptosis / BCL-XL", "Oncology, senolytics, neuronal survival", "BCL-XL; navitoclax and ABT-737 bind the BH3 groove."),
    ("BCL2", "P10415", "Apoptosis / BCL-XL", "Oncology", "Venetoclax target; selectivity reference for BCL-XL."),
]

# Structures we know are good starting points (verified by build_targets.py via RCSB).
PREFERRED_PDB = {
    "BCL2L1": "2YXJ",  # BCL-XL with ABT-737
    "SOD1": "2C9V",
    "MAOB": "2V5Z",   # MAO-B with safinamide
    "BCL2": "6O0K",   # BCL-2 with venetoclax
}
