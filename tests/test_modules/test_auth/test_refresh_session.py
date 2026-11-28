from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.refresh_session import RefreshSession
from app.modules.auth.exceptions import InvalidRefreshTokenException
from app.modules.auth.refresh_service import RefreshSessionService
from app.modules.auth.repository import RefreshSessionRepository
from app.modules.auth.security import hash_refresh_token
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService
from tests.factories import UserFactory


async def create_user(
    db_session: AsyncSession,
    *,
    email: str = "refresh@example.com",
    is_active: bool = True,
):
    user = UserFactory.build(email=email, is_active=is_active)
    db_session.add(user)
    await db_session.flush()
    return user


def build_service(db_session: AsyncSession) -> RefreshSessionService:
    return RefreshSessionService(
        repository=RefreshSessionRepository(db_session),
        user_service=UserService(UserRepository(db_session)),
    )


async def test_issue_and_rotate_lifecycle(db_session: AsyncSession):
    user = await create_user(db_session)
    service = build_service(db_session)

    issued = await service.issue(user.id)
    assert issued.user_id == user.id
    assert isinstance(issued.token, str) and len(issued.token) > 20

    stored = await RefreshSessionRepository(db_session).get_by_token_hash(
        hash_refresh_token(issued.token)
    )
    assert stored is not None
    assert stored.token_hash != issued.token
    assert stored.consumed_at is None
    assert stored.revoked_at is None

    rotated = await service.rotate(issued.token)
    assert rotated.token != issued.token
    assert rotated.family_id == issued.family_id
    assert rotated.family_expires_at == issued.family_expires_at

    await db_session.refresh(stored)
    assert stored.consumed_at is not None


async def test_replay_revokes_family_but_keeps_other_sessions_valid(
    db_session: AsyncSession,
):
    user = await create_user(db_session)
    service = build_service(db_session)

    session_a = await service.issue(user.id)
    session_b = await service.issue(user.id)

    rotated_a = await service.rotate(session_a.token)

    with pytest.raises(InvalidRefreshTokenException):
        await service.rotate(session_a.token)

    with pytest.raises(InvalidRefreshTokenException):
        await service.rotate(rotated_a.token)

    rotated_b = await service.rotate(session_b.token)
    assert rotated_b.family_id == session_b.family_id


async def test_expired_token_and_expired_family_are_rejected(
    db_session: AsyncSession,
):
    user = await create_user(db_session)
    service = build_service(db_session)
    repo = RefreshSessionRepository(db_session)

    issued = await service.issue(user.id)
    stored = await repo.get_by_token_hash(hash_refresh_token(issued.token))
    assert stored is not None

    stored.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db_session.flush()
    with pytest.raises(InvalidRefreshTokenException):
        await service.rotate(issued.token)

    issued_2 = await service.issue(user.id)
    stored_2 = await repo.get_by_token_hash(hash_refresh_token(issued_2.token))
    assert stored_2 is not None
    stored_2.family_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db_session.flush()
    with pytest.raises(InvalidRefreshTokenException):
        await service.rotate(issued_2.token)


async def test_concurrent_consume_allows_only_one_winner(db_session: AsyncSession):
    user = await create_user(db_session)
    service = build_service(db_session)
    repo = RefreshSessionRepository(db_session)

    issued = await service.issue(user.id)
    stored = await repo.get_by_token_hash(hash_refresh_token(issued.token))
    assert stored is not None

    now = datetime.now(timezone.utc)
    first = await repo.consume_if_active(stored.id, now)
    second = await repo.consume_if_active(stored.id, now)

    assert first is not None
    assert second is None


async def test_failed_replacement_write_rolls_back_consumption(
    db_session: AsyncSession,
):
    user = await create_user(db_session)
    repo = RefreshSessionRepository(db_session)
    service = RefreshSessionService(
        repository=repo,
        user_service=UserService(UserRepository(db_session)),
    )

    issued = await service.issue(user.id)
    await db_session.flush()

    repo.add = AsyncMock(side_effect=RuntimeError("db write failed"))  # type: ignore[method-assign]
    with pytest.raises(RuntimeError, match="db write failed"):
        async with db_session.begin_nested():
            await service.rotate(issued.token)

    result = await db_session.execute(
        select(RefreshSession).where(
            RefreshSession.token_hash == hash_refresh_token(issued.token)
        )
    )
    stored = result.scalar_one_or_none()
    assert stored is not None
    assert stored.consumed_at is None


async def test_revoke_family_is_idempotent_and_inactive_user_rejected(
    db_session: AsyncSession,
):
    active_user = await create_user(db_session, email="active@example.com")
    inactive_user = await create_user(
        db_session, email="inactive@example.com", is_active=False
    )
    service = build_service(db_session)

    issued = await service.issue(active_user.id)
    await service.revoke_family(issued.family_id)
    await service.revoke_family(issued.family_id)

    with pytest.raises(InvalidRefreshTokenException):
        await service.rotate(issued.token)

    with pytest.raises(InvalidRefreshTokenException):
        await service.issue(inactive_user.id)

    with pytest.raises(InvalidRefreshTokenException):
        await service.issue(999999)


async def test_get_db_commits_on_invalid_refresh_token_exception(monkeypatch):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    monkeypatch.setattr("app.database.SessionLocal", lambda: mock_session)

    with pytest.raises(InvalidRefreshTokenException):
        async with asynccontextmanager(get_db)():
            raise InvalidRefreshTokenException()

    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_not_awaited()
