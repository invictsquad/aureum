"""
Exemplo de Migracao Gradual: PyTorch -> Aureum
Demonstra como substituir inferencia PyTorch por Aureum

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import time
import random

# ANTES: Modelo PyTorch (pesado)
def pytorch_version():
    print("=== VERSAO PYTORCH (PESADA) ===\n")
    
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("PyTorch nao instalado. Pulando...\n")
        return 1.0
    
    # Modelo simples
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc = nn.Linear(512, 10)
        
        def forward(self, x):
            return self.fc(x)
    
    model = SimpleModel()
    model.eval()
    
    # Dados de teste
    input_data = torch.randn(1, 512)
    
    # Inferencia repetida
    start = time.time()
    with torch.no_grad():
        for _ in range(1000):
            output = model(input_data)
            pred = output.argmax(dim=1).item()
    elapsed = time.time() - start
    
    print(f"Tempo: {elapsed:.3f}s")
    print(f"Predicao: classe {pred}\n")
    return elapsed

# DEPOIS: Modelo Aureum (leve)
def aureum_version():
    print("=== VERSAO AUREUM (LEVE) ===\n")
    
    import aureum as au
    
    # Modelo equivalente (pesos ternarios)
    model = au.AureumModel(
        input_dim=512,
        num_classes=10,
        labels=[f"classe_{i}" for i in range(10)]
    ).random_weights(seed=42)
    
    # Dados de teste (mesma dimensao)
    input_data = [random.randint(-100, 100) for _ in range(512)]
    
    # Inferencia repetida
    start = time.time()
    for _ in range(1000):
        result = model.classify(input_data)
        pred = result.class_id
    elapsed = time.time() - start
    
    print(f"Tempo: {elapsed:.3f}s")
    print(f"Predicao: {result.label}\n")
    return elapsed

# HIBRIDO: Treinamento PyTorch, Inferencia Aureum
def hybrid_version():
    print("=== VERSAO HIBRIDA (MELHOR DOS DOIS MUNDOS) ===\n")
    print("Treina em PyTorch, infere em Aureum\n")
    
    import aureum as au
    
    # Simula pesos treinados em PyTorch
    # (na pratica, voce converteria os pesos reais)
    def convert_pytorch_to_ternary(pytorch_weights):
        """Converte pesos FP32 para ternarios {-1, 0, 1}"""
        ternary = []
        for w in pytorch_weights:
            if w > 0.3:
                ternary.append(1)
            elif w < -0.3:
                ternary.append(-1)
            else:
                ternary.append(0)
        return ternary
    
    # Simula pesos PyTorch
    pytorch_weights = [random.uniform(-1, 1) for _ in range(512 * 10)]
    
    # Converte para Aureum
    ternary_weights = convert_pytorch_to_ternary(pytorch_weights)
    
    # Modelo Aureum com pesos convertidos
    model = au.AureumModel(
        input_dim=512,
        num_classes=10,
        labels=[f"classe_{i}" for i in range(10)]
    )
    model.load_weights(classify_weights=ternary_weights)
    
    # Inferencia em producao (rapida)
    input_data = [random.randint(-100, 100) for _ in range(512)]
    
    start = time.time()
    for _ in range(1000):
        result = model.classify(input_data)
    elapsed = time.time() - start
    
    print(f"Tempo: {elapsed:.3f}s")
    print(f"Predicao: {result.label}\n")
    print("VANTAGENS:")
    print("  - Treina com toda a flexibilidade do PyTorch")
    print("  - Infere com a velocidade do Aureum")
    print("  - Modelo 16x menor (FP32 -> 2 bits)")
    print("  - Roda em dispositivos de baixo custo\n")
    return elapsed

if __name__ == "__main__":
    print("DEMONSTRACAO: Migracao Gradual PyTorch -> Aureum\n")
    print("Cenario: 1000 inferencias de modelo Linear(512, 10)\n")
    print("-" * 60 + "\n")
    
    # Executa versoes
    t_pytorch = pytorch_version()
    t_aureum = aureum_version()
    t_hybrid = hybrid_version()
    
    # Comparacao
    print("=" * 60)
    print("RESULTADOS:")
    print(f"  PyTorch: {t_pytorch:.3f}s (baseline)")
    print(f"  Aureum:  {t_aureum:.3f}s ({t_pytorch/t_aureum:.1f}x mais rapido)")
    print(f"  Hibrido: {t_hybrid:.3f}s ({t_pytorch/t_hybrid:.1f}x mais rapido)")
    print("\nCONCLUSAO:")
    print("  - Mantem pipeline de treinamento PyTorch")
    print("  - Acelera inferencia em producao")
    print("  - Reduz custos de infraestrutura")
    print("  - Democratiza acesso a IA")
