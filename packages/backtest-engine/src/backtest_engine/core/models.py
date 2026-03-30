from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping
from uuid import UUID

from backtest_engine.data import BacktestRange

from .errors import BacktestConfigError


@dataclass(frozen=True)
class RuleInstance:
    template_key: str
    params: dict[str, Any]


@dataclass(frozen=True)
class StrategyRuleSet:
    entry: RuleInstance
    exit: RuleInstance
    stop_loss: RuleInstance | None
    take_profit: RuleInstance | None


@dataclass(frozen=True)
class MarketConfig:
    symbol: str
    timeframe: str
    backtest_range: BacktestRange


@dataclass(frozen=True)
class ExecutionConfig:
    initial_capital: Decimal
    fee_rate: Decimal
    position_mode: str
    trade_direction: str


@dataclass(frozen=True)
class NormalizedStrategyConfig:
    market: MarketConfig
    execution: ExecutionConfig
    rules: StrategyRuleSet

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "NormalizedStrategyConfig":
        market_payload = _require_mapping(payload, "market")
        execution_payload = _require_mapping(payload, "execution")
        rules_payload = _require_mapping(payload, "rules")

        backtest_range_payload = _require_mapping(market_payload, "backtest_range")
        market = MarketConfig(
            symbol=_require_str(market_payload, "symbol"),
            timeframe=_require_str(market_payload, "timeframe"),
            backtest_range=BacktestRange(
                start_at=_parse_utc_datetime(
                    backtest_range_payload.get("start_at"),
                    field_name="market.backtest_range.start_at",
                ),
                end_at=_parse_utc_datetime(
                    backtest_range_payload.get("end_at"),
                    field_name="market.backtest_range.end_at",
                ),
            ),
        )

        initial_capital = _parse_decimal(
            execution_payload.get("initial_capital"),
            field_name="execution.initial_capital",
        )
        if initial_capital <= Decimal("0"):
            raise BacktestConfigError("execution.initial_capital must be greater than 0")

        fee_rate = _parse_decimal(
            execution_payload.get("fee_rate"),
            field_name="execution.fee_rate",
        )
        if fee_rate < Decimal("0") or fee_rate >= Decimal("1"):
            raise BacktestConfigError("execution.fee_rate must be between 0 and 1")

        execution = ExecutionConfig(
            initial_capital=initial_capital,
            fee_rate=fee_rate,
            position_mode=_require_str(execution_payload, "position_mode"),
            trade_direction=_require_str(execution_payload, "trade_direction"),
        )

        rules = StrategyRuleSet(
            entry=_parse_rule_instance(
                rules_payload.get("entry"),
                field_name="rules.entry",
                allowed_templates={"ma_cross", "rsi_threshold"},
            ),
            exit=_parse_rule_instance(
                rules_payload.get("exit"),
                field_name="rules.exit",
                allowed_templates={"ma_cross", "rsi_threshold"},
            ),
            stop_loss=_parse_optional_rule_instance(
                rules_payload.get("stop_loss"),
                field_name="rules.stop_loss",
                allowed_templates={"fixed_stop_loss"},
            ),
            take_profit=_parse_optional_rule_instance(
                rules_payload.get("take_profit"),
                field_name="rules.take_profit",
                allowed_templates={"fixed_take_profit"},
            ),
        )

        return cls(market=market, execution=execution, rules=rules)


@dataclass(frozen=True)
class TradeRecord:
    trade_id: UUID
    entry_at: datetime
    exit_at: datetime
    entry_price: Decimal
    exit_price: Decimal
    quantity: Decimal
    pnl_amount: Decimal
    pnl_rate: Decimal
    entry_fee_amount: Decimal
    exit_fee_amount: Decimal
    holding_bars: int
    exit_reason: str


@dataclass(frozen=True)
class EquityPoint:
    ts: datetime
    close_price: Decimal
    cash: Decimal
    position_quantity: Decimal
    position_market_value: Decimal
    equity: Decimal


@dataclass(frozen=True)
class BacktestExecutionResult:
    trades: tuple[TradeRecord, ...]
    equity_curve: tuple[EquityPoint, ...]
    final_equity: Decimal
    total_fees_paid: Decimal


def parse_normalized_strategy_config(payload: Mapping[str, Any]) -> NormalizedStrategyConfig:
    return NormalizedStrategyConfig.from_dict(payload)


def _parse_rule_instance(
    payload: Any,
    *,
    field_name: str,
    allowed_templates: set[str],
) -> RuleInstance:
    payload_mapping = _require_mapping_from_value(payload, field_name=field_name)
    template_key = _require_str(payload_mapping, "template_key", prefix=field_name)
    if template_key not in allowed_templates:
        allowed = ", ".join(sorted(allowed_templates))
        raise BacktestConfigError(f"{field_name}.template_key must be one of: {allowed}")

    params = _require_mapping(payload_mapping, "params", prefix=field_name)
    return RuleInstance(template_key=template_key, params=dict(params))


def _parse_optional_rule_instance(
    payload: Any,
    *,
    field_name: str,
    allowed_templates: set[str],
) -> RuleInstance | None:
    if payload is None:
        return None
    return _parse_rule_instance(
        payload,
        field_name=field_name,
        allowed_templates=allowed_templates,
    )


def _require_mapping(
    payload: Mapping[str, Any],
    field_name: str,
    *,
    prefix: str | None = None,
) -> Mapping[str, Any]:
    value = payload.get(field_name)
    return _require_mapping_from_value(value, field_name=_join_field_name(prefix, field_name))


def _require_mapping_from_value(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BacktestConfigError(f"{field_name} must be an object")
    return value


def _require_str(
    payload: Mapping[str, Any],
    field_name: str,
    *,
    prefix: str | None = None,
) -> str:
    value = payload.get(field_name)
    full_name = _join_field_name(prefix, field_name)
    if not isinstance(value, str) or not value:
        raise BacktestConfigError(f"{full_name} must be a non-empty string")
    return value


def _parse_decimal(value: Any, *, field_name: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise BacktestConfigError(f"{field_name} must be a valid decimal value") from exc
    return parsed


def _parse_utc_datetime(value: Any, *, field_name: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.endswith("Z"):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise BacktestConfigError(f"{field_name} must be a UTC ISO 8601 string")

    if parsed.tzinfo != timezone.utc:
        raise BacktestConfigError(f"{field_name} must be normalized to UTC")
    return parsed


def _join_field_name(prefix: str | None, field_name: str) -> str:
    if prefix is None:
        return field_name
    return f"{prefix}.{field_name}"
