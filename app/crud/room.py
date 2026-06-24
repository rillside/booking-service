from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookings import Booking
from app.models.rooms import Room
from app.models.slots import Slot
from app.schemas.room import RoomCreate


class CRUDRoom:
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Room]:
        result = await db.execute(select(Room))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, room_id: int) -> Room | None:
        result = await db.execute(select(Room).where(Room.id == room_id))
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, room_in: RoomCreate) -> Room:
        db_room = Room(**room_in.model_dump())
        db.add(db_room)
        await db.commit()
        await db.refresh(db_room)
        return db_room

    @staticmethod
    async def get_availability(
        db: AsyncSession, room_id: int, booking_date: date
    ) -> list[dict]:
        """Сетка занятости слотов для комнаты на конкретную дату."""
        slots_result = await db.execute(select(Slot))
        all_slots = slots_result.scalars().all()

        bookings_result = await db.execute(
            select(Booking).where(
                Booking.room_id == room_id,
                Booking.booking_date == booking_date,
            )
        )
        occupied_slot_ids = {b.slot_id for b in bookings_result.scalars().all()}

        return [
            {
                "slot_id": slot.id,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "is_free": slot.id not in occupied_slot_ids,
            }
            for slot in all_slots
        ]
