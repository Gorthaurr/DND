"""Room CRUD API — create, join, leave, list rooms."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.models import Room, RoomMember, User
from app.db.postgres import get_db

router = APIRouter(prefix="/rooms", tags=["rooms"])


class CreateRoomRequest(BaseModel):
    name: str
    world_name: str = "medieval_village"
    max_players: int = 6


class JoinRoomRequest(BaseModel):
    character_name: str = "Adventurer"


class RoomResponse(BaseModel):
    id: str
    name: str
    world_id: str
    owner: str
    status: str
    max_players: int
    member_count: int
    members: list[dict]


class RoomListItem(BaseModel):
    id: str
    name: str
    status: str
    member_count: int
    owner: str


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    req: CreateRoomRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new game room with its own world instance."""
    world_id = uuid.uuid4().hex[:12]

    room = Room(
        name=req.name,
        world_id=world_id,
        owner_id=user.id,
        max_players=req.max_players,
        world_config={"world_name": req.world_name},
    )
    db.add(room)
    await db.flush()

    # Owner auto-joins as DM
    player_id = f"player-{str(user.id)[:8]}"
    member = RoomMember(
        room_id=room.id,
        user_id=user.id,
        player_id=player_id,
        character_name="Dungeon Master",
        role="dm",
    )
    db.add(member)
    await db.flush()

    return RoomResponse(
        id=str(room.id),
        name=room.name,
        world_id=room.world_id,
        owner=user.username,
        status=room.status,
        max_players=room.max_players,
        member_count=1,
        members=[{"username": user.username, "role": "dm", "character_name": "Dungeon Master"}],
    )


@router.get("", response_model=list[RoomListItem])
async def list_rooms(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List rooms the user is a member of."""
    result = await db.execute(
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == user.id)
        .where(Room.status != "archived")
    )
    rooms = result.scalars().all()
    items = []
    for room in rooms:
        items.append(RoomListItem(
            id=str(room.id),
            name=room.name,
            status=room.status,
            member_count=len(room.members),
            owner=room.owner.username if room.owner else "unknown",
        ))
    return items


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get room details."""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    members = [
        {"username": m.user.username, "role": m.role, "character_name": m.character_name}
        for m in room.members
    ]

    return RoomResponse(
        id=str(room.id),
        name=room.name,
        world_id=room.world_id,
        owner=room.owner.username,
        status=room.status,
        max_players=room.max_players,
        member_count=len(members),
        members=members,
    )


@router.post("/{room_id}/join")
async def join_room(
    room_id: str,
    req: JoinRoomRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Join an existing room."""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status != "active":
        raise HTTPException(status_code=400, detail="Room is not active")
    if len(room.members) >= room.max_players:
        raise HTTPException(status_code=400, detail="Room is full")

    # Check not already a member
    existing = await db.execute(
        select(RoomMember).where(RoomMember.room_id == room.id, RoomMember.user_id == user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already a member")

    player_id = f"player-{str(user.id)[:8]}"
    member = RoomMember(
        room_id=room.id,
        user_id=user.id,
        player_id=player_id,
        character_name=req.character_name,
        role="player",
    )
    db.add(member)

    return {"status": "joined", "player_id": player_id, "room": room.name}


@router.post("/{room_id}/leave")
async def leave_room(
    room_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Leave a room."""
    result = await db.execute(
        select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == user.id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Not a member")

    await db.delete(member)
    return {"status": "left"}


@router.delete("/{room_id}")
async def delete_room(
    room_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a room (owner only)."""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the room owner can delete it")

    room.status = "archived"
    return {"status": "archived"}
