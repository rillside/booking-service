from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.init_db import create_initial_admin, create_initial_slots
from app.database import AsyncSessionLocal, engine
from app.models import Base
from app.routers.auth import router as auth_router
from app.routers.booking import router as booking_router
from app.routers.room import router as room_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы и наполняем начальными данными (админ, дефолтные слоты).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await create_initial_admin(db)
        await create_initial_slots(db)
    yield


app = FastAPI(title="Сервис бронирования переговорных комнат", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(room_router)
app.include_router(auth_router)
app.include_router(booking_router)
