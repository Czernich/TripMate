from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.integrations.countries.schemas import (
    CountryCode,
    CurrencyCode,
    NonEmptyString,
    UtcOffset,
)


class ProviderSchema(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="ignore",
    )


class ProviderCountryCodes(ProviderSchema):
    alpha_2: CountryCode


class ProviderCountryNames(ProviderSchema):
    common: NonEmptyString


class ProviderCurrency(ProviderSchema):
    code: CurrencyCode
    name: NonEmptyString
    symbol: str | None = None


class ProviderLanguage(ProviderSchema):
    bcp47: NonEmptyString
    name: NonEmptyString


class ProviderCountry(ProviderSchema):
    codes: ProviderCountryCodes
    names: ProviderCountryNames
    currencies: list[ProviderCurrency]
    languages: list[ProviderLanguage]
    timezones: list[UtcOffset]


class ProviderData(ProviderSchema):
    objects: list[ProviderCountry]
    demo: Any = Field(default=None, alias="_demo")


class ProviderResponse(ProviderSchema):
    data: ProviderData
