from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.application.errors import (
    ConclusionNotEligibleForHandbookError,
    ConclusionNotFoundError,
    HandbookEntryAlreadyExistsError,
)
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.repositories.conclusion import ConclusionRepository
from app.infrastructure.database.repositories.handbook_entry import HandbookEntryRepository
from app.schemas.handbook import HandbookCreatePayload, HandbookEntryResponse


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HandbookService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.conclusion_repo = ConclusionRepository(session)
        self.handbook_repo = HandbookEntryRepository(session)

    def add_to_handbook(self, payload: HandbookCreatePayload) -> HandbookEntryResponse:
        user_id = self.settings.default_user_id

        # 1. Verify conclusion exists for this user
        conclusion = self.conclusion_repo.get_by_id_for_user(
            conclusion_id=payload.conclusion_id,
            user_id=user_id,
        )
        if conclusion is None:
            raise ConclusionNotFoundError(str(payload.conclusion_id))

        # 2. Verify conclusion is eligible (next_action must be "add_to_handbook")
        if conclusion.next_action != "add_to_handbook":
            raise ConclusionNotEligibleForHandbookError(str(payload.conclusion_id))

        # 3. Enforce one handbook entry per conclusion
        existing = self.handbook_repo.get_by_conclusion_id_for_user(
            conclusion_id=payload.conclusion_id,
            user_id=user_id,
        )
        if existing is not None:
            raise HandbookEntryAlreadyExistsError(str(payload.conclusion_id))

        # 4. Create
        now = utc_now()
        record = self.handbook_repo.create(
            entry_id=uuid4(),
            user_id=user_id,
            strategy_card_id=conclusion.strategy_card_id,
            backtest_result_id=conclusion.backtest_result_id,
            conclusion_id=conclusion.id,
            status="active",
            memo=payload.memo,
            created_at=now,
            updated_at=now,
        )
        self.session.commit()
        return self._to_response(record)

    def _to_response(self, record) -> HandbookEntryResponse:
        return HandbookEntryResponse(
            id=record.id,
            strategy_card_id=record.strategy_card_id,
            backtest_result_id=record.backtest_result_id,
            conclusion_id=record.conclusion_id,
            status=record.status,
            memo=record.memo,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
