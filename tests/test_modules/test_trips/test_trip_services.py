from datetime import date

import pytest

from app.models.trip import Trip
from app.modules.trips.exceptions import (
    TripAlreadyExistsException,
    TripNotFoundException,
    TripUnprocessableException,
)
from app.modules.trips.schemas import TripUpdate
from app.modules.trips.service import TripService


class FakeTripRepository:
    def __init__(self, trips: list[Trip] | None = None):
        self.trips = trips or []
        self.added_trip: Trip | None = None
        self.update_called = False

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

    async def update(self, trip: Trip, changes: dict) -> Trip:
        self.update_called = True

        for field, value in changes.items():
            setattr(trip, field, value)

        return trip


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


@pytest.mark.asyncio
async def test_update_trip_changes_one_field(trip_factory):
    trip = trip_factory(id=7)
    repo = FakeTripRepository(trips=[trip])
    service = TripService(repo)

    result = await service.update_trip(
        7,
        TripUpdate(destination="Madrid"),
    )

    assert result.id == 7
    assert result.destination == "Madrid"
    assert result.name == "All inclusive"
    assert result.start_date == date(2026, 10, 1)
    assert result.end_date == date(2026, 10, 10)
    assert repo.update_called


@pytest.mark.asyncio
async def test_update_trip_changes_both_dates(trip_factory):
    trip = trip_factory(id=7)
    repo = FakeTripRepository(trips=[trip])
    service = TripService(repo)

    result = await service.update_trip(
        7,
        TripUpdate(
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 10),
        ),
    )

    assert result.start_date == date(2026, 11, 1)
    assert result.end_date == date(2026, 11, 10)
    assert repo.update_called


@pytest.mark.asyncio
async def test_update_trip_accepts_equal_dates(trip_factory):
    trip = trip_factory(id=7)
    repo = FakeTripRepository(trips=[trip])
    service = TripService(repo)

    result = await service.update_trip(
        7,
        TripUpdate(end_date=date(2026, 10, 1)),
    )

    assert result.start_date == result.end_date
    assert repo.update_called


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param(
            {"start_date": date(2026, 10, 11)},
            id="start_after_stored_end",
        ),
        pytest.param(
            {"end_date": date(2026, 9, 30)},
            id="end_before_stored_start",
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_trip_invalid_dates_do_not_change_trip(trip_factory, changes):
    trip = trip_factory(id=7)
    repo = FakeTripRepository(trips=[trip])
    service = TripService(repo)

    payload = TripUpdate(destination="Madrid", **changes)

    with pytest.raises(TripUnprocessableException):
        await service.update_trip(7, payload)

    assert not repo.update_called
    assert trip.name == "All inclusive"
    assert trip.destination == "Paris"
    assert trip.start_date == date(2026, 10, 1)
    assert trip.end_date == date(2026, 10, 10)


@pytest.mark.asyncio
async def test_update_trip_no_exist():
    repo = FakeTripRepository()
    service = TripService(repo)

    with pytest.raises(TripNotFoundException):
        await service.update_trip(
            7,
            TripUpdate(destination="Madrid"),
        )

    assert not repo.update_called
