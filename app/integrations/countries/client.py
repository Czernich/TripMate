import re
from typing import Protocol

import httpx
from pydantic import ValidationError

from app.integrations.countries.config import CountryProviderSettings
from app.integrations.countries.exceptions import (
    CountryNotFound,
    CountryProviderTimeout,
    CountryProviderUnavailable,
    InvalidCountryCode,
    MalformedCountryResponse,
)
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

        if response.status_code != 200:
            raise CountryProviderUnavailable()

        return self._map_response(response, normalized_code)

    @staticmethod
    def _map_response(
        response: httpx.Response,
        expected_code: str,
    ) -> Country:
        try:
            payload = response.json()
            data = payload["data"]

            # Klucz demonstracyjny zwraca przykładowy kraj.
            if "_demo" in data:
                raise MalformedCountryResponse()

            objects = data["objects"]

            if not isinstance(objects, list):
                raise MalformedCountryResponse()

            if not objects:
                raise CountryNotFound()

            if len(objects) != 1:
                raise MalformedCountryResponse()

            item = objects[0]

            country = Country.model_validate(
                {
                    "code": item["codes"]["alpha_2"],
                    "name": item["names"]["common"],
                    "currencies": [
                        {
                            "code": currency["code"],
                            "name": currency["name"],
                            "symbol": currency.get("symbol"),
                        }
                        for currency in item["currencies"]
                    ],
                    "languages": [
                        {
                            "code": language["bcp47"],
                            "name": language["name"],
                        }
                        for language in item["languages"]
                    ],
                    "utc_offsets": item["timezones"],
                }
            )

            if country.code != expected_code:
                raise MalformedCountryResponse()

            return country

        except (
            KeyError,
            TypeError,
            AttributeError,
            ValueError,
            ValidationError,
        ):
            raise MalformedCountryResponse() from None
