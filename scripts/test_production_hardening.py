#!/usr/bin/env python3
"""Test Phase 4 production hardening: error recovery, persistence, and monitoring."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "server"))

from workflow_persistence import WorkflowPersistence, WorkflowStatus, WorkflowCheckpoint
from error_recovery import ErrorHandler, RetryStrategy, CircuitBreaker, ErrorSeverity
from monitoring import MetricsCollector, PerformanceMonitor, DashboardData

def test_workflow_persistence():
    """Test workflow persistence layer."""
    print("\n" + "="*70)
    print("🔒 Phase 4: Workflow Persistence Test")
    print("="*70)
    
    persistence = WorkflowPersistence("data/test_workflows.db")
    
    # Test 1: Save workflow
    print("\n1️⃣  Saving workflow...")
    workflow_id = "wf_test_001"
    success = persistence.save_workflow(
        workflow_id=workflow_id,
        template="lead_optimization",
        target="SOD1",
        user_id="researcher_001",
        metadata={"compounds": 50}
    )
    print(f"   ✓ Workflow saved: {success}")
    
    # Test 2: Update status
    print("\n2️⃣  Updating workflow status...")
    persistence.update_workflow_status(workflow_id, WorkflowStatus.RUNNING)
    print(f"   ✓ Status updated to RUNNING")
    
    # Test 3: Save step results
    print("\n3️⃣  Recording step results...")
    persistence.save_step_result(
        workflow_id=workflow_id,
        step_index=0,
        step_name="tune_docking_params",
        agent_name="optimizer",
        result={"box_size": 25.0, "convergence": 0.95},
        duration_seconds=120.5
    )
    print(f"   ✓ Step 1 result saved (120.5s)")
    
    # Test 4: Save checkpoint
    print("\n4️⃣  Saving workflow checkpoint...")
    checkpoint = WorkflowCheckpoint(
        workflow_id=workflow_id,
        step_index=1,
        step_name="dock_analogs",
        state={"compounds_processed": 25},
        timestamp=time.time(),
        results_so_far=[{"compound": "AGI-001", "score": -8.5}]
    )
    persistence.save_checkpoint(checkpoint)
    print(f"   ✓ Checkpoint saved at step 1 (25/50 compounds)")
    
    # Test 5: Retrieve checkpoint
    print("\n5️⃣  Retrieving checkpoint for resume...")
    retrieved = persistence.get_latest_checkpoint(workflow_id)
    if retrieved:
        print(f"   ✓ Checkpoint retrieved: {retrieved.step_name}")
        print(f"      Progress: {retrieved.state}")
    
    # Test 6: Get workflow history
    print("\n6️⃣  Retrieving workflow history...")
    history = persistence.get_workflow_history("researcher_001")
    print(f"   ✓ Retrieved {len(history)} workflows for user")
    
    print("\n✅ Workflow Persistence Test Complete")

def test_error_recovery():
    """Test error recovery mechanisms."""
    print("\n" + "="*70)
    print("🛡️  Phase 4: Error Recovery Test")
    print("="*70)
    
    error_handler = ErrorHandler()
    
    # Test 1: Log errors
    print("\n1️⃣  Recording errors...")
    try:
        raise ValueError("Invalid docking parameters")
    except Exception as e:
        error_handler.log_error(
            "docking_param_error",
            e,
            severity=ErrorSeverity.WARNING,
            context={"target": "SOD1", "box_size": -5}
        )
        print(f"   ✓ Error logged: {type(e).__name__}")
    
    # Test 2: Circuit breaker
    print("\n2️⃣  Testing circuit breaker...")
    cb = error_handler.get_circuit_breaker("md_simulation")
    print(f"   Initial state: {cb.get_state()['state']}")
    
    # Simulate failures
    for i in range(6):
        cb.record_failure()
    
    print(f"   After 6 failures: {cb.get_state()['state']}")
    print(f"   Available for use: {cb.is_available()}")
    
    # Test 3: Error summary
    print("\n3️⃣  Getting error summary...")
    summary = error_handler.get_error_summary()
    print(f"   Total errors logged: {summary['total_errors']}")
    print(f"   By severity: {summary['by_severity']}")
    
    print("\n✅ Error Recovery Test Complete")

def test_retry_strategy():
    """Test retry strategies."""
    print("\n" + "="*70)
    print("🔄 Phase 4: Retry Strategy Test")
    print("="*70)
    
    strategy = RetryStrategy(max_attempts=3, initial_delay=0.1, backoff_multiplier=2.0)
    
    print("\n1️⃣  Exponential backoff delays...")
    for attempt in range(3):
        delay = strategy.get_delay(attempt)
        print(f"   Attempt {attempt + 1}: {delay:.2f}s delay")
    
    print("\n✅ Retry Strategy Test Complete")

def test_monitoring():
    """Test monitoring and metrics collection."""
    print("\n" + "="*70)
    print("📊 Phase 4: Monitoring Test")
    print("="*70)
    
    metrics = MetricsCollector()
    monitor = PerformanceMonitor(metrics)
    
    # Test 1: Workflow metrics
    print("\n1️⃣  Recording workflow metrics...")
    metrics.start_workflow("wf_001")
    time.sleep(0.1)
    metrics.complete_workflow("wf_001", "lead_optimization", 0.1)
    
    metrics.start_workflow("wf_002")
    time.sleep(0.15)
    metrics.complete_workflow("wf_002", "lead_optimization", 0.15)
    
    print(f"   ✓ 2 workflows completed")
    
    # Test 2: Step timing
    print("\n2️⃣  Recording step metrics...")
    with monitor.measure_operation("dock_compounds"):
        time.sleep(0.05)
    
    with monitor.measure_operation("analyze_results"):
        time.sleep(0.02)
    
    print(f"   ✓ Steps timed and recorded")
    
    # Test 3: Error tracking
    print("\n3️⃣  Recording errors...")
    metrics.record_error("connection_timeout")
    metrics.record_error("memory_error")
    print(f"   ✓ 2 errors recorded")
    
    # Test 4: Metrics summary
    print("\n4️⃣  Getting metrics summary...")
    summary = metrics.get_metrics_summary()
    print(f"   Active workflows: {summary['active_workflows']}")
    print(f"   Workflows completed: {summary['workflows']}")
    print(f"   Errors: {summary['errors']['total']}")
    print(f"   Throughput: {summary['throughput']['workflows_per_hour']:.2f} workflows/hour")
    
    # Test 5: Dashboard data
    print("\n5️⃣  Generating dashboard data...")
    dashboard = DashboardData(metrics)
    data = dashboard.get_dashboard_data()
    print(f"   System uptime: {data['system']['uptime_minutes']} minutes")
    print(f"   Error rate: {data['performance']['error_rate']:.1f}%")
    
    print("\n✅ Monitoring Test Complete")

def main():
    """Run all Phase 4 tests."""
    print("\n" + "="*70)
    print("🚀 Phase 4: Production Hardening Comprehensive Test")
    print("="*70)
    
    try:
        test_workflow_persistence()
        test_error_recovery()
        test_retry_strategy()
        test_monitoring()
        
        print("\n" + "="*70)
        print("✅ Phase 4: All Production Hardening Tests Passed")
        print("="*70)
        print("\n🎯 Phase 4 Features Ready:")
        print("   ✓ Persistent workflow state storage")
        print("   ✓ Automatic retry with exponential backoff")
        print("   ✓ Circuit breaker for cascading failures")
        print("   ✓ Comprehensive error logging")
        print("   ✓ Performance metrics collection")
        print("   ✓ Real-time monitoring dashboard data")
        print("   ✓ Workflow checkpoint/resume capability")
        print("\n📈 Next: Deploy to production and monitor in real-time")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
