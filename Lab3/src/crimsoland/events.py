from __future__ import annotations

import pygame


START_WAVE = pygame.USEREVENT + 1
ENEMY_SPAWN = pygame.USEREVENT + 2
PLAYER_HIT = pygame.USEREVENT + 3
PLAYER_DIED = pygame.USEREVENT + 4
WAVE_COMPLETED = pygame.USEREVENT + 5
GAME_OVER = pygame.USEREVENT + 6


def post_event(event_type: int, **payload: object) -> None:
    pygame.event.post(pygame.event.Event(event_type, payload))
