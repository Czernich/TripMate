from pydantic import Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CountryProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="COUNTRY_PROVIDER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: HttpUrl = HttpUrl("https://api.restcountries.com/countries/v5")
    api_key: SecretStr = Field(min_length=1)
    timeout: float = Field(
        default=5.0,
        gt=0,
        allow_inf_nan=False,
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: HttpUrl) -> HttpUrl:
        if (
            value.scheme != "https"
            or value.username is not None
            or value.password is not None
            or value.query is not None
            or value.fragment is not None
        ):
            raise ValueError(
                "Provider URL must use HTTPS without credentials, "
                "query parameters or fragments"
            )

        return value

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: SecretStr) -> SecretStr:
        key = value.get_secret_value()

        if not key.strip() or any(character.isspace() for character in key):
            raise ValueError(
                "Provider API key must be non-empty and contain no whitespace"
            )

        return value
