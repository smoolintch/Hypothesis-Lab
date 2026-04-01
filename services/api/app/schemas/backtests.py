from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BacktestRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    strategy_card_id: UUID
    strategy_snapshot_id: UUID
    status: str
    error_code: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    result_url: str | None
    created_at: datetime


class SummaryMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_return_rate: float
    max_drawdown_rate: float
    win_rate: float
    profit_factor: float
    trade_count: int
    avg_holding_bars: float
    final_equity: float


class CurvePointResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: str
    value: float


class TradeRecordResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trade_id: str
    entry_at: str
    exit_at: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl_amount: float
    pnl_rate: float
    exit_reason: str


class BacktestResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result_id: UUID
    run_id: UUID
    strategy_card_id: UUID
    strategy_snapshot_id: UUID
    dataset_version: str
    summary_metrics: SummaryMetricsResponse
    equity_curve: list[CurvePointResponse]
    drawdown_curve: list[CurvePointResponse]
    trades: list[TradeRecordResponse]
    result_summary: dict
    created_at: datetime


class RecentExperimentItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    strategy_card_id: UUID
    strategy_card_name: str
    status: str
    result_url: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class RecentExperimentsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[RecentExperimentItemResponse]


class HistoricalBacktestItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    status: str
    result_url: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class HistoricalBacktestsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategy_card_id: UUID
    items: list[HistoricalBacktestItemResponse]
