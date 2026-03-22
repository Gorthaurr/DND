import numpy as np

from app.utils.logger import get_logger

log = get_logger("embeddings")

_model = None
_model_failed = False


def _get_model():
    global _model, _model_failed
    if _model_failed:
        return None
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            log.info("loading_embedding_model")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            log.info("embedding_model_loaded")
        except Exception as e:
            log.warning("embedding_model_failed", error=str(e))
            _model_failed = True
            return None
    return _model


def encode(text: str) -> list[float]:
    """Encode text into embedding vector. Returns empty list if model unavailable."""
    model = _get_model()
    if model is None:
        return []
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def encode_batch(texts: list[str]) -> list[list[float]]:
    """Encode multiple texts into embedding vectors."""
    model = _get_model()
    if model is None:
        return [[] for _ in texts]
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two normalized vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    return float(np.dot(a, b))


def find_most_relevant(query_embedding: list[float], embeddings: list[list[float]], top_k: int = 5) -> list[int]:
    """Return indices of most relevant embeddings sorted by similarity."""
    if not embeddings or not query_embedding:
        return list(range(min(top_k, len(embeddings)))) if embeddings else []
    scores = [cosine_similarity(query_embedding, emb) for emb in embeddings]
    sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return sorted_indices[:top_k]
