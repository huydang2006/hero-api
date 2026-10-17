"""add hero status and created_at

Revision ID: 8f1a2c3d4e5f
Revises: 69b38f0f83a1
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f1a2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "69b38f0f83a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hero",
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
    )
    op.add_column(
        "hero",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_column("hero", "created_at")
    op.drop_column("hero", "status")
