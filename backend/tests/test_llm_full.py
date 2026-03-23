"""Tests for app.utils.llm — Multi-provider LLM integration."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Helpers ──────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_provider():
    """Reset the global _provider between tests."""
    import app.utils.llm as llm_mod
    llm_mod._provider = None
    yield
    llm_mod._provider = None


def _mock_provider(response: str = "Hello"):
    """Create a mock LLMProvider."""
    p = MagicMock()
    p.generate = AsyncMock(return_value=response)
    p.close = AsyncMock()
    p.is_available = AsyncMock(return_value=True)
    return p


# ── _get_provider ────────────────────────────────────────────────────────

def test_get_provider_creates_once():
    with patch("app.utils.llm.create_provider") as mock_create:
        mock_create.return_value = _mock_provider()
        from app.utils.llm import _get_provider
        p1 = _get_provider()
        p2 = _get_provider()
    assert p1 is p2
    mock_create.assert_called_once()


# ── generate ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_success():
    mock_p = _mock_provider("The sky is blue.")
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate
        result = await generate("What color is the sky?", system="Be helpful.")
    assert result == "The sky is blue."
    mock_p.generate.assert_awaited_once_with("What color is the sky?", "Be helpful.", None)


@pytest.mark.asyncio
async def test_generate_with_temperature():
    mock_p = _mock_provider("response")
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate
        result = await generate("test", temperature=0.5)
    mock_p.generate.assert_awaited_once_with("test", "", 0.5)


@pytest.mark.asyncio
async def test_generate_returns_fallback_on_empty():
    mock_p = _mock_provider("")
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate
        result = await generate("test", fallback="default answer")
    assert result == "default answer"


@pytest.mark.asyncio
async def test_generate_returns_fallback_on_exception():
    mock_p = _mock_provider()
    mock_p.generate = AsyncMock(side_effect=RuntimeError("API down"))
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate
        result = await generate("test", fallback="fallback")
    assert result == "fallback"


@pytest.mark.asyncio
async def test_generate_returns_empty_string_no_fallback():
    mock_p = _mock_provider()
    mock_p.generate = AsyncMock(side_effect=RuntimeError("fail"))
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate
        result = await generate("test")
    assert result == ""


# ── generate_json ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_json_valid():
    mock_p = _mock_provider('{"name": "Goran", "mood": "angry"}')
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate_json
        result = await generate_json("Give me JSON.")
    assert result["name"] == "Goran"
    assert result["mood"] == "angry"


@pytest.mark.asyncio
async def test_generate_json_from_code_block():
    raw = '```json\n{"key": "value"}\n```'
    mock_p = _mock_provider(raw)
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate_json
        result = await generate_json("test")
    assert result["key"] == "value"


@pytest.mark.asyncio
async def test_generate_json_returns_default_on_empty():
    mock_p = _mock_provider("")
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate_json
        result = await generate_json("test", default={"fallback": True})
    assert result == {"fallback": True}


@pytest.mark.asyncio
async def test_generate_json_returns_error_dict_on_empty_no_default():
    mock_p = _mock_provider("")
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate_json
        result = await generate_json("test")
    assert result == {"error": "llm_unavailable"}


@pytest.mark.asyncio
async def test_generate_json_returns_default_on_parse_failure():
    mock_p = _mock_provider("not json at all")
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate_json
        result = await generate_json("test", default={"ok": False})
    assert result == {"ok": False}


# ── generate_batch ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_batch():
    call_count = 0

    async def fake_generate(prompt, system="", temperature=None):
        nonlocal call_count
        call_count += 1
        return f"response-{call_count}"

    mock_p = _mock_provider()
    mock_p.generate = fake_generate
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate_batch
        prompts = [
            {"prompt": "Q1", "system": "S1"},
            {"prompt": "Q2"},
            {"prompt": "Q3", "temperature": 0.5},
        ]
        results = await generate_batch(prompts, max_concurrent=2)
    assert len(results) == 3
    assert all(r.startswith("response-") for r in results)


@pytest.mark.asyncio
async def test_generate_batch_empty():
    mock_p = _mock_provider()
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import generate_batch
        results = await generate_batch([])
    assert results == []


# ── is_llm_available ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_is_llm_available_true():
    mock_p = _mock_provider()
    mock_p.is_available = AsyncMock(return_value=True)
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import is_llm_available
        assert await is_llm_available() is True


@pytest.mark.asyncio
async def test_is_llm_available_false():
    mock_p = _mock_provider()
    mock_p.is_available = AsyncMock(return_value=False)
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import is_llm_available
        assert await is_llm_available() is False


@pytest.mark.asyncio
async def test_is_llm_available_fallback_generate():
    """Provider without is_available method falls back to test generate call."""
    mock_p = MagicMock(spec=[])  # no is_available
    mock_p.generate = AsyncMock(return_value="OK")
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import is_llm_available
        assert await is_llm_available() is True


@pytest.mark.asyncio
async def test_is_llm_available_fallback_exception():
    mock_p = MagicMock(spec=[])
    mock_p.generate = AsyncMock(side_effect=ConnectionError("down"))
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        from app.utils.llm import is_llm_available
        assert await is_llm_available() is False


# ── close_client ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_close_client():
    mock_p = _mock_provider()
    with patch("app.utils.llm.create_provider", return_value=mock_p):
        import app.utils.llm as llm_mod
        llm_mod._provider = mock_p
        await llm_mod.close_client()
    mock_p.close.assert_awaited_once()
    assert llm_mod._provider is None


@pytest.mark.asyncio
async def test_close_client_no_provider():
    import app.utils.llm as llm_mod
    llm_mod._provider = None
    await llm_mod.close_client()  # should not raise


# ── _extract_json ────────────────────────────────────────────────────────

def test_extract_json_direct():
    from app.utils.llm import _extract_json
    assert _extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_code_block():
    from app.utils.llm import _extract_json
    text = 'Here is the JSON:\n```json\n{"b": 2}\n```\nDone.'
    assert _extract_json(text) == {"b": 2}


def test_extract_json_embedded_braces():
    from app.utils.llm import _extract_json
    text = 'Some text {"c": 3} more text'
    assert _extract_json(text) == {"c": 3}


def test_extract_json_trailing_comma_fix():
    from app.utils.llm import _extract_json
    text = '{"items": ["a", "b",]}'
    result = _extract_json(text)
    assert result.get("items") == ["a", "b"]


def test_extract_json_parse_failed():
    from app.utils.llm import _extract_json
    result = _extract_json("no json here at all")
    assert result == {"error": "parse_failed"}


# ── _find_balanced_braces ────────────────────────────────────────────────

def test_find_balanced_braces():
    from app.utils.llm import _find_balanced_braces
    assert _find_balanced_braces('pre {"a": {"b": 1}} post') == '{"a": {"b": 1}}'
    assert _find_balanced_braces("no braces") is None


# ── _fix_json ────────────────────────────────────────────────────────────

def test_fix_json_trailing_comma():
    from app.utils.llm import _fix_json
    fixed = _fix_json('{"a": 1,}')
    assert fixed == '{"a": 1}'


def test_fix_json_single_quotes():
    from app.utils.llm import _fix_json
    fixed = _fix_json("{'a': 'b'}")
    assert '"a"' in fixed and '"b"' in fixed


def test_fix_json_comments():
    from app.utils.llm import _fix_json
    fixed = _fix_json('{"a": 1} // comment')
    assert "//" not in fixed
