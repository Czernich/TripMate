from sqlalchemy import select

from app.database import SessionLocal
from app.models.trip import Trip


async def test_create_trip_returns_201_and_persists_trip(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Barcelona Trip",
            "destination": "Barcelona",
            "start_date": "2026-10-10",
            "end_date": "2026-10-15",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["name"] == "Barcelona Trip"
    assert body["destination"] == "Barcelona"

    async with SessionLocal() as fresh_session:
        trip = await fresh_session.get(Trip, body["id"])

    assert trip is not None
    assert trip.id == body["id"]


async def test_create_trip_returns_422_for_invalid_payload(client):
    response = await client.post(
        "/trips",
        json={
            "name": "",
            "destination": "Barcelona",
            "start_date": "2026-10-10",
            "end_date": "2026-10-15",
        },
    )

    assert response.status_code == 422


async def test_create_trip_does_not_insert_invalid_payload(client):
    response = await client.post(
        "/trips",
        json={
            "name": "Barcelona Trip",
            "destination": "Barcelona",
            "start_date": "2026-10-20",
            "end_date": "2026-10-10",
        },
    )

    assert response.status_code == 422

    async with SessionLocal() as fresh_session:
        result = await fresh_session.execute(select(Trip))
        trips = result.scalars().all()

    assert trips == []