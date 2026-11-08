import pytest_asyncio
from sqlalchemy import delete

from app.database import SessionLocal
from app.models.trip import Trip
from tests.factories import TripCreatePayloadFactory


@pytest_asyncio.fixture
async def trip(client):
    payload = TripCreatePayloadFactory.build()

    response = await client.post("/trips", json=payload)
    assert response.status_code == 201

    trip = response.json()

    yield trip

    async with SessionLocal() as session:
        await session.execute(delete(Trip).where(Trip.id == trip["id"]))
        await session.commit()


async def test_trip_lifecycle_persists_across_requests(client, trip):
    trip_id = trip["id"]

    detail_response = await client.get(f"/trips/{trip_id}")
    assert detail_response.status_code == 200
    assert detail_response.json() == trip

    list_response = await client.get("/trips", params={"limit": 100})
    assert list_response.status_code == 200
    assert trip in list_response.json()

    update_response = await client.patch(
        f"/trips/{trip_id}",
        json={"destination": "Amsterdam"},
    )
    assert update_response.status_code == 200

    updated = {**trip, "destination": "Amsterdam"}
    assert update_response.json() == updated

    async with SessionLocal() as session:
        persisted = await session.get(Trip, trip_id)
        assert persisted is not None
        assert persisted.destination == "Amsterdam"

    delete_response = await client.delete(f"/trips/{trip_id}")
    assert delete_response.status_code == 204

    async with SessionLocal() as session:
        persisted = await session.get(Trip, trip_id)
        assert persisted is not None
        assert persisted.deleted_at is not None

    list_after_delete = await client.get("/trips", params={"limit": 100})
    assert trip_id not in {item["id"] for item in list_after_delete.json()}

    detail_after_delete = await client.get(f"/trips/{trip_id}")
    assert detail_after_delete.status_code == 404
