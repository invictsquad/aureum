#!/bin/bash
# Build Aureum for WebAssembly
# Generates .wasm + .js bindings for use in browsers
#
# Requirements:
#   - wasm-pack: cargo install wasm-pack
#   - OR: rustup target add wasm32-unknown-unknown
#
# Author: Luiz Antônio De Lima Mendonça
# Date: 2026-03-25

set -e

echo "========================================================================"
echo "  Building Aureum for WebAssembly"
echo "========================================================================"
echo ""

# Check if wasm-pack is available
if command -v wasm-pack &> /dev/null; then
    echo "Using wasm-pack (recommended)..."
    echo ""
    
    # Build with wasm-pack (generates JS bindings automatically)
    wasm-pack build --target web --release --out-dir ../wasm-dist
    
    echo ""
    echo "✓ WebAssembly build complete!"
    echo ""
    echo "Output: ../wasm-dist/"
    echo "  - aureum_kernel_bg.wasm  (binary)"
    echo "  - aureum_kernel.js       (JS bindings)"
    echo "  - aureum_kernel.d.ts     (TypeScript definitions)"
    echo ""
    echo "Usage in HTML:"
    echo "  <script type=\"module\">"
    echo "    import init, { wasm_classify } from './aureum_kernel.js';"
    echo "    await init();"
    echo "    const result = wasm_classify(input, weights, 3, 256);"
    echo "  </script>"
    
else
    echo "wasm-pack not found. Using cargo directly..."
    echo ""
    echo "Install wasm-pack for better experience:"
    echo "  cargo install wasm-pack"
    echo ""
    
    # Build with cargo (manual approach)
    cargo build --release --target wasm32-unknown-unknown
    
    echo ""
    echo "✓ WebAssembly build complete!"
    echo ""
    echo "Output: target/wasm32-unknown-unknown/release/aureum_kernel.wasm"
    echo ""
    echo "Note: You'll need to create JS bindings manually or use wasm-pack."
fi

echo ""
echo "========================================================================"
