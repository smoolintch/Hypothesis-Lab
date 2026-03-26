"""create strategy cards table

Revision ID: 20260325_01
Revises:
Create Date: 2026-03-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260325_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "strategy_cards",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("timeframe", sa.String(length=10), nullable=False),
        sa.Column("backtest_range", sa.JSON(), nullable=False),
        sa.Column("initial_capital", sa.Numeric(18, 2), nullable=False),
        sa.Column("fee_rate", sa.Numeric(8, 6), nullable=False),
        sa.Column("rule_set", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_strategy_cards_user_id_updated_at",
        "strategy_cards",
        ["user_id", "updated_at"],
        unique=False,
    )
    op.create_index(
        "ix_strategy_cards_user_id",
        "strategy_cards",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_strategy_cards_user_id", table_name="strategy_cards")
    op.drop_index("ix_strategy_cards_user_id_updated_at", table_name="strategy_cards")
    op.drop_table("strategy_cards")
