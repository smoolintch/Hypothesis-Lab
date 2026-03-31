from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class HandbookCreatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conclusion_id: UUID
    memo: str | None = None

    @field_validator("memo")
    @classmethod
    def validate_memo(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("memo must be at most 2000 characters")
        return v


class HandbookEntryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    strategy_card_id: UUID
    backtest_result_id: UUID
    conclusion_id: UUID
    status: str
    memo: str | None
    created_at: datetime
    updated_at: datetime
