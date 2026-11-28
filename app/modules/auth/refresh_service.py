from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.refresh_session import RefreshSession
from app.modules.auth.exceptions import InvalidRefreshTokenException
from app.modules.auth.repository import RefreshSessionRepository
from app.modules.auth.security import generate_refresh_token, hash_refresh_token
from app.modules.users.exceptions import UserNotFoundException
from app.modules.users.service import UserService
from app.settings import settings_db


@dataclass(frozen=True)
class IssuedRefreshToken:
    token: str
    family_id: str
    user_id: int
    expires_at: datetime
    family_expires_at: datetime


class RefreshSessionService:
    def __init__(
        self,
        repository: RefreshSessionRepository,
        user_service: UserService,
    ):
        self.repository = repository
        self.user_service = user_service

    async def require_active_user(self, user_id: int) -> None:
        try:
            user = await self.user_service.get_user_by_id(user_id)
        except UserNotFoundException as exc:
            raise InvalidRefreshTokenException() from exc

        if not user.is_active:
            raise InvalidRefreshTokenException()

    async def issue(self, user_id: int) -> IssuedRefreshToken:
        await self.require_active_user(user_id)

        now = datetime.now(timezone.utc)
        family_expires_at = now + timedelta(
            days=settings_db.REFRESH_SESSION_ABSOLUTE_EXPIRE_DAYS
        )
        expires_at = min(
            now + timedelta(days=settings_db.REFRESH_TOKEN_EXPIRE_DAYS),
            family_expires_at,
        )
        raw_token = generate_refresh_token()
        family_id = str(uuid4())

        refresh_session = RefreshSession(
            user_id=user_id,
            family_id=family_id,
            token_hash=hash_refresh_token(raw_token),
            issued_at=now,
            expires_at=expires_at,
            family_expires_at=family_expires_at,
        )
        await self.repository.add(refresh_session)

        return IssuedRefreshToken(
            token=raw_token,
            family_id=family_id,
            user_id=user_id,
            expires_at=expires_at,
            family_expires_at=family_expires_at,
        )

    async def rotate(self, raw_token: str) -> IssuedRefreshToken:
        now = datetime.now(timezone.utc)
        current = await self.repository.get_by_token_hash(hash_refresh_token(raw_token))

        if current is None:
            raise InvalidRefreshTokenException()

        if current.consumed_at is not None:
            await self.repository.revoke_family(current.family_id, now)
            raise InvalidRefreshTokenException()

        if (
            current.revoked_at is not None
            or current.expires_at <= now
            or current.family_expires_at <= now
        ):
            raise InvalidRefreshTokenException()

        await self.require_active_user(current.user_id)

        consumed = await self.repository.consume_if_active(current.id, now)
        if consumed is None:
            await self.repository.revoke_family(current.family_id, now)
            raise InvalidRefreshTokenException()

        new_raw_token = generate_refresh_token()
        new_expires_at = min(
            now + timedelta(days=settings_db.REFRESH_TOKEN_EXPIRE_DAYS),
            current.family_expires_at,
        )
        replacement = RefreshSession(
            user_id=current.user_id,
            family_id=current.family_id,
            token_hash=hash_refresh_token(new_raw_token),
            issued_at=now,
            expires_at=new_expires_at,
            family_expires_at=current.family_expires_at,
        )
        await self.repository.add(replacement)

        return IssuedRefreshToken(
            token=new_raw_token,
            family_id=current.family_id,
            user_id=current.user_id,
            expires_at=new_expires_at,
            family_expires_at=current.family_expires_at,
        )

    async def revoke_family(self, family_id: str) -> None:
        await self.repository.revoke_family(family_id, datetime.now(timezone.utc))
