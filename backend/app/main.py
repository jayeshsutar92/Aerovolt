from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    description="Aerovolt — Wind generation forecasting and analytics backend service.",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes with consistent /api prefix
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"], summary="Root endpoint")
def root():
    """Service status and quick links."""
    return {
        "message": f"{settings.app_name} backend is running",
        "docs_url": "/docs",
        "health_check": f"{settings.api_prefix}/health",
    }