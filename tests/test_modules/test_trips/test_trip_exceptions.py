import pytest

from app.exceptions import AppBaseException
from app.modules.trips.exceptions import (
    TripAlreadyExistsException,
    TripException,
    TripFullException,
    TripNotFoundException,
    TripUnprocessableException,
)


@pytest.mark.parametrize(
    "exc_class, status_code, error_code, message",
    [
        (TripNotFoundException, 404, "TRIP_NOT_FOUND", "Trip not found."),
        (
            TripAlreadyExistsException,
            409,
            "TRIP_ALREADY_EXISTS",
            "Trip already exists.",
        ),
        (
            TripUnprocessableException,
            422,
            "TRIP_UNPROCESSABLE",
            "The trip cannot be edited in its current state.",
        ),
        (TripFullException, 400, "TRIP_IS_FULL", "Trip is fully booked."),
    ],
)
def test_trip_exception_defaults(exc_class, status_code, error_code, message):
    exc = exc_class()

    assert exc.status_code == status_code
    assert exc.error_code == error_code
    assert exc.message == message
    assert str(exc) == message


def test_trip_exception_accepts_custom_message_and_code():
    exc = TripNotFoundException(message="Trip with id 5 was not found.", error_code="X")

    assert exc.message == "Trip with id 5 was not found."
    assert exc.error_code == "X"
    assert exc.status_code == 404


@pytest.mark.parametrize(
    "exc_class",
    [
        TripNotFoundException,
        TripAlreadyExistsException,
        TripUnprocessableException,
        TripFullException,
    ],
)
def test_trip_exceptions_inherit_from_base(exc_class):
    assert issubclass(exc_class, TripException)
    assert issubclass(exc_class, AppBaseException)
