import pytest
from app.modules.trips.models import Trip
from app.modules.trips.schemas import TripCreate

from app.modules.trips.service import TripService


class FakeTripRepository:
    def __init__(self, trips=None):
        self.trips = trips or []
        self.created = None

    async def create(self, trip: TripCreate) -> Trip:
        created_trip = Trip(
            id=1,
            name=trip.name,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
        )
        self.created = created_trip
        self.trips.append(created_trip)
        return created_trip

    async def list(self) -> list[Trip]:
        return self.trips

    async def get_by_id(self, trip_id: int) -> Trip | None:
        for trip in self.trips:
            if trip.id == trip_id:
                return trip
        return None


@pytest.mark.asyncio
async def test_create_trip():
    repo = FakeTripRepository()
    service = TripService(repo)

    trip_data = TripCreate(
        name="Summer trip",
        destination="Paris",
        start_date="2026-06-01",
        end_date="2026-06-07",
    )

    trip = await service.create_trip(trip_data)

    assert trip.name == "Summer trip"
    assert trip.destination == "Paris"
    assert trip.id == 1


@pytest.mark.asyncio
async def test_list_trips():
    repo = FakeTripRepository(
        trips=[
            Trip(
                id=1,
                name="Trip 1",
                destination="Rome",
                start_date="2026-07-01",
                end_date="2026-07-05",
            ),
            Trip(
                id=2,
                name="Trip 2",
                destination="Paris",
                start_date="2026-07-01",
                end_date="2026-07-05",
            ),
        ]
    )
    service = TripService(repo)

    trips = await service.list_trips()

    assert len(trips) == 2
    assert trips[0].destination == "Rome"


@pytest.mark.asyncio
async def test_get_trip():
    repo = FakeTripRepository(
        trips=[
            Trip(
                id=7,
                name="Trip 7",
                destination="Berlin",
                start_date="2026-09-01",
                end_date="2026-09-05",
            )
        ]
    )
    service = TripService(repo)

    trip = await service.get_trip(7)

    assert trip is not None
    assert trip.id == 7
    assert trip.destination == "Berlin"


@pytest.mark.asyncio
async def test_get_trip_no_exist():
    repo = FakeTripRepository(trips=[])
    service = TripService(repo)

    with pytest.raises(ValueError, match="Trip with id 2 not found."):
        await service.get_trip(2)
