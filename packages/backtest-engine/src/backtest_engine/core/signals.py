from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Sequence

from backtest_engine.data import Candle

from .errors import BacktestConfigError
from .models import RuleInstance


def build_signal_series(rule: RuleInstance, candles: Sequence[Candle]) -> tuple[bool, ...]:
    closes = tuple(candle.close for candle in candles)

    if rule.template_key == "ma_cross":
        return _build_ma_cross_signal_series(closes, rule.params)

    if rule.template_key == "rsi_threshold":
        return _build_rsi_threshold_signal_series(closes, rule.params)

    raise BacktestConfigError(f"Unsupported signal template_key: {rule.template_key}")


def _build_ma_cross_signal_series(
    closes: Sequence[Decimal],
    params: dict[str, object],
) -> tuple[bool, ...]:
    ma_type = _require_str_param(params, "ma_type", allowed={"sma", "ema"})
    fast_period = _require_int_param(params, "fast_period", minimum=2)
    slow_period = _require_int_param(params, "slow_period", minimum=3)
    cross_direction = _require_str_param(
        params,
        "cross_direction",
        allowed={"golden", "dead"},
    )

    if slow_period <= fast_period:
        raise BacktestConfigError("ma_cross.slow_period must be greater than fast_period")

    fast_series = build_moving_average_series(
        closes,
        period=fast_period,
        ma_type=ma_type,
    )
    slow_series = build_moving_average_series(
        closes,
        period=slow_period,
        ma_type=ma_type,
    )

    signals: list[bool] = [False] * len(closes)
    for index in range(1, len(closes)):
        prev_fast = fast_series[index - 1]
        prev_slow = slow_series[index - 1]
        current_fast = fast_series[index]
        current_slow = slow_series[index]
        if None in (prev_fast, prev_slow, current_fast, current_slow):
            continue

        if cross_direction == "golden":
            signals[index] = prev_fast <= prev_slow and current_fast > current_slow
        else:
            signals[index] = prev_fast >= prev_slow and current_fast < current_slow

    return tuple(signals)


def _build_rsi_threshold_signal_series(
    closes: Sequence[Decimal],
    params: dict[str, object],
) -> tuple[bool, ...]:
    period = _require_int_param(params, "period", minimum=2)
    comparison = _require_str_param(params, "comparison", allowed={"lte", "gte"})
    threshold = _require_decimal_param(params, "threshold")

    rsi_values = build_rsi_series(closes, period=period)

    signals: list[bool] = [False] * len(closes)
    for index, rsi in enumerate(rsi_values):
        if rsi is None:
            continue
        if comparison == "lte":
            signals[index] = rsi <= threshold
        else:
            signals[index] = rsi >= threshold

    return tuple(signals)


def build_moving_average_series(
    closes: Sequence[Decimal],
    *,
    period: int,
    ma_type: str,
) -> tuple[Decimal | None, ...]:
    if ma_type == "sma":
        return _build_sma_series(closes, period=period)
    if ma_type == "ema":
        return _build_ema_series(closes, period=period)
    raise BacktestConfigError(f"Unsupported moving average type: {ma_type}")


def build_rsi_series(
    closes: Sequence[Decimal],
    *,
    period: int,
) -> tuple[Decimal | None, ...]:
    series: list[Decimal | None] = [None] * len(closes)
    if len(closes) <= period:
        return tuple(series)

    gains: list[Decimal] = []
    losses: list[Decimal] = []
    for index in range(1, len(closes)):
        change = closes[index] - closes[index - 1]
        gains.append(change if change > Decimal("0") else Decimal("0"))
        losses.append(-change if change < Decimal("0") else Decimal("0"))

    avg_gain = sum(gains[:period], Decimal("0")) / Decimal(period)
    avg_loss = sum(losses[:period], Decimal("0")) / Decimal(period)
    series[period] = _calculate_rsi(avg_gain, avg_loss)

    for gain, loss, index in zip(gains[period:], losses[period:], range(period + 1, len(closes))):
        avg_gain = ((avg_gain * Decimal(period - 1)) + gain) / Decimal(period)
        avg_loss = ((avg_loss * Decimal(period - 1)) + loss) / Decimal(period)
        series[index] = _calculate_rsi(avg_gain, avg_loss)

    return tuple(series)


def _build_sma_series(closes: Sequence[Decimal], *, period: int) -> tuple[Decimal | None, ...]:
    series: list[Decimal | None] = [None] * len(closes)
    if len(closes) < period:
        return tuple(series)

    window_sum = sum(closes[:period], Decimal("0"))
    series[period - 1] = window_sum / Decimal(period)

    for index in range(period, len(closes)):
        window_sum += closes[index] - closes[index - period]
        series[index] = window_sum / Decimal(period)

    return tuple(series)


def _build_ema_series(closes: Sequence[Decimal], *, period: int) -> tuple[Decimal | None, ...]:
    series: list[Decimal | None] = [None] * len(closes)
    if len(closes) < period:
        return tuple(series)

    multiplier = Decimal("2") / Decimal(period + 1)
    initial_value = sum(closes[:period], Decimal("0")) / Decimal(period)
    series[period - 1] = initial_value

    ema = initial_value
    for index in range(period, len(closes)):
        ema = ((closes[index] - ema) * multiplier) + ema
        series[index] = ema

    return tuple(series)


def _calculate_rsi(avg_gain: Decimal, avg_loss: Decimal) -> Decimal:
    if avg_loss == Decimal("0"):
        if avg_gain == Decimal("0"):
            return Decimal("50")
        return Decimal("100")
    if avg_gain == Decimal("0"):
        return Decimal("0")

    relative_strength = avg_gain / avg_loss
    return Decimal("100") - (Decimal("100") / (Decimal("1") + relative_strength))


def _require_str_param(
    params: dict[str, object],
    field_name: str,
    *,
    allowed: set[str] | None = None,
) -> str:
    value = params.get(field_name)
    if not isinstance(value, str) or not value:
        raise BacktestConfigError(f"{field_name} must be a non-empty string")
    if allowed is not None and value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise BacktestConfigError(f"{field_name} must be one of: {allowed_values}")
    return value


def _require_int_param(
    params: dict[str, object],
    field_name: str,
    *,
    minimum: int,
) -> int:
    value = params.get(field_name)
    if not isinstance(value, int):
        raise BacktestConfigError(f"{field_name} must be an integer")
    if value < minimum:
        raise BacktestConfigError(f"{field_name} must be greater than or equal to {minimum}")
    return value


def _require_decimal_param(params: dict[str, object], field_name: str) -> Decimal:
    value = params.get(field_name)
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise BacktestConfigError(f"{field_name} must be a valid decimal value") from exc
