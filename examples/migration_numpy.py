"""
Exemplo de Migracao Gradual: NumPy -> Aureum
Demonstra como substituir operacoes pesadas do NumPy por Aureum

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import time
import numpy as np

# ANTES: Codigo NumPy puro (lento)
def numpy_version():
    print("=== VERSAO NUMPY (LENTA) ===\n")
    
    # Dados de entrada
    input_data = np.random.randint(-100, 100, size=1000, dtype=np.int32)
    weights = np.random.choice([-1, 0, 1], size=1000)
    
    # Operacao pesada: dot product repetido
    start = time.time()
    results = []
    for _ in range(1000):
        result = np.dot(input_data, weights)
        results.append(result)
    elapsed = time.time() - start
    
    print(f"Tempo: {elapsed:.3f}s")
    print(f"Resultado final: {results[-1]}\n")
    return elapsed

# DEPOIS: Codigo Aureum (rapido)
def aureum_version():
    print("=== VERSAO AUREUM (RAPIDA) ===\n")
    
    import aureum as au
    
    # Mesmos dados (compativel com NumPy)
    input_data = list(np.random.randint(-100, 100, size=1000, dtype=np.int32))
    weights = list(np.random.choice([-1, 0, 1], size=1000))
    
    # Operacao pesada: dot product repetido usando kernel Rust
    start = time.time()
    results = []
    for _ in range(1000):
        result = au.fast_compute(input_data, weights)
        results.append(result)
    elapsed = time.time() - start
    
    print(f"Tempo: {elapsed:.3f}s")
    print(f"Resultado final: {results[-1]}\n")
    return elapsed

# HIBRIDO: Migracao gradual (melhor abordagem)
def hybrid_version():
    print("=== VERSAO HIBRIDA (MIGRACAO GRADUAL) ===\n")
    print("Mantem codigo NumPy existente, acelera apenas gargalos\n")
    
    import aureum as au
    
    # Codigo NumPy existente (nao precisa mudar)
    input_data = np.random.randint(-100, 100, size=1000, dtype=np.int32)
    weights = np.random.choice([-1, 0, 1], size=1000)
    
    # Pre-processamento em NumPy (rapido)
    input_normalized = input_data / np.max(np.abs(input_data))
    
    # Operacao pesada: delega para Aureum
    start = time.time()
    results = []
    for _ in range(1000):
        # Converte apenas na hora de usar Aureum
        result = au.fast_compute(
            input_data.tolist(),
            weights.tolist()
        )
        results.append(result)
    elapsed = time.time() - start
    
    # Pos-processamento em NumPy (rapido)
    final_result = np.mean(results)
    
    print(f"Tempo: {elapsed:.3f}s")
    print(f"Resultado final: {final_result:.2f}\n")
    return elapsed

if __name__ == "__main__":
    print("DEMONSTRACAO: Migracao Gradual NumPy -> Aureum\n")
    print("Cenario: 1000 dot products de vetores com 1000 elementos\n")
    print("-" * 60 + "\n")
    
    # Executa versoes
    t_numpy = numpy_version()
    t_aureum = aureum_version()
    t_hybrid = hybrid_version()
    
    # Comparacao
    print("=" * 60)
    print("RESULTADOS:")
    print(f"  NumPy:   {t_numpy:.3f}s (baseline)")
    print(f"  Aureum:  {t_aureum:.3f}s ({t_numpy/t_aureum:.1f}x mais rapido)")
    print(f"  Hibrido: {t_hybrid:.3f}s ({t_numpy/t_hybrid:.1f}x mais rapido)")
    print("\nCONCLUSAO:")
    print("  - Nao precisa reescrever tudo")
    print("  - Substitua apenas os gargalos")
    print("  - Ganho imediato de performance")
    print("  - Migracao gradual e segura")
