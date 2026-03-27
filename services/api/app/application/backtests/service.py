from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.errors import BacktestRunNotFoundError, StrategyCardNotFoundError
from app.domain.backtests.normalized_config import build_normalized_config_from_card
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.repositories.backtest_run import BacktestRunRepository
from app.infrastructure.database.repositories.strategy_card import StrategyCardRepository
from app.infrastructure.database.repositories.strategy_snapshot import StrategySnapshotRepository
from app.schemas.backtests import BacktestRunResponse


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def coerce_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class BacktestRunService:
    MAX_SNAPSHOT_VERSION_RETRIES = 3

    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.card_repo = StrategyCardRepository(session)
        self.snapshot_repo = StrategySnapshotRepository(session)
        self.run_repo = BacktestRunRepository(session)

    def start_backtest_for_strategy_card(self, strategy_card_id: UUID) -> BacktestRunResponse:
        card = self.card_repo.get_by_id(
            strategy_card_id=strategy_card_id,
            user_id=self.settings.default_user_id,
        )
        if card is None:
            raise StrategyCardNotFoundError(str(strategy_card_id))

        normalized_config = build_normalized_config_from_card(card)
        now = utc_now()
        last_error: IntegrityError | None = None

        for _ in range(self.MAX_SNAPSHOT_VERSION_RETRIES):
            version = self.snapshot_repo.next_version(strategy_card_id=card.id)
            snapshot_id = uuid4()
            run_id = uuid4()
            try:
                snapshot_row = self.snapshot_repo.create(
                    snapshot_id=snapshot_id,
                    user_id=self.settings.default_user_id,
                    strategy_card_id=card.id,
                    version=version,
                    source_strategy_updated_at=coerce_utc(card.updated_at),
                    normalized_config=normalized_config,
                    created_at=now,
                )

                run = self.run_repo.create(
                    run_id=run_id,
                    user_id=self.settings.default_user_id,
                    strategy_snapshot_id=snapshot_row.id,
                    status="queued",
                    created_at=now,
                )

                self.card_repo.update_latest_backtest_run_id(
                    record=card,
                    latest_backtest_run_id=run_id,
                )
                self.session.commit()
                self.session.refresh(run)
                return self._to_response(run, snapshot_row)
            except IntegrityError as exc:
                self.session.rollback()
                if self._is_snapshot_version_conflict(exc):
                    last_error = exc
                    continue
                raise

        if last_error is not None:
            raise last_error
        raise RuntimeError("Backtest snapshot creation failed without an IntegrityError.")

    def get_run(self, run_id: UUID) -> BacktestRunResponse:
        result = self.run_repo.get_by_id_for_user(
            run_id=run_id,
            user_id=self.settings.default_user_id,
        )
        if result is None:
            raise BacktestRunNotFoundError(str(run_id))
        run, snapshot = result
        return self._to_response(run, snapshot)

    def _to_response(self, run, snapshot) -> BacktestRunResponse:
        return BacktestRunResponse(
            run_id=run.id,
            strategy_card_id=snapshot.strategy_card_id,
            strategy_snapshot_id=snapshot.id,
            status=run.status,
            error_code=run.error_code,
            error_message=run.error_message,
            started_at=coerce_utc(run.started_at) if run.started_at is not None else None,
            finished_at=coerce_utc(run.finished_at) if run.finished_at is not None else None,
            result_url=None,
            created_at=coerce_utc(run.created_at),
        )

    def _is_snapshot_version_conflict(self, exc: IntegrityError) -> bool:
        message = str(exc.orig).lower()
        constraint_name = "uq_strategy_snapshots_strategy_card_id_version"
        return (
            constraint_name in message
            or "strategy_snapshots.strategy_card_id, strategy_snapshots.version" in message
            or "strategy_snapshots(strategy_card_id, version)" in message
        )
