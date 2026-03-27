# 🚀 How to Run Aureum

**Complete guide to test all features**

---

## 📋 Prerequisites

### 1. Python 3.8+

```bash
python --version
```

### 2. Rust 1.70+

```bash
rustc --version
cargo --version
```

### 3. Python Dependencies

```bash
pip install lark numpy
```

---

## ✅ Quick Tests (Recommended)

### 1. Complete Transpiler Test

```bash
cd aureum
python test_compiler.py
```

**Expected output:**
```
[SUCCESS] All tests passed!

Checks:
  [OK] Aureum syntax parsing
  [OK] bit1.58 tensor detection
  [OK] Matryoshka operator [::512]
  [OK] Optimized Rust code generation
  [OK] BitNet kernel call
```

### 2. Complete Rust Kernel Test

```bash
cd aureum/backend
cargo test --release
```

**Expected output:**
```
running 6 tests
test tests::test_decode_ternary_values ... ok
test tests::test_matryoshka_scale ... ok
test tests::test_pack_and_infer_full_scale ... ok
test tests::test_zero_weights_no_accumulation ... ok
test tests::test_simd_large_dataset ... ok
test tests::test_simd_consistency ... ok

test result: ok. 6 passed; 0 failed
```

---

## 🎯 Main Demonstrations

### 1. Memory Benchmark (REAL)

**Demonstrates 4x savings vs INT8, 16x vs FP32**

```bash
cd aureum/backend
cargo run --release --example memory_benchmark
```

**What you'll see:**
- Memory usage for models from 1M to 1B parameters
- REAL allocations with memory addresses
- Bit-level compaction demonstration
- Direct comparison INT8 vs bit1.58

**Execution time:** ~2 seconds

### 2. Comparison with Python/NumPy

**Demonstrates Aureum advantages over NumPy**

```bash
cd aureum
python demo.py
```

**What you'll see:**
- NumPy memory usage (FP32, FP16, INT8)
- Aureum memory usage (bit1.58)
- Real NumPy allocations
- Compaction demonstration
- Calculated savings

**Execution time:** ~3 seconds

### 3. Example Compilation

**Demonstrates complete flow .aur → .rs**

```bash
cd aureum
python frontend/aureum_compiler.py examples/inferencia.aur
```

**What you'll see:**
- Original Aureum code
- Generated Rust code
- Detected optimizations
- Created .rs file

**Generated file:** `examples/inferencia.rs`

---

## 🔬 Advanced Benchmarks

### 1. SIMD Benchmark

**Measures SIMD vs Scalar performance**

```bash
cd aureum/backend
cargo bench
```

**What you'll see:**
- Execution time for different sizes
- SIMD vs Scalar comparison
- Calculated speedup
- Throughput in elements/second

**Execution time:** ~30 seconds

**Note:** Requires `cargo-criterion` installed:
```bash
cargo install cargo-criterion
```

### 2. Test All Examples

**Compiles all .aur files**

```bash
cd aureum

# Basic example
python frontend/aureum_compiler.py examples/inferencia.aur

# Benchmark with multiple scales
python frontend/aureum_compiler.py examples/benchmark.aur

# Validation test
python frontend/aureum_compiler.py examples/teste.aur

# Complete model
python frontend/aureum_compiler.py examples/modelo_completo.aur
```

**Generated files:** `examples/*.rs`

---

## 📊 Performance Verification

### 1. Verify SIMD Optimizations

```bash
cd aureum/backend
cargo test --release test_simd_consistency -- --nocapture
```

**What you'll see:**
- SIMD vs Scalar comparison
- Consistency verification
- Execution times

### 2. Verify Memory Savings

```bash
cd aureum/backend
cargo run --release --example memory_benchmark | grep "REAL PROOF"
```

**Expected output:**
```
✅ REAL PROOF: bit1.58 uses 4x less memory than INT8!
```

---

## 🐛 Troubleshooting

### Error: "lark not found"

```bash
pip install lark
```

### Error: "cargo not found"

Install Rust:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Error: "numpy not found"

```bash
pip install numpy
```

### Error: Rust compilation fails

Update Rust:
```bash
rustup update
```

### Rust Warnings

Warnings about unused variables are normal and don't affect functionality.

---

## 📚 Additional Documentation

### Recommended Reading

1. **QUICKSTART.md** - Start here (5 minutes)
2. **RELATORIO_FINAL.md** - Complete project overview
3. **MEMORY_BENCHMARK.md** - Benchmark details
4. **SIMD_OPTIMIZATION.md** - Optimization details
5. **ARCHITECTURE.md** - Technical architecture

### Code Examples

See the `examples/` folder for:
- `inferencia.aur` - Basic example
- `benchmark.aur` - Multiple scales
- `teste.aur` - Validation
- `modelo_completo.aur` - Complete example

---

## 🎯 Validation Checklist

Run these commands to validate everything:

```bash
# 1. Python Tests
cd aureum
python test_compiler.py
# ✅ Expected: [SUCCESS] All tests passed!

# 2. Rust Tests
cd backend
cargo test --release
# ✅ Expected: ok. 6 passed; 0 failed

# 3. Memory Benchmark
cargo run --release --example memory_benchmark
# ✅ Expected: REAL PROOF: bit1.58 uses 4x less memory

# 4. Python/NumPy Demo
cd ..
python demo.py
# ✅ Expected: Complete comparison with calculated savings

# 5. Example Compilation
python frontend/aureum_compiler.py examples/inferencia.aur
# ✅ Expected: inferencia.rs file generated
```

**If all 5 commands execute successfully, Aureum is 100% functional!** ✅

---

## 🚀 Next Steps

After validating everything:

1. **Explore examples** in `examples/`
2. **Read documentation** in `*.md`
3. **Create your own files** `.aur`
4. **Contribute** improvements (see `CONTRIBUTING.md`)
5. **Share** the project!

---

## 💡 Tips

### Maximum Performance

Always use `--release` for benchmarks:
```bash
cargo test --release
cargo run --release
cargo bench
```

### Detailed Debug

To see more information:
```bash
cargo test -- --nocapture
cargo run -- --verbose
```

### Cleanup

To clean compiled files:
```bash
cd backend
cargo clean
```

---

## 📞 Support

### Problems?

1. Check prerequisites
2. Read troubleshooting above
3. Consult documentation
4. Open an issue on GitHub

### Questions?

- Read `QUICKSTART.md` for quick start
- Read `ARCHITECTURE.md` for technical details
- Read `RELATORIO_FINAL.md` for complete overview

---

## 🎉 Conclusion

With these commands, you can:
- ✅ Validate entire implementation
- ✅ See optimizations in action
- ✅ Measure memory savings
- ✅ Compare with NumPy
- ✅ Compile your own examples

**Have fun exploring Aureum!** 🚀

---

**Created by:** Luiz Antônio De Lima Mendonça  
**Location:** Resende, RJ, Brazil  
**Instagram:** [@luizinvict](https://www.instagram.com/luizinvict/)

*Aureum: Ultra-efficient AI inference* ⚡
