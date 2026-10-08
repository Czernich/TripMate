import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import DatabaseUnavailableException
from app.main import app
from tests.factories import TripFactory


@pytest_asyncio.fixture
async def saved_trip_id(db_session: AsyncSession, override_get_db):
    trip = TripFactory.build()
    db_session.add(trip)
    await db_session.flush()
    return trip.id


@pytest.fixture
def database_unavailable():
    async def override_get_db():
        raise DatabaseUnavailableException()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


async def test_get_trip_returns_200_with_persisted_fields(client, saved_trip_id):
    response = await client.get(f"/trips/{saved_trip_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": saved_trip_id,
        "name": "Summer in Rome",
        "destination": "Rome",
        "start_date": "2026-07-01",
        "end_date": "2026-07-10",
    }


async def test_get_trip_returns_404_when_missing(client):
    response = await client.get("/trips/999999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "TRIP_NOT_FOUND",
            "message": "Trip with id 999999 was not found.",
        }
    }


@pytest.mark.parametrize("trip_id", ["abc", "1.5", "0", "-5"])
async def test_get_trip_returns_422_for_invalid_id(client, trip_id):
    response = await client.get(f"/trips/{trip_id}")

    assert response.status_code == 422


async def test_get_trip_returns_503_when_database_unavailable(
    client, database_unavailable
):
    response = await client.get("/trips/1")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "SERVICE_UNAVAILABLE",
            "message": "Database is currently unavailable. Please try again later.",
        }
    }
