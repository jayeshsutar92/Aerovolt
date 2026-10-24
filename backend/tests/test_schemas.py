from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.schemas.analytics import (
    AccuracyMetrics,
    ComparisonResponse,
    ForecastActualComparisonPoint,
)
from app.schemas.common import ErrorDetail, ErrorResponse, TimeWindowParams
from app.schemas.forecast import (
    ForecastFilterParams,
    ForecastListResponse,
    ForecastRecord,
)


def test_valid_forecast_record():
    """Verify initialization and normalization of valid ForecastRecord."""
    record = ForecastRecord(
        start_time="2026-10-24T12:00:00Z",
        publish_time="2026-10-24T06:00:00Z",
        settlement_date="2026-10-24",
        settlement_period=24,
        generation_mw=1250.5,
    )
    assert record.generation_mw == 1250.5
    assert record.settlement_period == 24
    assert record.fuel_type == "WIND"
    assert record.start_time.tzinfo == timezone.utc
    assert record.publish_time.tzinfo == timezone.utc


def test_forecast_record_negative_generation_raises():
    """Negative generation_mw must fail validation."""
    with pytest.raises(ValidationError):
        ForecastRecord(
            start_time="2026-10-24T12:00:00Z",
            publish_time="2026-10-24T06:00:00Z",
            settlement_date="2026-10-24",
            settlement_period=24,
            generation_mw=-10.0,
        )


def test_forecast_record_invalid_settlement_period_raises():
    """Settlement period out of 1-50 range must fail validation."""
    with pytest.raises(ValidationError):
        ForecastRecord(
            start_time="2026-10-24T12:00:00Z",
            publish_time="2026-10-24T06:00:00Z",
            settlement_date="2026-10-24",
            settlement_period=51,
            generation_mw=100.0,
        )


def test_forecast_record_lookahead_violation_raises():
    """publish_time after start_time must fail validation."""
    with pytest.raises(ValidationError) as exc:
        ForecastRecord(
            start_time="2026-10-24T12:00:00Z",
            publish_time="2026-10-24T13:00:00Z",
            settlement_date="2026-10-24",
            settlement_period=24,
            generation_mw=100.0,
        )
    assert "Lookahead forecasts are prohibited" in str(exc.value)


def test_forecast_list_response():
    """Verify ForecastListResponse container serialization."""
    rec = ForecastRecord(
        start_time="2026-10-24T12:00:00Z",
        publish_time="2026-10-24T06:00:00Z",
        settlement_date="2026-10-24",
        settlement_period=24,
        generation_mw=1250.5,
    )
    response = ForecastListResponse(
        items=[rec],
        count=1,
        settlement_date="2026-10-24",
    )
    assert response.count == 1
    assert len(response.items) == 1
    assert response.items[0].settlement_period == 24


def test_accuracy_metrics():
    """Verify AccuracyMetrics schema validation."""
    metrics = AccuracyMetrics(
        mae=42.5,
        rmse=55.1,
        bias=-5.2,
        wape_percent=6.25,
        sample_count=48,
    )
    assert metrics.mae == 42.5
    assert metrics.rmse == 55.1
    assert metrics.bias == -5.2
    assert metrics.sample_count == 48


def test_accuracy_metrics_negative_mae_raises():
    """Negative MAE must fail validation."""
    with pytest.raises(ValidationError):
        AccuracyMetrics(mae=-1.0, rmse=5.0, sample_count=10)


def test_forecast_actual_comparison_point():
    """Verify ForecastActualComparisonPoint serialization."""
    point = ForecastActualComparisonPoint(
        start_time="2026-10-24T12:00:00Z",
        settlement_date="2026-10-24",
        settlement_period=24,
        actual_mw=1200.0,
        forecast_mw=1250.0,
        error_mw=50.0,
        abs_error_mw=50.0,
    )
    assert point.start_time.tzinfo == timezone.utc
    assert point.actual_mw == 1200.0
    assert point.error_mw == 50.0


def test_comparison_response():
    """Verify ComparisonResponse envelope serialization."""
    point = ForecastActualComparisonPoint(
        start_time="2026-10-24T12:00:00Z",
        settlement_date="2026-10-24",
        settlement_period=24,
        actual_mw=1200.0,
        forecast_mw=1250.0,
        error_mw=50.0,
        abs_error_mw=50.0,
    )
    metrics = AccuracyMetrics(
        mae=50.0,
        rmse=50.0,
        bias=50.0,
        wape_percent=4.17,
        sample_count=1,
    )
    response = ComparisonResponse(
        points=[point],
        metrics=metrics,
        settlement_date="2026-10-24",
        sample_count=1,
    )
    assert response.sample_count == 1
    assert len(response.points) == 1
    assert response.metrics.mae == 50.0


def test_error_response_envelope():
    """Verify ErrorResponse schema structure."""
    err = ErrorResponse(
        error=ErrorDetail(
            code="INVALID_DATE",
            message="Date must be formatted as YYYY-MM-DD",
            details={"input": "24/10/2026"},
        )
    )
    assert err.error.code == "INVALID_DATE"
    assert err.error.details["input"] == "24/10/2026"


def test_time_window_params_valid():
    """TimeWindowParams with valid start and end should succeed."""
    params = TimeWindowParams(
        start_time="2026-10-24T00:00:00Z",
        end_time="2026-10-24T23:30:00Z",
    )
    assert params.start_time < params.end_time
    assert params.start_time.tzinfo == timezone.utc


def test_time_window_params_inverted_raises():
    """TimeWindowParams with end_time before start_time must raise ValidationError."""
    with pytest.raises(ValidationError) as exc:
        TimeWindowParams(
            start_time="2026-10-24T12:00:00Z",
            end_time="2026-10-24T10:00:00Z",
        )
    assert "end_time" in str(exc.value)
