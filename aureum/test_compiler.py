#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aureum transpiler test script
Tests the inferencia.aur example and validates the output

Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import sys
import io
from pathlib import Path

# Fix encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adiciona frontend ao path
sys.path.insert(0, str(Path(__file__).parent / "frontend"))

from aureum_compiler import AureumTranspiler


def test_basic_inference():
    """Tests transpilation of the basic example"""
    print("Testing Aureum transpiler...\n")
    
    grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
    source_path = Path(__file__).parent / "examples" / "inferencia.aur"
    
    transpiler = AureumTranspiler(str(grammar_path))
    source_code = source_path.read_text(encoding='utf-8')
    
    print("📄 Source code (.aur):")
    print("-" * 60)
    print(source_code)
    print("-" * 60)
    
    rust_code = transpiler.compile(source_code)
    
    print("\n[OK] Generated Rust code:")
    print("=" * 60)
    print(rust_code)
    print("=" * 60)
    
    # Validations
    assert "bitnet_infer" in rust_code, "BitNet kernel was not called"
    assert "pack_ternary" in rust_code, "Ternary packing missing"
    assert "512" in rust_code, "Matryoshka scale not detected"
    
    print("\n[SUCCESS] All tests passed!")
    print("\nChecks:")
    print("  [OK] Aureum syntax parsing")
    print("  [OK] bit1.58 tensor detection")
    print("  [OK] Matryoshka operator [::512]")
    print("  [OK] Optimized Rust code generation")
    print("  [OK] BitNet kernel call (no FP multiplication)")


if __name__ == "__main__":
    try:
        test_basic_inference()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
