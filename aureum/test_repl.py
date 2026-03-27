#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aureum REPL Test
Validates basic functionality of the interactive shell

Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import sys
from pathlib import Path

# Add frontend to path
sys.path.insert(0, str(Path(__file__).parent / "frontend"))

from shell import AureumShell, Tensor


def test_tensor_creation():
    """Tests tensor creation"""
    print("🧪 Test 1: Tensor creation\n")
    
    # BitNet tensor
    tensor_bitnet = Tensor([1024], "bit1.58", "weights")
    assert tensor_bitnet.size == 1024
    assert tensor_bitnet.memory_bytes == 256  # (1024 + 3) // 4
    assert tensor_bitnet.is_bitnet == True
    print(f"✅ BitNet Tensor: {tensor_bitnet}")
    
    # INT16 tensor
    tensor_int16 = Tensor([1024], "int16", "input")
    assert tensor_int16.size == 1024
    assert tensor_int16.memory_bytes == 2048  # 1024 * 2
    assert tensor_int16.is_bitnet == False
    print(f"✅ INT16 Tensor: {tensor_int16}")
    
    print()


def test_memory_calculation():
    """Tests memory calculation"""
    print("🧪 Test 2: Memory calculation\n")
    
    sizes = [1024, 10000, 1000000]
    
    for size in sizes:
        tensor = Tensor([size], "bit1.58", f"test_{size}")
        expected = (size + 3) // 4
        assert tensor.memory_bytes == expected
        
        # Compare with FP32
        fp32_memory = size * 4
        savings = (1 - tensor.memory_bytes / fp32_memory) * 100
        
        print(f"Size {size:>7}: {tensor.memory_bytes:>7} bytes (vs FP32: {fp32_memory:>10} bytes, {savings:.1f}% savings)")
    
    print()


def test_parser():
    """Tests declaration parser"""
    print("🧪 Test 3: Declaration parser\n")
    
    shell = AureumShell()
    
    # Test tensor parsing
    line = "input = tensor(shape=[1024], type=int16)"
    tensor = shell.parse_tensor_declaration(line)
    
    assert tensor is not None
    assert tensor.name == "input"
    assert tensor.shape == [1024]
    assert tensor.dtype == "int16"
    
    print(f"✅ Parsed: {line}")
    print(f"   → {tensor}")
    
    # Test BitNet tensor
    line2 = "weights = tensor(shape=[2048], type=bit1.58)"
    tensor2 = shell.parse_tensor_declaration(line2)
    
    assert tensor2 is not None
    assert tensor2.name == "weights"
    assert tensor2.shape == [2048]
    assert tensor2.dtype == "bit1.58"
    
    print(f"✅ Parsed: {line2}")
    print(f"   → {tensor2}")
    
    print()


def test_ffi_loading():
    """Tests FFI kernel loading"""
    print("🧪 Test 4: FFI kernel loading\n")
    
    try:
        from aureum_ffi import get_kernel
        kernel = get_kernel()
        print("✅ Rust kernel loaded via FFI")
        
        # Test basic operation
        weights = [1, -1, 0, 1]
        packed = kernel.pack_ternary(weights)
        print(f"✅ Packing: {weights} → {len(packed)} bytes")
        
        # Test inference
        input_data = [10, 20, 30, 40]
        result = kernel.bitnet_infer(input_data, packed)
        expected = 30  # 10 - 20 + 0 + 40
        assert result == expected
        print(f"✅ Inference: {result} (expected: {expected})")
        
    except Exception as e:
        print(f"⚠️  Kernel not available: {e}")
        print("   Compile with: cd backend && cargo build --release")
    
    print()


def test_commands():
    """Tests special commands"""
    print("🧪 Test 5: Special commands\n")
    
    shell = AureumShell()
    
    # Test .scale
    assert shell.global_scale is None
    shell.process_command(".scale 512")
    assert shell.global_scale == 512
    print("✅ .scale command working")
    
    # Test .clear
    shell.tensors["test"] = Tensor([100], "bit1.58", "test")
    shell.variables["x"] = 42
    assert len(shell.tensors) > 0
    assert len(shell.variables) > 0
    
    shell.process_command(".clear")
    assert len(shell.tensors) == 0
    assert len(shell.variables) == 0
    assert shell.global_scale is None
    print("✅ .clear command working")
    
    print()


def main():
    """Runs all tests"""
    print("\n" + "="*70)
    print("  AUREUM REPL TESTS")
    print("="*70 + "\n")
    
    try:
        test_tensor_creation()
        test_memory_calculation()
        test_parser()
        test_ffi_loading()
        test_commands()
        
        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70 + "\n")
        
        print("To test the interactive REPL:")
        print("  python main.py --shell")
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
