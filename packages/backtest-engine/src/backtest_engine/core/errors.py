class BacktestEngineError(Exception):
    """Base exception for backtest engine errors."""


class BacktestConfigError(BacktestEngineError):
    """Raised when normalized config violates engine constraints."""


class BacktestExecutionError(BacktestEngineError):
    """Raised when runtime inputs prevent a backtest from executing."""
