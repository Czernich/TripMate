import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database import Base, engine
from app.main import app
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


@pytest_asyncio.fixture(autouse=True)
async def reset_database_schema():
    ensure_test_database()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(
    reset_database_schema,
):
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
