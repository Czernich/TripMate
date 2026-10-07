from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.routes import health

app = FastAPI()
app.include_router(health.router)

register_exception_handlers(app)
