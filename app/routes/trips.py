from typing import Annotated

from fastapi import APIRouter, Path

from app.modules.trips.dependencies import SessionService
from app.modules.trips.schemas import TripDetail

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/{trip_id}", response_model=TripDetail, status_code=200)
async def get_trip(
    trip_id: Annotated[int, Path(gt=0)],
    service: SessionService,
) -> TripDetail:
    trip = await service.get_trip(trip_id)
    return TripDetail.model_validate(trip)
