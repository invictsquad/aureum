"""
Aureum Elastic System - Native Resilience
Elasticity system that automatically adapts processing scale

Concept: "AI that Breathes"
- Inhale (low load): expands accuracy
- Exhale (high load): contracts accuracy
- Continuous breathing: automatic adaptation

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-26
"""

import ctypes
import time
from typing import Callable, Any, Optional
from functools import wraps
from dataclasses import dataclass

from .aureum_ffi import get_kernel

@dataclass
class ElasticStats:
    """Elastic controller statistics"""
    current_scale: float
    avg_latency_ms: int
    request_count: int
    min_scale: float
    max_scale: float
    target_latency_ms: int


class _ElasticStatsC(ctypes.Structure):
    """C structure for statistics"""
    _fields_ = [
        ("current_scale", ctypes.c_float),
        ("avg_latency_ms", ctypes.c_uint64),
        ("request_count", ctypes.c_size_t),
        ("min_scale", ctypes.c_float),
        ("max_scale", ctypes.c_float),
        ("target_latency_ms", ctypes.c_uint64),
    ]


class ElasticController:
    """
    Elasticity controller for Aureum models
    
    Monitors latency and automatically adjusts scale to keep
    the system responsive even under extreme load.
    
    Example:
        >>> controller = ElasticController(
        ...     min_scale=0.1,      # Minimum 10% accuracy
        ...     max_scale=1.0,      # Maximum 100% accuracy
        ...     target_latency=100  # Always respond in ~100ms
        ... )
        >>> 
        >>> # System adapts automatically
        >>> scale = controller.get_scale()
        >>> # ... execute inference with scale ...
        >>> controller.record_request(latency_ms)
    """
    
    def __init__(
        self,
        min_scale: float = 0.1,
        max_scale: float = 1.0,
        target_latency: int = 100
    ):
        """
        Creates elastic controller
        
        Args:
            min_scale: Minimum scale (0.0 to 1.0)
            max_scale: Maximum scale (0.0 to 1.0)
            target_latency: Target latency in milliseconds
        """
        assert 0.0 < min_scale <= 1.0, "min_scale must be between 0.0 and 1.0"
        assert 0.0 < max_scale <= 1.0, "max_scale must be between 0.0 and 1.0"
        assert min_scale <= max_scale, "min_scale must be <= max_scale"
        
        lib = get_kernel().lib
        
        # Configure FFI signatures
        lib.aureum_elastic_new.argtypes = [
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_uint64
        ]
        lib.aureum_elastic_new.restype = ctypes.c_void_p
        
        lib.aureum_elastic_get_scale.argtypes = [ctypes.c_void_p]
        lib.aureum_elastic_get_scale.restype = ctypes.c_float
        
        lib.aureum_elastic_record.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        lib.aureum_elastic_record.restype = None
        
        lib.aureum_elastic_stats.argtypes = [ctypes.c_void_p, ctypes.POINTER(_ElasticStatsC)]
        lib.aureum_elastic_stats.restype = None
        
        lib.aureum_elastic_free.argtypes = [ctypes.c_void_p]
        lib.aureum_elastic_free.restype = None
        
        # Create controller
        self._controller = lib.aureum_elastic_new(
            ctypes.c_float(min_scale),
            ctypes.c_float(max_scale),
            ctypes.c_uint64(target_latency)
        )
        self._lib = lib
    
    def get_scale(self) -> float:
        """
        Gets current scale
        
        Returns:
            Value between min_scale and max_scale
        """
        return self._lib.aureum_elastic_get_scale(self._controller)
    
    def record_request(self, latency_ms: float):
        """
        Records request latency
        
        Accumulates latencies and adjusts scale periodically
        
        Args:
            latency_ms: Request latency in milliseconds
        """
        self._lib.aureum_elastic_record(
            self._controller,
            ctypes.c_uint64(int(latency_ms))
        )
    
    def get_stats(self) -> ElasticStats:
        """
        Gets controller statistics
        
        Returns:
            ElasticStats with current metrics
        """
        stats_c = _ElasticStatsC()
        self._lib.aureum_elastic_stats(self._controller, ctypes.byref(stats_c))
        
        return ElasticStats(
            current_scale=stats_c.current_scale,
            avg_latency_ms=stats_c.avg_latency_ms,
            request_count=stats_c.request_count,
            min_scale=stats_c.min_scale,
            max_scale=stats_c.max_scale,
            target_latency_ms=stats_c.target_latency_ms,
        )
    
    def __del__(self):
        """Frees controller memory"""
        if hasattr(self, '_controller') and self._controller:
            self._lib.aureum_elastic_free(self._controller)


class ElasticModel:
    """
    Aureum model with automatic elasticity
    
    Automatically adapts processing scale based on load,
    ensuring the system never crashes.
    
    Example:
        >>> from aureum_stdlib import AureumModel
        >>> from elastic import ElasticModel
        >>> 
        >>> base_model = AureumModel(input_dim=512, num_classes=10)
        >>> base_model.load_weights(...)
        >>> 
        >>> elastic_model = ElasticModel(
        ...     model=base_model,
        ...     min_scale=0.1,
        ...     max_scale=1.0,
        ...     target_latency=100
        ... )
        >>> 
        >>> # System adapts automatically
        >>> result = elastic_model.classify(input_data)
        >>> # Low load: 100% accuracy
        >>> # High load: 10% accuracy, but always responds
    """
    
    def __init__(
        self,
        model,
        min_scale: float = 0.1,
        max_scale: float = 1.0,
        target_latency: int = 100
    ):
        """
        Creates elastic model
        
        Args:
            model: Base Aureum model
            min_scale: Minimum scale (0.0 to 1.0)
            max_scale: Maximum scale (0.0 to 1.0)
            target_latency: Target latency in milliseconds
        """
        self.model = model
        self.controller = ElasticController(min_scale, max_scale, target_latency)
    
    def classify(self, input_data, **kwargs):
        """
        Elastic classification
        
        Args:
            input_data: Input vector
            **kwargs: Additional arguments for the model
        
        Returns:
            Classification result
        """
        start = time.time()
        
        # Get current scale
        scale = self.controller.get_scale()
        
        # Calculate effective scale (number of elements to process)
        effective_scale = int(len(input_data) * scale)
        
        # Execute inference with adaptive scale
        # Use only first N elements (Matryoshka)
        scaled_input = input_data[:effective_scale] if effective_scale < len(input_data) else input_data
        result = self.model.classify(scaled_input, **kwargs)
        
        # Record latency
        latency_ms = (time.time() - start) * 1000
        self.controller.record_request(latency_ms)
        
        return result
    
    def embed(self, input_data, **kwargs):
        """Elastic embedding"""
        start = time.time()
        
        scale = self.controller.get_scale()
        effective_scale = int(len(input_data) * scale)
        
        scaled_input = input_data[:effective_scale] if effective_scale < len(input_data) else input_data
        result = self.model.embed(scaled_input, **kwargs)
        
        latency_ms = (time.time() - start) * 1000
        self.controller.record_request(latency_ms)
        
        return result
    
    def get_stats(self) -> ElasticStats:
        """Gets controller statistics"""
        return self.controller.get_stats()


def elastic(
    min_scale: float = 0.1,
    max_scale: float = 1.0,
    target_latency: int = 100
):
    """
    Decorator for elastic functions
    
    Automatically adapts processing scale based on latency.
    
    Args:
        min_scale: Minimum scale (0.0 to 1.0)
        max_scale: Maximum scale (0.0 to 1.0)
        target_latency: Target latency in milliseconds
    
    Example:
        >>> @elastic(min_scale=0.1, max_scale=1.0, target_latency=100)
        ... def my_inference(input_data, scale=1.0):
        ...     # scale is injected automatically
        ...     return model.classify(input_data, scale=scale)
        >>> 
        >>> # System adapts automatically
        >>> result = my_inference(input_data)
    """
    def decorator(func: Callable) -> Callable:
        controller = ElasticController(min_scale, max_scale, target_latency)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.time()
            
            # Inject scale into kwargs
            kwargs['scale'] = controller.get_scale()
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Record latency
            latency_ms = (time.time() - start) * 1000
            controller.record_request(latency_ms)
            
            return result
        
        # Add method to get statistics
        wrapper.get_stats = controller.get_stats
        
        return wrapper
    return decorator


# Usage example
if __name__ == "__main__":
    print("\nElastic System Test\n")
    
    # Create controller
    controller = ElasticController(
        min_scale=0.1,
        max_scale=1.0,
        target_latency=100
    )
    
    print(f"Initial scale: {controller.get_scale():.2f}")
    
    # Simulate low load (low latency)
    print("\nSimulating low load (50ms)...")
    for _ in range(100):
        controller.record_request(50)
    
    stats = controller.get_stats()
    print(f"Scale after low load: {stats.current_scale:.2f}")
    print(f"Average latency: {stats.avg_latency_ms}ms")
    
    # Simulate high load (high latency)
    print("\nSimulating high load (200ms)...")
    for _ in range(100):
        controller.record_request(200)
    
    stats = controller.get_stats()
    print(f"Scale after high load: {stats.current_scale:.2f}")
    print(f"Average latency: {stats.avg_latency_ms}ms")
    
    print("\nSystem adapted automatically!")
    print("Low load: expands accuracy")
    print("High load: contracts accuracy")
    print("\nThe AI that breathes!")
