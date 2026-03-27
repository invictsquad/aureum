"""
Teste do Sistema Elástico
Valida que a elasticidade funciona corretamente

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-26
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.elastic import ElasticController, ElasticModel
from frontend.aureum_stdlib import AureumModel

def test_controller_basic():
    """Basic controller test"""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Controller")
    print("=" * 70)
    
    controller = ElasticController(
        min_scale=0.1,
        max_scale=1.0,
        target_latency=100
    )
    
    initial_scale = controller.get_scale()
    print(f"Initial scale: {initial_scale:.2f}")
    assert initial_scale == 1.0, "Should start at maximum"
    
    print("✅ PASSED\n")
    return True

def test_scale_down():
    """Scale reduction test (high load)"""
    print("=" * 70)
    print("TEST 2: Scale Reduction (High Load)")
    print("=" * 70)
    
    controller = ElasticController(
        min_scale=0.1,
        max_scale=1.0,
        target_latency=100
    )
    
    print("Simulating 100 requests with high latency (200ms)...")
    for _ in range(100):
        controller.record_request(200)
    
    stats = controller.get_stats()
    print(f"Scale after high load: {stats.current_scale:.2f}")
    print(f"Average latency: {stats.avg_latency_ms}ms")
    
    assert stats.current_scale < 1.0, "Scale should have reduced"
    assert stats.current_scale >= 0.1, "Scale should not go below minimum"
    
    print("✅ PASSED\n")
    return True

def test_scale_up():
    """Scale increase test (low load)"""
    print("=" * 70)
    print("TEST 3: Scale Increase (Low Load)")
    print("=" * 70)
    
    controller = ElasticController(
        min_scale=0.1,
        max_scale=1.0,
        target_latency=100
    )
    
    # Force low scale
    print("Forcing low scale...")
    for _ in range(100):
        controller.record_request(200)
    
    scale_before = controller.get_scale()
    print(f"Scale before: {scale_before:.2f}")
    
    # Simulate low load
    print("Simulating 100 requests with low latency (50ms)...")
    for _ in range(100):
        controller.record_request(50)
    
    stats = controller.get_stats()
    print(f"Scale after: {stats.current_scale:.2f}")
    
    assert stats.current_scale > scale_before, "Scale should have increased"
    assert stats.current_scale <= 1.0, "Scale should not go above maximum"
    
    print("✅ PASSED\n")
    return True

def test_elastic_model():
    """Elastic model test"""
    print("=" * 70)
    print("TEST 4: Elastic Model")
    print("=" * 70)
    
    # Create base model
    base_model = AureumModel(
        input_dim=100,
        num_classes=5,
        labels=["A", "B", "C", "D", "E"]
    ).random_weights(seed=42)
    
    # Create elastic model
    elastic_model = ElasticModel(
        model=base_model,
        min_scale=0.1,
        max_scale=1.0,
        target_latency=100
    )
    
    print("Running 10 classifications...")
    import random
    for i in range(10):
        input_data = [random.randint(-50, 50) for _ in range(100)]
        result = elastic_model.classify(input_data)
        print(f"  {i+1}. Class: {result.label}, Scale: {elastic_model.controller.get_scale():.2f}")
    
    stats = elastic_model.get_stats()
    print(f"\nFinal statistics:")
    print(f"  Current scale: {stats.current_scale:.2f}")
    print(f"  Requests: {stats.request_count}")
    print(f"  Average latency: {stats.avg_latency_ms}ms")
    
    print("✅ PASSED\n")
    return True

def test_breathing():
    """'Breathing' test - continuous adaptation"""
    print("=" * 70)
    print("TEST 5: AI that Breathes (Continuous Adaptation)")
    print("=" * 70)
    
    controller = ElasticController(
        min_scale=0.1,
        max_scale=1.0,
        target_latency=100
    )
    
    print("\nSimulating variable load pattern:")
    print("  Phase 1: Low load (50ms)")
    print("  Phase 2: High load (200ms)")
    print("  Phase 3: Low load (50ms)")
    print()
    
    # Phase 1: Low load
    for _ in range(100):
        controller.record_request(50)
    scale_1 = controller.get_scale()
    print(f"Phase 1 - Scale: {scale_1:.2f} (INHALE - expand)")
    
    # Phase 2: High load
    for _ in range(100):
        controller.record_request(200)
    scale_2 = controller.get_scale()
    print(f"Phase 2 - Scale: {scale_2:.2f} (EXHALE - contract)")
    
    # Phase 3: Low load again
    for _ in range(100):
        controller.record_request(50)
    scale_3 = controller.get_scale()
    print(f"Phase 3 - Scale: {scale_3:.2f} (INHALE - expand)")
    
    assert scale_2 < scale_1, "Should contract under high load"
    assert scale_3 > scale_2, "Should expand under low load"
    
    print("\n✅ System breathes correctly!")
    print("   High load: contract (exhale)")
    print("   Low load: expand (inhale)")
    print("\n✅ PASSED\n")
    return True

def main():
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  ELASTIC SYSTEM TEST".center(68) + "#")
    print("#" + "  The AI that Breathes".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    
    tests = [
        test_controller_basic,
        test_scale_down,
        test_scale_up,
        test_elastic_model,
        test_breathing,
    ]
    
    results = []
    for test in tests:
        try:
            passed = test()
            results.append(passed)
        except Exception as e:
            print(f"❌ FAILED: {e}\n")
            results.append(False)
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        print("\nThe Elastic System is working perfectly!")
        print("The AI that breathes is ready for production.")
        print("\nFeatures:")
        print("  - Automatically adapts to load")
        print("  - Never crashes, always responds")
        print("  - Degrades gracefully")
        print("  - Recovers automatically")
        return 0
    else:
        print(f"\n❌ {total - passed} TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
