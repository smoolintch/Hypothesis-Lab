"""add strategy_snapshots, backtest_runs, latest_backtest_run_id

Revision ID: 20260326_01
Revises: 20260325_01
Create Date: 2026-03-26 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260326_01"
down_revision: str | None = "20260325_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "strategy_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("strategy_card_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("source_strategy_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("normalized_config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["strategy_card_id"],
            ["strategy_cards.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "strategy_card_id",
            "version",
            name="uq_strategy_snapshots_strategy_card_id_version",
        ),
    )
    op.create_index(
        "ix_strategy_snapshots_strategy_card_id",
        "strategy_snapshots",
        ["strategy_card_id"],
        unique=False,
    )

    op.create_table(
        "backtest_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("strategy_snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.String(length=2000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["strategy_snapshot_id"],
            ["strategy_snapshots.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_backtest_runs_strategy_snapshot_id",
        "backtest_runs",
        ["strategy_snapshot_id"],
        unique=False,
    )
    op.create_index(
        "ix_backtest_runs_user_id_created_at",
        "backtest_runs",
        ["user_id", "created_at"],
        unique=False,
    )

    op.add_column(
        "strategy_cards",
        sa.Column("latest_backtest_run_id", sa.Uuid(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("strategy_cards", "latest_backtest_run_id")
    op.drop_index("ix_backtest_runs_user_id_created_at", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_strategy_snapshot_id", table_name="backtest_runs")
    op.drop_table("backtest_runs")
    op.drop_index("ix_strategy_snapshots_strategy_card_id", table_name="strategy_snapshots")
    op.drop_table("strategy_snapshots")
