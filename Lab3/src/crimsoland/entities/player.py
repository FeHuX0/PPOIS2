from __future__ import annotations

import pygame

from crimsoland.entities.weapon import Weapon, build_weapons
from crimsoland.utils import clamp_vector_to_rect, normalize_or_zero


class Player:
    def __init__(
        self,
        position: pygame.Vector2,
        radius: int,
        max_hp: int,
        speed: float,
        color: tuple[int, int, int],
        invulnerability_ms: int,
        weapons: dict[str, Weapon],
        start_weapon: str,
    ):
        self.position = position
        self.radius = radius
        self.max_hp = max_hp
        self.hp = max_hp
        self.speed = speed
        self.color = color
        self.invulnerability_ms = invulnerability_ms
        self.weapons = weapons
        self.weapon_order = list(weapons.keys())
        self.current_weapon_index = self.weapon_order.index(start_weapon)
        self.last_hit_at = -invulnerability_ms
        self.aim_direction = pygame.Vector2(1, 0)

    @classmethod
    def from_config(
        cls,
        config: dict,
        weapons_config: dict[str, dict],
        position: pygame.Vector2,
    ) -> "Player":
        weapons = build_weapons(weapons_config)
        return cls(
            position=position,
            radius=config["radius"],
            max_hp=config["max_hp"],
            speed=config["speed"],
            color=tuple(config["color"]),
            invulnerability_ms=config["invulnerability_ms"],
            weapons=weapons,
            start_weapon=config["start_weapon"],
        )

    @property
    def current_weapon(self) -> Weapon:
        return self.weapons[self.weapon_order[self.current_weapon_index]]

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def switch_weapon(self, slot_index: int) -> None:
        if 0 <= slot_index < len(self.weapon_order):
            self.current_weapon_index = slot_index

    def move(self, movement: pygame.Vector2, dt: float, arena_rect: pygame.Rect) -> None:
        direction = normalize_or_zero(movement)
        self.position += direction * self.speed * dt
        self.position = clamp_vector_to_rect(self.position, self.radius, arena_rect)

    def aim_at(self, target: pygame.Vector2) -> None:
        direction = normalize_or_zero(target - self.position)
        if direction.length_squared() > 0:
            self.aim_direction = direction

    def shoot(self, target: pygame.Vector2, now_ms: int):
        return self.current_weapon.fire(self.position, target, now_ms)

    def take_damage(self, amount: int, now_ms: int) -> bool:
        if now_ms - self.last_hit_at < self.invulnerability_ms:
            return False
        self.last_hit_at = now_ms
        self.hp = max(0, self.hp - amount)
        return self.hp == 0

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        muzzle = self.position + self.aim_direction * (self.radius + 6)
        pygame.draw.line(surface, (240, 240, 245), self.position, muzzle, 3)
