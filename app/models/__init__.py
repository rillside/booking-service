from app.database import Base  # Импортируем оригинальный Base из database.py
from app.models.booking import Booking
from app.models.rooms import Room
from app.models.users import User

__all__ = ["Base", "User", "Room", "Booking"]
