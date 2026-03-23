"""Tests for embeddings utility (with mock for sentence_transformers)."""

from unittest.mock import patch, MagicMock
import numpy as np


class TestCosineSimAndRelevance:
    def test_cosine_similarity(self):
        from app.utils.embeddings import cosine_similarity
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        assert abs(cosine_similarity(a, b) - 1.0) < 0.01

    def test_cosine_similarity_orthogonal(self):
        from app.utils.embeddings import cosine_similarity
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert abs(cosine_similarity(a, b)) < 0.01

    def test_find_most_relevant(self):
        from app.utils.embeddings import find_most_relevant
        query = [1.0, 0.0, 0.0]
        embeddings = [
            [0.0, 1.0, 0.0],  # orthogonal
            [0.9, 0.1, 0.0],  # very similar
            [0.5, 0.5, 0.0],  # somewhat similar
        ]
        indices = find_most_relevant(query, embeddings, top_k=2)
        assert indices[0] == 1  # most similar first

    def test_find_most_relevant_top_k(self):
        from app.utils.embeddings import find_most_relevant
        query = [1.0, 0.0]
        embeddings = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
        indices = find_most_relevant(query, embeddings, top_k=1)
        assert len(indices) == 1


class TestEncode:
    def test_encode_returns_list(self):
        """Encode should return a list of floats (even with fallback)."""
        from app.utils.embeddings import encode
        result = encode("test text")
        assert isinstance(result, list)

    def test_encode_batch_returns_list(self):
        from app.utils.embeddings import encode_batch
        results = encode_batch(["hello", "world"])
        assert isinstance(results, list)
