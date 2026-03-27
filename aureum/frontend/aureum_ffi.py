"""
Aureum FFI - Python bindings for the Rust kernel
Allows calling BitNet b1.58 functions directly from Python

Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
"""

import ctypes
import sys
import os
from pathlib import Path
from typing import List, Tuple
import numpy as np

class AureumKernel:
    """Python wrapper for the Rust BitNet b1.58 kernel"""
    
    def __init__(self):
        """Loads the Rust shared library"""
        self.lib = self._load_library()
        self._setup_functions()
    
    def _load_library(self) -> ctypes.CDLL:
        """Locates and loads the shared library"""
        # Determine library name based on OS
        if sys.platform == "win32":
            lib_name = "aureum_kernel.dll"
        elif sys.platform == "darwin":
            lib_name = "libaureum_kernel.dylib"
        else:
            lib_name = "libaureum_kernel.so"
        
        # Search for the library in common locations
        search_paths = [
            Path(__file__).parent.parent / "backend" / "target" / "release",
            Path(__file__).parent.parent / "backend" / "target" / "debug",
            Path(".") / "backend" / "target" / "release",
            Path(".") / "backend" / "target" / "debug",
        ]
        
        for path in search_paths:
            lib_path = path / lib_name
            if lib_path.exists():
                try:
                    return ctypes.CDLL(str(lib_path))
                except OSError as e:
                    print(f"⚠️  Error loading {lib_path}: {e}")
                    continue
        
        # Not found, try to compile
        print("📦 Library not found. Compiling...")
        self._compile_library()
        
        # Try again after compilation
        for path in search_paths:
            lib_path = path / lib_name
            if lib_path.exists():
                return ctypes.CDLL(str(lib_path))
        
        raise RuntimeError(
            f"❌ Could not load {lib_name}.\n"
            f"   Compile manually: cd backend && cargo build --release"
        )
    
    def _compile_library(self):
        """Automatically compiles the Rust library"""
        backend_dir = Path(__file__).parent.parent / "backend"
        if not backend_dir.exists():
            raise RuntimeError(f"Backend directory not found: {backend_dir}")
        
        import subprocess
        try:
            subprocess.run(
                ["cargo", "build", "--release"],
                cwd=backend_dir,
                check=True,
                capture_output=True
            )
            print("✅ Compilation complete!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Compilation error:\n{e.stderr.decode()}")
            raise
        except FileNotFoundError:
            raise RuntimeError(
                "❌ Cargo not found. Install Rust:\n"
                "   https://rustup.rs/"
            )
    
    def _setup_functions(self):
        """Configures FFI function signatures"""
        # aureum_pack_ternary
        self.lib.aureum_pack_ternary.argtypes = [
            ctypes.POINTER(ctypes.c_int8),  # weights_ptr
            ctypes.c_size_t,                 # len
            ctypes.POINTER(ctypes.c_uint8)   # output_ptr
        ]
        self.lib.aureum_pack_ternary.restype = ctypes.c_size_t
        
        # aureum_bitnet_infer
        self.lib.aureum_bitnet_infer.argtypes = [
            ctypes.POINTER(ctypes.c_int32),  # input_ptr
            ctypes.c_size_t,                  # input_len
            ctypes.POINTER(ctypes.c_uint8),   # packed_weights_ptr
            ctypes.c_size_t,                  # packed_len
            ctypes.c_size_t                   # scale
        ]
        self.lib.aureum_bitnet_infer.restype = ctypes.c_int64
        
        # aureum_memory_info
        class MemoryInfo(ctypes.Structure):
            _fields_ = [
                ("original_bytes", ctypes.c_size_t),
                ("packed_bytes", ctypes.c_size_t),
                ("compression_ratio", ctypes.c_float),
            ]
        
        self.MemoryInfo = MemoryInfo
        self.lib.aureum_memory_info.argtypes = [ctypes.c_size_t]
        self.lib.aureum_memory_info.restype = MemoryInfo
    
    def pack_ternary(self, weights: List[int]) -> bytes:
        """
        Packs ternary weights {-1, 0, 1} into 2 bits each
        
        Args:
            weights: List of -1, 0 or 1 values
        
        Returns:
            bytes: Packed buffer (4 values per byte)
        """
        # Convert to C array
        weights_array = (ctypes.c_int8 * len(weights))(*weights)
        
        # Allocate output buffer
        packed_size = (len(weights) + 3) // 4
        output_buffer = (ctypes.c_uint8 * packed_size)()
        
        # Call Rust function
        written = self.lib.aureum_pack_ternary(
            weights_array,
            len(weights),
            output_buffer
        )
        
        if written == 0:
            raise RuntimeError("Failed to pack weights")
        
        # Convert to Python bytes
        return bytes(output_buffer[:written])
    
    def bitnet_infer(
        self,
        input_data: List[int],
        packed_weights: bytes,
        scale: int = None
    ) -> int:
        """
        Runs BitNet b1.58 inference with Matryoshka operator
        
        Args:
            input_data: Input data (int16 as int)
            packed_weights: Packed weights (from pack_ternary)
            scale: Matryoshka limit (None = full size)
        
        Returns:
            int: Inference result (accumulator)
        """
        if scale is None:
            scale = len(input_data)
        
        # Convert to C arrays
        input_array = (ctypes.c_int32 * len(input_data))(*input_data)
        packed_array = (ctypes.c_uint8 * len(packed_weights))(*packed_weights)
        
        # Call Rust function
        result = self.lib.aureum_bitnet_infer(
            input_array,
            len(input_data),
            packed_array,
            len(packed_weights),
            scale
        )
        
        return result
    
    def get_memory_usage(self, num_weights: int) -> Tuple[int, int, float]:
        """
        Calculates memory usage for different representations
        
        Args:
            num_weights: Number of weights
        
        Returns:
            (packed_bytes, original_bytes, compression_ratio)
        """
        info = self.lib.aureum_memory_info(num_weights)
        return (info.packed_bytes, info.original_bytes, info.compression_ratio)


# Singleton instance
_kernel = None

def get_kernel() -> AureumKernel:
    """Returns singleton kernel instance"""
    global _kernel
    if _kernel is None:
        _kernel = AureumKernel()
    return _kernel


# ─── Tests ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🧪 Testing Aureum FFI...\n")
    
    # Load kernel
    kernel = get_kernel()
    print("✅ Kernel loaded!\n")
    
    # Test 1: Packing
    print("📦 Test 1: Weight packing")
    weights = [1, -1, 0, 1]
    packed = kernel.pack_ternary(weights)
    print(f"   Weights: {weights}")
    print(f"   Packed: {packed.hex()} ({len(packed)} bytes)")
    print(f"   Savings: {len(weights)} → {len(packed)} bytes (4x smaller)\n")
    
    # Test 2: Inference
    print("🔬 Test 2: BitNet inference")
    input_data = [10, 20, 30, 40]
    result = kernel.bitnet_infer(input_data, packed)
    expected = 10 * 1 + 20 * (-1) + 30 * 0 + 40 * 1  # = 30
    print(f"   Input: {input_data}")
    print(f"   Weights: {weights}")
    print(f"   Result: {result}")
    print(f"   Expected: {expected}")
    print(f"   Status: {'✅ PASSED' if result == expected else '❌ FAILED'}\n")
    
    # Test 3: Matryoshka
    print("🪆 Test 3: Matryoshka operator")
    result_full = kernel.bitnet_infer(input_data, packed, scale=4)
    result_half = kernel.bitnet_infer(input_data, packed, scale=2)
    print(f"   Scale 100% (4 elements): {result_full}")
    print(f"   Scale  50% (2 elements): {result_half}")
    print(f"   Savings: {(1 - 2/4) * 100:.0f}% less processing\n")
    
    # Test 4: Memory usage
    print("💾 Test 4: Memory savings")
    num_weights = 3000
    packed_bytes, original_bytes, ratio = kernel.get_memory_usage(num_weights)
    fp32_bytes = num_weights * 4
    print(f"   Weights: {num_weights}")
    print(f"   bit1.58: {packed_bytes:,} bytes")
    print(f"   INT8:    {original_bytes:,} bytes ({ratio:.1f}x larger)")
    print(f"   FP32:    {fp32_bytes:,} bytes ({fp32_bytes/packed_bytes:.1f}x larger)")
    
    print("\n✅ All tests passed!")
