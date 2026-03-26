from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.strategy_card import StrategyCardModel


class StrategyCardRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        strategy_card_id: UUID,
        user_id: UUID,
        name: str,
        symbol: str,
        timeframe: str,
        backtest_range: dict[str, str],
        initial_capital: Decimal,
        fee_rate: Decimal,
        rule_set: dict[str, object],
        status: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> StrategyCardModel:
        record = StrategyCardModel(
            id=strategy_card_id,
            user_id=user_id,
            name=name,
            symbol=symbol,
            timeframe=timeframe,
            backtest_range=backtest_range,
            initial_capital=initial_capital,
            fee_rate=fee_rate,
            rule_set=rule_set,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_by_id(self, *, strategy_card_id: UUID, user_id: UUID) -> StrategyCardModel | None:
        return (
            self.session.query(StrategyCardModel)
            .filter(
                StrategyCardModel.id == strategy_card_id,
                StrategyCardModel.user_id == user_id,
            )
            .one_or_none()
        )

    def update(
        self,
        *,
        record: StrategyCardModel,
        name: str,
        symbol: str,
        timeframe: str,
        backtest_range: dict[str, str],
        initial_capital: Decimal,
        fee_rate: Decimal,
        rule_set: dict[str, object],
        updated_at: datetime,
    ) -> StrategyCardModel:
        record.name = name
        record.symbol = symbol
        record.timeframe = timeframe
        record.backtest_range = backtest_range
        record.initial_capital = initial_capital
        record.fee_rate = fee_rate
        record.rule_set = rule_set
        record.updated_at = updated_at
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
