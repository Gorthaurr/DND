import json
import re

import httpx

from app.config import settings
from app.utils.logger import get_logger

log = get_logger("llm")

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=httpx.Timeout(120.0, connect=10.0),
        )
    return _client


async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


async def generate(prompt: str, system: str = "", temperature: float | None = None) -> str:
    """Generate text from Ollama. Returns raw string response."""
    client = _get_client()
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature or settings.ollama_temperature,
        },
    }
    if system:
        payload["system"] = system

    for attempt in range(3):
        try:
            resp = await client.post("/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            log.warning("llm_request_failed", attempt=attempt, error=str(e))
            if attempt == 2:
                raise

    return ""


async def generate_json(prompt: str, system: str = "", temperature: float | None = None) -> dict:
    """Generate and parse JSON response from LLM."""
    raw = await generate(prompt, system, temperature)
    return _extract_json(raw)


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Try direct parse
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from code block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding first { ... }
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    log.error("json_parse_failed", text=text[:200])
    return {}
