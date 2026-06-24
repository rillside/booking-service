from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.core.security import create_access_token, verify_password
from app.crud.user import CRUDUser
from app.database import get_db
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await CRUDUser.get_by_login(db, user_in.login)
    if existing_user:
        logger.warning(f"Регистрация отклонена: логин {user_in.login} уже занят")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже зарегистрирован"
        )
    user = await CRUDUser.create(db, user_in)
    logger.info(f"Зарегистрирован новый пользователь: {user.login} (id={user.id})")
    return user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await CRUDUser.get_by_login(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа для логина {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": user.login, "role": user.role}
    access_token = create_access_token(data=token_data)
    logger.info(f"Пользователь {user.login} вошёл в систему")

    return {"access_token": access_token, "token_type": "bearer"}
