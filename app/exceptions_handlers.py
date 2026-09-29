import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import AppBaseException

logger = logging.getLogger(__name__)

app = FastAPI()


@app.exception_handler(AppBaseException)
async def app_base_exception_handler(_request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.error_code, "message": exc.message}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error. Please try again later.",
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload.",
                "details": exc.errors(),
            }
        },
    )
