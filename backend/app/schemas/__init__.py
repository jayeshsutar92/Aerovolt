"""Pydantic schemas and API contracts for Aerovolt."""

from app.schemas.analytics import (
    AccuracyMetrics,
    ComparisonResponse,
    ForecastActualComparisonPoint,
)
from app.schemas.common import (
    ErrorDetail,
    ErrorResponse,
    TimeWindowParams,
)
from app.schemas.forecast import (
    ForecastFilterParams,
    ForecastListResponse,
    ForecastRecord,
)

__all__ = [
    # Forecast contracts
    "ForecastRecord",
    "ForecastListResponse",
    "ForecastFilterParams",
    # Analytics & comparison contracts
    "AccuracyMetrics",
    "ForecastActualComparisonPoint",
    "ComparisonResponse",
    # Common contracts
    "ErrorDetail",
    "ErrorResponse",
    "TimeWindowParams",
]
