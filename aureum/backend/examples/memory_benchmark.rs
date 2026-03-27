/// Real Memory Savings Demonstration - BitNet b1.58
/// 
/// This program proves that bit1.58 uses 4x less memory than int8
/// and 16x less memory than float32.
/// 
/// Author: Luiz Antônio De Lima Mendonça

use aureum_kernel::pack_ternary;
use std::mem::size_of;

fn main() {
    println!("\n╔══════════════════════════════════════════════════════════════╗");
    println!("║                                                              ║");
    println!("║     REAL MEMORY SAVINGS DEMONSTRATION - BitNet              ║");
    println!("║                                                              ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");

    // Real model sizes
    let sizes = vec![
        ("Small (1M parameters)", 1_000_000),
        ("Medium (10M parameters)", 10_000_000),
        ("Large (100M parameters)", 100_000_000),
        ("Very Large (1B parameters)", 1_000_000_000),
    ];

    for (name, num_params) in sizes {
        println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        println!("Modelo: {}", name);
        println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        
        // Calculate memory usage for each type
        let fp32_bytes = num_params * size_of::<f32>();
        let fp16_bytes = num_params * 2; // 2 bytes per weight
        let int8_bytes = num_params * size_of::<i8>();
        let bit158_bytes = (num_params + 3) / 4; // 2 bits = 0.25 bytes per weight
        
        println!("\n📊 Memory Usage by Type:");
        println!("  FP32 (float32):  {:>12} bytes = {:>8} MB = {:>6.2} GB", 
            fp32_bytes, fp32_bytes / 1_000_000, fp32_bytes as f64 / 1_000_000_000.0);
        println!("  FP16 (float16):  {:>12} bytes = {:>8} MB = {:>6.2} GB", 
            fp16_bytes, fp16_bytes / 1_000_000, fp16_bytes as f64 / 1_000_000_000.0);
        println!("  INT8:            {:>12} bytes = {:>8} MB = {:>6.2} GB", 
            int8_bytes, int8_bytes / 1_000_000, int8_bytes as f64 / 1_000_000_000.0);
        println!("  bit1.58 (Aureum): {:>12} bytes = {:>8} MB = {:>6.2} GB ⚡", 
            bit158_bytes, bit158_bytes / 1_000_000, bit158_bytes as f64 / 1_000_000_000.0);
        
        println!("\n💾 Memory Savings:");
        let saving_vs_fp32 = ((fp32_bytes - bit158_bytes) as f64 / fp32_bytes as f64) * 100.0;
        let saving_vs_int8 = ((int8_bytes - bit158_bytes) as f64 / int8_bytes as f64) * 100.0;
        
        println!("  vs FP32:  {:.1}% savings ({}x smaller)", saving_vs_fp32, fp32_bytes / bit158_bytes);
        println!("  vs INT8:  {:.1}% savings ({}x smaller)", saving_vs_int8, int8_bytes / bit158_bytes);
        
        println!();
    }

    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("PRACTICAL DEMONSTRATION: Real Memory Allocation");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    // Practical demonstration with real allocation
    let test_size = 10_000_000; // 10 million weights
    
    println!("Allocating {} weights in different formats...\n", test_size);

    // FP32
    println!("1️⃣  Allocating FP32 (float32)...");
    let fp32_weights: Vec<f32> = vec![0.5; test_size];
    let fp32_mem = fp32_weights.len() * size_of::<f32>();
    println!("   ✓ Allocated: {} MB", fp32_mem / 1_000_000);
    println!("   Address: {:p}", fp32_weights.as_ptr());
    drop(fp32_weights);

    // INT8
    println!("\n2️⃣  Allocating INT8...");
    let int8_weights: Vec<i8> = vec![1; test_size];
    let int8_mem = int8_weights.len() * size_of::<i8>();
    println!("   ✓ Allocated: {} MB", int8_mem / 1_000_000);
    println!("   Address: {:p}", int8_weights.as_ptr());
    
    // bit1.58 (packed)
    println!("\n3️⃣  Allocating bit1.58 (Aureum - PACKED)...");
    let bit158_weights = pack_ternary(&int8_weights);
    let bit158_mem = bit158_weights.len();
    println!("   ✓ Allocated: {} MB", bit158_mem / 1_000_000);
    println!("   Address: {:p}", bit158_weights.as_ptr());
    
    println!("\n📊 Real Comparison:");
    println!("   INT8:    {} MB", int8_mem / 1_000_000);
    println!("   bit1.58: {} MB ({}x smaller) ⚡", 
        bit158_mem / 1_000_000, 
        int8_mem / bit158_mem);
    
    println!("\n✅ REAL PROOF: bit1.58 uses {}x less memory than INT8!", 
        int8_mem / bit158_mem);

    // Packing demonstration
    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("DEMONSTRATION: How Packing Works");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    let example_weights = vec![1i8, -1, 0, 1, -1, 1, 0, -1];
    println!("Original weights (INT8): {:?}", example_weights);
    println!("Memory: {} bytes\n", example_weights.len());

    let packed = pack_ternary(&example_weights);
    println!("Packed weights (bit1.58): {:?}", packed);
    println!("Memory: {} bytes\n", packed.len());

    println!("Binary representation:");
    for (i, &byte) in packed.iter().enumerate() {
        println!("  Byte {}: {:08b} = [{:2}, {:2}, {:2}, {:2}]",
            i,
            byte,
            decode_weight(byte, 0),
            decode_weight(byte, 1),
            decode_weight(byte, 2),
            decode_weight(byte, 3),
        );
    }

    println!("\n✅ Packing: {} bytes → {} bytes ({}x smaller)",
        example_weights.len(),
        packed.len(),
        example_weights.len() / packed.len());

    println!("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("CONCLUSION");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

    println!("✅ BitNet b1.58 (Aureum) PROVABLY uses:");
    println!("   • 4x less memory than INT8");
    println!("   • 8x less memory than FP16");
    println!("   • 16x less memory than FP32");
    println!("\n✅ This is REAL, not just theoretical!");
    println!("✅ Measured with real memory allocations on the system.");
    println!("\n🎉 Aureum: Ultra-efficient AI inference!\n");

    println!("Created by: Luiz Antônio De Lima Mendonça");
    println!("Resende, RJ, Brazil | @luizinvict\n");
}

/// Helper to decode a weight from a packed byte
fn decode_weight(byte: u8, position: usize) -> i8 {
    let bits = (byte >> (position * 2)) & 0b11;
    match bits {
        0b00 => -1,
        0b01 => 0,
        0b10 => 1,
        _ => 0,
    }
}
