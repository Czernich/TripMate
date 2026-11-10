from datetime import date, datetime, timedelta, timezone

import factory

import app.models
from app.models import TripParticipant, TripRole


class TripCreatePayloadFactory(factory.DictFactory):
    name = "Test trip"
    destination = "Paris"
    start_date = factory.LazyFunction(
        lambda: (datetime.now(tz=timezone.utc).date() + timedelta(days=30)).isoformat()
    )
    end_date = factory.LazyAttribute(
        lambda payload: (
            date.fromisoformat(payload.start_date) + timedelta(days=5)
        ).isoformat()
    )


class TripFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = app.models.Trip

    name = "Summer in Rome"
    destination = "Rome"
    start_date = date(2026, 7, 1)
    end_date = date(2026, 7, 10)


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = app.models.User

    email = "user1@tripmate.com"
    password_hash = "$2a$12$qNvf9ovKdIaAQu9rSUZvKOlE"
    display_name = "TripMate"


class TripParticipantFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TripParticipant

    role = TripRole.MEMBER
