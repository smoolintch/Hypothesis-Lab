"""add conclusions table

Revision ID: 20260331_01
Revises: 20260330_01
Create Date: 2026-03-31 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260331_01"
down_revision: str | None = "20260330_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conclusions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("strategy_card_id", sa.Uuid(), nullable=False),
        sa.Column("backtest_result_id", sa.Uuid(), nullable=False),
        sa.Column("is_worth_researching", sa.Boolean(), nullable=False),
        sa.Column("can_accept_drawdown", sa.Boolean(), nullable=False),
        sa.Column("market_condition_notes", sa.Text(), nullable=True),
        sa.Column("next_action", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["backtest_result_id"],
            ["backtest_results.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["strategy_card_id"],
            ["strategy_cards.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("backtest_result_id", name="uq_conclusions_backtest_result_id"),
    )
    op.create_index(
        "ix_conclusions_user_id",
        "conclusions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_conclusions_strategy_card_id",
        "conclusions",
        ["strategy_card_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_conclusions_strategy_card_id", table_name="conclusions")
    op.drop_index("ix_conclusions_user_id", table_name="conclusions")
    op.drop_table("conclusions")
