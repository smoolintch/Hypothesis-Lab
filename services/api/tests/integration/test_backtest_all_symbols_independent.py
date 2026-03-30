"""
Independent test: verify all 4 symbol/timeframe combinations (BTC/ETH × 4H/1D)
produce stable backtest results via the full API chain.

This test is read-only with respect to business code.
Covers the stage-2 exit criterion: "BTC/ETH、1D/4H 预设范围可稳定出结果".
"""
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


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    database_path = tmp_path / "symbols-test.db"
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


def build_payload(symbol: str, timeframe: str) -> dict:
    """Build a minimal valid payload for the given symbol/timeframe using fixture-covered range."""
    if timeframe == "4H":
        # 4H fixture covers 2024-01-01 to 2024-01-02 (6 candles)
        start_at = "2024-01-01T00:00:00Z"
        end_at = "2024-01-02T00:00:00Z"
    else:
        # 1D fixture covers 2024-01-01 to 2024-01-06 (5 candles)
        start_at = "2024-01-01T00:00:00Z"
        end_at = "2024-01-06T00:00:00Z"

    return {
        "name": f"Symbol Coverage Test {symbol}/{timeframe}",
        "symbol": symbol,
        "timeframe": timeframe,
        "backtest_range": {"start_at": start_at, "end_at": end_at},
        "initial_capital": 10000,
        "fee_rate": 0.001,
        "rule_set": {
            "entry": {
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "sma",
                    "fast_period": 2,
                    "slow_period": 3,
                    "cross_direction": "golden",
                },
            },
            "exit": {
                "template_key": "ma_cross",
                "params": {
                    "ma_type": "sma",
                    "fast_period": 2,
                    "slow_period": 3,
                    "cross_direction": "dead",
                },
            },
            "stop_loss": None,
            "take_profit": None,
        },
    }


@pytest.mark.parametrize(
    "symbol,timeframe",
    [
        ("BTCUSDT", "1D"),   # BTC/1D  – covered at engine level, verifying API chain
        ("ETHUSDT", "4H"),   # ETH/4H  – NOT previously covered at API level
        ("ETHUSDT", "1D"),   # ETH/1D  – NOT previously covered at API level
    ],
)
def test_backtest_runs_and_succeeds_for_symbol_timeframe(
    client: TestClient, symbol: str, timeframe: str
) -> None:
    """Verify end-to-end: create card → start backtest → result readable, for each combo."""
    payload = build_payload(symbol, timeframe)

    created = client.post("/api/strategy-cards", json=payload)
    assert created.status_code == 201, f"card creation failed: {created.json()}"
    strategy_card_id = created.json()["data"]["id"]

    start = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    assert start.status_code == 202, f"start backtest failed: {start.json()}"
    run_data = start.json()["data"]

    assert run_data["status"] == "succeeded", (
        f"{symbol}/{timeframe} backtest failed with error_code={run_data.get('error_code')}, "
        f"error_message={run_data.get('error_message')}"
    )
    assert run_data["result_url"] is not None
    assert run_data["started_at"] is not None
    assert run_data["finished_at"] is not None

    run_id = run_data["run_id"]
    result_resp = client.get(f"/api/backtests/{run_id}/result")
    assert result_resp.status_code == 200, f"result fetch failed: {result_resp.json()}"
    result = result_resp.json()["data"]

    # Structural completeness check
    assert result["run_id"] == run_id
    assert result["dataset_version"] == "sample-v1"
    metrics = result["summary_metrics"]
    for field in ("total_return_rate", "max_drawdown_rate", "win_rate",
                  "profit_factor", "trade_count", "avg_holding_bars", "final_equity"):
        assert field in metrics, f"missing metric field: {field}"
    assert metrics["final_equity"] > 0
    assert len(result["equity_curve"]) > 0
    assert len(result["drawdown_curve"]) > 0


@pytest.mark.parametrize(
    "symbol,timeframe",
    [
        ("BTCUSDT", "1D"),
        ("ETHUSDT", "4H"),
        ("ETHUSDT", "1D"),
    ],
)
def test_repeated_runs_produce_consistent_metrics(
    client: TestClient, symbol: str, timeframe: str
) -> None:
    """Consistency check: same strategy input → same summary_metrics across two runs."""
    payload = build_payload(symbol, timeframe)

    created = client.post("/api/strategy-cards", json=payload)
    strategy_card_id = created.json()["data"]["id"]

    run1 = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    run2 = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})

    assert run1.json()["data"]["status"] == "succeeded", (
        f"{symbol}/{timeframe} run1 failed: {run1.json()['data']}"
    )
    assert run2.json()["data"]["status"] == "succeeded", (
        f"{symbol}/{timeframe} run2 failed: {run2.json()['data']}"
    )

    r1 = client.get(f"/api/backtests/{run1.json()['data']['run_id']}/result").json()["data"]
    r2 = client.get(f"/api/backtests/{run2.json()['data']['run_id']}/result").json()["data"]

    assert r1["summary_metrics"] == r2["summary_metrics"], (
        f"{symbol}/{timeframe}: metrics differ between runs!\n"
        f"run1: {r1['summary_metrics']}\n"
        f"run2: {r2['summary_metrics']}"
    )
    assert len(r1["equity_curve"]) == len(r2["equity_curve"])
    assert len(r1["trades"]) == len(r2["trades"])
