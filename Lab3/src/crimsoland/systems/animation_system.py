from __future__ import annotations

import random
from dataclasses import dataclass

import pygame


@dataclass(slots=True)
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple[int, int, int]
    size: int
    age_ms: int = 0
    lifetime_ms: int = 320


class AnimationSystem:
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.particles: list[Particle] = []

    def spawn_enemy_death(
        self,
        position: pygame.Vector2,
        color: tuple[int, int, int],
    ) -> None:
        for _ in range(8):
            velocity = pygame.Vector2(
                self.rng.uniform(-120, 120),
                self.rng.uniform(-120, 120),
            )
            self.particles.append(
                Particle(
                    position=position.copy(),
                    velocity=velocity,
                    color=color,
                    size=self.rng.randint(2, 5),
                )
            )

    def update(self, dt_ms: int) -> None:
        alive_particles: list[Particle] = []
        for particle in self.particles:
            particle.age_ms += dt_ms
            if particle.age_ms >= particle.lifetime_ms:
                continue
            particle.position += particle.velocity * (dt_ms / 1000)
            alive_particles.append(particle)
        self.particles = alive_particles

    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            alpha_ratio = 1 - (particle.age_ms / particle.lifetime_ms)
            color = tuple(
                max(0, min(255, int(channel * alpha_ratio)))
                for channel in particle.color
            )
            pygame.draw.circle(surface, color, particle.position, particle.size)
