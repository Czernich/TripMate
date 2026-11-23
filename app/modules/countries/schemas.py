from pydantic import BaseModel, ConfigDict, Field


class CountryCurrencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    symbol: str | None = None


class CountryLanguageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="BCP 47 language tag.")
    name: str


class CountryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str = Field(
        description="Uppercase ISO 3166-1 alpha-2 country code.",
        examples=["PL"],
    )
    name: str
    currencies: list[CountryCurrencyResponse]
    languages: list[CountryLanguageResponse]
    utc_offsets: list[str] = Field(
        description=(
            "UTC offsets reported by the provider. "
            "These are not IANA timezone identifiers "
            "and do not describe daylight-saving transition rules."
        ),
        examples=[["UTC+01:00"]],
    )
