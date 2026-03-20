import pygame

from crimsoland.entities.bullet import Bullet
from crimsoland.entities.enemy import Enemy
from crimsoland.entities.player import Player
from crimsoland.systems.animation_system import AnimationSystem
from crimsoland.systems.collision_system import CollisionSystem


def test_player_bullet_kills_enemy_and_spawns_particles(loaded_configs):
    enemy = Enemy.from_config('runner', loaded_configs['enemies']['runner'], pygame.Vector2(20, 20))
    bullet = Bullet(pygame.Vector2(20, 20), pygame.Vector2(0, 0), enemy.health, 10, 'player')
    animation = AnimationSystem()
    enemies = [enemy]
    report = CollisionSystem.resolve_player_bullets([bullet], enemies, animation)
    assert report.kills == 1
    assert report.score_gained == loaded_configs['enemies']['runner']['reward']
    assert enemies == []
    assert len(animation.particles) == 8


def test_enemy_bullet_and_contact_damage_player(loaded_configs):
    player = Player.from_config(loaded_configs['player'], loaded_configs['weapons'], pygame.Vector2(30, 30))
    enemy = Enemy.from_config('walker', loaded_configs['enemies']['walker'], pygame.Vector2(30, 30))
    bullet = Bullet(pygame.Vector2(30, 30), pygame.Vector2(0, 0), 5, 10, 'enemy')
    bullet_report = CollisionSystem.resolve_enemy_bullets([bullet], player, 1000)
    contact_report = CollisionSystem.resolve_enemy_contacts([enemy], player, 2000)
    assert bullet_report.player_hit
    assert contact_report.player_hit
    assert player.hp < player.max_hp
