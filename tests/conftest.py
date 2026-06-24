from datetime import time

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.constants import ADMIN_ROLE, EMPLOYEE_ROLE
from app.core.security import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models.rooms import Room
from app.models.slots import Slot
from app.models.users import User

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    """Изолированный движок: in-memory SQLite, общий на один тест через StaticPool."""
    eng = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
def session_factory(engine):
    return async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncSession:
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncClient:
    """HTTP-клиент с подменённой зависимостью get_db на тестовую БД."""

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _make_user(db_session, login: str, password: str, role: str) -> dict:
    user = User(login=login, hashed_password=hash_password(password), role=role)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    token = create_access_token({"sub": user.login, "role": user.role})
    return {"user": user, "id": user.id, "token": token, "headers": _auth(token)}


@pytest_asyncio.fixture
async def admin(db_session) -> dict:
    return await _make_user(db_session, "admin", "adminpass", ADMIN_ROLE)


@pytest_asyncio.fixture
async def employee(db_session) -> dict:
    return await _make_user(db_session, "alice", "alicepass", EMPLOYEE_ROLE)


@pytest_asyncio.fixture
async def employee2(db_session) -> dict:
    return await _make_user(db_session, "bob", "bobpass", EMPLOYEE_ROLE)


@pytest_asyncio.fixture
async def slots(db_session) -> list[Slot]:
    items = [
        Slot(start_time=time(9, 0), end_time=time(11, 0)),
        Slot(start_time=time(11, 0), end_time=time(13, 0)),
    ]
    db_session.add_all(items)
    await db_session.commit()
    for item in items:
        await db_session.refresh(item)
    return items


@pytest_asyncio.fixture
async def room(db_session) -> Room:
    item = Room(name="Переговорная А")
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item
