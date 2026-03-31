from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

VALID_NEXT_ACTIONS = ("rerun", "refine_rules", "observe_only", "add_to_handbook", "discard")


class ConclusionUpsertPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backtest_result_id: UUID
    is_worth_researching: bool
    can_accept_drawdown: bool
    market_condition_notes: str | None = None
    next_action: Literal["rerun", "refine_rules", "observe_only", "add_to_handbook", "discard"]
    notes: str | None = None

    @field_validator("market_condition_notes")
    @classmethod
    def validate_market_condition_notes(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("market_condition_notes must be at most 2000 characters")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 4000:
            raise ValueError("notes must be at most 4000 characters")
        return v


class ConclusionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    strategy_card_id: UUID
    backtest_result_id: UUID
    is_worth_researching: bool
    can_accept_drawdown: bool
    market_condition_notes: str | None
    next_action: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
