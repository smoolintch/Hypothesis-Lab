from __future__ import annotations

from pathlib import Path
import sys

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
    database_path = tmp_path / "strategy-cards.db"
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


def test_strategy_card_create_get_update_roundtrip(client: TestClient) -> None:
    payload = build_payload()

    create_response = client.post("/api/strategy-cards", json=payload)
    assert create_response.status_code == 201

    created_body = create_response.json()
    assert created_body["success"] is True
    assert created_body["data"]["name"] == payload["name"]
    assert created_body["data"]["status"] == "draft"
    assert created_body["data"]["latest_backtest_run_id"] is None

    strategy_card_id = created_body["data"]["id"]

    get_response = client.get(f"/api/strategy-cards/{strategy_card_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["rule_set"]["entry"]["template_key"] == "ma_cross"

    updated_payload = build_payload()
    updated_payload["name"] = "EMA Breakout Updated"
    updated_payload["fee_rate"] = 0.002

    update_response = client.put(
        f"/api/strategy-cards/{strategy_card_id}",
        json=updated_payload,
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == "EMA Breakout Updated"
    assert update_response.json()["data"]["fee_rate"] == 0.002

    reloaded_response = client.get(f"/api/strategy-cards/{strategy_card_id}")
    assert reloaded_response.status_code == 200
    assert reloaded_response.json()["data"]["name"] == "EMA Breakout Updated"


def test_strategy_card_rejects_invalid_rule_template_position(client: TestClient) -> None:
    payload = build_payload()
    payload["rule_set"]["stop_loss"] = {
        "template_key": "ma_cross",
        "params": {
            "ma_type": "ema",
            "fast_period": 20,
            "slow_period": 50,
            "cross_direction": "golden",
        },
    }

    response = client.post("/api/strategy-cards", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RULE_TEMPLATE_INVALID"


def test_strategy_card_rejects_invalid_rule_template_params(client: TestClient) -> None:
    payload = build_payload()
    payload["rule_set"]["entry"]["params"]["slow_period"] = 10

    response = client.post("/api/strategy-cards", json=payload)
    assert response.status_code == 422

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RULE_TEMPLATE_INVALID"
    assert body["error"]["details"]["position"] == "entry"
    assert body["error"]["details"]["template_key"] == "ma_cross"
    assert body["error"]["details"]["validation_errors"][0]["msg"] == (
        "Value error, slow_period must be greater than fast_period"
    )


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (lambda payload: payload.__setitem__("name", "   "), "STRATEGY_CARD_VALIDATION_FAILED"),
        (lambda payload: payload.__setitem__("symbol", "DOGEUSDT"), "UNSUPPORTED_SYMBOL"),
        (lambda payload: payload.__setitem__("timeframe", "1H"), "UNSUPPORTED_TIMEFRAME"),
        (
            lambda payload: payload["backtest_range"].__setitem__(
                "end_at",
                "2022-01-01T00:00:00Z",
            ),
            "STRATEGY_CARD_VALIDATION_FAILED",
        ),
        (lambda payload: payload.__setitem__("initial_capital", 0), "STRATEGY_CARD_VALIDATION_FAILED"),
        (lambda payload: payload.__setitem__("fee_rate", 0.02), "STRATEGY_CARD_VALIDATION_FAILED"),
    ],
)
def test_strategy_card_rejects_invalid_basic_fields(
    client: TestClient,
    mutator,
    expected_code: str,
) -> None:
    payload = build_payload()
    mutator(payload)

    response = client.post("/api/strategy-cards", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == expected_code
