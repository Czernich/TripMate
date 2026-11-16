import pytest
from pydantic import ValidationError

from app.integrations.countries.schemas import Country


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
            },
        ],
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "fr", "name": "French"},
        ],
        "utc_offsets": [
            "UTC-08:00",
            "UTC-03:30",
        ],
    }


def test_preserves_multiple_reference_values(country_data):
    country = Country.model_validate(country_data)

    assert country.model_dump() == {
        **country_data,
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
    }


@pytest.mark.parametrize(
    "field",
    ["code", "name", "currencies", "languages", "utc_offsets"],
)
def test_rejects_missing_required_field(country_data, field):
    del country_data[field]

    with pytest.raises(ValidationError):
        Country.model_validate(country_data)


@pytest.mark.parametrize(
    "code",
    ["", "P", "POL", "pl", "P1", " PL", "ÉA"],
)
def test_rejects_invalid_internal_country_code(country_data, code):
    country_data["code"] = code

    with pytest.raises(ValidationError):
        Country.model_validate(country_data)


@pytest.mark.parametrize(
    "offset",
    [
        "UTC",
        "UTC+00:00",
        "UTC-12:00",
        "UTC+05:30",
        "UTC+05:45",
        "UTC+14:00",
    ],
)
def test_accepts_utc_offsets(country_data, offset):
    country_data["utc_offsets"] = [offset]

    country = Country.model_validate(country_data)

    assert country.utc_offsets == [offset]


@pytest.mark.parametrize(
    "offset",
    [
        "Europe/Warsaw",
        "+01:00",
        "UTC+5:30",
        "UTC+01:60",
        "UTC+14:30",
        "UTC+15:00",
    ],
)
def test_rejects_invalid_utc_offsets(country_data, offset):
    country_data["utc_offsets"] = [offset]

    with pytest.raises(ValidationError):
        Country.model_validate(country_data)


@pytest.mark.parametrize("name", ["", "   ", None, 123])
def test_rejects_invalid_country_name(country_data, name):
    country_data["name"] = name

    with pytest.raises(ValidationError):
        Country.model_validate(country_data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("currencies", {}),
        ("languages", None),
        ("utc_offsets", "UTC+01:00"),
    ],
)
def test_rejects_invalid_collection_types(country_data, field, value):
    country_data[field] = value

    with pytest.raises(ValidationError):
        Country.model_validate(country_data)


@pytest.mark.parametrize(
    "currency",
    [
        {"code": "pln", "name": "Polish złoty"},
        {"code": "PL", "name": "Polish złoty"},
        {"code": "PLN", "name": " "},
        {"code": "PLN"},
    ],
)
def test_rejects_invalid_currency(country_data, currency):
    country_data["currencies"] = [currency]

    with pytest.raises(ValidationError):
        Country.model_validate(country_data)


@pytest.mark.parametrize(
    "language",
    [
        {"code": "", "name": "Polish"},
        {"code": "pl", "name": " "},
        {"name": "Polish"},
    ],
)
def test_rejects_invalid_language(country_data, language):
    country_data["languages"] = [language]

    with pytest.raises(ValidationError):
        Country.model_validate(country_data)


def test_rejects_fields_outside_internal_contract(country_data):
    country_data["population"] = 40_000_000

    with pytest.raises(ValidationError):
        Country.model_validate(country_data)
