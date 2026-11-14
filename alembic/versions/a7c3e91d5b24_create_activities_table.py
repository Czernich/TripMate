from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7c3e91d5b24"
down_revision: str | Sequence[str] | None = "bc5e46faea40"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(timezone=False), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["trip_id"],
            ["trips.id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "length(btrim(title)) > 0",
            name="ck_activities_title_not_blank",
        ),
    )
    op.create_index(
        "ix_activities_trip_id_activity_date_start_time",
        "activities",
        ["trip_id", "activity_date", "start_time"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_activities_trip_id_activity_date_start_time",
        table_name="activities",
    )
    op.drop_table("activities")
