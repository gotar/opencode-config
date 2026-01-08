"""
Configuration management with Pydantic Settings.

This example shows:
- Environment variable loading
- Type validation
- Default values
- Multiple configuration sources
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl, PostgresDsn, validator
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings with validation."""

    # Application
    app_name: str = "Example API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, ge=1, le=65535, env="PORT")

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql://user:pass@localhost:5432/db",
        env="DATABASE_URL",
    )

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        min_length=32,
        env="SECRET_KEY",
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = Field(default=3600, ge=60)

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        env="CORS_ORIGINS",
    )

    # External services
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    external_api_url: Optional[HttpUrl] = Field(default=None, env="EXTERNAL_API_URL")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Feature flags
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Create global settings instance
settings = Settings()


# Example usage
if __name__ == "__main__":
    print("Configuration loaded:")
    print(f"  App Name: {settings.app_name}")
    print(f"  Debug: {settings.debug}")
    print(f"  Database: {settings.database_url}")
    print(f"  Log Level: {settings.log_level}")
    print(f"  CORS Origins: {settings.cors_origins}")

    # Access environment-specific settings
    if settings.debug:
        print("  ⚠️  DEBUG MODE ENABLED")
    else:
        print("  Production mode")
