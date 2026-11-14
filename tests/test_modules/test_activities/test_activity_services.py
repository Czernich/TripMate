from datetime import date, datetime, time

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity, Trip
from app.modules.activities.exceptions import ActivityDateOutOfRangeException
from app.modules.activities.repository import ActivityRepository
from app.modules.activities.schemas import ActivityCreate
from app.modules.activities.service import ActivityService
from app.modules.trips.exceptions import TripNotFoundException
from app.modules.trips.repository import TripRepository
from tests.factories import TripFactory


@pytest.fixture
def service(db_session: AsyncSession) -> ActivityService:
    return ActivityService(
        repository=ActivityRepository(db_session),
        trip_repository=TripRepository(db_session),
    )


def make_payload(activity_date: date = date(2026, 7, 2)) -> ActivityCreate:
    return ActivityCreate(
        title="Colosseum tour",
        activity_date=activity_date,
        start_time=time(9, 30),
    )


async def create_trip(session: AsyncSession, **overrides) -> Trip:
    trip = TripFactory.build(**overrides)
    session.add(trip)
    await session.flush()
    return trip


async def count_activities(session: AsyncSession) -> int:
    result = await session.scalar(select(func.count()).select_from(Activity))
    assert result is not None
    return result


async def test_create_activity_persists_for_existing_trip(
    db_session: AsyncSession,
    service: ActivityService,
):
    trip = await create_trip(db_session)

    activity = await service.create_activity(trip.id, make_payload())

    assert activity.id is not None
    assert activity.trip_id == trip.id
    assert activity.title == "Colosseum tour"
    assert activity.start_time == time(9, 30)
    assert await count_activities(db_session) == 1


@pytest.mark.parametrize("day", [date(2026, 7, 1), date(2026, 7, 10)])
async def test_create_activity_accepts_first_and_last_trip_dates(
    db_session: AsyncSession,
    service: ActivityService,
    day: date,
):
    trip = await create_trip(db_session)

    activity = await service.create_activity(trip.id, make_payload(day))

    assert activity.activity_date == day


async def test_create_activity_accepts_date_of_one_day_trip(
    db_session: AsyncSession,
    service: ActivityService,
):
    day = date(2026, 7, 2)
    trip = await create_trip(db_session, start_date=day, end_date=day)

    activity = await service.create_activity(trip.id, make_payload(day))

    assert activity.activity_date == day


@pytest.mark.parametrize("day", [date(2026, 6, 30), date(2026, 7, 11)])
async def test_create_activity_rejects_dates_outside_trip_range(
    db_session: AsyncSession,
    service: ActivityService,
    day: date,
):
    trip = await create_trip(db_session)

    with pytest.raises(ActivityDateOutOfRangeException):
        await service.create_activity(trip.id, make_payload(day))

    assert await count_activities(db_session) == 0


async def test_create_activity_raises_when_trip_is_missing(
    db_session: AsyncSession,
    service: ActivityService,
):
    with pytest.raises(TripNotFoundException):
        await service.create_activity(999_999, make_payload())

    assert await count_activities(db_session) == 0


async def test_create_activity_raises_when_trip_is_deleted(
    db_session: AsyncSession,
    service: ActivityService,
):
    trip = await create_trip(db_session)
    trip.deleted_at = datetime.now().astimezone()
    await db_session.flush()

    with pytest.raises(TripNotFoundException):
        await service.create_activity(trip.id, make_payload())

    assert await count_activities(db_session) == 0


async def test_failed_write_leaves_no_partial_activity(
    db_session: AsyncSession,
    service: ActivityService,
    monkeypatch: pytest.MonkeyPatch,
):
    trip = await create_trip(db_session)
    trip_id = trip.id

    async def add_then_fail(
        self: ActivityRepository,
        activity: Activity,
    ) -> Activity:
        self.session.add(activity)
        await self.session.flush()
        raise SQLAlchemyError("simulated failure after insert")

    monkeypatch.setattr(ActivityRepository, "add", add_then_fail)

    with pytest.raises(SQLAlchemyError):
        async with db_session.begin_nested():
            await service.create_activity(trip_id, make_payload())

    assert await count_activities(db_session) == 0
    assert await db_session.get(Trip, trip_id) is not None
