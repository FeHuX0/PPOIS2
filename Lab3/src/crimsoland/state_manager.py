from __future__ import annotations

from typing import Any


class Screen:
    def __init__(self, app: Any):
        self.app = app

    def on_enter(self, **kwargs: Any) -> None:
        return None

    def on_exit(self) -> None:
        return None

    def handle_event(self, event: Any) -> None:
        return None

    def update(self, dt: float, now_ms: int) -> None:
        return None

    def render(self, surface: Any) -> None:
        return None


class StateManager:
    def __init__(self, app: Any):
        self.app = app
        self._screens: dict[str, Screen] = {}
        self.current_name: str | None = None
        self.current_screen: Screen | None = None

    def register(self, name: str, screen: Screen) -> None:
        self._screens[name] = screen

    def set_state(self, name: str, **kwargs: Any) -> None:
        if name not in self._screens:
            raise KeyError(f"Неизвестное состояние: {name}")
        if self.current_screen is not None:
            self.current_screen.on_exit()
        self.current_name = name
        self.current_screen = self._screens[name]
        self.current_screen.on_enter(**kwargs)

    def handle_event(self, event: Any) -> None:
        if self.current_screen is not None:
            self.current_screen.handle_event(event)

    def update(self, dt: float, now_ms: int) -> None:
        if self.current_screen is not None:
            self.current_screen.update(dt, now_ms)

    def render(self, surface: Any) -> None:
        if self.current_screen is not None:
            self.current_screen.render(surface)
