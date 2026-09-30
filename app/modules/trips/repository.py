from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip


class TripRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, trip: Trip) -> Trip:
        self.session.add(trip)
        return trip

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def refresh(self, trip: Trip) -> None:
        await self.session.refresh(trip)

    async def get_all(self) -> list[Trip]:
        result = await self.session.execute(select(Trip))
        return list(result.scalars().all())

    async def get_by_id(self, trip_id: int) -> Trip | None:
        return await self.session.get(Trip, trip_id)
