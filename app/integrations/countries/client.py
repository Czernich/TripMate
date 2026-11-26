import re
from typing import Protocol

import httpx
from pydantic import ValidationError

from app.integrations.countries.config import CountryProviderSettings
from app.integrations.countries.exceptions import (
    CountryNotFound,
    CountryProviderAuthenticationError,
    CountryProviderRateLimitExceeded,
    CountryProviderTimeout,
    CountryProviderUnavailable,
    InvalidCountryCode,
    MalformedCountryResponse,
)
from app.integrations.countries.provider_schemas import ProviderResponse
from app.integrations.countries.schemas import Country


class CountryProvider(Protocol):
    async def get_country(self, code: str) -> Country: ...


class RestCountriesClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        settings: CountryProviderSettings,
    ) -> None:
        self._client = client
        self._settings = settings

    async def get_country(self, code: str) -> Country:
        if not isinstance(code, str) or re.fullmatch(r"[A-Za-z]{2}", code) is None:
            raise InvalidCountryCode()

        normalized_code = code.upper()
        base_url = str(self._settings.url).rstrip("/")
        api_key = self._settings.api_key.get_secret_value()

        try:
            response = await self._client.get(
                f"{base_url}/codes.alpha_2/{normalized_code}",
                params={
                    "response_fields": (
                        "codes.alpha_2,names.common,currencies,languages,timezones"
                    ),
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
                timeout=self._settings.timeout,
                follow_redirects=False,
            )
        except httpx.TimeoutException:
            raise CountryProviderTimeout() from None
        except httpx.RequestError:
            raise CountryProviderUnavailable() from None

        match response.status_code:
            case 200:
                return self._map_response(response, normalized_code)
            case 401 | 403:
                raise CountryProviderAuthenticationError()
            case 429:
                raise CountryProviderRateLimitExceeded()
            case _:
                raise CountryProviderUnavailable()

    @staticmethod
    def _map_response(
        response: httpx.Response,
        expected_code: str,
    ) -> Country:
        try:
            payload = ProviderResponse.model_validate_json(response.content)

            if "demo" in payload.data.model_fields_set:
                raise MalformedCountryResponse()

            objects = payload.data.objects

            if not objects:
                raise CountryNotFound()

            if len(objects) != 1:
                raise MalformedCountryResponse()

            item = objects[0]

            if item.codes.alpha_2 != expected_code:
                raise MalformedCountryResponse()

            return Country.model_validate(
                {
                    "code": item.codes.alpha_2,
                    "name": item.names.common,
                    "currencies": [
                        currency.model_dump() for currency in item.currencies
                    ],
                    "languages": [
                        {
                            "code": language.bcp47,
                            "name": language.name,
                        }
                        for language in item.languages
                    ],
                    "utc_offsets": item.timezones,
                }
            )

        except ValidationError:
            raise MalformedCountryResponse() from None
