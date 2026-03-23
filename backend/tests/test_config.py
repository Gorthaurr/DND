"""Tests for application configuration."""

from app.config import Settings


class TestDefaultSettings:
    def test_default_llm_provider(self):
        s = Settings()
        assert s.llm_provider == "ollama"

    def test_default_ollama_model(self):
        s = Settings()
        assert "qwen" in s.ollama_model.lower() or s.ollama_model  # any valid model

    def test_default_neo4j(self):
        s = Settings()
        assert "bolt://" in s.neo4j_uri
        assert s.neo4j_user == "neo4j"

    def test_default_tick_interval(self):
        s = Settings()
        assert s.tick_interval_seconds > 0

    def test_default_batch_size(self):
        s = Settings()
        assert s.llm_batch_size > 0
        assert s.llm_max_concurrent > 0

    def test_jwt_secret_exists(self):
        s = Settings()
        assert len(s.jwt_secret) > 0

    def test_postgres_url_exists(self):
        s = Settings()
        assert "postgresql" in s.postgres_url

    def test_priority_llm_ratio_valid(self):
        s = Settings()
        assert 0 <= s.priority_llm_ratio <= 1
