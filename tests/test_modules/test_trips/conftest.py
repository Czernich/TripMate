import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import DatabaseUnavailableException
from app.main import app
from tests.factories import TripFactory


@pytest_asyncio.fixture
async def saved_trip(db_session: AsyncSession, override_get_db):
    trip = TripFactory.build()
    db_session.add(trip)
    await db_session.flush()
    return trip


@pytest_asyncio.fixture
async def second_saved_trip(db_session: AsyncSession, override_get_db):
    trip = TripFactory.build(name="Winter in Krakow", destination="Krakow")
    db_session.add(trip)
    await db_session.flush()
    return trip


@pytest.fixture
def database_unavailable():
    async def override_get_db():
        raise DatabaseUnavailableException()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
