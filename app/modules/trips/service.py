from app.models.trip import Trip
from app.modules.trips.repository import TripRepository
from app.exceptions import TripNotFoundException, TripAlreadyExistsException


class TripService:
    def __init__(self, repository: TripRepository):
        self.repository = repository

    def create_trip(self, trip: Trip) -> Trip:
        try:
            new_trip = self.repository.add(trip)
        except TripAlreadyExistsException:
            raise
        return new_trip

    async def list_trips(self) -> list[Trip]:
        return await self.repository.get_all()

    async def get_trip(self, trip_id: int) -> Trip:
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException()
        return trip
