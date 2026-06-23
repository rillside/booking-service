from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, get_db
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте приложения создаем все таблицы, если их еще нет в БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Сервис бронирования переговорных комнат",
              lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "OK", "message": "Конфиг загружен, сервер запущен!"}


@app.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    # Проверяем, работает ли динамический DATABASE_URL коннект к Postgres
    result = await db.execute(text("SELECT 'Успешное подключение!'"))
    return {"database_status": result.scalar()}
