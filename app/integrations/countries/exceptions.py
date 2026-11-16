from app.exceptions.base import AppBaseException


class CountryReferenceError(AppBaseException):
    error_code = "COUNTRY_REFERENCE_ERROR"
    message = "Country reference lookup failed."


class InvalidCountryCode(CountryReferenceError):
    status_code = 422
    error_code = "INVALID_COUNTRY_CODE"
    message = "Country code must contain exactly two ASCII letters."


class CountryNotFound(CountryReferenceError):
    status_code = 404
    error_code = "COUNTRY_NOT_FOUND"
    message = "Country was not found."


class CountryProviderTimeout(CountryReferenceError):
    status_code = 504
    error_code = "COUNTRY_PROVIDER_TIMEOUT"
    message = "Country provider timed out."


class CountryProviderUnavailable(CountryReferenceError):
    status_code = 503
    error_code = "COUNTRY_PROVIDER_UNAVAILABLE"
    message = "Country provider is unavailable."


class MalformedCountryResponse(CountryReferenceError):
    status_code = 502
    error_code = "MALFORMED_COUNTRY_RESPONSE"
    message = "Country provider returned an invalid response."
