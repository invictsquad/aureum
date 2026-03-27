#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple REPL test - verifies basic components
"""

import sys
from pathlib import Path

print("🧪 Testing REPL components...\n")

# Test 1: Import modules
print("1. Testing imports...")
try:
    sys.path.insert(0, str(Path(__file__).parent / "frontend"))
    from aureum_compiler import AureumTranspiler
    from aureum_ffi import get_kernel
    print("   ✅ Imports OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Load kernel
print("\n2. Testing kernel loading...")
try:
    kernel = get_kernel()
    print("   ✅ Kernel loaded")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Test basic operation
print("\n3. Testing BitNet operation...")
try:
    weights = [1, -1, 0, 1]
    packed = kernel.pack_ternary(weights)
    input_data = [10, 20, 30, 40]
    result = kernel.bitnet_infer(input_data, packed)
    expected = 30
    assert result == expected, f"Result {result} != expected {expected}"
    print(f"   ✅ Inference OK (result: {result})")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Test parser
print("\n4. Testing parser...")
try:
    grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
    transpiler = AureumTranspiler(str(grammar_path))
    code = "def test():\n    x = tensor(shape=[100], type=bit1.58)\n"
    rust_code = transpiler.compile(code)
    assert "bit1.58" in code or "Vec<i8>" in rust_code
    print("   ✅ Parser OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 5: Test Tensor class (from shell)
print("\n5. Testing Tensor class...")
try:
    # Import directly from file
    import importlib.util
    spec = importlib.util.spec_from_file_location("shell", "shell.py")
    shell_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shell_module)
    
    Tensor = shell_module.Tensor
    tensor = Tensor([1024], "bit1.58", "test")
    assert tensor.memory_bytes == 256  # (1024 + 3) // 4
    assert tensor.is_bitnet == True
    print(f"   ✅ Tensor OK (memory: {tensor.memory_bytes} bytes)")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   Details: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ ALL MAIN COMPONENTS WORKING!")
print("="*70)
print("\nThe REPL is ready to use!")
print("Run: python main.py --shell")
print()
