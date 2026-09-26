"""merge baseline and trips migrations

Revision ID: 1779671dce8b
Revises: 44bc4bfbb1d2, ced771a59407
Create Date: 2026-09-26 18:12:49.167920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1779671dce8b'
down_revision: Union[str, Sequence[str], None] = ('44bc4bfbb1d2', 'ced771a59407')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
