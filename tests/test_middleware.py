import io
import json
import logging
import re

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.exceptions import register_exception_handlers
from app.logging_config import JsonFormatter, RequestIdFilter
from app.middleware import REQUEST_ID_HEADER, RequestContextMiddleware

GENERATED_ID = r"[0-9a-f]{32}"


@pytest.fixture
def log_entries():
    """Captures log output in the same JSON format the app uses."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    root = logging.getLogger()
    previous_level = root.level
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    yield lambda: [json.loads(line) for line in stream.getvalue().splitlines() if line]

    root.removeHandler(handler)
    root.setLevel(previous_level)


@pytest_asyncio.fixture
async def failing_client():
    test_app = FastAPI()
    test_app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(test_app)

    @test_app.get("/boom")
    async def boom():
        raise RuntimeError("kaboom")

    @test_app.get("/log")
    async def log_something():
        logging.getLogger("tests.route").info("inside handler")
        return {"status": "ok"}

    transport = ASGITransport(app=test_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_generates_request_id_when_header_is_missing(client):
    response = await client.get("/health")

    assert re.fullmatch(GENERATED_ID, response.headers[REQUEST_ID_HEADER])


async def test_generated_request_ids_are_unique(client):
    first = await client.get("/health")
    second = await client.get("/health")

    assert first.headers[REQUEST_ID_HEADER] != second.headers[REQUEST_ID_HEADER]


async def test_reuses_valid_incoming_request_id(client):
    response = await client.get(
        "/health", headers={REQUEST_ID_HEADER: "client-req-123"}
    )

    assert response.headers[REQUEST_ID_HEADER] == "client-req-123"


@pytest.mark.parametrize("invalid", ["", "bad id with spaces", "x" * 129, "semi;colon"])
async def test_replaces_invalid_incoming_request_id(client, invalid):
    response = await client.get("/health", headers={REQUEST_ID_HEADER: invalid})

    request_id = response.headers[REQUEST_ID_HEADER]
    assert request_id != invalid
    assert re.fullmatch(GENERATED_ID, request_id)


async def test_logs_one_structured_entry_per_request(client, log_entries):
    await client.get("/health", headers={REQUEST_ID_HEADER: "req-log-1"})

    entries = [e for e in log_entries() if e["logger"] == "app.request"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["message"] == "request completed"
    assert entry["level"] == "INFO"
    assert entry["method"] == "GET"
    assert entry["path"] == "/health"
    assert entry["status_code"] == 200
    assert entry["request_id"] == "req-log-1"
    assert entry["duration_ms"] >= 0
    assert "timestamp" in entry


async def test_logs_status_and_header_for_unknown_route(client, log_entries):
    response = await client.get("/does-not-exist")

    entries = [e for e in log_entries() if e["logger"] == "app.request"]
    assert response.status_code == 404
    assert len(entries) == 1
    assert entries[0]["status_code"] == 404
    assert entries[0]["request_id"] == response.headers[REQUEST_ID_HEADER]


async def test_request_id_is_available_in_logs_written_during_request(
    failing_client, log_entries
):
    await failing_client.get("/log", headers={REQUEST_ID_HEADER: "inner-1"})

    inner = [e for e in log_entries() if e["logger"] == "tests.route"]
    assert len(inner) == 1
    assert inner[0]["request_id"] == "inner-1"


async def test_unhandled_exception_logs_request_id_and_stack_trace(
    failing_client, log_entries
):
    response = await failing_client.get("/boom", headers={REQUEST_ID_HEADER: "boom-1"})

    assert response.status_code == 500
    assert response.headers[REQUEST_ID_HEADER] == "boom-1"
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Internal server error. Please try again later.",
        }
    }
    assert "kaboom" not in response.text
    assert "Traceback" not in response.text

    entries = log_entries()
    error = next(e for e in entries if e["level"] == "ERROR")
    assert error["request_id"] == "boom-1"
    assert "Traceback" in error["exception"]
    assert "RuntimeError" in error["exception"]

    request_entry = next(e for e in entries if e["logger"] == "app.request")
    assert request_entry["status_code"] == 500
    assert request_entry["request_id"] == "boom-1"


async def test_request_log_excludes_query_headers_and_body(client, log_entries):
    await client.post(
        "/health",
        params={"token": "query-secret"},
        headers={"Authorization": "Bearer header-secret"},
        json={"password": "body-secret"},
    )

    entries = [e for e in log_entries() if e["logger"] == "app.request"]
    assert len(entries) == 1
    assert entries[0]["path"] == "/health"
    serialized = json.dumps(entries[0])
    for secret in ("query-secret", "header-secret", "body-secret"):
        assert secret not in serialized
