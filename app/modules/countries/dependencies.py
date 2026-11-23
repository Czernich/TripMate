from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends

from app.integrations.countries.client import CountryProvider, RestCountriesClient
from app.integrations.countries.config import CountryProviderSettings


def get_country_provider_settings() -> CountryProviderSettings:
    return CountryProviderSettings()


async def get_country_provider(
    settings: Annotated[
        CountryProviderSettings,
        Depends(get_country_provider_settings),
    ],
) -> AsyncIterator[CountryProvider]:
    async with httpx.AsyncClient() as client:
        yield RestCountriesClient(
            client=client,
            settings=settings,
        )
