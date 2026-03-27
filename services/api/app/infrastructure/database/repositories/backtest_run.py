from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.backtest_run import BacktestRunModel
from app.infrastructure.database.models.strategy_snapshot import StrategySnapshotModel


class BacktestRunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        run_id: UUID,
        user_id: UUID,
        strategy_snapshot_id: UUID,
        status: str,
        created_at: datetime,
    ) -> BacktestRunModel:
        record = BacktestRunModel(
            id=run_id,
            user_id=user_id,
            strategy_snapshot_id=strategy_snapshot_id,
            status=status,
            error_code=None,
            error_message=None,
            started_at=None,
            finished_at=None,
            created_at=created_at,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get_by_id_for_user(
        self,
        *,
        run_id: UUID,
        user_id: UUID,
    ) -> tuple[BacktestRunModel, StrategySnapshotModel] | None:
        run = (
            self.session.query(BacktestRunModel)
            .filter(
                BacktestRunModel.id == run_id,
                BacktestRunModel.user_id == user_id,
            )
            .one_or_none()
        )
        if run is None:
            return None
        snapshot = (
            self.session.query(StrategySnapshotModel)
            .filter(StrategySnapshotModel.id == run.strategy_snapshot_id)
            .one_or_none()
        )
        if snapshot is None:
            return None
        return run, snapshot
