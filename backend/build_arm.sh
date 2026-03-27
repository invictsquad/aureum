#!/bin/bash
# Build Aureum for ARM devices (phones, Raspberry Pi, IoT)
# Optimized for low-cost hardware
#
# Requirements:
#   rustup target add aarch64-unknown-linux-gnu
#   rustup target add armv7-unknown-linux-gnueabihf
#
# Author: Luiz Antônio De Lima Mendonça
# Date: 2026-03-25

set -e

echo "========================================================================"
echo "  Building Aureum for ARM Devices"
echo "========================================================================"
echo ""

# ─── ARM64 (64-bit) ───────────────────────────────────────────────────────────

echo "[1/2] Building for ARM64 (aarch64)..."
echo "  Target devices: Raspberry Pi 3/4/5, modern Android phones, ARM servers"
echo ""

cargo build --release --target aarch64-unknown-linux-gnu

echo "✓ ARM64 build complete!"
echo "  Output: target/aarch64-unknown-linux-gnu/release/libaureum_kernel.so"
echo ""

# ─── ARM32 (32-bit) ───────────────────────────────────────────────────────────

echo "[2/2] Building for ARM32 (armv7)..."
echo "  Target devices: Cheap Android phones ($50), Raspberry Pi 2, IoT devices"
echo ""

cargo build --release --target armv7-unknown-linux-gnueabihf

echo "✓ ARM32 build complete!"
echo "  Output: target/armv7-unknown-linux-gnueabihf/release/libaureum_kernel.so"
echo ""

# ─── Summary ──────────────────────────────────────────────────────────────────

echo "========================================================================"
echo "  ARM BUILD COMPLETE"
echo "========================================================================"
echo ""
echo "Binaries ready for:"
echo "  ✓ ARM64 devices (Raspberry Pi, modern phones)"
echo "  ✓ ARM32 devices (cheap phones, IoT)"
echo ""
echo "Both use NEON SIMD for maximum performance!"
echo ""
echo "Democratizing AI for low-cost hardware 🌍"
echo "========================================================================"
