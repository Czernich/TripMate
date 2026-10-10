from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip
from app.modules.trips.repository import TripRepository


@pytest.mark.asyncio
async def test_add_adds_trip_to_database(db_session: AsyncSession, trip_factory):
    repository = TripRepository(db_session)
    trip = trip_factory()

    result = await repository.add(trip)

    assert result is trip
    assert trip.id is not None

    statement = select(Trip).where(Trip.id == trip.id)
    dp_trip = await db_session.scalar(statement)

    assert dp_trip is not None
    assert dp_trip.id == trip.id
    assert dp_trip.name == "All inclusive"


@pytest.mark.asyncio
async def test_get_all_returns_all_trips(db_session: AsyncSession, trip_factory):
    repository = TripRepository(db_session)
    trip1 = saved_trip
    trip2 = second_saved_trip
    db_session.add_all([trip1, trip2])
    await db_session.flush()
    result = await repository.get_all()

    assert len(result) == 2
    assert {trip.destination for trip in result} == {"Rome", "Krakow"}


@pytest.mark.asyncio
async def test_get_trip_by_id_returns_correct_trip(
    db_session: AsyncSession, saved_trip
):
    repository = TripRepository(db_session)
    trip1 = saved_trip
    db_session.add(trip1)
    await db_session.flush()
    result = await repository.get_by_id(trip1.id)

    assert result is not None
    assert result.name == "Summer in Rome"
    assert result.id == trip1.id


@pytest.mark.asyncio
async def test_get_trip_by_id_returns_none_when_trip_no_exists(
    db_session: AsyncSession,
):
    repository = TripRepository(db_session)
    result = await repository.get_by_id(100)

    assert result is None


@pytest.mark.asyncio
async def test_get_all_returns_empty_list_when_database_is_empty(
    db_session: AsyncSession,
):
    repository = TripRepository(db_session)
    result = await repository.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_update_changes_only_supplied_field(
    db_session: AsyncSession, trip_factory
):
    repository = TripRepository(db_session)
    trip = trip_factory()
    await repository.add(trip)

    original_id = trip.id
    original_created_at = trip.created_at

    result = await repository.update(
        trip,
        {"destination": "Madrid"},
    )

    await db_session.refresh(result)

    assert result.id == original_id
    assert result.created_at == original_created_at
    assert result.destination == "Madrid"
    assert result.name == "All inclusive"
    assert result.start_date == date(2026, 10, 1)
    assert result.end_date == date(2026, 10, 10)


@pytest.mark.asyncio
async def test_update_changes_both_dates(db_session: AsyncSession, trip_factory):
    repository = TripRepository(db_session)
    trip = trip_factory()
    await repository.add(trip)

    result = await repository.update(
        trip,
        {
            "start_date": date(2026, 11, 1),
            "end_date": date(2026, 11, 10),
        },
    )

    await db_session.refresh(result)

    assert result.start_date == date(2026, 11, 1)
    assert result.end_date == date(2026, 11, 10)
    assert result.name == "All inclusive"
    assert result.destination == "Paris"
