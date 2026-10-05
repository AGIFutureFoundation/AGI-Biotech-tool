"""Scaling Infrastructure for Enterprise Deployment

Features:
- Service discovery and load balancing
- Distributed caching (Redis-ready)
- Microservice orchestration
- Horizontal scaling configuration
- Health monitoring and auto-recovery
"""

import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class ServiceType(Enum):
    """Types of services in distributed system."""
    API_SERVER = "api_server"
    WORKFLOW_EXECUTOR = "workflow_executor"
    AGENT_ORCHESTRATOR = "agent_orchestrator"
    DATABASE = "database"
    CACHE = "cache"
    MONITOR = "monitor"

class ServiceInstance:
    """Represents a single service instance in cluster."""
    
    def __init__(self, instance_id: str, service_type: ServiceType, 
                 host: str, port: int, capacity: int = 100):
        self.instance_id = instance_id
        self.service_type = service_type
        self.host = host
        self.port = port
        self.capacity = capacity
        self.current_load = 0
        self.healthy = True
        self.created_at = datetime.utcnow().isoformat()
        self.last_heartbeat = datetime.utcnow().isoformat()
        self.requests_handled = 0
        self.error_count = 0
    
    def can_accept_request(self) -> bool:
        """Check if instance can accept more requests."""
        return self.healthy and self.current_load < self.capacity
    
    def get_load_percent(self) -> float:
        """Calculate load as percentage of capacity."""
        return (self.current_load / self.capacity) * 100
    
    def get_health_score(self) -> float:
        """Calculate instance health (0-1)."""
        if not self.healthy:
            return 0.0
        
        error_rate = (self.error_count / max(self.requests_handled, 1))
        load_ratio = self.current_load / self.capacity
        
        # Health = (1 - error_rate) * (1 - load_ratio * 0.5)
        return max(0, (1 - error_rate) * (1 - load_ratio * 0.5))

class LoadBalancer:
    """Distribute requests across service instances."""
    
    def __init__(self):
        self.instances: Dict[ServiceType, List[ServiceInstance]] = {}
        self.routing_policy = "least_loaded"  # or "round_robin", "random"
    
    def register_instance(self, instance: ServiceInstance):
        """Register a new service instance."""
        if instance.service_type not in self.instances:
            self.instances[instance.service_type] = []
        self.instances[instance.service_type].append(instance)
    
    def deregister_instance(self, instance_id: str):
        """Remove instance from load balancer."""
        for service_type in self.instances:
            self.instances[service_type] = [
                i for i in self.instances[service_type] 
                if i.instance_id != instance_id
            ]
    
    def get_instance(self, service_type: ServiceType) -> Optional[ServiceInstance]:
        """Get best instance for service type."""
        instances = self.instances.get(service_type, [])
        available = [i for i in instances if i.can_accept_request()]
        
        if not available:
            return None
        
        if self.routing_policy == "least_loaded":
            return min(available, key=lambda i: i.current_load)
        elif self.routing_policy == "round_robin":
            return available[0]  # Simplified
        else:
            return available[0]
    
    def get_cluster_status(self, service_type: ServiceType) -> Dict:
        """Get status of all instances for a service type."""
        instances = self.instances.get(service_type, [])
        
        return {
            'service_type': service_type.value,
            'total_instances': len(instances),
            'healthy_instances': len([i for i in instances if i.healthy]),
            'avg_load_percent': sum(i.get_load_percent() for i in instances) / max(len(instances), 1),
            'total_capacity': sum(i.capacity for i in instances),
            'current_load': sum(i.current_load for i in instances),
        }

class DistributedCache:
    """Distributed caching layer (Redis-compatible interface)."""
    
    def __init__(self, nodes: List[str] = None):
        self.nodes = nodes or ["cache_node_1", "cache_node_2", "cache_node_3"]
        self.data = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_keys': 0,
        }
    
    def _get_node_for_key(self, key: str) -> str:
        """Consistent hashing to determine cache node."""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return self.nodes[hash_value % len(self.nodes)]
    
    def get(self, key: str):
        """Retrieve value from cache."""
        entry = self.data.get(key)
        if entry is not None:
            if datetime.utcnow() > datetime.fromisoformat(entry['expires_at']):
                del self.data[key]
                self.stats['total_keys'] = len(self.data)
            else:
                self.stats['hits'] += 1
                return entry['value']

        self.stats['misses'] += 1
        return None

    def set(self, key: str, value, ttl_seconds: int = 3600):
        """Store value in cache."""
        if key not in self.data and len(self.data) >= 10000:  # Max keys
            # Evict oldest (dicts preserve insertion order)
            oldest = next(iter(self.data))
            del self.data[oldest]
            self.stats['evictions'] += 1

        self.data[key] = {
            'value': value,
            'node': self._get_node_for_key(key),
            'expires_at': (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat(),
        }
        self.stats['total_keys'] = len(self.data)
    
    def delete(self, key: str) -> bool:
        """Remove key from cache."""
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    def flush_all(self):
        """Clear entire cache."""
        self.data.clear()
        self.stats['evictions'] += 1

class AutoScaler:
    """Automatically scale services based on demand."""
    
    def __init__(self, load_balancer: LoadBalancer):
        self.load_balancer = load_balancer
        self.scaling_policies = {
            'workflow_executor': {'scale_up_threshold': 0.8, 'scale_down_threshold': 0.3},
            'api_server': {'scale_up_threshold': 0.7, 'scale_down_threshold': 0.2},
            'agent_orchestrator': {'scale_up_threshold': 0.75, 'scale_down_threshold': 0.25},
        }
        self.scaling_actions = []
    
    def check_and_scale(self, service_type: ServiceType) -> Optional[Dict]:
        """Check if scaling is needed and take action."""
        status = self.load_balancer.get_cluster_status(service_type)
        policy = self.scaling_policies.get(service_type.value)
        
        if not policy:
            return None
        
        load_percent = status['avg_load_percent']
        
        if load_percent >= policy['scale_up_threshold'] * 100:
            action = {
                'service': service_type.value,
                'action': 'scale_up',
                'reason': f'Load {load_percent:.1f}% exceeds threshold',
                'new_instances': status['total_instances'] + 1,
                'timestamp': datetime.utcnow().isoformat(),
            }
            self.scaling_actions.append(action)
            return action
        
        elif load_percent < policy['scale_down_threshold'] * 100:
            if status['total_instances'] > 1:
                action = {
                    'service': service_type.value,
                    'action': 'scale_down',
                    'reason': f'Load {load_percent:.1f}% below threshold',
                    'new_instances': status['total_instances'] - 1,
                    'timestamp': datetime.utcnow().isoformat(),
                }
                self.scaling_actions.append(action)
                return action
        
        return None

class ServiceMesh:
    """Manage inter-service communication and resilience."""
    
    def __init__(self):
        self.circuit_breakers = {}
        self.routes = {}
        self.retry_policies = {}
    
    def add_route(self, source: ServiceType, destination: ServiceType, 
                  timeout_ms: int = 5000):
        """Define service-to-service route."""
        self.routes[f"{source.value}->{destination.value}"] = {
            'timeout_ms': timeout_ms,
            'retries': 3,
            'backoff_multiplier': 2,
        }
    
    def get_route_policy(self, source: ServiceType, destination: ServiceType) -> Dict:
        """Get policy for service communication."""
        route_key = f"{source.value}->{destination.value}"
        return self.routes.get(route_key, {
            'timeout_ms': 5000,
            'retries': 3,
            'backoff_multiplier': 2,
        })

class ClusterConfig:
    """Configuration for multi-node cluster deployment."""
    
    def __init__(self):
        self.nodes: List[Dict] = [
            {
                'id': 'node_1',
                'role': 'control_plane',
                'host': 'localhost',
                'port': 8000,
                'capacity': 200,
            },
            {
                'id': 'node_2',
                'role': 'worker',
                'host': 'localhost',
                'port': 8001,
                'capacity': 150,
            },
            {
                'id': 'node_3',
                'role': 'worker',
                'host': 'localhost',
                'port': 8002,
                'capacity': 150,
            },
        ]
        self.total_capacity = sum(n['capacity'] for n in self.nodes)
        self.min_replicas = {'workflow_executor': 2, 'api_server': 3}
        self.max_replicas = {'workflow_executor': 10, 'api_server': 20}
    
    def get_deployment_config(self, service_type: ServiceType) -> Dict:
        """Get deployment configuration for service."""
        return {
            'service_type': service_type.value,
            'min_replicas': self.min_replicas.get(service_type.value, 1),
            'max_replicas': self.max_replicas.get(service_type.value, 5),
            'resources': {
                'memory_mb': 512,
                'cpu_cores': 2,
            },
            'health_check': {
                'interval_seconds': 30,
                'timeout_seconds': 5,
                'unhealthy_threshold': 3,
            },
        }

def generate_deployment_manifest() -> Dict:
    """Generate Kubernetes-style deployment manifest."""
    return {
        'api_version': 'v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'biodao-blockchain',
            'namespace': 'production',
            'labels': {'app': 'biodao', 'version': 'phase-6'},
        },
        'spec': {
            'replicas': 3,
            'selector': {'app': 'biodao'},
            'template': {
                'metadata': {'labels': {'app': 'biodao'}},
                'spec': {
                    'containers': [
                        {
                            'name': 'api-server',
                            'image': 'biodao/flask-server:latest',
                            'ports': [{'containerPort': 8000}],
                            'env': [
                                {'name': 'ENVIRONMENT', 'value': 'production'},
                                {'name': 'DATABASE_URL', 'value': 'postgresql://...'},
                            ],
                            'resources': {
                                'requests': {'memory': '512Mi', 'cpu': '500m'},
                                'limits': {'memory': '1Gi', 'cpu': '1000m'},
                            },
                        }
                    ],
                    'affinity': {
                        'pod_anti_affinity': {
                            'required_during_scheduling': [
                                {
                                    'label_selector': {'matchLabels': {'app': 'biodao'}},
                                    'topology_key': 'kubernetes.io/hostname',
                                }
                            ]
                        }
                    },
                },
            },
        },
    }

