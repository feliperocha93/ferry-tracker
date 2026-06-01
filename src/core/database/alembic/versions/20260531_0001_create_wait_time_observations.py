"""create wait_time_observations

Revision ID: 20260531_0001
Revises:
Create Date: 2026-05-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260531_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wait_time_observations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ferry_route_id", sa.Text(), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("wait_minutes", sa.Integer(), nullable=True),
        sa.Column("number_of_ships", sa.SmallInteger(), nullable=True),
        sa.Column("weather_alert", sa.Text(), nullable=True),
        sa.Column("scrape_status", sa.Text(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ferry_route_id",
            "collected_at",
            name="uq_wait_time_observations_route_collected",
        ),
    )
    op.create_index(
        "ix_wait_time_observations_collected_at",
        "wait_time_observations",
        ["collected_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_wait_time_observations_collected_at",
        table_name="wait_time_observations",
    )
    op.drop_table("wait_time_observations")
