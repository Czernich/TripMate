import pytest

from app.models.trip import Trip
from app.modules.trips.service import TripService


class FakeTripRepository:
    def __init__(self, trips: list[Trip] | None = None):
        self.trips = trips or []
        self.added_trip: Trip | None = None

    async def add(self, trip: Trip) -> Trip:
        self.added_trip = trip
        self.trips.append(trip)
        return trip

    async def get_all(self) -> list[Trip]:
        return self.trips

    async def get_by_id(self, trip_id: int) -> Trip | None:
        for trip in self.trips:
            if trip.id == trip_id:
                return trip
        return None


@pytest.mark.asyncio
async def test_create_trip(trip_factory):
    repo = FakeTripRepository()
    service = TripService(repo)

    trip_data = trip_factory(
        name="All you need",
        destination="Barcelona",
    )

    trip = await service.create_trip(trip_data)

    assert trip.name == "All you need"
    assert trip.destination == "Barcelona"
    assert trip is trip_data
    assert repo.added_trip is trip_data


@pytest.mark.asyncio
async def test_list_trips(trip_factory):
    trip1 = trip_factory(name="Your trip", destination="Amsterdam")
    trip2 = trip_factory(name="Dream trip", destination="Dubai")
    repo = FakeTripRepository(trips=[trip1, trip2])
    service = TripService(repo)

    trips = await service.list_trips()

    assert len(trips) == 2
    assert trips[0].destination == "Amsterdam"


@pytest.mark.asyncio
async def test_get_trip(trip_factory):
    trip1 = trip_factory(id=7, name="All inclusive", destination="Miami")
    repo = FakeTripRepository(trips=[trip1])
    service = TripService(repo)

    trip = await service.get_trip(7)

    assert trip is not None
    assert trip.id == 7
    assert trip.destination == "Miami"


@pytest.mark.asyncio
async def test_get_trip_no_exist():
    repo = FakeTripRepository()
    service = TripService(repo)

    with pytest.raises(ValueError, match="Trip with id 2 not found."):
        await service.get_trip(2)
