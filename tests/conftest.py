import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import SessionLocal, engine, get_db
from app.main import app
from app.models import Trip
from app.settings import settings_db


def ensure_test_database() -> None:
    if not settings_db.TESTING:
        raise RuntimeError("Database cleanup is allowed only in testing mode")
    if not settings_db.POSTGRES_DB.endswith("_test"):
        raise RuntimeError("Tests must use a database ending with '_test'")


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session():
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_factory() as session:
            yield session
        await transaction.rollback()


@pytest_asyncio.fixture
async def override_get_db(db_session: AsyncSession):
    async def get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_test_database():
    ensure_test_database()

    async with SessionLocal() as session:
        await session.execute(delete(Trip))
        await session.commit()

    yield
