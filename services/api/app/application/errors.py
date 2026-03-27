from __future__ import annotations

from typing import Any


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


class StrategyCardNotFoundError(AppError):
    def __init__(self, strategy_card_id: str) -> None:
        super().__init__(
            status_code=404,
            code="STRATEGY_CARD_NOT_FOUND",
            message="Strategy card was not found.",
            details={"strategy_card_id": strategy_card_id},
        )


class BacktestRunNotFoundError(AppError):
    def __init__(self, run_id: str) -> None:
        super().__init__(
            status_code=404,
            code="BACKTEST_RUN_NOT_FOUND",
            message="Backtest run was not found.",
            details={"run_id": run_id},
        )
