from datetime import date

import pytest
from pydantic import ValidationError

from app.modules.trips.schemas import TripCreate, TripDetail


def test_trip_create_valid():
    trip = TripCreate(
        name="Barcelona Trip",
        destination="Barcelona",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )
    assert trip.name == "Barcelona Trip"


@pytest.mark.parametrize(
    "name, start_date, end_date",
    [
        pytest.param("", date(2026, 9, 10), date(2026, 9, 15), id="empty_name"),
        pytest.param("   ", date(2026, 9, 10), date(2026, 9, 15), id="blank_name"),
        pytest.param(
            "Barcelona Trip",
            date(2026, 9, 15),
            date(2026, 9, 10),
            id="end_before_start",
        ),
    ],
)
def test_trip_create_invalid_raises(name, start_date, end_date):
    with pytest.raises(ValidationError):
        TripCreate(
            name=name,
            destination="Barcelona",
            start_date=start_date,
            end_date=end_date,
        )


def test_trip_create_end_before_start_message():
    with pytest.raises(ValidationError) as exc_info:
        TripCreate(
            name="Barcelona Trip",
            destination="Barcelona",
            start_date=date(2026, 9, 15),
            end_date=date(2026, 9, 10),
        )
    assert "end_date cannot be earlier than start_date" in str(exc_info.value)


def test_trip_detail_valid():
    trip = TripDetail(
        id=1,
        name="Barcelona Trip",
        destination="Barcelona",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )
    assert trip.id == 1
    assert trip.name == "Barcelona Trip"


@pytest.mark.parametrize(
    "name, start_date, end_date",
    [
        pytest.param("", date(2026, 9, 10), date(2026, 9, 15), id="empty_name"),
        pytest.param(
            "Barcelona Trip",
            date(2026, 9, 15),
            date(2026, 9, 10),
            id="end_before_start",
        ),
    ],
)
def test_trip_detail_invalid_raises(name, start_date, end_date):
    with pytest.raises(ValidationError):
        TripDetail(
            id=1,
            name=name,
            destination="Barcelona",
            start_date=start_date,
            end_date=end_date,
        )
