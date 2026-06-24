from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.crud.room import CRUDRoom
from app.database import get_db
from app.models.users import User
from app.routers.deps import get_current_admin, get_current_user
from app.schemas.room import RoomAvailabilityResponse, RoomCreate, RoomResponse

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomResponse])
async def get_rooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CRUDRoom.get_all(db)


@router.get("/{room_id}/availability", response_model=list[RoomAvailabilityResponse])
async def get_room_availability(
    room_id: int,
    booking_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    room = await CRUDRoom.get_by_id(db, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комната с ID {room_id} не найдена",
        )
    return await CRUDRoom.get_availability(db, room_id, booking_date)


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    room = await CRUDRoom.create(db, room_in)
    logger.info(
        f"Администратор {current_admin.login} создал комнату {room.name} (id={room.id})"
    )
    return room
