from datetime import date

import factory

import app.models


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
