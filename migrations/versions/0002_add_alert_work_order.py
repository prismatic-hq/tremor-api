"""add alert work order

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "tremor"


def upgrade() -> None:
    op.add_column("alerts", sa.Column("work_order_id", sa.Uuid(), nullable=True), schema=SCHEMA)


def downgrade() -> None:
    op.drop_column("alerts", "work_order_id", schema=SCHEMA)
