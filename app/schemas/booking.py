from datetime import date

from pydantic import BaseModel, ConfigDict


class BookingBase(BaseModel):
    booking_date: date
    room_id: int
    slot_id: int


class BookingCreate(BookingBase):
    pass


class BookingResponse(BookingBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
