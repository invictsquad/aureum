# Aureum Deployment Guide

Quick guide to deploy Aureum on different platforms.

---

## 🖥️ Desktop/Server (Linux, Windows, macOS)

### Requirements
- Rust 1.70+
- Python 3.8+ (for Python bindings)

### Build
```bash
cd aureum/backend
cargo build --release
```

### Use
```python
from aureum_stdlib import AureumModel

model = AureumModel(input_dim=512, num_classes=10)
model.random_weights()
result = model.classify(your_input)
```

---

## 📱 ARM Devices ($50 Phones, Raspberry Pi)

### Requirements
```bash
rustup target add aarch64-unknown-linux-gnu  # ARM64
rustup target add armv7-unknown-linux-gnueabihf  # ARM32
```

### Build
```bash
cd aureum/backend
./build_arm.sh
```

### Deploy to Device
```bash
# Copy library to device
scp target/aarch64-unknown-linux-gnu/release/libaureum_kernel.so user@device:~/

# Copy Python code
scp -r ../frontend/*.py user@device:~/aureum/

# On device: install Python deps
pip3 install lark psutil numpy
```

### Use on Device
```python
# Same Python API works everywhere!
from aureum_stdlib import AureumModel
model = AureumModel(input_dim=512, num_classes=10)
# ...
```

---

## 🌐 Browser (WebAssembly)

### Requirements
```bash
cargo install wasm-pack
```

### Build
```bash
cd aureum/backend
./build_wasm.sh
```

### Deploy
```html
<!-- Copy wasm-dist/ to your web server -->
<script type="module">
  import init, { wasm_classify } from './aureum_kernel.js';
  await init();
  
  // Use Aureum in browser!
  const result = wasm_classify(input, weights, 3, 256);
</script>
```

### Example
See `examples/browser_demo.html` for complete demo.

---

## 🚀 RISC-V (Future Hardware)

### Requirements
```bash
rustup target add riscv64gc-unknown-linux-gnu
```

### Build
```bash
cd aureum/backend
./build_riscv.sh
```

### Deploy
Same as ARM — copy `.so` file to device and use Python API.

---

## 📦 Distribution

### Python Package (PyPI)
```bash
# Build wheels for all platforms
python setup.py bdist_wheel

# Upload to PyPI
twine upload dist/*
```

### NPM Package (WebAssembly)
```bash
# Publish WASM to NPM
cd wasm-dist
npm publish
```

### Docker
```dockerfile
FROM rust:1.70 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/libaureum_kernel.so /usr/lib/
# ...
```

---

## 🔒 Security

### Recommendations
- Use release builds (optimized + stripped)
- Validate input sizes (prevent buffer overflows)
- Sandbox WASM (browser does this automatically)
- Keep dependencies updated

---

## ⚡ Performance Tips

### ARM Devices
- Use ARM64 when possible (2x faster than ARM32)
- Enable NEON (automatic in our builds)
- Use Matryoshka for adaptive performance

### WebAssembly
- Use streaming compilation (`WebAssembly.instantiateStreaming`)
- Cache compiled module (`IndexedDB`)
- Use Web Workers for background inference

### All Platforms
- Batch inputs when possible
- Use appropriate Matryoshka scale
- Profile with `cargo bench`

---

## 📊 Monitoring

### Memory Usage
```python
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Inference Speed
```python
import time
start = time.perf_counter()
result = model.classify(input)
elapsed = time.perf_counter() - start
print(f"Inference: {elapsed*1000:.1f} ms")
```

---

## 🐛 Troubleshooting

### "Library not found"
- Check `LD_LIBRARY_PATH` includes library directory
- On macOS: `DYLD_LIBRARY_PATH`
- On Windows: Copy DLL to same folder as Python script

### "SIMD not available"
- ARM: Ensure NEON is enabled (check `/proc/cpuinfo`)
- x86: Ensure AVX2 is available (`lscpu | grep avx2`)
- Fallback to scalar version works on all CPUs

### "Out of memory"
- Reduce model size
- Use smaller Matryoshka scale
- Close other applications

---

## 📞 Support

- GitHub Issues: Report bugs
- Discussions: Ask questions
- Email: [your-email]
- Instagram: @luizinvict

---

**Deploy Aureum Everywhere!** 🌍
