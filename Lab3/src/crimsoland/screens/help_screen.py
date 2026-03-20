from __future__ import annotations

import pygame

from crimsoland.state_manager import Screen
from crimsoland.ui_text import BACK_TO_MENU_HINT, HELP_BLOCKS, HELP_TITLE
from crimsoland.utils import wrap_text


class HelpScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        ui = app.configs["game"]["ui"]
        self.title_font = app.resource_manager.load_font(44, ui.get("font_name"))
        self.body_font = app.resource_manager.load_font(ui.get("small_font_size", 20), ui.get("font_name"))
        self.blocks = list(HELP_BLOCKS)

    def on_enter(self, **kwargs) -> None:
        self.app.audio_system.play_music("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.app.change_state("menu")

    def render(self, surface: pygame.Surface) -> None:
        ui = self.app.configs["game"]["ui"]
        surface.fill(tuple(ui["background_color"]))
        title = self.title_font.render(HELP_TITLE, True, tuple(ui["accent_color"]))
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 60)))
        y = 120
        for block in self.blocks:
            for line in wrap_text(self.body_font, block, surface.get_width() - 120):
                text = self.body_font.render(line, True, tuple(ui["text_color"]))
                surface.blit(text, (60, y))
                y += 28
            y += 16
        footer = self.body_font.render(BACK_TO_MENU_HINT, True, tuple(ui["text_color"]))
        surface.blit(footer, (60, surface.get_height() - 50))
