#!/bin/bash
# Aureum Everywhere - Build Script
# Compila o kernel Aureum para todas as plataformas suportadas
#
# Author: Luiz Antônio De Lima Mendonça
# Location: Resende, RJ, Brazil
# Instagram: @luizinvict
# Date: 2026-03-25

set -e

echo "========================================================================"
echo "  AUREUM EVERYWHERE - Cross-Platform Build"
echo "========================================================================"
echo ""
echo "Building Aureum BitNet b1.58 kernel for all supported platforms..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─── Desktop/Server Platforms ─────────────────────────────────────────────────

echo -e "${BLUE}[1/8]${NC} Building for Linux x86_64..."
cargo build --release --target x86_64-unknown-linux-gnu
echo -e "${GREEN}✓${NC} Linux x86_64 done"
echo ""

echo -e "${BLUE}[2/8]${NC} Building for Windows x86_64..."
cargo build --release --target x86_64-pc-windows-msvc
echo -e "${GREEN}✓${NC} Windows x86_64 done"
echo ""

echo -e "${BLUE}[3/8]${NC} Building for macOS Intel..."
cargo build --release --target x86_64-apple-darwin
echo -e "${GREEN}✓${NC} macOS Intel done"
echo ""

echo -e "${BLUE}[4/8]${NC} Building for macOS Apple Silicon..."
cargo build --release --target aarch64-apple-darwin
echo -e "${GREEN}✓${NC} macOS Apple Silicon done"
echo ""

# ─── ARM Platforms (Mobile/IoT) ───────────────────────────────────────────────

echo -e "${BLUE}[5/8]${NC} Building for ARM64 Linux (Raspberry Pi, servers)..."
cargo build --release --target aarch64-unknown-linux-gnu
echo -e "${GREEN}✓${NC} ARM64 Linux done"
echo ""

echo -e "${BLUE}[6/8]${NC} Building for ARM32 Linux (cheap phones, IoT)..."
cargo build --release --target armv7-unknown-linux-gnueabihf
echo -e "${GREEN}✓${NC} ARM32 Linux done"
echo ""

# ─── RISC-V (Future Open Hardware) ────────────────────────────────────────────

echo -e "${BLUE}[7/8]${NC} Building for RISC-V 64-bit..."
cargo build --release --target riscv64gc-unknown-linux-gnu
echo -e "${GREEN}✓${NC} RISC-V 64-bit done"
echo ""

# ─── WebAssembly (Browser) ────────────────────────────────────────────────────

echo -e "${BLUE}[8/8]${NC} Building for WebAssembly..."
cargo build --release --target wasm32-unknown-unknown --profile release-wasm
echo -e "${GREEN}✓${NC} WebAssembly done"
echo ""

# ─── Summary ──────────────────────────────────────────────────────────────────

echo "========================================================================"
echo "  BUILD COMPLETE"
echo "========================================================================"
echo ""
echo "Binaries available in target/<platform>/release/"
echo ""
echo "Platforms built:"
echo "  ✓ Linux x86_64              (desktop/server)"
echo "  ✓ Windows x86_64            (desktop)"
echo "  ✓ macOS Intel               (desktop)"
echo "  ✓ macOS Apple Silicon       (desktop)"
echo "  ✓ ARM64 Linux               (Raspberry Pi, servers)"
echo "  ✓ ARM32 Linux               (cheap phones, IoT)"
echo "  ✓ RISC-V 64-bit             (future open hardware)"
echo "  ✓ WebAssembly               (browser)"
echo ""
echo "Total platforms: 8"
echo ""
echo "Aureum now runs EVERYWHERE! 🌍"
echo "========================================================================"
