#!/usr/bin/env python3
"""Test the full voice-to-execution pipeline: voice → master agent → orchestrator → streaming."""

import json
import asyncio
import sys
import time
from pathlib import Path

# Add server to path
sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

from master_agent import MasterAgentWithOrchestration
from agent_orchestrator import AgentOrchestrator
from websocket_streaming import StreamingServer

def test_voice_pipeline():
    """Run end-to-end test."""
    print("=" * 70)
    print("🎤 Phase 3: Voice-to-Execution Pipeline Test")
    print("=" * 70)
    
    # Initialize components
    print("\n1️⃣  Initializing Agent Orchestrator...")
    mock_team = {
        'optimizer': {'name': 'Optimizer Agent', 'status': 'ready'},
        'analyst': {'name': 'Analyst Agent', 'status': 'ready'},
        'orchestrator': {'name': 'Orchestrator Agent', 'status': 'ready'},
    }
    orchestrator = AgentOrchestrator(master_agent=None, agent_team=mock_team)
    print("   ✓ Orchestrator ready")
    
    print("\n2️⃣  Initializing Master Agent...")
    master_agent = MasterAgentWithOrchestration(
        orchestrator=orchestrator,
        streaming_server=None  # Would connect in real deployment
    )
    print("   ✓ Master Agent ready")
    print(f"   Name: {master_agent.name}")
    print(f"   Status: {master_agent.status}")
    
    # Test voice commands
    test_commands = [
        "Load SOD1 as the target",
        "Run a lead optimization on SOD1",
        "What's the status of my workflow?",
        "Analyze the results for hotspots",
        "Run MD on the best compound",
        "Generate a paper from these results",
    ]
    
    print("\n3️⃣  Processing Voice Commands...")
    print("─" * 70)
    
    for cmd_idx, voice_cmd in enumerate(test_commands, 1):
        print(f"\n📢 Command {cmd_idx}: \"{voice_cmd}\"")
        
        # Process through master agent
        response = master_agent.process_voice_command(voice_cmd)
        
        print(f"   Intent: {response.get('intent', 'unknown')}")
        print(f"   Message: {response.get('message', 'N/A')}")
        
        if 'workflow_id' in response:
            workflow_id = response['workflow_id']
            print(f"   Workflow ID: {workflow_id}")
            
            # Check workflow status
            print("\n   📊 Workflow Progress:")
            for i in range(3):
                status = orchestrator.get_workflow_progress(workflow_id)
                if status:
                    print(f"      Step {status.get('current_step', 0)}: {status.get('current_step_name', 'unknown')}")
                    print(f"      Progress: {status.get('percent_complete', 0)}%")
                    print(f"      Best Score: {status.get('best_score', 'N/A')} kcal/mol")
                time.sleep(0.5)
        
        if response.get('voice_response'):
            print(f"   🔊 Voice: {response['voice_response']}")
    
    # Test memory suggestions
    print("\n4️⃣  Testing Agent Memory Suggestions...")
    print("─" * 70)

    suggestion = orchestrator.agent_memory.suggest_optimization('SOD1_docking')
    if suggestion:
        print(f"\nSuggestion for SOD1 docking: {suggestion}")
    else:
        print(f"\nNo learned patterns yet for SOD1. Will learn from first optimization run.")
    
    # Test workflow listing
    print("\n5️⃣  Active Workflows...")
    print("─" * 70)
    
    workflows = master_agent.list_active_workflows()
    print(f"\nTotal active workflows: {len(workflows)}")
    
    for wf in workflows[:3]:
        print(f"\n  Workflow: {wf.get('workflow_id', 'unknown')[:8]}...")
        print(f"  Template: {wf.get('template', 'unknown')}")
        print(f"  Target: {wf.get('target', 'unknown')}")
        print(f"  Status: {wf.get('status', {}).get('status', 'unknown')}")
    
    print("\n" + "=" * 70)
    print("✅ Voice-to-Execution Pipeline Test Complete")
    print("=" * 70)
    print("\n🚀 Next steps:")
    print("   1. Start the Flask server: python server/server.py")
    print("   2. Open http://localhost:8000 in your browser")
    print("   3. Enable voice input and speak a command")
    print("   4. Watch the workflow execute in real-time in VR")
    print("\n📡 WebSocket streaming:")
    print("   Connect to ws://localhost:8001 for real-time docking/MD/analysis updates")

if __name__ == '__main__':
    test_voice_pipeline()
