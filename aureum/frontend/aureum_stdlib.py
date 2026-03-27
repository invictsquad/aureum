"""
Aureum AI-Native Standard Library — Python Interface
Native AI functions optimized for BitNet b1.58 kernel.

Usage:
    from aureum_stdlib import classify, detect, embed, summarize, similarity

Example (5 lines of AI):
    model = AureumModel(input_dim=512, num_classes=10)
    result = model.classify(my_input)
    print(result.label)

Author: Luiz Antônio De Lima Mendonça
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

import ctypes
import sys
import os
import random
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

# ─── C Structures ─────────────────────────────────────────────────────────────

class _ClassifyResult(ctypes.Structure):
    _fields_ = [
        ("class_id",    ctypes.c_int32),
        ("score",       ctypes.c_int64),
        ("num_classes", ctypes.c_size_t),
    ]

class _DetectResult(ctypes.Structure):
    _fields_ = [
        ("position",   ctypes.c_int32),
        ("confidence", ctypes.c_int64),
        ("detected",   ctypes.c_bool),
    ]

class _SimilarityResult(ctypes.Structure):
    _fields_ = [
        ("score",       ctypes.c_int64),
        ("magnitude_a", ctypes.c_int64),
        ("magnitude_b", ctypes.c_int64),
    ]

# ─── Python Results ───────────────────────────────────────────────────────────

@dataclass
class ClassifyResult:
    """Result from classify()"""
    class_id: int
    score: int
    num_classes: int
    label: str = ""

    def __str__(self):
        return f"Class {self.class_id} (score={self.score})"

@dataclass
class DetectResult:
    """Result from detect()"""
    position: int
    confidence: int
    detected: bool

    def __str__(self):
        status = "DETECTED" if self.detected else "not detected"
        return f"{status} at position {self.position} (confidence={self.confidence})"

@dataclass
class SimilarityResult:
    """Result from similarity()"""
    score: int
    magnitude_a: int
    magnitude_b: int

    @property
    def normalized(self) -> float:
        """Normalized score in [0, 1] (approximate)"""
        denom = max(self.magnitude_a, self.magnitude_b, 1)
        return min(abs(self.score) / denom, 1.0)

    def __str__(self):
        return f"Similarity: {self.score} (normalized≈{self.normalized:.3f})"

# ─── Library Loader ───────────────────────────────────────────────────────────

def _load_lib() -> ctypes.CDLL:
    """Loads the compiled Rust library"""
    if sys.platform == "win32":
        lib_name = "aureum_kernel.dll"
    elif sys.platform == "darwin":
        lib_name = "libaureum_kernel.dylib"
    else:
        lib_name = "libaureum_kernel.so"

    base = Path(__file__).parent.parent / "backend" / "target"
    for profile in ("release", "debug"):
        p = base / profile / lib_name
        if p.exists():
            return ctypes.CDLL(str(p))

    raise RuntimeError(
        f"Library not found. Compile with:\n"
        f"  cd aureum/backend && cargo build --release"
    )

# ─── AureumStdLib ─────────────────────────────────────────────────────────────

class AureumStdLib:
    """
    Interface Python para a AI-Native Standard Library do Aureum.

    Todas as funções rodam no kernel Rust via FFI — zero overhead Python
    nas operações críticas.
    """

    def __init__(self):
        self._lib = _load_lib()
        self._setup()

    def _setup(self):
        """Configures FFI signatures"""
        lib = self._lib

        # classify
        lib.aureum_classify.argtypes = [
            ctypes.POINTER(ctypes.c_int32),  # input
            ctypes.c_size_t,                  # input_len
            ctypes.POINTER(ctypes.c_int8),    # weights
            ctypes.c_size_t,                  # num_classes
            ctypes.c_size_t,                  # scale
            ctypes.POINTER(_ClassifyResult),  # result
        ]
        lib.aureum_classify.restype = None

        # detect
        lib.aureum_detect.argtypes = [
            ctypes.POINTER(ctypes.c_int32),  # sequence
            ctypes.c_size_t,                  # seq_len
            ctypes.POINTER(ctypes.c_int8),    # pattern
            ctypes.c_size_t,                  # pattern_len
            ctypes.c_int64,                   # threshold
            ctypes.c_size_t,                  # scale
            ctypes.POINTER(_DetectResult),    # result
        ]
        lib.aureum_detect.restype = None

        # embed
        lib.aureum_embed.argtypes = [
            ctypes.POINTER(ctypes.c_int32),  # input
            ctypes.c_size_t,                  # input_len
            ctypes.POINTER(ctypes.c_int8),    # weights
            ctypes.c_size_t,                  # embed_dim
            ctypes.c_size_t,                  # scale
            ctypes.POINTER(ctypes.c_int64),   # output
        ]
        lib.aureum_embed.restype = None

        # summarize
        lib.aureum_summarize.argtypes = [
            ctypes.POINTER(ctypes.c_int32),  # sequence
            ctypes.c_size_t,                  # num_tokens
            ctypes.c_size_t,                  # dim
            ctypes.POINTER(ctypes.c_int8),    # attention
            ctypes.c_size_t,                  # scale
            ctypes.POINTER(ctypes.c_int64),   # output
        ]
        lib.aureum_summarize.restype = None

        # similarity
        lib.aureum_similarity.argtypes = [
            ctypes.POINTER(ctypes.c_int64),      # vec_a
            ctypes.POINTER(ctypes.c_int64),      # vec_b
            ctypes.c_size_t,                      # len
            ctypes.POINTER(_SimilarityResult),   # result
        ]
        lib.aureum_similarity.restype = None

        # normalize
        lib.aureum_normalize.argtypes = [
            ctypes.POINTER(ctypes.c_int64),  # input
            ctypes.c_size_t,                  # len
            ctypes.POINTER(ctypes.c_int8),    # output
        ]
        lib.aureum_normalize.restype = None

        # topk
        lib.aureum_topk.argtypes = [
            ctypes.POINTER(ctypes.c_int64),  # scores
            ctypes.c_size_t,                  # scores_len
            ctypes.c_size_t,                  # k
            ctypes.POINTER(ctypes.c_size_t),  # output
        ]
        lib.aureum_topk.restype = ctypes.c_size_t

    # ─── classify() ───────────────────────────────────────────────────────────

    def classify(
        self,
        input_data: List[int],
        weights: List[int],
        num_classes: int,
        scale: Optional[int] = None,
        labels: Optional[List[str]] = None,
    ) -> ClassifyResult:
        """
        Classifies input vector into one of num_classes classes.

        Args:
            input_data:  input vector (int16 as int)
            weights:     ternary weights {-1,0,1} of all classes
                         concatenated (num_classes × len(input_data))
            num_classes: number of classes
            scale:       Matryoshka scale (None = full)
            labels:      class names (optional)

        Returns:
            ClassifyResult with class_id, score and label
        """
        n = len(input_data)
        scale = scale or n

        inp = (ctypes.c_int32 * n)(*input_data)
        wts = (ctypes.c_int8 * len(weights))(*weights)
        res = _ClassifyResult()

        self._lib.aureum_classify(inp, n, wts, num_classes, scale, ctypes.byref(res))

        label = ""
        if labels and 0 <= res.class_id < len(labels):
            label = labels[res.class_id]

        return ClassifyResult(
            class_id=res.class_id,
            score=res.score,
            num_classes=res.num_classes,
            label=label,
        )

    # ─── detect() ─────────────────────────────────────────────────────────────

    def detect(
        self,
        sequence: List[int],
        pattern: List[int],
        threshold: int = 0,
        scale: Optional[int] = None,
    ) -> DetectResult:
        """
        Detects pattern in sequence using BitNet sliding window.

        Args:
            sequence:  input sequence
            pattern:   ternary weights of pattern to detect
            threshold: minimum score for positive detection
            scale:     Matryoshka scale

        Returns:
            DetectResult with position, confidence and detected flag
        """
        scale = scale or len(pattern)

        seq = (ctypes.c_int32 * len(sequence))(*sequence)
        pat = (ctypes.c_int8 * len(pattern))(*pattern)
        res = _DetectResult()

        self._lib.aureum_detect(
            seq, len(sequence),
            pat, len(pattern),
            threshold, scale,
            ctypes.byref(res)
        )

        return DetectResult(
            position=res.position,
            confidence=res.confidence,
            detected=res.detected,
        )

    # ─── embed() ──────────────────────────────────────────────────────────────

    def embed(
        self,
        input_data: List[int],
        weights: List[int],
        embed_dim: int,
        scale: Optional[int] = None,
    ) -> List[int]:
        """
        Generates compact embedding via ternary projection.

        Args:
            input_data: input vector
            weights:    ternary projection matrix (embed_dim × input_len)
            embed_dim:  output embedding dimension
            scale:      Matryoshka scale

        Returns:
            List[int] with embedding (embed_dim elements)
        """
        n = len(input_data)
        scale = scale or n

        inp = (ctypes.c_int32 * n)(*input_data)
        wts = (ctypes.c_int8 * len(weights))(*weights)
        out = (ctypes.c_int64 * embed_dim)()

        self._lib.aureum_embed(inp, n, wts, embed_dim, scale, out)

        return list(out)

    # ─── summarize() ──────────────────────────────────────────────────────────

    def summarize(
        self,
        sequence: List[int],
        num_tokens: int,
        dim: int,
        attention: List[int],
        scale: Optional[int] = None,
    ) -> List[int]:
        """
        Summarizes sequence of vectors by ternary attention.

        Args:
            sequence:   concatenated vectors (num_tokens × dim)
            num_tokens: number of tokens
            dim:        dimension of each vector
            attention:  ternary attention weights (num_tokens elements)
            scale:      Matryoshka scale

        Returns:
            List[int] with summarized vector (dim elements)
        """
        scale = scale or num_tokens

        seq = (ctypes.c_int32 * len(sequence))(*sequence)
        attn = (ctypes.c_int8 * len(attention))(*attention)
        out = (ctypes.c_int64 * dim)()

        self._lib.aureum_summarize(seq, num_tokens, dim, attn, scale, out)

        return list(out)

    # ─── similarity() ─────────────────────────────────────────────────────────

    def similarity(
        self,
        vec_a: List[int],
        vec_b: List[int],
    ) -> SimilarityResult:
        """
        Calculates similarity between two embeddings.

        Args:
            vec_a: primeiro embedding (saída de embed())
            vec_b: segundo embedding (saída de embed())

        Returns:
            SimilarityResult com score e magnitudes
        """
        assert len(vec_a) == len(vec_b)
        n = len(vec_a)

        a = (ctypes.c_int64 * n)(*vec_a)
        b = (ctypes.c_int64 * n)(*vec_b)
        res = _SimilarityResult()

        self._lib.aureum_similarity(a, b, n, ctypes.byref(res))

        return SimilarityResult(
            score=res.score,
            magnitude_a=res.magnitude_a,
            magnitude_b=res.magnitude_b,
        )

    # ─── normalize() ──────────────────────────────────────────────────────────

    def normalize(self, vec: List[int]) -> List[int]:
        """
        Normalizes embedding vector to [-127, 127].

        Args:
            vec: i64 vector (output from embed())

        Returns:
            List[int] normalized to [-127, 127]
        """
        n = len(vec)
        inp = (ctypes.c_int64 * n)(*vec)
        out = (ctypes.c_int8 * n)()

        self._lib.aureum_normalize(inp, n, out)

        return list(out)

    # ─── topk() ───────────────────────────────────────────────────────────────

    def topk(self, scores: List[int], k: int) -> List[int]:
        """
        Returns indices of K highest scores.

        Args:
            scores: list of scores
            k:      number of top elements

        Returns:
            List[int] with k indices in descending order
        """
        n = len(scores)
        k = min(k, n)

        sc = (ctypes.c_int64 * n)(*scores)
        out = (ctypes.c_size_t * k)()

        written = self._lib.aureum_topk(sc, n, k, out)

        return list(out[:written])


# ─── AureumModel — High-Level API ────────────────────────────────────────────

class AureumModel:
    """
    High-level AI model — simplified API for junior developers.

    Usage example (5 lines):
        model = AureumModel(input_dim=512, num_classes=10)
        model.load_weights(my_weights)
        result = model.classify(my_input)
        print(result.label)
    """

    def __init__(
        self,
        input_dim: int,
        num_classes: int = 0,
        embed_dim: int = 128,
        labels: Optional[List[str]] = None,
        scale: Optional[int] = None,
    ):
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.embed_dim = embed_dim
        self.labels = labels or [f"class_{i}" for i in range(num_classes)]
        self.scale = scale or input_dim

        self._stdlib = AureumStdLib()
        self._classify_weights: Optional[List[int]] = None
        self._embed_weights: Optional[List[int]] = None

    def load_weights(
        self,
        classify_weights: Optional[List[int]] = None,
        embed_weights: Optional[List[int]] = None,
    ):
        """
        Loads ternary weights into model.

        Args:
            classify_weights: classification weights (num_classes × input_dim)
            embed_weights:    embedding weights (embed_dim × input_dim)
        """
        self._classify_weights = classify_weights
        self._embed_weights = embed_weights
        return self

    def random_weights(self, seed: int = 42) -> "AureumModel":
        """
        Initializes random ternary weights {-1, 0, 1}.
        Useful for rapid prototyping.
        """
        rng = random.Random(seed)
        choices = [-1, 0, 0, 1]  # 0 with higher probability (sparsity)

        if self.num_classes > 0:
            self._classify_weights = [
                rng.choice(choices)
                for _ in range(self.num_classes * self.input_dim)
            ]

        self._embed_weights = [
            rng.choice(choices)
            for _ in range(self.embed_dim * self.input_dim)
        ]
        return self

    def classify(self, input_data: List[int]) -> ClassifyResult:
        """
        Classifies input vector.

        Args:
            input_data: input vector (int16 as int, size = input_dim)

        Returns:
            ClassifyResult with class_id, score and label
        """
        if self._classify_weights is None:
            raise RuntimeError("Weights not loaded. Use load_weights() or random_weights()")

        return self._stdlib.classify(
            input_data,
            self._classify_weights,
            self.num_classes,
            scale=self.scale,
            labels=self.labels,
        )

    def embed(self, input_data: List[int]) -> List[int]:
        """
        Generates embedding from input vector.

        Args:
            input_data: input vector

        Returns:
            List[int] with embedding of size embed_dim
        """
        if self._embed_weights is None:
            raise RuntimeError("Weights not loaded. Use load_weights() or random_weights()")

        return self._stdlib.embed(
            input_data,
            self._embed_weights,
            self.embed_dim,
            scale=self.scale,
        )

    def similarity(self, input_a: List[int], input_b: List[int]) -> SimilarityResult:
        """
        Calculates similarity between two input vectors.

        Internally generates embeddings of both and compares.
        """
        emb_a = self.embed(input_a)
        emb_b = self.embed(input_b)
        return self._stdlib.similarity(emb_a, emb_b)

    def detect(
        self,
        sequence: List[int],
        pattern: List[int],
        threshold: int = 0,
    ) -> DetectResult:
        """
        Detects pattern in sequence.
        """
        return self._stdlib.detect(sequence, pattern, threshold, self.scale)

    def topk_classes(self, input_data: List[int], k: int = 3) -> List[ClassifyResult]:
        """
        Returns the K most probable classes.

        Args:
            input_data: input vector
            k:          number of classes to return

        Returns:
            List[ClassifyResult] with k best classes
        """
        if self._classify_weights is None:
            raise RuntimeError("Weights not loaded.")

        # Calculate score for each class individually
        scores = []
        for c in range(self.num_classes):
            start = c * self.input_dim
            end = start + self.input_dim
            class_w = self._classify_weights[start:end]
            result = self._stdlib.classify(
                input_data, class_w, 1, scale=self.scale
            )
            scores.append(result.score)

        top_indices = self._stdlib.topk(scores, k)

        return [
            ClassifyResult(
                class_id=idx,
                score=scores[idx],
                num_classes=self.num_classes,
                label=self.labels[idx] if idx < len(self.labels) else f"class_{idx}",
            )
            for idx in top_indices
        ]


# ─── Global Singleton ─────────────────────────────────────────────────────────

_stdlib_instance: Optional[AureumStdLib] = None

def get_stdlib() -> AureumStdLib:
    """Returns singleton instance of stdlib"""
    global _stdlib_instance
    if _stdlib_instance is None:
        _stdlib_instance = AureumStdLib()
    return _stdlib_instance


# ─── Convenience Functions (top-level API) ────────────────────────────────────

def classify(input_data, weights, num_classes, scale=None, labels=None):
    """Classifies input vector. See AureumStdLib.classify()"""
    return get_stdlib().classify(input_data, weights, num_classes, scale, labels)

def detect(sequence, pattern, threshold=0, scale=None):
    """Detects pattern in sequence. See AureumStdLib.detect()"""
    return get_stdlib().detect(sequence, pattern, threshold, scale)

def embed(input_data, weights, embed_dim, scale=None):
    """Generates embedding. See AureumStdLib.embed()"""
    return get_stdlib().embed(input_data, weights, embed_dim, scale)

def summarize(sequence, num_tokens, dim, attention, scale=None):
    """Summarizes sequence. See AureumStdLib.summarize()"""
    return get_stdlib().summarize(sequence, num_tokens, dim, attention, scale)

def similarity(vec_a, vec_b):
    """Calculates similarity. See AureumStdLib.similarity()"""
    return get_stdlib().similarity(vec_a, vec_b)

def normalize(vec):
    """Normalizes vector. See AureumStdLib.normalize()"""
    return get_stdlib().normalize(vec)

def topk(scores, k):
    """Top-K indices. See AureumStdLib.topk()"""
    return get_stdlib().topk(scores, k)
