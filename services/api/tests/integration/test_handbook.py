from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

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


def build_strategy_payload() -> dict:
    return {
        "name": "Handbook Test Strategy",
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
    database_path = tmp_path / "handbook.db"
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


@pytest.fixture
def eligible_conclusion_id(client: TestClient) -> str:
    """Create a full chain (card → backtest → result → conclusion with add_to_handbook) and return conclusion id."""
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload()).json()["data"]["id"]

    run_resp = client.post(f"/api/strategy-cards/{card_id}/backtests", json={})
    assert run_resp.json()["data"]["status"] == "succeeded"
    run_id = run_resp.json()["data"]["run_id"]

    result_id = client.get(f"/api/backtests/{run_id}/result").json()["data"]["result_id"]

    conclusion_payload = {
        "backtest_result_id": result_id,
        "is_worth_researching": True,
        "can_accept_drawdown": True,
        "next_action": "add_to_handbook",
        "notes": "Ready for handbook",
    }
    conclusion_resp = client.post(f"/api/strategy-cards/{card_id}/conclusions", json=conclusion_payload)
    assert conclusion_resp.status_code == 201
    return conclusion_resp.json()["data"]["id"]


def test_add_to_handbook_success(client: TestClient, eligible_conclusion_id: str) -> None:
    payload = {"conclusion_id": eligible_conclusion_id, "memo": "Strong trend strategy"}
    resp = client.post("/api/handbook", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True

    data = body["data"]
    assert data["conclusion_id"] == eligible_conclusion_id
    assert data["status"] == "active"
    assert data["memo"] == "Strong trend strategy"
    assert "id" in data
    assert "strategy_card_id" in data
    assert "backtest_result_id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_add_to_handbook_without_memo(client: TestClient, eligible_conclusion_id: str) -> None:
    payload = {"conclusion_id": eligible_conclusion_id}
    resp = client.post("/api/handbook", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["memo"] is None
    assert data["status"] == "active"


def test_add_to_handbook_duplicate_returns_409(client: TestClient, eligible_conclusion_id: str) -> None:
    payload = {"conclusion_id": eligible_conclusion_id}
    first = client.post("/api/handbook", json=payload)
    assert first.status_code == 201

    second = client.post("/api/handbook", json=payload)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "HANDBOOK_ENTRY_ALREADY_EXISTS"


def test_add_to_handbook_unknown_conclusion_returns_404(client: TestClient) -> None:
    missing = "00000000-0000-0000-0000-000000000099"
    resp = client.post("/api/handbook", json={"conclusion_id": missing})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "CONCLUSION_NOT_FOUND"


def test_add_to_handbook_ineligible_conclusion_returns_422(client: TestClient) -> None:
    """A conclusion with next_action != 'add_to_handbook' must be rejected."""
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload()).json()["data"]["id"]
    run_resp = client.post(f"/api/strategy-cards/{card_id}/backtests", json={})
    assert run_resp.json()["data"]["status"] == "succeeded"
    run_id = run_resp.json()["data"]["run_id"]
    result_id = client.get(f"/api/backtests/{run_id}/result").json()["data"]["result_id"]

    conclusion_payload = {
        "backtest_result_id": result_id,
        "is_worth_researching": False,
        "can_accept_drawdown": False,
        "next_action": "discard",
    }
    conclusion_id = client.post(
        f"/api/strategy-cards/{card_id}/conclusions", json=conclusion_payload
    ).json()["data"]["id"]

    resp = client.post("/api/handbook", json={"conclusion_id": conclusion_id})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "CONCLUSION_NOT_ELIGIBLE_FOR_HANDBOOK"


def test_add_to_handbook_memo_too_long_returns_422(client: TestClient, eligible_conclusion_id: str) -> None:
    payload = {"conclusion_id": eligible_conclusion_id, "memo": "x" * 2001}
    resp = client.post("/api/handbook", json=payload)
    assert resp.status_code == 422


def test_handbook_response_has_correct_linked_ids(client: TestClient) -> None:
    """HandbookEntry must echo back strategy_card_id and backtest_result_id from the conclusion chain."""
    card_id = client.post("/api/strategy-cards", json=build_strategy_payload()).json()["data"]["id"]
    run_resp = client.post(f"/api/strategy-cards/{card_id}/backtests", json={})
    assert run_resp.json()["data"]["status"] == "succeeded"
    run_id = run_resp.json()["data"]["run_id"]
    result_id = client.get(f"/api/backtests/{run_id}/result").json()["data"]["result_id"]

    conclusion_payload = {
        "backtest_result_id": result_id,
        "is_worth_researching": True,
        "can_accept_drawdown": True,
        "next_action": "add_to_handbook",
    }
    conclusion_data = client.post(
        f"/api/strategy-cards/{card_id}/conclusions", json=conclusion_payload
    ).json()["data"]

    entry = client.post("/api/handbook", json={"conclusion_id": conclusion_data["id"]}).json()["data"]

    assert entry["strategy_card_id"] == card_id
    assert entry["backtest_result_id"] == result_id
    assert entry["conclusion_id"] == conclusion_data["id"]
