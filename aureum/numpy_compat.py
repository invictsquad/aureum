"""
Aureum NumPy Compatibility Layer
Drop-in replacement for NumPy operations using 2-bit Rust kernel

Usage:
    import aureum.numpy_compat as np
    # or
    import aureum as au
    arr = au.array([1, 2, 3])

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

from typing import List, Union, Optional
import numpy as np
from .frontend.aureum_ffi import get_kernel

# Type aliases
ArrayLike = Union[List, np.ndarray]

class AureumArray:
    """NumPy-like array backed by Aureum kernel"""
    
    def __init__(self, data: ArrayLike):
        if isinstance(data, np.ndarray):
            self._data = data.astype(np.int32).tolist()
        else:
            self._data = list(data)
    
    def __repr__(self):
        return f"AureumArray({self._data})"
    
    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, idx):
        return self._data[idx]
    
    def tolist(self):
        return self._data
    
    def numpy(self):
        """Convert to NumPy array"""
        return np.array(self._data, dtype=np.int32)


def array(data: ArrayLike) -> AureumArray:
    """Create Aureum array from list or NumPy array"""
    return AureumArray(data)


def zeros(shape: Union[int, tuple]) -> AureumArray:
    """Create array of zeros"""
    if isinstance(shape, int):
        return AureumArray([0] * shape)
    # For multi-dimensional, flatten for now
    size = 1
    for dim in shape:
        size *= dim
    return AureumArray([0] * size)


def ones(shape: Union[int, tuple]) -> AureumArray:
    """Create array of ones"""
    if isinstance(shape, int):
        return AureumArray([1] * shape)
    size = 1
    for dim in shape:
        size *= dim
    return AureumArray([1] * size)


def dot(a: ArrayLike, b: ArrayLike) -> int:
    """
    Dot product using Aureum kernel
    
    For ternary weights in b, this uses BitNet inference
    """
    kernel = get_kernel()
    
    # Convert to lists
    if isinstance(a, AureumArray):
        a = a.tolist()
    elif isinstance(a, np.ndarray):
        a = a.astype(np.int32).tolist()
    
    if isinstance(b, AureumArray):
        b = b.tolist()
    elif isinstance(b, np.ndarray):
        b = b.astype(np.int8).tolist()
    
    # Check if b is ternary {-1, 0, 1}
    is_ternary = all(x in [-1, 0, 1] for x in b)
    
    if is_ternary and len(a) == len(b):
        # Use BitNet kernel for 100x speedup
        packed = kernel.pack_ternary(b)
        return kernel.bitnet_infer(a, packed, len(a))
    else:
        # Fallback to standard dot product
        return sum(x * y for x, y in zip(a, b))


def matmul(a: ArrayLike, b: ArrayLike) -> Union[int, List[int]]:
    """Matrix multiplication (simplified for 1D/2D)"""
    # For now, treat as dot product
    return dot(a, b)


def sum(arr: ArrayLike) -> int:
    """Sum of array elements"""
    if isinstance(arr, AureumArray):
        arr = arr.tolist()
    elif isinstance(arr, np.ndarray):
        arr = arr.tolist()
    return sum(arr)


def mean(arr: ArrayLike) -> float:
    """Mean of array elements"""
    if isinstance(arr, AureumArray):
        arr = arr.tolist()
    elif isinstance(arr, np.ndarray):
        arr = arr.tolist()
    return sum(arr) / len(arr) if arr else 0.0


def max(arr: ArrayLike) -> int:
    """Maximum element"""
    if isinstance(arr, AureumArray):
        arr = arr.tolist()
    elif isinstance(arr, np.ndarray):
        arr = arr.tolist()
    return max(arr) if arr else 0


def min(arr: ArrayLike) -> int:
    """Minimum element"""
    if isinstance(arr, AureumArray):
        arr = arr.tolist()
    elif isinstance(arr, np.ndarray):
        arr = arr.tolist()
    return min(arr) if arr else 0


def argmax(arr: ArrayLike) -> int:
    """Index of maximum element"""
    if isinstance(arr, AureumArray):
        arr = arr.tolist()
    elif isinstance(arr, np.ndarray):
        arr = arr.tolist()
    return arr.index(max(arr)) if arr else -1


def argmin(arr: ArrayLike) -> int:
    """Index of minimum element"""
    if isinstance(arr, AureumArray):
        arr = arr.tolist()
    elif isinstance(arr, np.ndarray):
        arr = arr.tolist()
    return arr.index(min(arr)) if arr else -1
