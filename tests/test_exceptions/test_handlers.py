import logging

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, field_validator

from app.exceptions import AppBaseException, register_exception_handlers
from app.modules.trips.exceptions import (
    TripAlreadyExistsException,
    TripFullException,
    TripNotFoundException,
    TripUnprocessableException,
)

DOMAIN_EXCEPTIONS = {
    "base": (
        AppBaseException,
        500,
        "INTERNAL_SERVER_ERROR",
        "An unexpected server error occurred.",
    ),
    "not_found": (TripNotFoundException, 404, "TRIP_NOT_FOUND", "Trip not found."),
    "already_exists": (
        TripAlreadyExistsException,
        409,
        "TRIP_ALREADY_EXISTS",
        "Trip already exists.",
    ),
    "unprocessable": (
        TripUnprocessableException,
        422,
        "TRIP_UNPROCESSABLE",
        "The trip cannot be edited in its current state.",
    ),
    "full": (TripFullException, 400, "TRIP_IS_FULL", "Trip is fully booked."),
}


class Payload(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def always_fail(cls, value: str) -> str:
        raise ValueError("invalid name")


@pytest.fixture
def exc_app() -> FastAPI:
    exc_app = FastAPI()
    register_exception_handlers(exc_app)

    @exc_app.get("/raise/{name}")
    async def raise_domain(name: str):
        raise DOMAIN_EXCEPTIONS[name][0]()

    @exc_app.get("/unhandled")
    async def unhandled():
        raise RuntimeError("secret internal detail")

    @exc_app.get("/items/{item_id}")
    async def get_item(item_id: int):
        return {"id": item_id}

    @exc_app.post("/items")
    async def create_item(payload: Payload):
        return payload

    return exc_app


@pytest.fixture
async def exc_client(exc_app):
    transport = ASGITransport(app=exc_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.parametrize(
    "name, status_code, error_code, message",
    [(name, *values[1:]) for name, values in DOMAIN_EXCEPTIONS.items()],
)
async def test_domain_exception_is_mapped_to_error_response(
    exc_client, name, status_code, error_code, message
):
    response = await exc_client.get(f"/raise/{name}")

    assert response.status_code == status_code
    assert response.json() == {"error": {"code": error_code, "message": message}}


async def test_validation_error_for_path_param(exc_client):
    response = await exc_client.get("/items/abc")

    body = response.json()
    assert response.status_code == 422
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Invalid request payload."
    assert body["error"]["details"][0]["loc"] == ["path", "item_id"]


async def test_validation_error_with_value_error_is_serializable(exc_client):
    response = await exc_client.post("/items", json={"name": "   "})

    body = response.json()
    assert response.status_code == 422
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"][0]["loc"] == ["body", "name"]


async def test_unhandled_exception_returns_generic_500_and_logs(exc_client, caplog):
    with caplog.at_level(logging.ERROR):
        response = await exc_client.get("/unhandled")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Internal server error. Please try again later.",
        }
    }
    assert "secret internal detail" not in response.text
    assert "Traceback" not in response.text
    assert "secret internal detail" in caplog.text
