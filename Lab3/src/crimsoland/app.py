from __future__ import annotations

from pathlib import Path

import pygame

from crimsoland.config_loader import ConfigLoader
from crimsoland.resource_manager import ResourceManager
from crimsoland.screens import (
    GameOverScreen,
    GameScreen,
    HelpScreen,
    MenuScreen,
    NameInputScreen,
    ScoresScreen,
)
from crimsoland.settings import DEFAULT_STATE, build_runtime_paths
from crimsoland.state_manager import StateManager
from crimsoland.systems.audio_system import AudioSystem
from crimsoland.systems.score_system import ScoreSystem


class CrimsolandApp:
    def __init__(
        self,
        config_dir: str | Path | None = None,
        highscores_file: str | Path | None = None,
        headless: bool = False,
    ):
        self.paths = build_runtime_paths(config_dir, highscores_file)
        pygame.init()
        pygame.font.init()
        self.configs = ConfigLoader(self.paths.config_dir).load_all()
        window = self.configs["game"]["window"]
        flags = pygame.HIDDEN if headless and hasattr(pygame, "HIDDEN") else 0
        self.surface = pygame.display.set_mode((window["width"], window["height"]), flags)
        pygame.display.set_caption(self.configs["game"]["title"])
        self.clock = pygame.time.Clock()
        self.running = True
        self.headless = headless
        self.resource_manager = ResourceManager(self.paths.data_dir / "assets")
        self.audio_system = AudioSystem(
            self.configs["audio"],
            self.resource_manager,
            enabled=not headless,
        )
        highscore_settings = self.configs["game"]["highscores"]
        self.score_system = ScoreSystem(
            self.paths.highscores_file,
            limit=highscore_settings["limit"],
            name_max_length=highscore_settings["name_max_length"],
        )
        self.state_manager = StateManager(self)
        self._register_screens()
        self.change_state(DEFAULT_STATE)

    def _register_screens(self) -> None:
        self.state_manager.register("menu", MenuScreen(self))
        self.state_manager.register("game", GameScreen(self))
        self.state_manager.register("help", HelpScreen(self))
        self.state_manager.register("scores", ScoresScreen(self))
        self.state_manager.register("game_over", GameOverScreen(self))
        self.state_manager.register("name_input", NameInputScreen(self))

    def change_state(self, name: str, **kwargs: object) -> None:
        self.state_manager.set_state(name, **kwargs)

    def stop(self) -> None:
        self.running = False

    def run(self, max_frames: int | None = None) -> int:
        fps = self.configs["game"]["window"]["fps"]
        frames = 0
        while self.running:
            dt_ms = self.clock.tick(fps)
            now_ms = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                else:
                    self.state_manager.handle_event(event)
            self.state_manager.update(dt_ms / 1000, now_ms)
            self.state_manager.render(self.surface)
            pygame.display.flip()
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
        return 0

    def shutdown(self) -> None:
        self.audio_system.stop_music()
        pygame.quit()
