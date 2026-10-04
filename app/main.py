from fastapi import FastAPI

from app.exceptions_handlers import register_exception_handlers
from app.routes import health, trips

app = FastAPI()
app.include_router(health.router)
app.include_router(trips.router)

register_exception_handlers(app)
