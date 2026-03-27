from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrategySnapshotModel(Base):
    __tablename__ = "strategy_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "strategy_card_id",
            "version",
            name="uq_strategy_snapshots_strategy_card_id_version",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    strategy_card_id: Mapped[UUID] = mapped_column(
        ForeignKey("strategy_cards.id", ondelete="CASCADE"),
        index=True,
    )
    version: Mapped[int] = mapped_column(nullable=False)
    source_strategy_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    normalized_config: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
