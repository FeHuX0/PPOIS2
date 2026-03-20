import pygame

from crimsoland.events import ENEMY_SPAWN, START_WAVE, WAVE_COMPLETED
from crimsoland.systems.wave_system import WaveSystem


def test_wave_system_posts_start_spawn_and_complete(loaded_configs):
    pygame.event.clear()
    wave_system = WaveSystem(loaded_configs['waves']['waves'][:2], wave_break_ms=100)
    wave_system.start(0)
    wave_system.update(0, 0)
    events = pygame.event.get()
    assert any(event.type == START_WAVE for event in events)
    assert any(event.type == ENEMY_SPAWN for event in events)
    wave_system.update(9999, 0)
    pygame.event.get()
    wave_system.update(10000, 0)
    events = pygame.event.get()
    assert any(event.type == WAVE_COMPLETED for event in events)
    wave_system.update(10150, 0)
    events = pygame.event.get()
    assert any(event.type == START_WAVE and event.wave_number == 2 for event in events)


def test_wave_system_reset_clears_state(loaded_configs):
    wave_system = WaveSystem(loaded_configs['waves']['waves'][:1], wave_break_ms=100)
    wave_system.start(0)
    wave_system.update(0, 0)
    wave_system.reset()
    assert wave_system.current_wave_number == 0
    assert wave_system.spawn_queue == []
    assert not wave_system.started
