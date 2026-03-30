from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence
from uuid import NAMESPACE_URL, uuid5

from backtest_engine.data import Candle
from backtest_engine.metrics import (
    PositionSnapshot,
    build_equity_point,
    quantize_amount,
    quantize_price,
    quantize_quantity,
    quantize_rate,
)

from .errors import BacktestConfigError, BacktestExecutionError
from .models import BacktestExecutionResult, NormalizedStrategyConfig, TradeRecord
from .signals import build_signal_series


ONE = Decimal("1")
ZERO = Decimal("0")


@dataclass
class OpenPosition:
    entry_at: object
    entry_price: Decimal
    quantity: Decimal
    entry_fee_amount: Decimal
    entry_index: int
    entry_equity: Decimal


@dataclass(frozen=True)
class ExitDecision:
    price: Decimal
    reason: str


def run_backtest(
    config: NormalizedStrategyConfig,
    candles: Sequence[Candle],
) -> BacktestExecutionResult:
    _validate_config(config)
    normalized_candles = tuple(candles)
    _validate_candles(config, normalized_candles)

    entry_signals = build_signal_series(config.rules.entry, normalized_candles)
    exit_signals = build_signal_series(config.rules.exit, normalized_candles)

    cash = config.execution.initial_capital
    total_fees_paid = ZERO
    trades: list[TradeRecord] = []
    equity_curve = []
    position: OpenPosition | None = None
    last_index = len(normalized_candles) - 1

    for index, candle in enumerate(normalized_candles):
        exited_this_bar = False

        if position is not None:
            exit_decision = _resolve_risk_exit(config, position, candle)
            if exit_decision is None and exit_signals[index]:
                exit_decision = ExitDecision(price=candle.close, reason="exit_rule")
            if exit_decision is None and index == last_index:
                exit_decision = ExitDecision(price=candle.close, reason="end_of_data")

            if exit_decision is not None:
                cash, trade, exit_fee_amount = _close_position(
                    config=config,
                    cash=cash,
                    position=position,
                    exit_price=exit_decision.price,
                    exit_at=candle.ts,
                    exit_index=index,
                    exit_reason=exit_decision.reason,
                    trade_number=len(trades) + 1,
                )
                total_fees_paid += exit_fee_amount
                trades.append(trade)
                position = None
                exited_this_bar = True

        if position is None and not exited_this_bar and index < last_index and entry_signals[index]:
            position, cash, entry_fee_amount = _open_position(
                cash=cash,
                entry_price=candle.close,
                entry_at=candle.ts,
                entry_index=index,
                fee_rate=config.execution.fee_rate,
            )
            total_fees_paid += entry_fee_amount

        equity_curve.append(
            build_equity_point(
                ts=candle.ts,
                close_price=candle.close,
                cash=cash,
                position=(
                    None
                    if position is None
                    else PositionSnapshot(
                        quantity=position.quantity,
                        entry_price=position.entry_price,
                    )
                ),
            )
        )

    return BacktestExecutionResult(
        trades=tuple(trades),
        equity_curve=tuple(equity_curve),
        final_equity=equity_curve[-1].equity,
        total_fees_paid=quantize_amount(total_fees_paid),
    )


def _validate_config(config: NormalizedStrategyConfig) -> None:
    if config.market.backtest_range.start_at >= config.market.backtest_range.end_at:
        raise BacktestConfigError("market.backtest_range.end_at must be later than start_at")
    if config.execution.position_mode != "all_in":
        raise BacktestConfigError("Only execution.position_mode=all_in is supported")
    if config.execution.trade_direction != "long_only":
        raise BacktestConfigError("Only execution.trade_direction=long_only is supported")


def _validate_candles(
    config: NormalizedStrategyConfig,
    candles: tuple[Candle, ...],
) -> None:
    if not candles:
        raise BacktestExecutionError("At least one candle is required to run a backtest")

    previous_ts = None
    for candle in candles:
        if previous_ts is not None and candle.ts <= previous_ts:
            raise BacktestExecutionError("Candles must be strictly ordered by ascending ts")
        if not (config.market.backtest_range.start_at <= candle.ts < config.market.backtest_range.end_at):
            raise BacktestExecutionError("Candles must fall within config.market.backtest_range")
        previous_ts = candle.ts


def _resolve_risk_exit(
    config: NormalizedStrategyConfig,
    position: OpenPosition,
    candle: Candle,
) -> ExitDecision | None:
    if config.rules.stop_loss is not None:
        stop_loss_rate = _parse_fraction_param(
            config.rules.stop_loss.params,
            field_name="stop_loss_rate",
            rule_name="fixed_stop_loss",
        )
        stop_loss_price = position.entry_price * (ONE - stop_loss_rate)
        if candle.low <= stop_loss_price:
            return ExitDecision(price=stop_loss_price, reason="stop_loss")

    if config.rules.take_profit is not None:
        take_profit_rate = _parse_fraction_param(
            config.rules.take_profit.params,
            field_name="take_profit_rate",
            rule_name="fixed_take_profit",
        )
        take_profit_price = position.entry_price * (ONE + take_profit_rate)
        if candle.high >= take_profit_price:
            return ExitDecision(price=take_profit_price, reason="take_profit")

    return None


def _open_position(
    *,
    cash: Decimal,
    entry_price: Decimal,
    entry_at: object,
    entry_index: int,
    fee_rate: Decimal,
) -> tuple[OpenPosition, Decimal, Decimal]:
    quantity = quantize_quantity(cash / (entry_price * (ONE + fee_rate)))
    if quantity <= ZERO:
        raise BacktestExecutionError("Available cash is too small to open an all-in position")

    notional = quantity * entry_price
    entry_fee_amount = notional * fee_rate
    remaining_cash = cash - notional - entry_fee_amount

    position = OpenPosition(
        entry_at=entry_at,
        entry_price=entry_price,
        quantity=quantity,
        entry_fee_amount=entry_fee_amount,
        entry_index=entry_index,
        entry_equity=cash,
    )
    return position, remaining_cash, entry_fee_amount


def _close_position(
    *,
    config: NormalizedStrategyConfig,
    cash: Decimal,
    position: OpenPosition,
    exit_price: Decimal,
    exit_at: object,
    exit_index: int,
    exit_reason: str,
    trade_number: int,
) -> tuple[Decimal, TradeRecord, Decimal]:
    gross_proceeds = position.quantity * exit_price
    exit_fee_amount = gross_proceeds * config.execution.fee_rate
    cash_after_exit = cash + gross_proceeds - exit_fee_amount
    pnl_amount = cash_after_exit - position.entry_equity
    pnl_rate = ZERO if position.entry_equity == ZERO else pnl_amount / position.entry_equity

    trade = TradeRecord(
        trade_id=_build_trade_id(
            config=config,
            position=position,
            exit_at=exit_at,
            exit_reason=exit_reason,
            trade_number=trade_number,
        ),
        entry_at=position.entry_at,
        exit_at=exit_at,
        entry_price=quantize_price(position.entry_price),
        exit_price=quantize_price(exit_price),
        quantity=quantize_quantity(position.quantity),
        pnl_amount=quantize_amount(pnl_amount),
        pnl_rate=quantize_rate(pnl_rate),
        entry_fee_amount=quantize_amount(position.entry_fee_amount),
        exit_fee_amount=quantize_amount(exit_fee_amount),
        holding_bars=exit_index - position.entry_index,
        exit_reason=exit_reason,
    )
    return cash_after_exit, trade, exit_fee_amount


def _build_trade_id(
    *,
    config: NormalizedStrategyConfig,
    position: OpenPosition,
    exit_at: object,
    exit_reason: str,
    trade_number: int,
):
    key = "|".join(
        [
            config.market.symbol,
            config.market.timeframe,
            str(trade_number),
            str(position.entry_at),
            str(exit_at),
            str(position.entry_price),
            str(position.quantity),
            exit_reason,
        ]
    )
    return uuid5(NAMESPACE_URL, key)


def _parse_fraction_param(
    params: dict[str, object],
    *,
    field_name: str,
    rule_name: str,
) -> Decimal:
    raw_value = params.get(field_name)
    try:
        value = Decimal(str(raw_value))
    except Exception as exc:  # pragma: no cover - defensive parsing
        raise BacktestConfigError(f"{rule_name}.{field_name} must be a valid decimal value") from exc

    if value <= ZERO or value >= ONE:
        raise BacktestConfigError(f"{rule_name}.{field_name} must be between 0 and 1")
    return value
