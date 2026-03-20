
from __future__ import annotations

import json
from pathlib import Path


class ConfigError(ValueError):
    """Raised when a configuration file is missing or invalid."""


class ConfigLoader:
    CONFIG_FILES = {
        "game": "game.json",
        "player": "player.json",
        "weapons": "weapons.json",
        "enemies": "enemies.json",
        "waves": "waves.json",
        "audio": "audio.json",
    }

    def __init__(self, config_dir: str | Path):
        self.config_dir = Path(config_dir)

    def load_json(self, filename: str) -> dict:
        path = self.config_dir / filename
        try:
            raw = path.read_text(encoding="utf-8-sig")
        except FileNotFoundError as error:
            raise ConfigError(f"Не найден файл конфигурации: {path}") from error
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ConfigError(f"Некорректный JSON в файле {path}") from error
        if not isinstance(data, dict):
            raise ConfigError(f"Корневой JSON в {path} должен быть объектом.")
        return data

    def load_all(self) -> dict[str, dict]:
        payload = {
            name: self.load_json(filename)
            for name, filename in self.CONFIG_FILES.items()
        }
        self.validate_all(payload)
        return payload

    def validate_all(self, payload: dict[str, dict]) -> None:
        self._validate_game(payload["game"])
        self._validate_player(payload["player"], payload["weapons"])
        self._validate_weapons(payload["weapons"])
        self._validate_enemies(payload["enemies"])
        self._validate_waves(payload["waves"], payload["enemies"])
        self._validate_audio(payload["audio"])

    def _validate_game(self, config: dict) -> None:
        for key in ("title", "window", "arena", "ui", "rules", "highscores"):
            self._require_key(config, key, "game")
        for key in ("width", "height", "fps"):
            self._require_positive_number(config["window"], key, "game.window")
        for key in ("width", "height", "spawn_margin"):
            self._require_positive_number(config["arena"], key, "game.arena")
        self._require_positive_number(config["rules"], "wave_break_ms", "game.rules")
        self._require_non_negative_number(config["rules"], "wave_bonus_score", "game.rules")
        self._require_positive_number(config["highscores"], "limit", "game.highscores")
        self._require_positive_number(
            config["highscores"], "name_max_length", "game.highscores"
        )

    def _validate_player(self, config: dict, weapons: dict) -> None:
        for key in ("radius", "max_hp", "speed", "color", "invulnerability_ms", "start_weapon"):
            self._require_key(config, key, "player")
        for key in ("radius", "max_hp", "speed", "invulnerability_ms"):
            self._require_positive_number(config, key, "player")
        self._validate_color(config["color"], "player.color")
        if config["start_weapon"] not in weapons:
            raise ConfigError("player.start_weapon должен ссылаться на оружие из weapons.json")

    def _validate_weapons(self, config: dict) -> None:
        if len(config) < 3:
            raise ConfigError("В weapons.json должно быть минимум 3 типа оружия.")
        for name, weapon in config.items():
            for key in (
                "label",
                "damage",
                "cooldown_ms",
                "bullet_speed",
                "spread_deg",
                "projectiles_per_shot",
                "max_range",
                "bullet_radius",
                "bullet_color",
                "sound",
            ):
                self._require_key(weapon, key, f"weapon:{name}")
            for key in (
                "damage",
                "cooldown_ms",
                "bullet_speed",
                "projectiles_per_shot",
                "max_range",
                "bullet_radius",
            ):
                self._require_positive_number(weapon, key, f"weapon:{name}")
            self._validate_color(weapon["bullet_color"], f"weapon:{name}.bullet_color")

    def _validate_enemies(self, config: dict) -> None:
        if len(config) < 5:
            raise ConfigError("В enemies.json должно быть минимум 5 типов противников.")
        for name, enemy in config.items():
            for key in (
                "label",
                "behavior",
                "radius",
                "health",
                "speed",
                "damage",
                "reward",
                "attack_range",
                "attack_cooldown_ms",
                "contact_cooldown_ms",
                "projectile_speed",
                "projectile_damage",
                "color",
            ):
                self._require_key(enemy, key, f"enemy:{name}")
            for key in (
                "radius",
                "health",
                "speed",
                "damage",
                "reward",
                "attack_range",
                "attack_cooldown_ms",
                "contact_cooldown_ms",
                "projectile_speed",
                "projectile_damage",
            ):
                self._require_non_negative_number(enemy, key, f"enemy:{name}")
            self._validate_color(enemy["color"], f"enemy:{name}.color")

    def _validate_waves(self, config: dict, enemies: dict) -> None:
        self._require_key(config, "waves", "waves")
        waves = config["waves"]
        if not isinstance(waves, list) or len(waves) < 20:
            raise ConfigError("В waves.json должно быть не меньше 20 волн.")
        expected_number = 1
        for wave in waves:
            if wave.get("number") != expected_number:
                raise ConfigError("Номера волн должны идти подряд, начиная с 1.")
            expected_number += 1
            entries = wave.get("entries")
            if not isinstance(entries, list) or not entries:
                raise ConfigError("Каждая волна должна содержать непустой список entries.")
            for entry in entries:
                for key in ("enemy", "count", "interval_ms", "start_delay_ms"):
                    self._require_key(entry, key, f"wave:{wave['number']}")
                if entry["enemy"] not in enemies:
                    raise ConfigError(
                        f"Волна {wave['number']} ссылается на неизвестного врага {entry['enemy']}."
                    )
                for key in ("count", "interval_ms", "start_delay_ms"):
                    self._require_non_negative_number(entry, key, f"wave:{wave['number']}")

    def _validate_audio(self, config: dict) -> None:
        for key in ("music", "sounds", "music_volume", "sfx_volume"):
            self._require_key(config, key, "audio")
        self._require_non_negative_number(config, "music_volume", "audio")
        self._require_non_negative_number(config, "sfx_volume", "audio")

    @staticmethod
    def _require_key(config: dict, key: str, section: str) -> None:
        if key not in config:
            raise ConfigError(f"Отсутствует ключ {key!r} в секции {section}.")

    @staticmethod
    def _require_positive_number(config: dict, key: str, section: str) -> None:
        value = config.get(key)
        if not isinstance(value, (int, float)) or value <= 0:
            raise ConfigError(f"Поле {section}.{key} должно быть положительным числом.")

    @staticmethod
    def _require_non_negative_number(config: dict, key: str, section: str) -> None:
        value = config.get(key)
        if not isinstance(value, (int, float)) or value < 0:
            raise ConfigError(f"Поле {section}.{key} должно быть неотрицательным числом.")

    @staticmethod
    def _validate_color(value: object, section: str) -> None:
        if not isinstance(value, list) or len(value) != 3:
            raise ConfigError(f"Поле {section} должно быть RGB-массивом из 3 чисел.")
        if not all(isinstance(channel, int) and 0 <= channel <= 255 for channel in value):
            raise ConfigError(f"Поле {section} должно содержать только RGB-значения 0..255.")
