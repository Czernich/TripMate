from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.trips.repository import TripRepository
from app.modules.trips.service import TripService

SessionDep = Annotated[
    AsyncSession,
    Depends(get_db),
]


def get_trip_repository(
    session: SessionDep,
) -> TripRepository:
    return TripRepository(session)


TripRepositoryDep = Annotated[
    TripRepository,
    Depends(get_trip_repository),
]


def get_trip_service(
    repository: TripRepositoryDep,
    session: SessionDep,
) -> TripService:
    return TripService(
        repository=repository,
        session=session,
    )


TripServiceDep = Annotated[
    TripService,
    Depends(get_trip_service),
]
