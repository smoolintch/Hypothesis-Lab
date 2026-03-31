from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError("datetime must include timezone information")
    return value.astimezone(timezone.utc)


class BacktestRangePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_at: datetime
    end_at: datetime

    @field_validator("start_at", "end_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        return ensure_utc(value)

    @model_validator(mode="after")
    def validate_order(self) -> "BacktestRangePayload":
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be later than start_at")
        return self


class RuleInstancePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template_key: str
    params: dict[str, Any]


class StrategyRuleSetPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry: RuleInstancePayload
    exit: RuleInstancePayload
    stop_loss: RuleInstancePayload | None = None
    take_profit: RuleInstancePayload | None = None


class StrategyCardUpsertPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    symbol: str
    timeframe: str
    backtest_range: BacktestRangePayload
    initial_capital: float
    fee_rate: float
    rule_set: StrategyRuleSetPayload

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("name must not be blank")
        return stripped

    @field_validator("initial_capital")
    @classmethod
    def validate_initial_capital(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("initial_capital must be greater than 0")
        return value

    @field_validator("fee_rate")
    @classmethod
    def validate_fee_rate(cls, value: float) -> float:
        if value < 0 or value > 0.01:
            raise ValueError("fee_rate must be between 0 and 0.01")
        return value


class StrategyCardDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str
    symbol: str
    timeframe: str
    status: str
    updated_at: datetime
    latest_backtest_run_id: UUID | None = None
    backtest_range: BacktestRangePayload
    initial_capital: float
    fee_rate: float
    rule_set: StrategyRuleSetPayload
    created_at: datetime


class StrategyCardSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str
    symbol: str
    timeframe: str
    status: str
    updated_at: datetime
    latest_backtest_run_id: UUID | None = None


class PaginationMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int
    page_size: int
    total: int


class StrategyCardListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[StrategyCardSummaryResponse]
    pagination: PaginationMeta
