"""API routes for wind generation forecast retrieval and selection."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.forecast import ForecastListResponse, ForecastRecord
from app.services.elexon_service import (
    ElexonAPIError,
    ElexonError,
    ElexonService,
    ElexonTimeoutError,
)
from app.services.forecast_service import ForecastService

router = APIRouter(tags=["forecasts"])


def get_elexon_service() -> ElexonService:
    """Dependency provider for ElexonService."""
    return ElexonService()


def get_forecast_service() -> ForecastService:
    """Dependency provider for ForecastService."""
    return ForecastService()


@router.get(
    "/forecasts",
    response_model=ForecastListResponse,
    summary="Get Wind Generation Forecasts",
    description=(
        "Retrieve and select national wind generation forecasts (WINDFOR) for a UK "
        "settlement date. Enforces anti-leakage forecast selection based on purchasing "
        "decision time or day-ahead gate closure."
    ),
)
async def get_forecasts(
    settlement_date: Optional[str] = Query(
        default="2026-01-01",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="UK electricity settlement date (YYYY-MM-DD)",
        examples=["2026-01-01"],
    ),
    settlement_period: Optional[int] = Query(
        default=None,
        ge=1,
        le=50,
        description="Optional half-hour settlement period filter (1-50)",
        examples=[1],
    ),
    decision_time: Optional[datetime] = Query(
        default=None,
        description="Optional purchasing decision cutoff timestamp in UTC. Only forecasts published on or before this time are selected.",
    ),
    elexon_service: ElexonService = Depends(get_elexon_service),
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> ForecastListResponse:
    """Retrieve and process wind forecasts for a settlement date and optional period."""
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

    # Filter raw forecasts for target delivery settlement date
    date_records = [r for r in raw_forecasts if r.settlement_date == target_date]

    # Select forecasts based on anti-leakage decision cutoff or day-ahead rules
    if decision_time is not None:
        selected_records = forecast_service.select_forecasts_for_decision_time(
            date_records, decision_time=decision_time
        )
    else:
        # Default to Day-Ahead selection (17:00 UTC D-1)
        selected_records = forecast_service.select_day_ahead_forecasts(
            date_records, settlement_date=target_date
        )
        # If day-ahead yields no forecasts (e.g., feed starts after D-1 17:00), fallback to latest available prior to delivery
        if not selected_records and date_records:
            selected_records = forecast_service.select_gate_closure_forecasts(
                date_records, lead_hours=0.0
            )

    # Apply period filter if specified
    if settlement_period is not None:
        selected_records = [r for r in selected_records if r.settlement_period == settlement_period]

    return ForecastListResponse(
        items=selected_records,
        count=len(selected_records),
        settlement_date=target_date,
        fuel_type="WIND",
    )
