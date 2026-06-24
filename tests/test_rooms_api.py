async def test_rooms_require_auth(client):
    resp = await client.get("/rooms/")
    assert resp.status_code == 401


async def test_employee_can_list_rooms(client, employee, room):
    resp = await client.get("/rooms/", headers=employee["headers"])
    assert resp.status_code == 200
    assert any(r["id"] == room.id for r in resp.json())


async def test_employee_cannot_create_room(client, employee):
    resp = await client.post(
        "/rooms/", headers=employee["headers"], json={"name": "Forbidden"}
    )
    assert resp.status_code == 403


async def test_admin_can_create_room(client, admin):
    resp = await client.post(
        "/rooms/", headers=admin["headers"], json={"name": "Boardroom"}
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Boardroom"


async def test_availability_returns_slots(client, employee, room, slots):
    resp = await client.get(
        f"/rooms/{room.id}/availability?booking_date=2026-07-01",
        headers=employee["headers"],
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == len(slots)
    assert all(item["is_free"] for item in body)


async def test_availability_missing_room(client, employee):
    resp = await client.get(
        "/rooms/999999/availability?booking_date=2026-07-01",
        headers=employee["headers"],
    )
    assert resp.status_code == 404
