"""
Aureum Fast API - Convenience functions for quick AI operations

These are the "magic" functions that make Aureum feel effortless.
Perfect for developers who want speed without complexity.

Usage:
    import aureum as au
    result = au.fast_compute(my_data, my_weights)

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

from typing import List, Optional
from .frontend.aureum_ffi import get_kernel
from .frontend.aureum_stdlib import AureumModel, ClassifyResult

def fast_compute(
    input_data: List[int],
    weights: List[int],
    scale: Optional[int] = None
) -> int:
    """
    Ultra-fast computation using BitNet kernel
    
    Perfect for: Heavy tensor operations that would be slow in Python
    
    Args:
        input_data: Your input vector (int16 as int)
        weights: Ternary weights {-1, 0, 1}
        scale: Matryoshka scale (None = full)
    
    Returns:
        int: Result (10-100x faster than NumPy)
    
    Example:
        >>> result = fast_compute([10, 20, 30], [1, 0, -1])
        >>> print(result)  # 10 + 0 - 30 = -20
    """
    kernel = get_kernel()
    packed = kernel.pack_ternary(weights)
    return kernel.bitnet_infer(input_data, packed, scale or len(input_data))


def fast_infer(
    input_data: List[int],
    model_weights: List[int],
    num_classes: int,
    labels: Optional[List[str]] = None
) -> ClassifyResult:
    """
    Fast inference for classification tasks
    
    Perfect for: Real-time classification on edge devices
    
    Args:
        input_data: Input vector
        model_weights: All class weights concatenated
        num_classes: Number of classes
        labels: Optional class names
    
    Returns:
        ClassifyResult with predicted class
    
    Example:
        >>> result = fast_infer(
        ...     [10, 20, 30],
        ...     [1, 0, -1, 0, 1, 1, -1, 1, 0],  # 3 classes x 3 features
        ...     num_classes=3,
        ...     labels=["cat", "dog", "bird"]
        ... )
        >>> print(result.label)  # "dog"
    """
    model = AureumModel(
        input_dim=len(input_data),
        num_classes=num_classes,
        labels=labels
    )
    model.load_weights(classify_weights=model_weights)
    return model.classify(input_data)


def fast_classify(
    input_data: List[int],
    model_weights: List[int],
    num_classes: int,
    labels: Optional[List[str]] = None
) -> str:
    """
    Fast classification returning just the label
    
    Perfect for: When you just want the answer, not the details
    
    Args:
        input_data: Input vector
        model_weights: All class weights
        num_classes: Number of classes
        labels: Class names
    
    Returns:
        str: Predicted class label
    
    Example:
        >>> label = fast_classify(my_image, my_model, 10, ["0", "1", ..., "9"])
        >>> print(f"Predicted digit: {label}")
    """
    result = fast_infer(input_data, model_weights, num_classes, labels)
    return result.label


def fast_embed(
    input_data: List[int],
    embed_weights: List[int],
    embed_dim: int = 128
) -> List[int]:
    """
    Fast embedding generation
    
    Perfect for: Semantic search, similarity matching, RAG systems
    
    Args:
        input_data: Input vector (e.g., tokenized text)
        embed_weights: Projection matrix (embed_dim x input_len)
        embed_dim: Embedding dimension
    
    Returns:
        List[int]: Compact embedding vector
    
    Example:
        >>> text_embedding = fast_embed(tokenize("hello world"), model_weights, 128)
        >>> # Now compare with other embeddings for similarity
    """
    model = AureumModel(
        input_dim=len(input_data),
        embed_dim=embed_dim
    )
    model.load_weights(embed_weights=embed_weights)
    return model.embed(input_data)


def fast_similarity(
    text_a: List[int],
    text_b: List[int],
    embed_weights: List[int],
    embed_dim: int = 128
) -> float:
    """
    Fast similarity between two inputs
    
    Perfect for: Semantic search, duplicate detection, recommendation
    
    Args:
        text_a: First input vector
        text_b: Second input vector
        embed_weights: Shared embedding weights
        embed_dim: Embedding dimension
    
    Returns:
        float: Similarity score (0-1, higher = more similar)
    
    Example:
        >>> sim = fast_similarity(
        ...     tokenize("machine learning"),
        ...     tokenize("deep learning"),
        ...     model_weights,
        ...     128
        ... )
        >>> print(f"Similarity: {sim:.2%}")
    """
    model = AureumModel(
        input_dim=len(text_a),
        embed_dim=embed_dim
    )
    model.load_weights(embed_weights=embed_weights)
    
    result = model.similarity(text_a, text_b)
    return result.normalized


# Convenience aliases
compute = fast_compute
infer = fast_infer
classify = fast_classify
embed = fast_embed
similarity = fast_similarity
