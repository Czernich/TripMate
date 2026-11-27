from fastapi import APIRouter, status

from app.modules.auth.dependencies import AuthServiceDep
from app.modules.auth.schemas import LoginRequest, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: LoginRequest,
    service: AuthServiceDep,
) -> TokenResponse:
    return await service.login(payload)
