from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip
from app.modules.trips.repository import TripRepository


class TripService:
    def __init__(
        self,
        repository: TripRepository,
        session: AsyncSession,
    ) -> None:
        self.repository = repository
        self.session = session

    async def create_trip(self, trip: Trip) -> Trip:
        new_trip = self.repository.add(trip)

        await self.session.flush()
        await self.session.refresh(new_trip)

        return new_trip

    async def list_trips(self) -> list[Trip]:
        return await self.repository.get_all()

    async def get_trip(self, trip_id: int) -> Trip:
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise ValueError(f"Trip with id {trip_id} not found.")
        return trip
