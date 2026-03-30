from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.backtest_result import BacktestResultModel


class BacktestResultRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        result_id: UUID,
        user_id: UUID,
        backtest_run_id: UUID,
        dataset_version: str,
        summary_metrics: dict,
        equity_curve: list,
        drawdown_curve: list,
        trades: list,
        result_summary: dict,
        created_at: datetime,
    ) -> BacktestResultModel:
        record = BacktestResultModel(
            id=result_id,
            user_id=user_id,
            backtest_run_id=backtest_run_id,
            dataset_version=dataset_version,
            summary_metrics=summary_metrics,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve,
            trades=trades,
            result_summary=result_summary,
            created_at=created_at,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get_by_run_id_for_user(
        self,
        *,
        run_id: UUID,
        user_id: UUID,
    ) -> BacktestResultModel | None:
        return (
            self.session.query(BacktestResultModel)
            .filter(
                BacktestResultModel.backtest_run_id == run_id,
                BacktestResultModel.user_id == user_id,
            )
            .one_or_none()
        )
