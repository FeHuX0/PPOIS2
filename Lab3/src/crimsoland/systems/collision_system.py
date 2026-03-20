from __future__ import annotations

from dataclasses import dataclass

import pygame

from crimsoland.entities.bullet import Bullet
from crimsoland.entities.enemy import Enemy
from crimsoland.entities.player import Player
from crimsoland.systems.animation_system import AnimationSystem


@dataclass(slots=True)
class CollisionReport:
    score_gained: int = 0
    kills: int = 0
    player_hit: bool = False
    player_died: bool = False


class CollisionSystem:
    @staticmethod
    def resolve_player_bullets(
        bullets: list[Bullet],
        enemies: list[Enemy],
        animation_system: AnimationSystem,
    ) -> CollisionReport:
        report = CollisionReport()
        for bullet in bullets:
            if not bullet.alive:
                continue
            for enemy in list(enemies):
                if not enemy.is_alive:
                    continue
                if CollisionSystem._circle_hit(
                    bullet.position,
                    bullet.radius,
                    enemy.position,
                    enemy.radius,
                ):
                    bullet.alive = False
                    died = enemy.take_damage(bullet.damage)
                    if died:
                        enemies.remove(enemy)
                        report.score_gained += enemy.reward
                        report.kills += 1
                        animation_system.spawn_enemy_death(enemy.position, enemy.color)
                    break
        return report

    @staticmethod
    def resolve_enemy_bullets(
        bullets: list[Bullet],
        player: Player,
        now_ms: int,
    ) -> CollisionReport:
        report = CollisionReport()
        for bullet in bullets:
            if not bullet.alive:
                continue
            if CollisionSystem._circle_hit(
                bullet.position,
                bullet.radius,
                player.position,
                player.radius,
            ):
                bullet.alive = False
                died = player.take_damage(bullet.damage, now_ms)
                report.player_hit = True
                report.player_died = died
        return report

    @staticmethod
    def resolve_enemy_contacts(
        enemies: list[Enemy],
        player: Player,
        now_ms: int,
    ) -> CollisionReport:
        report = CollisionReport()
        for enemy in enemies:
            if not enemy.can_contact_damage(now_ms):
                continue
            if CollisionSystem._circle_hit(
                enemy.position,
                enemy.radius,
                player.position,
                player.radius,
            ):
                enemy.mark_contact(now_ms)
                died = player.take_damage(enemy.damage, now_ms)
                report.player_hit = True
                report.player_died = report.player_died or died
        return report

    @staticmethod
    def _circle_hit(
        a_pos: pygame.Vector2,
        a_radius: float,
        b_pos: pygame.Vector2,
        b_radius: float,
    ) -> bool:
        return a_pos.distance_to(b_pos) <= a_radius + b_radius
