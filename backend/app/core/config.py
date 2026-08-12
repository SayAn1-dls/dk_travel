"""Application configuration using pydantic settings."""
import os
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/dk_travel",
    )
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    echo: bool = False


@dataclass
class RedisConfig:
    url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    max_connections: int = 20
    decode_responses: bool = True


@dataclass
class AuthConfig:
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 30
    password_min_length: int = 8


@dataclass
class StorageConfig:
    provider: str = os.getenv("STORAGE_PROVIDER", "s3")
    bucket_name: str = os.getenv("STORAGE_BUCKET", "dk-travel-uploads")
    region: str = os.getenv("STORAGE_REGION", "ap-south-1")
    cdn_url: str = os.getenv("CDN_URL", "")


@dataclass
class EmailConfig:
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = 587
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    from_email: str = os.getenv("FROM_EMAIL", "noreply@dktravel.com")
    from_name: str = "DK Travel"


@dataclass
class AppConfig:
    app_name: str = "DK Travel API"
    version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENV", "development")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    allowed_origins: List[str] = field(
        default_factory=lambda: os.getenv(
            "ALLOWED_ORIGINS", "http://localhost:3000"
        ).split(",")
    )
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Sub-configs
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    email: EmailConfig = field(default_factory=EmailConfig)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


# Singleton
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
