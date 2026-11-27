from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

SessionDep = Annotated[
    AsyncSession,
    Depends(get_db),
]


def get_user_repository(
    session: SessionDep,
) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[
    UserRepository,
    Depends(get_user_repository),
]


def get_user_service(
    repository: UserRepositoryDep,
) -> UserService:
    return UserService(repository)


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]
