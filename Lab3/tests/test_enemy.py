import pygame

from crimsoland.entities.enemy import Enemy


def test_walker_moves_towards_player(loaded_configs):
    enemy = Enemy.from_config('walker', loaded_configs['enemies']['walker'], pygame.Vector2(0, 0))
    enemy.update(1.0, pygame.Vector2(100, 0))
    assert enemy.position.x > 0


def test_shooter_attacks_with_cooldown(loaded_configs):
    enemy = Enemy.from_config('shooter', loaded_configs['enemies']['shooter'], pygame.Vector2(0, 0))
    bullets = enemy.try_attack(pygame.Vector2(100, 0), now_ms=1000)
    assert len(bullets) == 1
    assert enemy.try_attack(pygame.Vector2(100, 0), now_ms=1100) == []


def test_kamikaze_accelerates_near_player(loaded_configs):
    enemy = Enemy.from_config('kamikaze', loaded_configs['enemies']['kamikaze'], pygame.Vector2(0, 0))
    enemy.update(1.0, pygame.Vector2(300, 0))
    far_distance = enemy.position.length()
    enemy.position = pygame.Vector2(0, 0)
    enemy.update(1.0, pygame.Vector2(80, 0))
    near_distance = enemy.position.length()
    assert near_distance > far_distance


def test_enemy_take_damage_returns_death(loaded_configs):
    enemy = Enemy.from_config('runner', loaded_configs['enemies']['runner'], pygame.Vector2(0, 0))
    assert enemy.take_damage(enemy.health)
    assert not enemy.is_alive
