from datetime import date

import factory

from app.models.trip import Trip


class TripFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Trip
        sqlalchemy_session = None
        sqlalchemy_session_persistence = None

    name = "Summer in Rome"
    destination = "Rome"
    start_date = date(2026, 7, 1)
    end_date = date(2026, 7, 10)
