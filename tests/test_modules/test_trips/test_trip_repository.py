from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip
from app.modules.trips.repository import TripRepository


async def test_add_adds_trip_to_database(db_session: AsyncSession, saved_trip):
    repository = TripRepository(db_session)
    trip = saved_trip
    await repository.add(trip)

    assert trip.id is not None
    assert trip.created_at is not None

    statement = select(Trip).where(Trip.id == trip.id)
    db_trip = await db_session.scalar(statement)

    assert db_trip is not None
    assert db_trip.id == trip.id
    assert db_trip.name == "Summer in Rome"


async def test_get_all_returns_all_trips(
    db_session: AsyncSession, saved_trip, second_saved_trip
):
    repository = TripRepository(db_session)
    trip1 = saved_trip
    trip2 = second_saved_trip
    db_session.add_all([trip1, trip2])
    await db_session.flush()
    result = await repository.get_all()

    assert len(result) == 2
    assert {trip.destination for trip in result} == {"Rome", "Krakow"}


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


async def test_get_trip_by_id_returns_none_when_trip_no_exists(
    db_session: AsyncSession,
):
    repository = TripRepository(db_session)
    result = await repository.get_by_id(100)

    assert result is None


async def test_get_all_returns_empty_list_when_database_is_empty(
    db_session: AsyncSession,
):
    repository = TripRepository(db_session)
    result = await repository.get_all()

    assert result == []


async def test_remove_trip_deletes_trip_from_database(
    db_session: AsyncSession, saved_trip
):
    repository = TripRepository(db_session)
    trip = saved_trip
    db_session.add(trip)
    await db_session.flush()

    await repository.remove(trip)

    result = await db_session.get(Trip, trip.id)
    assert result is None
