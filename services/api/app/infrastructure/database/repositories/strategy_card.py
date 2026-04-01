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

    def duplicate(
        self,
        *,
        source_record: StrategyCardModel,
        strategy_card_id: UUID,
        created_at: datetime,
        updated_at: datetime,
    ) -> StrategyCardModel:
        record = StrategyCardModel(
            id=strategy_card_id,
            user_id=source_record.user_id,
            name=source_record.name,
            symbol=source_record.symbol,
            timeframe=source_record.timeframe,
            backtest_range=source_record.backtest_range,
            initial_capital=source_record.initial_capital,
            fee_rate=source_record.fee_rate,
            rule_set=source_record.rule_set,
            status=source_record.status,
            latest_backtest_run_id=None,
            created_at=created_at,
            updated_at=updated_at,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

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

    def update_latest_backtest_run_id(
        self,
        *,
        record: StrategyCardModel,
        latest_backtest_run_id: UUID | None,
    ) -> StrategyCardModel:
        record.latest_backtest_run_id = latest_backtest_run_id
        self.session.add(record)
        self.session.flush()
        return record

    def list_paginated(
        self,
        *,
        user_id: UUID,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[StrategyCardModel], int]:
        query = self.session.query(StrategyCardModel).filter(
            StrategyCardModel.user_id == user_id,
        )
        if status is not None:
            query = query.filter(StrategyCardModel.status == status)
        total: int = query.count()
        items = (
            query.order_by(StrategyCardModel.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total
