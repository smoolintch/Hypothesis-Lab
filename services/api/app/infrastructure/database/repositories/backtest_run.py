from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.backtest_run import BacktestRunModel
from app.infrastructure.database.models.strategy_card import StrategyCardModel
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

    def update_status(
        self,
        record: BacktestRunModel,
        *,
        status: str,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> BacktestRunModel:
        record.status = status
        if started_at is not None:
            record.started_at = started_at
        if finished_at is not None:
            record.finished_at = finished_at
        if error_code is not None:
            record.error_code = error_code
        if error_message is not None:
            record.error_message = error_message
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

    def list_recent_for_user(
        self,
        *,
        user_id: UUID,
        limit: int = 5,
    ) -> list[tuple[BacktestRunModel, StrategySnapshotModel, StrategyCardModel]]:
        rows = (
            self.session.query(BacktestRunModel, StrategySnapshotModel, StrategyCardModel)
            .join(
                StrategySnapshotModel,
                StrategySnapshotModel.id == BacktestRunModel.strategy_snapshot_id,
            )
            .join(
                StrategyCardModel,
                StrategyCardModel.id == StrategySnapshotModel.strategy_card_id,
            )
            .filter(BacktestRunModel.user_id == user_id)
            .order_by(BacktestRunModel.created_at.desc(), BacktestRunModel.id.desc())
            .limit(limit)
            .all()
        )
        return rows

    def list_for_strategy_card(
        self,
        *,
        strategy_card_id: UUID,
        user_id: UUID,
        limit: int = 20,
    ) -> list[tuple[BacktestRunModel, StrategySnapshotModel]]:
        rows = (
            self.session.query(BacktestRunModel, StrategySnapshotModel)
            .join(
                StrategySnapshotModel,
                StrategySnapshotModel.id == BacktestRunModel.strategy_snapshot_id,
            )
            .filter(
                BacktestRunModel.user_id == user_id,
                StrategySnapshotModel.strategy_card_id == strategy_card_id,
            )
            .order_by(BacktestRunModel.created_at.desc(), BacktestRunModel.id.desc())
            .limit(limit)
            .all()
        )
        return rows
