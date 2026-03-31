"""add handbook_entries table

Revision ID: 20260331_02
Revises: 20260331_01
Create Date: 2026-03-31 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260331_02"
down_revision: str | None = "20260331_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "handbook_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("strategy_card_id", sa.Uuid(), nullable=False),
        sa.Column("backtest_result_id", sa.Uuid(), nullable=False),
        sa.Column("conclusion_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["backtest_result_id"],
            ["backtest_results.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["conclusion_id"],
            ["conclusions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["strategy_card_id"],
            ["strategy_cards.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conclusion_id", name="uq_handbook_entries_conclusion_id"),
    )
    op.create_index(
        "ix_handbook_entries_user_id",
        "handbook_entries",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_handbook_entries_strategy_card_id",
        "handbook_entries",
        ["strategy_card_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_handbook_entries_strategy_card_id", table_name="handbook_entries")
    op.drop_index("ix_handbook_entries_user_id", table_name="handbook_entries")
    op.drop_table("handbook_entries")
