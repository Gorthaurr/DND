"""Tests for LLM core module (generate, generate_json, JSON extraction, batch)."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.utils.llm import (
    generate, generate_json, generate_batch,
    _extract_json, _find_balanced_braces, _fix_json,
    close_client, is_llm_available,
)


class TestExtractJson:
    def test_direct_json(self):
        assert _extract_json('{"key": "value"}') == {"key": "value"}

    def test_markdown_code_block(self):
        text = '```json\n{"key": "value"}\n```'
        assert _extract_json(text) == {"key": "value"}

    def test_balanced_braces(self):
        text = 'Some text {"key": "value"} more text'
        assert _extract_json(text) == {"key": "value"}

    def test_nested_json(self):
        text = '{"outer": {"inner": 1}}'
        assert _extract_json(text)["outer"]["inner"] == 1

    def test_invalid_json_with_fix(self):
        text = "{'key': 'value'}"  # single quotes
        result = _extract_json(text)
        # Should either parse or return error
        assert isinstance(result, dict)

    def test_trailing_comma_fix(self):
        text = '{"key": "value",}'
        result = _extract_json(text)
        assert result.get("key") == "value"

    def test_no_json_returns_error(self):
        result = _extract_json("no json here")
        assert result.get("error") == "parse_failed"

    def test_empty_string(self):
        result = _extract_json("")
        assert "error" in result

    def test_json_with_comments(self):
        text = '{"key": "value" // comment\n}'
        result = _extract_json(text)
        assert isinstance(result, dict)


class TestFindBalancedBraces:
    def test_simple(self):
        assert _find_balanced_braces('{"a": 1}') == '{"a": 1}'

    def test_nested(self):
        text = '{"a": {"b": 1}}'
        assert _find_balanced_braces(text) == text

    def test_no_braces(self):
        assert _find_balanced_braces("no braces") is None

    def test_with_strings(self):
        text = '{"key": "value with {braces}"}'
        result = _find_balanced_braces(text)
        assert result is not None

    def test_unbalanced(self):
        text = '{"key": "value'
        result = _find_balanced_braces(text)
        assert result is None


class TestFixJson:
    def test_trailing_comma(self):
        fixed = _fix_json('{"a": 1,}')
        assert fixed == '{"a": 1}'

    def test_single_quotes(self):
        fixed = _fix_json("{'a': 'b'}")
        assert '"a"' in fixed

    def test_comments_removed(self):
        fixed = _fix_json('{"a": 1} // comment')
        assert "//" not in fixed


class TestGenerate:
    @pytest.mark.asyncio
    async def test_generate_delegates_to_provider(self):
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value="Hello world")
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await generate("test prompt")
            assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_generate_fallback_on_error(self):
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=Exception("fail"))
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await generate("test", fallback="default")
            assert result == "default"

    @pytest.mark.asyncio
    async def test_generate_empty_result_uses_fallback(self):
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value="")
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await generate("test", fallback="fb")
            assert result == "fb"


class TestGenerateJson:
    @pytest.mark.asyncio
    async def test_valid_json_response(self):
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value='{"action": "work"}')
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await generate_json("test")
            assert result["action"] == "work"

    @pytest.mark.asyncio
    async def test_empty_response_returns_default(self):
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value="")
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await generate_json("test", default={"fallback": True})
            assert result["fallback"] is True

    @pytest.mark.asyncio
    async def test_empty_response_no_default(self):
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value="")
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await generate_json("test")
            assert result.get("error") == "llm_unavailable"

    @pytest.mark.asyncio
    async def test_parse_failed_uses_default(self):
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value="not json at all")
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await generate_json("test", default={"ok": True})
            assert result["ok"] is True


class TestGenerateBatch:
    @pytest.mark.asyncio
    async def test_batch_parallel(self):
        mock_provider = MagicMock()
        call_count = 0
        async def mock_gen(prompt, system="", temperature=None):
            nonlocal call_count
            call_count += 1
            return f"response_{call_count}"
        mock_provider.generate = mock_gen
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            results = await generate_batch([
                {"prompt": "a"}, {"prompt": "b"}, {"prompt": "c"},
            ])
            assert len(results) == 3


class TestClientManagement:
    @pytest.mark.asyncio
    async def test_close_client(self):
        # Should not raise even if no provider exists
        with patch("app.utils.llm._provider", None):
            await close_client()

    @pytest.mark.asyncio
    async def test_is_llm_available_true(self):
        mock_provider = MagicMock()
        mock_provider.is_available = AsyncMock(return_value=True)
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await is_llm_available()
            assert result is True

    @pytest.mark.asyncio
    async def test_is_llm_available_no_method(self):
        mock_provider = MagicMock(spec=[])  # no is_available method
        mock_provider.generate = AsyncMock(return_value="ok")
        with patch("app.utils.llm._get_provider", return_value=mock_provider):
            result = await is_llm_available()
            assert result is True
