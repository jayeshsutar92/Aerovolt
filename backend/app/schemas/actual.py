"""Pydantic schemas for actual wind generation contracts."""

from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.datetime_utils import ensure_utc, parse_timestamp


class ActualGenerationRecord(BaseModel):
    """Schema representing an actual wind generation outturn record for a settlement period."""

    model_config = ConfigDict(frozen=True)

    start_time: datetime = Field(
        ...,
        description="Target delivery start timestamp in UTC (half-hour window start)",
        examples=["2026-01-01T00:00:00Z"],
    )
    settlement_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="UK electricity settlement date (YYYY-MM-DD)",
        examples=["2026-01-01"],
    )
    settlement_period: int = Field(
        ...,
        ge=1,
        le=50,
        description="UK half-hourly settlement period (1-48; 46 or 50 on clock-change days)",
        examples=[1],
    )
    generation_mw: float = Field(
        ...,
        ge=0.0,
        description="Actual measured wind generation in megawatts (MW)",
        examples=[1420.5],
    )
    fuel_type: str = Field(
        default="WIND",
        description="Generation fuel source type",
        examples=["WIND"],
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


class ActualGenerationListResponse(BaseModel):
    """Container schema for actual generation outturn queries."""

    model_config = ConfigDict(frozen=True)

    items: List[ActualGenerationRecord] = Field(
        default_factory=list,
        description="List of actual generation outturn records",
    )
    count: int = Field(
        ...,
        ge=0,
        description="Total number of actual generation records",
    )
    settlement_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Filtered settlement date if query was date-scoped",
        examples=["2026-01-01"],
    )
    fuel_type: str = Field(
        default="WIND",
        description="Reported fuel type",
    )
