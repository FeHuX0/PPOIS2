from __future__ import annotations

import pygame

from crimsoland.state_manager import Screen
from crimsoland.ui_text import BACK_TO_MENU_HINT, SCORES_EMPTY, SCORES_TITLE


class ScoresScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        ui = app.configs["game"]["ui"]
        self.title_font = app.resource_manager.load_font(44, ui.get("font_name"))
        self.body_font = app.resource_manager.load_font(ui.get("small_font_size", 20), ui.get("font_name"))
        self.entries = []
        self.highlight_name: str | None = None

    def on_enter(self, **kwargs) -> None:
        self.app.audio_system.play_music("menu")
        self.entries = self.app.score_system.load()
        self.highlight_name = kwargs.get("highlight_name")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.app.change_state("menu")

    def render(self, surface: pygame.Surface) -> None:
        ui = self.app.configs["game"]["ui"]
        surface.fill(tuple(ui["background_color"]))
        title = self.title_font.render(SCORES_TITLE, True, tuple(ui["accent_color"]))
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 60)))
        for index, entry in enumerate(self.entries[:10], start=1):
            color = tuple(ui["accent_color"]) if entry.name == self.highlight_name else tuple(ui["text_color"])
            row = f"{index:>2}. {entry.name:<12}  {entry.score:>5}  {entry.date}"
            text = self.body_font.render(row, True, color)
            surface.blit(text, (120, 120 + index * 32))
        if not self.entries:
            empty = self.body_font.render(SCORES_EMPTY, True, tuple(ui["text_color"]))
            surface.blit(empty, (120, 160))
        footer = self.body_font.render(BACK_TO_MENU_HINT, True, tuple(ui["text_color"]))
        surface.blit(footer, (120, surface.get_height() - 50))
