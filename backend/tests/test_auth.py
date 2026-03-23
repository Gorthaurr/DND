"""Tests for JWT auth system."""

from app.auth.jwt import hash_password, verify_password, create_token, decode_token


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("secret123")
        assert verify_password("secret123", hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("secret123")
        assert not verify_password("wrong_password", hashed)

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # different salts

    def test_hash_format(self):
        hashed = hash_password("test")
        assert hashed.startswith("pbkdf2:sha256:")
        parts = hashed.split(":")
        assert len(parts) == 4

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed)
        assert not verify_password("notempty", hashed)

    def test_verify_malformed_hash_returns_false(self):
        """Line 29: wrong format → False."""
        assert not verify_password("test", "not:a:valid:hash:format:extra")
        assert not verify_password("test", "wrong:sha256:salt:dk")

    def test_verify_exception_returns_false(self):
        """Lines 34-35: Exception in verify → False."""
        assert not verify_password("test", None)  # type: ignore
        assert not verify_password("test", 123)   # type: ignore


class TestJWTTokens:
    def test_create_and_decode(self):
        token = create_token("user-123", "testuser")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["username"] == "testuser"

    def test_invalid_token_returns_none(self):
        assert decode_token("garbage.token.here") is None

    def test_empty_token_returns_none(self):
        assert decode_token("") is None

    def test_token_contains_exp(self):
        token = create_token("uid", "user")
        payload = decode_token(token)
        assert "exp" in payload
        assert "iat" in payload

    def test_expired_token(self):
        """Line 54: ExpiredSignatureError → None."""
        import jwt as pyjwt
        from datetime import datetime, timezone, timedelta
        from app.config import settings
        payload = {
            "sub": "uid",
            "username": "user",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        }
        token = pyjwt.encode(payload, settings.jwt_secret, algorithm="HS256")
        assert decode_token(token) is None
