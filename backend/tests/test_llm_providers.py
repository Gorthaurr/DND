"""Tests for LLM provider abstraction."""

from app.utils.llm_providers import (
    LLMProvider, OllamaProvider, OpenAIProvider, AnthropicProvider, create_provider,
)


class TestCreateProvider:
    def test_ollama_default(self):
        p = create_provider("ollama")
        assert isinstance(p, OllamaProvider)

    def test_openai(self):
        p = create_provider("openai")
        assert isinstance(p, OpenAIProvider)

    def test_anthropic(self):
        p = create_provider("anthropic")
        assert isinstance(p, AnthropicProvider)

    def test_unknown_falls_to_ollama(self):
        p = create_provider("unknown")
        assert isinstance(p, OllamaProvider)

    def test_case_insensitive(self):
        p = create_provider("OpenAI")
        assert isinstance(p, OpenAIProvider)


class TestProtocolCompliance:
    def test_ollama_satisfies_protocol(self):
        assert isinstance(OllamaProvider(), LLMProvider)

    def test_openai_satisfies_protocol(self):
        assert isinstance(OpenAIProvider(), LLMProvider)

    def test_anthropic_satisfies_protocol(self):
        assert isinstance(AnthropicProvider(), LLMProvider)


class TestProviderAttributes:
    def test_ollama_has_close(self):
        p = OllamaProvider()
        assert hasattr(p, "close")
        assert hasattr(p, "is_available")

    def test_openai_has_close(self):
        p = OpenAIProvider()
        assert hasattr(p, "close")

    def test_anthropic_has_close(self):
        p = AnthropicProvider()
        assert hasattr(p, "close")
