import traceback

import httpx
import pytest

from app.integrations.countries.client import RestCountriesClient
from app.integrations.countries.config import CountryProviderSettings
from app.integrations.countries.exceptions import (
    CountryNotFound,
    CountryProviderTimeout,
    CountryProviderUnavailable,
    InvalidCountryCode,
    MalformedCountryResponse,
)


@pytest.fixture
def payload():
    # Syntetyczne dane testowe zgodne z kontraktem dostawcy.
    return {
        "data": {
            "objects": [
                {
                    "codes": {"alpha_2": "CA"},
                    "names": {"common": "Canada"},
                    "currencies": [
                        {
                            "code": "CAD",
                            "name": "Canadian dollar",
                            "symbol": "$",
                            "upstream_extra": "discard",
                        },
                        {
                            "code": "USD",
                            "name": "US dollar",
                        },
                    ],
                    "languages": [
                        {
                            "bcp47": "en",
                            "name": "English",
                            "native_name": "English",
                        },
                        {
                            "bcp47": "fr",
                            "name": "French",
                        },
                    ],
                    "timezones": [
                        "UTC-08:00",
                        "UTC-03:30",
                    ],
                    "population": 40_000_000,
                }
            ]
        }
    }


@pytest.fixture
def settings():
    return CountryProviderSettings(
        url="https://provider.example/countries/v5",
        api_key="test-secret",
        timeout=2.5,
        _env_file=None,
    )


@pytest.mark.asyncio
async def test_maps_response_and_normalizes_code(payload, settings):
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/countries/v5/codes.alpha_2/CA"
        assert request.headers["Authorization"] == "Bearer test-secret"
        assert "test-secret" not in str(request.url)
        assert request.extensions["timeout"]["read"] == 2.5
        assert request.url.params["response_fields"] == (
            "codes.alpha_2,names.common,currencies,languages,timezones"
        )

        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        country = await client.get_country("ca")

    assert country.model_dump() == {
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "code",
    ["", "P", "POL", "P1", " PL", "pl ", "éa", "ſa"],
)
async def test_rejects_invalid_code_before_request(code, settings):
    def handler(request):
        pytest.fail("Invalid country code must not trigger HTTP")

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(InvalidCountryCode):
            await client.get_country(code)


@pytest.mark.asyncio
async def test_unknown_country(settings):
    def handler(request):
        return httpx.Response(
            200,
            json={"data": {"objects": []}},
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(CountryNotFound):
            await client.get_country("ZZ")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code",
    [301, 400, 401, 403, 404, 410, 429, 500, 503],
)
async def test_upstream_failure(status_code, settings):
    def handler(request):
        return httpx.Response(
            status_code,
            text="upstream message containing test-secret",
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(CountryProviderUnavailable) as caught:
            await client.get_country("CA")

    assert "test-secret" not in str(caught.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "http_error,expected_error",
    [
        (httpx.ReadTimeout, CountryProviderTimeout),
        (httpx.ConnectTimeout, CountryProviderTimeout),
        (httpx.ConnectError, CountryProviderUnavailable),
        (httpx.RemoteProtocolError, CountryProviderUnavailable),
    ],
)
async def test_transport_failure_is_safe(
    http_error,
    expected_error,
    settings,
):
    def handler(request):
        raise http_error(
            "upstream error containing test-secret",
            request=request,
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(expected_error) as caught:
            await client.get_country("CA")

    formatted_exception = "".join(traceback.format_exception(caught.value))

    assert "test-secret" not in formatted_exception


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field",
    ["codes", "names", "currencies", "languages", "timezones"],
)
async def test_missing_required_field(payload, settings, field):
    del payload["data"]["objects"][0][field]

    def handler(request):
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(MalformedCountryResponse):
            await client.get_country("CA")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body",
    [
        "not JSON",
        "null",
        "[]",
        "{}",
        '{"data": null}',
        '{"data": {}}',
        '{"data": {"objects": null}}',
        '{"data": {"objects": [null]}}',
    ],
)
async def test_malformed_response(body, settings):
    def handler(request):
        return httpx.Response(200, text=body)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(MalformedCountryResponse):
            await client.get_country("CA")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field,value",
    [
        ("codes", {"alpha_2": "PL"}),
        ("names", {"common": ""}),
        ("currencies", None),
        ("languages", [{"name": "English"}]),
        ("timezones", ["Europe/Warsaw"]),
    ],
)
async def test_invalid_country_fields(payload, settings, field, value):
    payload["data"]["objects"][0][field] = value

    def handler(request):
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(MalformedCountryResponse):
            await client.get_country("CA")


@pytest.mark.asyncio
async def test_rejects_multiple_results(payload, settings):
    payload["data"]["objects"].append(payload["data"]["objects"][0].copy())

    def handler(request):
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(MalformedCountryResponse):
            await client.get_country("CA")


@pytest.mark.asyncio
async def test_rejects_demo_response(payload, settings):
    payload["data"]["_demo"] = {"message": "Example response"}

    def handler(request):
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(MalformedCountryResponse):
            await client.get_country("CA")


@pytest.mark.asyncio
async def test_does_not_follow_redirects(settings):
    requests = []

    def handler(request):
        requests.append(request)

        return httpx.Response(
            302,
            headers={"Location": "https://other.example/countries"},
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        follow_redirects=True,
    ) as http:
        client = RestCountriesClient(http, settings)

        with pytest.raises(CountryProviderUnavailable):
            await client.get_country("CA")

    assert len(requests) == 1
