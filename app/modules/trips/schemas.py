from datetime import date
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

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


class TripUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: TrimmedText255 | None = None
    destination: TrimmedText255 | None = None
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_patch(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")

        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")

        return self
