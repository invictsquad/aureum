"""
Aureum - Ultra-Fast AI Library for Python
Drop-in replacement for NumPy/PyTorch heavy operations

Usage:
    import aureum as au
    
    # Looks like NumPy, runs on 2-bit Rust kernel
    result = au.classify(input, weights)
    embedding = au.embed(text, model)
    
Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

__version__ = "0.1.0"
__author__ = "Luiz Antônio De Lima Mendonça"

# Import core functionality
from .frontend.aureum_stdlib import (
    # High-level API
    AureumModel,
    
    # Core functions (NumPy-like API)
    classify,
    detect,
    embed,
    summarize,
    similarity,
    normalize,
    topk,
    
    # Result types
    ClassifyResult,
    DetectResult,
    SimilarityResult,
)

# Fast API (convenience functions)
try:
    from .fast import (
        fast_compute,
        fast_infer,
        fast_classify,
        fast_embed,
        fast_similarity,
    )
except ImportError:
    # Graceful degradation if dependencies missing
    fast_compute = None
    fast_infer = None
    fast_classify = None
    fast_embed = None
    fast_similarity = None

# NumPy compatibility layer
try:
    from .numpy_compat import (
        array,
        zeros,
        ones,
        dot,
        matmul,
    )
except ImportError:
    array = None
    zeros = None
    ones = None
    dot = None
    matmul = None

# PyTorch compatibility layer
try:
    from .torch_compat import (
        Tensor,
        nn,
        optim,
    )
except ImportError:
    Tensor = None
    nn = None
    optim = None

__all__ = [
    # Version
    '__version__',
    '__author__',
    
    # High-level API
    'AureumModel',
    
    # Core functions
    'classify',
    'detect',
    'embed',
    'summarize',
    'similarity',
    'normalize',
    'topk',
    
    # Result types
    'ClassifyResult',
    'DetectResult',
    'SimilarityResult',
    
    # NumPy compatibility
    'array',
    'zeros',
    'ones',
    'dot',
    'matmul',
    
    # PyTorch compatibility
    'Tensor',
    'nn',
    'optim',
    
    # Fast API
    'fast_compute',
    'fast_infer',
    'fast_classify',
    'fast_embed',
    'fast_similarity',
]

# Print welcome message on import
def _welcome():
    import sys
    if not hasattr(sys, '_aureum_welcomed'):
        sys._aureum_welcomed = True
        print(f"Aureum v{__version__} - Ultra-fast AI with 2-bit weights")
        print("Tip: Use aureum.fast_compute() for 10-100x speedup!")

# Uncomment to show welcome message
# _welcome()
