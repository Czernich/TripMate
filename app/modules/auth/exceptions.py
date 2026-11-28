from typing import ClassVar

from fastapi import status

from app.exceptions.base import AppBaseException


class InvalidCredentialsException(AppBaseException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    error_code: str = "INVALID_CREDENTIALS"
    message: str = "Invalid email or password."
    headers: ClassVar[dict[str, str] | None] = {"WWW-Authenticate": "Bearer"}


class InvalidRefreshTokenException(AppBaseException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    error_code: str = "INVALID_REFRESH_TOKEN"
    message: str = "Invalid or expired refresh token."
    headers: ClassVar[dict[str, str] | None] = {"WWW-Authenticate": "Bearer"}
    commit_on_error: ClassVar[bool] = True
