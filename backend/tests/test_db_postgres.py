"""Tests for PostgreSQL connection module."""

from unittest.mock import patch, MagicMock

from app.db.postgres import get_engine, get_session_factory, close_db


class TestGetEngine:
    def test_get_engine_returns_engine(self):
        import app.db.postgres as mod
        mod._engine = None
        with patch("app.db.postgres.create_async_engine") as mock_create:
            mock_create.return_value = MagicMock()
            engine = get_engine()
            assert engine is not None
            mock_create.assert_called_once()
        mod._engine = None  # cleanup

    def test_get_engine_singleton(self):
        import app.db.postgres as mod
        mod._engine = None
        with patch("app.db.postgres.create_async_engine") as mock_create:
            mock_create.return_value = MagicMock()
            e1 = get_engine()
            e2 = get_engine()
            assert e1 is e2
            mock_create.assert_called_once()
        mod._engine = None


class TestGetSessionFactory:
    def test_returns_sessionmaker(self):
        with patch("app.db.postgres.get_engine", return_value=MagicMock()):
            factory = get_session_factory()
            assert factory is not None


class TestCloseDb:
    @staticmethod
    async def _run_close():
        import app.db.postgres as mod
        mock_engine = MagicMock()
        mock_engine.dispose = MagicMock(return_value=MagicMock(__await__=lambda self: iter([None])))
        mod._engine = mock_engine
        await close_db()
        assert mod._engine is None
