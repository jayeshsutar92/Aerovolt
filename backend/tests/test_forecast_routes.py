"""Tests for the forecast and analytics API routes."""

from datetime import datetime, timezone
from typing import List
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
import pytest

from app.api.routes.forecasts import get_elexon_service
from app.main import app
from app.schemas.forecast import ForecastRecord
from app.services.elexon_service import ElexonAPIError, ElexonTimeoutError


@pytest.fixture
def sample_forecasts() -> List[ForecastRecord]:
    t1 = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc)
    return [
        ForecastRecord(
            start_time=t1,
            publish_time=datetime(2025, 12, 31, 15, 30, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=1,
            generation_mw=1200.0,
        ),
        ForecastRecord(
            start_time=t2,
            publish_time=datetime(2025, 12, 31, 15, 30, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=3,
            generation_mw=1350.0,
        ),
    ]


def test_openapi_contains_forecast_routes(client: TestClient):
    """OpenAPI schema must declare /api/forecasts and /api/analytics endpoints."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/forecasts" in paths
    assert "/api/analytics" in paths
    assert "get" in paths["/api/forecasts"]
    assert "get" in paths["/api/analytics"]


def test_get_forecasts_success(client: TestClient, sample_forecasts: List[ForecastRecord]):
    """GET /api/forecasts should return 200 with forecast list response."""
    mock_service = AsyncMock()
    mock_service.get_wind_forecasts.return_value = sample_forecasts

    app.dependency_overrides[get_elexon_service] = lambda: mock_service
    try:
        response = client.get("/api/forecasts?settlement_date=2026-01-01")
        assert response.status_code == 200

        data = response.json()
        assert data["settlement_date"] == "2026-01-01"
        assert data["fuel_type"] == "WIND"
        assert data["count"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["settlement_period"] == 1
        assert data["items"][0]["generation_mw"] == 1200.0
    finally:
        app.dependency_overrides.pop(get_elexon_service, None)


def test_get_forecasts_period_filter(client: TestClient, sample_forecasts: List[ForecastRecord]):
    """GET /api/forecasts?settlement_period=3 should filter to period 3."""
    mock_service = AsyncMock()
    mock_service.get_wind_forecasts.return_value = sample_forecasts

    app.dependency_overrides[get_elexon_service] = lambda: mock_service
    try:
        response = client.get("/api/forecasts?settlement_date=2026-01-01&settlement_period=3")
        assert response.status_code == 200

        data = response.json()
        assert data["count"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["settlement_period"] == 3
    finally:
        app.dependency_overrides.pop(get_elexon_service, None)


def test_get_forecasts_invalid_date_format(client: TestClient):
    """GET /api/forecasts with malformed date should return 422 validation error."""
    response = client.get("/api/forecasts?settlement_date=not-a-date")
    assert response.status_code == 422


def test_get_forecasts_upstream_timeout(client: TestClient):
    """Upstream Elexon timeout should return 504 Gateway Timeout."""
    mock_service = AsyncMock()
    mock_service.get_wind_forecasts.side_effect = ElexonTimeoutError("Timed out")

    app.dependency_overrides[get_elexon_service] = lambda: mock_service
    try:
        response = client.get("/api/forecasts?settlement_date=2026-01-01")
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(get_elexon_service, None)


def test_get_forecasts_upstream_error(client: TestClient):
    """Upstream Elexon API error should return 502 Bad Gateway."""
    mock_service = AsyncMock()
    mock_service.get_wind_forecasts.side_effect = ElexonAPIError(500, "Internal upstream failure")

    app.dependency_overrides[get_elexon_service] = lambda: mock_service
    try:
        response = client.get("/api/forecasts?settlement_date=2026-01-01")
        assert response.status_code == 502
        assert "500" in response.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_elexon_service, None)
