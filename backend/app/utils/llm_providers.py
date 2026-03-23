"""Multi-provider LLM abstraction.

Supports Ollama (local), OpenAI-compatible APIs (OpenRouter, Together, etc.),
and Anthropic. Developers choose provider + model via config.
"""

from __future__ import annotations

import asyncio
import json
import random as _rng
from typing import Protocol, runtime_checkable

import httpx

from app.config import settings
from app.utils.logger import get_logger

log = get_logger("llm_providers")


@runtime_checkable
class LLMProvider(Protocol):
    """Interface that all LLM providers must implement."""

    async def generate(
        self, prompt: str, system: str = "", temperature: float | None = None,
    ) -> str: ...


class OllamaProvider:
    """Ollama local inference via HTTP API."""

    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self._semaphore: asyncio.Semaphore | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.ollama_base_url,
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
        return self._client

    def _get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(settings.llm_max_concurrent)
        return self._semaphore

    async def generate(
        self, prompt: str, system: str = "", temperature: float | None = None,
    ) -> str:
        client = self._get_client()
        sem = self._get_semaphore()
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature or settings.ollama_temperature},
        }
        if system:
            payload["system"] = system

        max_retries = 3
        base_delay = settings.llm_retry_base_delay

        async with sem:
            for attempt in range(max_retries):
                try:
                    resp = await client.post("/api/generate", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    return data.get("response", "")
                except httpx.TimeoutException:
                    delay = base_delay * (2 ** attempt) + _rng.uniform(0, 0.5)
                    log.warning("ollama_timeout", attempt=attempt, retry_in=f"{delay:.1f}s")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                except httpx.HTTPStatusError as e:
                    log.warning("ollama_http_error", attempt=attempt, status=e.response.status_code)
                    if e.response.status_code >= 500 and attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                    else:
                        break
                except httpx.HTTPError as e:
                    delay = base_delay * (2 ** attempt) + _rng.uniform(0, 0.5)
                    log.warning("ollama_request_failed", attempt=attempt, error=str(e))
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)

        log.error("ollama_all_retries_exhausted")
        return ""

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def is_available(self) -> bool:
        try:
            client = self._get_client()
            resp = await client.get("/api/tags", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False


class OpenAIProvider:
    """OpenAI-compatible API (works with OpenRouter, Together, vLLM, etc.)."""

    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self._semaphore: asyncio.Semaphore | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.openai_base_url,
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
        return self._client

    def _get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(settings.llm_max_concurrent)
        return self._semaphore

    async def generate(
        self, prompt: str, system: str = "", temperature: float | None = None,
    ) -> str:
        client = self._get_client()
        sem = self._get_semaphore()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.openai_model,
            "messages": messages,
            "temperature": temperature or settings.ollama_temperature,
        }

        max_retries = 3
        base_delay = settings.llm_retry_base_delay

        async with sem:
            for attempt in range(max_retries):
                try:
                    resp = await client.post("/chat/completions", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                except httpx.TimeoutException:
                    delay = base_delay * (2 ** attempt) + _rng.uniform(0, 0.5)
                    log.warning("openai_timeout", attempt=attempt)
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        delay = base_delay * (2 ** attempt) + _rng.uniform(1, 3)
                        log.warning("openai_rate_limited", attempt=attempt)
                        if attempt < max_retries - 1:
                            await asyncio.sleep(delay)
                    elif e.response.status_code >= 500 and attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                    else:
                        log.error("openai_error", status=e.response.status_code,
                                  body=e.response.text[:200])
                        break
                except httpx.HTTPError as e:
                    log.warning("openai_request_failed", attempt=attempt, error=str(e))
                    if attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))

        log.error("openai_all_retries_exhausted")
        return ""

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


class AnthropicProvider:
    """Anthropic Messages API."""

    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self._semaphore: asyncio.Semaphore | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url="https://api.anthropic.com",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
        return self._client

    def _get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(settings.llm_max_concurrent)
        return self._semaphore

    async def generate(
        self, prompt: str, system: str = "", temperature: float | None = None,
    ) -> str:
        client = self._get_client()
        sem = self._get_semaphore()
        payload: dict = {
            "model": settings.anthropic_model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature or settings.ollama_temperature,
        }
        if system:
            # Use prompt caching: system prompt is cached for 5 minutes
            # This saves 30-50% on tokens when making repeated calls with same world context
            payload["system"] = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ]

        max_retries = 3
        base_delay = settings.llm_retry_base_delay

        async with sem:
            for attempt in range(max_retries):
                try:
                    resp = await client.post("/v1/messages", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    return data["content"][0]["text"]
                except httpx.TimeoutException:
                    delay = base_delay * (2 ** attempt) + _rng.uniform(0, 0.5)
                    log.warning("anthropic_timeout", attempt=attempt)
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt) + _rng.uniform(1, 3))
                    elif e.response.status_code >= 500 and attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))
                    else:
                        log.error("anthropic_error", status=e.response.status_code)
                        break
                except httpx.HTTPError as e:
                    log.warning("anthropic_request_failed", attempt=attempt, error=str(e))
                    if attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))

        log.error("anthropic_all_retries_exhausted")
        return ""

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


# ── Provider factory ──────────────────────────────────────────

def create_provider(provider_name: str | None = None) -> LLMProvider:
    """Create LLM provider based on config or explicit name."""
    name = (provider_name or settings.llm_provider).lower()
    if name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    else:
        return OllamaProvider()
