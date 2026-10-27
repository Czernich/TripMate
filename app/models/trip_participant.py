from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from app.database import Base
from app.models import Trip

if TYPE_CHECKING:
    from app.models.trip import Trip
    from app.models.user import User


class TripRole(str, Enum):
    OWNER = "Owner"
    ADMIN = "Admin"
    MEMBER = "Member"
    VIEWER = "Viewer"


class TripParticipant(Base):
    __tablename__ = "trip_participants"

    __table_args__ = (
        UniqueConstraint("user_id", "trip_id", name="trip_participant_user_id_trip_id"),
        Index("ix_trip_participant_trip_id", "trip_id"),
        Index("trip_participant_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    role: Mapped[TripRole] = mapped_column(
        SAEnum(
            TripRole,
            values_callable=lambda enum_cls: [role.value for role in enum_cls],
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            name="ck_trip_participant_role",
            length=16,
        ),
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="participants",
    )

    user: Mapped["User"] = relationship(
        back_populates="trip_participations",
    )
