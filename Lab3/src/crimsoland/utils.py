from __future__ import annotations

import math
import random

import pygame


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def normalize_or_zero(vector: pygame.Vector2) -> pygame.Vector2:
    if vector.length_squared() == 0:
        return pygame.Vector2()
    return vector.normalize()


def vector_from_angle(angle_radians: float) -> pygame.Vector2:
    return pygame.Vector2(math.cos(angle_radians), math.sin(angle_radians))


def clamp_vector_to_rect(
    position: pygame.Vector2,
    radius: float,
    rect: pygame.Rect,
) -> pygame.Vector2:
    return pygame.Vector2(
        clamp(position.x, rect.left + radius, rect.right - radius),
        clamp(position.y, rect.top + radius, rect.bottom - radius),
    )


def random_spawn_position(
    arena_rect: pygame.Rect,
    rng: random.Random,
    margin: int,
) -> pygame.Vector2:
    side = rng.choice(("top", "right", "bottom", "left"))
    if side == "top":
        return pygame.Vector2(
            rng.uniform(arena_rect.left, arena_rect.right),
            arena_rect.top + margin,
        )
    if side == "right":
        return pygame.Vector2(
            arena_rect.right - margin,
            rng.uniform(arena_rect.top, arena_rect.bottom),
        )
    if side == "bottom":
        return pygame.Vector2(
            rng.uniform(arena_rect.left, arena_rect.right),
            arena_rect.bottom - margin,
        )
    return pygame.Vector2(
        arena_rect.left + margin,
        rng.uniform(arena_rect.top, arena_rect.bottom),
    )


def wrap_text(font: pygame.font.Font, text: str, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines
