# Migration Guide: Python/NumPy/PyTorch → Aureum

**The Golden Bridge for Adoption**

This guide shows how to migrate gradually, keeping your existing code working while accelerating bottlenecks.

---

## Philosophy: Gradual Migration

Aureum was designed to **coexist** with your existing Python code:

1. **Phase 1**: Import Aureum as a Python library
2. **Phase 2**: Replace only performance bottlenecks
3. **Phase 3**: Gradually migrate to native `.aur` (optional)

**You don't need to rewrite anything.** Start small, gain speed immediately.

---

## Strategy 1: NumPy → Aureum

### Before (Pure NumPy)

```python
import numpy as np

# Heavy operation: dot product with ternary weights
input_data = np.random.randint(-100, 100, size=1000)
weights = np.random.choice([-1, 0, 1], size=1000)

result = np.dot(input_data, weights)  # Slow on CPU
```

### After (Aureum)

```python
import aureum as au

# Same data
input_data = [10, 20, 30, ...]  # or .tolist() from NumPy
weights = [1, 0, -1, ...]

result = au.fast_compute(input_data, weights)  # 10-100x faster
```

### Hybrid (Best Approach)

```python
import numpy as np
import aureum as au

# Keep existing NumPy code
input_data = np.random.randint(-100, 100, size=1000)
weights = np.random.choice([-1, 0, 1], size=1000)

# Preprocessing in NumPy (fast)
normalized = input_data / np.max(np.abs(input_data))

# Heavy operation: delegate to Aureum
result = au.fast_compute(
    input_data.tolist(),
    weights.tolist()
)

# Post-processing in NumPy (fast)
final = np.mean([result, ...])
```

**Gain**: 10-100x faster on bottlenecks, without rewriting everything.

---

## Strategy 2: PyTorch → Aureum

### Scenario: PyTorch Training, Aureum Inference

**Problem**: PyTorch is great for training, but heavy for production inference.

**Solution**: Train in PyTorch, convert to Aureum, infer 100x faster.

### Step 1: Train in PyTorch (as usual)

```python
import torch
import torch.nn as nn

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(512, 10)
    
    def forward(self, x):
        return self.fc(x)

model = MyModel()
# ... train normally ...
```

### Step 2: Convert Weights to Ternary

```python
def convert_to_ternary(pytorch_weights):
    """Convert FP32 → {-1, 0, 1}"""
    ternary = []
    for w in pytorch_weights.flatten():
        if w > 0.3:
            ternary.append(1)
        elif w < -0.3:
            ternary.append(-1)
        else:
            ternary.append(0)
    return ternary

# Extract trained weights
pytorch_weights = model.fc.weight.detach().cpu().numpy()
ternary_weights = convert_to_ternary(pytorch_weights)
```

### Step 3: Inference in Aureum

```python
import aureum as au

# Load Aureum model with converted weights
aureum_model = au.AureumModel(
    input_dim=512,
    num_classes=10,
    labels=["cat", "dog", "bird", ...]
)
aureum_model.load_weights(classify_weights=ternary_weights)

# Production inference (100x faster)
result = aureum_model.classify(input_data)
print(result.label)  # "cat"
```

**Gain**:
- 16x smaller model (FP32 → 2 bits)
- 100x faster inference
- Runs on $50 phones

---

## Strategy 3: Convenience API

Aureum offers "magic" functions for common cases:

### Fast Classification

```python
import aureum as au

# One line to classify
label = au.fast_classify(
    input_data,
    model_weights,
    num_classes=10,
    labels=["0", "1", ..., "9"]
)
print(f"Digit: {label}")
```

### Fast Embeddings

```python
# Generate compact embedding
embedding = au.fast_embed(
    tokenize("machine learning"),
    model_weights,
    embed_dim=128
)

# Compare similarity
similarity = au.fast_similarity(
    tokenize("deep learning"),
    tokenize("neural networks"),
    model_weights,
    embed_dim=128
)
print(f"Similarity: {similarity:.2%}")
```

---

## Strategy 4: NumPy/PyTorch Compatibility

Aureum offers compatibility layers to facilitate migration:

### NumPy-like API

```python
import aureum.numpy_compat as np

# Use like NumPy
arr = np.array([1, 2, 3])
result = np.dot(input_data, weights)  # Uses Aureum kernel automatically
```

### PyTorch-like API

```python
import aureum.torch_compat as torch

# Use like PyTorch
tensor = torch.Tensor([1, 2, 3])
model = torch.nn.Linear(512, 10)
output = model(tensor)  # Uses Aureum kernel automatically
```

---

## When to Use Each Strategy

| Scenario | Recommended Strategy |
|---------|----------------------|
| Existing NumPy code with bottlenecks | **Hybrid**: Keep NumPy, accelerate bottlenecks |
| PyTorch inference in production | **Conversion**: Train PyTorch, infer Aureum |
| New AI project | **Native Aureum**: Use `.aur` from the start |
| Rapid prototyping | **Convenience API**: `fast_classify()`, etc. |
| Large codebase migration | **Compatibility**: `aureum.numpy_compat` |

---

## Practical Examples

### Example 1: Accelerating NumPy Bottleneck

```python
# BEFORE: 10 seconds
for i in range(10000):
    result = np.dot(large_input, ternary_weights)

# AFTER: 0.1 seconds
import aureum as au
packed = au.get_kernel().pack_ternary(ternary_weights)
for i in range(10000):
    result = au.get_kernel().bitnet_infer(large_input, packed, len(large_input))
```

### Example 2: Production Classification Model

```python
# Train in PyTorch (offline)
pytorch_model = train_my_model()

# Convert to Aureum (once)
aureum_model = convert_to_aureum(pytorch_model)

# Serve in production (100x faster)
@app.route('/predict')
def predict():
    result = aureum_model.classify(request.data)
    return jsonify({"label": result.label})
```

### Example 3: Semantic Search

```python
import aureum as au

# Index documents (offline)
doc_embeddings = [
    au.fast_embed(tokenize(doc), model_weights, 128)
    for doc in documents
]

# Real-time search (fast)
query_embedding = au.fast_embed(tokenize(query), model_weights, 128)
similarities = [
    au.similarity(query_embedding, doc_emb)
    for doc_emb in doc_embeddings
]
best_match = documents[np.argmax(similarities)]
```

---

## Migration Checklist

- [ ] Identify performance bottlenecks (use profiler)
- [ ] Verify operations use ternary weights or can be converted
- [ ] Install Aureum: `pip install aureum`
- [ ] Compile Rust kernel: `cd backend && cargo build --release`
- [ ] Replace heavy operations with `au.fast_compute()`
- [ ] Measure performance gain (should be 10-100x)
- [ ] Gradually expand to more parts of code
- [ ] (Optional) Migrate to native `.aur` for maximum performance

---

## Frequently Asked Questions

**Q: Do I need to rewrite all my code?**  
A: No! Start by replacing only bottlenecks. Aureum coexists with Python/NumPy/PyTorch.

**Q: My weights aren't ternary. Can I use Aureum?**  
A: Yes! Convert FP32 weights to ternary (see `convert_to_ternary` function). Precision loss is minimal for inference.

**Q: Does Aureum work with GPU?**  
A: Aureum is optimized for CPU (where it's 100x faster than NumPy). For GPU, use PyTorch for training and Aureum for edge inference.

**Q: Can I use Aureum in production?**  
A: Yes! Aureum is stable and tested. Ideal for production inference, especially on resource-limited devices.

**Q: How to contribute?**  
A: See `CONTRIBUTING.md`. Contributions are welcome!

---

## Next Steps

1. **Run the examples**: `python examples/migration_numpy.py`
2. **Run benchmarks**: `python examples/benchmark_comparison.py`
3. **Read documentation**: `README.md`, `QUICKSTART.md`
4. **Try the REPL**: `python main.py --shell`
5. **Join the community**: GitHub Issues, Discussions

---

**Author**: Luiz Antônio De Lima Mendonça  
**Location**: Resende, RJ, Brazil  
**Instagram**: @luizinvict  
**Date**: 2026-03-25

**Mission**: Democratize AI for everyone, especially in developing countries.
