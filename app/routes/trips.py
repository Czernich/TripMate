from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.models.trip import Trip
from app.modules.trips.dependencies import get_trip_service
from app.modules.trips.schemas import TripCreate, TripDetail
from app.modules.trips.service import TripService

router = APIRouter(prefix="/trips", tags=["trips"])

TripServiceDep = Annotated[TripService, Depends(get_trip_service)]


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
