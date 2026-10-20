import pytest

from app.models.trip import Trip
from app.modules.trips.exceptions import (
    TripAlreadyExistsException,
    TripNotFoundException,
)
from app.modules.trips.service import TripService


class FakeTripRepository:
    def __init__(self, trips: list[Trip] | None = None):
        self.trips = trips or []
        self.added_trip: Trip | None = None

    async def add(self, trip: Trip) -> Trip:
        self.added_trip = trip
        self.trips.append(trip)
        return trip

    async def get_trips(self, limit: int, offset: int) -> list[Trip]:
        return sorted(self.trips, key=lambda trip: trip.id)[offset : offset + limit]

    async def get_by_id(self, trip_id: int) -> Trip | None:
        for trip in self.trips:
            if trip.id == trip_id:
                return trip
        return None


@pytest.mark.asyncio
async def test_create_trip(trip_factory):
    repo = FakeTripRepository()
    service = TripService(repo)

    trip_data = trip_factory(name="All you need", destination="Barcelona")

    trip = await service.create_trip(trip_data)

    assert trip.name == "All you need"
    assert trip.destination == "Barcelona"


async def test_list_trips(trip_factory):
    trips = [trip_factory(id=i, name=f"Trip {i}") for i in range(1, 6)]
    repo = FakeTripRepository(trips=trips)
    service = TripService(repo)

    result = await service.list_trips(
        limit=2,
        offset=1,
    )

    assert [trip.id for trip in result] == [2, 3]


async def test_get_trip(trip_factory):
    trip1 = trip_factory(id=7, name="All inclusive", destination="Miami")
    repo = FakeTripRepository(trips=[trip1])
    service = TripService(repo)

    trip = await service.get_trip(7)

    assert trip is not None
    assert trip.id == 7
    assert trip.destination == "Miami"


async def test_get_trip_no_exist():
    repo = FakeTripRepository()
    service = TripService(repo)

    with pytest.raises(TripNotFoundException, match="Trip with id 2 was not found."):
        await service.get_trip(2)


class DuplicateTripRepository(FakeTripRepository):
    async def add(self, trip: Trip) -> Trip:
        raise TripAlreadyExistsException()


@pytest.mark.asyncio
async def test_create_trip_raises_when_trip_already_exists(trip_factory):
    service = TripService(DuplicateTripRepository())

    with pytest.raises(TripAlreadyExistsException, match="Trip already exists."):
        await service.create_trip(trip_factory())
