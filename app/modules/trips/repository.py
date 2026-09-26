from app.modules.trips.models import Trip
from app.modules.trips.schemas import TripCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TripRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, trip: TripCreate) -> Trip:
        db_trip = Trip(**trip.model_dump())
        self.session.add(db_trip)
        await self.session.commit()
        await self.session.refresh(db_trip)
        return db_trip

    async def list(self) -> list[Trip]:
        result = await self.session.execute(select(Trip))
        return list(result.scalars().all())

    async def get_by_id(self, trip_id: int) -> Trip | None:
        result = await self.session.execute(select(Trip).filter(Trip.id == trip_id))
        return result.scalars().first()
