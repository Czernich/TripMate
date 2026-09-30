from typing import Annotated

from fastapi import APIRouter, Path, status

from app.models.trip import Trip
from app.modules.trips.dependencies import SessionService
from app.modules.trips.schemas import TripCreate, TripDetail

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/{trip_id}", response_model=TripDetail, status_code=200)
async def get_trip(
    trip_id: Annotated[int, Path(gt=0)],
    service: SessionService,
) -> Trip:
    return await service.get_trip(trip_id)


@router.post(
    "",
    response_model=TripDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_trip(
    payload: TripCreate,
    service: SessionService,
) -> Trip:
    trip = Trip(**payload.model_dump())
    return await service.create_trip(trip)