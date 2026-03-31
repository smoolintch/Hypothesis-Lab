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
        "name": "Conclusion Test Strategy",
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


def build_conclusion_payload(backtest_result_id: str) -> dict:
    return {
        "backtest_result_id": backtest_result_id,
        "is_worth_researching": True,
        "can_accept_drawdown": False,
        "market_condition_notes": "Works best in trending markets",
        "next_action": "refine_rules",
        "notes": "MA parameters might need tuning",
    }


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    database_path = tmp_path / "conclusions.db"
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
def strategy_card_with_result(client: TestClient) -> tuple[str, str]:
    """Create a strategy card, run a backtest, return (strategy_card_id, backtest_result_id)."""
    created = client.post("/api/strategy-cards", json=build_strategy_payload())
    assert created.status_code == 201
    strategy_card_id = created.json()["data"]["id"]

    start = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    assert start.status_code == 202
    run_data = start.json()["data"]
    assert run_data["status"] == "succeeded", f"Backtest failed: {run_data}"

    run_id = run_data["run_id"]
    result_resp = client.get(f"/api/backtests/{run_id}/result")
    assert result_resp.status_code == 200
    backtest_result_id = result_resp.json()["data"]["result_id"]

    return strategy_card_id, backtest_result_id


def test_create_conclusion_success(
    client: TestClient,
    strategy_card_with_result: tuple[str, str],
) -> None:
    strategy_card_id, backtest_result_id = strategy_card_with_result
    payload = build_conclusion_payload(backtest_result_id)

    resp = client.post(f"/api/strategy-cards/{strategy_card_id}/conclusions", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True

    data = body["data"]
    assert data["strategy_card_id"] == strategy_card_id
    assert data["backtest_result_id"] == backtest_result_id
    assert data["is_worth_researching"] is True
    assert data["can_accept_drawdown"] is False
    assert data["market_condition_notes"] == "Works best in trending markets"
    assert data["next_action"] == "refine_rules"
    assert data["notes"] == "MA parameters might need tuning"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_conclusion_minimal_fields(
    client: TestClient,
    strategy_card_with_result: tuple[str, str],
) -> None:
    """Only required fields - optional fields default to None."""
    strategy_card_id, backtest_result_id = strategy_card_with_result
    payload = {
        "backtest_result_id": backtest_result_id,
        "is_worth_researching": False,
        "can_accept_drawdown": True,
        "next_action": "discard",
    }

    resp = client.post(f"/api/strategy-cards/{strategy_card_id}/conclusions", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["is_worth_researching"] is False
    assert data["can_accept_drawdown"] is True
    assert data["next_action"] == "discard"
    assert data["market_condition_notes"] is None
    assert data["notes"] is None


def test_create_conclusion_all_next_action_values(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each valid next_action value must be accepted."""
    valid_actions = ["rerun", "refine_rules", "observe_only", "add_to_handbook", "discard"]

    for action in valid_actions:
        # Create fresh client for each to avoid conflicts
        database_path = tmp_path / f"conclusions_{action}.db"
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

        with TestClient(app) as c:
            card_resp = c.post("/api/strategy-cards", json=build_strategy_payload())
            card_id = card_resp.json()["data"]["id"]
            run_resp = c.post(f"/api/strategy-cards/{card_id}/backtests", json={})
            assert run_resp.json()["data"]["status"] == "succeeded"
            run_id = run_resp.json()["data"]["run_id"]
            result_id = c.get(f"/api/backtests/{run_id}/result").json()["data"]["result_id"]

            payload = {
                "backtest_result_id": result_id,
                "is_worth_researching": True,
                "can_accept_drawdown": True,
                "next_action": action,
            }
            resp = c.post(f"/api/strategy-cards/{card_id}/conclusions", json=payload)
            assert resp.status_code == 201, f"Failed for next_action={action}: {resp.json()}"

        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_create_conclusion_duplicate_returns_409(
    client: TestClient,
    strategy_card_with_result: tuple[str, str],
) -> None:
    strategy_card_id, backtest_result_id = strategy_card_with_result
    payload = build_conclusion_payload(backtest_result_id)

    first = client.post(f"/api/strategy-cards/{strategy_card_id}/conclusions", json=payload)
    assert first.status_code == 201

    second = client.post(f"/api/strategy-cards/{strategy_card_id}/conclusions", json=payload)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "CONCLUSION_ALREADY_EXISTS"


def test_create_conclusion_unknown_strategy_card_returns_404(
    client: TestClient,
    strategy_card_with_result: tuple[str, str],
) -> None:
    _, backtest_result_id = strategy_card_with_result
    missing_card = "00000000-0000-0000-0000-000000000099"
    payload = build_conclusion_payload(backtest_result_id)

    resp = client.post(f"/api/strategy-cards/{missing_card}/conclusions", json=payload)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "STRATEGY_CARD_NOT_FOUND"


def test_create_conclusion_unknown_backtest_result_returns_404(
    client: TestClient,
    strategy_card_with_result: tuple[str, str],
) -> None:
    strategy_card_id, _ = strategy_card_with_result
    missing_result = "00000000-0000-0000-0000-000000000099"
    payload = build_conclusion_payload(missing_result)

    resp = client.post(f"/api/strategy-cards/{strategy_card_id}/conclusions", json=payload)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "BACKTEST_RESULT_NOT_FOUND"


def test_create_conclusion_result_belongs_to_wrong_card_returns_404(
    client: TestClient,
) -> None:
    """Backtest result from card A cannot be used to create conclusion on card B."""
    # Create card A and run a backtest
    card_a = client.post("/api/strategy-cards", json=build_strategy_payload()).json()["data"]["id"]
    run_a = client.post(f"/api/strategy-cards/{card_a}/backtests", json={}).json()["data"]
    assert run_a["status"] == "succeeded"
    result_a_id = client.get(f"/api/backtests/{run_a['run_id']}/result").json()["data"]["result_id"]

    # Create card B
    payload_b = build_strategy_payload()
    payload_b["name"] = "Card B"
    card_b = client.post("/api/strategy-cards", json=payload_b).json()["data"]["id"]

    # Try to create conclusion on card B with result from card A
    payload = build_conclusion_payload(result_a_id)
    resp = client.post(f"/api/strategy-cards/{card_b}/conclusions", json=payload)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "BACKTEST_RESULT_NOT_FOUND"


def test_create_conclusion_invalid_next_action_returns_422(
    client: TestClient,
    strategy_card_with_result: tuple[str, str],
) -> None:
    strategy_card_id, backtest_result_id = strategy_card_with_result
    payload = build_conclusion_payload(backtest_result_id)
    payload["next_action"] = "invalid_value"

    resp = client.post(f"/api/strategy-cards/{strategy_card_id}/conclusions", json=payload)
    assert resp.status_code == 422


def test_create_conclusion_notes_too_long_returns_422(
    client: TestClient,
    strategy_card_with_result: tuple[str, str],
) -> None:
    strategy_card_id, backtest_result_id = strategy_card_with_result
    payload = build_conclusion_payload(backtest_result_id)
    payload["notes"] = "x" * 4001  # exceeds 4000

    resp = client.post(f"/api/strategy-cards/{strategy_card_id}/conclusions", json=payload)
    assert resp.status_code == 422


def test_create_conclusion_market_condition_notes_too_long_returns_422(
    client: TestClient,
    strategy_card_with_result: tuple[str, str],
) -> None:
    strategy_card_id, backtest_result_id = strategy_card_with_result
    payload = build_conclusion_payload(backtest_result_id)
    payload["market_condition_notes"] = "x" * 2001  # exceeds 2000

    resp = client.post(f"/api/strategy-cards/{strategy_card_id}/conclusions", json=payload)
    assert resp.status_code == 422
