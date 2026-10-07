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
    assert trip.destination == "Barcelona"


def test_trip_create_trims_text_fields():
    trip = TripCreate(
        name="  Barcelona Trip  ",
        destination="  Barcelona  ",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )

    assert trip.name == "Barcelona Trip"
    assert trip.destination == "Barcelona"


def test_trip_create_accepts_equal_start_and_end_date():
    trip = TripCreate(
        name="Barcelona Trip",
        destination="Barcelona",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 10),
    )

    assert trip.start_date == trip.end_date


def test_trip_create_accepts_max_length_text_fields():
    trip = TripCreate(
        name="a" * 255,
        destination="b" * 255,
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )

    assert len(trip.name) == 255
    assert len(trip.destination) == 255


@pytest.mark.parametrize(
    "name, destination, start_date, end_date",
    [
        pytest.param(
            "", "Barcelona", date(2026, 9, 10), date(2026, 9, 15), id="empty_name"
        ),
        pytest.param(
            "   ", "Barcelona", date(2026, 9, 10), date(2026, 9, 15), id="blank_name"
        ),
        pytest.param(
            "a" * 256,
            "Barcelona",
            date(2026, 9, 10),
            date(2026, 9, 15),
            id="name_too_long",
        ),
        pytest.param(
            "Barcelona Trip",
            "",
            date(2026, 9, 10),
            date(2026, 9, 15),
            id="empty_destination",
        ),
        pytest.param(
            "Barcelona Trip",
            " ",
            date(2026, 9, 10),
            date(2026, 9, 15),
            id="blank_destination",
        ),
        pytest.param(
            "Barcelona Trip",
            "a" * 256,
            date(2026, 9, 10),
            date(2026, 9, 15),
            id="destination_too_long",
        ),
        pytest.param(
            "Barcelona Trip",
            "Barcelona",
            date(2026, 9, 15),
            date(2026, 9, 10),
            id="end_before_start",
        ),
    ],
)
def test_trip_create_invalid_raises(name, destination, start_date, end_date):
    with pytest.raises(ValidationError):
        TripCreate(
            name=name,
            destination=destination,
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
    assert trip.destination == "Barcelona"


def test_trip_create_validates_max_length_after_trimming():
    trip = TripCreate(
        name="  " + "a" * 255 + "  ",
        destination="  " + "b" * 255 + "  ",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )

    assert trip.name == "a" * 255
    assert trip.destination == "b" * 255
