# app/models/__init__.py
from app.database import Base
from app.models.trip import Trip
from app.models.user import User

__all__ = ["Base", "Trip", "User"]
