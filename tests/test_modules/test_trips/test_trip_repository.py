from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip
from app.modules.trips.repository import TripRepository


async def test_add_adds_trip_to_database(db_session: AsyncSession, trip_factory):
    repository = TripRepository(db_session)
    trip = trip_factory()
    repository.add(trip)
    await db_session.flush()

    assert trip.id is not None

    statement = select(Trip).where(Trip.id == trip.id)
    db_trip = await db_session.scalar(statement)

    assert db_trip is not None
    assert db_trip.id == trip.id
    assert db_trip.name == "All inclusive"


async def test_get_all_returns_all_trips(db_session: AsyncSession, trip_factory):
    repository = TripRepository(db_session)
    trip1 = trip_factory()
    trip2 = trip_factory(name="City break", destination="Berlin")
    db_session.add_all([trip1, trip2])
    await db_session.flush()
    result = await repository.get_all()

    assert len(result) == 2
    assert {trip.destination for trip in result} == {"Paris", "Berlin"}


async def test_get_trip_by_id_returns_correct_trip(
    db_session: AsyncSession, trip_factory
):
    repository = TripRepository(db_session)
    trip1 = trip_factory()
    db_session.add(trip1)
    await db_session.flush()
    result = await repository.get_by_id(trip1.id)

    assert result is not None
    assert result.name == "All inclusive"
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
