from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.application.errors import (
    BacktestResultNotFoundError,
    ConclusionAlreadyExistsError,
    StrategyCardNotFoundError,
)
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.repositories.backtest_result import BacktestResultRepository
from app.infrastructure.database.repositories.backtest_run import BacktestRunRepository
from app.infrastructure.database.repositories.conclusion import ConclusionRepository
from app.infrastructure.database.repositories.strategy_card import StrategyCardRepository
from app.schemas.conclusions import ConclusionResponse, ConclusionUpsertPayload


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ConclusionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.card_repo = StrategyCardRepository(session)
        self.result_repo = BacktestResultRepository(session)
        self.run_repo = BacktestRunRepository(session)
        self.conclusion_repo = ConclusionRepository(session)

    def create_conclusion(
        self,
        strategy_card_id: UUID,
        payload: ConclusionUpsertPayload,
    ) -> ConclusionResponse:
        user_id = self.settings.default_user_id

        # 1. Verify strategy card exists for this user
        card = self.card_repo.get_by_id(
            strategy_card_id=strategy_card_id,
            user_id=user_id,
        )
        if card is None:
            raise StrategyCardNotFoundError(str(strategy_card_id))

        # 2. Verify backtest result exists for this user
        result_record = self.result_repo.get_by_id_for_user(
            result_id=payload.backtest_result_id,
            user_id=user_id,
        )
        if result_record is None:
            raise BacktestResultNotFoundError(str(payload.backtest_result_id))

        # 3. Verify ownership: result → run → snapshot → strategy_card
        run_and_snapshot = self.run_repo.get_by_id_for_user(
            run_id=result_record.backtest_run_id,
            user_id=user_id,
        )
        if run_and_snapshot is None:
            raise BacktestResultNotFoundError(str(payload.backtest_result_id))
        _, snapshot = run_and_snapshot
        if snapshot.strategy_card_id != card.id:
            raise BacktestResultNotFoundError(str(payload.backtest_result_id))

        # 4. Enforce one conclusion per backtest result
        existing = self.conclusion_repo.get_by_result_id_for_user(
            backtest_result_id=payload.backtest_result_id,
            user_id=user_id,
        )
        if existing is not None:
            raise ConclusionAlreadyExistsError(str(payload.backtest_result_id))

        # 5. Create
        now = utc_now()
        record = self.conclusion_repo.create(
            conclusion_id=uuid4(),
            user_id=user_id,
            strategy_card_id=card.id,
            backtest_result_id=payload.backtest_result_id,
            is_worth_researching=payload.is_worth_researching,
            can_accept_drawdown=payload.can_accept_drawdown,
            market_condition_notes=payload.market_condition_notes,
            next_action=payload.next_action,
            notes=payload.notes,
            created_at=now,
            updated_at=now,
        )
        self.session.commit()
        return self._to_response(record)

    def _to_response(self, record) -> ConclusionResponse:
        return ConclusionResponse(
            id=record.id,
            strategy_card_id=record.strategy_card_id,
            backtest_result_id=record.backtest_result_id,
            is_worth_researching=record.is_worth_researching,
            can_accept_drawdown=record.can_accept_drawdown,
            market_condition_notes=record.market_condition_notes,
            next_action=record.next_action,
            notes=record.notes,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
