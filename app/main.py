from fastapi import FastAPI

from app.routes import health, trips

app = FastAPI()

app.include_router(health.router)
app.include_router(trips.router)
