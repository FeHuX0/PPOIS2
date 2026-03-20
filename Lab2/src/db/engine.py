from sqlalchemy import Engine, create_engine

from src.core.settings import Settings


def validate_database_url(database_url: str) -> str:
    if not database_url.startswith("postgresql+psycopg2://"):
        raise RuntimeError(
            "DATABASE_URL должен использовать драйвер psycopg2 и начинаться с "
            "'postgresql+psycopg2://'."
        )
    return database_url


def create_db_engine(settings: Settings) -> Engine:
    return create_engine(
        validate_database_url(settings.database_url),
        future=True,
        pool_pre_ping=True,
    )
