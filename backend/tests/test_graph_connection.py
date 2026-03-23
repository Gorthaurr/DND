"""Tests for app.graph.connection — get_driver / close_driver."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import app.graph.connection as conn_mod


@pytest.fixture(autouse=True)
def reset_driver():
    """Ensure _driver is reset before each test."""
    conn_mod._driver = None
    yield
    conn_mod._driver = None


def test_get_driver_creates_singleton():
    """get_driver should create an AsyncDriver and return it."""
    mock_driver = MagicMock()
    with patch("app.graph.connection.AsyncGraphDatabase") as mock_agd:
        mock_agd.driver.return_value = mock_driver
        driver = conn_mod.get_driver()

    assert driver is mock_driver
    mock_agd.driver.assert_called_once()


def test_get_driver_returns_same_instance():
    """Subsequent calls should return the same driver (singleton)."""
    mock_driver = MagicMock()
    with patch("app.graph.connection.AsyncGraphDatabase") as mock_agd:
        mock_agd.driver.return_value = mock_driver
        d1 = conn_mod.get_driver()
        d2 = conn_mod.get_driver()

    assert d1 is d2
    # Should only call driver() once
    assert mock_agd.driver.call_count == 1


@pytest.mark.asyncio
async def test_close_driver():
    """close_driver should call driver.close() and reset global."""
    mock_driver = MagicMock()
    mock_driver.close = AsyncMock()
    conn_mod._driver = mock_driver

    await conn_mod.close_driver()

    mock_driver.close.assert_awaited_once()
    assert conn_mod._driver is None


@pytest.mark.asyncio
async def test_close_driver_when_none():
    """close_driver with no driver should be a no-op."""
    conn_mod._driver = None
    await conn_mod.close_driver()
    assert conn_mod._driver is None
