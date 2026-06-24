from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ADMIN_ROLE
from app.core.logger import logger
from app.crud.booking import CRUDBooking, SlotAlreadyBookedError
from app.crud.room import CRUDRoom
from app.crud.slot import CRUDSlot
from app.database import get_db
from app.models.users import User
from app.routers.deps import get_current_user
from app.schemas.booking import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])

SLOT_TAKEN_DETAIL = (
    "Этот временной слот в выбранной комнате уже забронирован на указанную дату"
)


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not await CRUDRoom.get_by_id(db, booking_in.room_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комната с ID {booking_in.room_id} не найдена",
        )

    if not await CRUDSlot.get_by_id(db, booking_in.slot_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Временной слот с ID {booking_in.slot_id} не найден",
        )

    occupied = await CRUDBooking.check_slot_occupied(
        db,
        room_id=booking_in.room_id,
        slot_id=booking_in.slot_id,
        booking_date=booking_in.booking_date,
    )
    if occupied:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=SLOT_TAKEN_DETAIL
        )

    try:
        booking = await CRUDBooking.create(db, booking_in, current_user.id)
    except SlotAlreadyBookedError:
        logger.warning(
            f"Конфликт бронирования: комната {booking_in.room_id}, "
            f"слот {booking_in.slot_id}, дата {booking_in.booking_date} уже заняты"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=SLOT_TAKEN_DETAIL
        )

    logger.info(
        f"Создано бронирование id={booking.id} пользователем {current_user.login} "
        f"(комната {booking.room_id}, слот {booking.slot_id}, "
        f"дата {booking.booking_date})"
    )
    return booking


@router.get("/", response_model=list[BookingResponse])
async def get_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == ADMIN_ROLE:
        return await CRUDBooking.get_all(db)
    return await CRUDBooking.get_by_user_id(db, user_id=current_user.id)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = await CRUDBooking.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено"
        )

    # Сотрудник может отменять только свои брони, администратор — любые.
    if current_user.role != ADMIN_ROLE and booking.user_id != current_user.id:
        logger.warning(
            f"Отказ в отмене брони id={booking_id}: "
            f"пользователь {current_user.login} не владелец"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Вы можете отменять только свои бронирования",
        )

    await db.delete(booking)
    await db.commit()
    logger.info(
        f"Отменено бронирование id={booking_id} пользователем {current_user.login}"
    )
