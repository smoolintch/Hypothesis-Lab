"""Backtest engine package."""

from .core import (
    BacktestConfigError,
    BacktestEngineError,
    BacktestExecutionError,
    BacktestExecutionResult,
    EquityPoint,
    ExecutionConfig,
    MarketConfig,
    NormalizedStrategyConfig,
    RuleInstance,
    StrategyRuleSet,
    TradeRecord,
    parse_normalized_strategy_config,
    run_backtest,
)
from .data import (
    BacktestRange,
    Candle,
    InvalidMarketDatasetError,
    LoadedMarketDataset,
    MarketDatasetMetadata,
    MarketDatasetNotFoundError,
    load_market_candles,
)

__all__ = [
    "BacktestConfigError",
    "BacktestEngineError",
    "BacktestExecutionError",
    "BacktestExecutionResult",
    "BacktestRange",
    "Candle",
    "EquityPoint",
    "ExecutionConfig",
    "InvalidMarketDatasetError",
    "LoadedMarketDataset",
    "MarketConfig",
    "MarketDatasetMetadata",
    "MarketDatasetNotFoundError",
    "NormalizedStrategyConfig",
    "RuleInstance",
    "StrategyRuleSet",
    "TradeRecord",
    "load_market_candles",
    "parse_normalized_strategy_config",
    "run_backtest",
]
