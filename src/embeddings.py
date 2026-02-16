"""
Sentence-T5 embeddings for semantic similarity and entity extraction.
Lazy-loads model for efficiency.
"""

from typing import Optional

_MODEL: Optional[object] = None


def get_embedding_model():
    """Lazy-load sentence-transformers model."""
    global _MODEL
    if _MODEL is None:
        from src.hf_auth import login as hf_login
        hf_login()
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # lighter fallback
    return _MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Compute embeddings for a list of texts."""
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_single(text: str) -> list[float]:
    """Compute embedding for a single text."""
    return embed_texts([text])[0]


def similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors."""
    import math

    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
