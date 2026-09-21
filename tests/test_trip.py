from datetime import date

from app.models.trip import Trip


def test_trip_creation():
    trip = Trip(
        name="Test vacation",
        destination="Test City",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 14),
    )

    assert trip.name == "Test vacation"
    assert trip.destination == "Test City"
    assert trip.start_date == date(2026, 7, 1)
    assert trip.end_date == date(2026, 7, 14)


def test_trip_required_fields():
    required_fields = {
        "name",
        "destination",
        "start_date",
        "end_date",
    }

    for field in required_fields:
        assert Trip.__table__.c[field].nullable is False
