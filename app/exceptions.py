from fastapi import status


class AppBaseException(Exception):
    """
    The base exception for the entire application.
    All custom exceptions should inherit from it.
    """
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_SERVER_ERROR"
    message: str = "An unexpected server error occurred."

    def __init__(self, message: str | None = None, error_code: str | None = None):
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)



class TripException(AppBaseException):
    """Base exception for all trip-related errors."""
    pass


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