import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import ADMIN_ROLE
from app.core.logger import logger
from app.crud.user import CRUDUser
from app.database import get_db
from app.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось валидировать учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        login: str | None = payload.get("sub")
        if login is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await CRUDUser.get_by_login(db, login=login)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != ADMIN_ROLE:
        logger.warning(
            f"Отказ в доступе: пользователь {current_user.login} "
            f"не является администратором"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Требуются права администратора",
        )
    return current_user
