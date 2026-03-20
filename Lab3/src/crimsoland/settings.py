from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_ROOT / "data"
CONFIG_DIR = DATA_DIR / "configs"
HIGHSCORES_FILE = DATA_DIR / "highscores.json"
DEFAULT_STATE = "menu"


@dataclass(slots=True)
class RuntimePaths:
    config_dir: Path
    highscores_file: Path
    data_dir: Path


def build_runtime_paths(
    config_dir: str | Path | None = None,
    highscores_file: str | Path | None = None,
) -> RuntimePaths:
    config_path = Path(config_dir) if config_dir is not None else CONFIG_DIR
    highscores_path = (
        Path(highscores_file) if highscores_file is not None else HIGHSCORES_FILE
    )
    return RuntimePaths(
        config_dir=config_path,
        highscores_file=highscores_path,
        data_dir=config_path.parent,
    )
