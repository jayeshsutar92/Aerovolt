"""API routes for wind generation forecast accuracy analytics and comparisons."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.analytics import ComparisonResponse
from app.services.analytics_service import AnalyticsService
from app.services.elexon_service import (
    ElexonAPIError,
    ElexonError,
    ElexonService,
    ElexonTimeoutError,
)
from app.services.forecast_service import ForecastService

router = APIRouter(tags=["analytics"])


def get_elexon_service() -> ElexonService:
    """Dependency provider for ElexonService."""
    return ElexonService()


def get_forecast_service() -> ForecastService:
    """Dependency provider for ForecastService."""
    return ForecastService()


def get_analytics_service() -> AnalyticsService:
    """Dependency provider for AnalyticsService."""
    return AnalyticsService()


@router.get(
    "/analytics",
    response_model=ComparisonResponse,
    summary="Get Forecast vs Actual Analytics",
    description=(
        "Retrieve paired forecast-versus-actual generation records and evaluate quantitative "
        "accuracy benchmarks (MAE, RMSE, Bias, and zero-suppressed WAPE) for a UK settlement date."
    ),
)
async def get_analytics(
    settlement_date: Optional[str] = Query(
        default="2026-01-01",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="UK electricity settlement date (YYYY-MM-DD)",
        examples=["2026-01-01"],
    ),
    elexon_service: ElexonService = Depends(get_elexon_service),
    forecast_service: ForecastService = Depends(get_forecast_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ComparisonResponse:
    """Compare selected forecasts with actual generation outturn and calculate accuracy benchmarks."""
    target_date = settlement_date or "2026-01-01"

    # Validate that date is a real calendar date
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid settlement_date '{target_date}'. Expected a valid calendar date in YYYY-MM-DD format.",
        )

    try:
        raw_forecasts = await elexon_service.get_wind_forecasts(settlement_date=target_date)
        actuals = await elexon_service.get_actual_wind_generation(settlement_date=target_date)
    except ElexonTimeoutError as err:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Upstream Elexon API timed out: {err}",
        )
    except ElexonAPIError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream Elexon API returned error ({err.status_code}): {err.message}",
        )
    except ElexonError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Communication error with Elexon API: {err}",
        )

    # Filter forecasts for target settlement date
    date_records = [r for r in raw_forecasts if r.settlement_date == target_date]

    # Select day-ahead forecasts (or fallback to latest gate closure)
    selected_forecasts = forecast_service.select_day_ahead_forecasts(
        date_records, settlement_date=target_date
    )
    if not selected_forecasts and date_records:
        selected_forecasts = forecast_service.select_gate_closure_forecasts(
            date_records, lead_hours=0.0
        )

    # Align series and calculate accuracy metrics
    return analytics_service.compare(
        forecasts=selected_forecasts,
        actuals=actuals,
        settlement_date=target_date,
    )
