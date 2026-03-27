from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

SERVICE_ROOT = Path(__file__).resolve().parents[2]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from app.infrastructure.config.settings import get_settings
from app.infrastructure.database import create_engine, create_session_factory
from app.infrastructure.database import models  # noqa: F401
from app.infrastructure.database.base import Base
from app.main import create_app


def build_payload() -> dict[str, object]:
    return {
        "name": "EMA Breakout Draft",
        "symbol": "BTCUSDT",
        "timeframe": "4H",
        "backtest_range": {
            "start_at": "2023-01-01T00:00:00Z",
            "end_at": "2024-01-01T00:00:00Z",
        },
        "initial_capital": 10000,
        "fee_rate": 0.001,
        "rule_set": {
            "entry": {
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "ema",
                    "fast_period": 20,
                    "slow_period": 50,
                    "cross_direction": "golden",
                },
            },
            "exit": {
                "template_key": "rsi_threshold",
                "params": {
                    "period": 14,
                    "comparison": "gte",
                    "threshold": 70,
                },
            },
            "stop_loss": {
                "template_key": "fixed_stop_loss",
                "params": {
                    "stop_loss_rate": 0.08,
                },
            },
            "take_profit": None,
        },
    }


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    database_path = tmp_path / "backtests-placeholder.db"
    database_url = f"sqlite+pysqlite:///{database_path}"

    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("APP_USER_MODE", "single_user")
    monkeypatch.setenv("DEFAULT_USER_ID", "00000000-0000-0000-0000-000000000001")

    get_settings.cache_clear()
    create_engine.cache_clear()
    create_session_factory.cache_clear()

    engine = create_engine()
    Base.metadata.create_all(bind=engine)

    app = create_app()

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    get_settings.cache_clear()
    create_engine.cache_clear()
    create_session_factory.cache_clear()


def test_start_backtest_placeholder_creates_snapshot_and_run(client: TestClient) -> None:
    created = client.post("/api/strategy-cards", json=build_payload())
    assert created.status_code == 201
    strategy_card_id = created.json()["data"]["id"]

    start = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    assert start.status_code == 202
    body = start.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] == "queued"
    assert data["result_url"] is None
    assert data["error_code"] is None
    assert data["error_message"] is None
    assert data["started_at"] is None
    assert data["finished_at"] is None
    assert data["strategy_card_id"] == strategy_card_id

    run_id = data["run_id"]
    poll = client.get(f"/api/backtests/{run_id}")
    assert poll.status_code == 200
    polled = poll.json()["data"]
    assert polled["run_id"] == run_id
    assert polled["strategy_snapshot_id"] == data["strategy_snapshot_id"]
    assert polled["status"] == "queued"

    detail = client.get(f"/api/strategy-cards/{strategy_card_id}")
    assert detail.status_code == 200
    assert detail.json()["data"]["latest_backtest_run_id"] == run_id


def test_snapshot_version_increments_on_second_backtest(client: TestClient) -> None:
    created = client.post("/api/strategy-cards", json=build_payload())
    strategy_card_id = created.json()["data"]["id"]

    first = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={}).json()[
        "data"
    ]
    second = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={}).json()[
        "data"
    ]

    assert first["strategy_snapshot_id"] != second["strategy_snapshot_id"]
    assert first["run_id"] != second["run_id"]
    assert client.get(f"/api/strategy-cards/{strategy_card_id}").json()["data"][
        "latest_backtest_run_id"
    ] == second["run_id"]


def test_backtest_run_not_found(client: TestClient) -> None:
    missing = UUID("00000000-0000-0000-0000-000000000099")
    response = client.get(f"/api/backtests/{missing}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "BACKTEST_RUN_NOT_FOUND"


def test_start_backtest_unknown_strategy_card(client: TestClient) -> None:
    missing = "00000000-0000-0000-0000-000000000099"
    response = client.post(f"/api/strategy-cards/{missing}/backtests", json={})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "STRATEGY_CARD_NOT_FOUND"


def test_start_backtest_retries_when_snapshot_version_conflicts(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created = client.post("/api/strategy-cards", json=build_payload())
    assert created.status_code == 201
    strategy_card_id = created.json()["data"]["id"]

    from app.infrastructure.database.repositories.strategy_snapshot import (
        StrategySnapshotRepository,
    )

    original_create = StrategySnapshotRepository.create
    create_calls = {"count": 0}

    def conflict_then_succeed(self, **kwargs):
        create_calls["count"] += 1
        if create_calls["count"] == 1:
            raise IntegrityError(
                statement="INSERT INTO strategy_snapshots ...",
                params={},
                orig=Exception(
                    "UNIQUE constraint failed: "
                    "strategy_snapshots.strategy_card_id, strategy_snapshots.version"
                ),
            )
        return original_create(self, **kwargs)

    monkeypatch.setattr(
        "app.infrastructure.database.repositories.strategy_snapshot.StrategySnapshotRepository.create",
        conflict_then_succeed,
    )

    response = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    assert response.status_code == 202
    body = response.json()["data"]
    assert body["strategy_card_id"] == strategy_card_id
    assert body["status"] == "queued"
    assert create_calls["count"] == 2

    detail = client.get(f"/api/strategy-cards/{strategy_card_id}")
    assert detail.status_code == 200
    assert detail.json()["data"]["latest_backtest_run_id"] == body["run_id"]
