"""add end_date check constraint to trips

Revision ID: 44bc4bfbb1d2
Revises: 9e21dae12166
Create Date: 2026-09-24 22:15:33.185087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44bc4bfbb1d2'
down_revision: Union[str, Sequence[str], None] = '9e21dae12166'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_trips_end_date_after_start_date",
        "trips",
        "end_date >= start_date",
    )


def downgrade() -> None:
    op.drop_constraint("ck_trips_end_date_after_start_date", "trips", type_="check")
