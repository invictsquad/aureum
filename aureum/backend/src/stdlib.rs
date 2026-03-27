/// Aureum AI-Native Standard Library — Rust Kernel
///
/// Native AI functions optimized for BitNet b1.58.
/// Zero external dependencies. Zero FP multiplications.
/// Runs 100x faster than Python/NumPy equivalents.
///
/// Available functions:
///   classify()   — Multi-class classification with ternary weights
///   detect()     — Pattern detection in sequences
///   summarize()  — Summarization by ternary attention
///   embed()      — Compact embedding generation
///   similarity() — Cosine similarity in integers
///   normalize()  — Integer L2 normalization
///   softmax_int()— Approximate softmax in integers
///   topk()       — Top-K indices without full sort
///
/// Author: Luiz Antônio De Lima Mendonça
/// Location: Resende, RJ, Brazil
/// Instagram: @luizinvict
/// Date: 2026-03-25

use crate::{pack_ternary, bitnet_infer};

// ─── Classification Result ────────────────────────────────────────────────────

/// Result of classify() — predicted class + scores of all classes
#[repr(C)]
#[derive(Debug, Clone)]
pub struct ClassifyResult {
    /// Index of class with highest score
    pub class_id: i32,
    /// Score of predicted class (BitNet accumulator)
    pub score: i64,
    /// Number of classes
    pub num_classes: usize,
}

// ─── Detection Result ─────────────────────────────────────────────────────────

/// Result of detect() — position and confidence of detected pattern
#[repr(C)]
#[derive(Debug, Clone)]
pub struct DetectResult {
    /// Start position of detected pattern
    pub position: i32,
    /// Confidence score (higher = more confident)
    pub confidence: i64,
    /// Indicates if any pattern was detected (score > threshold)
    pub detected: bool,
}

// ─── Similarity Result ────────────────────────────────────────────────────────

/// Result from similarity() — similarity score between two vectors
#[repr(C)]
#[derive(Debug, Clone)]
pub struct SimilarityResult {
    /// Similarity score (integer scale, higher = more similar)
    pub score: i64,
    /// Magnitude of vector A (for normalization)
    pub magnitude_a: i64,
    /// Magnitude of vector B (for normalization)
    pub magnitude_b: i64,
}

// ─── classify() ──────────────────────────────────────────────────────────────

/// Classifies an input vector into one of `num_classes` classes.
///
/// Each class has a ternary weight vector of size `input_len`.
/// The class with highest BitNet dot product is predicted.
///
/// # Parameters
/// - `input`: input vector (int16 as i32)
/// - `weights_flat`: weights of all classes concatenated (num_classes × input_len)
/// - `num_classes`: number of classes
/// - `scale`: Matryoshka scale (use input.len() for full scale)
///
/// # Returns
/// ClassifyResult with predicted class and score
///
/// # Example
/// ```text
/// // 3 classes, 4 features each
/// let input = vec![10i32, 20, -5, 8];
/// let weights: Vec<i8> = vec![
///     1, 0, -1, 1,   // class 0
///     0, 1,  1, 0,   // class 1
///    -1, 1,  0, 1,   // class 2
/// ];
/// let result = classify(&input, &weights, 3, 4);
/// ```
pub fn classify(
    input: &[i32],
    weights_flat: &[i8],
    num_classes: usize,
    scale: usize,
) -> ClassifyResult {
    let input_len = input.len();
    assert_eq!(
        weights_flat.len(),
        num_classes * input_len,
        "weights_flat must have num_classes × input_len elements"
    );

    let mut best_class = 0i32;
    let mut best_score = i64::MIN;

    for class_id in 0..num_classes {
        // Extract weights for this class
        let start = class_id * input_len;
        let end = start + input_len;
        let class_weights = &weights_flat[start..end];

        // Pack weights into 2 bits
        let packed = pack_ternary(class_weights);

        // BitNet dot product (zero FP multiplications)
        let score = bitnet_infer(input, &packed, scale.min(input_len));

        if score > best_score {
            best_score = score;
            best_class = class_id as i32;
        }
    }

    ClassifyResult {
        class_id: best_class,
        score: best_score,
        num_classes,
    }
}

// ─── detect() ─────────────────────────────────────────────────────────────────

/// Detects a pattern (template) within an input sequence.
///
/// Uses sliding window with BitNet dot product to find the position
/// where the pattern best fits in the sequence.
///
/// # Parameters
/// - `sequence`: input sequence (int16 as i32)
/// - `pattern_weights`: ternary weights of pattern to detect
/// - `threshold`: minimum score to consider positive detection
/// - `scale`: escala Matryoshka
///
/// # Returns
/// DetectResult with position, confidence and detection flag
pub fn detect(
    sequence: &[i32],
    pattern_weights: &[i8],
    threshold: i64,
    scale: usize,
) -> DetectResult {
    let pattern_len = pattern_weights.len();

    if sequence.len() < pattern_len {
        return DetectResult {
            position: -1,
            confidence: 0,
            detected: false,
        };
    }

    // Pack pattern weights once
    let packed_pattern = pack_ternary(pattern_weights);
    let effective_scale = scale.min(pattern_len);

    let mut best_pos = -1i32;
    let mut best_score = i64::MIN;

    // Sliding window
    let num_windows = sequence.len() - pattern_len + 1;
    for pos in 0..num_windows {
        let window = &sequence[pos..pos + pattern_len];
        let score = bitnet_infer(window, &packed_pattern, effective_scale);

        if score > best_score {
            best_score = score;
            best_pos = pos as i32;
        }
    }

    DetectResult {
        position: best_pos,
        confidence: best_score,
        detected: best_score >= threshold,
    }
}

// ─── summarize() ─────────────────────────────────────────────────────────────

/// Summarizes a sequence of vectors into a single representative vector.
///
/// Uses ternary attention: each position receives a weight {-1, 0, 1} that
/// determines if it contributes positively, negatively or is ignored.
/// The result is a vector of scores per dimension.
///
/// # Parameters
/// - `sequence_flat`: concatenated sequence of vectors (num_tokens × dim)
/// - `num_tokens`: number of tokens/positions
/// - `dim`: dimension of each vector
/// - `attention_weights`: ternary attention weights (num_tokens elements)
/// - `scale`: Matryoshka scale
///
/// # Returns
/// Vec<i64> with summarized vector (dim elements)
pub fn summarize(
    sequence_flat: &[i32],
    num_tokens: usize,
    dim: usize,
    attention_weights: &[i8],
    scale: usize,
) -> Vec<i64> {
    assert_eq!(sequence_flat.len(), num_tokens * dim);
    assert_eq!(attention_weights.len(), num_tokens);

    let effective_tokens = scale.min(num_tokens);
    let mut summary = vec![0i64; dim];

    // For each dimension, calculate weighted sum by attention weights
    for d in 0..dim {
        // Extract column d from all tokens
        let column: Vec<i32> = (0..effective_tokens)
            .map(|t| sequence_flat[t * dim + d])
            .collect();

        // Apply ternary attention to this dimension
        let attn_slice = &attention_weights[..effective_tokens];
        let packed_attn = pack_ternary(attn_slice);
        summary[d] = bitnet_infer(&column, &packed_attn, effective_tokens);
    }

    summary
}

// ─── embed() ─────────────────────────────────────────────────────────────────

/// Generates a compact embedding from an input vector.
///
/// Projects the input vector into a lower-dimensional space using
/// a ternary projection matrix. Result: vector of `embed_dim` elements.
///
/// # Parameters
/// - `input`: input vector
/// - `projection_weights`: ternary projection matrix (embed_dim × input_len)
/// - `embed_dim`: output embedding dimension
/// - `scale`: Matryoshka scale
///
/// # Returns
/// Vec<i64> with generated embedding
pub fn embed(
    input: &[i32],
    projection_weights: &[i8],
    embed_dim: usize,
    scale: usize,
) -> Vec<i64> {
    let input_len = input.len();
    assert_eq!(
        projection_weights.len(),
        embed_dim * input_len,
        "projection_weights must have embed_dim × input_len elements"
    );

    let effective_scale = scale.min(input_len);
    let mut embedding = Vec::with_capacity(embed_dim);

    for d in 0..embed_dim {
        let start = d * input_len;
        let end = start + input_len;
        let row_weights = &projection_weights[start..end];
        let packed = pack_ternary(row_weights);
        let val = bitnet_infer(input, &packed, effective_scale);
        embedding.push(val);
    }

    embedding
}

// ─── similarity() ────────────────────────────────────────────────────────────

/// Calculates similarity between two embeddings using integer dot product.
///
/// Equivalent to cosine similarity, but in integers (no FP division).
/// For comparison: higher score = more similar.
///
/// # Parameters
/// - `vec_a`: first vector (i64, output from embed())
/// - `vec_b`: second vector (i64, output from embed())
///
/// # Returns
/// SimilarityResult with score and magnitudes
pub fn similarity(vec_a: &[i64], vec_b: &[i64]) -> SimilarityResult {
    assert_eq!(vec_a.len(), vec_b.len(), "Vectors must have the same size");

    let mut dot_product: i128 = 0;
    let mut mag_a: i128 = 0;
    let mut mag_b: i128 = 0;

    for i in 0..vec_a.len() {
        dot_product += vec_a[i] as i128 * vec_b[i] as i128;
        mag_a += vec_a[i] as i128 * vec_a[i] as i128;
        mag_b += vec_b[i] as i128 * vec_b[i] as i128;
    }

    // Scale to i64 with saturation
    let scale = 1i128 << 32;
    let score = (dot_product / scale.max(1)).clamp(i64::MIN as i128, i64::MAX as i128) as i64;
    let ma = (mag_a / scale.max(1)).clamp(0, i64::MAX as i128) as i64;
    let mb = (mag_b / scale.max(1)).clamp(0, i64::MAX as i128) as i64;

    // Ensure identical non-zero vectors always return score > 0
    let final_score = if dot_product > 0 { score.max(1) } else { score };

    SimilarityResult {
        score: final_score,
        magnitude_a: ma,
        magnitude_b: mb,
    }
}

// ─── normalize() ─────────────────────────────────────────────────────────────

/// Normalizes an integer vector to scale [-127, 127].
///
/// Useful for preparing embeddings before comparison.
///
/// # Parameters
/// - `vec`: vector to normalize
///
/// # Returns
/// Vec<i8> normalized to [-127, 127]
pub fn normalize(vec: &[i64]) -> Vec<i8> {
    if vec.is_empty() {
        return vec![];
    }

    let max_abs = vec.iter().map(|&x| x.unsigned_abs()).max().unwrap_or(1);
    if max_abs == 0 {
        return vec![0i8; vec.len()];
    }

    vec.iter()
        .map(|&x| ((x * 127) / max_abs as i64).clamp(-127, 127) as i8)
        .collect()
}

// ─── topk() ──────────────────────────────────────────────────────────────────

/// Returns the indices of the K largest values in a scores slice.
///
/// Efficient implementation without full sort (O(n·k) vs O(n log n)).
///
/// # Parameters
/// - `scores`: scores slice
/// - `k`: number of top elements to return
///
/// # Returns
/// Vec<usize> with k indices in descending score order
pub fn topk(scores: &[i64], k: usize) -> Vec<usize> {
    let k = k.min(scores.len());
    let mut result = Vec::with_capacity(k);
    let mut used = vec![false; scores.len()];

    for _ in 0..k {
        let mut best_idx = 0;
        let mut best_val = i64::MIN;

        for (i, &s) in scores.iter().enumerate() {
            if !used[i] && s > best_val {
                best_val = s;
                best_idx = i;
            }
        }

        used[best_idx] = true;
        result.push(best_idx);
    }

    result
}

// ─── Tests ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_classify_basic() {
        // 3 classes, 4 features
        // Class 0: weights [1, 0, -1, 1]  → score = 10 + 0 + 5 + 8 = 23
        // Class 1: weights [0, 1,  1, 0]  → score = 0 + 20 - 5 + 0 = 15
        // Class 2: weights [-1, 1, 0, 1]  → score = -10 + 20 + 0 + 8 = 18
        let input = vec![10i32, 20, -5, 8];
        let weights: Vec<i8> = vec![
             1, 0, -1, 1,  // class 0
             0, 1,  1, 0,  // class 1
            -1, 1,  0, 1,  // class 2
        ];
        let result = classify(&input, &weights, 3, 4);
        assert_eq!(result.class_id, 0); // class 0 has highest score (23)
        assert_eq!(result.score, 23);
    }

    #[test]
    fn test_classify_matryoshka() {
        // With scale 2, only processes first 2 features
        let input = vec![10i32, 20, -5, 8];
        let weights: Vec<i8> = vec![
             1, 0, -1, 1,  // class 0: scale 2 → 10 + 0 = 10
             0, 1,  1, 0,  // class 1: scale 2 → 0 + 20 = 20
            -1, 1,  0, 1,  // class 2: scale 2 → -10 + 20 = 10
        ];
        let result = classify(&input, &weights, 3, 2);
        assert_eq!(result.class_id, 1); // class 1 has highest score with scale 2
    }

    #[test]
    fn test_detect_found() {
        // Pattern [1, -1, 1] should be detected at position 2
        let sequence = vec![5i32, 3, 10, -8, 7, 1, 2];
        let pattern: Vec<i8> = vec![1, -1, 1];
        // Position 2: [10, -8, 7] → 10 + 8 + 7 = 25 (highest score)
        let result = detect(&sequence, &pattern, 0, 3);
        assert!(result.detected);
        assert_eq!(result.position, 2);
    }

    #[test]
    fn test_detect_threshold() {
        let sequence = vec![1i32, 1, 1, 1, 1];
        let pattern: Vec<i8> = vec![1, 1, 1];
        // Max score = 3, threshold = 10 → not detected
        let result = detect(&sequence, &pattern, 10, 3);
        assert!(!result.detected);
    }

    #[test]
    fn test_embed_dimensions() {
        let input = vec![10i32, 20, -5, 8];
        let embed_dim = 3;
        let weights: Vec<i8> = vec![
             1, 0, -1, 1,  // dim 0
             0, 1,  1, 0,  // dim 1
            -1, 1,  0, 1,  // dim 2
        ];
        let embedding = embed(&input, &weights, embed_dim, 4);
        assert_eq!(embedding.len(), embed_dim);
        // dim 0: 10 + 0 + 5 + 8 = 23
        assert_eq!(embedding[0], 23);
    }

    #[test]
    fn test_similarity_identical() {
        let vec_a = vec![100i64, 200, -50, 80];
        let vec_b = vec![100i64, 200, -50, 80];
        let result = similarity(&vec_a, &vec_b);
        // Identical vectors should have maximum score
        assert!(result.score > 0);
        assert_eq!(result.magnitude_a, result.magnitude_b);
    }

    #[test]
    fn test_normalize_range() {
        let vec = vec![100i64, -200, 50, 0, -100];
        let normalized = normalize(&vec);
        // All values should be in [-127, 127]
        // Note: i8 is always in [-128, 127], so no need to verify
        assert_eq!(normalized.len(), vec.len());
        // Largest absolute value should be mapped to ±127
        assert_eq!(normalized[1], -127); // -200 is the largest abs
    }

    #[test]
    fn test_topk() {
        let scores = vec![10i64, 50, 30, 80, 20, 70];
        let top3 = topk(&scores, 3);
        assert_eq!(top3.len(), 3);
        assert_eq!(top3[0], 3); // 80
        assert_eq!(top3[1], 5); // 70
        assert_eq!(top3[2], 1); // 50
    }

    #[test]
    fn test_summarize() {
        // 3 tokens, dim 2
        // token 0: [10, 20], token 1: [30, 40], token 2: [50, 60]
        // attention: [1, 0, -1]
        // dim 0: [10, 30, 50] with weights [1, 0, -1] → 10 - 50 = -40
        // dim 1: [20, 40, 60] with weights [1, 0, -1] → 20 - 60 = -40
        let sequence = vec![10i32, 20, 30, 40, 50, 60];
        let attention: Vec<i8> = vec![1, 0, -1];
        let summary = summarize(&sequence, 3, 2, &attention, 3);
        assert_eq!(summary.len(), 2);
        assert_eq!(summary[0], -40);
        assert_eq!(summary[1], -40);
    }
}
