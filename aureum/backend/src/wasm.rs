/// Aureum WebAssembly Bindings
/// Allows running BitNet b1.58 models directly in the browser
/// Zero server needed — 100% local AI on client
///
/// Uso:
///   import init, { classify, detect, embed } from './aureum_kernel.js';
///   await init();
///   const result = classify(input, weights, numClasses, scale);
///
/// Author: Luiz Antônio De Lima Mendonça
/// Location: Resende, RJ, Brazil
/// Instagram: @luizinvict
/// Date: 2026-03-25

#[cfg(target_arch = "wasm32")]
use wasm_bindgen::prelude::*;

#[cfg(target_arch = "wasm32")]
use crate::{pack_ternary, bitnet_infer};

#[cfg(target_arch = "wasm32")]
use crate::stdlib::{classify, detect, embed, similarity, topk, ClassifyResult, DetectResult, SimilarityResult};

// ─── WASM Utilities ───────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

#[cfg(target_arch = "wasm32")]
macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}

// ─── Version and Info ─────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn aureum_version() -> String {
    "0.1.0".to_string()
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn aureum_info() -> String {
    format!(
        "Aureum BitNet b1.58 Kernel v{}\n\
         Platform: WebAssembly\n\
         Features: classify, detect, embed, similarity, topk\n\
         Memory: 2 bits per weight (16x smaller than FP32)\n\
         Speed: Zero FP multiplications",
        aureum_version()
    )
}

// ─── Core BitNet ──────────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_pack_ternary(weights: Vec<i8>) -> Vec<u8> {
    pack_ternary(&weights)
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_bitnet_infer(input: Vec<i32>, packed_weights: Vec<u8>, scale: usize) -> i64 {
    bitnet_infer(&input, &packed_weights, scale)
}

// ─── Stdlib: classify ─────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub struct WasmClassifyResult {
    pub class_id: i32,
    pub score: i64,
    pub num_classes: usize,
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_classify(
    input: Vec<i32>,
    weights: Vec<i8>,
    num_classes: usize,
    scale: usize,
) -> WasmClassifyResult {
    let result = classify(&input, &weights, num_classes, scale);
    WasmClassifyResult {
        class_id: result.class_id,
        score: result.score,
        num_classes: result.num_classes,
    }
}

// ─── Stdlib: detect ───────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub struct WasmDetectResult {
    pub position: i32,
    pub confidence: i64,
    pub detected: bool,
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_detect(
    sequence: Vec<i32>,
    pattern: Vec<i8>,
    threshold: i64,
    scale: usize,
) -> WasmDetectResult {
    let result = detect(&sequence, &pattern, threshold, scale);
    WasmDetectResult {
        position: result.position,
        confidence: result.confidence,
        detected: result.detected,
    }
}

// ─── Stdlib: embed ────────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_embed(
    input: Vec<i32>,
    projection: Vec<i8>,
    embed_dim: usize,
    scale: usize,
) -> Vec<i64> {
    embed(&input, &projection, embed_dim, scale)
}

// ─── Stdlib: similarity ───────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub struct WasmSimilarityResult {
    pub score: i64,
    pub magnitude_a: i64,
    pub magnitude_b: i64,
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_similarity(vec_a: Vec<i64>, vec_b: Vec<i64>) -> WasmSimilarityResult {
    let result = similarity(&vec_a, &vec_b);
    WasmSimilarityResult {
        score: result.score,
        magnitude_a: result.magnitude_a,
        magnitude_b: result.magnitude_b,
    }
}

// ─── Stdlib: topk ─────────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_topk(scores: Vec<i64>, k: usize) -> Vec<usize> {
    topk(&scores, k)
}

// ─── Memory Info ──────────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_memory_savings(num_weights: usize) -> String {
    let bit158_bytes = (num_weights + 3) / 4;
    let fp32_bytes = num_weights * 4;
    let savings_percent = (1.0 - bit158_bytes as f64 / fp32_bytes as f64) * 100.0;
    
    format!(
        "Weights: {}\n\
         BitNet b1.58: {} bytes\n\
         FP32: {} bytes\n\
         Savings: {:.1}% ({} bytes)",
        num_weights,
        bit158_bytes,
        fp32_bytes,
        savings_percent,
        fp32_bytes - bit158_bytes
    )
}

// ─── Demo/Test Functions ──────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_demo_classify() -> String {
    console_log!("Running Aureum classify demo...");
    
    let input = vec![10, 20, -5, 8];
    let weights = vec![
        1, 0, -1, 1,  // class 0
        0, 1,  1, 0,  // class 1
       -1, 1,  0, 1,  // class 2
    ];
    
    let result = classify(&input, &weights, 3, 4);
    
    format!(
        "Demo: classify()\n\
         Input: {:?}\n\
         Classes: 3\n\
         Result: class {} (score={})",
        input, result.class_id, result.score
    )
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen]
pub fn wasm_demo_detect() -> String {
    console_log!("Running Aureum detect demo...");
    
    let sequence = vec![2, 1, 3, 10, 50, 80, 60, 4, 2, 1, 5, 3];
    let pattern = vec![1, 1, 1];
    
    let result = detect(&sequence, &pattern, 100, 3);
    
    format!(
        "Demo: detect()\n\
         Sequence: {:?}\n\
         Pattern: {:?}\n\
         Detected: {} at position {} (confidence={})",
        sequence, pattern, result.detected, result.position, result.confidence
    )
}

// ─── Initialization ───────────────────────────────────────────────────────────

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen(start)]
pub fn wasm_init() {
    // Set panic hook for better error messages in browser console
    #[cfg(feature = "console_error_panic_hook")]
    console_error_panic_hook::set_once();
    
    console_log!("Aureum BitNet b1.58 Kernel initialized");
    console_log!("Version: {}", aureum_version());
    console_log!("Platform: WebAssembly");
    console_log!("Ready for AI inference in the browser!");
}
