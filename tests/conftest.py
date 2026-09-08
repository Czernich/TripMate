from fastapi.testclient import TestClient
from app.main import app
import pytest


@pytest.fixture
def client():
    client = TestClient(app)
    return client