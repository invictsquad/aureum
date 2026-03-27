#!/bin/bash
# Build Aureum for RISC-V (Future of Open Hardware)
# RISC-V is royalty-free and will power next-gen devices
#
# Requirements:
#   rustup target add riscv64gc-unknown-linux-gnu
#
# Author: Luiz Antônio De Lima Mendonça
# Date: 2026-03-25

set -e

echo "========================================================================"
echo "  Building Aureum for RISC-V"
echo "========================================================================"
echo ""
echo "RISC-V: The future of open hardware"
echo "  - Royalty-free ISA"
echo "  - Growing ecosystem"
echo "  - Will power next-gen devices"
echo ""

echo "Building for RISC-V 64-bit (RV64GC)..."
echo ""

cargo build --release --target riscv64gc-unknown-linux-gnu

echo ""
echo "✓ RISC-V build complete!"
echo ""
echo "Output: target/riscv64gc-unknown-linux-gnu/release/libaureum_kernel.so"
echo ""
echo "This binary will run on:"
echo "  - RISC-V development boards"
echo "  - Future RISC-V phones/tablets"
echo "  - RISC-V servers"
echo "  - Open hardware projects"
echo ""
echo "Aureum is ready for the open hardware revolution! 🚀"
echo "========================================================================"
