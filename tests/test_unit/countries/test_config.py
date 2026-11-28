import pytest
from pydantic import ValidationError

from app.integrations.countries.config import CountryProviderSettings


@pytest.fixture(autouse=True)
def clear_provider_environment(monkeypatch):
    for name in (
        "COUNTRY_PROVIDER_URL",
        "COUNTRY_PROVIDER_API_KEY",
        "COUNTRY_PROVIDER_TIMEOUT",
    ):
        monkeypatch.delenv(name, raising=False)


def test_default_configuration():
    settings = CountryProviderSettings(
        api_key="test-secret",
        _env_file=None,
    )

    assert str(settings.url) == ("https://api.restcountries.com/countries/v5")
    assert settings.timeout == 5.0
    assert settings.api_key.get_secret_value() == "test-secret"


def test_reads_configuration_from_environment(monkeypatch):
    monkeypatch.setenv(
        "COUNTRY_PROVIDER_URL",
        "https://provider.example/countries/v5",
    )
    monkeypatch.setenv("COUNTRY_PROVIDER_API_KEY", "environment-secret")
    monkeypatch.setenv("COUNTRY_PROVIDER_TIMEOUT", "2.5")

    settings = CountryProviderSettings(_env_file=None)

    assert str(settings.url) == ("https://provider.example/countries/v5")
    assert settings.api_key.get_secret_value() == "environment-secret"
    assert settings.timeout == 2.5


def test_reads_configuration_from_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "COUNTRY_PROVIDER_API_KEY=file-secret\n"
        "COUNTRY_PROVIDER_TIMEOUT=3\n"
        "POSTGRES_USER=tripmate\n",
        encoding="utf-8",
    )

    settings = CountryProviderSettings(_env_file=env_file)

    assert settings.api_key.get_secret_value() == "file-secret"
    assert settings.timeout == 3.0


def test_api_key_is_required():
    with pytest.raises(ValidationError):
        CountryProviderSettings(_env_file=None)


@pytest.mark.parametrize(
    "api_key",
    ["", "   ", "key with spaces", "key\nvalue", "key\tvalue"],
)
def test_rejects_invalid_api_key(api_key):
    with pytest.raises(ValidationError):
        CountryProviderSettings(
            api_key=api_key,
            _env_file=None,
        )


@pytest.mark.parametrize(
    "timeout",
    [0, -1, float("inf"), float("-inf"), float("nan"), "invalid"],
)
def test_rejects_invalid_timeout(timeout):
    with pytest.raises(ValidationError):
        CountryProviderSettings(
            api_key="test-secret",
            timeout=timeout,
            _env_file=None,
        )


@pytest.mark.parametrize(
    "url",
    [
        "not-a-url",
        "http://provider.example/countries/v5",
        "https://user:password@provider.example/countries/v5",
        "https://provider.example/countries/v5?api-key=secret",
        "https://provider.example/countries/v5#fragment",
    ],
)
def test_rejects_invalid_or_unsafe_url(url):
    with pytest.raises(ValidationError):
        CountryProviderSettings(
            url=url,
            api_key="test-secret",
            _env_file=None,
        )


def test_masks_api_key_in_standard_representations():
    settings = CountryProviderSettings(
        api_key="test-secret",
        _env_file=None,
    )

    assert "test-secret" not in repr(settings)
    assert "test-secret" not in str(settings)
    assert "test-secret" not in settings.model_dump_json()
