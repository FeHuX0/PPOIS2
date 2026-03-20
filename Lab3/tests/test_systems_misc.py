import random
from pathlib import Path

import pygame

from crimsoland.resource_manager import NullSound, ResourceManager
from crimsoland.systems.animation_system import AnimationSystem
from crimsoland.systems.audio_system import AudioSystem
from crimsoland.utils import clamp, clamp_vector_to_rect, normalize_or_zero, random_spawn_position, vector_from_angle, wrap_text


class FixedRng:
    def __init__(self, side):
        self.side = side

    def choice(self, _values):
        return self.side

    def uniform(self, left, right):
        return (left + right) / 2


def test_resource_and_audio_systems(loaded_configs, temp_game_data, monkeypatch, tmp_path: Path):
    manager = ResourceManager(temp_game_data['data_dir'] / 'assets')
    font = manager.load_font(18)
    null_sound = manager.load_sound(None)
    null_sound.play()
    null_sound.set_volume(0.2)
    sound_path = tmp_path / 'dummy.wav'
    sound_path.write_bytes(b'0')
    monkeypatch.setattr(manager, 'ensure_mixer', lambda: False)
    sound = manager.load_sound(sound_path)
    assert font is manager.load_font(18)
    assert isinstance(null_sound, NullSound)
    assert isinstance(sound, NullSound)
    assert sound is manager.load_sound(sound_path)
    manager2 = ResourceManager()
    monkeypatch.setattr(manager2, 'ensure_mixer', lambda: True)
    monkeypatch.setattr(pygame.mixer, 'Sound', lambda _path: (_ for _ in ()).throw(pygame.error('fail')))
    assert isinstance(manager2.load_sound(sound_path), NullSound)
    disabled_audio = AudioSystem(loaded_configs['audio'], manager, enabled=False)
    disabled_audio.play_sound('pistol')
    disabled_audio.play_music('menu')
    music_config = {
        'music': {'menu': str(sound_path)},
        'sounds': {'x': str(sound_path)},
        'music_volume': 0.1,
        'sfx_volume': 0.1,
    }
    audio = AudioSystem(music_config, manager2, enabled=True)
    monkeypatch.setattr(pygame.mixer.music, 'load', lambda _path: (_ for _ in ()).throw(pygame.error('fail')))
    audio.play_music('menu')
    audio.play_sound('x')
    audio.stop_music()


def test_animation_and_utils():
    animation = AnimationSystem(random.Random(1))
    animation.spawn_enemy_death(pygame.Vector2(10, 10), (255, 0, 0))
    surface = pygame.Surface((40, 40))
    animation.update(100)
    animation.draw(surface)
    assert len(animation.particles) <= 8
    assert clamp(10, 0, 5) == 5
    assert normalize_or_zero(pygame.Vector2()) == pygame.Vector2()
    clamped = clamp_vector_to_rect(pygame.Vector2(-5, 200), 10, pygame.Rect(0, 0, 100, 100))
    assert clamped == pygame.Vector2(10, 90)
    for side in ('top', 'right', 'bottom', 'left'):
        spawn = random_spawn_position(pygame.Rect(0, 0, 100, 100), FixedRng(side), 10)
        assert 0 <= spawn.x <= 100 and 0 <= spawn.y <= 100
    vector = vector_from_angle(0)
    assert round(vector.x, 3) == 1.0
    font = pygame.font.SysFont(None, 20)
    assert wrap_text(font, '', 40) == ['']
    lines = wrap_text(font, 'one two three four', 40)
    assert len(lines) >= 2
