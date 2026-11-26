from datetime import date, datetime, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    __table_args__ = (
        CheckConstraint(
            "length(btrim(title)) > 0",
            name="ck_activities_title_not_blank",
        ),
        Index(
            "ix_activities_trip_id_activity_date_start_time",
            "trip_id",
            "activity_date",
            "start_time",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Local itinerary time (wall-clock time at the trip destination).
    # Intentionally stored without a timezone; no timezone conversion is done.
    start_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
