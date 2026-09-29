from fastapi import status

from app.exceptions import AppBaseException


class TripException(AppBaseException):
    """Base exception for all trip-related errors."""


class TripNotFoundException(TripException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "TRIP_NOT_FOUND"
    message = "Trip not found."


class TripAlreadyExistsException(TripException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "TRIP_ALREADY_EXISTS"
    message = "Trip already exists."


class TripUnprocessableException(TripException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "TRIP_UNPROCESSABLE"
    message = "The trip cannot be edited in its current state."


class TripFullException(TripException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "TRIP_IS_FULL"
    message = "Trip is fully booked."
