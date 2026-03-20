from __future__ import annotations

import pygame

from crimsoland.state_manager import Screen
from crimsoland.ui_text import (
    GAME_OVER_MENU_HINT,
    GAME_OVER_SCORES_HINT,
    GAME_OVER_TITLE,
    VICTORY_TITLE,
    build_result_lines,
)


class GameOverScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        ui = app.configs["game"]["ui"]
        self.title_font = app.resource_manager.load_font(46, ui.get("font_name"))
        self.body_font = app.resource_manager.load_font(ui.get("font_size", 28), ui.get("font_name"))
        self.score = 0
        self.wave = 0
        self.victory = False

    def on_enter(self, **kwargs) -> None:
        self.app.audio_system.play_music("menu")
        self.score = int(kwargs.get("score", 0))
        self.wave = int(kwargs.get("wave", 0))
        self.victory = bool(kwargs.get("victory", False))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.app.change_state("menu")
            elif event.key == pygame.K_TAB:
                self.app.change_state("scores")

    def render(self, surface: pygame.Surface) -> None:
        ui = self.app.configs["game"]["ui"]
        surface.fill(tuple(ui["background_color"]))
        title_text = VICTORY_TITLE if self.victory else GAME_OVER_TITLE
        title = self.title_font.render(title_text, True, tuple(ui["accent_color"]))
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 120)))
        lines = [
            *build_result_lines(self.score, self.wave),
            GAME_OVER_MENU_HINT,
            GAME_OVER_SCORES_HINT,
        ]
        for index, line in enumerate(lines):
            text = self.body_font.render(line, True, tuple(ui["text_color"]))
            surface.blit(text, text.get_rect(center=(surface.get_width() // 2, 220 + index * 50)))
