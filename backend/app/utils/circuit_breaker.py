import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Prevents cascading failures by blocking requests to a service 
    that is known to be failing (e.g. Vector DB down).
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # OPEN, CLOSED, HALF-OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info(f"Circuit Breaker HALF-OPEN for {func.__name__} - Testing service...")
                self.state = "HALF-OPEN"
            else:
                raise CircuitBreakerOpenException(f"Circuit breaker is OPEN. Service {func.__name__} is temporarily unavailable.")

        try:
            result = func(*args, **kwargs)
            
            # If we were half-open and it succeeded, close it
            if self.state == "HALF-OPEN":
                logger.info(f"Circuit Breaker CLOSED for {func.__name__} - Service recovered.")
                self.state = "CLOSED"
                self.failure_count = 0
                
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                if self.state != "OPEN":
                    logger.error(f"Circuit Breaker OPEN for {func.__name__} after {self.failure_count} failures.")
                self.state = "OPEN"
            raise e

def circuit_breaker(failure_threshold: int = 3, recovery_timeout: int = 30):
    cb = CircuitBreaker(failure_threshold, recovery_timeout)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        return wrapper
    return decorator
