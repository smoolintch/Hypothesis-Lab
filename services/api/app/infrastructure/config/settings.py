from functools import lru_cache
from pathlib import Path
from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_ENV_FILE = REPO_ROOT / ".env"
FALLBACK_ENV_FILE = REPO_ROOT / ".env.example"

if DEFAULT_ENV_FILE.exists():
    ENV_FILES = (DEFAULT_ENV_FILE,)
elif FALLBACK_ENV_FILE.exists():
    ENV_FILES = (FALLBACK_ENV_FILE,)
else:
    ENV_FILES = None


class Settings(BaseSettings):
    app_name: str = "Hypothesis Lab API"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    app_user_mode: str = Field(default="single_user", alias="APP_USER_MODE")
    default_user_id: UUID = Field(alias="DEFAULT_USER_ID")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    database_url: str = Field(alias="DATABASE_URL")

    model_config = SettingsConfigDict(
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
