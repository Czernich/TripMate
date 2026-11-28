from datetime import timedelta

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.security import create_access_token
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate
from app.modules.users.service import UserService
from app.settings import settings_db


async def create_user(
    db_session: AsyncSession,
    *,
    email: str = "user@example.com",
    password: str = "StrongPass123!",
    is_active: bool = True,
):
    service = UserService(UserRepository(db_session))
    user = await service.create_user(
        UserCreate(
            email=email,
            display_name="Test User",
            password=password,
        )
    )
    if not is_active:
        user.is_active = False
        await db_session.flush()
    return user


async def test_login_success_and_token_claims(
    client: AsyncClient,
    db_session: AsyncSession,
    override_get_db,
):
    user = await create_user(db_session, email="user@example.com")

    response = await client.post(
        "/auth/login",
        json={"email": "  USER@Example.COM ", "password": "StrongPass123!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == settings_db.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    assert isinstance(body["access_token"], str)

    payload = jwt.decode(
        body["access_token"],
        settings_db.JWT_SECRET_KEY,
        algorithms=[settings_db.JWT_ALGORITHM],
    )
    assert payload["sub"] == str(user.id)
    assert isinstance(payload["iat"], int)
    assert isinstance(payload["exp"], int)
    assert payload["exp"] > payload["iat"]


async def test_login_invalid_email_password_and_inactive_user_return_identical_401(
    client: AsyncClient,
    db_session: AsyncSession,
    override_get_db,
):
    await create_user(db_session, email="active@example.com", is_active=True)
    await create_user(db_session, email="inactive@example.com", is_active=False)

    responses = [
        await client.post(
            "/auth/login",
            json={"email": "unknown@example.com", "password": "StrongPass123!"},
        ),
        await client.post(
            "/auth/login",
            json={"email": "active@example.com", "password": "WrongPassword!"},
        ),
        await client.post(
            "/auth/login",
            json={"email": "inactive@example.com", "password": "StrongPass123!"},
        ),
    ]

    expected_body = {
        "error": {
            "code": "INVALID_CREDENTIALS",
            "message": "Invalid email or password.",
        }
    }

    for resp in responses:
        assert resp.status_code == 401
        assert resp.headers.get("www-authenticate") == "Bearer"
        assert resp.json() == expected_body


async def test_login_validation_error(client: AsyncClient):
    response = await client.post("/auth/login", json={"email": "not-an-email"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_expired_access_token_is_rejected():
    token = create_access_token("123", expires_delta=timedelta(seconds=-1))

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            token,
            settings_db.JWT_SECRET_KEY,
            algorithms=[settings_db.JWT_ALGORITHM],
        )
