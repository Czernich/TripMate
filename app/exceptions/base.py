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


class DatabaseUnavailableException(AppBaseException):
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code: str = "SERVICE_UNAVAILABLE"
    message: str = "Database is currently unavailable. Please try again later."
