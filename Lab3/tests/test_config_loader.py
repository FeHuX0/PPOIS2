import json

import pytest

from crimsoland.config_loader import ConfigError, ConfigLoader


def test_load_all_configs(loaded_configs):
    assert set(loaded_configs) == {'game', 'player', 'weapons', 'enemies', 'waves', 'audio'}
    assert len(loaded_configs['waves']['waves']) >= 20
    assert len(loaded_configs['weapons']) >= 3
    assert len(loaded_configs['enemies']) >= 5
    assert loaded_configs['player']['start_weapon'] in loaded_configs['weapons']


def test_invalid_player_weapon_raises(temp_game_data):
    player_path = temp_game_data['config_dir'] / 'player.json'
    payload = json.loads(player_path.read_text(encoding='utf-8'))
    payload['start_weapon'] = 'laser'
    player_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    loader = ConfigLoader(temp_game_data['config_dir'])
    with pytest.raises(ConfigError):
        loader.load_all()


def test_missing_config_raises(tmp_path):
    loader = ConfigLoader(tmp_path)
    with pytest.raises(ConfigError):
        loader.load_all()


def test_invalid_json_and_validation_helpers(temp_game_data):
    loader = ConfigLoader(temp_game_data['config_dir'])
    broken = temp_game_data['config_dir'] / 'game.json'
    broken.write_text('{oops', encoding='utf-8')
    with pytest.raises(ConfigError):
        loader.load_json('game.json')
    broken.write_text('[]', encoding='utf-8')
    with pytest.raises(ConfigError):
        loader.load_json('game.json')
    with pytest.raises(ConfigError):
        loader._require_key({}, 'x', 'section')
    with pytest.raises(ConfigError):
        loader._require_positive_number({'x': 0}, 'x', 'section')
    with pytest.raises(ConfigError):
        loader._require_non_negative_number({'x': -1}, 'x', 'section')
    with pytest.raises(ConfigError):
        loader._validate_color([1, 2], 'color')
    with pytest.raises(ConfigError):
        loader._validate_color([1, 2, 999], 'color')
    with pytest.raises(ConfigError):
        loader._validate_weapons({})
    with pytest.raises(ConfigError):
        loader._validate_enemies({})
    with pytest.raises(ConfigError):
        loader._validate_waves({'waves': []}, {})
    with pytest.raises(ConfigError):
        loader._validate_waves({'waves': [{'number': 2, 'entries': [{'enemy': 'walker', 'count': 1, 'interval_ms': 1, 'start_delay_ms': 0}]}] * 20}, {'walker': {}})
    with pytest.raises(ConfigError):
        loader._validate_waves({'waves': [{'number': 1, 'entries': []}] + [{'number': index, 'entries': [{'enemy': 'walker', 'count': 1, 'interval_ms': 1, 'start_delay_ms': 0}]} for index in range(2, 21)]}, {'walker': {}})
