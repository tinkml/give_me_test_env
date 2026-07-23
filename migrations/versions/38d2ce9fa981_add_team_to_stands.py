"""add team to stands

Revision ID: 38d2ce9fa981
Revises: 1b05234702ec
Create Date: 2026-07-22 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "38d2ce9fa981"
down_revision: str | Sequence[str] | None = "1b05234702ec"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "stands",
        sa.Column("team", sa.String(), nullable=False, server_default="no_team"),
    )
    op.create_index(op.f("ix_stands_team"), "stands", ["team"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_stands_team"), table_name="stands")
    op.drop_column("stands", "team")
