from __future__ import annotations

import pygame

from crimsoland.state_manager import Screen
from crimsoland.ui_text import (
    FIRST_PLACE_TITLE,
    NAME_INPUT_CANCEL_HINT,
    NAME_INPUT_PROMPT,
    TOP_SCORE_TITLE,
    build_result_lines,
)


class NameInputScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        ui = app.configs["game"]["ui"]
        self.title_font = app.resource_manager.load_font(42, ui.get("font_name"))
        self.body_font = app.resource_manager.load_font(ui.get("font_size", 28), ui.get("font_name"))
        self.score = 0
        self.wave = 0
        self.victory = False
        self.is_first_place = False
        self.name = ""

    def on_enter(self, **kwargs) -> None:
        self.app.audio_system.play_music("menu")
        self.score = int(kwargs.get("score", 0))
        self.wave = int(kwargs.get("wave", 0))
        self.victory = bool(kwargs.get("victory", False))
        self.is_first_place = bool(kwargs.get("is_first_place", False))
        self.name = ""

    def handle_event(self, event: pygame.event.Event) -> None:
        limit = self.app.configs["game"]["highscores"]["name_max_length"]
        if event.type == pygame.TEXTINPUT and len(self.name) < limit:
            if event.text.isprintable():
                self.name += event.text
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.key == pygame.K_RETURN:
                safe_name = self.name.strip() or "PLAYER"
                self.app.score_system.record_score(safe_name, self.score)
                self.app.change_state("scores", highlight_name=safe_name[:limit])
            elif event.key == pygame.K_ESCAPE:
                self.app.change_state("menu")

    def render(self, surface: pygame.Surface) -> None:
        ui = self.app.configs["game"]["ui"]
        surface.fill(tuple(ui["background_color"]))
        title_text = FIRST_PLACE_TITLE if self.is_first_place else TOP_SCORE_TITLE
        title = self.title_font.render(title_text, True, tuple(ui["accent_color"]))
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 100)))
        details = [
            *build_result_lines(self.score, self.wave),
            NAME_INPUT_PROMPT,
        ]
        for index, line in enumerate(details):
            text = self.body_font.render(line, True, tuple(ui["text_color"]))
            surface.blit(text, text.get_rect(center=(surface.get_width() // 2, 180 + index * 40)))
        input_rect = pygame.Rect(surface.get_width() // 2 - 180, 320, 360, 56)
        pygame.draw.rect(surface, tuple(ui["panel_color"]), input_rect, border_radius=10)
        pygame.draw.rect(surface, tuple(ui["accent_color"]), input_rect, 2, border_radius=10)
        shown_name = self.name or "_"
        text = self.body_font.render(shown_name, True, tuple(ui["text_color"]))
        surface.blit(text, text.get_rect(center=input_rect.center))
        footer = self.body_font.render(NAME_INPUT_CANCEL_HINT, True, tuple(ui["text_color"]))
        surface.blit(footer, footer.get_rect(center=(surface.get_width() // 2, 410)))
