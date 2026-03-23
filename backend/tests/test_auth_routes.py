"""Tests for auth routes — register, login, me schemas."""

from app.auth.jwt import create_token, hash_password, verify_password


class TestAuthRouteSchemas:
    """Test the Pydantic models used in auth routes."""

    def test_register_request_schema(self):
        from app.auth.routes import RegisterRequest
        req = RegisterRequest(email="test@test.com", username="user1", password="secret")
        assert req.email == "test@test.com"
        assert req.username == "user1"

    def test_login_request_schema(self):
        from app.auth.routes import LoginRequest
        req = LoginRequest(email="test@test.com", password="secret")
        assert req.email == "test@test.com"

    def test_auth_response_schema(self):
        from app.auth.routes import AuthResponse
        resp = AuthResponse(token="tok123", user_id="u1", username="user1")
        assert resp.token == "tok123"

    def test_user_response_schema(self):
        from app.auth.routes import UserResponse
        resp = UserResponse(id="u1", email="a@b.com", username="user1", created_at="2025-01-01")
        assert resp.username == "user1"


class TestAuthDependencies:
    def test_dependency_importable(self):
        from app.auth.dependencies import get_current_user, get_room_member
        assert callable(get_current_user)
        assert callable(get_room_member)
