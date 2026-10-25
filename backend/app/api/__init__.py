"""Centralized API router organization."""

from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.forecasts import router as forecasts_router
from app.api.routes.health import router as health_router

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health_router)
api_router.include_router(forecasts_router)
api_router.include_router(analytics_router)

__all__ = ["api_router"]
