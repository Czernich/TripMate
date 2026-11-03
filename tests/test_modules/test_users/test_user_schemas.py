import pytest
from pydantic import ValidationError

from app.modules.users.schemas import (
    UserCreate,
)


def test_user_create_valid_data():
    user = UserCreate(
        email="john@example.com",
        display_name="John",
        password="Password123",
    )

    assert user.email == "john@example.com"
    assert user.display_name == "John"
    assert user.password == "Password123"


def test_email_is_trimmed_and_lowercased():
    user = UserCreate(
        email="  JOHN@EXAMPLE.COM  ",
        display_name="John",
        password="Password123",
    )

    assert user.email == "john@example.com"


@pytest.mark.parametrize(
    "email",
    [
        "invalid-email",
        "john@",
        "@example.com",
        "john@example",
        "john example@example.com",
    ],
)
def test_invalid_email(email):
    with pytest.raises(ValidationError):
        UserCreate(
            email=email,
            display_name="John",
            password="Password123",
        )


def test_email_max_length():
    with pytest.raises(ValidationError):
        UserCreate(
            email=f"{'a' * 245}@example.com",
            display_name="John",
            password="Password123",
        )


def test_display_name_is_trimmed():
    user = UserCreate(
        email="john@example.com",
        display_name="  John  ",
        password="Password123",
    )

    assert user.display_name == "John"


@pytest.mark.parametrize(
    "display_name",
    [
        "",
        "   ",
        "a" * 101,
    ],
)
def test_invalid_display_name(display_name):
    with pytest.raises(ValidationError):
        UserCreate(
            email="john@example.com",
            display_name=display_name,
            password="Password123",
        )


@pytest.mark.parametrize(
    "password",
    [
        "short1A",
        "password123",
        "PASSWORD123",
        "Password",
    ],
)
def test_invalid_password(password):
    with pytest.raises(ValidationError):
        UserCreate(
            email="john@example.com",
            display_name="John",
            password=password,
        )
