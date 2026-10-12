from pydantic import ValidationError

from app.models.trip import Trip
from app.modules.trips.exceptions import (
    TripAlreadyExistsException,
    TripNotFoundException,
    TripUnprocessableException,
)
from app.modules.trips.repository import TripRepository
from app.modules.trips.schemas import TripBase, TripUpdate


class TripService:
    def __init__(self, repository: TripRepository):
        self.repository = repository

    async def create_trip(self, trip: Trip) -> Trip:
        try:
            return await self.repository.add(trip)

        except TripAlreadyExistsException:
            raise TripAlreadyExistsException()

    async def list_trips(self, limit: int, offset: int) -> list[Trip]:
        return await self.repository.get_trips(
            limit=limit,
            offset=offset,
        )

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

    async def update_trip(
        self,
        trip_id: int,
        payload: TripUpdate,
    ) -> Trip:
        trip = await self.get_trip(trip_id)

        changes = payload.model_dump(exclude_unset=True)

        current_data = {
            "name": trip.name,
            "destination": trip.destination,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
        }

        merged_data = {**current_data, **changes}

        try:
            validated_trip = TripBase.model_validate(merged_data)
        except ValidationError as exc:
            raise TripUnprocessableException(
                message="The resulting trip data is invalid."
            ) from exc

        validated_changes = validated_trip.model_dump(include=set(changes))

        return await self.repository.update(trip, validated_changes)
