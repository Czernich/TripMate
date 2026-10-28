import pytest_asyncio
from sqlalchemy import delete

from app.database import SessionLocal
from app.models.trip import Trip
from tests.conftest import ensure_test_database


@pytest_asyncio.fixture
async def trip_ids_to_clean():
    trip_ids = []
    yield trip_ids

    if trip_ids:
        async with SessionLocal() as session:
            await session.execute(delete(Trip).where(Trip.id.in_(trip_ids)))
            await session.commit()


async def test_trip_lifecycle_persists_across_requests(client, trip_ids_to_clean):
    ensure_test_database()
    payload = {
        "name": "Test trip",
        "destination": "Paris",
        "start_date": "2026-11-05",
        "end_date": "2026-11-10",
    }

    post_response = await client.post("/trips", json=payload)

    assert post_response.status_code == 201

    trip = post_response.json()
    trip_id = trip["id"]
    trip_ids_to_clean.append(trip_id)

    assert trip == {"id": trip_id, **payload}

    async with SessionLocal() as session:
        persisted = await session.get(Trip, trip_id)

        assert persisted is not None
        assert persisted.name == trip["name"]

    detail_response = await client.get(f"/trips/{trip_id}")

    assert detail_response.status_code == 200
    assert detail_response.json() == trip

    list_response = await client.get("/trips", params={"limit": 100})

    assert list_response.status_code == 200
    assert trip in list_response.json()

    update_response = await client.patch(
        f"/trips/{trip_id}", json={"destination": "Amsterdam"}
    )

    assert update_response.status_code == 200

    updated = {**trip, "destination": "Amsterdam"}

    assert update_response.json() == updated

    async with SessionLocal() as session:
        persisted = await session.get(Trip, trip_id)

        assert persisted is not None
        assert persisted.name == updated["name"]
        assert persisted.destination == "Amsterdam"

    delete_response = await client.delete(f"/trips/{trip_id}")

    assert delete_response.status_code == 204

    async with SessionLocal() as session:
        persisted = await session.get(Trip, trip_id)

        assert persisted is not None
        assert persisted.deleted_at is not None

    list_after_delete = await client.get("/trips", params={"limit": 100})

    assert list_after_delete.status_code == 200
    listed_ids = {item["id"] for item in list_after_delete.json()}
    assert trip_id not in listed_ids
