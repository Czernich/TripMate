from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.exceptions.handlers import register_exception_handlers
from app.integrations.countries.client import CountryProvider
from app.integrations.countries.exceptions import (
    CountryNotFound,
    CountryProviderAuthenticationError,
    CountryProviderRateLimitExceeded,
    CountryProviderTimeout,
    CountryProviderUnavailable,
    MalformedCountryResponse,
)
from app.integrations.countries.schemas import Country
from app.modules.countries.dependencies import get_country_provider
from app.routes.countries import router


@pytest.fixture
def country_data():
    return {
        "code": "CA",
        "name": "Canada",
        "currencies": [
            {
                "code": "CAD",
                "name": "Canadian dollar",
                "symbol": "$",
            },
            {
                "code": "USD",
                "name": "US dollar",
                "symbol": None,
            },
        ],
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "fr", "name": "French"},
        ],
        "utc_offsets": ["UTC-08:00", "UTC-03:30"],
    }


@pytest.fixture
def provider(country_data):
    mock = AsyncMock(spec=CountryProvider)
    mock.get_country.return_value = Country.model_validate(country_data)
    return mock


@pytest.fixture
def api_app(provider):
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)

    def override_provider():
        return provider

    app.dependency_overrides[get_country_provider] = override_provider

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def api_client(api_app):
    async with AsyncClient(
        transport=ASGITransport(app=api_app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.mark.parametrize("code", ["CA", "ca", "cA"])
async def test_returns_normalized_country(
    api_client,
    provider,
    country_data,
    code,
):
    response = await api_client.get(f"/countries/{code}")

    assert response.status_code == 200
    assert response.json() == country_data
    provider.get_country.assert_awaited_once_with("CA")


@pytest.mark.parametrize(
    "code",
    ["C", "CAN", "C1", "%20CA", "CA%20", "%C3%A9a"],
)
async def test_rejects_malformed_code(api_client, provider, code):
    response = await api_client.get(f"/countries/{code}")

    assert response.status_code == 422

    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["loc"] == ["path", "country_code"]

    provider.get_country.assert_not_awaited()


@pytest.mark.parametrize(
    "exception_type,status_code,error_code",
    [
        (CountryNotFound, 404, "COUNTRY_NOT_FOUND"),
        (CountryProviderTimeout, 504, "COUNTRY_PROVIDER_TIMEOUT"),
        (
            CountryProviderUnavailable,
            503,
            "COUNTRY_PROVIDER_UNAVAILABLE",
        ),
        (
            MalformedCountryResponse,
            502,
            "MALFORMED_COUNTRY_RESPONSE",
        ),
        (
            CountryProviderAuthenticationError,
            502,
            "COUNTRY_PROVIDER_AUTHENTICATION_ERROR",
        ),
        (
            CountryProviderRateLimitExceeded,
            503,
            "COUNTRY_PROVIDER_RATE_LIMIT_EXCEEDED",
        ),
    ],
)
async def test_maps_provider_errors(
    api_client,
    provider,
    exception_type,
    status_code,
    error_code,
):
    provider.get_country.side_effect = exception_type()

    response = await api_client.get("/countries/ZZ")

    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": error_code,
            "message": exception_type.message,
        }
    }

    provider.get_country.assert_awaited_once_with("ZZ")


async def test_does_not_expose_upstream_exception_context(
    api_client,
    provider,
):
    async def fail(code):
        try:
            raise RuntimeError(
                "Authorization: Bearer secret-key; "
                '{"private_upstream_payload": "sensitive"}'
            )
        except RuntimeError:
            raise CountryProviderUnavailable() from None

    provider.get_country.side_effect = fail

    response = await api_client.get("/countries/CA")

    assert response.status_code == 503
    assert "secret-key" not in response.text
    assert "private_upstream_payload" not in response.text
    assert "Traceback" not in response.text
    assert response.json() == {
        "error": {
            "code": "COUNTRY_PROVIDER_UNAVAILABLE",
            "message": CountryProviderUnavailable.message,
        }
    }


def test_openapi_documents_country_response(api_app):
    schema = api_app.openapi()
    operation = schema["paths"]["/countries/{country_code}"]["get"]

    response_schema = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]

    assert response_schema["$ref"] == ("#/components/schemas/CountryResponse")

    country_schema = schema["components"]["schemas"]["CountryResponse"]

    assert set(country_schema["properties"]) == {
        "code",
        "name",
        "currencies",
        "languages",
        "utc_offsets",
    }


def test_openapi_documents_country_error_responses(api_app):
    operation = api_app.openapi()["paths"]["/countries/{country_code}"]["get"]

    assert {"200", "404", "422", "502", "503", "504"} <= set(operation["responses"])
