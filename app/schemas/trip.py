from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator


class TripBase(BaseModel):
    name: str = Field(..., min_length=1, description="Trip name, cannot be empty")
    destination: str
    start_date: date
    end_date: date

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be empty")
        return value

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
