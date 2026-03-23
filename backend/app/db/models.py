"""PostgreSQL models for users, rooms, and world snapshots."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    owned_rooms = relationship("Room", back_populates="owner", lazy="selectin")
    memberships = relationship("RoomMember", back_populates="user", lazy="selectin")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    world_id = Column(String(20), unique=True, nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    max_players = Column(Integer, default=6)
    status = Column(String(20), default="active")  # active | paused | archived
    world_config = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="owned_rooms")
    members = relationship("RoomMember", back_populates="room", lazy="selectin",
                           cascade="all, delete-orphan")
    snapshots = relationship("WorldSnapshot", back_populates="room", lazy="noload",
                             cascade="all, delete-orphan")


class RoomMember(Base):
    __tablename__ = "room_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    player_id = Column(String(50), nullable=False)  # ID in Neo4j graph
    character_name = Column(String(100), default="Adventurer")
    role = Column(String(20), default="player")  # player | dm | spectator
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    room = relationship("Room", back_populates="members")
    user = relationship("User", back_populates="memberships")


class WorldSnapshot(Base):
    __tablename__ = "world_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    day = Column(Integer, nullable=False)
    snapshot_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    room = relationship("Room", back_populates="snapshots")
