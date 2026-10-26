from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.logging_config import setup_logging
from app.middleware import RequestContextMiddleware
from app.routes import health, trips
from app.settings import settings_db

setup_logging(settings_db.LOG_LEVEL)

app = FastAPI()
app.add_middleware(RequestContextMiddleware)
app.include_router(health.router)
app.include_router(trips.router)


register_exception_handlers(app)
