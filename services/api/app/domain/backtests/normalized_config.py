from __future__ import annotations

from typing import Any

from app.infrastructure.database.models.strategy_card import StrategyCardModel


def build_normalized_config_from_card(card: StrategyCardModel) -> dict[str, Any]:
    """Build `NormalizedStrategyConfig` shape per `docs/contracts/domain-model.md` §5.4."""
    return {
        "market": {
            "symbol": card.symbol,
            "timeframe": card.timeframe,
            "backtest_range": {
                "start_at": card.backtest_range["start_at"],
                "end_at": card.backtest_range["end_at"],
            },
        },
        "execution": {
            "initial_capital": float(card.initial_capital),
            "fee_rate": float(card.fee_rate),
            "position_mode": "all_in",
            "trade_direction": "long_only",
        },
        "rules": card.rule_set,
    }
