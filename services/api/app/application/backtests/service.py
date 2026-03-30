from __future__ import annotations

import copy
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backtest_engine import (
    BacktestConfigError,
    BacktestExecutionError,
    BacktestExecutionResult,
    InvalidMarketDatasetError,
    MarketDatasetNotFoundError,
    NormalizedStrategyConfig,
    load_market_candles,
    parse_normalized_strategy_config,
    run_backtest,
)

from app.application.errors import (
    BacktestResultNotReadyError,
    BacktestResultUnavailableError,
    BacktestRunNotFoundError,
    StrategyCardNotFoundError,
)
from app.domain.backtests.normalized_config import build_normalized_config_from_card
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.repositories.backtest_result import BacktestResultRepository
from app.infrastructure.database.repositories.backtest_run import BacktestRunRepository
from app.infrastructure.database.repositories.strategy_card import StrategyCardRepository
from app.infrastructure.database.repositories.strategy_snapshot import StrategySnapshotRepository
from app.schemas.backtests import (
    BacktestResultResponse,
    BacktestRunResponse,
    CurvePointResponse,
    SummaryMetricsResponse,
    TradeRecordResponse,
)

from pathlib import Path

FIXTURE_DATASET_VERSION = "sample-v1"
# Resolve the repo root relative to this file so market data can be located
# regardless of how/where the backtest_engine package is installed.
_REPO_ROOT = Path(__file__).resolve().parents[5]
_MARKET_DATA_DIR = _REPO_ROOT / "data" / "market"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def coerce_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_utc_to_z(value: str) -> str:
    """Normalize '+00:00' suffix to 'Z' so the engine's date parser accepts it."""
    if value.endswith("+00:00"):
        return value[:-6] + "Z"
    return value


def _normalize_config_dates(config: dict) -> dict:
    """Return a deep copy of config with backtest_range dates normalized to 'Z' suffix."""
    config = copy.deepcopy(config)
    br = config.get("market", {}).get("backtest_range", {})
    if isinstance(br, dict):
        for key in ("start_at", "end_at"):
            if key in br and isinstance(br[key], str):
                br[key] = _normalize_utc_to_z(br[key])
    return config


class BacktestRunService:
    MAX_SNAPSHOT_VERSION_RETRIES = 3

    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.card_repo = StrategyCardRepository(session)
        self.snapshot_repo = StrategySnapshotRepository(session)
        self.run_repo = BacktestRunRepository(session)
        self.result_repo = BacktestResultRepository(session)

    def start_backtest_for_strategy_card(self, strategy_card_id: UUID) -> BacktestRunResponse:
        card = self.card_repo.get_by_id(
            strategy_card_id=strategy_card_id,
            user_id=self.settings.default_user_id,
        )
        if card is None:
            raise StrategyCardNotFoundError(str(strategy_card_id))

        normalized_config = build_normalized_config_from_card(card)
        now = utc_now()
        last_error: IntegrityError | None = None
        run = None
        snapshot_row = None

        for _ in range(self.MAX_SNAPSHOT_VERSION_RETRIES):
            version = self.snapshot_repo.next_version(strategy_card_id=card.id)
            snapshot_id = uuid4()
            run_id = uuid4()
            try:
                snapshot_row = self.snapshot_repo.create(
                    snapshot_id=snapshot_id,
                    user_id=self.settings.default_user_id,
                    strategy_card_id=card.id,
                    version=version,
                    source_strategy_updated_at=coerce_utc(card.updated_at),
                    normalized_config=normalized_config,
                    created_at=now,
                )

                run = self.run_repo.create(
                    run_id=run_id,
                    user_id=self.settings.default_user_id,
                    strategy_snapshot_id=snapshot_row.id,
                    status="queued",
                    created_at=now,
                )

                self.card_repo.update_latest_backtest_run_id(
                    record=card,
                    latest_backtest_run_id=run_id,
                )
                self.session.commit()
                break
            except IntegrityError as exc:
                self.session.rollback()
                if self._is_snapshot_version_conflict(exc):
                    last_error = exc
                    continue
                raise

        if run is None or snapshot_row is None:
            if last_error is not None:
                raise last_error
            raise RuntimeError("Backtest snapshot creation failed without an IntegrityError.")

        # Execute backtest synchronously in-process
        self._execute_and_persist_result(run, normalized_config)

        self.session.refresh(run)
        return self._to_run_response(run, snapshot_row)

    def get_run(self, run_id: UUID) -> BacktestRunResponse:
        result = self.run_repo.get_by_id_for_user(
            run_id=run_id,
            user_id=self.settings.default_user_id,
        )
        if result is None:
            raise BacktestRunNotFoundError(str(run_id))
        run, snapshot = result
        return self._to_run_response(run, snapshot)

    def get_result(self, run_id: UUID) -> BacktestResultResponse:
        result = self.run_repo.get_by_id_for_user(
            run_id=run_id,
            user_id=self.settings.default_user_id,
        )
        if result is None:
            raise BacktestRunNotFoundError(str(run_id))
        run, snapshot = result

        if run.status == "failed":
            raise BacktestResultUnavailableError(str(run_id))
        if run.status != "succeeded":
            raise BacktestResultNotReadyError(str(run_id))

        result_record = self.result_repo.get_by_run_id_for_user(
            run_id=run_id,
            user_id=self.settings.default_user_id,
        )
        if result_record is None:
            raise BacktestResultNotReadyError(str(run_id))

        return self._to_result_response(result_record, run, snapshot)

    def _execute_and_persist_result(self, run, normalized_config: dict) -> None:
        started_at = utc_now()
        try:
            engine_config = _normalize_config_dates(normalized_config)
            parsed_config: NormalizedStrategyConfig = parse_normalized_strategy_config(engine_config)

            dataset = load_market_candles(
                symbol=parsed_config.market.symbol,
                timeframe=parsed_config.market.timeframe,
                version=FIXTURE_DATASET_VERSION,
                backtest_range=parsed_config.market.backtest_range,
                market_data_dir=_MARKET_DATA_DIR,
            )

            engine_result: BacktestExecutionResult = run_backtest(parsed_config, dataset.candles)

            initial_capital = parsed_config.execution.initial_capital
            summary_metrics = _compute_summary_metrics(engine_result, initial_capital)
            equity_curve = _build_equity_curve_data(engine_result)
            drawdown_curve = _build_drawdown_curve_data(engine_result)
            trades_data = _build_trades_data(engine_result)

            finished_at = utc_now()
            self.result_repo.create(
                result_id=uuid4(),
                user_id=run.user_id,
                backtest_run_id=run.id,
                dataset_version=dataset.metadata.version,
                summary_metrics=summary_metrics,
                equity_curve=equity_curve,
                drawdown_curve=drawdown_curve,
                trades=trades_data,
                result_summary={},
                created_at=finished_at,
            )
            self.run_repo.update_status(
                run,
                status="succeeded",
                started_at=started_at,
                finished_at=finished_at,
            )
            self.session.commit()

        except (BacktestConfigError, BacktestExecutionError) as exc:
            self.session.rollback()
            self.run_repo.update_status(
                run,
                status="failed",
                started_at=started_at,
                finished_at=utc_now(),
                error_code="BACKTEST_EXECUTION_FAILED",
                error_message=str(exc)[:2000],
            )
            self.session.commit()

        except (MarketDatasetNotFoundError, InvalidMarketDatasetError) as exc:
            self.session.rollback()
            self.run_repo.update_status(
                run,
                status="failed",
                started_at=started_at,
                finished_at=utc_now(),
                error_code="BACKTEST_DATASET_UNAVAILABLE",
                error_message=str(exc)[:2000],
            )
            self.session.commit()

        except Exception as exc:
            self.session.rollback()
            self.run_repo.update_status(
                run,
                status="failed",
                started_at=started_at,
                finished_at=utc_now(),
                error_code="BACKTEST_EXECUTION_FAILED",
                error_message=f"{type(exc).__name__}: {str(exc)[:1900]}",
            )
            self.session.commit()

    def _to_run_response(self, run, snapshot) -> BacktestRunResponse:
        result_url = None
        if run.status == "succeeded":
            result_url = f"/api/backtests/{run.id}/result"
        return BacktestRunResponse(
            run_id=run.id,
            strategy_card_id=snapshot.strategy_card_id,
            strategy_snapshot_id=snapshot.id,
            status=run.status,
            error_code=run.error_code,
            error_message=run.error_message,
            started_at=coerce_utc(run.started_at) if run.started_at is not None else None,
            finished_at=coerce_utc(run.finished_at) if run.finished_at is not None else None,
            result_url=result_url,
            created_at=coerce_utc(run.created_at),
        )

    def _to_result_response(self, result_record, run, snapshot) -> BacktestResultResponse:
        return BacktestResultResponse(
            result_id=result_record.id,
            run_id=run.id,
            strategy_card_id=snapshot.strategy_card_id,
            strategy_snapshot_id=snapshot.id,
            dataset_version=result_record.dataset_version,
            summary_metrics=SummaryMetricsResponse(**result_record.summary_metrics),
            equity_curve=[CurvePointResponse(**p) for p in result_record.equity_curve],
            drawdown_curve=[CurvePointResponse(**p) for p in result_record.drawdown_curve],
            trades=[TradeRecordResponse(**t) for t in result_record.trades],
            result_summary=result_record.result_summary,
            created_at=coerce_utc(result_record.created_at),
        )

    def _is_snapshot_version_conflict(self, exc: IntegrityError) -> bool:
        message = str(exc.orig).lower()
        constraint_name = "uq_strategy_snapshots_strategy_card_id_version"
        return (
            constraint_name in message
            or "strategy_snapshots.strategy_card_id, strategy_snapshots.version" in message
            or "strategy_snapshots(strategy_card_id, version)" in message
        )


def _compute_summary_metrics(engine_result: BacktestExecutionResult, initial_capital: Decimal) -> dict:
    final_equity = engine_result.final_equity
    total_return_rate = (
        (final_equity - initial_capital) / initial_capital
        if initial_capital > Decimal("0")
        else Decimal("0")
    )

    trades = engine_result.trades
    trade_count = len(trades)
    win_rate = Decimal("0")
    profit_factor = Decimal("0")
    avg_holding_bars = Decimal("0")
    max_drawdown_rate = _compute_max_drawdown(engine_result.equity_curve)

    if trade_count > 0:
        winning = [t for t in trades if t.pnl_amount > Decimal("0")]
        losing = [t for t in trades if t.pnl_amount < Decimal("0")]
        win_rate = Decimal(str(len(winning))) / Decimal(str(trade_count))
        total_wins = sum((t.pnl_amount for t in winning), Decimal("0"))
        total_losses = abs(sum((t.pnl_amount for t in losing), Decimal("0")))
        if total_losses > Decimal("0"):
            profit_factor = total_wins / total_losses
        avg_holding_bars = (
            Decimal(str(sum(t.holding_bars for t in trades))) / Decimal(str(trade_count))
        )

    return {
        "total_return_rate": float(total_return_rate.quantize(Decimal("0.000001"))),
        "max_drawdown_rate": float(max_drawdown_rate.quantize(Decimal("0.000001"))),
        "win_rate": float(win_rate.quantize(Decimal("0.000001"))),
        "profit_factor": float(profit_factor.quantize(Decimal("0.000001"))),
        "trade_count": trade_count,
        "avg_holding_bars": float(avg_holding_bars.quantize(Decimal("0.01"))),
        "final_equity": float(final_equity),
    }


def _compute_max_drawdown(equity_curve) -> Decimal:
    if not equity_curve:
        return Decimal("0")
    peak = equity_curve[0].equity
    max_dd = Decimal("0")
    for point in equity_curve:
        if point.equity > peak:
            peak = point.equity
        if peak > Decimal("0"):
            dd = (peak - point.equity) / peak
            if dd > max_dd:
                max_dd = dd
    return max_dd


def _build_equity_curve_data(engine_result: BacktestExecutionResult) -> list[dict]:
    return [
        {"ts": point.ts.isoformat(), "value": float(point.equity)}
        for point in engine_result.equity_curve
    ]


def _build_drawdown_curve_data(engine_result: BacktestExecutionResult) -> list[dict]:
    equity_curve = engine_result.equity_curve
    if not equity_curve:
        return []
    peak = equity_curve[0].equity
    result = []
    for point in equity_curve:
        if point.equity > peak:
            peak = point.equity
        dd = Decimal("0") if peak == Decimal("0") else (peak - point.equity) / peak
        result.append({"ts": point.ts.isoformat(), "value": float(dd)})
    return result


def _build_trades_data(engine_result: BacktestExecutionResult) -> list[dict]:
    return [
        {
            "trade_id": str(trade.trade_id),
            "entry_at": trade.entry_at.isoformat(),
            "exit_at": trade.exit_at.isoformat(),
            "entry_price": float(trade.entry_price),
            "exit_price": float(trade.exit_price),
            "quantity": float(trade.quantity),
            "pnl_amount": float(trade.pnl_amount),
            "pnl_rate": float(trade.pnl_rate),
            "exit_reason": trade.exit_reason,
        }
        for trade in engine_result.trades
    ]
