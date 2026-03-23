"""JWT token creation and verification."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-SHA256 (stdlib, no bcrypt dependency issues)."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"pbkdf2:sha256:{salt}:{dk.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against PBKDF2 hash."""
    try:
        parts = hashed.split(":")
        if len(parts) != 4 or parts[0] != "pbkdf2":
            return False
        salt = parts[2]
        stored_dk = parts[3]
        dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 100_000)
        return hmac.compare_digest(dk.hex(), stored_dk)
    except Exception:
        return False


def create_token(user_id: str, username: str) -> str:
    """Create a JWT token for a user."""
    payload = {
        "sub": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT token. Returns payload or None if invalid."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
