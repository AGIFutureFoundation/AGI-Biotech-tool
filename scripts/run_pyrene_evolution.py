#!/usr/bin/env python3
"""Main script to run continuous pyrene compound evolution with team agents.

Demonstrates:
- AGI Compounds Pyrene Series 3 generation
- Apoptotic mechanism design (BCL2, FAS, XIAP targets)
- Continuous team agent optimization
- Pediatric safety focus
- High-value target discovery for rare diseases
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

from pyrene_apoptotic_discovery import PyreneSeries3Generator, ApoptosisType
from continuous_compound_evolution import ContinuousCompoundEvolution
from team_agent_orchestration import TeamAgentOrchestrator, AgentRole

async def main():
    """Run full pyrene evolution system."""

    print("\n" + "="*80)
    print("🧬 AGI COMPOUNDS - PYRENE APOPTOTIC DRUG DISCOVERY")
    print("="*80)
    print("\nEnhanced System:")
    print("✓ Pyrene Ring Series 3 (AGI Compounds platform)")
    print("✓ Apoptotic mechanism design (BCL2, FAS, XIAP)")
    print("✓ Continuous evolution with team agents")
    print("✓ Pediatric safety optimization")
    print("✓ Multi-target synergy discovery")

    # Initialize systems
    print("\n" + "-"*80)
    print("Initializing Systems...")
    print("-"*80)

    # Team agent orchestrator
    agent_team = TeamAgentOrchestrator()
    print(f"\n✓ Team Agent Orchestrator initialized")
    print(f"  - Optimizer Agent: {agent_team.agents[AgentRole.OPTIMIZER].role.value}")
    print(f"  - Analyst Agent: {agent_team.agents[AgentRole.ANALYST].role.value}")
    print(f"  - Orchestrator Agent: {agent_team.agents[AgentRole.ORCHESTRATOR].role.value}")

    # Pyrene generator
    generator = PyreneSeries3Generator()
    print(f"\n✓ Pyrene Series Generator initialized")
    print(f"  - Series 3 baseline: {len(generator.series_definitions['series_3'].warheads)} warheads")
    print(f"  - Apoptotic mechanisms: {len(generator.apoptosis_mechanisms)}")
    print(f"  - Warhead library: {len(generator.warhead_library)} compounds")

    # Continuous evolution
    evolution = ContinuousCompoundEvolution(team_agents={
        'optimizer': agent_team.agents[AgentRole.OPTIMIZER],
        'analyst': agent_team.agents[AgentRole.ANALYST],
        'orchestrator': agent_team.agents[AgentRole.ORCHESTRATOR],
    })
    print(f"\n✓ Continuous Evolution Engine initialized")

    # DEMONSTRATION 1: Single target optimization (BCL2 - pediatric lymphoma)
    print("\n" + "="*80)
    print("DEMONSTRATION 1: BCL2 Inhibitors for Pediatric Lymphoma")
    print("="*80)

    print("\n1️⃣  Initial Compound Generation (Series 3)...")
    bcl2_compounds = generator.generate_series3_compounds(
        target_protein='BCL2',
        target_indication='pediatric_lymphoma',
        num_compounds=20,
        apoptotic_mechanism=ApoptosisType.INTRINSIC,
    )

    print(f"\n   Generated {len(bcl2_compounds)} compounds:")
    for i, comp in enumerate(bcl2_compounds[:5], 1):
        print(f"\n   {i}. {comp.compound_id}")
        print(f"      Warheads: {comp.warhead_1} + {comp.warhead_2}")
        print(f"      Predicted affinity: {comp.predicted_potency:.2f} kcal/mol")
        print(f"      Pediatric safety: {comp.pediatric_safety_score:.1%}")
        print(f"      Selectivity: {comp.selectivity_score:.1%}")
        print(f"      Synergy partners: {', '.join(comp.combination_partners)}")

    # DEMONSTRATION 2: Multi-target optimization (FAS + XIAP)
    print("\n\n" + "="*80)
    print("DEMONSTRATION 2: Multi-Target Apoptotic Engineering")
    print("="*80)

    print("\n2️⃣  FAS Agonists for Extrinsic Pathway (pediatric leukemia)...")
    fas_compounds = generator.generate_series3_compounds(
        target_protein='FAS',
        target_indication='pediatric_acute_leukemia',
        num_compounds=15,
        apoptotic_mechanism=ApoptosisType.EXTRINSIC,
    )
    print(f"   ✓ Generated {len(fas_compounds)} FAS agonists")

    print("\n2️⃣  XIAP Antagonists for IAP Suppression (pediatric solid tumors)...")
    xiap_compounds = generator.generate_series3_compounds(
        target_protein='XIAP',
        target_indication='pediatric_solid_tumors',
        num_compounds=15,
        apoptotic_mechanism=ApoptosisType.ANTI_APOPTOTIC,
    )
    print(f"   ✓ Generated {len(xiap_compounds)} XIAP antagonists (SMAC mimetics)")

    # DEMONSTRATION 3: Continuous Evolution Loop (short demo - 10 minutes)
    print("\n\n" + "="*80)
    print("DEMONSTRATION 3: Continuous Team Agent Evolution (1 hour loop)")
    print("="*80)

    print("\n3️⃣  Running continuous evolution with team agents...")
    print("    Optimizing BCL2 inhibitors through iterative cycles...")

    evolution_results = await evolution.run_continuous_evolution(
        target_protein='BCL2',
        target_indication='pediatric_lymphoma',
        duration_hours=0.016,  # 1 minute demo (will show multiple cycles)
    )

    # Print evolution summary
    print(f"\n\n{'='*80}")
    print("📊 EVOLUTION RESULTS")
    print(f"{'='*80}")

    summary = evolution.get_evolution_summary()
    print(f"\nCycles completed: {summary['total_cycles']}")
    print(f"Total compounds generated: {summary['total_compounds_generated']}")
    print(f"Best compound: {summary['best_compound_overall']}")
    print(f"Best score: {summary['best_score']:.4f}")

    if summary['total_cycles'] > 1:
        print(f"Average improvement/cycle: {summary['average_improvement_per_cycle']:.4f}")

    print(f"\nEvolution timeline:")
    for entry in summary['timeline']:
        print(f"  {entry}")

    # DEMONSTRATION 4: High-value pediatric targets
    print("\n\n" + "="*80)
    print("DEMONSTRATION 4: High-Value Pediatric Targets")
    print("="*80)

    pediatric_targets = [
        {
            'protein': 'BCL2',
            'indication': 'pediatric_lymphoma',
            'mechanism': ApoptosisType.INTRINSIC,
            'unmet_need': 'Aggressive B-cell lymphomas',
        },
        {
            'protein': 'survivin',
            'indication': 'pediatric_hepatoblastoma',
            'mechanism': ApoptosisType.ANTI_APOPTOTIC,
            'unmet_need': 'Drug-resistant HBL',
        },
        {
            'protein': 'XIAP',
            'indication': 'pediatric_solid_tumors',
            'mechanism': ApoptosisType.ANTI_APOPTOTIC,
            'unmet_need': 'Multi-drug resistant cancers',
        },
        {
            'protein': 'FAS',
            'indication': 'pediatric_autoimmune',
            'mechanism': ApoptosisType.EXTRINSIC,
            'unmet_need': 'Treatment-resistant AIDs',
        },
        {
            'protein': 'caspase-3',
            'indication': 'pediatric_neuroblastoma',
            'mechanism': ApoptosisType.HYBRID,
            'unmet_need': 'MYCN-amplified NB',
        },
    ]

    print(f"\n🎯 Processing {len(pediatric_targets)} high-value pediatric targets:")

    for i, target_info in enumerate(pediatric_targets, 1):
        print(f"\n{i}. {target_info['protein']} ({target_info['indication']})")
        print(f"   Mechanism: {target_info['mechanism'].value}")
        print(f"   Unmet need: {target_info['unmet_need']}")

        # Generate compounds for each
        compounds = generator.generate_series3_compounds(
            target_protein=target_info['protein'],
            target_indication=target_info['indication'],
            num_compounds=10,
            apoptotic_mechanism=target_info['mechanism'],
        )
        print(f"   Generated {len(compounds)} candidate compounds")

        # Show top compound
        if compounds:
            top = max(compounds, key=evolution._calculate_composite_score)
            print(f"   Top candidate: {top.compound_id}")
            print(f"     - Affinity: {top.predicted_potency:.2f} kcal/mol")
            print(f"     - Safety: {top.pediatric_safety_score:.1%}")
            print(f"     - Partners: {', '.join(top.combination_partners)}")

    # DEMONSTRATION 5: Warhead optimization summary
    print("\n\n" + "="*80)
    print("DEMONSTRATION 5: Warhead Optimization Summary")
    print("="*80)

    print(f"\n🔧 Warhead Library Analysis:")
    print(f"   Total warheads: {len(generator.warhead_library)}")

    warhead_categories = {}
    for wname, wdata in generator.warhead_library.items():
        wtype = wdata['type'].value
        if wtype not in warhead_categories:
            warhead_categories[wtype] = []
        warhead_categories[wtype].append(wname)

    for wtype, warheads in warhead_categories.items():
        print(f"\n   {wtype.upper()}:")
        for warhead in warheads[:3]:
            data = generator.warhead_library[warhead]
            print(f"     - {warhead}")
            print(f"       Potency boost: +{data['potency_boost']:.1f} kcal/mol")
            print(f"       Pediatric safety: {data['pediatric_safety']:.0%}")
            print(f"       Off-target risk: {data['selectivity_risk']:.1%}")

    # Final recommendations
    print("\n\n" + "="*80)
    print("🎯 FINAL RECOMMENDATIONS")
    print("="*80)

    if evolution_results['top_compound']:
        comp = evolution_results['top_compound']
        recs = evolution_results['recommendations']

        print(f"\nRecommended Lead Compound: {comp.compound_id}")
        print(f"Target: {comp.target_protein}")
        print(f"Indication: {comp.target_indication}")
        print(f"\nSynthesis Priority: {recs['synthesis_priority']}")
        print(f"Suggested Combination Partners: {', '.join(recs['suggested_partners'])}")

        print(f"\nNext Experimental Steps:")
        for step in recs['next_experiments']:
            print(f"  • {step}")

        print(f"\nEstimated Timeline:")
        for phase, duration in recs['estimated_timeline'].items():
            print(f"  • {phase.replace('_', ' ').title()}: {duration}")

    print("\n" + "="*80)
    print("✅ PYRENE APOPTOTIC DISCOVERY SYSTEM COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Validate top compounds in biochemical assays")
    print("  2. Perform cellular apoptosis assays")
    print("  3. Test combination strategies with known drugs")
    print("  4. Pediatric formulation development")
    print("  5. IND preparation for clinical trials")
    print("\nStatus: READY FOR SYNTHESIS & TESTING 🚀\n")

if __name__ == '__main__':
    asyncio.run(main())
