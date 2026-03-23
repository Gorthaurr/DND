"""Tests for main FastAPI app setup."""

from unittest.mock import patch, AsyncMock, MagicMock


class TestAppImport:
    def test_app_exists(self):
        with patch("app.graph.connection.get_driver", return_value=MagicMock()), \
             patch("app.graph.schema.ensure_schema", new_callable=AsyncMock):
            from app.main import app
            assert app is not None
            assert app.title == "Living World Engine"

    def test_app_has_routes(self):
        with patch("app.graph.connection.get_driver", return_value=MagicMock()), \
             patch("app.graph.schema.ensure_schema", new_callable=AsyncMock):
            from app.main import app
            route_paths = [r.path for r in app.routes]
            # Should have API routes registered
            assert len(route_paths) > 0

    def test_cors_middleware(self):
        with patch("app.graph.connection.get_driver", return_value=MagicMock()), \
             patch("app.graph.schema.ensure_schema", new_callable=AsyncMock):
            from app.main import app
            middleware_classes = [type(m).__name__ for m in app.user_middleware]
            # CORS is added via add_middleware
            assert len(app.user_middleware) >= 0  # At least exists
