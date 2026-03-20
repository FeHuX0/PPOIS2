import os
import shutil
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from crimsoland.app import CrimsolandApp
from crimsoland.config_loader import ConfigLoader


class PressedKeys:
    def __init__(self, active: set[int] | None = None):
        self.active = active or set()

    def __getitem__(self, key: int) -> bool:
        return key in self.active


@pytest.fixture(autouse=True)
def pygame_ready():
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.init()
    pygame.display.set_mode((1, 1))
    pygame.event.clear()
    yield
    if pygame.get_init() and pygame.display.get_init():
        pygame.event.clear()


@pytest.fixture()
def temp_game_data(tmp_path: Path):
    source_data = Path(__file__).resolve().parents[1] / 'src' / 'crimsoland' / 'data'
    target_data = tmp_path / 'data'
    shutil.copytree(source_data, target_data)
    return {
        'data_dir': target_data,
        'config_dir': target_data / 'configs',
        'highscores_file': target_data / 'highscores.json',
    }


@pytest.fixture()
def loaded_configs(temp_game_data):
    return ConfigLoader(temp_game_data['config_dir']).load_all()


@pytest.fixture()
def app(temp_game_data):
    game_app = CrimsolandApp(
        config_dir=temp_game_data['config_dir'],
        highscores_file=temp_game_data['highscores_file'],
        headless=True,
    )
    yield game_app
    game_app.shutdown()
