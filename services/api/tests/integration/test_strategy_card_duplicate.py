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


def build_payload(name: str = "Original Strategy") -> dict:
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
    database_path = tmp_path / "strategy-duplicate.db"
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


def test_duplicate_strategy_card_success(client: TestClient) -> None:
    created = client.post("/api/strategy-cards", json=build_payload())
    original = created.json()["data"]

    resp = client.post(f"/api/strategy-cards/{original['id']}/duplicate")
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True

    duplicated = body["data"]
    assert duplicated["id"] != original["id"]
    assert duplicated["name"] == original["name"]
    assert duplicated["symbol"] == original["symbol"]
    assert duplicated["timeframe"] == original["timeframe"]
    assert duplicated["backtest_range"] == original["backtest_range"]
    assert duplicated["initial_capital"] == original["initial_capital"]
    assert duplicated["fee_rate"] == original["fee_rate"]
    assert duplicated["rule_set"] == original["rule_set"]
    assert duplicated["status"] == original["status"]


def test_duplicate_strategy_card_source_not_found(client: TestClient) -> None:
    resp = client.post("/api/strategy-cards/00000000-0000-0000-0000-000000000099/duplicate")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "STRATEGY_CARD_NOT_FOUND"


def test_duplicate_strategy_card_identity_fields_are_reset(client: TestClient) -> None:
    created = client.post("/api/strategy-cards", json=build_payload())
    original = created.json()["data"]

    duplicated = client.post(f"/api/strategy-cards/{original['id']}/duplicate").json()["data"]

    assert duplicated["id"] != original["id"]
    assert duplicated["created_at"] != original["created_at"]
    assert duplicated["updated_at"] != original["updated_at"]
    assert duplicated["latest_backtest_run_id"] is None


def test_duplicate_strategy_card_does_not_copy_latest_backtest_run_id(client: TestClient) -> None:
    created = client.post("/api/strategy-cards", json=build_payload())
    original_id = created.json()["data"]["id"]

    run_resp = client.post(f"/api/strategy-cards/{original_id}/backtests", json={})
    original_run_id = run_resp.json()["data"]["run_id"]

    original_detail = client.get(f"/api/strategy-cards/{original_id}").json()["data"]
    assert original_detail["latest_backtest_run_id"] == original_run_id

    duplicated = client.post(f"/api/strategy-cards/{original_id}/duplicate").json()["data"]
    assert duplicated["latest_backtest_run_id"] is None


def test_duplicate_strategy_card_creates_independent_record(client: TestClient) -> None:
    created = client.post("/api/strategy-cards", json=build_payload("Source Card"))
    original = created.json()["data"]
    duplicated = client.post(f"/api/strategy-cards/{original['id']}/duplicate").json()["data"]

    updated_duplicate_payload = build_payload("Duplicated Edited")
    update_resp = client.put(f"/api/strategy-cards/{duplicated['id']}", json=updated_duplicate_payload)
    assert update_resp.status_code == 200

    original_after = client.get(f"/api/strategy-cards/{original['id']}").json()["data"]
    duplicate_after = client.get(f"/api/strategy-cards/{duplicated['id']}").json()["data"]

    assert original_after["name"] == "Source Card"
    assert duplicate_after["name"] == "Duplicated Edited"
