"""Tests for graph schema module."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.graph.schema import CONSTRAINTS, INDEXES, ensure_schema


class TestSchemaConstants:
    def test_constraints_not_empty(self):
        assert len(CONSTRAINTS) > 0

    def test_indexes_not_empty(self):
        assert len(INDEXES) > 0

    def test_constraints_are_create_statements(self):
        for c in CONSTRAINTS:
            assert c.startswith("CREATE CONSTRAINT")

    def test_indexes_are_create_statements(self):
        for i in INDEXES:
            assert i.startswith("CREATE INDEX")


class TestEnsureSchema:
    @pytest.mark.asyncio
    async def test_ensure_schema_runs_all_statements(self):
        mock_session = AsyncMock()
        mock_session.run = AsyncMock()

        mock_driver = MagicMock()
        mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_driver.session.return_value.__aexit__ = AsyncMock(return_value=False)

        await ensure_schema(mock_driver)
        assert mock_session.run.call_count == len(CONSTRAINTS) + len(INDEXES)

    @pytest.mark.asyncio
    async def test_ensure_schema_tolerates_errors(self):
        mock_session = AsyncMock()
        mock_session.run = AsyncMock(side_effect=Exception("already exists"))

        mock_driver = MagicMock()
        mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_driver.session.return_value.__aexit__ = AsyncMock(return_value=False)

        # Should not raise
        await ensure_schema(mock_driver)
