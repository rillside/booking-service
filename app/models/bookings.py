from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.rooms import Room
    from app.models.users import User


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    slot_id: Mapped[int] = mapped_column(
        ForeignKey("slots.id", ondelete="CASCADE")
    )
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="bookings", lazy="joined"
    )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="bookings", lazy="joined"
    )

    # Один слот в комнате на дату нельзя забронировать дважды.
    __table_args__ = (
        UniqueConstraint(
            "room_id", "slot_id", "booking_date", name="uq_room_slot_date"
        ),
    )
