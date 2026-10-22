from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.models.trip import Trip


@pytest.fixture
def payload():
    return {
        "name": f"Barcelona Trip {uuid4().hex}",
        "destination": "Barcelona",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
    }


def database_error():
    return OperationalError(
        statement="INSERT INTO trips",
        params={},
        orig=OSError("Database connection lost"),
    )


async def test_create_trip_returns_201_and_persists_trip(client, payload):
    trip_id = None

    try:
        response = await client.post("/trips", json=payload)

        assert response.status_code == 201

        body = response.json()
        trip_id = body["id"]

        assert trip_id is not None
        assert body["name"] == payload["name"]
        assert body["destination"] == payload["destination"]

        async with SessionLocal() as fresh_session:
            trip = await fresh_session.get(Trip, trip_id)

            assert trip is not None
            assert trip.id == trip_id
            assert trip.name == payload["name"]

    finally:
        if trip_id is not None:
            async with SessionLocal() as session:
                trip = await session.get(Trip, trip_id)

                if trip is not None:
                    await session.delete(trip)
                    await session.commit()


async def test_create_trip_returns_422_for_invalid_payload(
    client, payload, override_get_db
):
    payload["name"] = ""

    response = await client.post("/trips", json=payload)

    assert response.status_code == 422


async def test_create_trip_does_not_insert_invalid_payload(
    client, payload, db_session, override_get_db
):
    payload["start_date"] = "2026-10-20"
    payload["end_date"] = "2026-10-10"

    result_before = await db_session.execute(
        select(Trip).where(Trip.name == payload["name"])
    )
    assert result_before.scalar_one_or_none() is None

    response = await client.post("/trips", json=payload)

    assert response.status_code == 422

    result_after = await db_session.execute(
        select(Trip).where(Trip.name == payload["name"])
    )
    assert result_after.scalar_one_or_none() is None


@pytest.mark.parametrize("failed_method", ["flush", "commit"])
async def test_create_trip_rolls_back_on_database_failure(
    client, payload, monkeypatch, failed_method
):
    rollback_mock = AsyncMock()

    original_rollback = AsyncSession.rollback

    async def track_rollback(session):
        await rollback_mock()
        await original_rollback(session)

    with monkeypatch.context() as patch:
        patch.setattr(
            AsyncSession,
            failed_method,
            AsyncMock(side_effect=database_error()),
        )
        patch.setattr(
            AsyncSession,
            "rollback",
            track_rollback,
        )

        response = await client.post("/trips", json=payload)

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "SERVICE_UNAVAILABLE",
            "message": ("Database is currently unavailable. Please try again later."),
        }
    }

    rollback_mock.assert_awaited_once()

    async with SessionLocal() as session:
        result = await session.execute(select(Trip).where(Trip.name == payload["name"]))

        assert result.scalar_one_or_none() is None
