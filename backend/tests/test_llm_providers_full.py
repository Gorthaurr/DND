"""Tests for app.utils.llm_providers — OllamaProvider, OpenAIProvider, AnthropicProvider, create_provider."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.llm_providers import (
    AnthropicProvider,
    LLMProvider,
    OllamaProvider,
    OpenAIProvider,
    create_provider,
)


# ── create_provider factory ──────────────────────────────────────────────

def test_create_provider_ollama():
    with patch("app.utils.llm_providers.settings") as s:
        s.llm_provider = "ollama"
        p = create_provider()
    assert isinstance(p, OllamaProvider)


def test_create_provider_openai():
    with patch("app.utils.llm_providers.settings") as s:
        s.llm_provider = "openai"
        p = create_provider()
    assert isinstance(p, OpenAIProvider)


def test_create_provider_anthropic():
    with patch("app.utils.llm_providers.settings") as s:
        s.llm_provider = "anthropic"
        p = create_provider()
    assert isinstance(p, AnthropicProvider)


def test_create_provider_explicit_name():
    p = create_provider("openai")
    assert isinstance(p, OpenAIProvider)


def test_create_provider_unknown_defaults_ollama():
    p = create_provider("something_unknown")
    assert isinstance(p, OllamaProvider)


def test_providers_implement_protocol():
    """All providers satisfy the LLMProvider protocol."""
    assert isinstance(OllamaProvider(), LLMProvider)
    assert isinstance(OpenAIProvider(), LLMProvider)
    assert isinstance(AnthropicProvider(), LLMProvider)


# ── OllamaProvider ───────────────────────────────────────────────────────

class TestOllamaProvider:

    @pytest.fixture
    def provider(self):
        with patch("app.utils.llm_providers.settings") as s:
            s.ollama_base_url = "http://localhost:11434"
            s.ollama_model = "test-model"
            s.ollama_temperature = 0.7
            s.llm_max_concurrent = 5
            s.llm_retry_base_delay = 0.01  # fast retries in tests
            yield OllamaProvider()

    @pytest.mark.asyncio
    async def test_generate_success(self, provider):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": "Hello world"}
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_resp)
        mock_client.is_closed = False
        provider._client = mock_client

        result = await provider.generate("Say hello", system="Be nice")
        assert result == "Hello world"
        mock_client.post.assert_awaited_once()
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json") or call_kwargs[0][1]
        # Verify system prompt was included
        if isinstance(payload, dict):
            assert payload.get("system") == "Be nice"

    @pytest.mark.asyncio
    async def test_generate_timeout_retries(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        provider._client = mock_client

        result = await provider.generate("test")
        assert result == ""
        assert mock_client.post.await_count == 3  # max_retries

    @pytest.mark.asyncio
    async def test_generate_server_error_retries(self, provider):
        error_resp = httpx.Response(500, request=httpx.Request("POST", "http://test"))
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(side_effect=httpx.HTTPStatusError("500", request=error_resp.request, response=error_resp))
        provider._client = mock_client

        result = await provider.generate("test")
        assert result == ""
        assert mock_client.post.await_count == 3

    @pytest.mark.asyncio
    async def test_generate_client_error_no_retry(self, provider):
        error_resp = httpx.Response(400, request=httpx.Request("POST", "http://test"))
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(side_effect=httpx.HTTPStatusError("400", request=error_resp.request, response=error_resp))
        provider._client = mock_client

        result = await provider.generate("test")
        assert result == ""
        assert mock_client.post.await_count == 1  # no retry for 4xx

    @pytest.mark.asyncio
    async def test_generate_http_error_retries(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(side_effect=httpx.HTTPError("connection failed"))
        provider._client = mock_client

        result = await provider.generate("test")
        assert result == ""
        assert mock_client.post.await_count == 3

    @pytest.mark.asyncio
    async def test_close(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()
        provider._client = mock_client

        await provider.close()
        mock_client.aclose.assert_awaited_once()
        assert provider._client is None

    @pytest.mark.asyncio
    async def test_close_already_closed(self, provider):
        provider._client = None
        await provider.close()  # should not raise

    @pytest.mark.asyncio
    async def test_is_available_true(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        provider._client = mock_client

        assert await provider.is_available() is True

    @pytest.mark.asyncio
    async def test_is_available_false(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.get = AsyncMock(side_effect=ConnectionError("down"))
        provider._client = mock_client

        assert await provider.is_available() is False


# ── OpenAIProvider ───────────────────────────────────────────────────────

class TestOpenAIProvider:

    @pytest.fixture
    def provider(self):
        with patch("app.utils.llm_providers.settings") as s:
            s.openai_base_url = "https://api.openai.com/v1"
            s.openai_api_key = "test-key"
            s.openai_model = "gpt-4o-mini"
            s.ollama_temperature = 0.7
            s.llm_max_concurrent = 5
            s.llm_retry_base_delay = 0.01
            yield OpenAIProvider()

    @pytest.mark.asyncio
    async def test_generate_success(self, provider):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "I am GPT."}}]
        }
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=mock_resp)
        provider._client = mock_client

        result = await provider.generate("Who are you?", system="You are helpful.")
        assert result == "I am GPT."

    @pytest.mark.asyncio
    async def test_generate_with_system_message(self, provider):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=mock_resp)
        provider._client = mock_client

        await provider.generate("test", system="Be concise.")
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1]["json"]
        messages = payload["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Be concise."
        assert messages[1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_generate_timeout_retries(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        provider._client = mock_client

        result = await provider.generate("test")
        assert result == ""
        assert mock_client.post.await_count == 3

    @pytest.mark.asyncio
    async def test_generate_rate_limited_retries(self, provider):
        error_resp = httpx.Response(429, request=httpx.Request("POST", "http://test"))
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(side_effect=httpx.HTTPStatusError("429", request=error_resp.request, response=error_resp))
        provider._client = mock_client

        result = await provider.generate("test")
        assert result == ""
        assert mock_client.post.await_count == 3

    @pytest.mark.asyncio
    async def test_close(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()
        provider._client = mock_client

        await provider.close()
        mock_client.aclose.assert_awaited_once()


# ── AnthropicProvider ────────────────────────────────────────────────────

class TestAnthropicProvider:

    @pytest.fixture
    def provider(self):
        with patch("app.utils.llm_providers.settings") as s:
            s.anthropic_api_key = "test-key"
            s.anthropic_model = "claude-sonnet-4-20250514"
            s.ollama_temperature = 0.7
            s.llm_max_concurrent = 5
            s.llm_retry_base_delay = 0.01
            yield AnthropicProvider()

    @pytest.mark.asyncio
    async def test_generate_success(self, provider):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "content": [{"text": "I am Claude."}]
        }
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=mock_resp)
        provider._client = mock_client

        result = await provider.generate("Who are you?")
        assert result == "I am Claude."

    @pytest.mark.asyncio
    async def test_generate_with_system_caching(self, provider):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"content": [{"text": "ok"}]}
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=mock_resp)
        provider._client = mock_client

        await provider.generate("test", system="World context here.")
        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1]["json"]
        # Anthropic uses cache_control for system prompts
        assert "system" in payload
        assert payload["system"][0]["cache_control"] == {"type": "ephemeral"}

    @pytest.mark.asyncio
    async def test_generate_timeout_retries(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        provider._client = mock_client

        result = await provider.generate("test")
        assert result == ""
        assert mock_client.post.await_count == 3

    @pytest.mark.asyncio
    async def test_generate_rate_limited_retries(self, provider):
        error_resp = httpx.Response(429, request=httpx.Request("POST", "http://test"))
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(side_effect=httpx.HTTPStatusError("429", request=error_resp.request, response=error_resp))
        provider._client = mock_client

        result = await provider.generate("test")
        assert result == ""
        assert mock_client.post.await_count == 3

    @pytest.mark.asyncio
    async def test_close(self, provider):
        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()
        provider._client = mock_client

        await provider.close()
        mock_client.aclose.assert_awaited_once()


# ── Client lazy init ─────────────────────────────────────────────────────

class TestClientLazyInit:

    def test_ollama_creates_client_on_demand(self):
        with patch("app.utils.llm_providers.settings") as s:
            s.ollama_base_url = "http://localhost:11434"
            s.llm_max_concurrent = 3
            p = OllamaProvider()
        assert p._client is None
        client = p._get_client()
        assert client is not None

    def test_openai_creates_client_on_demand(self):
        with patch("app.utils.llm_providers.settings") as s:
            s.openai_base_url = "https://api.openai.com/v1"
            s.openai_api_key = "key"
            s.llm_max_concurrent = 3
            p = OpenAIProvider()
        assert p._client is None
        client = p._get_client()
        assert client is not None

    def test_anthropic_creates_client_on_demand(self):
        with patch("app.utils.llm_providers.settings") as s:
            s.anthropic_api_key = "key"
            s.llm_max_concurrent = 3
            p = AnthropicProvider()
        assert p._client is None
        client = p._get_client()
        assert client is not None

    def test_semaphore_created_once(self):
        with patch("app.utils.llm_providers.settings") as s:
            s.ollama_base_url = "http://localhost:11434"
            s.llm_max_concurrent = 3
            p = OllamaProvider()
        s1 = p._get_semaphore()
        s2 = p._get_semaphore()
        assert s1 is s2
