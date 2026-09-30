from app.models.trip import Trip
from app.modules.trips.repository import TripRepository


class TripService:
    def __init__(self, repository: TripRepository):
        self.repository = repository

    async def create_trip(self, trip: Trip) -> Trip:
        try:
            new_trip = self.repository.add(trip)

            await self.repository.flush()
            await self.repository.commit()
            await self.repository.refresh(new_trip)

            return new_trip
        except Exception:
            await self.repository.rollback()
            raise

    async def list_trips(self) -> list[Trip]:
        return await self.repository.get_all()

    async def get_trip(self, trip_id: int) -> Trip:
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise ValueError(f"Trip with id {trip_id} not found.")
        return trip
