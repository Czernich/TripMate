from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.trip import TripCreate, TripDetail


def test_trip_create_valid():
    trip = TripCreate(
        name="Barcelona Trip",
        destination="Barcelona",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )
    assert trip.name == "Barcelona Trip"


def test_trip_create_empty_name_raises():
    with pytest.raises(ValidationError):
        TripCreate(
            name="",
            destination="Barcelona",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 15),
        )


def test_trip_create_blank_name_raises():
    with pytest.raises(ValidationError):
        TripCreate(
            name="   ",
            destination="Barcelona",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 15),
        )


def test_trip_create_end_before_start_raises():
    with pytest.raises(ValidationError):
        TripCreate(
            name="Barcelona Trip",
            destination="Barcelona",
            start_date=date(2026, 9, 15),
            end_date=date(2026, 9, 10),
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


def test_trip_detail_empty_name_raises():
    with pytest.raises(ValidationError):
        TripDetail(
            id=1,
            name="",
            destination="Barcelona",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 15),
        )


def test_trip_detail_end_before_start_raises():
    with pytest.raises(ValidationError):
        TripDetail(
            id=1,
            name="Barcelona Trip",
            destination="Barcelona",
            start_date=date(2026, 9, 15),
            end_date=date(2026, 9, 10),
        )
