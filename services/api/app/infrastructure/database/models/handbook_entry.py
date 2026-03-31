from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HandbookEntryModel(Base):
    __tablename__ = "handbook_entries"
    __table_args__ = (
        UniqueConstraint("conclusion_id", name="uq_handbook_entries_conclusion_id"),
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
    conclusion_id: Mapped[UUID] = mapped_column(
        ForeignKey("conclusions.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
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
