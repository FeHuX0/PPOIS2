# Crimsoland

`Crimsoland` - учебный 2D `top-down shooter` на `pygame`, вдохновленный `Crimsonland`. Проект построен вокруг волн врагов, нескольких типов оружия, таблицы рекордов и набора конфигураций в JSON.

## Требования

- Python 3.11+
- `uv`
- `pygame`
- `pytest`
- `pytest-cov`

## Установка зависимостей

```bash
uv sync --dev
```

## Запуск игры

```bash
uv run python -m crimsoland
```

Или через script entry point:

```bash
uv run crimsoland
```

## Запуск тестов

```bash
uv run pytest
```

## Проверка покрытия

```bash
uv run pytest --cov
```

Минимальный порог покрытия настроен в `pyproject.toml` и составляет 90%.

## Управление

- `W`, `A`, `S`, `D` - движение
- мышь - прицеливание
- левая кнопка мыши - стрельба
- `1`, `2`, `3` - смена оружия
- `Esc` - возврат в меню
- в меню: `W/S` или стрелки для выбора, `Enter` или `Пробел` для подтверждения

## Возможности

- 3 вида оружия: `Pistol`, `Shotgun`, `SMG`
- 5 типов врагов: `Walker`, `Runner`, `Tank`, `Shooter`, `Kamikaze`
- 20 последовательных волн в [`src/crimsoland/data/configs/waves.json`](src/crimsoland/data/configs/waves.json)
- таблица рекордов с хранением top-10 в [`src/crimsoland/data/highscores.json`](src/crimsoland/data/highscores.json)
- отдельные экраны меню, игры, справки, итогов и ввода имени
- fallback-режим без звука, если `pygame.mixer` недоступен или аудиофайлы не найдены

## Архитектура

Игра собрана вокруг `CrimsolandApp`, `StateManager` и отдельных экранов:

- `menu` - главное меню
- `game` - игровой экран
- `help` - справка
- `scores` - таблица рекордов
- `game_over` - экран завершения игры
- `name_input` - ввод имени для рекорда

Ключевые части проекта:

- `entities/` - игрок, враги и пули
- `systems/` - бой, коллизии, волны, анимации, звук, счет
- `screens/` - экраны интерфейса
- `data/configs/` - игровые JSON-конфиги

## Конфигурация

Основные параметры лежат в JSON-файлах:

- `game.json` - окно, арена, UI, правила игры, лимиты рекордов
- `player.json` - характеристики игрока и стартовое оружие
- `weapons.json` - параметры оружия
- `enemies.json` - параметры врагов
- `waves.json` - состав и порядок волн
- `audio.json` - музыка, звуки и уровни громкости
- `highscores.json` - сохраненные результаты игроков

## Структура проекта

```text
.
|-- pyproject.toml
|-- README.md
|-- src/
|   `-- crimsoland/
|       |-- __init__.py
|       |-- __main__.py
|       |-- app.py
|       |-- config_loader.py
|       |-- events.py
|       |-- main.py
|       |-- resource_manager.py
|       |-- settings.py
|       |-- state_manager.py
|       |-- ui_text.py
|       |-- utils.py
|       |-- data/
|       |   |-- configs/
|       |   `-- highscores.json
|       |-- entities/
|       |-- screens/
|       `-- systems/
`-- tests/
```
