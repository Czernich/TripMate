from fastapi import status

from app.exceptions.base import AppBaseException


class UserException(AppBaseException):
    """Base exception for all user-related errors."""


class UserNotFoundException(UserException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "USER_NOT_FOUND"
    message = "User not found."


class UserAlreadyExistsException(UserException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "USER_ALREADY_EXISTS"
    message = "User with this email already exists."
