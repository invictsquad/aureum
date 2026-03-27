/// FFI (Foreign Function Interface) for Python
/// Exposes Aureum kernel functions to be called via ctypes/cffi
///
/// Author: Luiz Antônio De Lima Mendonça
/// Location: Resende, RJ, Brazil
/// Instagram: @luizinvict
/// Date: 2026-03-25

use std::slice;
use crate::{pack_ternary, bitnet_infer};

/// Structure for returning memory information
#[repr(C)]
pub struct MemoryInfo {
    pub original_bytes: usize,
    pub packed_bytes: usize,
    pub compression_ratio: f32,
}

/// FFI: Packs array of ternary weights
/// 
/// # Safety
/// - `weights_ptr` must point to a valid array of `len` elements
/// - `output_ptr` must have space for (len + 3) / 4 bytes
/// - Returns number of bytes written
#[no_mangle]
pub extern "C" fn aureum_pack_ternary(
    weights_ptr: *const i8,
    len: usize,
    output_ptr: *mut u8,
) -> usize {
    if weights_ptr.is_null() || output_ptr.is_null() {
        return 0;
    }
    
    unsafe {
        let weights = slice::from_raw_parts(weights_ptr, len);
        let packed = pack_ternary(weights);
        let packed_len = packed.len();
        
        let output = slice::from_raw_parts_mut(output_ptr, packed_len);
        output.copy_from_slice(&packed);
        
        packed_len
    }
}

/// FFI: BitNet b1.58 inference
/// 
/// # Safety
/// - `input_ptr` must point to a valid array of `input_len` elements
/// - `packed_weights_ptr` must have enough bytes for `scale` elements
#[no_mangle]
pub extern "C" fn aureum_bitnet_infer(
    input_ptr: *const i32,
    input_len: usize,
    packed_weights_ptr: *const u8,
    packed_len: usize,
    scale: usize,
) -> i64 {
    if input_ptr.is_null() || packed_weights_ptr.is_null() {
        return 0;
    }
    
    unsafe {
        let input = slice::from_raw_parts(input_ptr, input_len);
        let packed_weights = slice::from_raw_parts(packed_weights_ptr, packed_len);
        
        bitnet_infer(input, packed_weights, scale)
    }
}

/// FFI: Calculates memory information for a tensor
#[no_mangle]
pub extern "C" fn aureum_memory_info(num_weights: usize) -> MemoryInfo {
    let original_bytes = num_weights; // i8 = 1 byte each
    let packed_bytes = (num_weights + 3) / 4; // 2 bits = 0.25 bytes each
    let compression_ratio = original_bytes as f32 / packed_bytes as f32;
    
    MemoryInfo {
        original_bytes,
        packed_bytes,
        compression_ratio,
    }
}

/// FFI: Allocates buffer for packed weights
/// Returns pointer that must be freed with aureum_free_buffer
#[no_mangle]
pub extern "C" fn aureum_alloc_packed_buffer(num_weights: usize) -> *mut u8 {
    let size = (num_weights + 3) / 4;
    let mut buffer = vec![0u8; size];
    let ptr = buffer.as_mut_ptr();
    std::mem::forget(buffer); // Prevent automatic drop
    ptr
}

/// FFI: Frees buffer allocated by aureum_alloc_packed_buffer
#[no_mangle]
pub extern "C" fn aureum_free_buffer(ptr: *mut u8, len: usize) {
    if !ptr.is_null() {
        unsafe {
            let _ = Vec::from_raw_parts(ptr, len, len);
            // Vec will be dropped automatically here
        }
    }
}

/// FFI: Kernel version
#[no_mangle]
pub extern "C" fn aureum_version() -> *const u8 {
    b"0.1.0\0".as_ptr()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ffi_pack_and_infer() {
        let weights = vec![1i8, -1, 0, 1];
        let input = vec![10i32, 20, 30, 40];
        
        // Allocate output buffer
        let packed_len = (weights.len() + 3) / 4;
        let mut packed = vec![0u8; packed_len];
        
        // Pack
        let written = aureum_pack_ternary(
            weights.as_ptr(),
            weights.len(),
            packed.as_mut_ptr(),
        );
        
        assert_eq!(written, packed_len);
        
        // Inference
        let result = aureum_bitnet_infer(
            input.as_ptr(),
            input.len(),
            packed.as_ptr(),
            packed.len(),
            input.len(),
        );
        
        assert_eq!(result, 30); // 10 - 20 + 0 + 40 = 30
    }

    #[test]
    fn test_memory_info() {
        let info = aureum_memory_info(1024);
        assert_eq!(info.original_bytes, 1024);
        assert_eq!(info.packed_bytes, 256);
        assert_eq!(info.compression_ratio, 4.0);
    }
}
