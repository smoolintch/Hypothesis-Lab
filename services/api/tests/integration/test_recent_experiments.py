from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[2]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

from app.infrastructure.config.settings import get_settings
from app.infrastructure.database import create_engine, create_session_factory
from app.infrastructure.database import models  # noqa: F401
from app.infrastructure.database.base import Base
from app.main import create_app


def build_strategy_payload(name: str) -> dict:
    return {
        "name": name,
        "symbol": "BTCUSDT",
        "timeframe": "4H",
        "backtest_range": {
            "start_at": "2024-01-01T00:00:00Z",
            "end_at": "2024-01-02T00:00:00Z",
        },
        "initial_capital": 10000,
        "fee_rate": 0.001,
        "rule_set": {
            "entry": {
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "ema",
                    "fast_period": 3,
                    "slow_period": 5,
                    "cross_direction": "golden",
                },
            },
            "exit": {
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "ema",
                    "fast_period": 3,
                    "slow_period": 5,
                    "cross_direction": "dead",
                },
            },
            "stop_loss": None,
            "take_profit": None,
        },
    }


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    database_path = tmp_path / "recent-experiments.db"
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


def test_recent_experiments_empty_returns_empty_list(client: TestClient) -> None:
    resp = client.get("/api/backtests/recent")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["items"] == []


def test_recent_experiments_returns_existing_runs(client: TestClient) -> None:
    first_card_id = client.post("/api/strategy-cards", json=build_strategy_payload("First Strategy")).json()["data"]["id"]
    second_card_id = client.post("/api/strategy-cards", json=build_strategy_payload("Second Strategy")).json()["data"]["id"]

    first_run = client.post(f"/api/strategy-cards/{first_card_id}/backtests", json={}).json()["data"]
    second_run = client.post(f"/api/strategy-cards/{second_card_id}/backtests", json={}).json()["data"]

    resp = client.get("/api/backtests/recent")
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    assert len(items) == 2
    returned_run_ids = {item["run_id"] for item in items}
    assert returned_run_ids == {first_run["run_id"], second_run["run_id"]}


def test_recent_experiments_ordered_by_created_at_desc(client: TestClient) -> None:
    first_card_id = client.post("/api/strategy-cards", json=build_strategy_payload("Older Strategy")).json()["data"]["id"]
    second_card_id = client.post("/api/strategy-cards", json=build_strategy_payload("Newer Strategy")).json()["data"]["id"]

    first_run = client.post(f"/api/strategy-cards/{first_card_id}/backtests", json={}).json()["data"]
    second_run = client.post(f"/api/strategy-cards/{second_card_id}/backtests", json={}).json()["data"]

    resp = client.get("/api/backtests/recent")
    items = resp.json()["data"]["items"]
    assert items[0]["run_id"] == second_run["run_id"]
    assert items[1]["run_id"] == first_run["run_id"]


def test_recent_experiments_returns_minimal_field_subset(client: TestClient) -> None:
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload("Minimal Fields Strategy")).json()["data"]["id"]
    run = client.post(f"/api/strategy-cards/{card_id}/backtests", json={}).json()["data"]

    item = client.get("/api/backtests/recent").json()["data"]["items"][0]
    assert item["run_id"] == run["run_id"]
    assert item["strategy_card_id"] == card_id
    assert item["strategy_card_name"] == "Minimal Fields Strategy"
    assert "status" in item
    assert "result_url" in item
    assert "started_at" in item
    assert "finished_at" in item
    assert "created_at" in item

    assert "strategy_snapshot_id" not in item
    assert "error_code" not in item
    assert "error_message" not in item


def test_recent_experiments_succeeded_run_has_result_url(client: TestClient) -> None:
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload("Result URL Strategy")).json()["data"]["id"]
    run = client.post(f"/api/strategy-cards/{card_id}/backtests", json={}).json()["data"]

    item = client.get("/api/backtests/recent").json()["data"]["items"][0]
    assert item["run_id"] == run["run_id"]
    assert item["result_url"] == f"/api/backtests/{run['run_id']}/result"
