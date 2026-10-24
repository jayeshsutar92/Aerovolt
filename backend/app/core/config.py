from functools import lru_cache
import json
from typing import Any, List, Union
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="Aerovolt", description="Name of the application")
    environment: str = Field(
        default="development",
        description="Current runtime environment (development, test, staging, production)",
    )
    version: str = Field(default="0.1.0", description="Application API version")
    debug: bool = Field(default=False, description="Debug mode flag")

    # API Routing configuration
    api_prefix: str = Field(default="/api", description="Base prefix for all API routes")

    # Frontend CORS origins
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        description="List of allowed CORS origins for browser clients",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[Any], None]) -> List[str]:
        """Parse CORS origins from a comma-separated string, JSON array, or list."""
        if value is None:
            return []
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        raise ValueError(f"Invalid CORS origins value: {value}")

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Enforce safe configuration in production: disallow wildcard CORS origins."""
        if self.environment.lower() == "production":
            for origin in self.cors_origins:
                if origin == "*" or origin.strip() == "*":
                    raise ValueError(
                        "Wildcard CORS origins ('*') are strictly prohibited in production."
                    )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached instance of application settings."""
    return Settings()
