from __future__ import annotations

import random

import pygame

from crimsoland.entities.enemy import Enemy
from crimsoland.entities.player import Player
from crimsoland.events import (
    ENEMY_SPAWN,
    GAME_OVER,
    PLAYER_DIED,
    PLAYER_HIT,
    START_WAVE,
    WAVE_COMPLETED,
    post_event,
)
from crimsoland.state_manager import Screen
from crimsoland.systems.animation_system import AnimationSystem
from crimsoland.systems.collision_system import CollisionSystem
from crimsoland.systems.combat_system import CombatSystem
from crimsoland.systems.wave_system import WaveSystem
from crimsoland.ui_text import (
    GAME_READY_BANNER,
    GAME_VICTORY_BANNER,
    format_score,
    format_wave,
    format_wave_banner,
    format_wave_cleared_banner,
    format_weapon,
)
from crimsoland.utils import random_spawn_position


class GameScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        ui = app.configs["game"]["ui"]
        self.font = app.resource_manager.load_font(ui.get("font_size", 28), ui.get("font_name"))
        self.small_font = app.resource_manager.load_font(ui.get("small_font_size", 20), ui.get("font_name"))
        self.rng = random.Random(42)
        self.reset_session(0)

    def reset_session(self, now_ms: int) -> None:
        game_cfg = self.app.configs["game"]
        arena_cfg = game_cfg["arena"]
        self.arena_rect = pygame.Rect(0, 0, arena_cfg["width"], arena_cfg["height"])
        center = pygame.Vector2(self.arena_rect.center)
        self.player = Player.from_config(
            self.app.configs["player"],
            self.app.configs["weapons"],
            center,
        )
        self.enemies: list[Enemy] = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.animation_system = AnimationSystem(random.Random(7))
        self.wave_system = WaveSystem(
            self.app.configs["waves"]["waves"],
            wave_break_ms=game_cfg["rules"]["wave_break_ms"],
            rng=self.rng,
        )
        self.wave_system.start(now_ms)
        self.current_wave_number = 0
        self.score = 0
        self.kills = 0
        self.finalized = False
        self.banner_text = GAME_READY_BANNER
        self.banner_until = now_ms + 900

    def on_enter(self, **kwargs) -> None:
        now_ms = pygame.time.get_ticks()
        self.reset_session(now_ms)
        self.app.audio_system.play_music("game")

    def on_exit(self) -> None:
        self.app.audio_system.stop_music()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.change_state("menu")
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.player.switch_weapon(event.key - pygame.K_1)
        elif event.type == START_WAVE:
            self.current_wave_number = int(event.wave_number)
            self.banner_text = format_wave_banner(self.current_wave_number)
            self.banner_until = pygame.time.get_ticks() + 1000
        elif event.type == ENEMY_SPAWN:
            self._spawn_enemy(event.enemy_type)
        elif event.type == WAVE_COMPLETED:
            bonus = self.app.configs["game"]["rules"]["wave_bonus_score"]
            self.score += bonus
            if bool(event.final_wave):
                self.banner_text = GAME_VICTORY_BANNER
                self.banner_until = pygame.time.get_ticks() + 1000
                self.finish_game(victory=True)
            else:
                self.banner_text = format_wave_cleared_banner(int(event.wave_number))
                self.banner_until = pygame.time.get_ticks() + 1000
        elif event.type in (PLAYER_DIED, GAME_OVER):
            self.finish_game(victory=False)

    def _spawn_enemy(self, enemy_type: str) -> None:
        config = self.app.configs["enemies"][enemy_type]
        spawn_position = random_spawn_position(
            self.arena_rect,
            self.rng,
            self.app.configs["game"]["arena"]["spawn_margin"],
        )
        self.enemies.append(Enemy.from_config(enemy_type, config, spawn_position))

    def update(self, dt: float, now_ms: int) -> None:
        if self.finalized:
            return
        movement = self._read_movement()
        mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        self.player.move(movement, dt, self.arena_rect)
        self.player.aim_at(mouse_position)
        if pygame.mouse.get_pressed(3)[0]:
            self.player_bullets.extend(
                CombatSystem.player_attack(
                    self.player,
                    mouse_position,
                    now_ms,
                    self.app.audio_system,
                )
            )
        self.wave_system.update(now_ms, len(self.enemies))
        for enemy in self.enemies:
            enemy.update(dt, self.player.position)
            self.enemy_bullets.extend(
                CombatSystem.enemy_attack(
                    enemy,
                    self.player.position,
                    now_ms,
                    self.app.audio_system,
                )
            )
        for bullet in self.player_bullets + self.enemy_bullets:
            bullet.update(dt)
        player_report = CollisionSystem.resolve_player_bullets(
            self.player_bullets,
            self.enemies,
            self.animation_system,
        )
        enemy_report = CollisionSystem.resolve_enemy_bullets(
            self.enemy_bullets,
            self.player,
            now_ms,
        )
        contact_report = CollisionSystem.resolve_enemy_contacts(
            self.enemies,
            self.player,
            now_ms,
        )
        self.score += player_report.score_gained
        self.kills += player_report.kills
        if enemy_report.player_hit or contact_report.player_hit:
            post_event(PLAYER_HIT, hp=self.player.hp)
        if enemy_report.player_died or contact_report.player_died:
            post_event(PLAYER_DIED, score=self.score, wave=self.current_wave_number)
            post_event(GAME_OVER, score=self.score, wave=self.current_wave_number)
        self.player_bullets = [bullet for bullet in self.player_bullets if bullet.alive]
        self.enemy_bullets = [bullet for bullet in self.enemy_bullets if bullet.alive]
        self.animation_system.update(int(dt * 1000))

    def finish_game(self, victory: bool) -> None:
        if self.finalized:
            return
        self.finalized = True
        payload = {
            "score": self.score,
            "wave": self.current_wave_number,
            "victory": victory,
        }
        if self.app.score_system.qualifies(self.score):
            self.app.change_state(
                "name_input",
                is_first_place=self.app.score_system.is_first_place(self.score),
                **payload,
            )
        else:
            self.app.change_state("game_over", **payload)

    def _read_movement(self) -> pygame.Vector2:
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2()
        if keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_s]:
            movement.y += 1
        if keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_d]:
            movement.x += 1
        return movement

    def render(self, surface: pygame.Surface) -> None:
        ui = self.app.configs["game"]["ui"]
        surface.fill(tuple(ui["background_color"]))
        self._draw_grid(surface, tuple(ui["grid_color"]))
        for bullet in self.player_bullets:
            bullet.draw(surface)
        for bullet in self.enemy_bullets:
            bullet.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        self.player.draw(surface)
        self.animation_system.draw(surface)
        self._draw_hud(surface)
        if pygame.time.get_ticks() < self.banner_until:
            banner = self.font.render(self.banner_text, True, tuple(ui["accent_color"]))
            surface.blit(banner, banner.get_rect(center=(surface.get_width() // 2, 32)))

    def _draw_grid(self, surface: pygame.Surface, color: tuple[int, int, int]) -> None:
        step = 40
        for x in range(0, surface.get_width(), step):
            pygame.draw.line(surface, color, (x, 0), (x, surface.get_height()), 1)
        for y in range(0, surface.get_height(), step):
            pygame.draw.line(surface, color, (0, y), (surface.get_width(), y), 1)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        ui = self.app.configs["game"]["ui"]
        text_color = tuple(ui["text_color"])
        accent = tuple(ui["accent_color"])
        hp_text = self.small_font.render(
            f"HP: {self.player.hp}/{self.player.max_hp}",
            True,
            tuple(ui["player_hud_color"]),
        )
        score_text = self.small_font.render(format_score(self.score), True, text_color)
        wave_text = self.small_font.render(format_wave(self.current_wave_number), True, text_color)
        weapon_text = self.small_font.render(
            format_weapon(self.player.current_weapon.label),
            True,
            accent,
        )
        surface.blit(hp_text, (18, surface.get_height() - 92))
        surface.blit(score_text, (18, surface.get_height() - 68))
        surface.blit(wave_text, (18, surface.get_height() - 44))
        surface.blit(weapon_text, (18, surface.get_height() - 20))
