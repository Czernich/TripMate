from collections.abc import Callable

import pytest

from app.models.user import User


@pytest.fixture
def user_factory() -> Callable[..., User]:
    def create_user(
        email="test@gmail.com", password_hash="123aBcD", display_name="Test user"
    ) -> User:
        return User(email=email, password_hash=password_hash, display_name=display_name)

    return create_user
