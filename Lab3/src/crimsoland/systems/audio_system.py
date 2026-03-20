from __future__ import annotations

from pathlib import Path

import pygame

from crimsoland.resource_manager import ResourceManager


class AudioSystem:
    def __init__(self, config: dict, resource_manager: ResourceManager, enabled: bool = True):
        self.config = config
        self.resource_manager = resource_manager
        self.enabled = enabled
        self.current_music: str | None = None

    def play_music(self, track_name: str) -> None:
        if not self.enabled or not self.resource_manager.ensure_mixer():
            return
        track_map = self.config.get("music", {})
        track_path = track_map.get(track_name)
        if not track_path:
            return
        path = Path(track_path)
        if self.resource_manager.asset_root is not None and not path.is_absolute():
            path = self.resource_manager.asset_root / path
        if not path.exists():
            return
        try:
            if self.current_music != track_name:
                pygame.mixer.music.load(str(path))
                pygame.mixer.music.set_volume(self.config.get("music_volume", 0.0))
                pygame.mixer.music.play(-1)
                self.current_music = track_name
        except pygame.error:
            return

    def stop_music(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.current_music = None

    def play_sound(self, sound_name: str) -> None:
        if not self.enabled:
            return
        sound_path = self.config.get("sounds", {}).get(sound_name)
        sound = self.resource_manager.load_sound(sound_path)
        if hasattr(sound, "set_volume"):
            sound.set_volume(self.config.get("sfx_volume", 0.0))
        if hasattr(sound, "play"):
            sound.play()
