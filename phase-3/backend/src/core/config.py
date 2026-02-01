"""
Application configuration using pydantic-settings.

Loads environment variables from .env file and provides type-safe access.
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    # ========================================
    # Database Configuration
    # ========================================
    database_url: str = Field(
        default='postgresql+psycopg://todoapp:todoapp_password@localhost:5432/todoapp',
        description='PostgreSQL connection string',
    )

    # ========================================
    # JWT Authentication
    # ========================================
    jwt_secret: str = Field(
        ...,
        min_length=32,
        description='Secret key for JWT token signing (min 32 characters)',
    )

    jwt_algorithm: str = Field(default='HS256', description='JWT algorithm')
    jwt_expiration_days: int = Field(default=7, description='JWT token expiration in days')

    # ========================================
    # Cloudinary Configuration (Avatar Storage)
    # ========================================
    cloudinary_cloud_name: Optional[str] = Field(
        default=None, description='Cloudinary cloud name'
    )
    cloudinary_api_key: Optional[str] = Field(default=None, description='Cloudinary API key')
    cloudinary_api_secret: Optional[str] = Field(
        default=None, description='Cloudinary API secret'
    )

    # ========================================
    # Hugging Face AI Configuration
    # ========================================
    huggingface_api_key: Optional[str] = Field(
        default=None, description='Hugging Face API key'
    )

    # ========================================
    # Email Configuration (Gmail SMTP)
    # ========================================
    gmail_email: Optional[str] = Field(
        default=None, description='Gmail address for sending reminders'
    )
    gmail_app_password: Optional[str] = Field(
        default=None, description='Gmail app-specific password for SMTP'
    )

    # ========================================
    # Frontend URL
    # ========================================
    frontend_url: str = Field(
        default='http://localhost:3000',
        description='Allowed CORS origin for frontend',
    )

    # ========================================
    # Application Settings
    # ========================================
    env: str = Field(default='development', description='Environment: development, staging, production')
    port: int = Field(default=8801, description='API port')
    log_level: str = Field(default='info', description='Log level: debug, info, warning, error, critical')

    # ========================================
    # Security Settings
    # ========================================
    bcrypt_rounds: int = Field(default=12, description='Bcrypt password hashing rounds')
    cors_origins: list[str] = Field(
        default=['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001', 'http://127.0.0.1:3002'], description='CORS allowed origins'
    )

    @field_validator('env')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'env must be one of {allowed}')
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        allowed = ['debug', 'info', 'warning', 'error', 'critical']
        if v not in allowed:
            raise ValueError(f'log_level must be one of {allowed}')
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.env == 'development'

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.env == 'production'

    @property
    def database_url_sync(self) -> str:
        """
        Get synchronous database URL for Alembic migrations.
        Replaces postgresql+psycopg with postgresql+psycopg2.
        """
        return self.database_url.replace('+psycopg', '+psycopg2')


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Export settings instance
settings = get_settings()
