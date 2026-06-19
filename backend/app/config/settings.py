"""WorkClaw configuration management."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "WorkClaw"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/workclaw.db"

    # Auth (simplified for local dev)
    secret_key: str = "dev-secret-key-change-in-production"
    auth_mode: str = "local"  # local | oauth (future)
    default_user_email: str = "dev@workclaw.local"

    # LLM
    default_model_profile: str = "claude-glm-5.1"
    anthropic_api_key: str = ""
    anthropic_auth_token: str = ""
    anthropic_base_url: str = "https://aigw-gzgy2.cucloud.cn:8443"
    anthropic_model: str = "glm-5.1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = ""

    # Permission
    default_permission_mode: str = "moderate"  # strict | moderate | trusted

    # File upload
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 20
    allowed_file_types: list[str] = [
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]

    # Context
    max_context_tokens: int = 100000
    compaction_threshold: float = 0.8

    model_config = {"env_prefix": "WORKCLAW_", "env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
