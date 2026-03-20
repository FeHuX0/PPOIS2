import pygame

from crimsoland.entities.player import Player


def test_player_moves_and_clamps(loaded_configs):
    player = Player.from_config(loaded_configs['player'], loaded_configs['weapons'], pygame.Vector2(20, 20))
    arena = pygame.Rect(0, 0, 80, 80)
    player.move(pygame.Vector2(-1, -1), 1.0, arena)
    assert player.position.x >= player.radius
    assert player.position.y >= player.radius


def test_player_switches_weapon_and_takes_damage(loaded_configs):
    player = Player.from_config(loaded_configs['player'], loaded_configs['weapons'], pygame.Vector2(50, 50))
    player.switch_weapon(2)
    assert player.current_weapon.name == 'smg'
    killed = player.take_damage(20, 1000)
    assert not killed
    assert player.hp == player.max_hp - 20
    assert player.take_damage(20, 1100) is False
    assert player.hp == player.max_hp - 20


def test_player_aim_and_shoot(loaded_configs):
    player = Player.from_config(loaded_configs['player'], loaded_configs['weapons'], pygame.Vector2(50, 50))
    player.aim_at(pygame.Vector2(80, 50))
    bullets = player.shoot(pygame.Vector2(80, 50), 1000)
    assert bullets and bullets[0].velocity.x > 0
