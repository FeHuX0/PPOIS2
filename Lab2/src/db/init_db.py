from sqlalchemy import Engine, text

from src.models.athlete import Athlete
from src.models.base import Base


def initialize_database(engine: Engine) -> None:
    _ = Athlete
    Base.metadata.create_all(bind=engine)


def check_database_connection(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
