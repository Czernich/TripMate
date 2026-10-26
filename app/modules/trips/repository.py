from sqlalchemy import func, select
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
        result = await self.session.execute(
            select(Trip).where(Trip.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    async def get_by_id(self, trip_id: int) -> Trip | None:
        result = await self.session.execute(
            select(Trip).where(Trip.id == trip_id, Trip.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    from datetime import date

    async def update(
        self,
        trip: Trip,
        changes: dict[str, str | date],
    ) -> Trip:
        for field_name, value in changes.items():
            setattr(trip, field_name, value)

        await self.session.flush()
        await self.session.refresh(trip)

        return trip
