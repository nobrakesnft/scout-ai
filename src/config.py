"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Literal["development", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    database_path: Path = Path("data/scout.db")

    # GitHub
    github_token: SecretStr = Field(..., description="GitHub Personal Access Token")

    # Telegram
    telegram_bot_token: SecretStr = Field(..., description="Telegram Bot Token")
    telegram_chat_id: str = Field(..., description="Telegram Chat ID to send messages to")
    telegram_webhook_url: str | None = Field(
        default=None, description="Webhook URL for production"
    )

    # AI Providers (priority order: DeepSeek > Qwen > OpenAI > Anthropic)
    deepseek_api_key: SecretStr | None = Field(
        default=None, description="DeepSeek API Key (primary, cheapest)"
    )
    qwen_api_key: SecretStr | None = Field(
        default=None, description="Qwen API Key (secondary)"
    )
    openai_api_key: SecretStr | None = Field(
        default=None, description="OpenAI API Key (fallback, expensive)"
    )
    anthropic_api_key: SecretStr | None = Field(
        default=None, description="Anthropic API Key (last resort)"
    )

    # Scheduler
    digest_schedule: str = Field(
        default="0 8 * * *", description="Cron expression for daily digest"
    )
    run_frequency: int = Field(default=2, description="Times per day to run scanner")

    # Cost Controls
    max_repos_per_run: int = Field(default=5, description="Max repos to analyze per run")
    max_tokens_per_run: int = Field(default=50000, description="Max tokens per run")
    monthly_budget_usd: float = Field(default=30.0, description="Monthly budget in USD")

    # Feature Flags
    enable_builder: bool = Field(default=False, description="Enable builder agent")
    enable_learning: bool = Field(default=False, description="Enable learning system")

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    @property
    def use_webhook(self) -> bool:
        """Check if webhook mode should be used."""
        return self.is_production and self.telegram_webhook_url is not None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
