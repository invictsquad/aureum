/// BitNet b1.58 Memory Packing Demonstration
/// Proves that we store 4 ternary values in 1 byte (2 bits each)
///
/// Author: Luiz Antônio De Lima Mendonça
/// Location: Resende, RJ, Brazil
/// Instagram: @luizinvict
/// Date: 2026-03-25

use crate::{pack_ternary, bitnet_infer};
use std::mem::size_of;

/// Structure for memory usage comparison
pub struct MemoryComparison {
    pub num_weights: usize,
    pub python_fp32_bytes: usize,
    pub python_int8_bytes: usize,
    pub aureum_bit158_bytes: usize,
    pub reduction_vs_fp32: f64,
    pub reduction_vs_int8: f64,
}

impl MemoryComparison {
    /// Calculates memory usage for different representations
    pub fn new(num_weights: usize) -> Self {
        // Traditional Python/NumPy
        let python_fp32_bytes = num_weights * size_of::<f32>();  // 4 bytes per weight
        let python_int8_bytes = num_weights * size_of::<i8>();   // 1 byte per weight
        
        // Aureum BitNet b1.58: 2 bits per weight = 4 weights per byte
        let aureum_bit158_bytes = (num_weights + 3) / 4;  // Round up
        
        // Calculate reductions
        let reduction_vs_fp32 = python_fp32_bytes as f64 / aureum_bit158_bytes as f64;
        let reduction_vs_int8 = python_int8_bytes as f64 / aureum_bit158_bytes as f64;
        
        Self {
            num_weights,
            python_fp32_bytes,
            python_int8_bytes,
            aureum_bit158_bytes,
            reduction_vs_fp32,
            reduction_vs_int8,
        }
    }
    
    /// Prints comparison report
    pub fn print_report(&self) {
        println!("\n╔══════════════════════════════════════════════════════════════╗");
        println!("║  MEMORY USAGE COMPARISON - BitNet b1.58                     ║");
        println!("╚══════════════════════════════════════════════════════════════╝\n");
        
        println!("Number of weights: {}", self.num_weights);
        println!();
        
        println!("┌─────────────────────────┬──────────────┬──────────────┐");
        println!("│ Representation          │ Memory       │ Bytes/weight │");
        println!("├─────────────────────────┼──────────────┼──────────────┤");
        println!("│ Python FP32 (float32)   │ {:>10} B │ 4.00 bytes   │", 
                 self.python_fp32_bytes);
        println!("│ Python INT8 (int8)      │ {:>10} B │ 1.00 bytes   │", 
                 self.python_int8_bytes);
        println!("│ Aureum bit1.58          │ {:>10} B │ 0.25 bytes   │", 
                 self.aureum_bit158_bytes);
        println!("└─────────────────────────┴──────────────┴──────────────┘");
        println!();
        
        println!("┌─────────────────────────────────────────────────────────┐");
        println!("│ MEMORY REDUCTION                                        │");
        println!("├─────────────────────────────────────────────────────────┤");
        println!("│ vs FP32:  {:.1}x smaller  ({:.1}% savings)             │", 
                 self.reduction_vs_fp32, 
                 (1.0 - 1.0/self.reduction_vs_fp32) * 100.0);
        println!("│ vs INT8:  {:.1}x smaller  ({:.1}% savings)              │", 
                 self.reduction_vs_int8,
                 (1.0 - 1.0/self.reduction_vs_int8) * 100.0);
        println!("└─────────────────────────────────────────────────────────┘");
        println!();
    }
}

/// Demonstrates packing 4 values into 1 byte
pub fn demonstrate_bit_packing() {
    println!("\n╔══════════════════════════════════════════════════════════════╗");
    println!("║  DEMONSTRATION: 4 VALUES IN 1 BYTE                          ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");
    
    // 4 ternary values: {-1, 0, 1, -1}
    let weights = vec![1i8, -1, 0, 1];
    
    println!("Original values (4 weights):");
    println!("  [1, -1, 0, 1]");
    println!();
    
    // Pack into 1 byte
    let packed = pack_ternary(&weights);
    
    println!("After packing:");
    println!("  1 byte = 0b{:08b} = 0x{:02X}", packed[0], packed[0]);
    println!();
    
    println!("Byte structure (2 bits per value):");
    println!("  ┌──────┬──────┬──────┬──────┐");
    println!("  │ Bits │ 7-6  │ 5-4  │ 3-2  │ 1-0  │");
    println!("  ├──────┼──────┼──────┼──────┼──────┤");
    println!("  │ Value│ {:>4} │ {:>4} │ {:>4} │ {:>4} │", 
             weights[3], weights[2], weights[1], weights[0]);
    println!("  │ Bits │  {:02b}  │  {:02b}  │  {:02b}  │  {:02b}  │",
             (packed[0] >> 6) & 0b11,
             (packed[0] >> 4) & 0b11,
             (packed[0] >> 2) & 0b11,
             packed[0] & 0b11);
    println!("  └──────┴──────┴──────┴──────┴──────┘");
    println!();
    
    println!("Encoding:");
    println!("  -1 → 00 (bits)");
    println!("   0 → 01 (bits)");
    println!("   1 → 10 (bits)");
    println!();
    
    println!("Memory savings:");
    println!("  Without packing: 4 bytes (1 byte × 4 values)");
    println!("  With packing: 1 byte");
    println!("  Reduction: 4x smaller (75% savings)");
    println!();
}

/// Demonstrates memory usage in real-world models
pub fn demonstrate_real_world_models() {
    println!("\n╔══════════════════════════════════════════════════════════════╗");
    println!("║  REAL MODELS - MEMORY SAVINGS                               ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");
    
    let models = vec![
        ("Small Model", 1_000_000),           // 1M parameters
        ("Medium Model", 100_000_000),        // 100M parameters
        ("Large Model", 1_000_000_000),       // 1B parameters
        ("Giant Model", 10_000_000_000),      // 10B parameters
    ];
    
    for (name, params) in models {
        println!("─────────────────────────────────────────────────────────────");
        println!("{} ({} parameters)", name, format_number(params));
        println!("─────────────────────────────────────────────────────────────");
        
        let comp = MemoryComparison::new(params);
        
        println!("  Python FP32:    {}", format_bytes(comp.python_fp32_bytes));
        println!("  Python INT8:    {}", format_bytes(comp.python_int8_bytes));
        println!("  Aureum bit1.58: {}", format_bytes(comp.aureum_bit158_bytes));
        println!();
        println!("  Savings vs FP32: {:.1}x ({:.1}% smaller)", 
                 comp.reduction_vs_fp32,
                 (1.0 - 1.0/comp.reduction_vs_fp32) * 100.0);
        println!("  Savings vs INT8: {:.1}x ({:.1}% smaller)",
                 comp.reduction_vs_int8,
                 (1.0 - 1.0/comp.reduction_vs_int8) * 100.0);
        println!();
    }
}

/// Demonstrates cache impact
pub fn demonstrate_cache_impact() {
    println!("\n╔══════════════════════════════════════════════════════════════╗");
    println!("║  L1/L2/L3 CACHE IMPACT                                      ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");
    
    // Typical modern CPU cache
    let l1_cache = 32 * 1024;      // 32 KB
    let l2_cache = 256 * 1024;     // 256 KB
    let l3_cache = 8 * 1024 * 1024; // 8 MB
    
    println!("L1 Cache (32 KB):");
    println!("  FP32:     {:>10} weights", l1_cache / 4);
    println!("  INT8:     {:>10} weights", l1_cache);
    println!("  bit1.58:  {:>10} weights  (16x more!)", l1_cache * 4);
    println!();
    
    println!("L2 Cache (256 KB):");
    println!("  FP32:     {:>10} weights", l2_cache / 4);
    println!("  INT8:     {:>10} weights", l2_cache);
    println!("  bit1.58:  {:>10} weights  (16x more!)", l2_cache * 4);
    println!();
    
    println!("L3 Cache (8 MB):");
    println!("  FP32:     {:>10} weights", format_number(l3_cache / 4));
    println!("  INT8:     {:>10} weights", format_number(l3_cache));
    println!("  bit1.58:  {:>10} weights  (16x more!)", format_number(l3_cache * 4));
    println!();
    
    println!("Benefits:");
    println!("  ✓ 16x more weights fit in cache");
    println!("  ✓ Fewer cache misses");
    println!("  ✓ Better data locality");
    println!("  ✓ Higher throughput");
    println!();
}

/// Formats number with separators
fn format_number(n: usize) -> String {
    let s = n.to_string();
    let mut result = String::new();
    for (i, c) in s.chars().rev().enumerate() {
        if i > 0 && i % 3 == 0 {
            result.push(',');
        }
        result.push(c);
    }
    result.chars().rev().collect()
}

/// Formats bytes into human-readable units
fn format_bytes(bytes: usize) -> String {
    const KB: usize = 1024;
    const MB: usize = KB * 1024;
    const GB: usize = MB * 1024;
    
    if bytes >= GB {
        format!("{:.2} GB", bytes as f64 / GB as f64)
    } else if bytes >= MB {
        format!("{:.2} MB", bytes as f64 / MB as f64)
    } else if bytes >= KB {
        format!("{:.2} KB", bytes as f64 / KB as f64)
    } else {
        format!("{} B", bytes)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_memory_comparison() {
        let comp = MemoryComparison::new(1000);
        
        // FP32: 1000 * 4 = 4000 bytes
        assert_eq!(comp.python_fp32_bytes, 4000);
        
        // INT8: 1000 * 1 = 1000 bytes
        assert_eq!(comp.python_int8_bytes, 1000);
        
        // bit1.58: (1000 + 3) / 4 = 250 bytes
        assert_eq!(comp.aureum_bit158_bytes, 250);
        
        // Reduction vs FP32: 4000 / 250 = 16x
        assert_eq!(comp.reduction_vs_fp32, 16.0);
        
        // Reduction vs INT8: 1000 / 250 = 4x
        assert_eq!(comp.reduction_vs_int8, 4.0);
    }
    
    #[test]
    fn test_bit_packing_efficiency() {
        // Tests that we really store 4 values in 1 byte
        let weights = vec![1i8, -1, 0, 1];
        let packed = pack_ternary(&weights);
        
        assert_eq!(packed.len(), 1, "4 values must fit in 1 byte");
        assert_eq!(weights.len() * size_of::<i8>(), 4, "Without packing: 4 bytes");
        assert_eq!(packed.len(), 1, "With packing: 1 byte");
    }
    
    #[test]
    fn test_large_model_memory() {
        // Model with 1 billion parameters
        let comp = MemoryComparison::new(1_000_000_000);
        
        // FP32: ~4 GB
        assert_eq!(comp.python_fp32_bytes, 4_000_000_000);
        
        // bit1.58: ~250 MB
        assert_eq!(comp.aureum_bit158_bytes, 250_000_000);
        
        // 16x smaller
        assert_eq!(comp.reduction_vs_fp32, 16.0);
    }
}
