import pygame

from crimsoland.entities.weapon import Weapon, WeaponSpec, build_weapons
from crimsoland.systems.combat_system import CombatSystem


def test_weapon_fire_and_cooldown(loaded_configs):
    weapons = build_weapons(loaded_configs['weapons'])
    pistol = weapons['pistol']
    origin = pygame.Vector2(10, 10)
    target = pygame.Vector2(50, 10)
    bullets = pistol.fire(origin, target, now_ms=1000)
    assert len(bullets) == 1
    assert bullets[0].owner == 'player'
    assert pistol.fire(origin, target, now_ms=1100) == []


def test_shotgun_creates_spread(loaded_configs):
    shotgun = build_weapons(loaded_configs['weapons'])['shotgun']
    bullets = shotgun.fire(pygame.Vector2(0, 0), pygame.Vector2(100, 0), now_ms=1000)
    assert len(bullets) == loaded_configs['weapons']['shotgun']['projectiles_per_shot']
    unique_y = {round(bullet.velocity.y, 3) for bullet in bullets}
    assert len(unique_y) > 1


def test_combat_system_player_attack_uses_player_weapon(loaded_configs):
    weapons = build_weapons(loaded_configs['weapons'])
    class DummyPlayer:
        current_weapon = weapons['smg']
        def shoot(self, target, now_ms):
            return self.current_weapon.fire(pygame.Vector2(0, 0), target, now_ms)
    bullets = CombatSystem.player_attack(DummyPlayer(), pygame.Vector2(20, 0), 1000)
    assert bullets
