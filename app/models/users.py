from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import EMPLOYEE_ROLE
from app.database import Base

if TYPE_CHECKING:
    from app.models.bookings import Booking


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    login: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default=EMPLOYEE_ROLE, nullable=False
    )

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
