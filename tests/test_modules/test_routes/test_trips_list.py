import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import DatabaseUnavailableException
from app.main import app


@pytest_asyncio.fixture
async def saved_trips(db_session: AsyncSession, override_get_db, trip_factory):
    trips = [trip_factory(name=f"Trip {i}") for i in range(25)]
    db_session.add_all(trips)
    await db_session.flush()

    return trips


@pytest.fixture
def database_unavailable():
    async def override_get_db():
        raise DatabaseUnavailableException()
        yield

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


async def test_list_trips_returns_200_with_persisted_fields(client, saved_trips):
    response = await client.get("/trips?limit=1")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": saved_trips[0].id,
            "name": "Trip 0",
            "destination": "Paris",
            "start_date": "2026-10-01",
            "end_date": "2026-10-10",
        }
    ]


async def test_list_trips_uses_default_pagination(client, saved_trips):
    response = await client.get("/trips")

    assert response.status_code == 200

    data = response.json()
    expected_ids = sorted(trip.id for trip in saved_trips)[:20]

    assert len(data) == 20
    assert [trip["id"] for trip in data] == expected_ids


@pytest.mark.parametrize("limit", [1, 20, 100])
async def test_list_trips_accepts_valid_limits(client, saved_trips, limit):
    response = await client.get("/trips", params={"limit": limit})

    assert response.status_code == 200
    assert len(response.json()) == min(limit, len(saved_trips))


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": -1},
        {"limit": 101},
        {"limit": "abc"},
        {"limit": "1.5"},
        {"offset": -1},
        {"offset": "abc"},
        {"offset": "1.5"},
    ],
)
async def test_list_trips_returns_422_for_invalid_pagination(client, params):
    response = await client.get("/trips", params=params)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_list_trips_returns_ordered_results(client, saved_trips):
    response = await client.get("/trips?limit=25")

    assert response.status_code == 200

    result_ids = [trip["id"] for trip in response.json()]
    expected_ids = sorted(trip.id for trip in saved_trips)

    assert result_ids == expected_ids


async def test_list_trips_returns_successive_pages_without_duplicates(
    client, saved_trips
):
    first_page = await client.get("/trips?limit=10&offset=0")
    second_page = await client.get("/trips?limit=10&offset=10")
    third_page = await client.get("/trips?limit=10&offset=20")

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert third_page.status_code == 200

    first_ids = [trip["id"] for trip in first_page.json()]
    second_ids = [trip["id"] for trip in second_page.json()]
    third_ids = [trip["id"] for trip in third_page.json()]

    all_ids = first_ids + second_ids + third_ids
    expected_ids = sorted(trip.id for trip in saved_trips)

    assert len(all_ids) == 25
    assert len(set(all_ids)) == 25
    assert all_ids == expected_ids


async def test_list_trips_returns_partial_last_page(client, saved_trips):
    response = await client.get("/trips?limit=10&offset=20")

    assert response.status_code == 200

    data = response.json()
    expected_ids = sorted(trip.id for trip in saved_trips)[20:]

    assert len(data) == 5
    assert [trip["id"] for trip in data] == expected_ids


async def test_list_trips_returns_empty_list_when_database_is_empty(
    client, override_get_db
):
    response = await client.get("/trips")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_trips_returns_empty_list_when_offset_exceeds_total(
    client, saved_trips
):
    response = await client.get("/trips?limit=10&offset=100")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_trips_returns_503_when_database_unavailable(
    client, database_unavailable
):
    response = await client.get("/trips")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "SERVICE_UNAVAILABLE",
            "message": "Database is currently unavailable. Please try again later.",
        }
    }
