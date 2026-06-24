async def test_register_returns_employee(client):
    resp = await client.post(
        "/auth/register", json={"login": "newuser", "password": "pwd12345"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["login"] == "newuser"
    assert body["role"] == "employee"
    assert "password" not in body


async def test_register_duplicate_login(client):
    await client.post(
        "/auth/register", json={"login": "dup", "password": "pwd12345"}
    )
    resp = await client.post(
        "/auth/register", json={"login": "dup", "password": "pwd12345"}
    )
    assert resp.status_code == 400


async def test_login_success_returns_token(client):
    await client.post(
        "/auth/register", json={"login": "loginer", "password": "pwd12345"}
    )
    resp = await client.post(
        "/auth/login", data={"username": "loginer", "password": "pwd12345"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_login_wrong_password(client):
    await client.post(
        "/auth/register", json={"login": "loginer2", "password": "pwd12345"}
    )
    resp = await client.post(
        "/auth/login", data={"username": "loginer2", "password": "wrong"}
    )
    assert resp.status_code == 401


async def test_login_unknown_user(client):
    resp = await client.post(
        "/auth/login", data={"username": "ghost", "password": "pwd12345"}
    )
    assert resp.status_code == 401
