import pytest
import pytest_asyncio
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.models import Trip
from tests.factories import TripFactory


@pytest_asyncio.fixture
async def seeded_trip():
    async with SessionLocal() as session:
        trip = TripFactory.build(name="Failure commit")
        session.add(trip)
        await session.flush()
        trip_id = trip.id
        await session.commit()
    yield trip_id

    async with SessionLocal() as session:
        left_over = await session.get(Trip, trip_id)
        if left_over is not None:
            await session.delete(left_over)
            await session.commit()


async def test_delete_trip_returns_204(client, saved_trip_id):
    response = await client.delete(f"/trips/{saved_trip_id}")

    assert response.status_code == 204
    assert response.text == ""


async def test_delete_trip_returns_404_after_deleting(client, saved_trip_id):
    await client.delete(f"/trips/{saved_trip_id}")
    response = await client.get(f"/trips/{saved_trip_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "TRIP_NOT_FOUND",
            "message": f"Trip with id {saved_trip_id} was not found.",
        }
    }


async def test_repeated_delete_returns_404(client, saved_trip_id):
    first = await client.delete(f"/trips/{saved_trip_id}")
    assert first.status_code == 204

    second = await client.delete(f"/trips/{saved_trip_id}")

    assert second.status_code == 404
    assert second.json() == {
        "error": {
            "code": "TRIP_NOT_FOUND",
            "message": f"Trip with id {saved_trip_id} was not found.",
        }
    }


async def test_delete_preserves_other_trips(
    client,
    saved_trip_id,
    second_saved_trip_id,
):
    delete_response = await client.delete(f"/trips/{saved_trip_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/trips/{second_saved_trip_id}")

    assert get_response.status_code == 200
    assert get_response.json() == {
        "id": second_saved_trip_id,
        "name": "Winter in Krakow",
        "destination": "Krakow",
        "start_date": "2026-07-01",
        "end_date": "2026-07-10",
    }


@pytest.mark.parametrize("trip_id", ["-100", "10.5", "z"])
async def test_delete_trip_returns_422_for_invalid_id(client, trip_id):
    response = await client.delete(f"/trips/{trip_id}")

    assert response.status_code == 422


async def test_delete_trip_returns_503_when_database_unavailable(
    client, database_unavailable
):
    response = await client.delete("/trips/1")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "SERVICE_UNAVAILABLE",
            "message": "Database is currently unavailable. Please try again later.",
        }
    }


async def test_delete_trip_returns_503_and_rolls_back_when_commit_fails(
    client, monkeypatch, seeded_trip
):
    trip_id = seeded_trip

    async def failing_commit(self, *args, **kwargs):
        raise OperationalError("commit failed", {}, RuntimeError("connection lost"))

    with monkeypatch.context() as m:
        m.setattr(AsyncSession, "commit", failing_commit)
        response = await client.delete(f"/trips/{trip_id}")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "SERVICE_UNAVAILABLE",
            "message": "Database is currently unavailable. Please try again later.",
        }
    }

    assert "connetion lost" not in response.text

    get_response = await client.get(f"/trips/{trip_id}")

    assert get_response.status_code == 200
