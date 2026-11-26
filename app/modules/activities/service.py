from app.models.activity import Activity
from app.modules.activities.exceptions import ActivityDateOutOfRangeException
from app.modules.activities.repository import ActivityRepository
from app.modules.activities.schemas import ActivityCreate
from app.modules.trips.exceptions import TripNotFoundException
from app.modules.trips.repository import TripRepository


class ActivityService:
    def __init__(
        self,
        repository: ActivityRepository,
        trip_repository: TripRepository,
    ):
        self.repository = repository
        self.trip_repository = trip_repository

    async def create_activity(
        self,
        trip_id: int,
        payload: ActivityCreate,
    ) -> Activity:
        trip = await self.trip_repository.get_by_id(trip_id)
        if trip is None:
            raise TripNotFoundException(
                message=f"Trip with id {trip_id} was not found."
            )

        if not trip.start_date <= payload.activity_date <= trip.end_date:
            raise ActivityDateOutOfRangeException(
                message=(
                    f"Activity date {payload.activity_date.isoformat()} is outside "
                    f"the trip dates {trip.start_date.isoformat()} - "
                    f"{trip.end_date.isoformat()}."
                )
            )

        activity = Activity(trip_id=trip.id, **payload.model_dump())
        return await self.repository.add(activity)
