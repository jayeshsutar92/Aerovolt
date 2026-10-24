"""Common shared schema contracts for Aerovolt API responses and errors."""

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.utils.datetime_utils import ensure_utc


class ErrorDetail(BaseModel):
    """Standardized error payload detail."""

    model_config = ConfigDict(frozen=True)

    code: str = Field(
        ...,
        description="Machine-readable error code (e.g. 'VALIDATION_ERROR', 'RESOURCE_NOT_FOUND')",
        examples=["INVALID_TIMESTAMP"],
    )
    message: str = Field(
        ...,
        description="Human-readable summary of the error",
        examples=["The specified settlement date is malformed."],
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Contextual diagnostic attributes or field-level validation errors",
    )


class ErrorResponse(BaseModel):
    """Standardized top-level error response envelope."""

    model_config = ConfigDict(frozen=True)

    error: ErrorDetail = Field(..., description="Error details envelope")


class TimeWindowParams(BaseModel):
    """Query parameters defining a UTC time window for analytics and forecasts."""

    model_config = ConfigDict(frozen=True)

    start_time: datetime = Field(..., description="Start of window in UTC")
    end_time: datetime = Field(..., description="End of window in UTC")

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def normalize_utc(cls, value: Any) -> datetime:
        """Ensure input datetimes are parsed and normalized to UTC."""
        if isinstance(value, datetime):
            return ensure_utc(value, assume_utc=True)
        if isinstance(value, str):
            from app.utils.datetime_utils import parse_timestamp
            from datetime import timezone

            return parse_timestamp(value, default_tz=timezone.utc)
        raise ValueError(f"Invalid datetime input: {value}")

    @model_validator(mode="after")
    def validate_interval(self) -> "TimeWindowParams":
        """Verify that end_time is not prior to start_time."""
        if self.end_time < self.start_time:
            raise ValueError(
                f"end_time ({self.end_time.isoformat()}) cannot be before "
                f"start_time ({self.start_time.isoformat()})."
            )
        return self
