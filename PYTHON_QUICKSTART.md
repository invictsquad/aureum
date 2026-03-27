# Aureum Python - Quick Start Guide

**Get started with Aureum as a Python library in 5 minutes!**

## Installation

```bash
cd aureum
pip install -r requirements.txt
cd backend && cargo build --release
```

## Your First Aureum Program

### Example 1: Fast Compute

```python
# test_aureum.py
import sys
sys.path.insert(0, '.')  # If not installed via pip

from frontend.aureum_ffi import get_kernel

# Prepare data
input_data = [10, 20, 30, 40]
weights = [1, -1, 0, 1]  # Ternary weights {-1, 0, 1}

# Use Aureum kernel
kernel = get_kernel()
packed = kernel.pack_ternary(weights)
result = kernel.bitnet_infer(input_data, packed, len(input_data))

print(f"Result: {result}")  # Output: 30
# Calculation: 10*1 + 20*(-1) + 30*0 + 40*1 = 30
```

### Example 2: Classification

```python
from frontend.aureum_stdlib import AureumModel

# Create model
model = AureumModel(
    input_dim=100,
    num_classes=3,
    labels=["cat", "dog", "bird"]
)

# Initialize random weights (for demo)
model.random_weights(seed=42)

# Classify
import random
input_data = [random.randint(-50, 50) for _ in range(100)]
result = model.classify(input_data)

print(f"Predicted: {result.label}")
print(f"Class ID: {result.class_id}")
print(f"Score: {result.score}")
```

### Example 3: Embeddings

```python
from frontend.aureum_stdlib import AureumModel

# Create model with embeddings
model = AureumModel(
    input_dim=256,
    embed_dim=64
).random_weights(seed=42)

# Generate embeddings
text_a = [random.randint(-50, 50) for _ in range(256)]
text_b = [random.randint(-50, 50) for _ in range(256)]

emb_a = model.embed(text_a)
emb_b = model.embed(text_b)

print(f"Embedding dimension: {len(emb_a)}")

# Calculate similarity
sim = model.similarity(text_a, text_b)
print(f"Similarity score: {sim.score}")
print(f"Normalized: {sim.normalized:.3f}")
```

## Run Examples

### Migration Examples

```bash
# NumPy migration
python examples/migration_numpy.py

# PyTorch migration
python examples/migration_pytorch.py
```

### Benchmarks

```bash
# Compare Aureum vs NumPy
python examples/benchmark_comparison.py
```

### Tests

```bash
# Run integration tests
python test_python_integration.py
```

## Common Patterns

### Pattern 1: Replace NumPy Dot Product

```python
# Before (NumPy)
import numpy as np
result = np.dot(input_data, weights)

# After (Aureum) - 100x faster for ternary weights
from frontend.aureum_ffi import get_kernel
kernel = get_kernel()
packed = kernel.pack_ternary(weights)
result = kernel.bitnet_infer(input_data, packed, len(input_data))
```

### Pattern 2: Production Inference

```python
from frontend.aureum_stdlib import AureumModel

# Load model once (at startup)
model = AureumModel(input_dim=512, num_classes=10)
model.load_weights(classify_weights=pretrained_weights)

# Fast inference (in request handler)
def predict(input_data):
    result = model.classify(input_data)
    return result.label
```

### Pattern 3: Semantic Search

```python
from frontend.aureum_stdlib import AureumModel

# Create embedding model
model = AureumModel(input_dim=512, embed_dim=128)
model.load_weights(embed_weights=pretrained_weights)

# Index documents (offline)
doc_embeddings = [model.embed(doc) for doc in documents]

# Search (online)
query_embedding = model.embed(query)
similarities = [
    model._stdlib.similarity(query_embedding, doc_emb)
    for doc_emb in doc_embeddings
]
best_match = documents[max(range(len(similarities)), 
                          key=lambda i: similarities[i].score)]
```

## Performance Tips

1. **Pack weights once**: Call `pack_ternary()` once and reuse the packed buffer
2. **Use Matryoshka**: Set `scale` parameter to process fewer elements
3. **Batch operations**: Process multiple inputs in a loop (kernel is very fast)
4. **Profile first**: Use Python profiler to find bottlenecks before optimizing

## Troubleshooting

### Error: "Library not found"

```bash
# Compile the Rust kernel
cd backend
cargo build --release
```

### Error: "No module named 'lark'"

```bash
pip install lark psutil numpy
```

### Error: "Cargo not found"

Install Rust:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Next Steps

1. Read `MIGRATION_GUIDE.md` for complete migration strategies
2. Read `PYTHON_INTEGRATION.md` for technical details
3. Try the REPL: `python main.py --shell`
4. Explore examples in `examples/` directory
5. Check `CONTRIBUTING.md` to contribute

## Support

- GitHub Issues: Report bugs and request features
- Documentation: See `README.md` and other `.md` files
- Examples: Check `examples/` directory

---

**Author**: Luiz Antônio De Lima Mendonça  
**Location**: Resende, RJ, Brazil  
**Instagram**: @luizinvict

**Happy coding with Aureum! 🚀**
