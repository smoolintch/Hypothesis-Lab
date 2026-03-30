from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from backtest_engine.core.models import EquityPoint


AMOUNT_QUANTIZER = Decimal("0.000001")
PRICE_QUANTIZER = Decimal("0.00000001")
QUANTITY_QUANTIZER = Decimal("0.00000001")
RATE_QUANTIZER = Decimal("0.000001")


@dataclass(frozen=True)
class PositionSnapshot:
    quantity: Decimal
    entry_price: Decimal


def build_equity_point(
    *,
    ts: datetime,
    close_price: Decimal,
    cash: Decimal,
    position: PositionSnapshot | None,
) -> EquityPoint:
    if position is None:
        position_quantity = Decimal("0")
        position_market_value = Decimal("0")
    else:
        position_quantity = position.quantity
        position_market_value = position.quantity * close_price

    equity = cash + position_market_value

    return EquityPoint(
        ts=ts,
        close_price=quantize_price(close_price),
        cash=quantize_amount(cash),
        position_quantity=quantize_quantity(position_quantity),
        position_market_value=quantize_amount(position_market_value),
        equity=quantize_amount(equity),
    )


def quantize_amount(value: Decimal) -> Decimal:
    return value.quantize(AMOUNT_QUANTIZER, rounding=ROUND_HALF_UP)


def quantize_price(value: Decimal) -> Decimal:
    return value.quantize(PRICE_QUANTIZER, rounding=ROUND_HALF_UP)


def quantize_quantity(value: Decimal) -> Decimal:
    return value.quantize(QUANTITY_QUANTIZER, rounding=ROUND_DOWN)


def quantize_rate(value: Decimal) -> Decimal:
    return value.quantize(RATE_QUANTIZER, rounding=ROUND_HALF_UP)
