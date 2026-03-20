from __future__ import annotations

import math

import pygame

from crimsoland.entities.bullet import Bullet
from crimsoland.utils import normalize_or_zero


class Enemy:
    def __init__(
        self,
        enemy_type: str,
        label: str,
        behavior: str,
        position: pygame.Vector2,
        radius: int,
        health: int,
        speed: float,
        damage: int,
        reward: int,
        attack_range: float,
        attack_cooldown_ms: int,
        contact_cooldown_ms: int,
        projectile_speed: float,
        projectile_damage: int,
        color: tuple[int, int, int],
    ):
        self.enemy_type = enemy_type
        self.label = label
        self.behavior = behavior
        self.position = position
        self.radius = radius
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.reward = reward
        self.attack_range = attack_range
        self.attack_cooldown_ms = attack_cooldown_ms
        self.contact_cooldown_ms = contact_cooldown_ms
        self.projectile_speed = projectile_speed
        self.projectile_damage = projectile_damage
        self.color = color
        self.last_attack_at = -attack_cooldown_ms
        self.last_contact_at = -contact_cooldown_ms

    @classmethod
    def from_config(
        cls,
        enemy_type: str,
        config: dict,
        position: pygame.Vector2,
    ) -> "Enemy":
        return cls(
            enemy_type=enemy_type,
            label=config["label"],
            behavior=config["behavior"],
            position=position,
            radius=config["radius"],
            health=config["health"],
            speed=config["speed"],
            damage=config["damage"],
            reward=config["reward"],
            attack_range=config["attack_range"],
            attack_cooldown_ms=config["attack_cooldown_ms"],
            contact_cooldown_ms=config["contact_cooldown_ms"],
            projectile_speed=config["projectile_speed"],
            projectile_damage=config["projectile_damage"],
            color=tuple(config["color"]),
        )

    @property
    def is_alive(self) -> bool:
        return self.health > 0

    def update(self, dt: float, player_position: pygame.Vector2) -> None:
        offset = player_position - self.position
        distance = offset.length()
        direction = normalize_or_zero(offset)
        if self.behavior == "shooter":
            desired = self.attack_range * 0.8
            if distance > desired:
                move = direction
            elif distance < desired * 0.55:
                move = -direction
            else:
                move = pygame.Vector2(-direction.y, direction.x)
            self.position += move * self.speed * dt
            return
        speed_multiplier = 1.0
        if self.behavior == "kamikaze" and distance <= self.attack_range:
            speed_multiplier = 1.8
        self.position += direction * self.speed * speed_multiplier * dt

    def try_attack(self, player_position: pygame.Vector2, now_ms: int) -> list[Bullet]:
        if self.behavior != "shooter":
            return []
        if now_ms - self.last_attack_at < self.attack_cooldown_ms:
            return []
        direction = normalize_or_zero(player_position - self.position)
        if direction.length_squared() == 0:
            return []
        distance = (player_position - self.position).length()
        if distance > self.attack_range:
            return []
        self.last_attack_at = now_ms
        angle = math.atan2(direction.y, direction.x)
        velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.projectile_speed
        return [
            Bullet(
                position=self.position.copy(),
                velocity=velocity,
                damage=self.projectile_damage,
                max_range=max(self.attack_range * 1.4, 120),
                owner="enemy",
                radius=4,
                color=(255, 120, 120),
            )
        ]

    def can_contact_damage(self, now_ms: int) -> bool:
        return now_ms - self.last_contact_at >= self.contact_cooldown_ms

    def mark_contact(self, now_ms: int) -> None:
        self.last_contact_at = now_ms

    def take_damage(self, amount: int) -> bool:
        self.health = max(0, self.health - amount)
        return self.health == 0

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        bar_width = self.radius * 2
        health_ratio = self.health / self.max_health if self.max_health else 0
        bar_rect = pygame.Rect(
            int(self.position.x - self.radius),
            int(self.position.y - self.radius - 8),
            bar_width,
            4,
        )
        pygame.draw.rect(surface, (50, 20, 20), bar_rect)
        if health_ratio > 0:
            pygame.draw.rect(
                surface,
                (120, 235, 120),
                (bar_rect.x, bar_rect.y, int(bar_rect.width * health_ratio), bar_rect.height),
            )
