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
    database_path = tmp_path / "history-backtests.db"
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


def test_history_returns_404_for_unknown_strategy_card(client: TestClient) -> None:
    resp = client.get("/api/backtests/strategy-cards/00000000-0000-0000-0000-000000000099/history")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "STRATEGY_CARD_NOT_FOUND"


def test_history_returns_empty_list_for_strategy_card_without_runs(client: TestClient) -> None:
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload("No Runs Strategy")).json()["data"]["id"]

    resp = client.get(f"/api/backtests/strategy-cards/{card_id}/history")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["strategy_card_id"] == card_id
    assert body["data"]["items"] == []


def test_history_returns_runs_for_strategy_card(client: TestClient) -> None:
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload("History Strategy")).json()["data"]["id"]
    run1 = client.post(f"/api/strategy-cards/{card_id}/backtests", json={}).json()["data"]
    run2 = client.post(f"/api/strategy-cards/{card_id}/backtests", json={}).json()["data"]

    resp = client.get(f"/api/backtests/strategy-cards/{card_id}/history")
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    returned_run_ids = {item["run_id"] for item in items}
    assert returned_run_ids == {run1["run_id"], run2["run_id"]}


def test_history_is_ordered_by_created_at_desc(client: TestClient) -> None:
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload("Ordered History Strategy")).json()["data"]["id"]
    older_run = client.post(f"/api/strategy-cards/{card_id}/backtests", json={}).json()["data"]
    newer_run = client.post(f"/api/strategy-cards/{card_id}/backtests", json={}).json()["data"]

    resp = client.get(f"/api/backtests/strategy-cards/{card_id}/history")
    items = resp.json()["data"]["items"]
    assert items[0]["run_id"] == newer_run["run_id"]
    assert items[1]["run_id"] == older_run["run_id"]


def test_history_returns_minimal_field_subset(client: TestClient) -> None:
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload("Minimal History Fields")).json()["data"]["id"]
    run = client.post(f"/api/strategy-cards/{card_id}/backtests", json={}).json()["data"]

    data = client.get(f"/api/backtests/strategy-cards/{card_id}/history").json()["data"]
    item = data["items"][0]

    assert data["strategy_card_id"] == card_id
    assert item["run_id"] == run["run_id"]
    assert "status" in item
    assert "result_url" in item
    assert "started_at" in item
    assert "finished_at" in item
    assert "created_at" in item

    assert "strategy_card_name" not in item
    assert "strategy_snapshot_id" not in item
    assert "error_code" not in item
    assert "error_message" not in item
