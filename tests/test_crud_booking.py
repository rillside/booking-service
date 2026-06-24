from datetime import date

import pytest

from app.crud.booking import CRUDBooking, SlotAlreadyBookedError
from app.schemas.booking import BookingCreate

BOOKING_DATE = date(2026, 7, 1)


def _payload(room, slot, day=BOOKING_DATE) -> BookingCreate:
    return BookingCreate(room_id=room.id, slot_id=slot.id, booking_date=day)


async def test_create_booking(db_session, room, slots, employee):
    booking = await CRUDBooking.create(
        db_session, _payload(room, slots[0]), employee["id"]
    )
    assert booking.id is not None
    assert booking.user_id == employee["id"]
    assert booking.room_id == room.id


async def test_check_slot_occupied_toggles(db_session, room, slots, employee):
    assert not await CRUDBooking.check_slot_occupied(
        db_session, room.id, slots[0].id, BOOKING_DATE
    )
    await CRUDBooking.create(db_session, _payload(room, slots[0]), employee["id"])
    assert await CRUDBooking.check_slot_occupied(
        db_session, room.id, slots[0].id, BOOKING_DATE
    )


async def test_duplicate_booking_raises(db_session, room, slots, employee):
    await CRUDBooking.create(db_session, _payload(room, slots[0]), employee["id"])
    # Гонка: повторная вставка того же слота ловится уникальным ограничением.
    with pytest.raises(SlotAlreadyBookedError):
        await CRUDBooking.create(db_session, _payload(room, slots[0]), employee["id"])


async def test_get_by_id(db_session, room, slots, employee):
    created = await CRUDBooking.create(
        db_session, _payload(room, slots[0]), employee["id"]
    )
    assert (await CRUDBooking.get_by_id(db_session, created.id)).id == created.id
    assert await CRUDBooking.get_by_id(db_session, 999999) is None


async def test_get_by_user_id_isolated(db_session, room, slots, employee, employee2):
    await CRUDBooking.create(db_session, _payload(room, slots[0]), employee["id"])
    await CRUDBooking.create(db_session, _payload(room, slots[1]), employee2["id"])

    own = await CRUDBooking.get_by_user_id(db_session, employee["id"])
    assert len(own) == 1
    assert own[0].user_id == employee["id"]


async def test_get_all_bookings(db_session, room, slots, employee, employee2):
    await CRUDBooking.create(db_session, _payload(room, slots[0]), employee["id"])
    await CRUDBooking.create(db_session, _payload(room, slots[1]), employee2["id"])
    assert len(await CRUDBooking.get_all(db_session)) == 2
