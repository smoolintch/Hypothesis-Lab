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


def build_card(name: str = "Test Strategy", symbol: str = "BTCUSDT") -> dict:
    return {
        "name": name,
        "symbol": symbol,
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
                "params": {"ma_type": "ema", "fast_period": 3, "slow_period": 5, "cross_direction": "golden"},
            },
            "exit": {
                "template_key": "ma_cross",
                "params": {"ma_type": "ema", "fast_period": 3, "slow_period": 5, "cross_direction": "dead"},
            },
            "stop_loss": None,
            "take_profit": None,
        },
    }


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    database_path = tmp_path / "strategy-list.db"
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


def test_list_strategy_cards_empty(client: TestClient) -> None:
    resp = client.get("/api/strategy-cards")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["items"] == []
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 20
    assert data["pagination"]["total"] == 0


def test_list_strategy_cards_returns_created_cards(client: TestClient) -> None:
    client.post("/api/strategy-cards", json=build_card("Strategy A"))
    client.post("/api/strategy-cards", json=build_card("Strategy B"))

    resp = client.get("/api/strategy-cards")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["pagination"]["total"] == 2
    assert len(data["items"]) == 2


def test_list_strategy_cards_summary_fields(client: TestClient) -> None:
    """Items must have exactly the StrategyCardSummary fields."""
    client.post("/api/strategy-cards", json=build_card("Summary Test"))

    resp = client.get("/api/strategy-cards")
    item = resp.json()["data"]["items"][0]

    assert "id" in item
    assert "name" in item
    assert "symbol" in item
    assert "timeframe" in item
    assert "status" in item
    assert "updated_at" in item
    assert "latest_backtest_run_id" in item

    # Detail fields must NOT appear in summary
    assert "rule_set" not in item
    assert "backtest_range" not in item
    assert "initial_capital" not in item
    assert "fee_rate" not in item
    assert "created_at" not in item


def test_list_strategy_cards_ordered_by_updated_at_desc(client: TestClient) -> None:
    """Most recently updated card must appear first."""
    r1 = client.post("/api/strategy-cards", json=build_card("First")).json()["data"]
    r2 = client.post("/api/strategy-cards", json=build_card("Second")).json()["data"]

    # Update card 1 so it becomes the most recently updated
    client.put(f"/api/strategy-cards/{r1['id']}", json=build_card("First Updated"))

    resp = client.get("/api/strategy-cards")
    items = resp.json()["data"]["items"]
    assert items[0]["id"] == r1["id"]
    assert items[1]["id"] == r2["id"]


def test_list_strategy_cards_pagination(client: TestClient) -> None:
    for i in range(5):
        client.post("/api/strategy-cards", json=build_card(f"Card {i}"))

    # Page 1 of 3 items per page
    resp = client.get("/api/strategy-cards?page=1&page_size=3")
    data = resp.json()["data"]
    assert data["pagination"]["total"] == 5
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 3
    assert len(data["items"]) == 3

    # Page 2
    resp2 = client.get("/api/strategy-cards?page=2&page_size=3")
    data2 = resp2.json()["data"]
    assert data2["pagination"]["page"] == 2
    assert len(data2["items"]) == 2

    # Page 3 (beyond data) returns empty items
    resp3 = client.get("/api/strategy-cards?page=3&page_size=3")
    data3 = resp3.json()["data"]
    assert data3["pagination"]["total"] == 5
    assert len(data3["items"]) == 0


def test_list_strategy_cards_page_size_max_100(client: TestClient) -> None:
    resp = client.get("/api/strategy-cards?page_size=101")
    assert resp.status_code == 422


def test_list_strategy_cards_status_filter(client: TestClient) -> None:
    """Filtering by status must return only matching cards."""
    client.post("/api/strategy-cards", json=build_card("Draft Card"))
    # All cards start as "draft" by default

    # Filter by draft — must find the card
    resp_draft = client.get("/api/strategy-cards?status=draft")
    assert resp_draft.status_code == 200
    data_draft = resp_draft.json()["data"]
    assert data_draft["pagination"]["total"] == 1
    assert data_draft["items"][0]["status"] == "draft"

    # Filter by ready — must return empty
    resp_ready = client.get("/api/strategy-cards?status=ready")
    assert resp_ready.json()["data"]["pagination"]["total"] == 0
    assert resp_ready.json()["data"]["items"] == []


def test_list_strategy_cards_no_filter_returns_all_statuses(client: TestClient) -> None:
    client.post("/api/strategy-cards", json=build_card("Card 1"))
    client.post("/api/strategy-cards", json=build_card("Card 2"))

    resp = client.get("/api/strategy-cards")
    assert resp.json()["data"]["pagination"]["total"] == 2


def test_list_strategy_cards_reflects_latest_backtest_run_id(client: TestClient) -> None:
    """latest_backtest_run_id should be populated after a backtest is started."""
    card_id = client.post("/api/strategy-cards", json=build_card()).json()["data"]["id"]

    # Before backtest
    before = client.get("/api/strategy-cards").json()["data"]["items"][0]
    assert before["latest_backtest_run_id"] is None

    # After backtest
    run_resp = client.post(f"/api/strategy-cards/{card_id}/backtests", json={})
    run_id = run_resp.json()["data"]["run_id"]

    after = client.get("/api/strategy-cards").json()["data"]["items"][0]
    assert after["latest_backtest_run_id"] == run_id
