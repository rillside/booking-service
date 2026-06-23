from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Чтобы не ловить ошибки от линтера
if TYPE_CHECKING:
    from app.models.rooms import Room
    from app.models.users import User


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id",
                                         ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",
                                         ondelete="CASCADE"))
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="bookings", lazy="joined"
        )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="bookings", lazy="joined"
        )

    __table_args__ = (
        CheckConstraint(
            "end_time > start_time",
            name="check_booking_time_order"
        ),
    )
