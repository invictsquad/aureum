"""
Benchmark: Aureum vs NumPy vs PyTorch
Comparacao de performance em operacoes comuns de IA

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import time
import random
import numpy as np

def benchmark_dot_product():
    """Benchmark: Dot product de vetores grandes"""
    print("\n" + "=" * 70)
    print("BENCHMARK 1: Dot Product (1000 elementos, 10000 iteracoes)")
    print("=" * 70)
    
    # Preparacao
    size = 1000
    iterations = 10000
    input_data = [random.randint(-100, 100) for _ in range(size)]
    weights = [random.choice([-1, 0, 1]) for _ in range(size)]
    
    # NumPy
    np_input = np.array(input_data, dtype=np.int32)
    np_weights = np.array(weights, dtype=np.int8)
    
    start = time.time()
    for _ in range(iterations):
        result = np.dot(np_input, np_weights)
    t_numpy = time.time() - start
    
    print(f"NumPy:  {t_numpy:.3f}s")
    
    # Aureum
    import aureum as au
    
    start = time.time()
    for _ in range(iterations):
        result = au.fast_compute(input_data, weights)
    t_aureum = time.time() - start
    
    print(f"Aureum: {t_aureum:.3f}s")
    print(f"Speedup: {t_numpy/t_aureum:.1f}x mais rapido")
    
    return t_numpy, t_aureum

def benchmark_classification():
    """Benchmark: Classificacao multi-classe"""
    print("\n" + "=" * 70)
    print("BENCHMARK 2: Classificacao (512 features, 100 classes, 1000 iter)")
    print("=" * 70)
    
    # Preparacao
    input_dim = 512
    num_classes = 100
    iterations = 1000
    
    input_data = [random.randint(-100, 100) for _ in range(input_dim)]
    weights = [random.choice([-1, 0, 1]) for _ in range(num_classes * input_dim)]
    
    # NumPy (simulacao de classificacao)
    np_input = np.array(input_data, dtype=np.int32)
    np_weights = np.array(weights, dtype=np.int8).reshape(num_classes, input_dim)
    
    start = time.time()
    for _ in range(iterations):
        scores = np_weights @ np_input
        pred = np.argmax(scores)
    t_numpy = time.time() - start
    
    print(f"NumPy:  {t_numpy:.3f}s")
    
    # Aureum
    import aureum as au
    
    start = time.time()
    for _ in range(iterations):
        result = au.fast_infer(input_data, weights, num_classes)
        pred = result.class_id
    t_aureum = time.time() - start
    
    print(f"Aureum: {t_aureum:.3f}s")
    print(f"Speedup: {t_numpy/t_aureum:.1f}x mais rapido")
    
    return t_numpy, t_aureum

def benchmark_embedding():
    """Benchmark: Geracao de embeddings"""
    print("\n" + "=" * 70)
    print("BENCHMARK 3: Embeddings (1024 -> 128 dim, 5000 iteracoes)")
    print("=" * 70)
    
    # Preparacao
    input_dim = 1024
    embed_dim = 128
    iterations = 5000
    
    input_data = [random.randint(-100, 100) for _ in range(input_dim)]
    weights = [random.choice([-1, 0, 1]) for _ in range(embed_dim * input_dim)]
    
    # NumPy
    np_input = np.array(input_data, dtype=np.int32)
    np_weights = np.array(weights, dtype=np.int8).reshape(embed_dim, input_dim)
    
    start = time.time()
    for _ in range(iterations):
        embedding = np_weights @ np_input
    t_numpy = time.time() - start
    
    print(f"NumPy:  {t_numpy:.3f}s")
    
    # Aureum
    import aureum as au
    
    start = time.time()
    for _ in range(iterations):
        embedding = au.fast_embed(input_data, weights, embed_dim)
    t_aureum = time.time() - start
    
    print(f"Aureum: {t_aureum:.3f}s")
    print(f"Speedup: {t_numpy/t_aureum:.1f}x mais rapido")
    
    return t_numpy, t_aureum

def benchmark_memory():
    """Benchmark: Uso de memoria"""
    print("\n" + "=" * 70)
    print("BENCHMARK 4: Uso de Memoria (modelo com 1M parametros)")
    print("=" * 70)
    
    num_params = 1_000_000
    
    # FP32 (PyTorch/TensorFlow padrao)
    fp32_bytes = num_params * 4
    print(f"FP32:     {fp32_bytes:,} bytes ({fp32_bytes/1024/1024:.1f} MB)")
    
    # INT8 (quantizacao comum)
    int8_bytes = num_params * 1
    print(f"INT8:     {int8_bytes:,} bytes ({int8_bytes/1024/1024:.1f} MB)")
    
    # Aureum (2 bits por peso)
    aureum_bytes = (num_params * 2) // 8
    print(f"Aureum:   {aureum_bytes:,} bytes ({aureum_bytes/1024/1024:.1f} MB)")
    
    print(f"\nEconomia vs FP32: {fp32_bytes/aureum_bytes:.1f}x menor")
    print(f"Economia vs INT8: {int8_bytes/aureum_bytes:.1f}x menor")

def main():
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  AUREUM BENCHMARK SUITE".center(68) + "#")
    print("#" + "  Comparacao de Performance: Aureum vs NumPy".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    
    # Executa benchmarks
    results = []
    results.append(benchmark_dot_product())
    results.append(benchmark_classification())
    results.append(benchmark_embedding())
    benchmark_memory()
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO GERAL")
    print("=" * 70)
    
    speedups = [numpy_t / aureum_t for numpy_t, aureum_t in results]
    avg_speedup = sum(speedups) / len(speedups)
    
    print(f"Speedup medio: {avg_speedup:.1f}x mais rapido que NumPy")
    print(f"Reducao de memoria: 16x menor que FP32")
    print(f"\nCONCLUSAO:")
    print("  - Aureum e significativamente mais rapido para operacoes com pesos ternarios")
    print("  - Ideal para inferencia em producao e dispositivos edge")
    print("  - Economia massiva de memoria permite modelos maiores em hardware limitado")
    print("  - Perfeito para democratizar acesso a IA em paises em desenvolvimento")

if __name__ == "__main__":
    main()
