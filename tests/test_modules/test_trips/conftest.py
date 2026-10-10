from collections.abc import Callable
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import DatabaseUnavailableException
from app.main import app
from app.models.trip import Trip
from tests.factories import TripFactory


@pytest.fixture
def trip_factory() -> Callable[..., Trip]:
    def create_trip(
        id=None,
        name="All inclusive",
        destination="Paris",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 10),
    ) -> Trip:
        return Trip(
            id=id,
            name=name,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
        )

    return create_trip


@pytest_asyncio.fixture
async def saved_trip_id(db_session: AsyncSession, override_get_db):
    trip = TripFactory.build()
    db_session.add(trip)
    await db_session.flush()
    return trip.id


@pytest_asyncio.fixture
async def second_saved_trip_id(db_session: AsyncSession, override_get_db):
    trip = TripFactory.build(name="Winter in Krakow", destination="Krakow")
    db_session.add(trip)
    await db_session.flush()
    return trip.id


@pytest.fixture
def database_unavailable():
    async def override_get_db():
        raise DatabaseUnavailableException()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
