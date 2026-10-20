from app.models.trip import Trip
from app.modules.trips.exceptions import (
    TripAlreadyExistsException,
    TripNotFoundException,
)
from app.modules.trips.repository import TripRepository


class TripService:
    def __init__(self, repository: TripRepository):
        self.repository = repository

    async def create_trip(self, trip: Trip) -> Trip:
        try:
            return await self.repository.add(trip)

        except TripAlreadyExistsException:
            raise TripAlreadyExistsException()

    async def list_trips(self) -> list[Trip]:
        return await self.repository.get_all()

    async def get_trip(self, trip_id: int) -> Trip:
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException(
                message=f"Trip with id {trip_id} was not found."
            )
        return trip

    async def delete_trip(self, trip_id: int) -> None:
        trip = await self.get_trip(trip_id)
        await self.repository.remove(trip)
