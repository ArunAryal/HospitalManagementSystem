"""
Configuration management for the application.

This module centralizes environment-based configuration using pydantic Settings,
enabling environment-specific configuration and type-safe access.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "Hospital Management System API"
    api_description: str = "A comprehensive Hospital Management System with patient, doctor, appointment, and billing management"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Database Configuration
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "hospital_management"
    db_echo: bool = False

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    cors_headers: List[str] = ["*"]

    # JWT/Authentication (for future use)
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application Settings
    pagination_default_limit: int = 100
    pagination_max_limit: int = 1000
    pagination_default_skip: int = 0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """Construct database URL from components."""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return os.getenv("ENVIRONMENT") == "production"

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return os.getenv("ENVIRONMENT") == "test"


# Create global settings instance
settings = Settings()
