from app.core.constants import EMPLOYEE_ROLE
from app.core.security import verify_password
from app.crud.user import CRUDUser
from app.schemas.user import UserCreate


async def test_create_user_defaults_to_employee(db_session):
    user = await CRUDUser.create(
        db_session, UserCreate(login="charlie", password="pwd12345")
    )
    assert user.id is not None
    assert user.login == "charlie"
    assert user.role == EMPLOYEE_ROLE


async def test_create_user_hashes_password(db_session):
    user = await CRUDUser.create(
        db_session, UserCreate(login="dana", password="pwd12345")
    )
    assert user.hashed_password != "pwd12345"
    assert verify_password("pwd12345", user.hashed_password)


async def test_get_by_login_found(db_session):
    await CRUDUser.create(db_session, UserCreate(login="erin", password="pwd12345"))
    found = await CRUDUser.get_by_login(db_session, "erin")
    assert found is not None
    assert found.login == "erin"


async def test_get_by_login_missing(db_session):
    assert await CRUDUser.get_by_login(db_session, "nobody") is None
