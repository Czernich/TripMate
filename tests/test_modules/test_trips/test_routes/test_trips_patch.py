from datetime import date

import pytest
import pytest_asyncio

from tests.factories import TripFactory


@pytest_asyncio.fixture
async def saved_trip(db_session, override_get_db):
    trip = TripFactory.build()
    db_session.add(trip)
    await db_session.flush()
    await db_session.refresh(trip)
    return trip


async def test_patch_trip_updates_destination(client, saved_trip):
    response = await client.patch(
        f"/trips/{saved_trip.id}",
        json={"destination": "Madrid"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": saved_trip.id,
        "name": "Summer in Rome",
        "destination": "Madrid",
        "start_date": "2026-07-01",
        "end_date": "2026-07-10",
    }

    get_response = await client.get(f"/trips/{saved_trip.id}")

    assert get_response.status_code == 200
    assert get_response.json() == response.json()


async def test_patch_trip_updates_both_dates(client, saved_trip):
    response = await client.patch(
        f"/trips/{saved_trip.id}",
        json={
            "start_date": "2026-08-01",
            "end_date": "2026-08-15",
        },
    )

    assert response.status_code == 200
    assert response.json()["start_date"] == "2026-08-01"
    assert response.json()["end_date"] == "2026-08-15"


@pytest.mark.parametrize("field", ["name", "destination"])
async def test_patch_trip_trims_text(client, saved_trip, field):
    response = await client.patch(
        f"/trips/{saved_trip.id}",
        json={field: "  Madrid  "},
    )

    assert response.status_code == 200
    assert response.json()[field] == "Madrid"


@pytest.mark.parametrize(
    "payload",
    [
        {"start_date": "2026-07-11"},
        {"end_date": "2026-06-30"},
        {
            "destination": "Madrid",
            "start_date": "2026-07-11",
        },
    ],
)
async def test_patch_trip_rejects_invalid_dates(
    client, saved_trip, db_session, payload
):
    response = await client.patch(
        f"/trips/{saved_trip.id}",
        json=payload,
    )

    assert response.status_code == 422

    await db_session.refresh(saved_trip)

    assert saved_trip.destination == "Rome"
    assert saved_trip.start_date == date(2026, 7, 1)
    assert saved_trip.end_date == date(2026, 7, 10)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": None},
        {"destination": None},
        {"start_date": None},
        {"end_date": None},
        {"name": "   "},
        {"destination": "   "},
        {"name": "a" * 256},
        {"destination": "a" * 256},
        {"start_date": "invalid-date"},
        {"unknown_field": "value"},
        {"id": 123},
        {"created_at": "2026-01-01T00:00:00Z"},
        {"updated_at": "2026-01-01T00:00:00Z"},
    ],
)
async def test_patch_trip_rejects_invalid_body(client, saved_trip, db_session, payload):
    response = await client.patch(
        f"/trips/{saved_trip.id}",
        json=payload,
    )

    assert response.status_code == 422

    await db_session.refresh(saved_trip)

    assert saved_trip.name == "Summer in Rome"
    assert saved_trip.destination == "Rome"
    assert saved_trip.start_date == date(2026, 7, 1)
    assert saved_trip.end_date == date(2026, 7, 10)


async def test_patch_trip_returns_404_when_missing(client, db_session, saved_trip):
    trip_id = saved_trip.id
    await db_session.delete(saved_trip)
    await db_session.flush()

    response = await client.patch(
        f"/trips/{trip_id}",
        json={"destination": "Madrid"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TRIP_NOT_FOUND"


@pytest.mark.parametrize("trip_id", ["abc", "1.5", "0", "-5"])
async def test_patch_trip_returns_422_for_invalid_id(client, trip_id):
    response = await client.patch(
        f"/trips/{trip_id}",
        json={"destination": "Madrid"},
    )

    assert response.status_code == 422


async def test_patch_trip_accepts_equal_dates(client, saved_trip):
    response = await client.patch(
        f"/trips/{saved_trip.id}",
        json={
            "start_date": "2026-08-01",
            "end_date": "2026-08-01",
        },
    )

    assert response.status_code == 200
    assert response.json()["start_date"] == "2026-08-01"
    assert response.json()["end_date"] == "2026-08-01"
