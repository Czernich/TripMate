from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip


class TripRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, trip: Trip) -> Trip:
        self.session.add(trip)
        await self.session.flush()
        await self.session.refresh(trip)
        return trip

    async def get_all(self) -> list[Trip]:
        result = await self.session.execute(select(Trip))
        return list(result.scalars().all())

    async def get_by_id(self, trip_id: int) -> Trip | None:
        return await self.session.get(Trip, trip_id)
