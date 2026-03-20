from __future__ import annotations

from pathlib import Path

import pygame


class NullSound:
    def play(self) -> None:
        return None

    def set_volume(self, _: float) -> None:
        return None


class ResourceManager:
    def __init__(self, asset_root: str | Path | None = None):
        self.asset_root = Path(asset_root) if asset_root is not None else None
        self._fonts: dict[tuple[str | None, int], pygame.font.Font] = {}
        self._sounds: dict[Path, object] = {}

    def ensure_mixer(self) -> bool:
        if pygame.mixer.get_init():
            return True
        try:
            pygame.mixer.init()
        except pygame.error:
            return False
        return True

    def load_font(self, size: int, font_name: str | None = None) -> pygame.font.Font:
        key = (font_name, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont(font_name, size)
        return self._fonts[key]

    def load_sound(self, sound_path: str | Path | None) -> object:
        if not sound_path:
            return NullSound()
        path = Path(sound_path)
        if self.asset_root is not None and not path.is_absolute():
            path = self.asset_root / path
        if path in self._sounds:
            return self._sounds[path]
        if not path.exists() or not self.ensure_mixer():
            self._sounds[path] = NullSound()
            return self._sounds[path]
        try:
            sound = pygame.mixer.Sound(str(path))
        except pygame.error:
            sound = NullSound()
        self._sounds[path] = sound
        return sound
