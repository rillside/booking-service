from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import EMPLOYEE_ROLE
from app.core.security import hash_password
from app.models.users import User
from app.schemas.user import UserCreate


class CRUDUser:
    @staticmethod
    async def get_by_login(db: AsyncSession, login: str) -> User | None:
        result = await db.execute(select(User).where(User.login == login))
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        db_user = User(
            login=user_in.login,
            hashed_password=hash_password(user_in.password),
            role=EMPLOYEE_ROLE,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
