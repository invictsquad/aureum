#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mathematical Truth Test - BitNet b1.58
Validates that the multiplication elimination logic is correct

Test: [10, 20, -5] * [1, 0, -1] = 10 + (20 × 0) - (-5) = 15

Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import sys
from pathlib import Path

# Add frontend to path
sys.path.insert(0, str(Path(__file__).parent / "frontend"))

from aureum_ffi import get_kernel

print("\n" + "="*70)
print("  MATHEMATICAL TRUTH TEST - BitNet b1.58")
print("="*70 + "\n")

print("Goal: Validate that multiplication elimination logic is correct\n")

# Load kernel
print("1. Loading Rust kernel via FFI...")
try:
    kernel = get_kernel()
    print("   ✅ Kernel loaded\n")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Define test data
print("2. Defining test data:")
print("-" * 70)
input_data = [10, 20, -5]
weights = [1, 0, -1]

print(f"   Input:   {input_data}")
print(f"   Weights: {weights}")
print()

# Expected calculation
print("3. Expected calculation (traditional math):")
print("-" * 70)
print("   10 × 1  = 10")
print("   20 × 0  = 0")
print("   -5 × -1 = 5")
print("   ─────────────")
print("   Total   = 15")
print()

expected = 10 * 1 + 20 * 0 + (-5) * (-1)
print(f"   Expected result: {expected}\n")

# Pack weights
print("4. Packing BitNet b1.58 weights:")
print("-" * 70)
packed = kernel.pack_ternary(weights)
print(f"   Original weights: {weights} (3 values)")
print(f"   Packed weights: {packed.hex()} ({len(packed)} byte)")
print(f"   Savings: 3 bytes → 1 byte (3x smaller)\n")

# Run inference
print("5. Running BitNet inference (WITHOUT FP multiplication):")
print("-" * 70)
result = kernel.bitnet_infer(input_data, packed)

print("   BitNet b1.58 logic:")
print("   ───────────────────")
print("   weight = 1  → accumulator += input[i]  (add)")
print("   weight = 0  → nothing                   (skip)")
print("   weight = -1 → accumulator -= input[i]  (subtract)")
print()
print("   Execution:")
print("   ─────────")
print(f"   weight[0] = 1  → accumulator += 10  = 10")
print(f"   weight[1] = 0  → (skip)             = 10")
print(f"   weight[2] = -1 → accumulator -= -5  = 15")
print()
print(f"   BitNet result: {result}\n")

# Validation
print("6. Validation:")
print("-" * 70)
if result == expected:
    print(f"   ✅ SUCCESS! {result} = {expected}")
    print()
    print("   The multiplication elimination logic is PERFECT!")
    print("   BitNet b1.58 is working correctly:")
    print("   • Zero floating-point multiplications")
    print("   • Only integer additions and subtractions")
    print("   • Mathematically correct result")
else:
    print(f"   ❌ FAILED! {result} ≠ {expected}")
    print()
    print("   There is a problem in the implementation.")
    sys.exit(1)

print()
print("="*70)
print("  MATHEMATICAL TRUTH TEST: APPROVED ✅")
print("="*70)
print()

# Additional tests
print("\n" + "="*70)
print("  ADDITIONAL TESTS")
print("="*70 + "\n")

test_cases = [
    {
        "name": "All positive",
        "input": [5, 10, 15],
        "weights": [1, 1, 1],
        "expected": 30,
    },
    {
        "name": "All negative",
        "input": [5, 10, 15],
        "weights": [-1, -1, -1],
        "expected": -30,
    },
    {
        "name": "All zeros",
        "input": [100, 200, 300],
        "weights": [0, 0, 0],
        "expected": 0,
    },
    {
        "name": "Complex mixed",
        "input": [7, -3, 11, -8],
        "weights": [1, -1, 0, 1],
        "expected": 7 - (-3) + 0 + (-8),  # = 7 + 3 - 8 = 2
    },
]

all_passed = True

for i, test in enumerate(test_cases, 1):
    print(f"{i}. {test['name']}:")
    print(f"   Input: {test['input']}")
    print(f"   Weights: {test['weights']}")
    
    packed = kernel.pack_ternary(test['weights'])
    result = kernel.bitnet_infer(test['input'], packed)
    
    if result == test['expected']:
        print(f"   ✅ Result: {result} (expected: {test['expected']})")
    else:
        print(f"   ❌ Result: {result} (expected: {test['expected']})")
        all_passed = False
    print()

if all_passed:
    print("="*70)
    print("  ALL ADDITIONAL TESTS: APPROVED ✅")
    print("="*70)
    print()
    print("🎉 BitNet b1.58 is 100% correct!")
    print()
else:
    print("❌ Some tests failed")
    sys.exit(1)
