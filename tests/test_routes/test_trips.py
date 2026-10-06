import pytest

from app.database import get_db
from app.exceptions import DatabaseUnavailableException
from app.main import app
from tests.factories import TripFactory


@pytest.fixture
def use_test_session(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    TripFactory._meta.sqlalchemy_session = db_session
    yield
    TripFactory._meta.sqlalchemy_session = None
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def database_unavailable():
    async def override_get_db():
        raise DatabaseUnavailableException()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


async def test_get_trip_returns_200_with_persisted_fields(
    client, db_session, use_test_session
):
    trip = TripFactory()
    await db_session.flush()
    await db_session.refresh(trip)

    response = await client.get(f"/trips/{trip.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": trip.id,
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
