from datetime import date

from app.crud.booking import CRUDBooking
from app.crud.room import CRUDRoom
from app.schemas.booking import BookingCreate
from app.schemas.room import RoomCreate

BOOKING_DATE = date(2026, 7, 1)


async def test_create_and_get_room(db_session):
    created = await CRUDRoom.create(db_session, RoomCreate(name="Room 1"))
    assert created.id is not None
    fetched = await CRUDRoom.get_by_id(db_session, created.id)
    assert fetched.name == "Room 1"


async def test_get_by_id_missing(db_session):
    assert await CRUDRoom.get_by_id(db_session, 12345) is None


async def test_get_all_rooms(db_session):
    await CRUDRoom.create(db_session, RoomCreate(name="Room A"))
    await CRUDRoom.create(db_session, RoomCreate(name="Room B"))
    rooms = await CRUDRoom.get_all(db_session)
    assert len(rooms) == 2


async def test_availability_all_free_without_bookings(db_session, room, slots):
    availability = await CRUDRoom.get_availability(db_session, room.id, BOOKING_DATE)
    assert len(availability) == len(slots)
    assert all(item["is_free"] for item in availability)


async def test_availability_marks_booked_slot(db_session, room, slots, employee):
    booked = slots[0]
    await CRUDBooking.create(
        db_session,
        BookingCreate(room_id=room.id, slot_id=booked.id, booking_date=BOOKING_DATE),
        employee["id"],
    )
    availability = await CRUDRoom.get_availability(db_session, room.id, BOOKING_DATE)
    by_slot = {item["slot_id"]: item["is_free"] for item in availability}
    assert by_slot[booked.id] is False
    assert by_slot[slots[1].id] is True


async def test_availability_is_date_specific(db_session, room, slots, employee):
    await CRUDBooking.create(
        db_session,
        BookingCreate(room_id=room.id, slot_id=slots[0].id, booking_date=BOOKING_DATE),
        employee["id"],
    )
    other_day = await CRUDRoom.get_availability(db_session, room.id, date(2026, 7, 2))
    assert all(item["is_free"] for item in other_day)
