from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class BacktestRange:
    start_at: datetime
    end_at: datetime


@dataclass(frozen=True)
class Candle:
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True)
class MarketDatasetMetadata:
    id: str
    source: str
    symbol: str
    timeframe: str
    version: str
    coverage_start_at: datetime
    coverage_end_at: datetime
    candle_count: int
    storage_uri: str
    created_at: datetime
    timezone: str
    sort_order: str
    columns: tuple[str, ...]


@dataclass(frozen=True)
class LoadedMarketDataset:
    metadata: MarketDatasetMetadata
    candles: tuple[Candle, ...]
