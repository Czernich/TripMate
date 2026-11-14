from datetime import date, datetime, time

import pytest
from sqlalchemy import Time, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity, Trip
from tests.factories import ActivityFactory, TripFactory


async def create_trip(session: AsyncSession) -> Trip:
    trip = TripFactory.build()
    session.add(trip)
    await session.flush()
    return trip


async def test_activity_persists_with_defaults(db_session: AsyncSession):
    trip = await create_trip(db_session)
    activity = ActivityFactory.build(trip_id=trip.id)
    db_session.add(activity)
    await db_session.flush()
    await db_session.refresh(activity)

    assert activity.id is not None
    assert activity.trip_id == trip.id
    assert activity.title == "Colosseum tour"
    assert activity.activity_date == date(2026, 7, 2)
    assert activity.start_time == time(9, 30)
    assert activity.start_time.tzinfo is None
    assert activity.description is None
    assert isinstance(activity.created_at, datetime)
    assert activity.created_at.tzinfo is not None


@pytest.mark.parametrize("column", ["trip_id", "title", "activity_date", "start_time"])
async def test_required_columns_reject_null(
    db_session: AsyncSession,
    column: str,
):
    trip = await create_trip(db_session)
    values = {"trip_id": trip.id}
    values[column] = None
    db_session.add(ActivityFactory.build(**values))

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()


@pytest.mark.parametrize("title", ["", "   "])
async def test_blank_title_rejected_by_database(
    db_session: AsyncSession,
    title: str,
):
    trip = await create_trip(db_session)
    db_session.add(ActivityFactory.build(trip_id=trip.id, title=title))

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()


async def test_invalid_trip_id_rejected(db_session: AsyncSession):
    db_session.add(ActivityFactory.build(trip_id=-1))

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()


async def test_deleting_trip_cascades_to_activities(db_session: AsyncSession):
    trip = await create_trip(db_session)
    activity = ActivityFactory.build(trip_id=trip.id)
    db_session.add(activity)
    await db_session.flush()
    activity_id = activity.id

    await db_session.execute(delete(Trip).where(Trip.id == trip.id))
    db_session.expire_all()

    remaining = await db_session.scalar(
        select(Activity.id).where(Activity.id == activity_id)
    )
    assert remaining is None


def test_start_time_column_has_no_timezone():
    column_type = Activity.__table__.c.start_time.type

    assert isinstance(column_type, Time)
    assert column_type.timezone is False


def test_model_defines_expected_index():
    indexes = {
        index.name: tuple(column.name for column in index.columns)
        for index in Activity.__table__.indexes
    }
    name = "ix_activities_trip_id_activity_date_start_time"

    assert indexes[name] == ("trip_id", "activity_date", "start_time")
