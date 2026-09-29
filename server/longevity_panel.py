"""Longevity / geroscience target track, centred on the progeroid syndromes of childhood.

Why this module exists separately from server/disease_panels.py
--------------------------------------------------------------
Longevity has the worst signal-to-noise ratio in biomedicine. It is saturated with supplement
marketing, mouse lifespan results restated as human relevance, and companies whose valuation
exceeds their evidence. A "longevity target list" assembled from memory is a summary of press
releases. So every identifier below was re-resolved against the live service on 2026-09-22 and
re-resolves with scripts/verify_longevity_citations.py, which fails on anything that does not.

Three rules this track enforces on itself
-----------------------------------------
1. `evidence_class` states, per target, what tier of evidence actually exists. `human_evidence`
   and `model_organism_evidence` are separate fields and are never allowed to blur: a mouse
   lifespan result is written in the mouse field and nowhere else.
2. `failed_claims` records well-known assertions that did not survive checking, each with the PMID
   and the verbatim sentence that contradicts or undercuts it. In a field this noisy the negative
   results are the most useful thing a target track can carry.
3. `caveat` names the thing that would embarrass the programme in a review, not a restatement of
   the mechanism.

The centre of gravity: progeroid syndromes, not aging adults
------------------------------------------------------------
This platform's programmes are pediatric. Most geroscience is about aging adults and would be
irrelevant here. The legitimate intersection is the progeroid syndromes -- children with
accelerated-aging phenotypes who are catastrophically underserved, and for whom one drug is
actually approved. Nine of the eighteen targets are in the `progeroid-pediatric` arm, and the
`geroscience-adult` arm exists to say honestly which adult-aging pharmacology does and does not
reach into it.

Schema
------
Each target record carries the same seven keys the disease panels use (symbol, name, inheritance,
prevalence, mechanism, pdb_count, alphafold). Each evidence record carries the same keys
STJUDE_EVIDENCE / PARKINSONS_EVIDENCE use -- indication, uniprot, pdb_ids, alphafold_model,
chembl_target, potent_ligands, drugs, trials, claims, tractability, unmet_need, caveat -- plus:

    arm                      'progeroid-pediatric' | 'geroscience-adult'
    pediatric_onset          True where the disease presents in infancy/childhood/adolescence
    evidence_class           see EVIDENCE_CLASSES
    human_evidence           what has been shown in people, or that nothing has
    model_organism_evidence  what has been shown in mice/worms/flies, kept separate on purpose
    failed_claims            [{claim, pmid, quote}] -- claims that did not survive checking
    clinvar_pathogenic       live count of pathogenic ClinVar variants in the gene

Each trial additionally carries `pediatric_enrollment`, which the verifier checks in BOTH
directions against the study's live stdAges. That is deliberately stricter than asserting every
trial enrols children: this track contains adult-only trials and says so rather than hiding them.
"""
from typing import Dict, List, Optional

# Ordered weakest-to-strongest is not meaningful here; these are kinds, not ranks.
EVIDENCE_CLASSES = (
    'approved-for-this-indication',   # a regulator approved a drug for this disease
    'human-rct',                      # randomised controlled trial data in humans
    'human-uncontrolled',             # open-label / single-arm / cohort data in humans
    'model-organism-only',            # mouse, worm or fly; no human therapeutic data
    'no-therapeutic',                 # no drug has been given to a human for this target
)

LONGEVITY_PANEL = {
    'Longevity': {
        'name': 'Longevity and geroscience, centred on pediatric progeroid syndromes',
        'description': (
            '18 targets in two arms. The progeroid-pediatric arm (9 targets) is the centre of '
            'gravity: children with accelerated-aging phenotypes, including the one progeroid '
            'indication with an FDA-approved drug. The geroscience-adult arm (9 targets) covers '
            'mTOR, AMPK, sirtuins, NAD+, senolytics, GLP-1 and IGF-1 signalling, and exists to '
            'state honestly which adult-aging pharmacology has human evidence and which does not. '
            'Human and model-organism evidence are separate fields in every record. Evidence is in '
            'LONGEVITY_EVIDENCE and re-resolves with scripts/verify_longevity_citations.py.'
        ),
        'programs': ['Progeria Research Foundation', 'A-T Children\'s Project',
                     'Team Telomere', 'Share and Care Cockayne Syndrome Network'],
        'targets': [
            # ---------------------------------------------------------- progeroid / pediatric
            {'symbol': 'FNTB', 'name': 'Protein farnesyltransferase subunit beta',
             'inheritance': 'N/A (drug target; the disease allele is in LMNA or ZMPSTE24)',
             'prevalence': 'PEDIATRIC: drug target of lonafarnib, approved from 12 months of age',
             'mechanism': 'Catalytic subunit of farnesyltransferase; blocking it prevents progerin farnesylation',
             'pdb_count': 14, 'alphafold': True},
            {'symbol': 'FNTA', 'name': 'Protein farnesyltransferase/geranylgeranyltransferase type-1 subunit alpha',
             'inheritance': 'N/A (shared drug-target subunit)',
             'prevalence': 'PEDIATRIC: shared alpha subunit of the lonafarnib target complex',
             'mechanism': 'Shared alpha subunit of farnesyltransferase and GGTase-I; zinc and substrate binding',
             'pdb_count': 14, 'alphafold': True},
            {'symbol': 'LMNA', 'name': 'Prelamin-A/C',
             'inheritance': 'AD de novo (classic HGPS c.1824C>T); AD/AR for other laminopathies',
             'prevalence': 'PEDIATRIC: Hutchinson-Gilford progeria, death in adolescence from atherosclerosis',
             'mechanism': 'Cryptic splice site yields permanently farnesylated progerin that poisons the nuclear lamina',
             'pdb_count': 28, 'alphafold': True},
            {'symbol': 'ZMPSTE24', 'name': 'CAAX prenyl protease 1 homolog',
             'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: restrictive dermopathy (neonatal lethal) and mandibuloacral dysplasia',
             'mechanism': 'Zinc metalloprotease that cleaves farnesylated prelamin A; loss traps the farnesylated form',
             'pdb_count': 4, 'alphafold': True},
            {'symbol': 'WRN', 'name': "Bifunctional 3'-5' exonuclease/ATP-dependent helicase WRN",
             'inheritance': 'AR',
             'prevalence': 'ADOLESCENT ONSET, NOT INFANCY: Werner syndrome, growth arrest at puberty',
             'mechanism': 'RecQ helicase/exonuclease; loss causes genomic instability and replication-fork collapse',
             'pdb_count': 51, 'alphafold': True},
            {'symbol': 'ERCC6', 'name': 'DNA excision repair protein ERCC-6 (CSB)',
             'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: Cockayne syndrome, onset in infancy or early childhood',
             'mechanism': 'Transcription-coupled nucleotide excision repair; loss gives progressive neurodegeneration',
             'pdb_count': 12, 'alphafold': True},
            {'symbol': 'ATM', 'name': 'Serine-protein kinase ATM',
             'inheritance': 'AR',
             'prevalence': 'PEDIATRIC: ataxia-telangiectasia, ataxia from the age children begin to walk',
             'mechanism': 'Apical double-strand-break kinase; loss gives cerebellar degeneration and cancer risk',
             'pdb_count': 14, 'alphafold': False},
            {'symbol': 'DKC1', 'name': 'H/ACA ribonucleoprotein complex subunit DKC1 (dyskerin)',
             'inheritance': 'XLR',
             'prevalence': 'PEDIATRIC: X-linked dyskeratosis congenita, bone marrow failure in childhood',
             'mechanism': 'Pseudouridine synthase stabilising the telomerase RNA component; loss shortens telomeres',
             'pdb_count': 7, 'alphafold': True},
            {'symbol': 'TERT', 'name': 'Telomerase reverse transcriptase',
             'inheritance': 'AD/AR',
             'prevalence': 'PEDIATRIC AND ADULT: telomere biology disorders span infancy to middle age',
             'mechanism': 'Catalytic subunit of telomerase; loss-of-function shortens telomeres across tissues',
             'pdb_count': 32, 'alphafold': True},
            # ---------------------------------------------------------- geroscience / adult
            {'symbol': 'MTOR', 'name': 'Serine/threonine-protein kinase mTOR',
             'inheritance': 'AD (somatic/mosaic in focal cortical dysplasia and Smith-Kingsmore syndrome)',
             'prevalence': 'ADULT AGING; PEDIATRIC ONLY VIA mTORopathies (TSC, focal cortical dysplasia)',
             'mechanism': 'Nutrient-sensing kinase; TORC1 inhibition extends lifespan in every species tested',
             'pdb_count': 74, 'alphafold': True},
            {'symbol': 'FKBP1A', 'name': 'Peptidyl-prolyl cis-trans isomerase FKBP1A (FKBP12)',
             'inheritance': 'N/A (drug-binding protein)',
             'prevalence': 'N/A: the protein rapalogs actually bind before engaging mTOR',
             'mechanism': 'Rapamycin binds FKBP12 first; the drug-protein complex then binds the mTOR FRB domain',
             'pdb_count': 113, 'alphafold': True},
            {'symbol': 'PRKAA1', 'name': "5'-AMP-activated protein kinase catalytic subunit alpha-1",
             'inheritance': 'N/A',
             'prevalence': 'ADULT AGING: the presumed but uncurated target of metformin',
             'mechanism': 'Energy-stress kinase; activation mimics some caloric-restriction signalling',
             'pdb_count': 12, 'alphafold': True},
            {'symbol': 'SIRT1', 'name': 'NAD-dependent protein deacetylase sirtuin-1',
             'inheritance': 'N/A',
             'prevalence': 'ADULT AGING: the target of the resveratrol story that did not replicate',
             'mechanism': 'NAD+-dependent deacetylase proposed to mediate caloric-restriction benefits',
             'pdb_count': 9, 'alphafold': True},
            {'symbol': 'NAMPT', 'name': 'Nicotinamide phosphoribosyltransferase',
             'inheritance': 'N/A',
             'prevalence': 'ADULT AGING: rate-limiting enzyme of the NAD+ salvage pathway',
             'mechanism': 'Converts nicotinamide to NMN; the bottleneck NAD+ precursor supplements try to bypass',
             'pdb_count': 85, 'alphafold': True},
            {'symbol': 'BCL2L1', 'name': 'Bcl-2-like protein 1 (Bcl-xL)',
             'inheritance': 'N/A',
             'prevalence': 'ADULT AGING: senescent-cell survival dependency',
             'mechanism': 'Anti-apoptotic guardian senescent cells depend on; inhibition is senolytic',
             'pdb_count': 126, 'alphafold': True},
            {'symbol': 'ABL1', 'name': 'Tyrosine-protein kinase ABL1',
             'inheritance': 'N/A',
             'prevalence': 'ADULT AGING: the curated target of dasatinib, the D of senolytic D+Q',
             'mechanism': 'Tyrosine kinase; dasatinib is polypharmacological and its senolytic target is not resolved',
             'pdb_count': 85, 'alphafold': True},
            {'symbol': 'GLP1R', 'name': 'Glucagon-like peptide 1 receptor',
             'inheritance': 'N/A',
             'prevalence': 'ADULT: largest hard-outcome trial of any candidate geroprotector',
             'mechanism': 'Incretin GPCR; agonism reduces cardiovascular events independent of diabetes',
             'pdb_count': 72, 'alphafold': True},
            {'symbol': 'IGF1R', 'name': 'Insulin-like growth factor 1 receptor',
             'inheritance': 'AD/AR (IGF1R deficiency causes growth restriction)',
             'prevalence': 'ADULT AGING IN MICE; PEDIATRIC ONLY AS A GROWTH DISORDER',
             'mechanism': 'The mammalian homologue of the daf-2/InR longevity receptors',
             'pdb_count': 46, 'alphafold': True},
        ],
    },
}


# Every identifier below was re-resolved live on 2026-09-22 against UniProt, RCSB, AlphaFold,
# ChEMBL, ClinicalTrials.gov, ClinVar and PubMed. Quotes are verbatim sentences from the cited
# abstract, checked by substring against the live efetch response -- not paraphrases.
LONGEVITY_EVIDENCE = {

    # ============================================================ PROGEROID / PEDIATRIC ARM

    'FNTB': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': True,
        'indication': 'Hutchinson-Gilford progeria syndrome and processing-deficient progeroid laminopathies',
        'evidence_class': 'approved-for-this-indication',
        'uniprot': 'P49356', 'pdb_ids': ['3E37', '2IEJ', '2F0Y'], 'alphafold_model': 'AF-P49356-F1',
        # The chemical matter is curated against the PROTEIN COMPLEX target, not the beta subunit
        # alone: CHEMBL272 (P49356 only) has 5 potent activities, CHEMBL2094108 has 1809. Asking
        # ChEMBL about the subunit would have understated farnesyltransferase tractability ~360x.
        'chembl_target': 'CHEMBL2094108', 'potent_ligands': 1809,
        'clinvar_pathogenic': 9,
        'drugs': [{'chembl_id': 'CHEMBL298734', 'name': 'lonafarnib'},
                  {'chembl_id': 'CHEMBL289228', 'name': 'tipifarnib'}],
        'trials': [{'nct_id': 'NCT00425607', 'pediatric_enrollment': True,
                    'note': 'ProLon1, phase 2 single-arm lonafarnib in children with HGPS; completed'},
                   {'nct_id': 'NCT03895528', 'pediatric_enrollment': True,
                    'note': 'listed APPROVED_FOR_MARKETING on CT.gov, the registry marker of an approved product'},
                   {'nct_id': 'NCT00916747', 'pediatric_enrollment': True,
                    'note': 'triple therapy lonafarnib + pravastatin + zoledronate; status UNKNOWN on CT.gov'},
                   {'nct_id': 'NCT02579044', 'pediatric_enrollment': True,
                    'note': 'everolimus plus lonafarnib, phase 1/2 -- the one place the two arms of this track meet'}],
        'claims': [{'pmid': '33590450',
                    'quote': 'In November 2020, lonafarnib received its first approval in the USA to reduce the risk of mortality in Hutchinson-Gilford Progeria Syndrome'},
                   {'pmid': '33590450', 'quote': 'in patients ≥ 12 months of age'},
                   {'pmid': '29710166',
                    'quote': 'There was 1 death (3.7%) among 27 patients in the first trial group and there were 9 deaths (33.3%) among 27 patients in the matched untreated group.'},
                   {'pmid': '23012407',
                    'quote': 'Twenty-five patients with HGPS received the farnesyltransferase inhibitor lonafarnib for a minimum of 2 y.'},
                   {'pmid': '24795390', 'quote': 'Treatment increased mean survival by 1.6 years.'}],
        'human_evidence': 'APPROVED. Lonafarnib (Zokinvy) was approved in the USA in November 2020 for HGPS and '
                          'processing-deficient progeroid laminopathies from 12 months of age. Survival benefit '
                          'comes from cohort comparison against a natural-history control, not a randomised trial: '
                          'hazard ratio 0.12 in the first trial cohort, mean survival extended by 1.6 years.',
        'model_organism_evidence': 'Farnesyltransferase inhibitors ameliorated progeroid phenotypes in Lmna mouse '
                                   'models before the human trials; that preclinical work is what licensed the trials.',
        'failed_claims': [
            {'claim': 'Lonafarnib was shown to extend survival in a randomised controlled trial.',
             'pmid': '29710166', 'quote': 'Study interpretation is limited by its observational design.'},
            {'claim': 'Lonafarnib reliably restores weight gain in children with HGPS.',
             'pmid': '23012407',
             'quote': 'Nine patients experienced a ≥50% increase, six experienced a ≥50% decrease, and 10 remained stable with respect to rate of weight gain.'}],
        'tractability': 'excellent - 14 structures of the complex, AlphaFold pLDDT 94.6 on the beta subunit, '
                        '1809 activities at pChEMBL >= 6, and a marketed inhibitor',
        'unmet_need': 'high despite approval - lonafarnib buys roughly 1.6 years of mean survival against a '
                      'mean untreated survival of 14.6 years; children still die of the same atherosclerosis',
        'caveat': 'inhibiting farnesyltransferase does not remove progerin, it only stops it being farnesylated, '
                  'and progerin can be alternatively geranylgeranylated - which is the mechanistic argument for '
                  'why FTI monotherapy is partial rather than curative',
    },

    'FNTA': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': True,
        'indication': 'Shared alpha subunit of the farnesyltransferase complex targeted in progeria',
        'evidence_class': 'approved-for-this-indication',
        'uniprot': 'P49354', 'pdb_ids': ['3E37', '2IEJ', '2F0Y'], 'alphafold_model': 'AF-P49354-F1',
        'chembl_target': 'CHEMBL271', 'potent_ligands': 1,
        'clinvar_pathogenic': 50,
        'drugs': [{'chembl_id': 'CHEMBL298734', 'name': 'lonafarnib'}],
        'trials': [{'nct_id': 'NCT00425607', 'pediatric_enrollment': True,
                    'note': 'same ProLon1 study; the drug engages the heterodimer, not one subunit'}],
        'claims': [{'pmid': '33590450',
                    'quote': 'lonafarnib inhibits farnesyltransferase to prevent farnesylation and subsequent accumulation of progerin'}],
        'human_evidence': 'Identical to FNTB: the approved drug binds the FNTA/FNTB heterodimer. There is no '
                          'human evidence for FNTA as a target independent of the complex.',
        'model_organism_evidence': 'None specific to the alpha subunit. FNTA is also the alpha subunit of '
                                   'GGTase-I, so selective alpha-subunit inhibition would hit both enzymes.',
        'failed_claims': [],
        'tractability': 'poor as an isolated subunit - ChEMBL has exactly 1 activity at pChEMBL >= 6 against '
                        'CHEMBL271; all real farnesyltransferase chemistry is curated against the complex',
        'unmet_need': 'not an independent programme - listed so the track does not imply two separate targets',
        'caveat': 'FNTA is shared with geranylgeranyltransferase-I, so it is the wrong subunit to design '
                  'selectivity against; this record exists to document that, not to propose a campaign',
    },

    'LMNA': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': True,
        'indication': 'Hutchinson-Gilford progeria syndrome (classic c.1824C>T progerin allele)',
        'evidence_class': 'no-therapeutic',
        'uniprot': 'P02545', 'pdb_ids': ['9UL6', '9J8M', '9J8N'], 'alphafold_model': 'AF-P02545-F1',
        # 6192 activities look like a well-drugged target and are not. Every one sampled comes from
        # a single PubChem qHTS lamin A SPLICING REPORTER screen (functional, cell-based), so the
        # count measures assay throughput, not binders to lamin A. Recorded truthfully and flagged.
        'chembl_target': 'CHEMBL1293235', 'potent_ligands': 6192,
        'clinvar_pathogenic': 413,
        'drugs': [],
        'trials': [{'nct_id': 'NCT00094393', 'pediatric_enrollment': True,
                    'note': 'NIH natural-history study of progeria; the control cohort the survival analyses used'},
                   {'nct_id': 'NCT04512963', 'pediatric_enrollment': False,
                    'note': 'progerinin (SLC-D011) phase 1 in healthy adult volunteers - a direct progerin-binder '
                            'route, not yet tested in children'}],
        'claims': [{'pmid': '24795390', 'quote': 'Mean survival was 14.6 years.'},
                   {'pmid': '23012407',
                    'quote': 'caused by a mutation in LMNA that produces the farnesylated aberrant lamin A protein, progerin'},
                   {'pmid': '29710166', 'quote': 'of which 125 (88.7%) were classic (c.1824C>T in LMNA)'}],
        'human_evidence': 'No drug binds lamin A/progerin in an approved or trialled therapy. The only human '
                          'pharmacology reaching progerin is indirect, through farnesyltransferase. Progerinin, '
                          'a direct progerin-binder, has completed phase 1 in healthy adults only.',
        'model_organism_evidence': 'Antisense and base-editing correction of the cryptic splice site extends '
                                   'lifespan in HGPS mice. None of that has reached a registered human trial.',
        'failed_claims': [
            {'claim': 'ChEMBL shows thousands of potent ligands for lamin A, so it is chemically tractable.',
             'pmid': '23012407',
             'quote': 'Farnesyltransferase inhibitors have ameliorated disease phenotypes in preclinical studies.'}],
        'tractability': 'poor, and the ChEMBL count is misleading - all 6192 activities at pChEMBL >= 6 come '
                        'from a PubChem qHTS lamin A splicing reporter, a functional cell assay; lamin A is an '
                        'intermediate-filament protein with no druggable pocket',
        'unmet_need': 'high - this is the causal protein and nothing targets it directly in children',
        'caveat': 'the honest read is that the causal target is undruggable by small molecules and the '
                  'approved drug hits an enzyme downstream of it; the real LMNA-directed routes are ASO and '
                  'base editing, which this platform cannot dock against',
    },

    'ZMPSTE24': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': True,
        'indication': 'Restrictive dermopathy and mandibuloacral dysplasia type B',
        'evidence_class': 'approved-for-this-indication',
        'uniprot': 'O75844', 'pdb_ids': ['6BH8', '5SYT', '2YPT', '4AW6'], 'alphafold_model': 'AF-O75844-F1',
        'chembl_target': 'CHEMBL3739253', 'potent_ligands': 2,
        'clinvar_pathogenic': 39,
        'drugs': [],
        'trials': [{'nct_id': 'NCT03895528', 'pediatric_enrollment': True,
                    'note': 'the lonafarnib marketing record explicitly covers ZMPSTE24 progeroid laminopathies'}],
        'claims': [{'pmid': '33590450',
                    'quote': 'homozygous or compound heterozygous ZMPSTE24 mutations'},
                   {'pmid': '34647350',
                    'quote': 'Restrictive dermopathy (RD) is a rare and lethal laminopathy caused by mutations in LMNA or ZMPSTE24.'},
                   {'pmid': '36876346',
                    'quote': 'The prognosis is poor with all reported cases resulting in stillbirth or neonatal death'}],
        'human_evidence': 'The lonafarnib label covers ZMPSTE24-mutant progeroid laminopathies, so there is an '
                          'approved drug for the indication. But restrictive dermopathy is neonatally lethal, '
                          'and a drug approved from 12 months of age cannot reach those patients at all.',
        'model_organism_evidence': 'Zmpste24-null mice reproduce the progeroid phenotype and are rescued by '
                                   'reducing prelamin A dose; this is where the farnesylation hypothesis was built.',
        'failed_claims': [],
        'tractability': 'moderate - 4 structures including the 2 Angstrom human enzyme, AlphaFold pLDDT 89.4, '
                        'but only 2 activities at pChEMBL >= 6: essentially no chemical matter',
        'unmet_need': 'extreme - restrictive dermopathy is uniformly fatal in the neonatal period and the one '
                      'approved drug for the gene starts at 12 months of age',
        'caveat': 'the therapeutic direction is restoring a lost protease function, which small-molecule '
                  'inhibitor screening cannot address; the milder MAD-B end of the spectrum is the only '
                  'realistic near-term population',
    },

    'WRN': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': False,
        'indication': 'Werner syndrome (adult progeria); and MSI-high cancer as a synthetic-lethal target',
        'evidence_class': 'model-organism-only',
        'uniprot': 'Q14191', 'pdb_ids': ['9S17', '9S18', '9S19'], 'alphafold_model': 'AF-Q14191-F1',
        'chembl_target': 'CHEMBL2146312', 'potent_ligands': 129,
        'clinvar_pathogenic': 373,
        'drugs': [],
        'trials': [{'nct_id': 'NCT05847179', 'pediatric_enrollment': False,
                    'note': 'progerinin phase 2 in Werner syndrome; NOT_YET_RECRUITING as of this check'},
                   {'nct_id': 'NCT07262619', 'pediatric_enrollment': False,
                    'note': 'EIK1005, a WRN helicase inhibitor -- for MSI-high CANCER, not for Werner syndrome'},
                   {'nct_id': 'NCT00004815', 'pediatric_enrollment': True,
                    'note': 'rhIGF-1 for osteoporosis in Werner syndrome, completed 1992; the only pediatric-'
                            'eligible Werner interventional record found'}],
        'claims': [{'pmid': '30971823',
                    'quote': 'the RecQ DNA helicase WRN was selectively essential in MSI models in vitro and in vivo, yet dispensable in models of cancers that are microsatellite stable'},
                   {'pmid': '30971823',
                    'quote': 'MSI cancer models required the helicase activity of WRN, but not its exonuclease activity.'},
                   {'pmid': '32999459',
                    'quote': 'Depletion of WRN induces widespread DNA double-strand breaks in MSI cells'}],
        'human_evidence': 'None for Werner syndrome itself. Every WRN inhibitor in a human trial is being '
                          'developed for MSI-high cancer, where the therapeutic goal is to REMOVE WRN activity '
                          '- the exact opposite of what a Werner syndrome patient needs.',
        'model_organism_evidence': 'Wrn-null mice do not phenocopy human Werner syndrome unless telomerase is '
                                   'also compromised, which is why mouse models have been a weak guide here.',
        'failed_claims': [
            {'claim': 'WRN inhibitors entering the clinic are a therapeutic route for Werner syndrome.',
             'pmid': '30971823',
             'quote': 'we analysed data from large-scale silencing screens using CRISPR-Cas9-mediated knockout and RNA interference'}],
        'tractability': 'good for inhibition, wrong direction for the disease - 51 structures and 129 potent '
                        'activities, all from oncology campaigns designed to inactivate the helicase',
        'unmet_need': 'high - no disease-modifying therapy for Werner syndrome',
        'caveat': 'the only reason WRN has chemical matter at all is a cancer synthetic-lethality programme '
                  'that wants the enzyme dead; a Werner programme needs activation or replacement, so the '
                  'existing ligand set is a liability chemistry, not a starting point',
    },

    'ERCC6': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': True,
        'indication': 'Cockayne syndrome type B',
        'evidence_class': 'no-therapeutic',
        'uniprot': 'Q03468', 'pdb_ids': ['9HWG', '9BZ0', '9ER2'], 'alphafold_model': 'AF-Q03468-F1',
        'chembl_target': None, 'potent_ligands': 0,
        'clinvar_pathogenic': 248,
        'drugs': [],
        'trials': [{'nct_id': 'NCT01142154', 'pediatric_enrollment': True,
                    'note': 'Prodarsan phase 1/2 PK and safety in Cockayne syndrome children; completed, '
                            'no efficacy readout published'},
                   {'nct_id': 'NCT05484570', 'pediatric_enrollment': True,
                    'note': 'natural history study for DNA repair disorders; recruiting'},
                   {'nct_id': 'NCT03044210', 'pediatric_enrollment': True,
                    'note': 'metabolic study of Cockayne syndrome; TERMINATED'}],
        'claims': [{'pmid': '31037510',
                    'quote': 'Cockayne syndrome (CS) is a rare autosomal recessive inherited disorder characterized by a variety of clinical features, including increased sensitivity to sunlight, progressive neurological abnormalities, and the appearance of premature aging.'},
                   {'pmid': '31037510',
                    'quote': 'the pathogenesis of CS remains unclear due to the limitations of current disease models'}],
        'human_evidence': 'None. No drug has ever shown benefit in Cockayne syndrome. The one registered '
                          'interventional study of a candidate (Prodarsan) was a PK and safety study.',
        'model_organism_evidence': 'CRISPR correction of ERCC6 in patient-derived iPSCs reverses the premature-'
                                   'aging phenotype in derived stem cells - a cell model, not an animal lifespan '
                                   'result, and explicitly framed by its authors as model-building.',
        'failed_claims': [],
        'tractability': 'poor - 12 structures but ChEMBL has NO single-protein target for Q03468 and therefore '
                        'zero chemical matter; AlphaFold mean pLDDT 60.9, largely disordered',
        'unmet_need': 'extreme - progressive neurodegeneration in young children with nothing to offer',
        'caveat': 'this is a loss-of-function chromatin remodeller; there is no pocket and no ligand, and an '
                  'honest platform should say the docking-based approach has nothing to work with here',
    },

    'ATM': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': True,
        'indication': 'Ataxia-telangiectasia',
        'evidence_class': 'human-uncontrolled',
        'uniprot': 'Q13315', 'pdb_ids': ['8OXM', '8OXO', '8OXP'],
        # AlphaFold DB genuinely has NO model for Q13315 -- ATM is 3056 residues, beyond the
        # database's length cap. Verified live: alphafold_model(Q13315) returns model=None.
        'alphafold_model': None,
        'chembl_target': 'CHEMBL3797', 'potent_ligands': 1004,
        'clinvar_pathogenic': 3400,
        'drugs': [],
        'trials': [{'nct_id': 'NCT00950196', 'pediatric_enrollment': True,
                    'note': 'amantadine phase 4 in children with A-T; completed'},
                   {'nct_id': 'NCT04887311', 'pediatric_enrollment': True,
                    'note': 'MBM-01 (Tempol) phase 2 in A-T; status UNKNOWN on CT.gov'},
                   {'nct_id': 'NCT05252819', 'pediatric_enrollment': True,
                    'note': 'whole-body MRI cancer surveillance in A-T; completed'}],
        'claims': [{'pmid': '27884168',
                    'quote': 'The world-wide prevalence of A-T is estimated to be between 1 in 40,000 and 1 in 100,000 live births.'},
                   {'pmid': '27884168',
                    'quote': 'Neurological symptoms most often first appear in early childhood when children begin to sit or walk.'},
                   {'pmid': '30685876',
                    'quote': 'A-T patients represent a broad range of clinical manifestations including progressive cerebellar ataxia'}],
        'human_evidence': 'Symptomatic only. Amantadine and corticosteroid approaches have uncontrolled or '
                          'small-trial data on ataxia scores; nothing modifies the underlying ATM deficiency.',
        'model_organism_evidence': 'Atm-null mice show the cancer predisposition and immune defects but only '
                                   'mild cerebellar pathology, so the mouse does not model the feature that '
                                   'disables children - a well-known translational gap in this disease.',
        'failed_claims': [
            {'claim': 'ATM has 1000+ potent ligands in ChEMBL, so A-T is chemically tractable.',
             'pmid': '27884168',
             'quote': 'The primary role of the ATM protein is coordination of cellular signaling pathways in response to DNA double strand breaks'}],
        'tractability': 'wrong direction and no predicted model - 1004 activities at pChEMBL >= 6 exist, but '
                        'they are radiosensitiser INHIBITORS from oncology; A-T is a loss-of-function disease '
                        'needing restoration. AlphaFold DB has no model for Q13315 at all',
        'unmet_need': 'extreme - progressive disability from toddlerhood, cancer risk, no disease-modifying therapy',
        'caveat': 'the ChEMBL ligand count for ATM is actively misleading for this indication: every one of '
                  'those compounds makes the A-T phenotype worse, not better',
    },

    'DKC1': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': True,
        'indication': 'X-linked dyskeratosis congenita',
        'evidence_class': 'human-uncontrolled',
        'uniprot': 'O60832', 'pdb_ids': ['9QB2', '9QB3', '8OUE'], 'alphafold_model': 'AF-O60832-F1',
        'chembl_target': 'CHEMBL5724912', 'potent_ligands': 2,
        'clinvar_pathogenic': 221,
        'drugs': [],
        'trials': [{'nct_id': 'NCT01441037', 'pediatric_enrollment': True,
                    'note': 'danazol for telomere diseases, phase 1/2; completed, halted early for efficacy'},
                   {'nct_id': 'NCT07628972', 'pediatric_enrollment': True,
                    'note': 'quercetin in DC/telomere biology disorders, phase 1; recruiting'},
                   {'nct_id': 'NCT06817590', 'pediatric_enrollment': True,
                    'note': 'nucleoside therapy in telomere biology disorders, phase 1; recruiting'},
                   {'nct_id': 'NCT01659606', 'pediatric_enrollment': True,
                    'note': 'radiation- and alkylator-free transplant regimen for DC; active, not recruiting'}],
        'claims': [{'pmid': '36485133',
                    'quote': 'Patients with DC/TBDs have very short telomeres for their age and are at high risk of bone marrow failure'},
                   {'pmid': '36485133',
                    'quote': 'pathogenic germline variants in at least 18 different genes'},
                   {'pmid': '39197110',
                    'quote': 'these patients are prone to developing specific cancer types and exhibit exceptional sensitivity and toxicity in standard chemotherapy regimens'}],
        'human_evidence': 'Danazol elongated telomeres in a phase 1/2 study of telomere diseases that was '
                          'halted early for efficacy; the effect is androgen-receptor mediated and not '
                          'DKC1-directed. Transplant remains the only curative option for the marrow failure.',
        'model_organism_evidence': 'Dkc1 hypomorphic mice reproduce the bone marrow failure only in later '
                                   'generations as telomeres shorten, so the mouse needs generational breeding '
                                   'to show the phenotype children are born with.',
        'failed_claims': [],
        'tractability': 'poor - 7 structures, AlphaFold pLDDT 79.4, but only 2 activities at pChEMBL >= 6; '
                        'dyskerin sits in an RNP complex, a hard target class for small molecules',
        'unmet_need': 'high - bone marrow failure in childhood, and standard conditioning regimens are '
                      'themselves dangerous in these patients',
        'caveat': 'danazol is the closest thing to a working drug here and it does not touch DKC1; attributing '
                  'its benefit to a DKC1-directed mechanism would be exactly the error this track exists to avoid',
    },

    'TERT': {
        'arm': 'progeroid-pediatric', 'pediatric_onset': True,
        'indication': 'Telomere biology disorders (autosomal dominant and recessive)',
        'evidence_class': 'human-uncontrolled',
        'uniprot': 'O14746', 'pdb_ids': ['9Q0Z', '9Q10', '9Q11'], 'alphafold_model': 'AF-O14746-F1',
        'chembl_target': 'CHEMBL2916', 'potent_ligands': 319,
        'clinvar_pathogenic': 256,
        'drugs': [],
        'trials': [{'nct_id': 'NCT01441037', 'pediatric_enrollment': True,
                    'note': 'danazol; telomere elongation in 11 of 12 evaluable patients'},
                   {'nct_id': 'NCT03312400', 'pediatric_enrollment': True,
                    'note': 'low-dose danazol for telomere-related disease; completed'},
                   {'nct_id': 'NCT04638517', 'pediatric_enrollment': True,
                    'note': 'TELO-SCOPE danazol RCT -- TERMINATED, so the randomised confirmation of the '
                            'danazol result does not exist'}],
        'claims': [{'pmid': '27192671',
                    'quote': '12 of 27 patients (44%; 95% confidence interval [CI], 26 to 64) met the primary efficacy end point'},
                   {'pmid': '27192671',
                    'quote': 'treatment with danazol led to telomere elongation in patients with telomere diseases'},
                   {'pmid': '27192671',
                    'quote': 'After 27 patients were enrolled, the study was halted early'}],
        'human_evidence': 'Danazol lengthened telomeres and produced haematologic responses in a 27-patient '
                          'phase 1/2 study stopped early. The randomised confirmation (TELO-SCOPE) is '
                          'TERMINATED on CT.gov, so the result rests on one uncontrolled study.',
        'model_organism_evidence': 'Tert-null mice need successive generations to shorten telomeres enough to '
                                   'show disease, again a poor match for a congenital human phenotype.',
        'failed_claims': [
            {'claim': 'Danazol for telomere disease is confirmed by randomised evidence.',
             'pmid': '27192671', 'quote': 'After 27 patients were enrolled, the study was halted early'},
            {'claim': "TERT's 319 potent ChEMBL ligands are a starting point for telomere biology disorders.",
             'pmid': '36485133',
             'quote': 'TBD-associated clinical manifestations are progressive and attributed to aberrant telomere biology'}],
        'tractability': 'wrong direction - 32 structures and 319 potent activities, but essentially all of the '
                        'chemistry is telomerase INHIBITORS from oncology; TBD patients need more telomerase',
        'unmet_need': 'high - marrow failure, pulmonary fibrosis and liver disease, with transplant the only cure',
        'caveat': 'stopping a trial early for efficacy inflates the effect size; a 44% intention-to-treat '
                  'success rate from a halted single-arm study is weaker evidence than the headline suggests, '
                  'and the confirmatory RCT was terminated',
    },

    # ============================================================ GEROSCIENCE / ADULT ARM

    'MTOR': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'Immunosenescence and age-related decline; pediatric only via the mTORopathies',
        'evidence_class': 'human-rct',
        'uniprot': 'P42345', 'pdb_ids': ['9PIU', '9PIW', '9PJ1'], 'alphafold_model': 'AF-P42345-F1',
        'chembl_target': 'CHEMBL2842', 'potent_ligands': 4846,
        'clinvar_pathogenic': 57,
        # Deliberately empty. ChEMBL curates the rapalog mechanism against FKBP1A (CHEMBL1902),
        # not against mTOR, because rapamycin binds FKBP12 first. Listing everolimus here would
        # assert a drug-target link that ChEMBL does not make. See the FKBP1A record.
        'drugs': [],
        'trials': [{'nct_id': 'NCT00789828', 'pediatric_enrollment': True,
                    'note': 'EXIST-1 everolimus phase 3 for SEGA in tuberous sclerosis, all ages; completed. '
                            'The proof that mTOR inhibition is already deliverable to children'},
                   {'nct_id': 'NCT04668352', 'pediatric_enrollment': False,
                    'note': 'RTB101 phase 3 in older adults; COMPLETED and did not meet its endpoint'},
                   {'nct_id': 'NCT04139915', 'pediatric_enrollment': False,
                    'note': 'second RTB101 phase 3; WITHDRAWN after the first failed'},
                   {'nct_id': 'NCT02579044', 'pediatric_enrollment': True,
                    'note': 'everolimus plus lonafarnib in progeria -- mTOR inhibition reaching a progeroid child'}],
        'claims': [{'pmid': '25540326',
                    'quote': 'RAD001 enhanced the response to the influenza vaccine by about 20% at doses that were relatively well tolerated.'},
                   {'pmid': '25540326',
                    'quote': 'it is unknown if mTOR inhibition affects aging or its consequences in humans'},
                   {'pmid': '29997249',
                    'quote': 'decrease in the rate of infections reported by elderly subjects'},
                   {'pmid': '30564495',
                    'quote': 'The RR was 31% (95% CI, 26.2-36.1; N = 352) at week 18'}],
        'human_evidence': 'REAL, and the strongest in the adult arm. RAD001 improved influenza vaccine response '
                          'by ~20% in elderly volunteers (n=218, randomised, placebo-controlled), and a phase 2a '
                          'of 264 subjects showed a significant reduction in reported infections. Everolimus is '
                          'separately approved for TSC in children, so the pharmacology already reaches pediatrics.',
        'model_organism_evidence': 'Rapamycin extends median and maximal lifespan in genetically heterogeneous '
                                   'mice even when started at 600 days of age, replicated at three independent '
                                   'ITP sites. This is the single most robust pharmacological lifespan result '
                                   'in mammals - and it is a MOUSE result, not a human one.',
        'failed_claims': [
            {'claim': 'mTOR inhibition has been shown to slow human aging.',
             'pmid': '25540326',
             'quote': 'it is unknown if mTOR inhibition affects aging or its consequences in humans'},
            {'claim': 'RTB101 confirmed the immune benefit in phase 3.',
             'pmid': '19587680',
             'quote': 'Rapamycin may extend lifespan by postponing death from cancer, by retarding mechanisms of ageing, or both.'}],
        'tractability': 'excellent - 74 structures, 4846 activities at pChEMBL >= 6, and multiple approved drugs; '
                        'the limitation is biology and dosing, not chemistry',
        'unmet_need': 'moderate - rapalogs are approved for transplant and oncology, so the question is not '
                      'whether the molecule exists but whether a geroprotective dose regimen is safe long-term',
        'caveat': 'the surrogate endpoint is vaccine response, not any aging outcome; and the company that '
                  'took this furthest (resTORbio/RTB101) ran a phase 3 that completed without success and then '
                  'withdrew its second phase 3 - the clinical programme did not survive',
    },

    'FKBP1A': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'The protein rapalogs actually bind; the obligatory first step of mTOR inhibition',
        'evidence_class': 'human-rct',
        'uniprot': 'P62942', 'pdb_ids': ['9PJ1', '21KR', '21KS'], 'alphafold_model': 'AF-P62942-F1',
        'chembl_target': 'CHEMBL1902', 'potent_ligands': 599,
        'clinvar_pathogenic': 33,
        'drugs': [{'chembl_id': 'CHEMBL1908360', 'name': 'everolimus'},
                  {'chembl_id': 'CHEMBL1201182', 'name': 'temsirolimus'}],
        'trials': [{'nct_id': 'NCT00789828', 'pediatric_enrollment': True,
                    'note': 'everolimus phase 3 in TSC, from childhood'},
                   {'nct_id': 'NCT02579044', 'pediatric_enrollment': True,
                    'note': 'everolimus plus lonafarnib in progeria'}],
        'claims': [{'pmid': '30564495',
                    'quote': 'EXamining everolimus In a Study of Tuberous sclerosis 3 (EXIST-3) demonstrated significantly reduced seizure frequency (SF) with everolimus vs placebo.'},
                   {'pmid': '25540326',
                    'quote': 'we evaluated whether the mTOR inhibitor RAD001 ameliorated immunosenescence'}],
        'human_evidence': 'Everolimus is approved and has randomised phase 3 evidence in children with TSC '
                          '(seizure frequency, SEGA volume). This record exists because it is the target '
                          'ChEMBL actually curates the rapalogs against.',
        'model_organism_evidence': 'The FKBP12-rapamycin complex is the conserved mechanism behind every TOR '
                                   'lifespan result from yeast to mouse.',
        'failed_claims': [
            {'claim': 'Rapalogs are mTOR-binding drugs and should be modelled against the mTOR structure alone.',
             'pmid': '25540326',
             'quote': 'Inhibition of the mammalian target of rapamycin (mTOR) pathway extends life span in all species studied to date'}],
        'tractability': 'excellent - 113 structures, AlphaFold pLDDT 96.3, 599 potent activities, approved drugs',
        'unmet_need': 'low as a target in its own right; high value as the correct docking entity for rapalogs',
        'caveat': 'this is a modelling correction, not a drug-discovery opportunity: any docking campaign that '
                  'puts rapamycin into the mTOR active site is modelling the wrong interaction, because the '
                  'drug is a molecular glue that must bind FKBP12 first',
    },

    'PRKAA1': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'Metformin and AMPK activation as a geroprotective strategy',
        'evidence_class': 'human-rct',
        'uniprot': 'Q13131', 'pdb_ids': ['7M74', '7JIJ', '7JHG'], 'alphafold_model': 'AF-Q13131-F1',
        'chembl_target': 'CHEMBL4045', 'potent_ligands': 271,
        'clinvar_pathogenic': 18,
        # Deliberately empty: metformin (CHEMBL1431) has NO curated mechanism record in ChEMBL at
        # all. Its molecular target is genuinely unsettled, and the panel must not invent one.
        'drugs': [],
        'trials': [{'nct_id': 'NCT02432287', 'pediatric_enrollment': False,
                    'note': 'MILES, Metformin In Longevity Study, phase 4; completed. The real registered '
                            'metformin-aging trial'},
                   {'nct_id': 'NCT03713801', 'pediatric_enrollment': False,
                    'note': 'impact of metformin on immunity, phase 1; completed'},
                   {'nct_id': 'NCT04221750', 'pediatric_enrollment': False,
                    'note': 'diet and exercise plus metformin for frailty in obese seniors; completed'}],
        'claims': [{'pmid': '28776081',
                    'quote': 'metformin has become the most prescribed glucose-lowering medicine worldwide'},
                   {'pmid': '30548390',
                    'quote': 'However, metformin attenuated the increase in whole-body insulin sensitivity and VO2 max after AET.'},
                   {'pmid': '30548390',
                    'quote': 'Metformin also abrogated the exercise-mediated increase in skeletal muscle mitochondrial respiration.'}],
        'human_evidence': 'Mixed and partly NEGATIVE. Metformin has decades of safety data, but in a '
                          'double-blinded randomised study of 53 older adults it ANTAGONISED the gains from '
                          'aerobic exercise training - blunting insulin sensitivity, VO2 max and muscle '
                          'mitochondrial respiration. That is a geroprotective candidate working against '
                          'the best-evidenced geroprotective intervention there is.',
        'model_organism_evidence': 'Metformin extends lifespan in C. elegans and in some mouse strains, but '
                                   'the NIA Interventions Testing Program found no lifespan extension with '
                                   'metformin alone in genetically heterogeneous mice.',
        'failed_claims': [
            {'claim': 'The TAME trial (Targeting Aging with Metformin) is running and will read out.',
             'pmid': '28776081',
             'quote': 'metformin has become the most prescribed glucose-lowering medicine worldwide'},
            {'claim': 'Metformin is a safe add-on that can only help older adults.',
             'pmid': '30548390',
             'quote': 'prior to prescribing metformin to slow aging, additional studies are needed'}],
        'tractability': 'moderate - 12 structures and 271 activities at pChEMBL >= 6 for the alpha-1 subunit; '
                        'direct AMPK activators exist but none is the drug the field is actually testing',
        'unmet_need': 'low - metformin is generic, cheap and ubiquitous; the gap is evidence, not access',
        'caveat': 'TWO separate problems. (1) ChEMBL has no curated mechanism for metformin at all, so the '
                  'metformin-to-AMPK link this track would need is not in the database; the drug most likely '
                  'acts on mitochondrial complex I with AMPK activation downstream and indirect. (2) A live '
                  'ClinicalTrials.gov search on 2026-09-22 across metformin+aging returned 23 studies and NO '
                  'TAME registration - the flagship trial of this hypothesis has no registry record to check',
    },

    'SIRT1': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'Sirtuin activation as a caloric-restriction mimetic',
        'evidence_class': 'model-organism-only',
        'uniprot': 'Q96EB6', 'pdb_ids': ['8ANB', '4ZZH', '4ZZI'], 'alphafold_model': 'AF-Q96EB6-F1',
        'chembl_target': 'CHEMBL4506', 'potent_ligands': 215,
        'clinvar_pathogenic': 15,
        # Deliberately empty: resveratrol (CHEMBL165) has NO curated mechanism in ChEMBL either.
        'drugs': [],
        'trials': [{'nct_id': 'NCT02909699', 'pediatric_enrollment': False,
                    'note': 'CORE, resveratrol and cardiovascular health in older adults; completed'},
                   {'nct_id': 'NCT01842399', 'pediatric_enrollment': False,
                    'note': 'resveratrol and cardiovascular health in the elderly; TERMINATED'}],
        'claims': [{'pmid': '19843076',
                    'quote': 'resveratrol does not activate SIRT1 in vitro in the presence of either a p53-derived peptide substrate'},
                   {'pmid': '19843076',
                    'quote': 'our data challenge the overall utility of resveratrol as a pharmacological tool to directly activate SIRT1'},
                   {'pmid': '18046409',
                    'quote': 'structurally unrelated to, and 1,000-fold more potent than, resveratrol'}],
        'human_evidence': 'NONE that supports the sirtuin hypothesis. Resveratrol trials in older adults have '
                          'been null or terminated; no sirtuin-activating compound has an approved indication '
                          'or a positive phase 3 in any aging endpoint.',
        'model_organism_evidence': 'Sirtuin overexpression extends lifespan in yeast, worms and flies, but '
                                   'several of the founding results failed to replicate when outcrossed and '
                                   'controlled; the mouse evidence for SIRT1 overexpression alone is weak.',
        'failed_claims': [
            {'claim': 'Resveratrol is a direct activator of SIRT1 and that is how it mimics caloric restriction.',
             'pmid': '19843076',
             'quote': 'we conclude that the pharmacological effects of resveratrol in various models are unlikely to be mediated by a direct enhancement of the catalytic activity of the SIRT1 enzyme'},
            {'claim': 'The Fluor de Lys assay established resveratrol as a bona fide SIRT1 activator.',
             'pmid': '19843076',
             'quote': 'the Fluor de Lys-SIRT1 peptide is an artificial SIRT1 substrate'},
            {'claim': 'STAC compounds were validated SIRT1 activators 1000-fold better than resveratrol.',
             'pmid': '18046409',
             'quote': 'These compounds bind to the SIRT1 enzyme-peptide substrate complex at an allosteric site'}],
        'tractability': 'moderate chemistry, discredited pharmacology - 9 structures and 215 potent activities, '
                        'but the activation assays the field was built on were shown to be fluorophore artifacts',
        'unmet_need': 'not a credible programme on current evidence',
        'caveat': 'this is the cautionary entry of the track. A Nature paper, a company acquired for $720M and '
                  'a decade of supplement marketing rest on an assay in which the activation depended on a '
                  'covalently linked fluorophore. Included precisely so the track records a failure rather '
                  'than quietly omitting it',
    },

    'NAMPT': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'NAD+ repletion in aging',
        'evidence_class': 'human-rct',
        'uniprot': 'P43490', 'pdb_ids': ['9WDD', '9IWT', '8Y55'], 'alphafold_model': 'AF-P43490-F1',
        'chembl_target': 'CHEMBL1744525', 'potent_ligands': 4786,
        'clinvar_pathogenic': 19,
        'drugs': [],
        'trials': [{'nct_id': 'NCT02835664', 'pediatric_enrollment': False,
                    'note': 'nicotinamide riboside and metabolic health; completed - the crossover trial that '
                            'found no effect on insulin sensitivity'},
                   {'nct_id': 'NCT05344404', 'pediatric_enrollment': False,
                    'note': 'NR-SAFE, high-dose nicotinamide riboside safety in Parkinson disease; completed'}],
        'claims': [{'pmid': '32320006',
                    'quote': 'no effects of NR were found on insulin sensitivity, mitochondrial function'},
                   {'pmid': '32320006',
                    'quote': 'in 13 healthy overweight or obese men and women'},
                   {'pmid': '29599478',
                    'quote': 'is well tolerated and effectively stimulates NAD+ metabolism in healthy middle-aged and older adults'}],
        'human_evidence': 'LARGELY NEGATIVE, and this should be stated plainly. NAD+ precursors do what they '
                          'say biochemically - NR raises NAD+ metabolites in human skeletal muscle and is well '
                          'tolerated - but the downstream clinical benefit has not appeared. A randomised '
                          'double-blind crossover trial found no effect on insulin sensitivity, mitochondrial '
                          'function, hepatic or intramyocellular lipid, cardiac energetics or blood pressure.',
        'model_organism_evidence': 'NMN and NR improve healthspan measures and some lifespan measures in aged '
                                   'mice. The gap between that and the human trials is the central problem of '
                                   'the NAD+ field.',
        'failed_claims': [
            {'claim': 'NAD+ precursors improve metabolic health in humans the way they do in mice.',
             'pmid': '32320006',
             'quote': 'However, no effects of NR were found on insulin sensitivity, mitochondrial function, hepatic and intramyocellular lipid accumulation, cardiac energy status, cardiac ejection fraction, ambulatory blood pressure, plasma markers of inflammation, or energy metabolism.'},
            {'claim': 'The NR trials demonstrated physiological benefit in older adults.',
             'pmid': '29599478',
             'quote': 'suggest that, in particular, future clinical trials should further assess the potential benefits'}],
        'tractability': 'excellent chemistry, wrong direction - 85 structures and 4786 activities at '
                        'pChEMBL >= 6, but they are NAMPT INHIBITORS developed as oncology agents; the '
                        'geroscience hypothesis wants more NAD+, not less',
        'unmet_need': 'low - NR and NMN are sold over the counter; the deficit is efficacy, not availability',
        'caveat': 'the 4786-ligand count would read as a strongly tractable target on any automated '
                  'tractability score and is pharmacologically opposite to what this indication needs; '
                  'meanwhile the supplements being sold on this biology have repeatedly null human trials',
    },

    'BCL2L1': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'Senolytic clearance of senescent cells',
        'evidence_class': 'model-organism-only',
        'uniprot': 'Q07817', 'pdb_ids': ['9TLU', '9I9E', '9IGB'], 'alphafold_model': 'AF-Q07817-F1',
        'chembl_target': 'CHEMBL4625', 'potent_ligands': 1506,
        'clinvar_pathogenic': 10,
        'drugs': [{'chembl_id': 'CHEMBL443684', 'name': 'navitoclax'}],
        'trials': [{'nct_id': 'NCT00481091', 'pediatric_enrollment': False,
                    'note': 'navitoclax in CLL; completed. Every navitoclax trial is oncology, none is a '
                            'senolytic aging trial'},
                   {'nct_id': 'NCT03181126', 'pediatric_enrollment': True,
                    'note': 'venetoclax plus navitoclax in relapsed leukaemia, enrols children - for cancer'}],
        'claims': [{'pmid': '30279143',
                    'quote': 'Senescent cells have been demonstrated to play a causal role in driving aging and age-related diseases using genetic and pharmacologic approaches.'},
                   {'pmid': '30616998',
                    'quote': 'Cellular senescence is a key mechanism that drives age-related diseases, but has yet to be targeted therapeutically in humans.'}],
        'human_evidence': 'NONE for aging. Navitoclax is a potent, well-characterised BCL-xL inhibitor with '
                          'extensive human oncology data, and its dose-limiting thrombocytopenia - platelets '
                          'depend on BCL-xL - is why it has never been taken into an aging indication.',
        'model_organism_evidence': 'Navitoclax and genetic p16-positive cell ablation clear senescent cells '
                                   'and improve multiple healthspan measures in mice. This is where essentially '
                                   'all of the senolytic lifespan evidence lives.',
        'failed_claims': [
            {'claim': 'Senolytics have been shown to target senescence therapeutically in humans.',
             'pmid': '30616998',
             'quote': 'Cellular senescence is a key mechanism that drives age-related diseases, but has yet to be targeted therapeutically in humans.'}],
        'tractability': 'excellent - 126 structures and 1506 activities at pChEMBL >= 6; BH3-mimetic chemistry '
                        'is mature',
        'unmet_need': 'the target is drugged; what is missing is an on-target-toxicity solution, since '
                      'BCL-xL inhibition is inherently thrombocytopenic',
        'caveat': 'the best-validated senolytic target has a mechanism-based toxicity that rules out chronic '
                  'dosing in healthy older people, which is exactly the population the hypothesis is about',
    },

    'ABL1': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'Dasatinib as the D of the dasatinib + quercetin senolytic combination',
        'evidence_class': 'human-uncontrolled',
        'uniprot': 'P00519', 'pdb_ids': ['9KS5', '8I7T', '8I7Z'], 'alphafold_model': 'AF-P00519-F1',
        'chembl_target': 'CHEMBL1862', 'potent_ligands': 5204,
        'clinvar_pathogenic': 45,
        'drugs': [{'chembl_id': 'CHEMBL5416410', 'name': 'dasatinib'}],
        'trials': [{'nct_id': 'NCT02874989', 'pediatric_enrollment': False,
                    'note': 'dasatinib + quercetin in IPF, phase 1; completed. The first-in-human senolytic study'},
                   {'nct_id': 'NCT04313634', 'pediatric_enrollment': False,
                    'note': 'senolytics for skeletal health in older humans, phase 2; completed'},
                   {'nct_id': 'NCT03430037', 'pediatric_enrollment': False,
                    'note': 'AFFIRM, fisetin for frailty in older women, phase 2; enrolling by invitation'},
                   {'nct_id': 'NCT04685590', 'pediatric_enrollment': False,
                    'note': 'SToMP-AD, senolytic therapy in Alzheimer disease, phase 2; active not recruiting'}],
        'claims': [{'pmid': '30616998',
                    'quote': 'was conducted in participants with IPF (n = 14) to evaluate feasibility'},
                   {'pmid': '30616998',
                    'quote': 'Physical function evaluated as 6-min walk distance, 4-m gait speed, and chair-stands time was significantly and clinically-meaningfully improved (p < .05).'},
                   {'pmid': '36857968',
                    'quote': 'Twelve participants with IPF aged >50 years were blinded and randomized'}],
        'human_evidence': 'THIN, and much thinner than the mouse data. The famous IPF result is an open-label, '
                          'uncontrolled study in 14 patients whose primary endpoints were retention and '
                          'completion rates - feasibility, not efficacy. When the same group ran the '
                          'placebo-controlled version in 12 patients, the functional measures did not separate.',
        'model_organism_evidence': 'D+Q improves frailty, osteoporosis, cardiovascular function and survival '
                                   'in multiple mouse models, and fisetin extended median and maximum lifespan '
                                   'in wild-type mice treated late in life. All mouse.',
        'failed_claims': [
            {'claim': 'The IPF senolytic trial showed that dasatinib + quercetin improves physical function.',
             'pmid': '30616998',
             'quote': 'The primary endpoints were retention rates and completion rates for planned clinical assessments.'},
            {'claim': 'The randomised follow-up confirmed the open-label functional benefit.',
             'pmid': '36857968',
             'quote': 'these measures do not appear to differ meaningfully between groups'},
            {'claim': 'Fisetin is an established human senolytic.',
             'pmid': '30279143',
             'quote': 'Administration of fisetin to wild-type mice late in life restored tissue homeostasis, reduced age-related pathology, and extended median and maximum lifespan.'}],
        'tractability': 'excellent but off-target for the hypothesis - 85 structures, 5204 potent activities; '
                        'dasatinib is polypharmacological and which kinase produces the senolytic effect is '
                        'not established',
        'unmet_need': 'moderate - both components are cheap and available, so the gap is controlled evidence',
        'caveat': 'ABL1 is where ChEMBL curates dasatinib, but nobody has shown ABL1 inhibition is the '
                  'senolytic mechanism; treating this as an ABL1 programme would be docking against a target '
                  'chosen by a database annotation rather than by biology',
    },

    'GLP1R': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'Cardiometabolic risk reduction as a geroprotective mechanism',
        'evidence_class': 'human-rct',
        'uniprot': 'P43220', 'pdb_ids': ['27XK', '9X20', '9MXU'], 'alphafold_model': 'AF-P43220-F1',
        'chembl_target': 'CHEMBL1784', 'potent_ligands': 2050,
        'clinvar_pathogenic': 6,
        'drugs': [{'chembl_id': 'CHEMBL2108724', 'name': 'semaglutide'},
                  {'chembl_id': 'CHEMBL4297839', 'name': 'tirzepatide'}],
        'trials': [{'nct_id': 'NCT03574597', 'pediatric_enrollment': False,
                    'note': 'SELECT, semaglutide cardiovascular outcomes in obesity without diabetes, '
                            'phase 3, 17604 patients; completed'},
                   {'nct_id': 'NCT06967389', 'pediatric_enrollment': True,
                    'note': 'cardiovascular risk mitigation in children with extreme obesity - GLP-1 '
                            'pharmacology reaching pediatrics'}],
        'claims': [{'pmid': '37952131',
                    'quote': 'A total of 17,604 patients were enrolled'},
                   {'pmid': '37952131',
                    'quote': 'hazard ratio, 0.80; 95% confidence interval, 0.72 to 0.90'},
                   {'pmid': '38740993',
                    'quote': 'weight loss continued over 65 weeks and was sustained for up to 4 years'}],
        'human_evidence': 'STRONGEST HARD-OUTCOME EVIDENCE IN THIS TRACK. SELECT randomised 17,604 adults with '
                          'cardiovascular disease and obesity but no diabetes and cut major adverse '
                          'cardiovascular events by 20% (HR 0.80, 95% CI 0.72-0.90). No other candidate '
                          'geroprotector has a hard-outcome trial of this size.',
        'model_organism_evidence': 'GLP-1 agonists have not been shown to extend lifespan in the NIA '
                                   'Interventions Testing Program. The evidence direction here is the reverse '
                                   'of the rest of the field: strong in humans, absent in mouse lifespan.',
        'failed_claims': [
            {'claim': 'Semaglutide is a proven geroprotective drug that slows aging.',
             'pmid': '37952131',
             'quote': 'Adverse events leading to permanent discontinuation of the trial product occurred in 1461 patients (16.6%) in the semaglutide group'}],
        'tractability': 'excellent - 72 structures including active-state cryo-EM, 2050 potent activities, '
                        'multiple approved agonists',
        'unmet_need': 'low for cardiometabolic disease; unestablished as an aging intervention',
        'caveat': 'SELECT is a cardiovascular-disease trial in people with obesity, not an aging trial; '
                  'reading it as evidence that GLP-1 agonism slows aging is a category error, and 16.6% of '
                  'the treated arm discontinued for adverse events',
    },

    'IGF1R': {
        'arm': 'geroscience-adult', 'pediatric_onset': False,
        'indication': 'Insulin/IGF-1 signalling attenuation, the most conserved longevity pathway',
        'evidence_class': 'model-organism-only',
        'uniprot': 'P08069', 'pdb_ids': ['9NCO', '8TAN', '8PYI'], 'alphafold_model': 'AF-P08069-F1',
        'chembl_target': 'CHEMBL1957', 'potent_ligands': 2978,
        'clinvar_pathogenic': 121,
        'drugs': [{'chembl_id': 'CHEMBL1091644', 'name': 'linsitinib'}],
        'trials': [{'nct_id': 'NCT00004815', 'pediatric_enrollment': True,
                    'note': 'rhIGF-1 in Werner syndrome osteoporosis; completed. Note the direction is IGF-1 '
                            'REPLACEMENT, not attenuation'}],
        'claims': [{'pmid': '12483226',
                    'quote': 'Igf1r(+/-) mice live on average 26% longer than their wild-type littermates (P < 0.02)'},
                   {'pmid': '12483226',
                    'quote': 'using heterozygous knockout mice because null mutants are not viable'},
                   {'pmid': '12483226',
                    'quote': 'These results indicate that the IGF-1 receptor may be a central regulator of mammalian lifespan.'}],
        'human_evidence': 'NONE for longevity. Every IGF1R inhibitor taken into humans was an oncology agent, '
                          'and that programme largely failed on efficacy and hyperglycaemia. No trial has ever '
                          'attenuated IGF-1 signalling in humans for an aging indication.',
        'model_organism_evidence': 'The founding result of the field: Igf1r heterozygous null mice live 26% '
                                   'longer on average (33% in females), and the pathway homologues daf-2 and '
                                   'InR are the canonical lifespan genes in worm and fly.',
        'failed_claims': [
            {'claim': 'Reducing IGF-1 signalling is a viable human longevity intervention.',
             'pmid': '12483226',
             'quote': 'using heterozygous knockout mice because null mutants are not viable'}],
        'tractability': 'excellent chemistry, prohibitive biology - 46 structures and 2978 potent activities '
                        'from the failed oncology campaigns',
        'unmet_need': 'not a tractable human programme; retained as the honest anchor of the mouse evidence',
        'caveat': 'THE PEDIATRIC CONTRAINDICATION. IGF-1 signalling drives childhood growth: attenuating it in '
                  'a growing child causes growth failure, and homozygous loss is not viable. This is the '
                  'clearest case in the track where a robust mouse longevity result must not be carried into '
                  'a pediatric programme',
    },
}


# --------------------------------------------------------------------------- accessors

def list_panels() -> List[str]:
    """Panel keys this module provides. Separate from disease_panels.list_panels() on purpose."""
    return sorted(LONGEVITY_PANEL)


def get_panel(name: str) -> Optional[Dict]:
    return LONGEVITY_PANEL.get(name)


def get_evidence(symbol: str) -> Optional[Dict]:
    return LONGEVITY_EVIDENCE.get(symbol)


def targets_by_arm(arm: str) -> List[Dict]:
    """Panel target records in one arm ('progeroid-pediatric' or 'geroscience-adult')."""
    return [t for t in LONGEVITY_PANEL['Longevity']['targets']
            if (LONGEVITY_EVIDENCE.get(t['symbol']) or {}).get('arm') == arm]


def pediatric_targets() -> List[Dict]:
    """Targets whose disease actually presents in childhood.

    Not the same as the progeroid arm: WRN is progeroid but adolescent-onset, and this function
    is the one a paediatric programme should filter on.
    """
    return [t for t in LONGEVITY_PANEL['Longevity']['targets']
            if (LONGEVITY_EVIDENCE.get(t['symbol']) or {}).get('pediatric_onset')]


def targets_with_human_evidence() -> List[str]:
    """Symbols whose evidence_class reflects data in humans rather than model organisms."""
    human = {'approved-for-this-indication', 'human-rct', 'human-uncontrolled'}
    return sorted(s for s, ev in LONGEVITY_EVIDENCE.items() if ev['evidence_class'] in human)


def failed_claims() -> List[Dict]:
    """Every recorded claim that did not survive checking, flattened for reporting.

    This is the part of the track that is hardest to get from a literature summary and the part
    most worth reading: well-known assertions with the citation that undercuts them.
    """
    out = []
    for symbol, ev in LONGEVITY_EVIDENCE.items():
        for fc in ev.get('failed_claims') or []:
            out.append(dict(fc, symbol=symbol, arm=ev['arm']))
    return out


def summary() -> Dict:
    """Counts the track can be challenged on, computed from the data rather than asserted."""
    arms: Dict[str, int] = {}
    classes: Dict[str, int] = {}
    for ev in LONGEVITY_EVIDENCE.values():
        arms[ev['arm']] = arms.get(ev['arm'], 0) + 1
        classes[ev['evidence_class']] = classes.get(ev['evidence_class'], 0) + 1
    return {
        'targets': len(LONGEVITY_PANEL['Longevity']['targets']),
        'by_arm': arms,
        'by_evidence_class': classes,
        'pediatric_onset': len(pediatric_targets()),
        'failed_claims': len(failed_claims()),
        'trials': sum(len(ev['trials']) for ev in LONGEVITY_EVIDENCE.values()),
        'pediatric_trials': sum(1 for ev in LONGEVITY_EVIDENCE.values()
                                for t in ev['trials'] if t['pediatric_enrollment']),
        'claims': sum(len(ev['claims']) for ev in LONGEVITY_EVIDENCE.values()),
    }
