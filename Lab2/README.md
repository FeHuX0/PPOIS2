# Спортсмены

GUI-приложение на Python для ведения записей о спортсменах по шаблону MVC.

## Стек

- PostgreSQL
- SQLAlchemy 2.x
- PySide6
- XML DOM/SAX

## Структура

- `src/db` - engine, session, инициализация БД
- `src/models` - SQLAlchemy модели
- `src/repo` - CRUD и транзакционные операции
- `src/fetch` - выборки, фильтры, distinct-списки и пагинация
- `src/ingest` - импорт/экспорт XML и генерация демо-данных
- `src/services` - сервисный слой и фабрика сервисов
- `src/view` - GUI-слой
- `src/controller` - контроллер приложения

## Запуск

1. Установите зависимости:

```bash
uv sync
```

2. Задайте переменную окружения:

```bash
set DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/athletes_db
```

Либо создайте `.env` в корне проекта:

```env
POSTGRES_DB=athletes_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/athletes_db
```

3. При использовании Docker Compose сначала поднимите PostgreSQL:

```bash
docker compose up -d
```

`docker-compose.yml` запускает только базу данных. GUI-приложение запускается отдельно с хоста и использует `DATABASE_URL` из `.env`.

4. Сгенерируйте демо XML:

```bash
uv run python -m src.ingest.demo_generator
```

5. Запустите приложение:

```bash
uv run python -m src.main
```

## XML

Экспорт выполняется через `xml.dom.minidom`, импорт - через `xml.sax`.

## Поиск и удаление

Поиск и удаление используют единый билдер SQLAlchemy-фильтров из `src.fetch.athlete_fetch`.

## Сессии и сервисы

Работа с SQLAlchemy-сессиями централизована через типизированный context manager в `src.db.session`, настройки загружаются из `src.core.settings`, а сервисы создаются через `src.services.service_factory`.

## Примечание по uv

Зависимости проекта хранятся в `pyproject.toml` и используются через `uv`. Файл `.env` предназначен только для конфигурации окружения, например `DATABASE_URL`.
