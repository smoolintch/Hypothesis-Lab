from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.strategy_snapshot import StrategySnapshotModel


class StrategySnapshotRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def next_version(self, *, strategy_card_id: UUID) -> int:
        stmt = select(func.coalesce(func.max(StrategySnapshotModel.version), 0)).where(
            StrategySnapshotModel.strategy_card_id == strategy_card_id,
        )
        current = self.session.execute(stmt).scalar_one()
        return int(current) + 1

    def create(
        self,
        *,
        snapshot_id: UUID,
        user_id: UUID,
        strategy_card_id: UUID,
        version: int,
        source_strategy_updated_at: datetime,
        normalized_config: dict[str, object],
        created_at: datetime,
    ) -> StrategySnapshotModel:
        record = StrategySnapshotModel(
            id=snapshot_id,
            user_id=user_id,
            strategy_card_id=strategy_card_id,
            version=version,
            source_strategy_updated_at=source_strategy_updated_at,
            normalized_config=normalized_config,
            created_at=created_at,
        )
        self.session.add(record)
        self.session.flush()
        return record
