"""API route handlers."""

from app.api.routes.analytics import router as analytics_router
from app.api.routes.forecasts import router as forecasts_router
from app.api.routes.health import router as health_router

__all__ = ["health_router", "forecasts_router", "analytics_router"]
