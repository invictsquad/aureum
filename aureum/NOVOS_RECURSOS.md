# New Features - Aureum v1.1

## Author
Luiz Antônio De Lima Mendonça  
Location: Resende, RJ, Brazil  
Instagram: @luizinvict  
Date: 2026-03-25

---

## 🎯 Summary of Improvements

This update adds support for:
1. **New mathematical operators**: division (`/`), modulo (`%`), power (`**`)
2. **Multidimensional tensors**: explicit support for 2D, 3D and N-D in grammar
3. **Practical examples**: demonstrations of new features usage

---

## 📊 New Mathematical Operators

### Division (`/`)
```aureum
def division_example():
    values = tensor(shape=[100], type=int32)
    divisor = tensor(shape=[100], type=int32)
    result = values / divisor
```

**Transpilation to Rust:**
```rust
let result = (values / divisor);
```

### Modulo (`%`)
```aureum
def modulo_example():
    values = tensor(shape=[100], type=int32)
    divisor = tensor(shape=[100], type=int32)
    remainder = values % divisor
```

**Transpilation to Rust:**
```rust
let remainder = (values % divisor);
```

### Power (`**`)
```aureum
def power_example():
    base = tensor(shape=[100], type=int32)
    square = base ** 2
    cube = base ** 3
```

**Transpilation to Rust:**
```rust
let square = (base.pow(2));
let cube = (base.pow(3));
```

---

## 🔢 Multidimensional Tensors

Grammar now explicitly supports tensors with multiple dimensions:

### 1D Tensor (Vector)
```aureum
vector = tensor(shape=[1024], type=int16)
```
**Usage:** Embeddings, features, activations

### 2D Tensor (Matrix)
```aureum
matrix = tensor(shape=[32, 64], type=float32)
```
**Usage:** Dense layer weights, attention matrices

### 3D Tensor
```aureum
images = tensor(shape=[32, 224, 224], type=int16)
```
**Usage:** Image batch, convolutional features

### 4D Tensor
```aureum
batch_rgb = tensor(shape=[16, 3, 256, 256], type=int16)
```
**Usage:** RGB image batch, CNN features

---

## 💡 Practical Examples

### 1. Combined Operators
```aureum
def complex_calculation():
    input = tensor(shape=[1024], type=int32)
    weights = tensor(shape=[1024], type=bit1.58)
    
    # Operator combination
    result = (input + 10) * 2 / 3
    
    # BitNet inference with Matryoshka
    output = input * weights[::512]
```

### 2. Deep Neural Network
```aureum
def deep_network():
    # Layer 1
    input = tensor(shape=[1024], type=int16)
    weights1 = tensor(shape=[1024, 2048], type=bit1.58)
    
    # Layer 2
    weights2 = tensor(shape=[2048, 4096], type=bit1.58)
    
    # Layer 3
    weights3 = tensor(shape=[4096, 1000], type=bit1.58)
    
    # Adaptive inference with Matryoshka
    fast_output = input * weights1[::512]      # Low latency
    balanced_output = input * weights1[::1024] # Balanced
    precise_output = input * weights1[::2048]  # Maximum precision
```

### 3. Transformer with BitNet
```aureum
def transformer():
    vocab_size = 50000
    hidden_dim = 4096
    num_layers = 32
    
    # Embeddings
    token_embeddings = tensor(shape=[vocab_size, hidden_dim], type=int16)
    
    # Attention (Q, K, V)
    attention_q = tensor(shape=[num_layers, hidden_dim, hidden_dim], type=bit1.58)
    attention_k = tensor(shape=[num_layers, hidden_dim, hidden_dim], type=bit1.58)
    attention_v = tensor(shape=[num_layers, hidden_dim, hidden_dim], type=bit1.58)
    
    # Feed-forward
    ff_w1 = tensor(shape=[num_layers, hidden_dim, hidden_dim * 4], type=bit1.58)
    ff_w2 = tensor(shape=[num_layers, hidden_dim * 4, hidden_dim], type=bit1.58)
    
    # Total: ~1.5B parameters
    # BitNet memory: ~375 MB (vs ~6 GB in FP32) ⚡
```

### 4. CNN for Computer Vision
```aureum
def cnn_classification():
    # Input: batch of 32 images 224x224 RGB
    input_images = tensor(shape=[32, 3, 224, 224], type=int16)
    
    # Convolutional layers
    conv1 = tensor(shape=[64, 3, 7, 7], type=bit1.58)    # 64 filters 7x7
    conv2 = tensor(shape=[128, 64, 3, 3], type=bit1.58)  # 128 filters 3x3
    conv3 = tensor(shape=[256, 128, 3, 3], type=bit1.58) # 256 filters 3x3
    conv4 = tensor(shape=[512, 256, 3, 3], type=bit1.58) # 512 filters 3x3
    
    # Fully connected layer
    fc = tensor(shape=[512 * 7 * 7, 1000], type=bit1.58)
    
    # Memory savings vs FP32: ~75% ⚡
```

---

## 📈 Memory Savings

### Comparison: FP32 vs BitNet b1.58

| Model | Parameters | FP32 | BitNet b1.58 | Savings |
|--------|-----------|------|--------------|----------|
| Small | 100M | 400 MB | 25 MB | **93.75%** |
| Medium | 1B | 4 GB | 250 MB | **93.75%** |
| Large | 7B | 28 GB | 1.75 GB | **93.75%** |
| Very Large | 70B | 280 GB | 17.5 GB | **93.75%** |

**Formula:**
- FP32: `parameters × 4 bytes`
- BitNet b1.58: `parameters × 0.25 bytes` (2 bits per weight)

---

## 🔧 Modified Files

### 1. `frontend/grammar.lark`
- Added operators: `div`, `mod`, `pow`
- Updated comment to indicate N-D tensor support
- Maintained precedence rules

### 2. `frontend/aureum_compiler.py`
- Extended `_process_expr` method with:
  - `node.data == 'div'` → `({left} / {right})`
  - `node.data == 'mod'` → `({left} % {right})`
  - `node.data == 'pow'` → `({left}.pow({right}))`

### 3. New Examples
- `examples/operadores_avancados.aur` - Demonstrates new operators
- `examples/tensores_multidimensionais.aur` - 2D/3D/4D examples
- `examples/operadores_simples.aur` - Basic test example

---

## ✅ Implementation Status

| Feature | Grammar | Transpiler | Rust Kernel | Examples | Status |
|---------|-----------|--------------|-------------|----------|--------|
| Division (`/`) | ✅ | ✅ | ⚠️ Pending | ✅ | 75% |
| Modulo (`%`) | ✅ | ✅ | ⚠️ Pending | ✅ | 75% |
| Power (`**`) | ✅ | ✅ | ⚠️ Pending | ✅ | 75% |
| 2D Tensors | ✅ | ⚠️ Partial | ⚠️ Pending | ✅ | 50% |
| 3D Tensors | ✅ | ⚠️ Partial | ⚠️ Pending | ✅ | 50% |
| N-D Tensors | ✅ | ⚠️ Partial | ⚠️ Pending | ✅ | 50% |

**Legend:**
- ✅ Complete
- ⚠️ Partial/Pending
- ❌ Not started

---

## 🚀 Next Steps

### Short Term
1. Implement tensor operations in Rust kernel (`div`, `mod`, `pow`)
2. Add complete multidimensional tensor support in transpiler
3. Create unit tests for new operators
4. Update REPL to support new operators

### Medium Term
1. Implement matrix operations (matmul, transpose)
2. Add broadcasting for element-wise operations
3. Support advanced slicing (beyond Matryoshka)
4. Reshape and view operations

### Long Term
1. SIMD optimizations for tensor operations
2. GPU support via CUDA/ROCm
3. Autograd for training
4. Integration with frameworks (PyTorch, JAX)

---

## 📚 Related Documentation

- `QUICKSTART.md` - Quick start guide
- `examples/tutorial.aur` - Complete language tutorial
- `ARCHITECTURE.md` - System architecture
- `PERFORMANCE.md` - Benchmarks and optimizations
- `CERTIFICACAO_REPL.md` - REPL certification
- `TESTE_VERDADE_MATEMATICA.md` - BitNet mathematical validation

---

## 🎓 References

1. **BitNet b1.58**: [Original Paper](https://arxiv.org/abs/2402.17764)
2. **Matryoshka Representation Learning**: Adaptive scales
3. **Ternary Neural Networks**: Weights {-1, 0, 1}

---

## 📝 Release Notes

### v1.1 (2026-03-25)
- ✅ Added operators: `/`, `%`, `**`
- ✅ Explicit multidimensional tensor support in grammar
- ✅ Practical usage examples
- ✅ Complete documentation

### v1.0 (2026-03-25)
- ✅ Functional interactive REPL
- ✅ Rust kernel with BitNet b1.58
- ✅ Matryoshka operator
- ✅ Python ↔ Rust FFI
- ✅ SIMD optimizations (AVX2/NEON)

---

**End of document**
