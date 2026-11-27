from typing import Annotated

from fastapi import Depends

from app.modules.auth.service import AuthService
from app.modules.users.dependencies import UserRepositoryDep


def get_auth_service(
    user_repository: UserRepositoryDep,
) -> AuthService:
    return AuthService(user_repository)


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]
