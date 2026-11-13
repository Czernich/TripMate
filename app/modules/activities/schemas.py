from datetime import date, time
from typing import Annotated

from pydantic import BaseModel, StringConstraints, field_validator

from app.modules.trips.schemas import TrimmedText255

TrimmedDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=2000),
]


class ActivityCreate(BaseModel):
    title: TrimmedText255
    activity_date: date
    start_time: time
    description: TrimmedDescription | None = None

    @field_validator("start_time")
    @classmethod
    def reject_timezone(cls, value: time) -> time:
        if value.tzinfo is not None:
            raise ValueError("start_time must not include a timezone offset")
        return value