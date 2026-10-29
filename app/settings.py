from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    title: str = "Network Route Optimizer"
    version: str = "1.0.0"
    database_url: str = "sqlite:///./routes.db"
    log_level: str = "INFO"
    history_default_limit: int = 50
    history_max_limit: int = 500


@lru_cache
def get_settings() -> Settings:
    return Settings()
