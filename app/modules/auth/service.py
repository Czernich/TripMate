import asyncio

from app.modules.auth.exceptions import InvalidCredentialsException
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.auth.security import create_access_token, verify_password
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import normalize_email
from app.settings import settings_db


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def login(self, payload: LoginRequest) -> TokenResponse:
        normalized_email = normalize_email(payload.email)
        user = await self.user_repository.get_by_email(normalized_email)

        if user is None or not user.is_active:
            raise InvalidCredentialsException()

        is_valid_password = await asyncio.to_thread(
            verify_password,
            payload.password,
            user.password_hash,
        )
        if not is_valid_password:
            raise InvalidCredentialsException()

        access_token = create_access_token(subject=str(user.id))
        return TokenResponse(
            access_token=access_token,
            expires_in=settings_db.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
