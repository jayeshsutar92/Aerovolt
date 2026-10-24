"""Pydantic schemas for wind generation forecast contracts."""

from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.datetime_utils import ensure_utc, parse_timestamp


class ForecastRecord(BaseModel):
    """Schema representing an individual wind generation forecast data point."""

    model_config = ConfigDict(frozen=True)

    start_time: datetime = Field(
        ...,
        description="Target delivery start timestamp in UTC (half-hour settlement interval start)",
        examples=["2026-10-24T12:00:00Z"],
    )
    publish_time: datetime = Field(
        ...,
        description="Timestamp when the forecast was generated and published by Elexon/NGESO in UTC",
        examples=["2026-10-24T08:00:00Z"],
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
    generation_mw: float = Field(
        ...,
        ge=0.0,
        description="Forecasted wind generation output in megawatts (MW)",
        examples=[1420.5],
    )
    fuel_type: str = Field(
        default="WIND",
        description="Generation fuel source type",
        examples=["WIND"],
    )

    @field_validator("start_time", "publish_time", mode="before")
    @classmethod
    def normalize_utc_timestamps(cls, value: Any) -> datetime:
        """Parse string or datetime and normalize to UTC."""
        if isinstance(value, datetime):
            return ensure_utc(value, assume_utc=True)
        if isinstance(value, str):
            return parse_timestamp(value, default_tz=timezone.utc)
        raise ValueError(f"Invalid timestamp value: {value}")

    @model_validator(mode="after")
    def validate_anti_leakage(self) -> "ForecastRecord":
        """Verify that forecast publication time does not occur after delivery start time."""
        if self.publish_time > self.start_time:
            raise ValueError(
                f"publish_time ({self.publish_time.isoformat()}) cannot be after "
                f"start_time ({self.start_time.isoformat()}). Lookahead forecasts are prohibited."
            )
        return self


class ForecastListResponse(BaseModel):
    """Container schema for wind generation forecast queries."""

    model_config = ConfigDict(frozen=True)

    items: List[ForecastRecord] = Field(
        default_factory=list,
        description="List of wind generation forecast records",
    )
    count: int = Field(
        ...,
        ge=0,
        description="Total number of forecast records in this payload",
    )
    settlement_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Filter settlement date if query was date-scoped",
        examples=["2026-10-24"],
    )
    fuel_type: str = Field(
        default="WIND",
        description="Reported fuel type",
    )


class ForecastFilterParams(BaseModel):
    """Parameters for querying wind forecasts."""

    model_config = ConfigDict(frozen=True)

    settlement_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="UK settlement date filter (YYYY-MM-DD)",
    )
    settlement_period: Optional[int] = Field(
        None,
        ge=1,
        le=50,
        description="Settlement period filter (1-50)",
    )
