"""Pydantic schemas for forecast-versus-actual comparisons and accuracy metrics."""

from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.datetime_utils import ensure_utc, parse_timestamp


class AccuracyMetrics(BaseModel):
    """Aggregate accuracy evaluation metrics for wind generation forecasts."""

    model_config = ConfigDict(frozen=True)

    mae: Optional[float] = Field(
        None,
        ge=0.0,
        description="Mean Absolute Error in megawatts (MW)",
        examples=[45.2],
    )
    rmse: Optional[float] = Field(
        None,
        ge=0.0,
        description="Root Mean Squared Error in megawatts (MW)",
        examples=[58.7],
    )
    bias: Optional[float] = Field(
        None,
        description="Mean Error / Bias in megawatts (MW). Positive = over-forecast, negative = under-forecast.",
        examples=[12.4],
    )
    wape_percent: Optional[float] = Field(
        None,
        ge=0.0,
        description="Weighted Absolute Percentage Error (WAPE / Normalized MAE) in percent (%)",
        examples=[6.85],
    )
    sample_count: int = Field(
        ...,
        ge=0,
        description="Number of paired forecast-actual intervals included in this calculation",
        examples=[48],
    )


class ForecastActualComparisonPoint(BaseModel):
    """A paired forecast and actual generation data point for a single settlement interval."""

    model_config = ConfigDict(frozen=True)

    start_time: datetime = Field(
        ...,
        description="Target delivery start timestamp in UTC (half-hour window start)",
        examples=["2026-10-24T12:00:00Z"],
    )
    settlement_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="UK electricity settlement date (YYYY-MM-DD)",
        examples=["2026-10-24"],
    )
    settlement_period: int = Field(
        ...,
        ge=1,
        le=50,
        description="UK half-hourly settlement period (1-48; 46 or 50 on clock-change days)",
        examples=[24],
    )
    actual_mw: Optional[float] = Field(
        None,
        ge=0.0,
        description="Actual measured wind generation in megawatts (MW)",
        examples=[1380.0],
    )
    forecast_mw: Optional[float] = Field(
        None,
        ge=0.0,
        description="Selected forecast wind generation in megawatts (MW)",
        examples=[1420.5],
    )
    error_mw: Optional[float] = Field(
        None,
        description="Signed error in megawatts (forecast_mw - actual_mw)",
        examples=[40.5],
    )
    abs_error_mw: Optional[float] = Field(
        None,
        ge=0.0,
        description="Absolute error in megawatts (|forecast_mw - actual_mw|)",
        examples=[40.5],
    )

    @field_validator("start_time", mode="before")
    @classmethod
    def normalize_utc_timestamp(cls, value: Any) -> datetime:
        """Parse string or datetime and normalize to UTC."""
        if isinstance(value, datetime):
            return ensure_utc(value, assume_utc=True)
        if isinstance(value, str):
            return parse_timestamp(value, default_tz=timezone.utc)
        raise ValueError(f"Invalid timestamp value: {value}")


class ComparisonResponse(BaseModel):
    """Response envelope containing timeseries comparison points and summary accuracy metrics."""

    model_config = ConfigDict(frozen=True)

    points: List[ForecastActualComparisonPoint] = Field(
        default_factory=list,
        description="Ordered timeseries of paired forecast-versus-actual comparison points",
    )
    metrics: AccuracyMetrics = Field(
        ...,
        description="Aggregate accuracy metrics calculated over the comparison points",
    )
    settlement_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Target settlement date if query was date-scoped",
        examples=["2026-10-24"],
    )
    sample_count: int = Field(
        ...,
        ge=0,
        description="Total number of points in the comparison series",
    )
