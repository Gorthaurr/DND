"""Multi-provider LLM integration with rate limiting, retries, batching, and fallback.

Public API (unchanged for all agents):
- generate(prompt, system, temperature, fallback) → str
- generate_json(prompt, system, temperature, default) → dict
- generate_batch(prompts) → list[str]
"""

from __future__ import annotations

import asyncio
import json
import re

from app.config import settings
from app.utils.logger import get_logger
from app.utils.llm_providers import LLMProvider, create_provider

log = get_logger("llm")

_provider: LLMProvider | None = None


def _get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = create_provider()
        log.info("llm_provider_created", provider=settings.llm_provider)
    return _provider


async def close_client() -> None:
    """Close the active LLM provider's HTTP client."""
    global _provider
    if _provider and hasattr(_provider, "close"):
        await _provider.close()
        _provider = None


async def is_llm_available() -> bool:
    """Check if the LLM provider is reachable."""
    provider = _get_provider()
    if hasattr(provider, "is_available"):
        return await provider.is_available()
    # For providers without health check, try a simple call
    try:
        result = await provider.generate("Say OK.", temperature=0.0)
        return bool(result)
    except Exception:
        return False


async def generate(
    prompt: str,
    system: str = "",
    temperature: float | None = None,
    fallback: str = "",
) -> str:
    """Generate text from the configured LLM provider."""
    provider = _get_provider()
    try:
        result = await provider.generate(prompt, system, temperature)
        return result or fallback
    except Exception as e:
        log.error("llm_generate_failed", error=str(e))
        return fallback


async def generate_json(
    prompt: str,
    system: str = "",
    temperature: float | None = None,
    default: dict | None = None,
) -> dict:
    """Generate and parse JSON response from LLM with fallback default."""
    raw = await generate(prompt, system, temperature, fallback="")
    if not raw:
        return default if default is not None else {"error": "llm_unavailable"}
    result = _extract_json(raw)
    if result.get("error") == "parse_failed" and default is not None:
        return default
    return result


async def generate_batch(
    prompts: list[dict],
    max_concurrent: int | None = None,
) -> list[str]:
    """Execute multiple LLM calls in parallel with rate limiting.

    Each dict: {"prompt": str, "system": str, "temperature": float | None}
    Returns list of responses in same order as prompts.
    """
    concurrency = max_concurrent or settings.llm_max_concurrent
    sem = asyncio.Semaphore(concurrency)

    async def _call(item: dict) -> str:
        async with sem:
            return await generate(
                prompt=item["prompt"],
                system=item.get("system", ""),
                temperature=item.get("temperature"),
                fallback=item.get("fallback", ""),
            )

    return await asyncio.gather(*[_call(p) for p in prompts])


# ── JSON extraction (unchanged) ────────────────────────────────

def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response with multiple fallback strategies."""
    text = text.strip()

    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: extract from markdown code block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: find first { ... } (greedy, handles nested)
    brace_match = _find_balanced_braces(text)
    if brace_match:
        try:
            return json.loads(brace_match)
        except json.JSONDecodeError:
            fixed = _fix_json(brace_match)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

    # Strategy 4: last resort — any { ... } with re.DOTALL
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            fixed = _fix_json(match.group(0))
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

    log.error("json_parse_failed", text_preview=text[:300])
    return {"error": "parse_failed"}


def _find_balanced_braces(text: str) -> str | None:
    """Find the first balanced { ... } block in text."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _fix_json(text: str) -> str:
    """Attempt to fix common JSON errors from LLMs."""
    text = re.sub(r",\s*([}\]])", r"\1", text)
    text = re.sub(r"(?<![\"\\])'([^']*)'(?![\"\\])", r'"\1"', text)
    text = re.sub(r"//[^\n]*", "", text)
    return text
