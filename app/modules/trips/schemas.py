from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator, StringConstraints

TrimmedText255 = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

class TripBase(BaseModel):
    name: TrimmedText255
    destination: TrimmedText255
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self) -> "TripBase":
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return self


class TripCreate(TripBase):
    pass


class TripDetail(TripBase):
    id: int

    model_config = {"from_attributes": True}
