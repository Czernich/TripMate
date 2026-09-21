from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.trips.repository import TripRepository
from app.modules.trips.service import TripService


async def get_trip_repository(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> TripRepository:
    return TripRepository(db)


async def get_trip_service(
    repo: TripRepository = Depends(get_trip_repository),  # noqa: B008
) -> TripService:
    return TripService(repo)
