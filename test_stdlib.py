#!/usr/bin/env python3
"""
Teste simples da AI-Native Standard Library
Sem emojis, sem Unicode especial - 100% ASCII
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "frontend"))

from aureum_stdlib import AureumModel

def test_classify():
    """Teste de classificacao"""
    print("\n[TEST] Classificacao em 5 linhas")
    model = AureumModel(input_dim=64, num_classes=4,
                        labels=["spam", "noticia", "codigo", "poesia"])
    model.random_weights(seed=42)
    entrada = [i % 127 for i in range(64)]
    resultado = model.classify(entrada)
    print(f"  Resultado: '{resultado.label}' (score={resultado.score})")
    assert resultado.class_id >= 0
    assert resultado.class_id < 4
    print("  [OK] Passou")
    return True

def test_topk():
    """Teste de top-K"""
    print("\n[TEST] Top-K classes")
    model = AureumModel(input_dim=32, num_classes=5,
                        labels=["gato", "cachorro", "passaro", "peixe", "coelho"])
    model.random_weights(seed=7)
    entrada = [10, -5, 20, 0, 15, -8, 3, 12, -2, 7,
               18, -1, 5, 9, -3, 14, 6, -7, 11, 4,
               -9, 16, 2, -4, 13, 8, -6, 17, 1, -10,
               19, 0]
    top3 = model.topk_classes(entrada, k=3)
    print(f"  Top-3: {[r.label for r in top3]}")
    assert len(top3) == 3
    print("  [OK] Passou")
    return True

def test_detect():
    """Teste de deteccao"""
    print("\n[TEST] Deteccao de padrao")
    from aureum_stdlib import get_stdlib
    stdlib = get_stdlib()
    sequencia = [2, 1, 3, 10, 50, 80, 60, 4, 2, 1, 5, 3]
    padrao = [1, 1, 1]
    resultado = stdlib.detect(sequencia, padrao, threshold=100)
    print(f"  Detectado: {resultado.detected}, posicao: {resultado.position}")
    assert resultado.detected
    assert resultado.position == 4
    print("  [OK] Passou")
    return True

def test_similarity():
    """Similarity test"""
    print("\n[TEST] Semantic similarity")
    model = AureumModel(input_dim=32, embed_dim=16)
    model.random_weights(seed=99)
    
    texto_a = [10, 20, -5, 8, 15, -3, 7, 12, -1, 9,
               4, -8, 6, 11, -2, 14, 3, -6, 13, 5,
               -9, 16, 2, -4, 17, 1, -7, 18, 0, -10,
               19, -11]
    
    texto_b = [11, 19, -4, 9, 14, -2, 8, 11, 0, 10,
               5, -7, 7, 10, -1, 15, 4, -5, 12, 6,
               -8, 17, 3, -3, 16, 2, -6, 19, 1, -9,
               18, -10]
    
    texto_c = [-10, -20, 5, -8, -15, 3, -7, -12, 1, -9,
               -4, 8, -6, -11, 2, -14, -3, 6, -13, -5,
               9, -16, -2, 4, -17, -1, 7, -18, 0, 10,
               -19, 11]
    
    sim_ab = model.similarity(texto_a, texto_b)
    sim_ac = model.similarity(texto_a, texto_c)
    print(f"  A vs B: {sim_ab.score}, A vs C: {sim_ac.score}")
    assert sim_ab.score >= sim_ac.score
    print("  [OK] Passou")
    return True

def main():
    print("\n" + "="*70)
    print("  AUREUM AI-NATIVE STANDARD LIBRARY - TESTES")
    print("="*70)
    
    testes = [
        ("Classificacao", test_classify),
        ("Top-K", test_topk),
        ("Deteccao", test_detect),
        ("Similaridade", test_similarity),
    ]
    
    resultados = []
    for nome, fn in testes:
        try:
            ok = fn()
            resultados.append((nome, ok))
        except Exception as e:
            print(f"\n  [ERRO] {nome}: {e}")
            import traceback
            traceback.print_exc()
            resultados.append((nome, False))
    
    print("\n" + "="*70)
    print("  RESUMO")
    print("="*70)
    passou = sum(1 for _, ok in resultados if ok)
    for nome, ok in resultados:
        status = "[OK]" if ok else "[FALHOU]"
        print(f"  {status} {nome}")
    
    print(f"\n  {passou}/{len(resultados)} testes passaram")
    print("="*70 + "\n")
    
    return 0 if passou == len(resultados) else 1

if __name__ == "__main__":
    sys.exit(main())
