import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

from dotenv import dotenv_values


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str


def load_settings(
    env_file: Optional[Path] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> Settings:
    dotenv_path = env_file or Path(".env")
    dotenv_data = {
        key: value
        for key, value in dotenv_values(dotenv_path).items()
        if value is not None
    }
    environment = environ or os.environ
    database_url = str(
        environment.get("DATABASE_URL")
        or dotenv_data.get("DATABASE_URL")
        or ""
    ).strip()
    if not database_url:
        raise RuntimeError(
            "Переменная окружения DATABASE_URL не задана. "
            "Укажите её в окружении или в файле .env."
        )

    return Settings(database_url=database_url)
