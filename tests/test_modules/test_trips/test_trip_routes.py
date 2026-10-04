from datetime import date

import pytest

from app.database import get_db
from app.exceptions import DatabaseUnavailableException
from app.main import app
from app.models.trip import Trip


@pytest.mark.asyncio
async def test_get_trip_returns_200_with_persisted_fields(client, db_session):
    trip = Trip(
        name="Summer in Rome",
        destination="Rome",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 10),
    )
    db_session.add(trip)
    await db_session.flush()
    await db_session.refresh(trip)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.get(f"/trips/{trip.id}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json() == {
        "id": trip.id,
        "name": "Summer in Rome",
        "destination": "Rome",
        "start_date": "2026-07-01",
        "end_date": "2026-07-10",
    }


@pytest.mark.asyncio
async def test_get_trip_returns_404_when_missing(client, db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.get("/trips/999999")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "TRIP_NOT_FOUND"
    assert "999999" in body["error"]["message"]


@pytest.mark.asyncio
@pytest.mark.parametrize("trip_id", ["abc", "1.5", "0", "-5"])
async def test_get_trip_returns_422_for_invalid_id(client, trip_id):
    response = await client.get(f"/trips/{trip_id}")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_trip_returns_503_when_database_unavailable(client):
    async def override_get_db_unavailable():
        raise DatabaseUnavailableException()

    app.dependency_overrides[get_db] = override_get_db_unavailable
    try:
        response = await client.get("/trips/1")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "SERVICE_UNAVAILABLE"
