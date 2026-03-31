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


class BacktestResultNotReadyError(AppError):
    def __init__(self, run_id: str) -> None:
        super().__init__(
            status_code=409,
            code="BACKTEST_RESULT_NOT_READY",
            message="Backtest result is not ready yet.",
            details={"run_id": run_id},
        )


class BacktestResultUnavailableError(AppError):
    def __init__(self, run_id: str) -> None:
        super().__init__(
            status_code=422,
            code="BACKTEST_RESULT_UNAVAILABLE",
            message="Backtest run failed; no result is available.",
            details={"run_id": run_id},
        )


class BacktestResultNotFoundError(AppError):
    def __init__(self, result_id: str) -> None:
        super().__init__(
            status_code=404,
            code="BACKTEST_RESULT_NOT_FOUND",
            message="Backtest result was not found.",
            details={"result_id": result_id},
        )


class ConclusionAlreadyExistsError(AppError):
    def __init__(self, backtest_result_id: str) -> None:
        super().__init__(
            status_code=409,
            code="CONCLUSION_ALREADY_EXISTS",
            message="A conclusion already exists for this backtest result.",
            details={"backtest_result_id": backtest_result_id},
        )

