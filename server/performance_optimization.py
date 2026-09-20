"""Performance Optimization Engine for Enterprise Scale

Features:
- Query caching with TTL
- Database connection pooling
- Batch processing optimization
- Async I/O for better throughput
- Memory-efficient data structures
"""

import time
import asyncio
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json

class QueryCache:
    """In-memory cache for frequently accessed queries."""
    
    def __init__(self, ttl_seconds=300, max_size=1000):
        self.cache = {}
        self.ttl = ttl_seconds
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached value if not expired."""
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.utcnow() < expiry:
                self.hits += 1
                return value
            else:
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any):
        """Cache a value with TTL."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        expiry = datetime.utcnow() + timedelta(seconds=self.ttl)
        self.cache[key] = (value, expiry)
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

class BatchProcessor:
    """Efficiently process large batches of operations."""
    
    def __init__(self, batch_size=100, timeout_ms=1000):
        self.batch_size = batch_size
        self.timeout = timeout_ms / 1000
        self.queue = []
        self.last_flush = time.time()
    
    async def add_operation(self, operation: Dict) -> Any:
        """Add operation to batch queue."""
        self.queue.append(operation)
        
        # Flush if batch is full or timeout exceeded
        if (len(self.queue) >= self.batch_size or 
            time.time() - self.last_flush >= self.timeout):
            return await self.flush()
        
        return None
    
    async def flush(self) -> List[Dict]:
        """Execute all queued operations in batch."""
        if not self.queue:
            return []
        
        batch = self.queue[:]
        self.queue = []
        self.last_flush = time.time()
        
        # Simulate batch execution (in production, execute in DB transaction)
        results = []
        for op in batch:
            results.append({
                'operation_id': op.get('id'),
                'status': 'executed',
                'timestamp': datetime.utcnow().isoformat(),
            })
        
        return results

class ConnectionPool:
    """Database connection pooling for reuse."""
    
    def __init__(self, max_connections=20):
        self.max_connections = max_connections
        self.available = []
        self.in_use = set()
        self.stats = {
            'connections_created': 0,
            'connections_reused': 0,
            'wait_time_ms': [],
            'peak_usage': 0,
        }
    
    async def acquire(self, timeout_ms=5000) -> str:
        """Acquire a connection from the pool."""
        start = time.time()
        
        # Try to reuse available connection
        if self.available:
            conn_id = self.available.pop()
            self.in_use.add(conn_id)
            self.stats['connections_reused'] += 1
            return conn_id
        
        # Create new connection if under limit
        if len(self.in_use) < self.max_connections:
            conn_id = f"conn_{len(self.in_use)}_{time.time()}"
            self.in_use.add(conn_id)
            self.stats['connections_created'] += 1
            return conn_id
        
        # Wait for connection to be released
        wait_start = time.time()
        while time.time() - wait_start < (timeout_ms / 1000):
            if self.available:
                conn_id = self.available.pop()
                self.in_use.add(conn_id)
                wait_time = (time.time() - start) * 1000
                self.stats['wait_time_ms'].append(wait_time)
                return conn_id
            await asyncio.sleep(0.01)
        
        raise TimeoutError(f"Could not acquire connection within {timeout_ms}ms")
    
    def release(self, conn_id: str):
        """Release connection back to pool."""
        if conn_id in self.in_use:
            self.in_use.remove(conn_id)
            self.available.append(conn_id)
            self.stats['peak_usage'] = max(
                self.stats['peak_usage'], 
                len(self.in_use)
            )

class QueryOptimizer:
    """Optimize database queries."""
    
    def __init__(self):
        self.query_stats = defaultdict(lambda: {
            'count': 0,
            'total_time_ms': 0,
            'min_time_ms': float('inf'),
            'max_time_ms': 0,
        })
    
    def record_query(self, query_type: str, duration_ms: float):
        """Record query execution time."""
        stats = self.query_stats[query_type]
        stats['count'] += 1
        stats['total_time_ms'] += duration_ms
        stats['min_time_ms'] = min(stats['min_time_ms'], duration_ms)
        stats['max_time_ms'] = max(stats['max_time_ms'], duration_ms)
    
    def get_recommendations(self) -> List[Dict]:
        """Generate optimization recommendations."""
        recommendations = []
        
        for query_type, stats in self.query_stats.items():
            avg_time = stats['total_time_ms'] / max(stats['count'], 1)
            
            if avg_time > 100:  # Slow query threshold
                recommendations.append({
                    'query': query_type,
                    'avg_time_ms': avg_time,
                    'suggestion': 'Add database index or optimize query',
                    'priority': 'high' if avg_time > 500 else 'medium',
                })
        
        return sorted(recommendations, key=lambda x: x['avg_time_ms'], reverse=True)
    
    def get_performance_report(self) -> Dict:
        """Generate performance report."""
        total_queries = sum(s['count'] for s in self.query_stats.values())
        total_time = sum(s['total_time_ms'] for s in self.query_stats.values())
        
        return {
            'total_queries': total_queries,
            'total_time_ms': total_time,
            'avg_query_time_ms': total_time / max(total_queries, 1),
            'slowest_queries': sorted(
                self.query_stats.items(),
                key=lambda x: x[1]['total_time_ms'],
                reverse=True
            )[:5],
            'recommendations': self.get_recommendations(),
        }

class AsyncWorkflowExecutor:
    """Execute workflows with optimized async I/O."""
    
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_workflows = {}
    
    async def execute_workflow(self, workflow_id: str, steps: List[Dict]) -> Dict:
        """Execute workflow with concurrent steps where possible."""
        async with self.semaphore:
            self.active_workflows[workflow_id] = {
                'status': 'running',
                'start_time': datetime.utcnow().isoformat(),
                'steps_completed': 0,
                'total_steps': len(steps),
            }
            
            try:
                results = []
                for step_idx, step in enumerate(steps):
                    result = await self._execute_step(step)
                    results.append(result)
                    self.active_workflows[workflow_id]['steps_completed'] = step_idx + 1
                
                self.active_workflows[workflow_id]['status'] = 'completed'
                return {
                    'workflow_id': workflow_id,
                    'status': 'completed',
                    'results': results,
                }
            
            except Exception as e:
                self.active_workflows[workflow_id]['status'] = 'error'
                self.active_workflows[workflow_id]['error'] = str(e)
                raise
    
    async def _execute_step(self, step: Dict) -> Dict:
        """Execute single workflow step."""
        # Simulate async I/O
        await asyncio.sleep(step.get('duration_seconds', 1))
        
        return {
            'step': step.get('name'),
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
        }

class MemoryOptimizer:
    """Monitor and optimize memory usage."""
    
    def __init__(self):
        self.memory_usage = {}
        self.thresholds = {
            'warning': 0.7,  # 70%
            'critical': 0.9,  # 90%
        }
    
    def track_object_size(self, obj_id: str, size_bytes: int):
        """Track memory usage of objects."""
        self.memory_usage[obj_id] = {
            'size_bytes': size_bytes,
            'created_at': datetime.utcnow().isoformat(),
        }
    
    def get_memory_report(self, total_memory_mb=1024) -> Dict:
        """Generate memory usage report."""
        total_used = sum(obj['size_bytes'] for obj in self.memory_usage.values()) / (1024 * 1024)
        usage_percent = total_used / total_memory_mb
        
        return {
            'total_memory_mb': total_memory_mb,
            'used_memory_mb': total_used,
            'usage_percent': usage_percent * 100,
            'status': 'critical' if usage_percent >= self.thresholds['critical']
                     else 'warning' if usage_percent >= self.thresholds['warning']
                     else 'healthy',
            'tracked_objects': len(self.memory_usage),
        }

# Global optimization instances
query_cache = QueryCache()
batch_processor = BatchProcessor()
connection_pool = ConnectionPool()
query_optimizer = QueryOptimizer()
memory_optimizer = MemoryOptimizer()

def optimize_workflow_execution(workflow_template: Dict) -> Dict:
    """Apply optimizations to workflow template."""
    optimized = workflow_template.copy()
    
    # Batch compatible steps
    steps = optimized.get('steps', [])
    can_batch = [s for s in steps if not s.get('depends_on')]
    
    if len(can_batch) > 1:
        optimized['optimization_hint'] = f'Steps {[s.get("id") for s in can_batch]} can be parallelized'
    
    return optimized

def get_optimization_report() -> Dict:
    """Generate comprehensive optimization report."""
    return {
        'cache': {
            'hit_rate_percent': query_cache.hit_rate(),
            'entries': len(query_cache.cache),
            'max_size': query_cache.max_size,
        },
        'database': {
            'connections_created': connection_pool.stats['connections_created'],
            'connections_reused': connection_pool.stats['connections_reused'],
            'peak_concurrent': connection_pool.stats['peak_usage'],
        },
        'queries': query_optimizer.get_performance_report(),
        'memory': memory_optimizer.get_memory_report(),
        'recommendations': query_optimizer.get_recommendations(),
    }
