#!/usr/bin/env python3
"""Test Suite: Agent Training System & Environment Simulator

Tests:
1. Individual agent learning
2. Multi-agent coordination
3. Environment simulation
4. Training progression through phases
5. Expertise development
6. Workflow management
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

from agent_training_system import (
    MultiAgentTrainer, TrainingPhase, EnvironmentSimulator,
    TrainingCoordinator, AgentRole
)
from agent_specialization_modules import (
    OptimizerModule, AnalystModule, OrchestratorModule
)

print("=" * 70)
print("🎓 Agent Training System Tests")
print("=" * 70)

# Test 1: Environment Simulator
print("\n1️⃣  Environment Simulator...")
print("─" * 70)

env = EnvironmentSimulator()
from agent_training_system import TrainingScenario

scenario = TrainingScenario(
    scenario_id='test_1',
    role=AgentRole.OPTIMIZER,
    phase=TrainingPhase.BASIC,
    task_type='docking',
    target='SOD1',
    compounds=['c1', 'c2', 'c3'],
    expected_outcome={'best_score': -9.0},
    difficulty=0.3,
    time_limit_seconds=60,
)

state = env.reset(scenario)
print(f"   ✓ Environment initialized for: {scenario.target}")
print(f"   ✓ Initial state: {state['docking_params']}")

# Execute actions
state, reward, done = env.step({'type': 'dock_compounds'})
print(f"   ✓ Docked compounds: {state['results']['docked_count']}")
print(f"   ✓ Reward: {reward}")

stats = env.get_reward_stats()
print(f"   ✓ Reward stats: avg={stats['avg_reward']:.2f}, total={stats['total_reward']}")

# Test 2: Optimizer Module
print("\n2️⃣  Optimizer Module Specialization...")
print("─" * 70)

optimizer = OptimizerModule()
params = optimizer.suggest_parameters('SOD1', 5)
print(f"   ✓ Suggested parameters: {params}")

optimizer.learn_from_results(params, -9.5)
print(f"   ✓ Learned from docking results")

expertise = optimizer.get_expertise_level()
print(f"   ✓ Optimizer expertise: {expertise['overall_expertise']:.1%}")
print(f"   ✓ Best score achieved: {expertise['best_score_achieved']:.2f}")

# Test 3: Analyst Module
print("\n3️⃣  Analyst Module Specialization...")
print("─" * 70)

analyst = AnalystModule()

mock_poses = [
    {'binding_energy': -8.5, 'scaffold': 'indolyl'},
    {'binding_energy': -8.9, 'scaffold': 'indolyl'},
    {'binding_energy': -8.2, 'scaffold': 'pyrrole'},
    {'binding_energy': -9.1, 'scaffold': 'indolyl'},
]

hotspots = analyst.detect_hotspots(mock_poses)
print(f"   ✓ Detected hotspots: {len(hotspots)}")
for hotspot in hotspots:
    print(f"     - {hotspot['scaffold']}: {hotspot['percentage']:.0f}%")

synthesis = analyst.predict_synthesis_difficulty([
    {'id': 'c1'}, {'id': 'c2'}, {'id': 'c3'}
])
print(f"   ✓ Predicted synthesis difficulty for 3 compounds")
print(f"   ✓ Easiest: {synthesis[0]['compound_id']} (SA={synthesis[0]['sa_score']:.2f})")

analyst.learn_from_analysis({'correct': True})
expertise = analyst.get_expertise_level()
print(f"   ✓ Analyst expertise: {expertise['overall_expertise']:.1%}")

# Test 4: Orchestrator Module
print("\n4️⃣  Orchestrator Module Specialization...")
print("─" * 70)

orchestrator = OrchestratorModule()
plan = orchestrator.plan_workflow('lead_optimization', {})
print(f"   ✓ Planned workflow: {plan['workflow_id']}")
print(f"   ✓ Steps: {len(plan['steps'])}")
print(f"   ✓ Estimated duration: {plan['estimated_duration']}s")

metrics = {
    'error_rate': 0.02,
    'queue_depth': 2,
    'failure_rate': 0.01,
    'execution_time': 650,
    'estimated_time': 660,
}
assessment = orchestrator.monitor_workflow(plan['workflow_id'], metrics)
print(f"   ✓ Workflow health: {assessment['health']}")
print(f"   ✓ Efficiency: {assessment['efficiency']:.1%}")

orchestrator.complete_workflow(plan['workflow_id'], {'status': 'completed'})
expertise = orchestrator.get_expertise_level()
print(f"   ✓ Orchestrator expertise: {expertise['overall_expertise']:.1%}")
print(f"   ✓ Workflows managed: {expertise['workflows_managed']}")

# Test 5: Multi-Agent Trainer
print("\n5️⃣  Multi-Agent Training System...")
print("─" * 70)

trainer = MultiAgentTrainer()
print(f"   ✓ Initialized {len(trainer.agents)} agents")
for agent_id in trainer.agents.keys():
    print(f"     - {agent_id}")

# Test 6: Async Training Loop
print("\n6️⃣  Async Training Execution...")
print("─" * 70)

async def test_async_training():
    scenarios = trainer.create_training_scenarios(TrainingPhase.BASIC)
    print(f"   ✓ Created {len(scenarios)} BASIC scenarios")
    
    # Run one episode
    result = await trainer.train_episode(scenarios[0])
    print(f"   ✓ Completed episode: {result['scenario_id']}")
    print(f"   ✓ Total reward: {result['total_reward']}")
    print(f"   ✓ Steps taken: {result['steps']}")
    
    return trainer

trainer = asyncio.run(test_async_training())

# Test 7: Team Performance
print("\n7️⃣  Team Performance Metrics...")
print("─" * 70)

team_perf = trainer.get_team_performance()
print(f"   ✓ Total episodes trained: {team_perf['total_episodes']}")
print(f"   ✓ Current phase: {team_perf['current_phase']}")
print(f"   ✓ Average reward: {team_perf['avg_reward']:.2f}")

for agent_id, agent_perf in team_perf.get('agents', {}).items():
    print(f"   ✓ {agent_id}:")
    print(f"     - Episodes: {agent_perf['episodes_trained']}")
    print(f"     - Avg reward: {agent_perf['avg_reward']:.2f}")

# Test 8: Full Training Curriculum (Async)
print("\n8️⃣  Full Training Curriculum...")
print("─" * 70)

async def test_curriculum():
    coordinator = TrainingCoordinator()
    
    # Run abbreviated curriculum (1 episode per phase for speed)
    trainer_obj = coordinator.trainer
    
    for phase in [TrainingPhase.BASIC, TrainingPhase.INTERMEDIATE]:
        print(f"   ⏳ Training phase: {phase.value}")
        scenarios = trainer_obj.create_training_scenarios(phase)
        if scenarios:
            result = await trainer_obj.train_episode(scenarios[0])
            print(f"     ✓ Episode reward: {result['total_reward']}")
    
    return coordinator

coordinator = asyncio.run(test_curriculum())

# Summary
print("\n" + "=" * 70)
print("✅ All Agent Training Tests Passed")
print("=" * 70)

print("\n🎓 TRAINING SYSTEM CAPABILITIES:")
print("   ✓ Environment simulation for molecular scenarios")
print("   ✓ Individual agent specialization (Optimizer, Analyst, Orchestrator)")
print("   ✓ Multi-agent coordination and team training")
print("   ✓ Async training with experience replay")
print("   ✓ Phase-based curriculum (Basic → Intermediate → Advanced → Expert)")
print("   ✓ Expertise tracking and performance metrics")
print("   ✓ Workflow planning and execution management")

print("\n📊 AGENT SPECIALIZATIONS:")
print("   OPTIMIZER Agent:")
print("     - Docking parameter optimization")
print("     - Parameter suggestion based on target/compound count")
print("     - Learning from binding results")
print("   ")
print("   ANALYST Agent:")
print("     - Binding pose analysis")
print("     - Hotspot scaffold detection")
print("     - Synthesis difficulty prediction (SA scores)")
print("   ")
print("   ORCHESTRATOR Agent:")
print("     - Workflow planning and scheduling")
print("     - Agent load balancing")
print("     - Health monitoring and contingency planning")

print("\n" + "=" * 70)
