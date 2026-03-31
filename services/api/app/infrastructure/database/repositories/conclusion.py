from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.conclusion import ConclusionModel


class ConclusionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        conclusion_id: UUID,
        user_id: UUID,
        strategy_card_id: UUID,
        backtest_result_id: UUID,
        is_worth_researching: bool,
        can_accept_drawdown: bool,
        market_condition_notes: str | None,
        next_action: str,
        notes: str | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> ConclusionModel:
        record = ConclusionModel(
            id=conclusion_id,
            user_id=user_id,
            strategy_card_id=strategy_card_id,
            backtest_result_id=backtest_result_id,
            is_worth_researching=is_worth_researching,
            can_accept_drawdown=can_accept_drawdown,
            market_condition_notes=market_condition_notes,
            next_action=next_action,
            notes=notes,
            created_at=created_at,
            updated_at=updated_at,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get_by_result_id_for_user(
        self,
        *,
        backtest_result_id: UUID,
        user_id: UUID,
    ) -> ConclusionModel | None:
        return (
            self.session.query(ConclusionModel)
            .filter(
                ConclusionModel.backtest_result_id == backtest_result_id,
                ConclusionModel.user_id == user_id,
            )
            .one_or_none()
        )

    def get_by_id_for_user(
        self,
        *,
        conclusion_id: UUID,
        user_id: UUID,
    ) -> ConclusionModel | None:
        return (
            self.session.query(ConclusionModel)
            .filter(
                ConclusionModel.id == conclusion_id,
                ConclusionModel.user_id == user_id,
            )
            .one_or_none()
        )
