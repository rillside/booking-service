from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import ADMIN_ROLE
from app.core.logger import logger
from app.crud.user import CRUDUser
from app.models.slots import Slot
from app.models.users import User

DEFAULT_SLOTS = [
    (time(9, 0), time(11, 0)),
    (time(11, 0), time(13, 0)),
    (time(13, 0), time(16, 0)),
    (time(16, 0), time(19, 0)),
]


async def create_initial_slots(db: AsyncSession):
    result = await db.execute(select(Slot))
    if result.scalars().first():
        return

    logger.info("Таблица слотов пуста. Генерирую дефолтные слоты...")
    db.add_all(
        Slot(start_time=start, end_time=end) for start, end in DEFAULT_SLOTS
    )
    await db.commit()
    logger.info("Дефолтные слоты успешно созданы.")


async def create_initial_admin(db: AsyncSession):
    admin = await CRUDUser.get_by_login(db, settings.ADMIN_LOGIN)
    if admin:
        return

    logger.info(f"Администратор {settings.ADMIN_LOGIN} не найден. Создаю...")
    # ADMIN_HASHED_PASSWORD хранит готовый bcrypt-хеш, повторно не хешируем.
    db.add(
        User(
            login=settings.ADMIN_LOGIN,
            hashed_password=settings.ADMIN_HASHED_PASSWORD,
            role=ADMIN_ROLE,
        )
    )
    await db.commit()
    logger.info("Администратор успешно создан.")
