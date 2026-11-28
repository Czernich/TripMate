from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_session import RefreshSession


class RefreshSessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, refresh_session: RefreshSession) -> RefreshSession:
        self.session.add(refresh_session)
        await self.session.flush()
        return refresh_session

    async def get_by_token_hash(self, token_hash: str) -> RefreshSession | None:
        result = await self.session.execute(
            select(RefreshSession).where(RefreshSession.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def consume_if_active(
        self,
        session_id: int,
        consumed_at: datetime,
    ) -> RefreshSession | None:
        result = await self.session.execute(
            update(RefreshSession)
            .where(
                RefreshSession.id == session_id,
                RefreshSession.consumed_at.is_(None),
                RefreshSession.revoked_at.is_(None),
            )
            .values(consumed_at=consumed_at)
            .returning(RefreshSession)
        )
        return result.scalar_one_or_none()

    async def revoke_family(self, family_id: str, revoked_at: datetime) -> int:
        result = await self.session.execute(
            update(RefreshSession)
            .where(
                RefreshSession.family_id == family_id,
                RefreshSession.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )
        return int(result.rowcount or 0)  # type: ignore[attr-defined]
