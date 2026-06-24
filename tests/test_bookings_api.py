BOOKING_DATE = "2026-07-01"


def _payload(room, slot, day=BOOKING_DATE) -> dict:
    return {"room_id": room.id, "slot_id": slot.id, "booking_date": day}


async def test_create_booking(client, employee, room, slots):
    resp = await client.post(
        "/bookings/", headers=employee["headers"], json=_payload(room, slots[0])
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["user_id"] == employee["id"]
    assert body["slot_id"] == slots[0].id


async def test_booking_requires_auth(client, room, slots):
    resp = await client.post("/bookings/", json=_payload(room, slots[0]))
    assert resp.status_code == 401


async def test_duplicate_booking_conflict(client, employee, room, slots):
    await client.post(
        "/bookings/", headers=employee["headers"], json=_payload(room, slots[0])
    )
    resp = await client.post(
        "/bookings/", headers=employee["headers"], json=_payload(room, slots[0])
    )
    assert resp.status_code == 409


async def test_booking_missing_room(client, employee, slots):
    resp = await client.post(
        "/bookings/",
        headers=employee["headers"],
        json={"room_id": 999999, "slot_id": slots[0].id, "booking_date": BOOKING_DATE},
    )
    assert resp.status_code == 404


async def test_booking_missing_slot(client, employee, room):
    resp = await client.post(
        "/bookings/",
        headers=employee["headers"],
        json={"room_id": room.id, "slot_id": 999999, "booking_date": BOOKING_DATE},
    )
    assert resp.status_code == 404


async def test_employee_sees_only_own_bookings(
    client, employee, employee2, room, slots
):
    await client.post(
        "/bookings/", headers=employee["headers"], json=_payload(room, slots[0])
    )
    await client.post(
        "/bookings/", headers=employee2["headers"], json=_payload(room, slots[1])
    )

    resp = await client.get("/bookings/", headers=employee2["headers"])
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert all(b["user_id"] == employee2["id"] for b in body)


async def test_admin_sees_all_bookings(client, admin, employee, employee2, room, slots):
    await client.post(
        "/bookings/", headers=employee["headers"], json=_payload(room, slots[0])
    )
    await client.post(
        "/bookings/", headers=employee2["headers"], json=_payload(room, slots[1])
    )

    resp = await client.get("/bookings/", headers=admin["headers"])
    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_employee_cannot_cancel_others_booking(
    client, employee, employee2, room, slots
):
    created = await client.post(
        "/bookings/", headers=employee["headers"], json=_payload(room, slots[0])
    )
    booking_id = created.json()["id"]

    resp = await client.delete(
        f"/bookings/{booking_id}", headers=employee2["headers"]
    )
    assert resp.status_code == 403


async def test_owner_can_cancel_own_booking(client, employee, room, slots):
    created = await client.post(
        "/bookings/", headers=employee["headers"], json=_payload(room, slots[0])
    )
    booking_id = created.json()["id"]

    resp = await client.delete(
        f"/bookings/{booking_id}", headers=employee["headers"]
    )
    assert resp.status_code == 204


async def test_admin_can_cancel_any_booking(client, admin, employee, room, slots):
    created = await client.post(
        "/bookings/", headers=employee["headers"], json=_payload(room, slots[0])
    )
    booking_id = created.json()["id"]

    resp = await client.delete(f"/bookings/{booking_id}", headers=admin["headers"])
    assert resp.status_code == 204


async def test_cancel_missing_booking(client, admin):
    resp = await client.delete("/bookings/999999", headers=admin["headers"])
    assert resp.status_code == 404
