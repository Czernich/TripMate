# Country reference integration

## Purpose

The integration retrieves reference information for one country by its
ISO 3166-1 alpha-2 code.

It does not provide HTTP endpoints, caching, country search or listing,
database persistence, or automatic assignment to trips.

## Provider

Selected provider: REST Countries, Countries API v5.

Default base URL:

https://api.restcountries.com/countries/v5

Lookup endpoint:

GET /codes.alpha_2/{code}

Authentication uses an API key sent in the Authorization header:

Authorization: Bearer <API_KEY>

The integration requests only:

- codes.alpha_2
- names.common
- currencies
- languages
- timezones

Provider documentation:

https://restcountries.com/docs/countries

## Access terms

Terms reviewed on 2026-11-16:

https://restcountries.com/legal/terms-of-service

REST Countries permits using API responses inside an application.
Relevant restrictions for TripMate include:

- Publicly displayed provider data requires attribution to REST Countries
  with a link to https://restcountries.com.
- Responses must not be retained for more than three days.
- Reselling or redistributing the dataset is restricted.
- The integration must comply with the account's request quota and rate limits.

This implementation does not cache or persist responses.

Before introducing persistence, public display, exports, or additional
data-sharing features, review the current terms against the planned use.

The hosted API's access terms apply independently of any license covering
the provider's source code.

## Configuration

| Environment variable | Required | Default |
| --- | --- | --- |
| COUNTRY_PROVIDER_URL | No | https://api.restcountries.com/countries/v5 |
| COUNTRY_PROVIDER_API_KEY | Yes | None |
| COUNTRY_PROVIDER_TIMEOUT | No | 5 seconds |

The URL must use HTTPS and must not contain credentials, query parameters,
or a fragment.

The timeout must be a positive, finite number. It configures HTTPX's
connect, read, write, and pool timeouts; it is not an overall deadline
for the entire operation.

The API key is represented by Pydantic SecretStr and is sent only in
the Authorization header. Never commit the real key.

Settings are loaded explicitly when CountryProviderSettings is instantiated.
Importing the integration does not require provider credentials.

## Input validation

Input must contain exactly two ASCII letters.

Lowercase and mixed-case codes are normalized to uppercase:

- pl -> PL
- pL -> PL

Whitespace, digits, non-ASCII letters, and codes of other lengths are rejected
before an HTTP request.

Format validation does not establish that a code is assigned to a country.
A valid-format code without a provider result produces CountryNotFound.

## Internal schema

The client returns a Country model containing only:

- code: uppercase ISO 3166-1 alpha-2 code
- name: common country name
- currencies: a list of currency codes, names, and optional symbols
- languages: a list of BCP 47 tags and language names
- utc_offsets: a list of UTC-offset strings

All currency, language, and offset entries are preserved.
Additional upstream fields are discarded during explicit mapping.

Required fields must be present. Empty collections are allowed.
Invalid required values produce MalformedCountryResponse.

## Timezone representation

The provider's timezones field contains UTC offsets, for example:

- UTC+01:00
- UTC+05:30
- UTC-03:30

TripMate exposes these values as utc_offsets.

These values are not IANA timezone identifiers such as Europe/Warsaw.
They do not contain daylight-saving transition rules and must not be used
alone to calculate a trip's local time for an arbitrary date.

## Error handling

| Exception | Meaning |
| --- | --- |
| InvalidCountryCode | Input does not contain exactly two ASCII letters |
| CountryNotFound | Provider returned an empty result list |
| CountryProviderTimeout | HTTPX reported a timeout |
| CountryProviderUnavailable | Transport failure or a non-200 response |
| MalformedCountryResponse | Invalid JSON, unexpected structure, missing or invalid fields, multiple results, or mismatched country code |

In API v5, HTTP 404 indicates an invalid endpoint or property and is treated
as a provider failure rather than an unknown country.

Demo responses are rejected because they return example data rather than
a reliable result for the requested code.

Errors use fixed messages. Raw upstream exception messages, response bodies,
and credentials are not included in integration error messages.

Redirects are disabled. The integration does not retry requests automatically.

## Usage

The caller owns the HTTP client and must close it.

```python
import httpx

from app.integrations.countries.client import RestCountriesClient
from app.integrations.countries.config import CountryProviderSettings


async def lookup_country():
    settings = CountryProviderSettings()

    async with httpx.AsyncClient() as http:
        provider = RestCountriesClient(
            client=http,
            settings=settings,
        )

        return await provider.get_country("pl")
```

For repeated lookups, reuse an AsyncClient within its owning application's
lifecycle rather than creating a new client for every request.

CountryProvider defines the interface that application code can depend on
when a replaceable provider is needed.
