from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "Naija Sentiment Tracker API"
    app_env: str = "development"
    api_v1_prefix: str = "/api"
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")
    pghost: str = "localhost"
    pgport: int = 5432
    pgdatabase: str = "naija_sentiment_tracker"
    pguser: str | None = None
    pgpassword: str | None = None
    azure_language_endpoint: str = ""
    azure_language_key: str = ""
    azure_language_default_language: str = "en"
    azure_language_batch_size: int = 10
    azure_language_retry_attempts: int = 3
    azure_language_retry_delay_seconds: int = 2
    azure_language_batch_sleep_seconds: float = 1.0
    ingest_batch_size: int = 10
    csv_source_path: str = "./data/raw_macro_data.csv"
    frontend_origin: str = "http://localhost:3000"
    auto_create_schema_on_startup: bool = False
    scheduler_enabled: bool = False
    scheduler_daily_hour: int = 6
    scheduler_include_news: bool = True
    scheduler_news_limit: int = 20
    scheduler_skip_news_pages: bool = True

    @computed_field
    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override

        if self.pguser and self.pgpassword:
            encoded_user = quote_plus(self.pguser)
            encoded_password = quote_plus(self.pgpassword)
            return (
                f"postgresql+psycopg://{encoded_user}:{encoded_password}"
                f"@{self.pghost}:{self.pgport}/{self.pgdatabase}"
            )

        return "sqlite:///./naija_sentiment.db"

    @computed_field
    @property
    def cors_allowed_origins(self) -> list[str]:
        origins = {
            self.frontend_origin,
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        }
        return sorted(origin for origin in origins if origin)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
