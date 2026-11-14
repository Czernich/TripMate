from datetime import date, time

import pytest
from pydantic import ValidationError

from app.modules.activities.schemas import ActivityCreate


def make_payload(**overrides: object) -> dict[str, object]:
    return {
        "title": "Colosseum tour",
        "activity_date": "2026-07-02",
        "start_time": "09:30",
        **overrides,
    }


def test_activity_create_valid():
    activity = ActivityCreate.model_validate(make_payload())

    assert activity.title == "Colosseum tour"
    assert activity.activity_date == date(2026, 7, 2)
    assert activity.start_time == time(9, 30)
    assert activity.description is None


def test_activity_create_trims_text_fields():
    activity = ActivityCreate.model_validate(
        make_payload(title="  Colosseum tour  ", description="  Guided  ")
    )

    assert activity.title == "Colosseum tour"
    assert activity.description == "Guided"


def test_activity_create_accepts_max_length_text_fields():
    activity = ActivityCreate.model_validate(
        make_payload(title="x" * 255, description="y" * 2000)
    )

    assert len(activity.title) == 255
    assert activity.description is not None
    assert len(activity.description) == 2000


@pytest.mark.parametrize("value", ["00:00", "23:59:59"])
def test_activity_create_accepts_boundary_times(value: str):
    activity = ActivityCreate.model_validate(make_payload(start_time=value))

    assert activity.start_time == time.fromisoformat(value)


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"title": ""}, id="empty_title"),
        pytest.param({"title": "   "}, id="blank_title"),
        pytest.param({"title": "x" * 256}, id="title_too_long"),
        pytest.param({"title": None}, id="null_title"),
        pytest.param({"title": 123}, id="non_string_title"),
        pytest.param({"activity_date": "2026-13-40"}, id="invalid_date"),
        pytest.param({"activity_date": None}, id="null_date"),
        pytest.param({"start_time": "25:00"}, id="invalid_time"),
        pytest.param({"start_time": None}, id="null_time"),
        pytest.param({"start_time": "09:30+02:00"}, id="time_with_offset"),
        pytest.param({"start_time": "09:30Z"}, id="time_with_utc"),
        pytest.param({"description": "x" * 2001}, id="description_too_long"),
    ],
)
def test_activity_create_invalid_raises(overrides: dict[str, object]):
    with pytest.raises(ValidationError):
        ActivityCreate.model_validate(make_payload(**overrides))


def test_activity_create_requires_all_mandatory_fields():
    with pytest.raises(ValidationError):
        ActivityCreate.model_validate({"title": "Colosseum tour"})
