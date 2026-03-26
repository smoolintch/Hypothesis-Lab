from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator


class RuleParamsBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MaCrossParams(RuleParamsBase):
    ma_type: str
    fast_period: int
    slow_period: int
    cross_direction: str

    @model_validator(mode="after")
    def validate_values(self) -> "MaCrossParams":
        if self.ma_type not in {"sma", "ema"}:
            raise ValueError("ma_type must be one of: sma, ema")
        if not 2 <= self.fast_period <= 200:
            raise ValueError("fast_period must be between 2 and 200")
        if not 3 <= self.slow_period <= 400:
            raise ValueError("slow_period must be between 3 and 400")
        if self.slow_period <= self.fast_period:
            raise ValueError("slow_period must be greater than fast_period")
        if self.cross_direction not in {"golden", "dead"}:
            raise ValueError("cross_direction must be one of: golden, dead")
        return self


class RsiThresholdParams(RuleParamsBase):
    period: int
    comparison: str
    threshold: float

    @model_validator(mode="after")
    def validate_values(self) -> "RsiThresholdParams":
        if not 2 <= self.period <= 100:
            raise ValueError("period must be between 2 and 100")
        if self.comparison not in {"lte", "gte"}:
            raise ValueError("comparison must be one of: lte, gte")
        if not 0 <= self.threshold <= 100:
            raise ValueError("threshold must be between 0 and 100")
        return self


class PriceBreakoutParams(RuleParamsBase):
    lookback_bars: int
    breakout_side: str

    @model_validator(mode="after")
    def validate_values(self) -> "PriceBreakoutParams":
        if not 2 <= self.lookback_bars <= 200:
            raise ValueError("lookback_bars must be between 2 and 200")
        if self.breakout_side not in {"break_high", "break_low"}:
            raise ValueError("breakout_side must be one of: break_high, break_low")
        return self


class StreakReversalParams(RuleParamsBase):
    direction: str
    streak_count: int

    @model_validator(mode="after")
    def validate_values(self) -> "StreakReversalParams":
        if self.direction not in {"up", "down"}:
            raise ValueError("direction must be one of: up, down")
        if not 2 <= self.streak_count <= 10:
            raise ValueError("streak_count must be between 2 and 10")
        return self


class FixedTakeProfitParams(RuleParamsBase):
    take_profit_rate: float

    @model_validator(mode="after")
    def validate_values(self) -> "FixedTakeProfitParams":
        if not 0 < self.take_profit_rate < 1:
            raise ValueError("take_profit_rate must be between 0 and 1")
        return self


class FixedStopLossParams(RuleParamsBase):
    stop_loss_rate: float

    @model_validator(mode="after")
    def validate_values(self) -> "FixedStopLossParams":
        if not 0 < self.stop_loss_rate < 1:
            raise ValueError("stop_loss_rate must be between 0 and 1")
        return self


RULE_TEMPLATE_PARAM_MODELS: dict[str, type[RuleParamsBase]] = {
    "ma_cross": MaCrossParams,
    "rsi_threshold": RsiThresholdParams,
    "price_breakout": PriceBreakoutParams,
    "streak_reversal": StreakReversalParams,
    "fixed_take_profit": FixedTakeProfitParams,
    "fixed_stop_loss": FixedStopLossParams,
}


def validate_rule_params(template_key: str, params: dict[str, Any]) -> dict[str, Any]:
    model = RULE_TEMPLATE_PARAM_MODELS.get(template_key)
    if model is None:
        raise ValueError(f"unsupported template_key: {template_key}")

    try:
        validated = model.model_validate(params)
    except ValidationError as exc:  # pragma: no cover - exercised via API tests
        raise ValueError(
            exc.errors(
                include_url=False,
                include_context=False,
            )
        ) from exc

    return validated.model_dump(mode="json")
