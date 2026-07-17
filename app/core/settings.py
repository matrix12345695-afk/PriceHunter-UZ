from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==========================================================
    # Project
    # ==========================================================

    PROJECT_NAME: str = "PriceHunter UZ"
    VERSION: str = "0.1.0"

    DEBUG: bool = True

    # ==========================================================
    # Telegram
    # ==========================================================

    BOT_TOKEN: str = Field(...)

    ADMIN_IDS: str = ""

    WEBHOOK_URL: str = ""

    WEBHOOK_SECRET: str = ""

    # ==========================================================
    # Database
    # ==========================================================

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/pricehunter"
    )

    # ==========================================================
    # Redis
    # ==========================================================

    REDIS_URL: str = "redis://localhost:6379"

    # ==========================================================
    # Logging
    # ==========================================================

    LOG_LEVEL: str = "INFO"

    # ==========================================================
    # Scheduler
    # ==========================================================

    PRICE_CHECK_INTERVAL: int = 60

    # ==========================================================
    # OpenAI
    # ==========================================================

    OPENAI_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
