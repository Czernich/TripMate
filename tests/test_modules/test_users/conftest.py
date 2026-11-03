import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import engine
from app.models.user import User


@pytest_asyncio.fixture
async def db_session():
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def saved_user(db_session):
    user = User(
        email="john@example.com",
        display_name="John",
        password_hash="test_password_hash",
    )

    db_session.add(user)
    await db_session.flush()

    return user


@pytest.fixture
def user_factory():
    def create_user(**kwargs):
        defaults = {
            "email": "john@example.com",
            "display_name": "John",
            "password_hash": "test_password_hash",
        }
        defaults.update(kwargs)

        return User(**defaults)

    return create_user
