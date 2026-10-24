from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Structured response schema for health check endpoint."""

    status: str = Field(default="healthy", description="Application operational status")
    app: str = Field(description="Application name")
    environment: str = Field(description="Current runtime environment")
    version: str = Field(description="Application version")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
    description="Returns application health status, environment, and version.",
)
async def get_health(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Return application operational status and metadata."""
    return HealthResponse(
        status="healthy",
        app=settings.app_name,
        environment=settings.environment,
        version=settings.version,
    )
