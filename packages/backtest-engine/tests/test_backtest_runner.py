from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from backtest_engine import Candle, load_market_candles, parse_normalized_strategy_config, run_backtest


REPO_ROOT = Path(__file__).resolve().parents[3]
MARKET_DATA_DIR = REPO_ROOT / "data" / "market"


def test_run_backtest_can_execute_on_standardized_fixture_data() -> None:
    candles = load_market_candles(
        symbol="BTCUSDT",
        timeframe="1D",
        version="sample-v1",
        market_data_dir=MARKET_DATA_DIR,
    ).candles
    config = parse_normalized_strategy_config(
        build_config_payload(
            start_at=candles[0].ts,
            end_at=candles[-1].ts + timedelta(days=1),
            entry_rule={
                "template_key": "rsi_threshold",
                "params": {
                    "period": 2,
                    "comparison": "lte",
                    "threshold": 71,
                },
            },
            exit_rule={
                "template_key": "rsi_threshold",
                "params": {
                    "period": 2,
                    "comparison": "gte",
                    "threshold": 99,
                },
            },
            take_profit_rule={
                "template_key": "fixed_take_profit",
                "params": {
                    "take_profit_rate": 0.015,
                },
            },
        )
    )

    result = run_backtest(config, candles)

    assert len(result.trades) == 1
    assert result.trades[0].exit_reason == "take_profit"
    assert result.equity_curve[-1].equity == result.final_equity
    assert result.final_equity > Decimal("10000")


def test_run_backtest_is_deterministic_for_same_input() -> None:
    candles = load_market_candles(
        symbol="BTCUSDT",
        timeframe="1D",
        version="sample-v1",
        market_data_dir=MARKET_DATA_DIR,
    ).candles
    config = parse_normalized_strategy_config(
        build_config_payload(
            start_at=candles[0].ts,
            end_at=candles[-1].ts + timedelta(days=1),
            entry_rule={
                "template_key": "rsi_threshold",
                "params": {
                    "period": 2,
                    "comparison": "lte",
                    "threshold": 71,
                },
            },
            exit_rule={
                "template_key": "rsi_threshold",
                "params": {
                    "period": 2,
                    "comparison": "gte",
                    "threshold": 90,
                },
            },
        )
    )

    first_result = run_backtest(config, candles)
    second_result = run_backtest(config, candles)

    assert first_result == second_result


def test_run_backtest_supports_ma_cross_entry_and_exit() -> None:
    candles = build_candles(closes=["10", "9", "8", "9", "11", "10", "8"])
    config = parse_normalized_strategy_config(
        build_config_payload(
            start_at=candles[0].ts,
            end_at=candles[-1].ts + timedelta(days=1),
            entry_rule={
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "sma",
                    "fast_period": 2,
                    "slow_period": 3,
                    "cross_direction": "golden",
                },
            },
            exit_rule={
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "sma",
                    "fast_period": 2,
                    "slow_period": 3,
                    "cross_direction": "dead",
                },
            },
        )
    )

    result = run_backtest(config, candles)

    assert len(result.trades) == 1
    assert result.trades[0].entry_at == candles[4].ts
    assert result.trades[0].exit_at == candles[6].ts
    assert result.trades[0].exit_reason == "exit_rule"
    assert result.final_equity < Decimal("10000")


def test_run_backtest_supports_rsi_threshold_entry_and_exit() -> None:
    candles = load_market_candles(
        symbol="BTCUSDT",
        timeframe="1D",
        version="sample-v1",
        market_data_dir=MARKET_DATA_DIR,
    ).candles
    config = parse_normalized_strategy_config(
        build_config_payload(
            start_at=candles[0].ts,
            end_at=candles[-1].ts + timedelta(days=1),
            entry_rule={
                "template_key": "rsi_threshold",
                "params": {
                    "period": 2,
                    "comparison": "lte",
                    "threshold": 71,
                },
            },
            exit_rule={
                "template_key": "rsi_threshold",
                "params": {
                    "period": 2,
                    "comparison": "gte",
                    "threshold": 90,
                },
            },
        )
    )

    result = run_backtest(config, candles)

    assert len(result.trades) == 1
    assert result.trades[0].entry_at == candles[2].ts
    assert result.trades[0].exit_at == candles[3].ts
    assert result.trades[0].exit_reason == "exit_rule"


def test_run_backtest_triggers_stop_loss_before_exit_rule() -> None:
    candles = build_candles(
        closes=["10", "9", "8", "9", "11", "10"],
        highs=["10.50", "9.50", "8.50", "9.50", "11.50", "10.40"],
        lows=["9.50", "8.50", "7.50", "8.50", "10.50", "9.50"],
    )
    config = parse_normalized_strategy_config(
        build_config_payload(
            start_at=candles[0].ts,
            end_at=candles[-1].ts + timedelta(days=1),
            entry_rule={
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "sma",
                    "fast_period": 2,
                    "slow_period": 3,
                    "cross_direction": "golden",
                },
            },
            exit_rule={
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "sma",
                    "fast_period": 2,
                    "slow_period": 3,
                    "cross_direction": "dead",
                },
            },
            stop_loss_rule={
                "template_key": "fixed_stop_loss",
                "params": {
                    "stop_loss_rate": 0.05,
                },
            },
        )
    )

    result = run_backtest(config, candles)

    assert len(result.trades) == 1
    assert result.trades[0].exit_reason == "stop_loss"
    assert result.trades[0].exit_price == Decimal("10.45000000")
    assert result.trades[0].holding_bars == 1


def build_candles(
    *,
    closes: list[str],
    highs: list[str] | None = None,
    lows: list[str] | None = None,
) -> tuple[Candle, ...]:
    start_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    candles: list[Candle] = []

    for index, close_value in enumerate(closes):
        close_decimal = Decimal(close_value)
        open_decimal = Decimal(closes[index - 1] if index > 0 else close_value)
        high_decimal = Decimal(highs[index]) if highs is not None else close_decimal + Decimal("0.50")
        low_decimal = Decimal(lows[index]) if lows is not None else close_decimal - Decimal("0.50")

        candles.append(
            Candle(
                ts=start_at + timedelta(days=index),
                open=open_decimal,
                high=high_decimal,
                low=low_decimal,
                close=close_decimal,
                volume=Decimal("100"),
            )
        )

    return tuple(candles)


def build_config_payload(
    *,
    start_at: datetime,
    end_at: datetime,
    entry_rule: dict[str, object],
    exit_rule: dict[str, object],
    stop_loss_rule: dict[str, object] | None = None,
    take_profit_rule: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "market": {
            "symbol": "BTCUSDT",
            "timeframe": "1D",
            "backtest_range": {
                "start_at": isoformat_z(start_at),
                "end_at": isoformat_z(end_at),
            },
        },
        "execution": {
            "initial_capital": 10000,
            "fee_rate": 0.001,
            "position_mode": "all_in",
            "trade_direction": "long_only",
        },
        "rules": {
            "entry": entry_rule,
            "exit": exit_rule,
            "stop_loss": stop_loss_rule,
            "take_profit": take_profit_rule,
        },
    }


def isoformat_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
