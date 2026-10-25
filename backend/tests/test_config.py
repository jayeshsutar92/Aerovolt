import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_default_settings():
    """Verify default settings initialization."""
    settings = Settings()
    assert settings.app_name == "Aerovolt"
    assert settings.environment == "development"
    assert settings.api_prefix == "/api"
    assert "http://localhost:5173" in settings.cors_origins


def test_comma_separated_cors_origins():
    """Verify comma-separated string parsing for CORS origins."""
    settings = Settings(cors_origins="http://localhost:3000, https://aerovolt.app")
    assert settings.cors_origins == ["http://localhost:3000", "https://aerovolt.app"]


def test_json_array_cors_origins():
    """Verify JSON array string parsing for CORS origins."""
    settings = Settings(cors_origins='["http://localhost:3000", "https://aerovolt.app"]')
    assert settings.cors_origins == ["http://localhost:3000", "https://aerovolt.app"]


def test_production_disallows_wildcard_cors():
    """Production environment must disallow wildcard CORS origins."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(environment="production", cors_origins="*")

    assert "Wildcard CORS origins ('*') are strictly prohibited in production." in str(
        exc_info.value
    )


def test_production_allows_explicit_origins():
    """Production environment should allow explicitly specified non-wildcard domains."""
    settings = Settings(
        environment="production", cors_origins="https://aerovolt.app,https://admin.aerovolt.app"
    )
    assert settings.environment == "production"
    assert settings.cors_origins == ["https://aerovolt.app", "https://admin.aerovolt.app"]


def test_cors_origins_from_environment_comma_separated(monkeypatch):
    """Verify that pydantic-settings EnvSettingsSource correctly parses comma-separated CORS_ORIGINS."""
    monkeypatch.setenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:80"
    )
    settings = Settings()
    assert settings.cors_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:80",
    ]


def test_cors_origins_from_environment_json_array(monkeypatch):
    """Verify that pydantic-settings EnvSettingsSource correctly parses JSON array CORS_ORIGINS."""
    monkeypatch.setenv(
        "CORS_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173"]'
    )
    settings = Settings()
    assert settings.cors_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

