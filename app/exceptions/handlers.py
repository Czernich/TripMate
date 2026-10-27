import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.base import AppBaseException
from app.middleware import REQUEST_ID_HEADER

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppBaseException)
    async def app_base_exception_handler(
        _request: Request, exc: AppBaseException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # This handler runs outside the logging middleware, so the request ID
        # is taken from request.state instead of the context variable.
        request_id = getattr(request.state, "request_id", "-")
        logger.exception("Unhandled error: %s", exc, extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            headers={REQUEST_ID_HEADER: request_id},
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error. Please try again later.",
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request payload.",
                    "details": jsonable_encoder(exc.errors()),
                }
            },
        )
