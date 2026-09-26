from sqlalchemy import text

from app.database import SessionLocal, engine, get_db
from app.main import app


class FailingSession:
    async def execute(self, *args, **kwargs):
        raise RuntimeError("Database unavailable")


def override_get_db():
    yield FailingSession()


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_db(client):
    response = await client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_session_lifecycle_closes_without_leaking_connections():
    before = engine.pool.checkedout()

    async with SessionLocal() as session:
        await session.execute(text("SELECT 1"))
        assert engine.pool.checkedout() >= before + 1
    assert engine.pool.checkedout() == before


async def test_health_db_unavailable(client):
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await client.get("/health/db")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json()["detail"] == "Database unavailable"
