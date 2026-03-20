from __future__ import annotations

import pygame

from crimsoland.state_manager import Screen
from crimsoland.ui_text import MENU_FOOTER, MENU_OPTIONS, MENU_SUBTITLE


class MenuScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        ui = app.configs["game"]["ui"]
        self.title_font = app.resource_manager.load_font(56, ui.get("font_name"))
        self.body_font = app.resource_manager.load_font(ui.get("font_size", 28), ui.get("font_name"))
        self.small_font = app.resource_manager.load_font(ui.get("small_font_size", 20), ui.get("font_name"))
        self.options = list(MENU_OPTIONS)
        self.selected = 0
        self.option_rects: list[pygame.Rect] = []

    def on_enter(self, **kwargs) -> None:
        self.app.audio_system.play_music("menu")
        if "selected" in kwargs:
            self.selected = int(kwargs["selected"])

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate(self.selected)
            elif event.key == pygame.K_ESCAPE:
                self.app.stop()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self._activate(index)
                    break

    def _activate(self, index: int) -> None:
        _, action = self.options[index]
        if action == "quit":
            self.app.stop()
        else:
            self.app.change_state(action)

    def render(self, surface: pygame.Surface) -> None:
        ui = self.app.configs["game"]["ui"]
        text_color = tuple(ui["text_color"])
        accent = tuple(ui["accent_color"])
        panel = tuple(ui["panel_color"])
        surface.fill(tuple(ui["background_color"]))
        title = self.title_font.render("Crimsoland", True, accent)
        subtitle = self.small_font.render(MENU_SUBTITLE, True, text_color)
        surface.blit(title, title.get_rect(center=(surface.get_width() // 2, 90)))
        surface.blit(subtitle, subtitle.get_rect(center=(surface.get_width() // 2, 135)))
        self.option_rects = []
        for index, (label, _) in enumerate(self.options):
            is_selected = index == self.selected
            rect = pygame.Rect(surface.get_width() // 2 - 180, 190 + index * 70, 360, 52)
            self.option_rects.append(rect)
            pygame.draw.rect(surface, panel, rect, border_radius=10)
            if is_selected:
                pygame.draw.rect(surface, accent, rect, 3, border_radius=10)
            label_surface = self.body_font.render(label, True, accent if is_selected else text_color)
            surface.blit(label_surface, label_surface.get_rect(center=rect.center))
        footer = self.small_font.render(MENU_FOOTER, True, text_color)
        surface.blit(footer, footer.get_rect(center=(surface.get_width() // 2, surface.get_height() - 40)))
