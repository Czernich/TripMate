from datetime import date

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.main import app
from app.models.trip import Trip


@pytest.fixture
def client():
    client = TestClient(app)
    return client

@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

