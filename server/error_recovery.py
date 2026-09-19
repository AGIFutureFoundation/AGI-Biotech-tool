"""Error recovery and resilience layer for workflow execution.

Features:
- Automatic retry with exponential backoff
- Circuit breaker pattern for cascading failures
- Graceful degradation
- Error logging and alerting
- Health checks and diagnostics
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Callable, Optional, Any, Dict
from enum import Enum
import traceback

class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class RetryStrategy:
    """Configurable retry strategy."""
    
    def __init__(self, max_attempts: int = 3, initial_delay: float = 1.0,
                 backoff_multiplier: float = 2.0, max_delay: float = 300.0):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
    
    def get_delay(self, attempt: int) -> float:
        """Get delay for attempt number (0-indexed)."""
        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay)

class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: float = 300.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def is_available(self) -> bool:
        """Check if circuit is available for use."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed > self.recovery_timeout:
                    self.state = "half_open"
                    return True
            return False
        
        # half_open state - allow one request to test
        return True
    
    def get_state(self) -> Dict:
        """Get circuit breaker state."""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None,
        }

class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self):
        self.error_log = []
        self.circuit_breakers = {}
        self.max_log_size = 1000
    
    def log_error(self, error_id: str, error: Exception, 
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 context: Dict = None):
        """Log an error with context."""
        error_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_id': error_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'severity': severity.value,
            'context': context or {},
            'traceback': traceback.format_exc(),
        }
        
        self.error_log.append(error_record)
        
        # Keep log size bounded
        if len(self.error_log) > self.max_log_size:
            self.error_log = self.error_log[-self.max_log_size:]
        
        # Print severe errors
        if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            print(f"[{severity.value.upper()}] {error_id}: {error}")
        
        return error_record
    
    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker()
        return self.circuit_breakers[service]
    
    def get_error_summary(self) -> Dict:
        """Get error summary statistics."""
        return {
            'total_errors': len(self.error_log),
            'by_severity': {
                'critical': len([e for e in self.error_log if e['severity'] == 'critical']),
                'error': len([e for e in self.error_log if e['severity'] == 'error']),
                'warning': len([e for e in self.error_log if e['severity'] == 'warning']),
                'info': len([e for e in self.error_log if e['severity'] == 'info']),
            },
            'recent_errors': self.error_log[-10:],
            'circuit_breakers': {
                name: cb.get_state() for name, cb in self.circuit_breakers.items()
            }
        }

async def retry_with_backoff(func: Callable, *args, strategy: RetryStrategy = None, 
                            error_handler: ErrorHandler = None, **kwargs) -> Any:
    """Execute function with automatic retry and backoff."""
    strategy = strategy or RetryStrategy()
    
    for attempt in range(strategy.max_attempts):
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            if error_handler:
                error_handler.get_circuit_breaker(func.__name__).record_success()
            
            return result
        
        except Exception as e:
            if error_handler:
                error_handler.log_error(
                    f"{func.__name__}_attempt_{attempt + 1}",
                    e,
                    severity=ErrorSeverity.ERROR,
                    context={'attempt': attempt + 1, 'max_attempts': strategy.max_attempts}
                )
                error_handler.get_circuit_breaker(func.__name__).record_failure()
            
            if attempt < strategy.max_attempts - 1:
                delay = strategy.get_delay(attempt)
                await asyncio.sleep(delay)
            else:
                raise

class HealthCheck:
    """Health check for system components."""
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_fn: Callable):
        """Register a health check function."""
        self.checks[name] = check_fn
    
    async def run_checks(self) -> Dict:
        """Run all health checks."""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {},
            'overall_health': 'healthy'
        }
        
        for name, check_fn in self.checks.items():
            try:
                result = await check_fn() if asyncio.iscoroutinefunction(check_fn) else check_fn()
                results['checks'][name] = {
                    'status': 'healthy' if result else 'degraded',
                    'result': result
                }
            except Exception as e:
                results['checks'][name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                results['overall_health'] = 'unhealthy'
        
        # Overall health is healthy only if all checks pass
        if any(c['status'] != 'healthy' for c in results['checks'].values()):
            results['overall_health'] = 'degraded'
        
        return results

