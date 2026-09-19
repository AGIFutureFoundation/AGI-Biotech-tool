"""Monitoring and observability for production deployments.

Tracks:
- Workflow execution metrics
- Performance statistics
- Resource usage
- System health
- User activity
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
import statistics

class MetricsCollector:
    """Collects and aggregates system metrics."""
    
    def __init__(self):
        self.workflow_times = defaultdict(list)  # workflow_type -> [durations]
        self.step_times = defaultdict(list)       # step_name -> [durations]
        self.error_count = defaultdict(int)       # error_type -> count
        self.success_count = defaultdict(int)     # workflow_type -> count
        self.active_workflows = {}                # workflow_id -> start_time
        self.vr_client_connections = 0
        self.last_reset = datetime.utcnow()
    
    def start_workflow(self, workflow_id: str):
        """Record workflow start."""
        self.active_workflows[workflow_id] = time.time()
    
    def complete_workflow(self, workflow_id: str, workflow_type: str, duration: float):
        """Record workflow completion."""
        self.workflow_times[workflow_type].append(duration)
        self.success_count[workflow_type] += 1
        
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
    
    def record_step(self, step_name: str, duration: float):
        """Record step execution time."""
        self.step_times[step_name].append(duration)
    
    def record_error(self, error_type: str):
        """Record an error."""
        self.error_count[error_type] += 1
    
    def get_metrics_summary(self) -> Dict:
        """Get comprehensive metrics summary."""
        now = datetime.utcnow()
        uptime_seconds = (now - self.last_reset).total_seconds()
        
        # Workflow metrics
        workflow_stats = {}
        for wf_type, times in self.workflow_times.items():
            if times:
                workflow_stats[wf_type] = {
                    'count': self.success_count.get(wf_type, 0),
                    'avg_duration': statistics.mean(times),
                    'min_duration': min(times),
                    'max_duration': max(times),
                    'median_duration': statistics.median(times),
                    'stdev': statistics.stdev(times) if len(times) > 1 else 0,
                }
        
        # Step metrics
        step_stats = {}
        for step_name, times in self.step_times.items():
            if times:
                step_stats[step_name] = {
                    'count': len(times),
                    'avg_duration': statistics.mean(times),
                    'min_duration': min(times),
                    'max_duration': max(times),
                }
        
        # Error metrics
        total_errors = sum(self.error_count.values())
        
        return {
            'timestamp': now.isoformat(),
            'uptime_seconds': uptime_seconds,
            'active_workflows': len(self.active_workflows),
            'vr_clients': self.vr_client_connections,
            'workflows': workflow_stats,
            'steps': step_stats,
            'errors': {
                'total': total_errors,
                'by_type': dict(self.error_count),
            },
            'throughput': {
                'workflows_per_hour': (sum(self.success_count.values()) / max(uptime_seconds / 3600, 1)),
            }
        }
    
    def reset_metrics(self):
        """Reset metrics (for periodic snapshots)."""
        self.workflow_times.clear()
        self.step_times.clear()
        self.error_count.clear()
        self.success_count.clear()
        self.last_reset = datetime.utcnow()

class PerformanceMonitor:
    """Monitors and tracks performance of operations."""
    
    def __init__(self, metrics_collector: MetricsCollector = None):
        self.metrics = metrics_collector or MetricsCollector()
        self.operation_times = []
    
    def measure_operation(self, operation_name: str):
        """Context manager for timing operations."""
        return OperationTimer(operation_name, self.metrics)
    
    def get_performance_report(self) -> Dict:
        """Get detailed performance report."""
        return {
            'metrics': self.metrics.get_metrics_summary(),
            'generated_at': datetime.utcnow().isoformat(),
        }

class OperationTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, metrics: MetricsCollector):
        self.operation_name = operation_name
        self.metrics = metrics
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            # Operation succeeded
            self.metrics.record_step(self.operation_name, duration)
        else:
            # Operation failed
            error_type = exc_type.__name__ if exc_type else 'unknown_error'
            self.metrics.record_error(error_type)

class DashboardData:
    """Aggregates data for monitoring dashboard."""
    
    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
    
    def get_dashboard_data(self) -> Dict:
        """Get data for real-time dashboard."""
        summary = self.metrics.get_metrics_summary()
        
        return {
            'system': {
                'uptime_minutes': int(summary['uptime_seconds'] / 60),
                'active_workflows': summary['active_workflows'],
                'vr_clients_connected': summary['vr_clients'],
            },
            'performance': {
                'avg_workflow_duration': next(
                    iter(summary['workflows'].values()), {}
                ).get('avg_duration', 0),
                'workflows_per_hour': summary['throughput']['workflows_per_hour'],
                'error_rate': self._calculate_error_rate(summary),
            },
            'workflows': summary['workflows'],
            'errors': summary['errors'],
        }
    
    def _calculate_error_rate(self, summary: Dict) -> float:
        """Calculate error rate percentage."""
        total_errors = summary['errors']['total']
        # Extract count from each workflow type's stats
        workflows = summary.get('workflows', {})
        total_workflows = sum(w['count'] for w in workflows.values() if isinstance(w, dict))

        if total_workflows == 0:
            return 0.0

        return (total_errors / total_workflows) * 100

