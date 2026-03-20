from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from crimsoland.entities.bullet import Bullet
from crimsoland.utils import normalize_or_zero, vector_from_angle


@dataclass(slots=True)
class WeaponSpec:
    name: str
    label: str
    damage: int
    cooldown_ms: int
    bullet_speed: float
    spread_deg: float
    projectiles_per_shot: int
    max_range: float
    bullet_radius: int
    bullet_color: tuple[int, int, int]
    sound: str

    @classmethod
    def from_dict(cls, name: str, payload: dict) -> "WeaponSpec":
        return cls(
            name=name,
            label=payload["label"],
            damage=payload["damage"],
            cooldown_ms=payload["cooldown_ms"],
            bullet_speed=payload["bullet_speed"],
            spread_deg=payload["spread_deg"],
            projectiles_per_shot=payload["projectiles_per_shot"],
            max_range=payload["max_range"],
            bullet_radius=payload["bullet_radius"],
            bullet_color=tuple(payload["bullet_color"]),
            sound=payload["sound"],
        )


class Weapon:
    def __init__(self, spec: WeaponSpec):
        self.spec = spec
        self.last_shot_at = -spec.cooldown_ms

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def label(self) -> str:
        return self.spec.label

    @property
    def sound(self) -> str:
        return self.spec.sound

    def can_fire(self, now_ms: int) -> bool:
        return now_ms - self.last_shot_at >= self.spec.cooldown_ms

    def fire(
        self,
        origin: pygame.Vector2,
        target: pygame.Vector2,
        now_ms: int,
    ) -> list[Bullet]:
        if not self.can_fire(now_ms):
            return []
        direction = normalize_or_zero(target - origin)
        if direction.length_squared() == 0:
            return []
        self.last_shot_at = now_ms
        base_angle = math.atan2(direction.y, direction.x)
        shots = self.spec.projectiles_per_shot
        spread = math.radians(self.spec.spread_deg)
        bullets: list[Bullet] = []
        for index in range(shots):
            if shots == 1:
                angle = base_angle
            else:
                ratio = index / (shots - 1)
                offset = (ratio - 0.5) * spread
                angle = base_angle + offset
            velocity = vector_from_angle(angle) * self.spec.bullet_speed
            bullets.append(
                Bullet(
                    position=origin.copy(),
                    velocity=velocity,
                    damage=self.spec.damage,
                    max_range=self.spec.max_range,
                    owner="player",
                    radius=self.spec.bullet_radius,
                    color=self.spec.bullet_color,
                )
            )
        return bullets


def build_weapons(config: dict[str, dict]) -> dict[str, Weapon]:
    return {
        name: Weapon(WeaponSpec.from_dict(name, payload))
        for name, payload in config.items()
    }
