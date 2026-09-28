from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip


@pytest.mark.asyncio
async def test_trip_creation(db_session: AsyncSession):
    trip = Trip(
        name="Test vacation",
        destination="Test City",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 14),
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)

    assert trip.id is not None

    result = await db_session.execute(select(Trip).where(Trip.id == trip.id))
    saved_trip = result.scalars().one()

    assert saved_trip.id == trip.id
    assert saved_trip.name == "Test vacation"
    assert saved_trip.destination == "Test City"
    assert saved_trip.start_date == date(2026, 7, 1)
    assert saved_trip.end_date == date(2026, 7, 14)


@pytest.mark.asyncio
async def test_trip_requires_destination(db_session: AsyncSession):
    trip = Trip(
        name="Test vacation",
        destination=None,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 14),
    )

    db_session.add(trip)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_trip_dates_order(db_session: AsyncSession):
    trip = Trip(
        name="Invalid trip",
        destination="Test City",
        start_date=date(2026, 7, 14),
        end_date=date(2026, 7, 1),
    )

    db_session.add(trip)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()
