from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backtest_engine.data import BacktestRange, load_market_candles
from backtest_engine.data.errors import InvalidMarketDatasetError, MarketDatasetNotFoundError


REPO_ROOT = Path(__file__).resolve().parents[3]
MARKET_DATA_DIR = REPO_ROOT / "data" / "market"


def test_load_market_candles_returns_sorted_standardized_candles() -> None:
    dataset = load_market_candles(
        symbol="BTCUSDT",
        timeframe="1D",
        version="sample-v1",
        market_data_dir=MARKET_DATA_DIR,
    )

    assert dataset.metadata.symbol == "BTCUSDT"
    assert dataset.metadata.timeframe == "1D"
    assert dataset.metadata.version == "sample-v1"
    assert len(dataset.candles) == 5
    assert dataset.candles[0].ts == datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert dataset.candles[-1].ts == datetime(2024, 1, 5, tzinfo=timezone.utc)
    assert dataset.candles[0].open == dataset.candles[0].open.__class__("42000.00")
    assert tuple(candle.ts for candle in dataset.candles) == tuple(
        sorted(candle.ts for candle in dataset.candles)
    )


def test_load_market_candles_raises_clear_error_for_missing_dataset() -> None:
    with pytest.raises(MarketDatasetNotFoundError, match="Market dataset not found"):
        load_market_candles(
            symbol="BTCUSDT",
            timeframe="1D",
            version="missing-v1",
            market_data_dir=MARKET_DATA_DIR,
        )


def test_load_market_candles_raises_clear_error_for_invalid_format(tmp_path: Path) -> None:
    market_data_dir = tmp_path / "data" / "market"
    dataset_dir = market_data_dir / "fixture" / "BTCUSDT" / "1D" / "sample-v1"
    dataset_dir.mkdir(parents=True)

    manifest = {
        "id": "dataset-1",
        "source": "fixture",
        "symbol": "BTCUSDT",
        "timeframe": "1D",
        "version": "sample-v1",
        "coverage_start_at": "2024-01-01T00:00:00Z",
        "coverage_end_at": "2024-01-03T00:00:00Z",
        "candle_count": 2,
        "storage_uri": "data/market/fixture/BTCUSDT/1D/sample-v1/candles.csv",
        "created_at": "2026-03-25T00:00:00Z",
        "timezone": "UTC",
        "sort_order": "ts_asc",
        "columns": ["ts", "open", "high", "low", "close", "volume"],
    }
    (dataset_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (dataset_dir / "candles.csv").write_text(
        "ts,open,high,low,close,volume\n"
        "2024-01-02T00:00:00Z,10,11,9,10.5,100\n"
        "2024-01-01T00:00:00Z,9,10,8,9.5,90\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidMarketDatasetError, match="timestamps must be strictly increasing"):
        load_market_candles(
            symbol="BTCUSDT",
            timeframe="1D",
            version="sample-v1",
            market_data_dir=market_data_dir,
        )


def test_load_market_candles_can_filter_by_backtest_range() -> None:
    dataset = load_market_candles(
        symbol="BTCUSDT",
        timeframe="1D",
        version="sample-v1",
        market_data_dir=MARKET_DATA_DIR,
        backtest_range=BacktestRange(
            start_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            end_at=datetime(2024, 1, 4, tzinfo=timezone.utc),
        ),
    )

    assert len(dataset.candles) == 2
    assert [candle.ts for candle in dataset.candles] == [
        datetime(2024, 1, 2, tzinfo=timezone.utc),
        datetime(2024, 1, 3, tzinfo=timezone.utc),
    ]
