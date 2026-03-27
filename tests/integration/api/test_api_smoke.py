from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app


def test_create_app_builds_fastapi_application_with_expected_metadata() -> None:
    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "Hypothesis Lab API"
    assert app.openapi_url == "/openapi.json"
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"


def test_default_fastapi_docs_endpoints_are_available() -> None:
    app = create_app()
    client = TestClient(app)

    docs_response = client.get("/docs")
    openapi_response = client.get("/openapi.json")
    redoc_response = client.get("/redoc")

    assert docs_response.status_code == 200
    assert openapi_response.status_code == 200
    assert redoc_response.status_code == 200
    openapi_document = openapi_response.json()

    assert openapi_document["info"]["title"] == "Hypothesis Lab API"
    assert "/api/strategy-cards" in openapi_document["paths"]
    assert "post" in openapi_document["paths"]["/api/strategy-cards"]
    assert "/api/strategy-cards/{strategy_card_id}" in openapi_document["paths"]
    assert "get" in openapi_document["paths"]["/api/strategy-cards/{strategy_card_id}"]
    assert "put" in openapi_document["paths"]["/api/strategy-cards/{strategy_card_id}"]
    assert "/api/strategy-cards/{strategy_card_id}/backtests" in openapi_document["paths"]
    assert "post" in openapi_document["paths"]["/api/strategy-cards/{strategy_card_id}/backtests"]
    assert "/api/backtests/{run_id}" in openapi_document["paths"]
    assert "get" in openapi_document["paths"]["/api/backtests/{run_id}"]
