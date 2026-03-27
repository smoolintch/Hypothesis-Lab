from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.application.errors import StrategyCardNotFoundError
from app.domain.strategy_cards.constants import STRATEGY_CARD_DEFAULT_STATUS
from app.domain.strategy_cards.validation import validate_strategy_card_payload
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.repositories.strategy_card import StrategyCardRepository
from app.schemas.strategy_cards import (
    BacktestRangePayload,
    StrategyCardDetailResponse,
    StrategyCardUpsertPayload,
    StrategyRuleSetPayload,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def coerce_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class StrategyCardService:
    def __init__(self, session: Session) -> None:
        self.repository = StrategyCardRepository(session)
        self.settings = get_settings()

    def create(self, payload: StrategyCardUpsertPayload) -> StrategyCardDetailResponse:
        normalized_rule_set = validate_strategy_card_payload(payload)
        now = utc_now()
        record = self.repository.create(
            strategy_card_id=uuid4(),
            user_id=self.settings.default_user_id,
            name=payload.name,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            backtest_range=payload.backtest_range.model_dump(mode="json"),
            initial_capital=Decimal(str(payload.initial_capital)),
            fee_rate=Decimal(str(payload.fee_rate)),
            rule_set=normalized_rule_set,
            status=STRATEGY_CARD_DEFAULT_STATUS,
            created_at=now,
            updated_at=now,
        )
        return self._to_detail_response(record)

    def get(self, strategy_card_id: UUID) -> StrategyCardDetailResponse:
        record = self.repository.get_by_id(
            strategy_card_id=strategy_card_id,
            user_id=self.settings.default_user_id,
        )
        if record is None:
            raise StrategyCardNotFoundError(str(strategy_card_id))
        return self._to_detail_response(record)

    def update(
        self,
        strategy_card_id: UUID,
        payload: StrategyCardUpsertPayload,
    ) -> StrategyCardDetailResponse:
        record = self.repository.get_by_id(
            strategy_card_id=strategy_card_id,
            user_id=self.settings.default_user_id,
        )
        if record is None:
            raise StrategyCardNotFoundError(str(strategy_card_id))

        normalized_rule_set = validate_strategy_card_payload(payload)
        record = self.repository.update(
            record=record,
            name=payload.name,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            backtest_range=payload.backtest_range.model_dump(mode="json"),
            initial_capital=Decimal(str(payload.initial_capital)),
            fee_rate=Decimal(str(payload.fee_rate)),
            rule_set=normalized_rule_set,
            updated_at=utc_now(),
        )
        return self._to_detail_response(record)

    def _to_detail_response(
        self,
        record,
    ) -> StrategyCardDetailResponse:
        return StrategyCardDetailResponse(
            id=record.id,
            name=record.name,
            symbol=record.symbol,
            timeframe=record.timeframe,
            status=record.status,
            updated_at=coerce_utc(record.updated_at),
            latest_backtest_run_id=record.latest_backtest_run_id,
            backtest_range=BacktestRangePayload.model_validate(record.backtest_range),
            initial_capital=float(record.initial_capital),
            fee_rate=float(record.fee_rate),
            rule_set=StrategyRuleSetPayload.model_validate(record.rule_set),
            created_at=coerce_utc(record.created_at),
        )
