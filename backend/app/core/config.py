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
    ingest_batch_size: int = 10
    csv_source_path: str = "./data/sample_macro_sentiment.csv"

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
