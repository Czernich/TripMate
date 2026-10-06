from fastapi import APIRouter, status

from app.models.trip import Trip
from app.modules.trips.dependencies import TripServiceDep
from app.modules.trips.schemas import TripCreate, TripDetail

router = APIRouter(
    prefix="/trips",
    tags=["trips"],
)


@router.post(
    "",
    response_model=TripDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_trip(
    payload: TripCreate,
    service: TripServiceDep,
) -> Trip:
    trip = Trip(**payload.model_dump())

    return await service.create_trip(trip)
