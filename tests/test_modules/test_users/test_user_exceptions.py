from fastapi import status

from app.modules.users.exceptions import (
    UserAlreadyExistsException,
    UserException,
    UserNotFoundException,
)


def test_user_exception():
    exception = UserException()

    assert isinstance(exception, Exception)


def test_user_not_found_exception():
    exception = UserNotFoundException()

    assert exception.status_code == status.HTTP_404_NOT_FOUND
    assert exception.error_code == "USER_NOT_FOUND"
    assert exception.message == "User not found."


def test_user_already_exists_exception():
    exception = UserAlreadyExistsException()

    assert exception.status_code == status.HTTP_409_CONFLICT
    assert exception.error_code == "USER_ALREADY_EXISTS"
    assert exception.message == "User with this email already exists."


def test_user_exceptions_inherit_from_user_exception():
    assert issubclass(UserNotFoundException, UserException)
    assert issubclass(UserAlreadyExistsException, UserException)
