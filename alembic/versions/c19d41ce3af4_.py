"""empty message

Revision ID: c19d41ce3af4
Revises: b3258a542fcc
Create Date: 2026-10-26 13:26:12.282789

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "c19d41ce3af4"
down_revision: str | Sequence[str] | None = "b3258a542fcc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
