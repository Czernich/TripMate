from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.integrations.countries.client import CountryProvider
from app.modules.countries.dependencies import get_country_provider
from app.modules.countries.schemas import CountryResponse

router = APIRouter(
    prefix="/countries",
    tags=["countries"],
)


@router.get(
    "/{country_code}",
    response_model=CountryResponse,
    summary="Get country reference information",
    description=(
        "Returns normalized country information for an ISO 3166-1 "
        "alpha-2 code. Codes are case-insensitive. "
        "Trip membership is not required. "
        "UTC offsets are not IANA timezone identifiers."
    ),
    responses={
        404: {"description": "Country was not found."},
        422: {"description": "Invalid country-code format."},
        502: {
            "description": (
                "Country provider returned a malformed response "
                "or authentication failed."
            )
        },
        503: {
            "description": (
                "Country provider is unavailable or its rate limit was reached."
            )
        },
        504: {"description": "Country provider timed out."},
    },
)
async def get_country(
    country_code: Annotated[
        str,
        Path(
            min_length=2,
            max_length=2,
            pattern=r"^[A-Za-z]{2}$",
            description=(
                "ISO 3166-1 alpha-2 country code. "
                "Lowercase and mixed-case codes are accepted."
            ),
            examples=["PL"],
        ),
    ],
    provider: Annotated[
        CountryProvider,
        Depends(get_country_provider),
    ],
) -> CountryResponse:
    country = await provider.get_country(country_code.upper())

    return CountryResponse.model_validate(country)
