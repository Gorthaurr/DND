"""Async Claude API client with rate limiting and retries."""

from __future__ import annotations

import asyncio
import json
import logging
import re

import anthropic

from finetune.config import (
    CLAUDE_HAIKU_MODEL,
    CLAUDE_MAX_RETRIES,
    CLAUDE_SONNET_MODEL,
    SONNET_AGENT_TYPES,
)

logger = logging.getLogger(__name__)

# Pricing per 1M tokens (USD) — used for cost estimation only.
_PRICING: dict[str, tuple[float, float]] = {
    CLAUDE_HAIKU_MODEL: (1.00, 5.00),
    CLAUDE_SONNET_MODEL: (3.00, 15.00),
}

_RETRYABLE_STATUS_CODES = {429, 500, 529}
_CODE_BLOCK_RE = re.compile(r"```(?:json)?\s*\n?(.*?)```", re.DOTALL)


class ClaudeClient:
    """Thin async wrapper around the Anthropic SDK with concurrency control."""

    def __init__(self, api_key: str, max_concurrent: int = 10) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0

    # ── Public API ────────────────────────────────────────────────────────────

    async def generate(
        self,
        rendered_prompt: str,
        agent_type: str,
        system_prompt: str = "",
    ) -> dict:
        """Send *rendered_prompt* to Claude and return parsed JSON response.

        Model selection: Sonnet for creative agent types, Haiku otherwise.
        Retries with exponential backoff on 429 / 500 / 529.
        """
        model = (
            CLAUDE_SONNET_MODEL
            if agent_type in SONNET_AGENT_TYPES
            else CLAUDE_HAIKU_MODEL
        )
        messages = [{"role": "user", "content": rendered_prompt}]

        async with self._semaphore:
            return await self._call_with_retries(model, messages, system_prompt)

    @property
    def estimated_cost_usd(self) -> float:
        """Estimate cumulative cost based on token counts."""
        cost = 0.0
        for model, (inp_price, out_price) in _PRICING.items():
            # We don't track per-model; use weighted average as approximation.
            # For a more precise estimate we'd need per-model counters.
            pass
        # Simplified: assume worst-case Sonnet pricing for safety.
        inp = self.total_input_tokens / 1_000_000 * 3.00
        out = self.total_output_tokens / 1_000_000 * 15.00
        cost = inp + out
        return cost

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _call_with_retries(
        self,
        model: str,
        messages: list[dict],
        system_prompt: str,
    ) -> dict:
        last_exc: Exception | None = None
        for attempt in range(1, CLAUDE_MAX_RETRIES + 1):
            try:
                kwargs: dict = {
                    "model": model,
                    "max_tokens": 2048,
                    "messages": messages,
                }
                if system_prompt:
                    kwargs["system"] = system_prompt

                resp = await self._client.messages.create(**kwargs)

                self.total_input_tokens += resp.usage.input_tokens
                self.total_output_tokens += resp.usage.output_tokens

                raw_text = resp.content[0].text
                return self._parse_json(raw_text)

            except anthropic.RateLimitError as exc:
                last_exc = exc
                wait = 2**attempt
                logger.warning("Rate-limited (attempt %d/%d), retrying in %ds", attempt, CLAUDE_MAX_RETRIES, wait)
                await asyncio.sleep(wait)

            except anthropic.APIStatusError as exc:
                if exc.status_code in _RETRYABLE_STATUS_CODES:
                    last_exc = exc
                    wait = 2**attempt
                    logger.warning("Server error %d (attempt %d/%d), retrying in %ds", exc.status_code, attempt, CLAUDE_MAX_RETRIES, wait)
                    await asyncio.sleep(wait)
                else:
                    raise

        raise RuntimeError(
            f"Claude API failed after {CLAUDE_MAX_RETRIES} retries"
        ) from last_exc

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract JSON from raw response text, handling markdown code blocks."""
        # Try to extract from ```json ... ``` block first.
        match = _CODE_BLOCK_RE.search(text)
        candidate = match.group(1).strip() if match else text.strip()
        return json.loads(candidate)
