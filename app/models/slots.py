from datetime import time

from sqlalchemy import Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
