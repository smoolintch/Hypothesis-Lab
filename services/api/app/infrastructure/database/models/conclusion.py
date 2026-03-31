from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ConclusionModel(Base):
    __tablename__ = "conclusions"
    __table_args__ = (
        UniqueConstraint("backtest_result_id", name="uq_conclusions_backtest_result_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    strategy_card_id: Mapped[UUID] = mapped_column(
        ForeignKey("strategy_cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    backtest_result_id: Mapped[UUID] = mapped_column(
        ForeignKey("backtest_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_worth_researching: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_accept_drawdown: Mapped[bool] = mapped_column(Boolean, nullable=False)
    market_condition_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_action: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
