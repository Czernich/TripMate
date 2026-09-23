import pytest
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip

@pytest.mark.asyncio
async def test_trip_creation(session: AsyncSession):
    trip = Trip(
        name="Test vacation",
        destination="Test City",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 14),
    )
    session.add(trip)
    await session.commit()
    await session.refresh(trip)

    assert trip.id is not None

    result = await session.execute(
        select(Trip).where(Trip.id == trip.id)
    )
    saved_trip = result.scalars().one()

    assert saved_trip.id == trip.id
    assert saved_trip.name == "Test vacation"
    assert saved_trip.destination == "Test City"
    assert saved_trip.start_date == date(2026, 7, 1)
    assert saved_trip.end_date == date(2026, 7, 14)


@pytest.mark.asyncio
async def test_trip_requires_destination(session: AsyncSession):
    trip = Trip(
        name="Test vacation",
        destination=None,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 14),
    )

    session.add(trip)

    with pytest.raises(IntegrityError):
        await session.commit()

    await session.rollback()
