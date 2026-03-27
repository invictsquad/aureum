"""
Tests for Python "Ghost" Integration
Validates that the Python API works correctly

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import sys
import os
import random

# Add parent directory to path to import aureum
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Tests that all imports work"""
    print("Test 1: Imports")
    
    try:
        # Direct import from local __init__.py
        from frontend.aureum_stdlib import AureumModel, ClassifyResult
        from frontend.aureum_ffi import get_kernel
        print("  - basic imports: OK")
        
        # Check classes
        assert AureumModel is not None
        assert ClassifyResult is not None
        print("  - Classes: OK")
        
        # Check kernel
        kernel = get_kernel()
        assert kernel is not None
        print("  - Rust Kernel: OK")
        
        print("PASSED\n")
        return True
    except Exception as e:
        print(f"FAILED: {e}\n")
        return False

def test_fast_compute():
    """Tests fast_compute()"""
    print("Test 2: fast_compute()")
    
    try:
        from frontend.aureum_ffi import get_kernel
        
        # Simple test
        input_data = [10, 20, 30, 40]
        weights = [1, -1, 0, 1]
        
        kernel = get_kernel()
        packed = kernel.pack_ternary(weights)
        result = kernel.bitnet_infer(input_data, packed, len(input_data))
        
        # Check result
        expected = 10 * 1 + 20 * (-1) + 30 * 0 + 40 * 1  # = 30
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"  - Result: {result} (correct)")
        
        print("PASSED\n")
        return True
    except Exception as e:
        print(f"FAILED: {e}\n")
        return False

def test_fast_classify():
    """Tests fast_classify()"""
    print("Test 3: fast_classify()")
    
    try:
        from frontend.aureum_stdlib import classify
        
        # 3 classes, 4 features
        input_data = [10, 20, -5, 8]
        weights = [
             1, 0, -1, 1,  # class 0: score = 23
             0, 1,  1, 0,  # class 1: score = 15
            -1, 1,  0, 1,  # class 2: score = 18
        ]
        labels = ["cat", "dog", "bird"]
        
        result = classify(input_data, weights, 3, labels=labels)
        label = result.label
        
        # Class 0 has highest score
        assert label == "cat", f"Expected 'cat', got '{label}'"
        print(f"  - Classification: {label} (correct)")
        
        print("PASSED\n")
        return True
    except Exception as e:
        print(f"FAILED: {e}\n")
        return False

def test_aureum_model():
    """Tests AureumModel"""
    print("Test 4: AureumModel")
    
    try:
        from frontend.aureum_stdlib import AureumModel
        
        # Create model
        model = AureumModel(
            input_dim=100,
            num_classes=5,
            labels=["A", "B", "C", "D", "E"]
        )
        
        # Initialize random weights
        model.random_weights(seed=42)
        
        # Classify
        input_data = [random.randint(-50, 50) for _ in range(100)]
        result = model.classify(input_data)
        
        # Check result
        assert 0 <= result.class_id < 5
        assert result.label in ["A", "B", "C", "D", "E"]
        print(f"  - Classification: {result.label} (class {result.class_id})")
        print(f"  - Score: {result.score}")
        
        print("PASSED\n")
        return True
    except Exception as e:
        print(f"FAILED: {e}\n")
        return False

def test_embeddings():
    """Tests embedding generation"""
    print("Test 5: Embeddings")
    
    try:
        from frontend.aureum_stdlib import AureumModel
        
        # Create model
        model = AureumModel(
            input_dim=256,
            embed_dim=64
        ).random_weights(seed=42)
        
        # Generate embeddings
        input_a = [random.randint(-50, 50) for _ in range(256)]
        input_b = [random.randint(-50, 50) for _ in range(256)]
        
        emb_a = model.embed(input_a)
        emb_b = model.embed(input_b)
        
        # Check dimensions
        assert len(emb_a) == 64
        assert len(emb_b) == 64
        print(f"  - Dimension: {len(emb_a)} (correct)")
        
        # Calculate similarity
        sim = model.similarity(input_a, input_b)
        print(f"  - Similarity: {sim.score}")
        
        # Identical embeddings should have high similarity
        sim_self = model.similarity(input_a, input_a)
        assert sim_self.score > 0, "Self-similarity should be positive"
        print(f"  - Self-similarity: {sim_self.score} (correct)")
        
        print("PASSED\n")
        return True
    except Exception as e:
        print(f"FAILED: {e}\n")
        return False

def test_numpy_compat():
    """Tests NumPy compatibility"""
    print("Test 6: NumPy Compatibility")
    
    try:
        from frontend.aureum_ffi import get_kernel
        
        # Direct dot product
        a = [10, 20, 30]
        b = [1, 0, -1]
        
        kernel = get_kernel()
        packed = kernel.pack_ternary(b)
        result = kernel.bitnet_infer(a, packed, len(a))
        expected = 10 * 1 + 20 * 0 + 30 * (-1)  # = -20
        assert result == expected
        print(f"  - dot product: {result} (correct)")
        
        print("PASSED\n")
        return True
    except Exception as e:
        print(f"FAILED: {e}\n")
        return False

def test_performance():
    """Tests basic performance"""
    print("Test 7: Performance")
    
    try:
        from frontend.aureum_ffi import get_kernel
        import time
        
        # Prepare large data
        size = 1000
        iterations = 1000
        input_data = [random.randint(-100, 100) for _ in range(size)]
        weights = [random.choice([-1, 0, 1]) for _ in range(size)]
        
        kernel = get_kernel()
        packed = kernel.pack_ternary(weights)
        
        # Benchmark
        start = time.time()
        for _ in range(iterations):
            result = kernel.bitnet_infer(input_data, packed, len(input_data))
        elapsed = time.time() - start
        
        ops_per_sec = iterations / elapsed
        print(f"  - {iterations} operations in {elapsed:.3f}s")
        print(f"  - {ops_per_sec:.0f} ops/s")
        
        # Should be fast (>100 ops/s)
        assert ops_per_sec > 100, f"Performance too low: {ops_per_sec:.0f} ops/s"
        
        print("PASSED\n")
        return True
    except Exception as e:
        print(f"FAILED: {e}\n")
        return False

def main():
    print("\n" + "=" * 70)
    print("PYTHON 'GHOST' INTEGRATION TESTS")
    print("=" * 70 + "\n")
    
    tests = [
        test_imports,
        test_fast_compute,
        test_fast_classify,
        test_aureum_model,
        test_embeddings,
        test_numpy_compat,
        test_performance,
    ]
    
    results = []
    for test in tests:
        try:
            passed = test()
            results.append(passed)
        except Exception as e:
            print(f"CRITICAL ERROR: {e}\n")
            results.append(False)
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\nSTATUS: ALL TESTS PASSED")
        print("\nThe Python 'Ghost' integration is working perfectly!")
        print("Users can import Aureum as a Python library and")
        print("accelerate their bottlenecks without rewriting existing code.")
        return 0
    else:
        print(f"\nSTATUS: {total - passed} TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
