from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

NonEmptyString = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]

CountryCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z]{2}$"),
]

CurrencyCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Z]{3}$"),
]

UtcOffset = Annotated[
    str,
    StringConstraints(
        pattern=r"^UTC(?:[+-](?:0\d|1[0-3]):[0-5]\d|[+-]14:00)?$",
    ),
]


class ReferenceSchema(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )


class Currency(ReferenceSchema):
    code: CurrencyCode
    name: NonEmptyString
    symbol: str | None = None


class Language(ReferenceSchema):
    code: NonEmptyString
    name: NonEmptyString


class Country(ReferenceSchema):
    code: CountryCode
    name: NonEmptyString
    currencies: list[Currency]
    languages: list[Language]
    utc_offsets: list[UtcOffset]
