/// Aureum Kernel - BitNet b1.58 inference engine
/// Ternary weights {-1, 0, 1} packed into 2 bits per element.
/// Uses only additions/subtractions — zero floating-point multiplications.
/// OPTIMIZED: SIMD (AVX2/NEON) for vectorized processing
///
/// Author: Luiz Antônio De Lima Mendonça
/// Location: Resende, RJ, Brazil
/// Instagram: @luizinvict
/// Date: 2026-03-25

// FFI module for Python bindings
pub mod ffi;

// AI-Native Standard Library
pub mod stdlib;

// FFI da stdlib
pub mod stdlib_ffi;

// WebAssembly bindings
#[cfg(target_arch = "wasm32")]
pub mod wasm;

// Elastic controller for native resilience
pub mod elastic;

// Conditional SIMD imports by architecture
#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

#[cfg(target_arch = "aarch64")]
use std::arch::aarch64::*;

/// Decodes 2 bits to ternary value: 00=-1, 01=0, 10=1
#[inline(always)]
fn decode_ternary(bits: u8) -> i32 {
    match bits & 0b11 {
        0b00 => -1,
        0b01 =>  0,
        0b10 =>  1,
        _    =>  0, // 0b11 reserved, treat as zero
    }
}

/// Extracts the ternary weight at index `i` from the packed buffer.
/// Each byte stores 4 weights (2 bits each).
#[inline(always)]
fn get_weight(packed: &[u8], i: usize) -> i32 {
    let byte_idx = i / 4;
    let bit_offset = (i % 4) * 2;
    let bits = (packed[byte_idx] >> bit_offset) as u8;
    decode_ternary(bits)
}

/// Packs a slice of ternary i8 values ({-1,0,1}) into 2-bit bytes.
/// Useful for preparing weights before inference.
pub fn pack_ternary(weights: &[i8]) -> Vec<u8> {
    let n_bytes = (weights.len() + 3) / 4;
    let mut packed = vec![0u8; n_bytes];
    for (i, &w) in weights.iter().enumerate() {
        let bits: u8 = match w {
            -1 => 0b00,
             0 => 0b01,
             1 => 0b10,
             _ => 0b01, // out-of-range values treated as zero
        };
        let byte_idx = i / 4;
        let bit_offset = (i % 4) * 2;
        packed[byte_idx] |= bits << bit_offset;
    }
    packed
}

/// BitNet b1.58 inference with Matryoshka operator support.
///
/// # Parameters
/// - `input`:  input vector (int16 as i32 to avoid overflow)
/// - `packed_weights`: bit1.58 packed weights (2 bits/element)
/// - `scale`:  Matryoshka limit — processes only the first `scale` elements.
///             Pass `input.len()` to use full scale.
///
/// # Returns
/// Accumulated sum (dot product) using only integer +/-.
pub fn bitnet_infer(input: &[i32], packed_weights: &[u8], scale: usize) -> i64 {
    // Matryoshka: limit to minimum of scale and actual input size
    let limit = scale.min(input.len());

    // Ensure the weights buffer has enough bytes for `limit` elements
    let required_bytes = (limit + 3) / 4;
    assert!(
        packed_weights.len() >= required_bytes,
        "Insufficient weights buffer: needs {} bytes for {} elements",
        required_bytes,
        limit
    );

    // Try SIMD version if available and advantageous
    #[cfg(target_arch = "x86_64")]
    {
        if is_x86_feature_detected!("avx2") && limit >= 32 {
            // SIMD available and dataset large enough
            return unsafe { bitnet_infer_avx2(input, packed_weights, limit) };
        }
    }

    #[cfg(target_arch = "aarch64")]
    {
        if std::arch::is_aarch64_feature_detected!("neon") && limit >= 16 {
            // NEON available and dataset large enough
            return unsafe { bitnet_infer_neon(input, packed_weights, limit) };
        }
    }

    // Fallback: optimized scalar version
    bitnet_infer_scalar(input, packed_weights, limit)
}

/// Scalar version (fallback) - optimized but without SIMD
#[inline]
fn bitnet_infer_scalar(input: &[i32], packed_weights: &[u8], limit: usize) -> i64 {
    let mut accumulator: i64 = 0;

    for i in 0..limit {
        let w = get_weight(packed_weights, i);
        // No multiplication: only add, subtract or ignore
        match w {
             1 => accumulator += input[i] as i64,
            -1 => accumulator -= input[i] as i64,
             _ => {} // weight 0: do nothing (cycle savings)
        }
    }

    accumulator
}

/// AVX2 SIMD version (x86_64) - processes 8 elements at a time
#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "avx2")]
unsafe fn bitnet_infer_avx2(input: &[i32], packed_weights: &[u8], limit: usize) -> i64 {
    // Process in blocks of 8 elements (256 bits / 32 bits per element)
    let simd_limit = (limit / 8) * 8;
    let mut i = 0;
    
    // Vector accumulator (4 x i64)
    let mut acc_vec = _mm256_setzero_si256();
    
    while i < simd_limit {
        // Load 8 input elements
        let input_vec = _mm256_loadu_si256(input.as_ptr().add(i) as *const __m256i);
        
        // Extract 8 weights (2 bytes = 8 weights of 2 bits each)
        let byte_idx = i / 4;
        let weights_byte1 = packed_weights[byte_idx] as i32;
        let weights_byte2 = packed_weights[byte_idx + 1] as i32;
        
        // Decode weights to vector
        let mut weights = [0i32; 8];
        for j in 0..4 {
            weights[j] = decode_ternary((weights_byte1 >> (j * 2)) as u8);
            weights[j + 4] = decode_ternary((weights_byte2 >> (j * 2)) as u8);
        }
        
        let weights_vec = _mm256_loadu_si256(weights.as_ptr() as *const __m256i);
        
        // Multiply (actually, conditional add/sub based on weight)
        // For weight = 1: add input
        // For weight = -1: subtract input
        // For weight = 0: skip
        
        // Create masks for each case
        let ones_vec = _mm256_set1_epi32(1);
        let neg_ones_vec = _mm256_set1_epi32(-1);
        
        let mask_pos = _mm256_cmpeq_epi32(weights_vec, ones_vec);
        let mask_neg = _mm256_cmpeq_epi32(weights_vec, neg_ones_vec);
        
        // Apply conditional operations
        let pos_contrib = _mm256_and_si256(mask_pos, input_vec);
        let neg_contrib = _mm256_and_si256(mask_neg, input_vec);
        
        // Accumulate (positives - negatives)
        let contrib = _mm256_sub_epi32(pos_contrib, neg_contrib);
        
        // Convert to i64 and accumulate
        let contrib_lo = _mm256_cvtepi32_epi64(_mm256_castsi256_si128(contrib));
        let contrib_hi = _mm256_cvtepi32_epi64(_mm256_extracti128_si256(contrib, 1));
        
        acc_vec = _mm256_add_epi64(acc_vec, contrib_lo);
        acc_vec = _mm256_add_epi64(acc_vec, contrib_hi);
        
        i += 8;
    }
    
    // Reduce vector accumulator to scalar
    let mut acc_array = [0i64; 4];
    _mm256_storeu_si256(acc_array.as_mut_ptr() as *mut __m256i, acc_vec);
    let mut accumulator: i64 = acc_array.iter().sum();
    
    // Process remaining elements (tail) in scalar mode
    while i < limit {
        let w = get_weight(packed_weights, i);
        match w {
             1 => accumulator += input[i] as i64,
            -1 => accumulator -= input[i] as i64,
             _ => {}
        }
        i += 1;
    }
    
    accumulator
}

/// NEON SIMD version (ARM/aarch64) - processes 4 elements at a time
#[cfg(target_arch = "aarch64")]
#[target_feature(enable = "neon")]
unsafe fn bitnet_infer_neon(input: &[i32], packed_weights: &[u8], limit: usize) -> i64 {
    let mut accumulator: i64 = 0;
    
    // Process in blocks of 4 elements (128 bits / 32 bits per element)
    let simd_limit = (limit / 4) * 4;
    let mut i = 0;
    
    // Vector accumulator (2 x i64)
    let mut acc_vec = vdupq_n_s64(0);
    
    while i < simd_limit {
        // Load 4 input elements
        let input_vec = vld1q_s32(input.as_ptr().add(i));
        
        // Extract 4 weights (1 byte = 4 weights of 2 bits each)
        let byte_idx = i / 4;
        let weights_byte = packed_weights[byte_idx] as i32;
        
        // Decode weights
        let mut weights = [0i32; 4];
        for j in 0..4 {
            weights[j] = decode_ternary((weights_byte >> (j * 2)) as u8);
        }
        
        let weights_vec = vld1q_s32(weights.as_ptr());
        
        // Create masks
        let ones_vec = vdupq_n_s32(1);
        let neg_ones_vec = vdupq_n_s32(-1);
        
        let mask_pos = vceqq_s32(weights_vec, ones_vec);
        let mask_neg = vceqq_s32(weights_vec, neg_ones_vec);
        
        // Apply conditional operations
        let pos_contrib = vandq_s32(mask_pos, input_vec);
        let neg_contrib = vandq_s32(mask_neg, input_vec);
        
        // Accumulate
        let contrib = vsubq_s32(pos_contrib, neg_contrib);
        
        // Convert to i64 and accumulate
        let contrib_lo = vmovl_s32(vget_low_s32(contrib));
        let contrib_hi = vmovl_s32(vget_high_s32(contrib));
        
        acc_vec = vaddq_s64(acc_vec, contrib_lo);
        acc_vec = vaddq_s64(acc_vec, contrib_hi);
        
        i += 4;
    }
    
    // Reduce vector accumulator
    accumulator = vgetq_lane_s64(acc_vec, 0) + vgetq_lane_s64(acc_vec, 1);
    
    // Process tail
    while i < limit {
        let w = get_weight(packed_weights, i);
        match w {
             1 => accumulator += input[i] as i64,
            -1 => accumulator -= input[i] as i64,
             _ => {}
        }
        i += 1;
    }
    
    accumulator
}

// ─── Tests ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pack_and_infer_full_scale() {
        // Weights: [1, -1, 0, 1]  → accumulator = 10 - 20 + 0 + 40 = 30
        let weights: Vec<i8> = vec![1, -1, 0, 1];
        let input:   Vec<i32> = vec![10, 20, 30, 40];
        let packed = pack_ternary(&weights);
        let result = bitnet_infer(&input, &packed, input.len());
        assert_eq!(result, 30);
    }

    #[test]
    fn test_matryoshka_scale() {
        // Same weights, but Matryoshka limits to 2 elements: 10 - 20 = -10
        let weights: Vec<i8> = vec![1, -1, 0, 1];
        let input:   Vec<i32> = vec![10, 20, 30, 40];
        let packed = pack_ternary(&weights);
        let result = bitnet_infer(&input, &packed, 2);
        assert_eq!(result, -10);
    }

    #[test]
    fn test_zero_weights_no_accumulation() {
        let weights: Vec<i8> = vec![0, 0, 0, 0];
        let input:   Vec<i32> = vec![100, 200, 300, 400];
        let packed = pack_ternary(&weights);
        let result = bitnet_infer(&input, &packed, input.len());
        assert_eq!(result, 0);
    }

    #[test]
    fn test_decode_ternary_values() {
        assert_eq!(decode_ternary(0b00), -1);
        assert_eq!(decode_ternary(0b01),  0);
        assert_eq!(decode_ternary(0b10),  1);
    }

    #[test]
    fn test_simd_large_dataset() {
        // Test with large dataset to activate SIMD
        let size = 1024;
        let weights: Vec<i8> = (0..size).map(|i| match i % 3 {
            0 => 1,
            1 => -1,
            _ => 0,
        }).collect();
        let input: Vec<i32> = (0..size).map(|i| i as i32).collect();
        
        let packed = pack_ternary(&weights);
        let result_simd = bitnet_infer(&input, &packed, size);
        let result_scalar = bitnet_infer_scalar(&input, &packed, size);
        
        // SIMD and scalar should give the same result
        assert_eq!(result_simd, result_scalar);
    }

    #[test]
    fn test_simd_consistency() {
        // Tests consistency between SIMD and scalar versions
        for size in [32, 64, 128, 256, 512, 1024] {
            let weights: Vec<i8> = (0..size).map(|i| ((i % 3) as i8) - 1).collect();
            let input: Vec<i32> = (1..=size).map(|i| i as i32).collect();
            
            let packed = pack_ternary(&weights);
            let result_auto = bitnet_infer(&input, &packed, size);
            let result_scalar = bitnet_infer_scalar(&input, &packed, size);
            
            assert_eq!(result_auto, result_scalar, 
                "Inconsistency for size={}: SIMD={}, Scalar={}", 
                size, result_auto, result_scalar);
        }
    }
}

// ─── Benchmarks ──────────────────────────────────────────────────────────────
// To run benchmarks, use: cargo bench (requires nightly)
// Or create a file in benches/ following Cargo structure
