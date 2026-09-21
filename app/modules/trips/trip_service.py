from app.models.trip import Trip
from app.modules.trips.trip_repository import TripRepository
from app.schemas.trip import TripCreate


class TripService:
    def __init__(self, repository: TripRepository):
        self.repository = repository

    async def create_trip(self, trip: TripCreate) -> Trip:
        try:
            new_trip = await self.repository.create(trip)
        except ValueError as exc:
            raise RuntimeError(f"Can not create the trip: {exc}")
        return new_trip

    async def list_trips(self) -> list[Trip]:
        trips = await self.repository.list()
        if not trips:
            raise ValueError("There are no trips.")
        return trips

    async def get_trip(self, trip_id: int) -> Trip:
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise ValueError(f"Trip with id {trip_id} not found.")
        return trip
