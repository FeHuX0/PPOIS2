import pygame
import pytest

from crimsoland.state_manager import Screen, StateManager


class DummyScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.entered = False
        self.exited = False
        self.events = []
        self.updated = False
        self.rendered = False

    def on_enter(self, **kwargs):
        self.entered = kwargs.get('flag', True)

    def on_exit(self):
        self.exited = True

    def handle_event(self, event):
        self.events.append(event.type)

    def update(self, dt, now_ms):
        self.updated = True

    def render(self, surface):
        self.rendered = True


def test_state_manager_switches_and_delegates():
    manager = StateManager(app=object())
    first = DummyScreen(None)
    second = DummyScreen(None)
    manager.register('first', first)
    manager.register('second', second)
    manager.set_state('first', flag=True)
    assert first.entered is True
    manager.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    manager.update(0.1, 10)
    manager.render(pygame.Surface((20, 20)))
    manager.set_state('second', flag=False)
    assert first.exited is True
    assert second.entered is False
    assert first.events == [pygame.KEYDOWN]
    assert first.updated and first.rendered


def test_state_manager_rejects_unknown_state():
    manager = StateManager(app=object())
    with pytest.raises(KeyError):
        manager.set_state('missing')
