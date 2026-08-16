"""Embedder helpers with offline fallback."""
import hashlib
from typing import List, Optional, Any

import numpy as np

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    _HAS_ST = True
except Exception:  # pragma: no cover
    _HAS_ST = False


FALLBACK_DIM = 384


class HashEmbedder:
    """Deterministic offline embedder implementing the SentenceTransformer
    surface area used by the memory/RAG subsystems."""

    def __init__(self, dim: int = FALLBACK_DIM, model_name: Optional[str] = None):
        self.dim = dim
        self.model_name = model_name or "hash-fallback"

    def get_sentence_embedding_dimension(self) -> int:
        return self.dim

    def encode(self, sentences: List[str], **kwargs: Any) -> np.ndarray:
        vectors = []
        for s in sentences:
            text = s if isinstance(s, str) else str(s)
            seed = hashlib.sha256(text.encode("utf-8")).digest()
            needed = self.dim * 4
            buf = (seed * ((needed // len(seed)) + 1))[:needed]
            arr = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
            arr = (arr - 128.0) / 128.0
            if arr.shape[0] > self.dim:
                arr = arr[: self.dim]
            elif arr.shape[0] < self.dim:
                arr = np.pad(arr, (0, self.dim - arr.shape[0]))
            norm = np.linalg.norm(arr)
            if norm > 0:
                arr = arr / norm
            vectors.append(arr)
        return np.array(vectors)


def get_embedder(model_name: Optional[str] = None, dim: int = FALLBACK_DIM):
    """Return a SentenceTransformer when available; otherwise a HashEmbedder.

    Falls back gracefully when the model cannot be downloaded (offline CI,
    invalid model id, etc.).
    """
    if _HAS_ST:
        try:
            return SentenceTransformer(model_name) if model_name else SentenceTransformer()
        except Exception:
            pass
    return HashEmbedder(dim=dim, model_name=model_name)
