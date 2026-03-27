/// FFI for AI-Native Standard Library
/// Exposes classify(), detect(), summarize(), embed(), similarity(), topk()
/// to Python via ctypes — zero external dependencies.
///
/// Author: Luiz Antônio De Lima Mendonça
/// Location: Resende, RJ, Brazil
/// Instagram: @luizinvict
/// Date: 2026-03-25

use std::slice;
use crate::stdlib::{
    classify, detect, embed, normalize, similarity, summarize, topk,
    ClassifyResult, DetectResult, SimilarityResult,
};

// ─── classify() FFI ──────────────────────────────────────────────────────────

/// FFI: Classifies input vector into one of num_classes classes.
///
/// # Safety
/// - `input_ptr`: pointer to i32 array with `input_len` elements
/// - `weights_ptr`: pointer to i8 array with `num_classes × input_len` elements
/// - `result_ptr`: pointer to ClassifyResult where result will be written
#[no_mangle]
pub extern "C" fn aureum_classify(
    input_ptr: *const i32,
    input_len: usize,
    weights_ptr: *const i8,
    num_classes: usize,
    scale: usize,
    result_ptr: *mut ClassifyResult,
) {
    if input_ptr.is_null() || weights_ptr.is_null() || result_ptr.is_null() {
        return;
    }

    unsafe {
        let input = slice::from_raw_parts(input_ptr, input_len);
        let weights = slice::from_raw_parts(weights_ptr, num_classes * input_len);
        let result = classify(input, weights, num_classes, scale);
        *result_ptr = result;
    }
}

// ─── detect() FFI ────────────────────────────────────────────────────────────

/// FFI: Detects pattern in sequence.
///
/// # Safety
/// - `sequence_ptr`: pointer to i32 array with `seq_len` elements
/// - `pattern_ptr`: pointer to i8 array with `pattern_len` elements
/// - `result_ptr`: pointer to DetectResult where result will be written
#[no_mangle]
pub extern "C" fn aureum_detect(
    sequence_ptr: *const i32,
    seq_len: usize,
    pattern_ptr: *const i8,
    pattern_len: usize,
    threshold: i64,
    scale: usize,
    result_ptr: *mut DetectResult,
) {
    if sequence_ptr.is_null() || pattern_ptr.is_null() || result_ptr.is_null() {
        return;
    }

    unsafe {
        let sequence = slice::from_raw_parts(sequence_ptr, seq_len);
        let pattern = slice::from_raw_parts(pattern_ptr, pattern_len);
        let result = detect(sequence, pattern, threshold, scale);
        *result_ptr = result;
    }
}

// ─── embed() FFI ─────────────────────────────────────────────────────────────

/// FFI: Generates embedding from input vector.
///
/// # Safety
/// - `input_ptr`: pointer to i32 array with `input_len` elements
/// - `weights_ptr`: pointer to i8 array with `embed_dim × input_len` elements
/// - `output_ptr`: pointer to i64 array with `embed_dim` elements (output)
#[no_mangle]
pub extern "C" fn aureum_embed(
    input_ptr: *const i32,
    input_len: usize,
    weights_ptr: *const i8,
    embed_dim: usize,
    scale: usize,
    output_ptr: *mut i64,
) {
    if input_ptr.is_null() || weights_ptr.is_null() || output_ptr.is_null() {
        return;
    }

    unsafe {
        let input = slice::from_raw_parts(input_ptr, input_len);
        let weights = slice::from_raw_parts(weights_ptr, embed_dim * input_len);
        let embedding = embed(input, weights, embed_dim, scale);

        let output = slice::from_raw_parts_mut(output_ptr, embed_dim);
        output.copy_from_slice(&embedding);
    }
}

// ─── summarize() FFI ─────────────────────────────────────────────────────────

/// FFI: Summarizes sequence of vectors.
///
/// # Safety
/// - `sequence_ptr`: pointer to i32 array with `num_tokens × dim` elements
/// - `attention_ptr`: pointer to i8 array with `num_tokens` elements
/// - `output_ptr`: pointer to i64 array with `dim` elements (output)
#[no_mangle]
pub extern "C" fn aureum_summarize(
    sequence_ptr: *const i32,
    num_tokens: usize,
    dim: usize,
    attention_ptr: *const i8,
    scale: usize,
    output_ptr: *mut i64,
) {
    if sequence_ptr.is_null() || attention_ptr.is_null() || output_ptr.is_null() {
        return;
    }

    unsafe {
        let sequence = slice::from_raw_parts(sequence_ptr, num_tokens * dim);
        let attention = slice::from_raw_parts(attention_ptr, num_tokens);
        let summary = summarize(sequence, num_tokens, dim, attention, scale);

        let output = slice::from_raw_parts_mut(output_ptr, dim);
        output.copy_from_slice(&summary);
    }
}

// ─── similarity() FFI ────────────────────────────────────────────────────────

/// FFI: Calculates similarity between two vectors.
///
/// # Safety
/// - `vec_a_ptr`, `vec_b_ptr`: pointers to i64 arrays with `len` elements
/// - `result_ptr`: pointer to SimilarityResult where result will be written
#[no_mangle]
pub extern "C" fn aureum_similarity(
    vec_a_ptr: *const i64,
    vec_b_ptr: *const i64,
    len: usize,
    result_ptr: *mut SimilarityResult,
) {
    if vec_a_ptr.is_null() || vec_b_ptr.is_null() || result_ptr.is_null() {
        return;
    }

    unsafe {
        let vec_a = slice::from_raw_parts(vec_a_ptr, len);
        let vec_b = slice::from_raw_parts(vec_b_ptr, len);
        let result = similarity(vec_a, vec_b);
        *result_ptr = result;
    }
}

// ─── normalize() FFI ─────────────────────────────────────────────────────────

/// FFI: Normalizes i64 vector to i8 in [-127, 127].
///
/// # Safety
/// - `input_ptr`: pointer to i64 array with `len` elements
/// - `output_ptr`: pointer to i8 array with `len` elements (output)
#[no_mangle]
pub extern "C" fn aureum_normalize(
    input_ptr: *const i64,
    len: usize,
    output_ptr: *mut i8,
) {
    if input_ptr.is_null() || output_ptr.is_null() {
        return;
    }

    unsafe {
        let input = slice::from_raw_parts(input_ptr, len);
        let normalized = normalize(input);

        let output = slice::from_raw_parts_mut(output_ptr, len);
        output.copy_from_slice(&normalized);
    }
}

// ─── topk() FFI ──────────────────────────────────────────────────────────────

/// FFI: Returns indices of K largest scores.
///
/// # Safety
/// - `scores_ptr`: pointer to i64 array with `scores_len` elements
/// - `output_ptr`: pointer to usize array with `k` elements (output)
/// - Returns actual number of elements written (min(k, scores_len))
#[no_mangle]
pub extern "C" fn aureum_topk(
    scores_ptr: *const i64,
    scores_len: usize,
    k: usize,
    output_ptr: *mut usize,
) -> usize {
    if scores_ptr.is_null() || output_ptr.is_null() {
        return 0;
    }

    unsafe {
        let scores = slice::from_raw_parts(scores_ptr, scores_len);
        let indices = topk(scores, k);
        let written = indices.len();

        let output = slice::from_raw_parts_mut(output_ptr, written);
        output.copy_from_slice(&indices);

        written
    }
}
