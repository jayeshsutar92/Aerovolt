from datetime import datetime, timezone
import pytest

from app.schemas.actual import ActualGenerationRecord
from app.schemas.analytics import ForecastActualComparisonPoint
from app.schemas.forecast import ForecastRecord
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def analytics_service() -> AnalyticsService:
    return AnalyticsService()


def test_align_records_complete_and_missing(analytics_service: AnalyticsService):
    """Verify alignment handles complete pairs and missing counterparts cleanly."""
    t1 = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc)
    t3 = datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc)

    # Forecasts for t1 and t2
    forecasts = [
        ForecastRecord(
            start_time=t1,
            publish_time=datetime(2025, 12, 31, 17, 0, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=1,
            generation_mw=1000.0,
        ),
        ForecastRecord(
            start_time=t2,
            publish_time=datetime(2025, 12, 31, 17, 0, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=2,
            generation_mw=1100.0,
        ),
    ]

    # Actuals for t2 and t3 (t1 missing in actuals, t3 missing in forecasts)
    actuals = [
        ActualGenerationRecord(
            start_time=t2,
            settlement_date="2026-01-01",
            settlement_period=2,
            generation_mw=1050.0,
        ),
        ActualGenerationRecord(
            start_time=t3,
            settlement_date="2026-01-01",
            settlement_period=3,
            generation_mw=950.0,
        ),
    ]

    points = analytics_service.align_records(forecasts, actuals)
    assert len(points) == 3

    # Point 1 (t1): forecast present, actual missing
    assert points[0].start_time == t1
    assert points[0].forecast_mw == 1000.0
    assert points[0].actual_mw is None
    assert points[0].error_mw is None
    assert points[0].abs_error_mw is None

    # Point 2 (t2): both present
    assert points[1].start_time == t2
    assert points[1].forecast_mw == 1100.0
    assert points[1].actual_mw == 1050.0
    assert points[1].error_mw == 50.0  # 1100 - 1050
    assert points[1].abs_error_mw == 50.0

    # Point 3 (t3): forecast missing, actual present
    assert points[2].start_time == t3
    assert points[2].forecast_mw is None
    assert points[2].actual_mw == 950.0
    assert points[2].error_mw is None


def test_calculate_accuracy_metrics(analytics_service: AnalyticsService):
    """Verify quantitative error formulas (MAE, RMSE, Bias, WAPE)."""
    t = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    points = [
        # actual: 100, forecast: 110 -> error: +10, abs: 10, sq: 100
        ForecastActualComparisonPoint(
            start_time=t,
            settlement_date="2026-01-01",
            settlement_period=1,
            actual_mw=100.0,
            forecast_mw=110.0,
            error_mw=10.0,
            abs_error_mw=10.0,
        ),
        # actual: 200, forecast: 180 -> error: -20, abs: 20, sq: 400
        ForecastActualComparisonPoint(
            start_time=t,
            settlement_date="2026-01-01",
            settlement_period=2,
            actual_mw=200.0,
            forecast_mw=180.0,
            error_mw=-20.0,
            abs_error_mw=20.0,
        ),
    ]

    metrics = analytics_service.calculate_accuracy_metrics(points)
    assert metrics.sample_count == 2
    # MAE = (10 + 20) / 2 = 15.0
    assert metrics.mae == 15.0
    # RMSE = sqrt((100 + 400) / 2) = sqrt(250) = 15.811
    assert metrics.rmse == 15.811
    # Bias = (10 - 20) / 2 = -5.0
    assert metrics.bias == -5.0
    # WAPE = (10 + 20) / (100 + 200) * 100% = 30 / 300 * 100 = 10.0%
    assert metrics.wape_percent == 10.0


def test_calculate_accuracy_metrics_zero_actual_avoids_misleading_percentage(
    analytics_service: AnalyticsService,
):
    """WAPE should return None when total actual generation is zero or near zero."""
    t = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    points = [
        ForecastActualComparisonPoint(
            start_time=t,
            settlement_date="2026-01-01",
            settlement_period=1,
            actual_mw=0.0,
            forecast_mw=5.0,
            error_mw=5.0,
            abs_error_mw=5.0,
        ),
    ]

    metrics = analytics_service.calculate_accuracy_metrics(points, min_actual_sum_mw=1.0)
    assert metrics.sample_count == 1
    assert metrics.mae == 5.0
    assert metrics.rmse == 5.0
    # WAPE must be None to prevent division by zero or inflated percentage
    assert metrics.wape_percent is None


def test_calculate_accuracy_metrics_empty(analytics_service: AnalyticsService):
    """Empty points list should yield sample_count=0 and None metrics."""
    metrics = analytics_service.calculate_accuracy_metrics([])
    assert metrics.sample_count == 0
    assert metrics.mae is None
    assert metrics.rmse is None
    assert metrics.bias is None
    assert metrics.wape_percent is None


def test_compare_method(analytics_service: AnalyticsService):
    """Verify compare returns a structured ComparisonResponse."""
    t = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    forecasts = [
        ForecastRecord(
            start_time=t,
            publish_time=datetime(2025, 12, 31, 17, 0, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=1,
            generation_mw=100.0,
        )
    ]
    actuals = [
        ActualGenerationRecord(
            start_time=t,
            settlement_date="2026-01-01",
            settlement_period=1,
            generation_mw=90.0,
        )
    ]

    response = analytics_service.compare(forecasts, actuals, settlement_date="2026-01-01")
    assert response.settlement_date == "2026-01-01"
    assert response.sample_count == 1
    assert len(response.points) == 1
    assert response.metrics.mae == 10.0
