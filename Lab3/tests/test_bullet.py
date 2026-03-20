import pygame

from crimsoland.entities.bullet import Bullet


def test_bullet_update_rect_and_draw():
    bullet = Bullet(pygame.Vector2(5, 5), pygame.Vector2(10, 0), 5, 100, 'player')
    bullet.update(0.5)
    bullet.update(0.5)
    rect = bullet.rect()
    assert rect.width == bullet.radius * 2
    surface = pygame.Surface((50, 50))
    bullet.draw(surface)
    assert len(bullet.trail) >= 2


def test_bullet_stops_after_max_range_and_ignores_future_updates():
    bullet = Bullet(pygame.Vector2(0, 0), pygame.Vector2(10, 0), 5, 5, 'player')
    bullet.update(1.0)
    assert bullet.alive is False
    previous = bullet.position.copy()
    bullet.update(1.0)
    assert bullet.position == previous
