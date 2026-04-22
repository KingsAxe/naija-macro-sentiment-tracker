from app.core.config import get_settings


def _normalize_postgres_driver(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def get_database_url() -> str:
    return _normalize_postgres_driver(get_settings().database_url)
