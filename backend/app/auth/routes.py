"""Authentication endpoints: register, login, me."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_token, hash_password, verify_password
from app.db.models import User
from app.db.postgres import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    username: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    created_at: str


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check existing
    existing = await db.execute(
        select(User).where((User.email == req.email) | (User.username == req.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already taken")

    user = User(
        email=req.email,
        username=req.username,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    await db.flush()

    token = create_token(str(user.id), user.username)
    return AuthResponse(token=token, user_id=str(user.id), username=user.username)


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.last_login = datetime.now(timezone.utc)
    token = create_token(str(user.id), user.username)
    return AuthResponse(token=token, user_id=str(user.id), username=user.username)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        created_at=user.created_at.isoformat(),
    )
