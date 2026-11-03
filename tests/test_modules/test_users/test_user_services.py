import hashlib

import pytest

from app.modules.users.exceptions import UserNotFoundException
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate
from app.modules.users.service import UserService


@pytest.fixture
def user_service(db_session):
    repository = UserRepository(db_session)
    return UserService(repository)


@pytest.mark.asyncio
async def test_create_user(user_service):
    payload = UserCreate(
        email="test@example.com",
        display_name="Test",
        password="Password123",
    )

    user = await user_service.create_user(payload)

    assert user.email == payload.email
    assert user.display_name == payload.display_name
    assert user.password_hash != payload.password


def test_hash_password():
    password = "Password123"

    result = UserService._hash_password(password)

    _, n, r, p, salt, actual_hash = result.split("$")

    expected_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt),
        n=int(n),
        r=int(r),
        p=int(p),
        dklen=64,
    )

    assert actual_hash == expected_hash.hex()


@pytest.mark.asyncio
async def test_get_user_by_id(user_service):
    created_user = await user_service.create_user(
        UserCreate(
            email="test@example.com",
            display_name="Test",
            password="Password123",
        )
    )

    user = await user_service.get_user_by_id(created_user.id)

    assert user.id == created_user.id
    assert user.email == created_user.email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service):
    with pytest.raises(UserNotFoundException):
        await user_service.get_user_by_id(999999)


@pytest.mark.asyncio
async def test_get_user_by_email(user_service):
    payload = UserCreate(
        email="test@example.com",
        display_name="Test",
        password="Password123",
    )
    created_user = await user_service.create_user(payload)

    user = await user_service.get_user_by_email(payload.email)

    assert user.email == payload.email
    assert user.display_name == payload.display_name
    assert user.password_hash == created_user.password_hash


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(user_service):
    with pytest.raises(UserNotFoundException):
        await user_service.get_user_by_email("missing@example.com")
