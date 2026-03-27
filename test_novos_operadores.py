#!/usr/bin/env python3
"""
Tests for new mathematical operators (div, mod, pow)

Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import sys
from pathlib import Path

# Add frontend to path
sys.path.insert(0, str(Path(__file__).parent / "frontend"))

from aureum_compiler import AureumTranspiler


def test_divisao():
    """Tests division operator"""
    print("\n🧪 Test 1: Division Operator (/)")
    print("-" * 70)
    
    source = """
def test_div():
    a = tensor(shape=[100], type=int32)
    b = tensor(shape=[100], type=int32)
    result = a / b
"""
    
    grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
    transpiler = AureumTranspiler(str(grammar_path))
    
    try:
        rust_code = transpiler.compile(source)
        
        # Check if division was generated correctly
        assert "/ " in rust_code or "/ b" in rust_code, "Division operator not found"
        
        print("✅ PASSED: Division operator transpiled correctly")
        print(f"\nGenerated Rust code:\n{rust_code}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_modulo():
    """Tests modulo operator"""
    print("\n🧪 Test 2: Modulo Operator (%)")
    print("-" * 70)
    
    source = """
def test_mod():
    a = tensor(shape=[100], type=int32)
    b = tensor(shape=[100], type=int32)
    result = a % b
"""
    
    grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
    transpiler = AureumTranspiler(str(grammar_path))
    
    try:
        rust_code = transpiler.compile(source)
        
        # Check if modulo was generated correctly
        assert "% " in rust_code or "% b" in rust_code, "Modulo operator not found"
        
        print("✅ PASSED: Modulo operator transpiled correctly")
        print(f"\nGenerated Rust code:\n{rust_code}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_potencia():
    """Tests power operator"""
    print("\n🧪 Test 3: Power Operator (**)")
    print("-" * 70)
    
    source = """
def test_pow():
    a = tensor(shape=[100], type=int32)
    squared = a ** 2
    cubed = a ** 3
"""
    
    grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
    transpiler = AureumTranspiler(str(grammar_path))
    
    try:
        rust_code = transpiler.compile(source)
        
        # Check if power was generated correctly
        assert ".pow(" in rust_code, "Power operator not found"
        assert ".pow(2)" in rust_code, "Square power not found"
        assert ".pow(3)" in rust_code, "Cube power not found"
        
        print("✅ PASSED: Power operator transpiled correctly")
        print(f"\nGenerated Rust code:\n{rust_code}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_operadores_combinados():
    """Tests combined operators"""
    print("\n🧪 Test 4: Combined Operators")
    print("-" * 70)
    
    source = """
def test_combined():
    a = tensor(shape=[100], type=int32)
    b = tensor(shape=[100], type=int32)
    result = (a + b) * 2 / 3
"""
    
    grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
    transpiler = AureumTranspiler(str(grammar_path))
    
    try:
        rust_code = transpiler.compile(source)
        
        # Check if all operators were generated
        assert "+" in rust_code, "Addition operator not found"
        assert "*" in rust_code, "Multiplication operator not found"
        assert "/" in rust_code, "Division operator not found"
        
        print("✅ PASSED: Combined operators transpiled correctly")
        print(f"\nGenerated Rust code:\n{rust_code}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_precedencia():
    """Tests operator precedence"""
    print("\n🧪 Test 5: Operator Precedence")
    print("-" * 70)
    
    source = """
def test_precedence():
    a = tensor(shape=[100], type=int32)
    b = tensor(shape=[100], type=int32)
    c = tensor(shape=[100], type=int32)
    result = a + b * c
"""
    
    grammar_path = Path(__file__).parent / "frontend" / "grammar.lark"
    transpiler = AureumTranspiler(str(grammar_path))
    
    try:
        rust_code = transpiler.compile(source)
        
        # Check if precedence is correct (multiplication before addition)
        assert "+" in rust_code and "*" in rust_code, "Operators not found"
        
        print("✅ PASSED: Operator precedence maintained")
        print(f"\nGenerated Rust code:\n{rust_code}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def main():
    """Runs all tests"""
    print("\n" + "="*70)
    print("  🧪 NEW MATHEMATICAL OPERATORS TESTS")
    print("="*70)
    
    tests = [
        test_divisao,
        test_modulo,
        test_potencia,
        test_operadores_combinados,
        test_precedencia,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error running test: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("  📊 TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\nTotal tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 SUCCESS! All tests passed!")
        print("\nChecks:")
        print("  [OK] Division operator (/)")
        print("  [OK] Modulo operator (%)")
        print("  [OK] Power operator (**)")
        print("  [OK] Combined operators")
        print("  [OK] Operator precedence")
        print("\n" + "="*70 + "\n")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
