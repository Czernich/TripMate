from re import fullmatch
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
)


def normalize_email(value: str) -> str:
    return value.strip().lower()


def validate_email(value: str) -> str:
    pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"

    if not fullmatch(pattern, value):
        raise ValueError("Invalid email address")

    return value


def validate_password(value: str) -> str:
    if not any(char.isupper() for char in value):
        raise ValueError("Password must contain an uppercase letter")

    if not any(char.islower() for char in value):
        raise ValueError("Password must contain a lowercase letter")

    if not any(char.isdigit() for char in value):
        raise ValueError("Password must contain a digit")

    return value


NormalizedEmail = Annotated[
    str,
    BeforeValidator(validate_email),
    BeforeValidator(normalize_email),
    Field(max_length=254),
]

TrimmedDisplayName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

ValidatedPassword = Annotated[
    str,
    StringConstraints(min_length=8),
    BeforeValidator(validate_password),
]


class UserBase(BaseModel):
    email: NormalizedEmail
    display_name: TrimmedDisplayName


class UserCreate(UserBase):
    password: ValidatedPassword


class UserDetail(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
