"""add is_verified and verification_token to users

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "users",
        sa.Column("verification_token", sa.String(100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "verification_token")
    op.drop_column("users", "is_verified")
