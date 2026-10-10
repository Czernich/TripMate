"""empty message

Revision ID: c19d41ce3af4
Revises: b3258a542fcc
Create Date: 2026-10-26 13:26:12.282789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c19d41ce3af4'
down_revision: Union[str, Sequence[str], None] = 'b3258a542fcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
