import runpy

import pygame
import pytest

from crimsoland.entities.bullet import Bullet
from crimsoland.entities.enemy import Enemy
from crimsoland.events import ENEMY_SPAWN, GAME_OVER, PLAYER_DIED, PLAYER_HIT, START_WAVE, WAVE_COMPLETED
from crimsoland.main import main


class PressedKeys:
    def __init__(self, active=None):
        self.active = active or set()

    def __getitem__(self, key):
        return key in self.active


def test_module_entrypoint(monkeypatch):
    import crimsoland.main as main_module

    monkeypatch.setattr(main_module, 'main', lambda: 0)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module('crimsoland.__main__', run_name='__main__')
    assert exc.value.code == 0


def test_main_runs_headless_for_a_few_frames(temp_game_data):
    result = main(
        config_dir=temp_game_data['config_dir'],
        highscores_file=temp_game_data['highscores_file'],
        headless=True,
        max_frames=2,
    )
    assert result == 0


def test_app_handles_quit_event(app):
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    app.run(max_frames=5)
    assert app.running is False


def test_game_screen_update_render_and_events(app, monkeypatch):
    app.change_state('game')
    game = app.state_manager.current_screen
    monkeypatch.setattr(pygame.key, 'get_pressed', lambda: PressedKeys({pygame.K_d}))
    monkeypatch.setattr(pygame.mouse, 'get_pos', lambda: (int(game.player.position.x + 5), int(game.player.position.y)))
    monkeypatch.setattr(pygame.mouse, 'get_pressed', lambda count=3: (1, 0, 0))
    enemy = Enemy.from_config('runner', app.configs['enemies']['runner'], game.player.position.copy())
    game.enemies.append(enemy)
    game.enemy_bullets.append(Bullet(game.player.position.copy(), pygame.Vector2(0, 0), game.player.max_hp, 10, 'enemy'))
    game.update(0.0, 5000)
    game.player_bullets = [Bullet(game.player.position.copy(), pygame.Vector2(0, 0), 1, 10, 'player')]
    game.player_bullets[0].trail = [game.player.position.copy(), game.player.position.copy()]
    game.enemy_bullets = [Bullet(game.player.position.copy(), pygame.Vector2(0, 0), 1, 10, 'enemy')]
    game.enemy_bullets[0].trail = [game.player.position.copy(), game.player.position.copy()]
    game.enemies = [Enemy.from_config('walker', app.configs['enemies']['walker'], pygame.Vector2(100, 100))]
    game.render(app.surface)
    events = pygame.event.get()
    event_types = {event.type for event in events}
    assert PLAYER_HIT in event_types
    assert PLAYER_DIED in event_types
    assert GAME_OVER in event_types


def test_game_screen_custom_events_and_finish_paths(app, monkeypatch):
    app.change_state('game')
    game = app.state_manager.current_screen
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))
    assert game.player.current_weapon.name == 'shotgun'
    game.handle_event(pygame.event.Event(START_WAVE, wave_number=3))
    assert game.current_wave_number == 3
    score_before = game.score
    game.handle_event(pygame.event.Event(WAVE_COMPLETED, wave_number=3, final_wave=False))
    assert game.score == score_before + app.configs['game']['rules']['wave_bonus_score']
    monkeypatch.setattr(app.score_system, 'qualifies', lambda score: False)
    game.finalized = False
    game.handle_event(pygame.event.Event(PLAYER_DIED, score=10, wave=3))
    assert app.state_manager.current_name == 'game_over'
    app.change_state('game')
    game = app.state_manager.current_screen
    monkeypatch.setattr(app.score_system, 'qualifies', lambda score: True)
    game.score = 2001
    game.finish_game(victory=False)
    game.finish_game(victory=False)
    assert app.state_manager.current_name == 'name_input'
    app.change_state('game')
    game = app.state_manager.current_screen
    game.score = 2001
    game.handle_event(pygame.event.Event(WAVE_COMPLETED, wave_number=20, final_wave=True))
    assert app.state_manager.current_name == 'name_input'
