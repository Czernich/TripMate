from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip
from app.modules.trips.repository import TripRepository


async def test_add_adds_trip_to_database(db_session: AsyncSession, saved_trip):
    repository = TripRepository(db_session)
    trip = await saved_trip()
    await repository.add(trip)

    assert trip.id is not None
    assert trip.created_at is not None

    statement = select(Trip).where(Trip.id == trip.id)
    db_trip = await db_session.scalar(statement)

    assert db_trip is not None
    assert db_trip.id == trip.id
    assert db_trip.name == "Summer in Rome"


async def test_get_trips_returns_trips_ordered_by_id(
    db_session: AsyncSession, trip_factory
):
    repository = TripRepository(db_session)

    trip1 = trip_factory()
    trip2 = trip_factory(name="City break", destination="Berlin")

    db_session.add_all([trip1, trip2])

    await db_session.flush()
    result = await repository.get_trips(limit=20, offset=0)

    assert len(result) == 2
    assert [trip.id for trip in result] == [trip1.id, trip2.id]
    assert {trip.destination for trip in result} == {"Paris", "Berlin"}


async def test_get_trip_by_id_returns_correct_trip(
    db_session: AsyncSession, saved_trip
):
    repository = TripRepository(db_session)
    trip1 = await saved_trip()
    result = await repository.get_by_id(trip1.id)

    assert result is not None
    assert result.name == "Summer in Rome"
    assert result.id == trip1.id


async def test_get_trip_by_id_returns_none_when_trip_no_exists(
    db_session: AsyncSession,
):
    repository = TripRepository(db_session)
    result = await repository.get_by_id(100)

    assert result is None


async def test_get_trips_returns_empty_list_when_database_is_empty(
    db_session: AsyncSession,
):
    repository = TripRepository(db_session)
    result = await repository.get_trips(limit=20, offset=0)

    assert result == []


async def test_get_trips_returns_paginated_trips(
    db_session: AsyncSession,
    trip_factory,
):
    repository = TripRepository(db_session)

    trips = [trip_factory(name=f"Trip {i}") for i in range(25)]
    db_session.add_all(trips)
    await db_session.flush()

    result = await repository.get_trips(limit=10, offset=10)

    expected_ids = sorted(trip.id for trip in trips)[10:20]

    assert len(result) == 10
    assert [trip.id for trip in result] == expected_ids


async def test_get_trips_returns_partial_last_page(
    db_session: AsyncSession,
    trip_factory,
):
    repository = TripRepository(db_session)

    trips = [trip_factory(name=f"Trip {i}") for i in range(25)]
    db_session.add_all(trips)
    await db_session.flush()

    result = await repository.get_trips(limit=10, offset=20)

    expected_ids = sorted(trip.id for trip in trips)[20:]

    assert len(result) == 5
    assert [trip.id for trip in result] == expected_ids


async def test_get_trips_returns_empty_list_when_offset_exceeds_total(
    db_session: AsyncSession,
    trip_factory,
):
    repository = TripRepository(db_session)

    trips = [trip_factory(name=f"Trip {i}") for i in range(5)]
    db_session.add_all(trips)
    await db_session.flush()

    result = await repository.get_trips(limit=10, offset=10)

    assert result == []


async def test_soft_remove_trip_sets_deleted_at_attribute(
    db_session: AsyncSession, saved_trip
):
    repository = TripRepository(db_session)
    trip = await saved_trip()

    await repository.remove(trip)
    await db_session.refresh(trip)

    result = await db_session.get(Trip, trip.id)

    assert result is not None
    assert result.deleted_at is not None

    get_trip = await repository.get_by_id(trip.id)

    assert get_trip is None


async def test_get_all_excludes_soft_deleted_trips(
    db_session: AsyncSession, saved_trip
):
    repository = TripRepository(db_session)
    deleted_trip = await saved_trip()
    active_trip = await saved_trip(name="Winter in Krakow", destination="Krakow")

    await repository.remove(deleted_trip)

    result = await repository.get_trips(limit=10, offset=0)

    assert result == [active_trip]


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
