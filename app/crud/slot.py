from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.slots import Slot


class CRUDSlot:
    @staticmethod
    async def get_by_id(db: AsyncSession, slot_id: int) -> Slot | None:
        result = await db.execute(select(Slot).where(Slot.id == slot_id))
        return result.scalars().first()
