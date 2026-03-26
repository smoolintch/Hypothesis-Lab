from __future__ import annotations

from typing import Any

from app.application.errors import AppError
from app.domain.strategy_cards.constants import (
    ALLOWED_RULE_TEMPLATES_BY_POSITION,
    SUPPORTED_SYMBOLS,
    SUPPORTED_TIMEFRAMES,
)
from app.domain.strategy_cards.rule_templates import validate_rule_params
from app.schemas.strategy_cards import RuleInstancePayload, StrategyCardUpsertPayload


def _validate_symbol(symbol: str) -> None:
    if symbol not in SUPPORTED_SYMBOLS:
        raise AppError(
            status_code=422,
            code="UNSUPPORTED_SYMBOL",
            message="Symbol is not supported.",
            details={"symbol": symbol, "allowed_values": sorted(SUPPORTED_SYMBOLS)},
        )


def _validate_timeframe(timeframe: str) -> None:
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise AppError(
            status_code=422,
            code="UNSUPPORTED_TIMEFRAME",
            message="Timeframe is not supported.",
            details={
                "timeframe": timeframe,
                "allowed_values": sorted(SUPPORTED_TIMEFRAMES),
            },
        )


def _validate_rule_instance(position: str, rule: RuleInstancePayload) -> dict[str, Any]:
    allowed_templates = ALLOWED_RULE_TEMPLATES_BY_POSITION[position]
    if rule.template_key not in allowed_templates:
        raise AppError(
            status_code=422,
            code="RULE_TEMPLATE_INVALID",
            message="Rule template is invalid for the current position.",
            details={
                "position": position,
                "template_key": rule.template_key,
                "allowed_values": sorted(allowed_templates),
            },
        )

    try:
        normalized_params = validate_rule_params(rule.template_key, rule.params)
    except ValueError as exc:
        raise AppError(
            status_code=422,
            code="RULE_TEMPLATE_INVALID",
            message="Rule template parameters are invalid.",
            details={
                "position": position,
                "template_key": rule.template_key,
                "validation_errors": exc.args[0],
            },
        ) from exc

    return {
        "template_key": rule.template_key,
        "params": normalized_params,
    }


def validate_strategy_card_payload(
    payload: StrategyCardUpsertPayload,
) -> dict[str, Any]:
    _validate_symbol(payload.symbol)
    _validate_timeframe(payload.timeframe)

    normalized_rule_set = {
        "entry": _validate_rule_instance("entry", payload.rule_set.entry),
        "exit": _validate_rule_instance("exit", payload.rule_set.exit),
        "stop_loss": None,
        "take_profit": None,
    }

    if payload.rule_set.stop_loss is not None:
        normalized_rule_set["stop_loss"] = _validate_rule_instance(
            "stop_loss",
            payload.rule_set.stop_loss,
        )

    if payload.rule_set.take_profit is not None:
        normalized_rule_set["take_profit"] = _validate_rule_instance(
            "take_profit",
            payload.rule_set.take_profit,
        )

    return normalized_rule_set
