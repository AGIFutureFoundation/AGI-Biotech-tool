"""Load testing framework for biodao.blockchain.

Simulates concurrent workflows to test:
- Database performance under load
- API response times
- WebSocket streaming capacity
- Memory usage patterns
- Error recovery under stress
"""

import asyncio
import time
import random
from datetime import datetime
from typing import List, Dict, Callable
from dataclasses import dataclass
import statistics

@dataclass
class LoadTestResult:
    """Result of a single test operation."""
    operation_name: str
    duration_ms: float
    success: bool
    error: str = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

class LoadTestRunner:
    """Orchestrates load testing with concurrent operations."""
    
    def __init__(self, max_concurrent: int = 100, test_duration_seconds: int = 300):
        self.max_concurrent = max_concurrent
        self.test_duration = test_duration_seconds
        self.results: List[LoadTestResult] = []
        self.start_time = None
        self.end_time = None
    
    async def run_concurrent_test(self, 
                                  operation: Callable,
                                  num_operations: int = 100,
                                  operation_name: str = "test_operation") -> Dict:
        """Run concurrent operations and measure performance."""
        print(f"\n🔄 Running {num_operations} concurrent {operation_name}s...")
        
        self.start_time = time.time()
        tasks = []
        
        # Create tasks with rate limiting
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def limited_operation(op_num: int):
            async with semaphore:
                return await self._execute_operation(
                    operation, op_num, operation_name
                )
        
        for i in range(num_operations):
            task = asyncio.create_task(limited_operation(i))
            tasks.append(task)
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self.end_time = time.time()
        
        # Process results
        return self._analyze_results(operation_name, results)
    
    async def _execute_operation(self, operation: Callable, 
                                op_num: int, op_name: str) -> LoadTestResult:
        """Execute a single operation and time it."""
        start = time.time()
        try:
            result = await operation(op_num) if asyncio.iscoroutinefunction(operation) else operation(op_num)
            duration_ms = (time.time() - start) * 1000
            return LoadTestResult(
                operation_name=op_name,
                duration_ms=duration_ms,
                success=True
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            return LoadTestResult(
                operation_name=op_name,
                duration_ms=duration_ms,
                success=False,
                error=str(e)
            )
    
    def _analyze_results(self, operation_name: str, results: List) -> Dict:
        """Analyze test results and generate statistics."""
        successful = [r for r in results if isinstance(r, LoadTestResult) and r.success]
        failed = [r for r in results if isinstance(r, LoadTestResult) and not r.success]
        
        if not successful:
            return {
                'operation': operation_name,
                'total_operations': len(results),
                'success_count': 0,
                'failure_count': len(failed),
                'success_rate': 0.0,
                'status': 'FAILED - No successful operations'
            }
        
        durations = [r.duration_ms for r in successful]
        
        analysis = {
            'operation': operation_name,
            'total_operations': len(results),
            'success_count': len(successful),
            'failure_count': len(failed),
            'success_rate': (len(successful) / len(results)) * 100,
            'performance': {
                'min_ms': min(durations),
                'max_ms': max(durations),
                'avg_ms': statistics.mean(durations),
                'median_ms': statistics.median(durations),
                'p95_ms': sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0],
                'p99_ms': sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 1 else durations[0],
                'stdev_ms': statistics.stdev(durations) if len(durations) > 1 else 0,
            },
            'total_time_seconds': self.end_time - self.start_time,
            'throughput_per_second': len(successful) / (self.end_time - self.start_time),
        }
        
        # Print summary
        self._print_summary(analysis)
        
        return analysis
    
    def _print_summary(self, analysis: Dict):
        """Print test results summary."""
        print(f"\n{'='*70}")
        print(f"📊 Load Test Results: {analysis['operation']}")
        print(f"{'='*70}")
        print(f"Success Rate: {analysis['success_rate']:.1f}% ({analysis['success_count']}/{analysis['total_operations']})")
        print(f"\nPerformance Metrics:")
        print(f"  Min:     {analysis['performance']['min_ms']:.2f}ms")
        print(f"  Max:     {analysis['performance']['max_ms']:.2f}ms")
        print(f"  Avg:     {analysis['performance']['avg_ms']:.2f}ms")
        print(f"  Median:  {analysis['performance']['median_ms']:.2f}ms")
        print(f"  P95:     {analysis['performance']['p95_ms']:.2f}ms")
        print(f"  P99:     {analysis['performance']['p99_ms']:.2f}ms")
        print(f"  StdDev:  {analysis['performance']['stdev_ms']:.2f}ms")
        print(f"\nThroughput:")
        print(f"  {analysis['throughput_per_second']:.2f} ops/second")
        print(f"  Total time: {analysis['total_time_seconds']:.2f}s")

class WorkflowLoadTest:
    """Simulate realistic workflow load."""
    
    def __init__(self, persistence=None):
        self.persistence = persistence
    
    async def simulate_workflow(self, workflow_num: int) -> bool:
        """Simulate a complete workflow execution."""
        try:
            # Simulate workflow steps
            workflow_id = f"load_test_{workflow_num}"
            
            # Step 1: Create workflow (10ms)
            await asyncio.sleep(0.01)
            
            # Step 2: Run docking (simulate 50-100ms)
            await asyncio.sleep(random.uniform(0.05, 0.1))
            
            # Step 3: Analyze results (simulate 20-40ms)
            await asyncio.sleep(random.uniform(0.02, 0.04))
            
            # Step 4: Generate report (simulate 10-20ms)
            await asyncio.sleep(random.uniform(0.01, 0.02))
            
            return True
        except Exception as e:
            print(f"Workflow {workflow_num} failed: {e}")
            return False

class StressTest:
    """Stress test for finding breaking points."""
    
    def __init__(self):
        self.max_concurrent_found = None
        self.breaking_point_found = False
    
    async def run_stress_test(self, operation: Callable, 
                              start_concurrent: int = 10,
                              increment: int = 10,
                              max_test: int = 500) -> Dict:
        """Gradually increase concurrency to find breaking point."""
        print(f"\n🔥 Running stress test (finding breaking point)...")
        
        current_concurrent = start_concurrent
        results = []
        
        while current_concurrent <= max_test and not self.breaking_point_found:
            runner = LoadTestRunner(max_concurrent=current_concurrent)
            result = await runner.run_concurrent_test(
                operation,
                num_operations=current_concurrent,
                operation_name=f"stress_test_{current_concurrent}"
            )
            
            results.append(result)
            
            # Check for breaking point (success rate < 80%)
            if result['success_rate'] < 80:
                self.breaking_point_found = True
                self.max_concurrent_found = current_concurrent - increment
                print(f"\n⚠️  Breaking point found at {current_concurrent} concurrent ops")
                print(f"   Maximum stable: {self.max_concurrent_found}")
            else:
                print(f"✓ {current_concurrent} concurrent ops - OK ({result['success_rate']:.1f}%)")
            
            current_concurrent += increment
        
        if not self.breaking_point_found:
            self.max_concurrent_found = max_test
            print(f"\n✓ System stable up to {max_test} concurrent operations")
        
        return {
            'breaking_point': self.max_concurrent_found,
            'test_results': results
        }

