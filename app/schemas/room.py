from datetime import time

from pydantic import BaseModel, ConfigDict


class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomAvailabilityResponse(BaseModel):
    slot_id: int
    start_time: time
    end_time: time
    is_free: bool
