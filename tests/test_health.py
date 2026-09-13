from app.main import app
from app.database import get_db


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


class FailingSession:
    def execute(self, *args, **kwargs):
        raise RuntimeError("Database unavailable")
    
    
def override_get_db():
    yield FailingSession()
    

def test_health_db_unavailable(client):
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/health/db")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert "Database unavailable" in response.json()["detail"]
