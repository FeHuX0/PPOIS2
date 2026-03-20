from __future__ import annotations

from typing import Final

MENU_OPTIONS: Final = (
    ("Новая игра", "game"),
    ("Таблица рекордов", "scores"),
    ("Справка", "help"),
    ("Выход", "quit"),
)
MENU_SUBTITLE: Final = "Учебный top-down shooter в духе Crimsonland"
MENU_FOOTER: Final = "W/S или стрелки, Enter или пробел"

HELP_TITLE: Final = "Справка"
HELP_BLOCKS: Final = (
    "Выживите на арене, отбиваясь от волн врагов и набирая очки за уничтожение противников.",
    "WASD для движения. Мышь для прицеливания. ЛКМ для стрельбы. 1/2/3 для смены оружия.",
    "Esc возвращает в меню. После каждой волны вы получаете бонус к счету, а сложность постепенно растет.",
    "Если аудио не загрузилось, игра все равно продолжит работать: у проекта есть fallback-режим без звука.",
)
BACK_TO_MENU_HINT: Final = "Esc или Enter: назад в меню"

GAME_READY_BANNER: Final = "Приготовьтесь!"
GAME_VICTORY_BANNER: Final = "Все волны пройдены"

VICTORY_TITLE: Final = "Победа"
GAME_OVER_TITLE: Final = "Игра окончена"
GAME_OVER_MENU_HINT: Final = "Enter или Esc: в меню"
GAME_OVER_SCORES_HINT: Final = "Tab: к таблице рекордов"

FIRST_PLACE_TITLE: Final = "Новый рекорд!"
TOP_SCORE_TITLE: Final = "Вы в топе"
NAME_INPUT_PROMPT: Final = "Введите имя и нажмите Enter"
NAME_INPUT_CANCEL_HINT: Final = "Esc: отмена"

SCORES_TITLE: Final = "Таблица рекордов"
SCORES_EMPTY: Final = "Записей пока нет."


def format_score(score: int) -> str:
    return f"Счет: {score}"


def format_wave(wave: int) -> str:
    return f"Волна: {wave}"


def format_weapon(weapon_label: str) -> str:
    return f"Оружие: {weapon_label}"


def format_wave_banner(wave: int) -> str:
    return f"Волна {wave}"


def format_wave_cleared_banner(wave: int) -> str:
    return f"Волна {wave} очищена"


def build_result_lines(score: int, wave: int) -> tuple[str, str]:
    return format_score(score), format_wave(wave)
