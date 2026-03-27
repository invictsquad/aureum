# Aureum Everywhere — Cross-Platform AI

**Democratizing AI for Low-Cost Hardware**

Aureum runs on ANY platform: from $50 phones to browsers to RISC-V boards.  
BitNet b1.58 + Matryoshka makes AI accessible to everyone, everywhere.

---

## 🌍 Supported Platforms

### Desktop & Server
- ✅ **Linux x86_64** — Servers, workstations
- ✅ **Windows x86_64** — Desktop PCs
- ✅ **macOS Intel** — MacBook Pro/Air (Intel)
- ✅ **macOS Apple Silicon** — M1/M2/M3 Macs

### Mobile & IoT (ARM)
- ✅ **ARM64 Linux** — Raspberry Pi 3/4/5, modern Android phones
- ✅ **ARM32 Linux** — **$50 phones**, Raspberry Pi 2, IoT devices
- 🔥 **NEON SIMD** — Hardware acceleration on all ARM devices

### Future Open Hardware
- ✅ **RISC-V 64-bit** — Open ISA, royalty-free
- 🚀 Will power next-gen devices

### Browser (WebAssembly)
- ✅ **WASM** — Runs in ANY modern browser
- 🔒 **100% local** — No server, no internet needed
- 🔐 **Private** — Data never leaves device

---

## 🚀 Quick Start

### 1. Install Rust Targets

```bash
# ARM devices
rustup target add aarch64-unknown-linux-gnu
rustup target add armv7-unknown-linux-gnueabihf

# RISC-V
rustup target add riscv64gc-unknown-linux-gnu

# WebAssembly
rustup target add wasm32-unknown-unknown
cargo install wasm-pack
```

### 2. Build for Your Platform

```bash
cd aureum/backend

# Build for ARM64 (Raspberry Pi, modern phones)
./build_arm.sh

# Build for RISC-V
./build_riscv.sh

# Build for WebAssembly (browser)
./build_wasm.sh

# Build for ALL platforms
./build_all.sh
```

### 3. Use the Binary

**ARM64 Linux:**
```bash
# Copy to device
scp target/aarch64-unknown-linux-gnu/release/libaureum_kernel.so pi@raspberrypi:~/

# Use with Python
python3 your_ai_app.py
```

**WebAssembly:**
```html
<script type="module">
  import init, { wasm_classify } from './aureum_kernel.js';
  await init();
  
  const result = wasm_classify(input, weights, numClasses, scale);
  console.log('Predicted class:', result.class_id);
</script>
```

---

## 💡 Why Aureum Everywhere?

### Problem: AI is Expensive
- Traditional models need 4GB+ RAM
- Require powerful GPUs
- Can't run on cheap phones
- Need internet/servers

### Solution: Aureum BitNet b1.58
- **16x less memory** (2 bits per weight)
- **Zero FP multiplications** (only integer +/-)
- **Runs on $50 phones** (ARM32 with 512MB RAM)
- **Works offline** (100% local inference)

---

## 📊 Platform Comparison

| Platform | RAM Needed | Speed | Use Case |
|----------|-----------|-------|----------|
| **x86_64 Desktop** | 256MB | ⚡⚡⚡ | Development, servers |
| **ARM64 (Pi 4)** | 512MB | ⚡⚡ | Edge devices, prototyping |
| **ARM32 ($50 phone)** | 512MB | ⚡ | Democratization, IoT |
| **RISC-V** | 512MB | ⚡⚡ | Future open hardware |
| **WebAssembly** | 256MB | ⚡⚡ | Privacy, offline apps |

All platforms use the SAME code — compile once, run everywhere!

---

## 🎯 Real-World Impact

### Scenario 1: Student in India
- **Device:** $50 Android phone (ARM32, 1GB RAM)
- **Model:** 1B parameter BitNet (250MB)
- **Result:** Runs sentiment analysis locally, no internet needed
- **Impact:** Access to AI without expensive hardware

### Scenario 2: Offline Medical Diagnosis
- **Device:** Raspberry Pi 4 (ARM64, 2GB RAM)
- **Model:** Medical image classifier (500MB)
- **Result:** Works in remote clinics without internet
- **Impact:** Healthcare in underserved areas

### Scenario 3: Privacy-First Browser App
- **Device:** Any laptop/phone with browser
- **Model:** Text classifier (100MB WASM)
- **Result:** Processes sensitive data locally
- **Impact:** Zero data sent to servers, 100% private

---

## 🔧 Technical Details

### ARM Optimizations
- **NEON SIMD** — Processes 4 elements at once (ARM32) or 8 (ARM64)
- **Cache-friendly** — 2-bit weights fit in L1 cache
- **Low power** — Integer-only math saves battery

### RISC-V Optimizations
- **RVV (Vector Extension)** — When available, uses vector instructions
- **Scalar fallback** — Works on all RISC-V chips
- **Future-proof** — Ready for next-gen hardware

### WebAssembly Optimizations
- **Size-optimized** — Profile `release-wasm` with `opt-level="z"`
- **No threading** — Single-threaded for browser compatibility
- **Streaming** — Can load models progressively

---

## 📦 Binary Sizes

| Platform | Library Size | Notes |
|----------|-------------|-------|
| x86_64 | ~120 KB | With SIMD AVX2 |
| ARM64 | ~110 KB | With NEON |
| ARM32 | ~100 KB | With NEON |
| RISC-V | ~95 KB | Scalar only |
| WASM | ~80 KB | Size-optimized |

All sizes are for release builds with LTO and strip enabled.

---

## 🛠️ Build Scripts Reference

### `build_all.sh`
Builds for ALL 8 platforms:
- Linux x86_64
- Windows x86_64
- macOS Intel
- macOS Apple Silicon
- ARM64 Linux
- ARM32 Linux
- RISC-V 64-bit
- WebAssembly

**Usage:**
```bash
./build_all.sh
```

**Output:** `target/<platform>/release/`

### `build_arm.sh`
Builds for ARM devices (phones, Raspberry Pi, IoT):
- ARM64 (aarch64)
- ARM32 (armv7)

**Usage:**
```bash
./build_arm.sh
```

**Output:**
- `target/aarch64-unknown-linux-gnu/release/libaureum_kernel.so`
- `target/armv7-unknown-linux-gnueabihf/release/libaureum_kernel.so`

### `build_riscv.sh`
Builds for RISC-V (future open hardware):
- RISC-V 64-bit (RV64GC)

**Usage:**
```bash
./build_riscv.sh
```

**Output:** `target/riscv64gc-unknown-linux-gnu/release/libaureum_kernel.so`

### `build_wasm.sh`
Builds for WebAssembly (browser):
- Uses `wasm-pack` (recommended) or `cargo`
- Generates `.wasm` + `.js` bindings

**Usage:**
```bash
./build_wasm.sh
```

**Output:** `../wasm-dist/aureum_kernel.{wasm,js,d.ts}`

---

## 🌐 WebAssembly API

### Initialization
```javascript
import init from './aureum_kernel.js';
await init();
```

### Functions Available

#### `wasm_classify(input, weights, numClasses, scale)`
Classifies input into one of `numClasses` classes.

**Parameters:**
- `input: Int32Array` — Input vector
- `weights: Int8Array` — Ternary weights {-1, 0, 1}
- `numClasses: number` — Number of classes
- `scale: number` — Matryoshka scale

**Returns:** `{ class_id, score, num_classes }`

#### `wasm_detect(sequence, pattern, threshold, scale)`
Detects pattern in sequence.

**Returns:** `{ position, confidence, detected }`

#### `wasm_embed(input, projection, embedDim, scale)`
Generates embedding.

**Returns:** `Int64Array` — Embedding vector

#### `wasm_similarity(vecA, vecB)`
Calculates similarity between two embeddings.

**Returns:** `{ score, magnitude_a, magnitude_b }`

#### `wasm_topk(scores, k)`
Returns indices of top-K scores.

**Returns:** `Uint32Array` — Indices

#### `wasm_memory_savings(numWeights)`
Shows memory savings vs FP32.

**Returns:** `string` — Formatted savings info

---

## 📱 Example: $50 Phone App

```python
# app.py - Runs on ARM32 phone with 512MB RAM

from aureum_stdlib import AureumModel

# Model fits in 250MB (vs 4GB for FP32)
model = AureumModel(input_dim=512, num_classes=10)
model.load_weights("sentiment_model_bitnet.bin")

# Classify text (runs in <100ms)
text = "This product is amazing!"
tokens = tokenize(text)
result = model.classify(tokens)

print(f"Sentiment: {result.label}")
# Output: Sentiment: positive
```

**Requirements:**
- ARM32 phone with 512MB RAM
- Python 3.8+
- Aureum library (100KB)

**Performance:**
- Inference: <100ms
- Memory: 250MB
- Battery: Minimal (integer-only math)

---

## 🎓 Educational Impact

### Before Aureum
- AI education requires expensive hardware
- Students in developing countries excluded
- Cloud APIs cost money, need internet

### After Aureum
- ✅ Runs on ANY device (even $50 phones)
- ✅ Works offline (no internet needed)
- ✅ Free to use (open source)
- ✅ Democratizes AI education globally

**Target:** 1 billion students worldwide with access to AI

---

## 🚀 Future Roadmap

### Short Term (Q2 2026)
- [ ] Android APK with Aureum embedded
- [ ] iOS framework (Swift bindings)
- [ ] NPM package for Node.js
- [ ] PyPI package with pre-built binaries

### Medium Term (Q3-Q4 2026)
- [ ] GPU acceleration (CUDA, Metal, Vulkan)
- [ ] Quantization tools (FP32 → BitNet converter)
- [ ] Model zoo (pre-trained BitNet models)
- [ ] Cloud-free training (on-device learning)

### Long Term (2027+)
- [ ] Aureum OS (Linux distro for AI)
- [ ] Hardware accelerators (custom ASIC)
- [ ] Federated learning (privacy-preserving)
- [ ] Global AI network (peer-to-peer)

---

## 📚 Resources

### Documentation
- `README.md` — Project overview
- `QUICKSTART.md` — 5-minute tutorial
- `ARCHITECTURE.md` — Technical deep dive
- `PERFORMANCE.md` — Benchmarks

### Examples
- `examples/browser_demo.html` — WebAssembly demo
- `examples/stdlib_demo.py` — Python API demo
- `examples/stdlib_nativa.aur` — Native Aureum syntax

### Build Scripts
- `backend/build_all.sh` — Build for all platforms
- `backend/build_arm.sh` — Build for ARM
- `backend/build_riscv.sh` — Build for RISC-V
- `backend/build_wasm.sh` — Build for WebAssembly

---

## 🤝 Contributing

We welcome contributions for:
- New platform support (Android, iOS, etc.)
- Performance optimizations
- Documentation improvements
- Example applications

See `CONTRIBUTING.md` for guidelines.

---

## 📄 License

MIT License — Free for everyone, everywhere.

---

## 👤 Author

**Luiz Antônio De Lima Mendonça**  
Location: Resende, RJ, Brazil  
Instagram: @luizinvict  
Mission: Democratize AI for the world 🌍

---

**Aureum Everywhere: AI for Everyone, on Every Device** 🚀
