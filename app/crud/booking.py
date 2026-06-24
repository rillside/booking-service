from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookings import Booking
from app.schemas.booking import BookingCreate


class SlotAlreadyBookedError(Exception):
    """Слот уже занят (нарушение uq_room_slot_date при конкурентной записи)."""


class CRUDBooking:
    @staticmethod
    async def get_by_id(db: AsyncSession, booking_id: int) -> Booking | None:
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Booking]:
        """Все бронирования (для администратора)."""
        result = await db.execute(select(Booking))
        return result.scalars().all()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> list[Booking]:
        """Бронирования конкретного пользователя (для сотрудника)."""
        result = await db.execute(select(Booking).where(Booking.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def check_slot_occupied(
        db: AsyncSession, room_id: int, slot_id: int, booking_date: date
    ) -> bool:
        query = select(Booking).where(
            and_(
                Booking.room_id == room_id,
                Booking.slot_id == slot_id,
                Booking.booking_date == booking_date,
            )
        )
        result = await db.execute(query)
        return result.scalars().first() is not None

    @staticmethod
    async def create(
        db: AsyncSession, booking_in: BookingCreate, user_id: int
    ) -> Booking:
        db_booking = Booking(
            user_id=user_id,
            room_id=booking_in.room_id,
            slot_id=booking_in.slot_id,
            booking_date=booking_in.booking_date,
        )
        db.add(db_booking)
        try:
            await db.commit()
        except IntegrityError as exc:
            # Параллельный запрос успел занять тот же слот после check_slot_occupied —
            # уникальное ограничение БД ловит гонку.
            await db.rollback()
            raise SlotAlreadyBookedError from exc

        await db.refresh(db_booking)
        return db_booking
