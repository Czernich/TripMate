from datetime import date

import pytest
from pydantic import ValidationError

from app.modules.trips.schemas import TripCreate, TripDetail, TripUpdate


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


def test_trip_update_accepts_one_field():
    trip = TripUpdate(destination="Madrid")

    assert trip.destination == "Madrid"
    assert trip.model_dump(exclude_unset=True) == {
        "destination": "Madrid",
    }


def test_trip_update_accepts_both_dates():
    trip = TripUpdate(
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )

    assert trip.model_dump(exclude_unset=True) == {
        "start_date": date(2026, 9, 10),
        "end_date": date(2026, 9, 15),
    }


@pytest.mark.parametrize("field", ["name", "destination"])
def test_trip_update_trims_text(field):
    trip = TripUpdate(**{field: "  Barcelona  "})

    assert trip.model_dump(exclude_unset=True) == {
        field: "Barcelona",
    }


@pytest.mark.parametrize("field", ["name", "destination"])
def test_trip_update_accepts_255_characters(field):
    value = "a" * 255

    trip = TripUpdate(**{field: value})

    assert trip.model_dump(exclude_unset=True) == {field: value}


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="empty_body"),
        pytest.param({"name": None}, id="null_name"),
        pytest.param({"destination": None}, id="null_destination"),
        pytest.param({"start_date": None}, id="null_start_date"),
        pytest.param({"end_date": None}, id="null_end_date"),
        pytest.param({"name": ""}, id="empty_name"),
        pytest.param({"name": "   "}, id="blank_name"),
        pytest.param({"destination": ""}, id="empty_destination"),
        pytest.param({"destination": "   "}, id="blank_destination"),
        pytest.param({"name": "a" * 256}, id="name_too_long"),
        pytest.param(
            {"destination": "a" * 256},
            id="destination_too_long",
        ),
        pytest.param({"start_date": "invalid"}, id="invalid_date"),
        pytest.param({"unknown": "value"}, id="unknown_field"),
        pytest.param({"id": 1}, id="protected_id"),
        pytest.param(
            {"created_at": "2026-01-01T00:00:00Z"},
            id="protected_created_at",
        ),
        pytest.param(
            {"updated_at": "2026-01-01T00:00:00Z"},
            id="protected_updated_at",
        ),
    ],
)
def test_trip_update_invalid_raises(payload):
    with pytest.raises(ValidationError):
        TripUpdate(**payload)
