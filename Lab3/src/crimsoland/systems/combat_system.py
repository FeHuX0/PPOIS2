from __future__ import annotations

import pygame

from crimsoland.entities.enemy import Enemy
from crimsoland.entities.player import Player
from crimsoland.systems.audio_system import AudioSystem


class CombatSystem:
    @staticmethod
    def player_attack(
        player: Player,
        target: pygame.Vector2,
        now_ms: int,
        audio_system: AudioSystem | None = None,
    ):
        bullets = player.shoot(target, now_ms)
        if bullets and audio_system is not None:
            audio_system.play_sound(player.current_weapon.sound)
        return bullets

    @staticmethod
    def enemy_attack(
        enemy: Enemy,
        player_position: pygame.Vector2,
        now_ms: int,
        audio_system: AudioSystem | None = None,
    ):
        bullets = enemy.try_attack(player_position, now_ms)
        if bullets and audio_system is not None:
            audio_system.play_sound("enemy_shot")
        return bullets
