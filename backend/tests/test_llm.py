"""Tests for LLM utility: JSON extraction, rate limiting, fallback."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.utils.llm import _extract_json, _find_balanced_braces, _fix_json


class TestExtractJson:
    def test_direct_json(self):
        result = _extract_json('{"action": "move", "target": "tavern"}')
        assert result == {"action": "move", "target": "tavern"}

    def test_codeblock_json(self):
        text = '```json\n{"action": "fight", "target": "goblin"}\n```'
        result = _extract_json(text)
        assert result == {"action": "fight", "target": "goblin"}

    def test_codeblock_no_lang(self):
        text = '```\n{"key": "value"}\n```'
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_json_in_text(self):
        text = 'Here is the response:\n{"action": "rest"}\nThat is my choice.'
        result = _extract_json(text)
        assert result == {"action": "rest"}

    def test_nested_json(self):
        text = '{"outer": {"inner": [1, 2, 3]}, "key": "val"}'
        result = _extract_json(text)
        assert result == {"outer": {"inner": [1, 2, 3]}, "key": "val"}

    def test_garbage_input(self):
        result = _extract_json("This is not JSON at all, just random text!")
        assert result.get("error") == "parse_failed"

    def test_empty_input(self):
        result = _extract_json("")
        assert result.get("error") == "parse_failed"

    def test_trailing_comma(self):
        text = '{"action": "move", "target": "forest",}'
        result = _extract_json(text)
        assert result["action"] == "move"

    def test_multiple_json_returns_first(self):
        text = '{"a": 1} some text {"b": 2}'
        result = _extract_json(text)
        assert result == {"a": 1}


class TestFixJson:
    def test_trailing_comma_object(self):
        assert '{"a": 1}' == _fix_json('{"a": 1,}')

    def test_trailing_comma_array(self):
        assert '{"a": [1, 2]}' == _fix_json('{"a": [1, 2,]}')

    def test_comments_removed(self):
        fixed = _fix_json('{"key": "val" // this is a comment\n}')
        assert "//" not in fixed


class TestFindBalancedBraces:
    def test_simple(self):
        assert _find_balanced_braces('{"a": 1}') == '{"a": 1}'

    def test_nested(self):
        text = 'prefix {"a": {"b": 1}} suffix'
        assert _find_balanced_braces(text) == '{"a": {"b": 1}}'

    def test_no_braces(self):
        assert _find_balanced_braces("no json here") is None

    def test_string_with_braces(self):
        text = '{"text": "hello {world}"}'
        assert _find_balanced_braces(text) == '{"text": "hello {world}"}'


class TestGenerateFallback:
    @pytest.mark.asyncio
    async def test_fallback_on_failure(self):
        """generate() returns fallback when all retries fail."""
        from app.utils.llm import generate

        with patch("app.utils.llm._get_client") as mock_client:
            client = MagicMock()
            client.post = AsyncMock(side_effect=Exception("connection refused"))
            mock_client.return_value = client

            # Reset semaphore for test
            import app.utils.llm as llm_mod
            llm_mod._semaphore = asyncio.Semaphore(5)

            result = await generate("test prompt", fallback="default_response")
            assert result == "default_response"

    @pytest.mark.asyncio
    async def test_generate_json_default(self):
        """generate_json() returns default dict when LLM unavailable."""
        from app.utils.llm import generate_json

        with patch("app.utils.llm.generate", new_callable=AsyncMock, return_value=""):
            result = await generate_json("test", default={"action": "rest"})
            assert result == {"action": "rest"}


class TestRateLimiting:
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """Semaphore prevents more than N concurrent LLM calls."""
        import app.utils.llm as llm_mod

        llm_mod._semaphore = asyncio.Semaphore(2)
        sem = llm_mod._get_semaphore()

        concurrent_count = 0
        max_concurrent = 0

        async def mock_generate(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent
            async with sem:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
                await asyncio.sleep(0.05)
                concurrent_count -= 1
            return ""

        tasks = [mock_generate() for _ in range(5)]
        await asyncio.gather(*tasks)
        assert max_concurrent <= 2
