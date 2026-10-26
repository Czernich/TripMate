from typing import Annotated

from fastapi import APIRouter, Path, status

from app.models.trip import Trip
from app.modules.trips.dependencies import TripServiceDep
from app.modules.trips.schemas import TripCreate, TripDetail, TripUpdate

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


@router.get(
    "/{trip_id}",
    response_model=TripDetail,
    status_code=status.HTTP_200_OK,
)
async def get_trip(
    trip_id: Annotated[int, Path(gt=0)],
    service: TripServiceDep,
) -> Trip:
    return await service.get_trip(trip_id)


@router.patch(
    "/{trip_id}",
    response_model=TripDetail,
    status_code=status.HTTP_200_OK,
)
async def update_trip(
    trip_id: Annotated[int, Path(gt=0)],
    payload: TripUpdate,
    service: TripServiceDep,
) -> Trip:
    return await service.update_trip(trip_id, payload)
