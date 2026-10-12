from typing import Annotated

from fastapi import APIRouter, Path, Query

from app.models.trip import Trip
from app.modules.trips.dependencies import SessionService
from app.modules.trips.schemas import TripDetail

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/{trip_id}", response_model=TripDetail, status_code=200)
async def get_trip(
    trip_id: Annotated[int, Path(gt=0)],
    service: SessionService,
) -> Trip:
    return await service.get_trip(trip_id)


@router.get("", response_model=list[TripDetail], status_code=200)
async def list_trips(
    service: SessionService,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Trip]:
    return await service.list_trips(
        limit=limit,
        offset=offset,
    )
