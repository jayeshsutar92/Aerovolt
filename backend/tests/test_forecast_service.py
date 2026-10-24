from datetime import datetime, timezone
import pytest

from app.schemas.forecast import ForecastRecord
from app.services.forecast_service import ForecastService


@pytest.fixture
def forecast_service() -> ForecastService:
    return ForecastService()


@pytest.fixture
def sample_forecast_records() -> list[ForecastRecord]:
    # Target delivery interval: 2026-01-01 12:00 UTC (Period 25)
    t_delivery = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    return [
        # D-2 forecast
        ForecastRecord(
            start_time=t_delivery,
            publish_time=datetime(2025, 12, 30, 16, 0, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=25,
            generation_mw=900.0,
        ),
        # Day-ahead forecast (D-1 16:30 UTC)
        ForecastRecord(
            start_time=t_delivery,
            publish_time=datetime(2025, 12, 31, 16, 30, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=25,
            generation_mw=1050.0,
        ),
        # Morning intraday forecast (D-Day 08:00 UTC)
        ForecastRecord(
            start_time=t_delivery,
            publish_time=datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=25,
            generation_mw=1150.0,
        ),
        # 1-hour ahead gate closure forecast (D-Day 11:00 UTC)
        ForecastRecord(
            start_time=t_delivery,
            publish_time=datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
            settlement_date="2026-01-01",
            settlement_period=25,
            generation_mw=1200.0,
        ),
    ]


def test_select_forecasts_for_decision_time_early(
    forecast_service: ForecastService,
    sample_forecast_records: list[ForecastRecord],
):
    """Decision made at D-1 12:00 should only select the D-2 forecast (publish_time <= decision_time)."""
    decision_time = datetime(2025, 12, 31, 12, 0, tzinfo=timezone.utc)
    selected = forecast_service.select_forecasts_for_decision_time(
        sample_forecast_records, decision_time=decision_time
    )

    assert len(selected) == 1
    # Only 900.0 MW was published prior to decision_time
    assert selected[0].generation_mw == 900.0
    assert selected[0].publish_time == datetime(2025, 12, 30, 16, 0, tzinfo=timezone.utc)


def test_select_forecasts_for_decision_time_never_selects_future(
    forecast_service: ForecastService,
    sample_forecast_records: list[ForecastRecord],
):
    """Never select a forecast published after the decision time."""
    decision_time = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
    selected = forecast_service.select_forecasts_for_decision_time(
        sample_forecast_records, decision_time=decision_time
    )

    assert len(selected) == 1
    # At 09:00 UTC, the 11:00 forecast (1200 MW) did NOT exist yet. The 08:00 forecast (1150 MW) is latest.
    assert selected[0].generation_mw == 1150.0
    assert selected[0].publish_time <= decision_time


def test_select_day_ahead_forecasts(
    forecast_service: ForecastService,
    sample_forecast_records: list[ForecastRecord],
):
    """Day-ahead selection targets 17:00 UTC on D-1."""
    selected = forecast_service.select_day_ahead_forecasts(
        sample_forecast_records, settlement_date="2026-01-01"
    )

    assert len(selected) == 1
    # The 16:30 forecast on D-1 was the latest before D-1 17:00 UTC
    assert selected[0].generation_mw == 1050.0
    assert selected[0].publish_time == datetime(2025, 12, 31, 16, 30, tzinfo=timezone.utc)


def test_select_gate_closure_forecasts(
    forecast_service: ForecastService,
    sample_forecast_records: list[ForecastRecord],
):
    """Gate closure selection with lead_hours=1.0 selects latest forecast on or before start_time - 1h."""
    selected = forecast_service.select_gate_closure_forecasts(
        sample_forecast_records, lead_hours=1.0
    )

    assert len(selected) == 1
    # Delivery is 12:00, cutoff is 11:00. The 11:00 forecast is chosen.
    assert selected[0].generation_mw == 1200.0
    assert selected[0].publish_time == datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc)


def test_normalize_record_from_dict(forecast_service: ForecastService):
    """Verify normalizing raw dict into typed ForecastRecord."""
    raw = {
        "start_time": "2026-01-01T12:00:00Z",
        "publish_time": "2026-01-01T08:00:00Z",
        "settlement_date": "2026-01-01",
        "settlement_period": 25,
        "generation_mw": 1400.0,
    }
    rec = forecast_service.normalize_record(raw)
    assert rec.generation_mw == 1400.0
    assert rec.start_time.tzinfo == timezone.utc
