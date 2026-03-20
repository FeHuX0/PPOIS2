from __future__ import annotations

from dataclasses import dataclass, field

import pygame


@dataclass(slots=True)
class Bullet:
    position: pygame.Vector2
    velocity: pygame.Vector2
    damage: int
    max_range: float
    owner: str
    radius: int = 4
    color: tuple[int, int, int] = (255, 220, 110)
    distance_travelled: float = 0.0
    alive: bool = True
    trail: list[pygame.Vector2] = field(default_factory=list)

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        step = self.velocity * dt
        self.position += step
        self.distance_travelled += step.length()
        self.trail.append(self.position.copy())
        if len(self.trail) > 4:
            self.trail.pop(0)
        if self.distance_travelled >= self.max_range:
            self.alive = False

    def rect(self) -> pygame.Rect:
        diameter = self.radius * 2
        return pygame.Rect(
            int(self.position.x - self.radius),
            int(self.position.y - self.radius),
            diameter,
            diameter,
        )

    def draw(self, surface: pygame.Surface) -> None:
        if len(self.trail) >= 2:
            pygame.draw.lines(surface, self.color, False, self.trail, 2)
        pygame.draw.circle(surface, self.color, self.position, self.radius)
