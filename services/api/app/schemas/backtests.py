from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BacktestRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID
    strategy_card_id: UUID
    strategy_snapshot_id: UUID
    status: str
    error_code: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    result_url: str | None
    created_at: datetime
