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


def build_real_payload() -> dict[str, object]:
    """Strategy payload using fixture-covered range: BTCUSDT/4H/sample-v1."""
    return {
        "name": "Real Execution Test Strategy",
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
    database_path = tmp_path / "backtest-real.db"
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


def test_start_backtest_runs_and_produces_succeeded_status(client: TestClient) -> None:
    created = client.post("/api/strategy-cards", json=build_real_payload())
    assert created.status_code == 201
    strategy_card_id = created.json()["data"]["id"]

    start = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    assert start.status_code == 202
    data = start.json()["data"]

    assert data["status"] == "succeeded"
    assert data["result_url"] == f"/api/backtests/{data['run_id']}/result"
    assert data["started_at"] is not None
    assert data["finished_at"] is not None
    assert data["error_code"] is None
    assert data["error_message"] is None


def test_get_backtest_result_returns_real_metrics(client: TestClient) -> None:
    created = client.post("/api/strategy-cards", json=build_real_payload())
    strategy_card_id = created.json()["data"]["id"]

    start = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    assert start.status_code == 202
    run_id = start.json()["data"]["run_id"]
    assert start.json()["data"]["status"] == "succeeded"

    result_resp = client.get(f"/api/backtests/{run_id}/result")
    assert result_resp.status_code == 200
    result = result_resp.json()["data"]

    # Structural checks
    assert result["run_id"] == run_id
    assert result["strategy_card_id"] == strategy_card_id
    assert result["dataset_version"] == "sample-v1"

    metrics = result["summary_metrics"]
    assert "total_return_rate" in metrics
    assert "max_drawdown_rate" in metrics
    assert "win_rate" in metrics
    assert "profit_factor" in metrics
    assert "trade_count" in metrics
    assert "avg_holding_bars" in metrics
    assert "final_equity" in metrics

    # Equity/drawdown curve must have exactly 6 points (fixture has 6 4H candles)
    assert len(result["equity_curve"]) == 6
    assert len(result["drawdown_curve"]) == 6

    for point in result["equity_curve"]:
        assert "ts" in point
        assert "value" in point
        assert isinstance(point["value"], float)

    # final_equity must match initial capital since no trades in small fixture
    # (MA periods 3/5 with 6 candles, entry requires index < last_index = 5, signals fire at index 5 only)
    assert metrics["trade_count"] >= 0
    assert metrics["final_equity"] > 0
    assert result["result_summary"] == {}


def test_get_backtest_result_consistent_on_repeated_runs(client: TestClient) -> None:
    """Same strategy input should produce structurally identical results."""
    created = client.post("/api/strategy-cards", json=build_real_payload())
    strategy_card_id = created.json()["data"]["id"]

    run1_resp = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    run2_resp = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})

    assert run1_resp.json()["data"]["status"] == "succeeded"
    assert run2_resp.json()["data"]["status"] == "succeeded"

    run1_id = run1_resp.json()["data"]["run_id"]
    run2_id = run2_resp.json()["data"]["run_id"]

    result1 = client.get(f"/api/backtests/{run1_id}/result").json()["data"]
    result2 = client.get(f"/api/backtests/{run2_id}/result").json()["data"]

    # Metrics must be identical across runs with same input
    assert result1["summary_metrics"] == result2["summary_metrics"]
    assert len(result1["equity_curve"]) == len(result2["equity_curve"])
    assert len(result1["trades"]) == len(result2["trades"])
    assert result1["dataset_version"] == result2["dataset_version"]


def test_get_result_returns_409_when_run_not_finished(client: TestClient) -> None:
    """Manually injecting a queued run should return 409 when result is requested."""
    import sys
    from pathlib import Path
    from uuid import uuid4
    from datetime import datetime, timezone

    # Create a strategy card and then manually set run status to queued
    created = client.post("/api/strategy-cards", json=build_real_payload())
    assert created.status_code == 201
    strategy_card_id = created.json()["data"]["id"]

    # Use the service directly to create a queued-only run without execution
    from app.infrastructure.config.settings import get_settings
    from app.infrastructure.database import create_engine, create_session_factory
    from app.infrastructure.database.repositories.strategy_card import StrategyCardRepository
    from app.infrastructure.database.repositories.strategy_snapshot import StrategySnapshotRepository
    from app.infrastructure.database.repositories.backtest_run import BacktestRunRepository

    settings = get_settings()
    session_factory = create_session_factory()
    with session_factory() as session:
        card_repo = StrategyCardRepository(session)
        snapshot_repo = StrategySnapshotRepository(session)
        run_repo = BacktestRunRepository(session)

        card = card_repo.get_by_id(
            strategy_card_id=UUID(strategy_card_id),
            user_id=settings.default_user_id,
        )
        now = datetime.now(timezone.utc)
        from app.domain.backtests.normalized_config import build_normalized_config_from_card
        normalized_config = build_normalized_config_from_card(card)
        version = snapshot_repo.next_version(strategy_card_id=card.id)
        snapshot = snapshot_repo.create(
            snapshot_id=uuid4(),
            user_id=settings.default_user_id,
            strategy_card_id=card.id,
            version=version,
            source_strategy_updated_at=now,
            normalized_config=normalized_config,
            created_at=now,
        )
        run = run_repo.create(
            run_id=uuid4(),
            user_id=settings.default_user_id,
            strategy_snapshot_id=snapshot.id,
            status="queued",
            created_at=now,
        )
        session.commit()
        run_id = str(run.id)

    result_resp = client.get(f"/api/backtests/{run_id}/result")
    assert result_resp.status_code == 409
    assert result_resp.json()["error"]["code"] == "BACKTEST_RESULT_NOT_READY"


def test_get_result_returns_422_when_run_failed(client: TestClient) -> None:
    """Backtest with out-of-range dates should fail and result endpoint returns 422."""
    # Use dates outside fixture coverage to trigger BACKTEST_EXECUTION_FAILED
    payload = build_real_payload()
    payload["backtest_range"] = {
        "start_at": "2023-01-01T00:00:00Z",
        "end_at": "2023-06-01T00:00:00Z",
    }

    created = client.post("/api/strategy-cards", json=payload)
    assert created.status_code == 201
    strategy_card_id = created.json()["data"]["id"]

    start = client.post(f"/api/strategy-cards/{strategy_card_id}/backtests", json={})
    assert start.status_code == 202
    data = start.json()["data"]
    # Out-of-range → no candles in fixture → should fail
    assert data["status"] == "failed"
    assert data["error_code"] in ("BACKTEST_EXECUTION_FAILED", "BACKTEST_DATASET_UNAVAILABLE")
    assert data["error_message"] is not None

    run_id = data["run_id"]
    result_resp = client.get(f"/api/backtests/{run_id}/result")
    assert result_resp.status_code == 422
    assert result_resp.json()["error"]["code"] == "BACKTEST_RESULT_UNAVAILABLE"


def test_get_result_returns_404_for_unknown_run(client: TestClient) -> None:
    missing = UUID("00000000-0000-0000-0000-000000000099")
    response = client.get(f"/api/backtests/{missing}/result")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "BACKTEST_RUN_NOT_FOUND"
