from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.handbook_entry import HandbookEntryModel


class HandbookEntryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        entry_id: UUID,
        user_id: UUID,
        strategy_card_id: UUID,
        backtest_result_id: UUID,
        conclusion_id: UUID,
        status: str,
        memo: str | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> HandbookEntryModel:
        record = HandbookEntryModel(
            id=entry_id,
            user_id=user_id,
            strategy_card_id=strategy_card_id,
            backtest_result_id=backtest_result_id,
            conclusion_id=conclusion_id,
            status=status,
            memo=memo,
            created_at=created_at,
            updated_at=updated_at,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get_by_conclusion_id_for_user(
        self,
        *,
        conclusion_id: UUID,
        user_id: UUID,
    ) -> HandbookEntryModel | None:
        return (
            self.session.query(HandbookEntryModel)
            .filter(
                HandbookEntryModel.conclusion_id == conclusion_id,
                HandbookEntryModel.user_id == user_id,
            )
            .one_or_none()
        )
