# Stand Booking Bot

> Для локального запуска нужен локальный Mattermost — поднимается автоматически через `make init`.

## Оглавление

- [Описание](#описание)
- [Стек](#стек)
- [Инструменты разработки](#инструменты-разработки)
- [Переменные окружения](#переменные-окружения)
- [Быстрый старт](#быстрый-старт)
- [Полезные make-команды](#полезные-make-команды)
- [Локальный Mattermost](#локальный-mattermost)
- [Интеграция с Mattermost](#интеграция-с-mattermost)
- [Команды бота](#команды-бота)
- [Мониторинг и наблюдаемость](#мониторинг-и-наблюдаемость)
- [Схема взаимодействия](#схема-взаимодействия)

## Описание

Чат-бот для Mattermost, который ведёт учёт занятости тестовых стендов: кто занял стенд, когда,
и позволяет освободить его. Решает проблему "непонятно, кто и когда занял стенд" — снижает риск
случайно сломать чужую работу, раскатив свою ветку на занятый стенд.

Рассчитан на небольшую команду с минимальной нагрузкой.
Ролей нет — все команды доступны всем участникам канала, модель строится на ответственности
пользователей, а не на правах доступа. История занятости не хранится — только текущее состояние
каждого стенда (`free` / `occupied`, кем и с какого момента).

Бот обслуживает несколько команд (**team**) одновременно: у каждой team свой webhook-токен и свой
список стендов. Связка team → токен → стенды описывается в `config/channels.yml`, сами значения
токенов — в `.env` (по переменной на team).

## Стек

- Python 3.12+, FastAPI, uvicorn, pydantic / pydantic-settings
- SQLAlchemy (ORM), PostgreSQL, Alembic (миграции применяются автоматически при старте контейнера)
- structlog (структурированное логирование), Sentry, Elastic APM, Prometheus (RED-метрики)
- pytest / pytest-asyncio, ruff, pre-commit
- Docker / Docker Compose, uv

## Инструменты разработки

| Инструмент   | Назначение                                        |
|--------------|----------------------------------------------------|
| `uv`         | Управление зависимостями и виртуальным окружением   |
| `ruff`       | Линтер и форматтер (замена flake8/black/isort)      |
| `pre-commit` | Автоматическая проверка кода перед коммитом         |
| `pytest`     | Тесты                                               |

## Переменные окружения

`.env` создаётся автоматически из `.env.example` при `make init` (или вручную: `cp .env.example .env`).

| Переменная                                            | Назначение                                                              |
|---------------------------------------------------------|----------------------------------------------------------------------------|
| `ENVIRONMENT`                                          | `local` / `dev` / `prod` — влияет на формат логов и теги Sentry/APM        |
| `WEBHOOK_TOKEN_<TEAM>`                                 | Токен, который Mattermost выдаст при создании Outgoing Webhook для конкретной team — по переменной на team, имя переменной задаётся полем `token_env` в `config/channels.yml` (например `WEBHOOK_TOKEN_AKB`) |
| `CHANNELS_CONFIG_PATH`                                 | Опционально: путь к YAML-конфигу команд, по умолчанию `config/channels.yml` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`  | Учётные данные локальной БД бота                                          |
| `POSTGRES_HOST` / `POSTGRES_PORT`                      | Хост/порт Postgres (по умолчанию — сервис `stands-bot-postgres`, `5432`)   |
| `SENTRY_DSN` / `SENTRY_TRACES_SAMPLE_RATE`             | Опционально: пусто — интеграция с Sentry отключена                        |
| `ELASTIC_APM_SERVER_URL` / `ELASTIC_APM_SERVICE_NAME`  | Опционально: пусто — интеграция с Elastic APM отключена                   |

`DATABASE_URL` отдельно не задаётся — собирается из `POSTGRES_*` автоматически.

### Конфигурация команд (`config/channels.yml`)

Список team, их webhook-токенов и стендов описывается декларативно:

```yaml
channels:
  akb:
    token_env: WEBHOOK_TOKEN_AKB
    stands:
      - akb1
      - slplay4
      - slplay7
      - slplay8
      - slplay9

  sl:
    token_env: WEBHOOK_TOKEN_SL
    stands:
      - ecom5
      - slplay1
      - slplay2
```

Чтобы добавить новую team, изменения в коде не нужны:

1. Добавить в `config/channels.yml` новую секцию с уникальным именем team, `token_env` и списком стендов.
2. Добавить в `.env` переменную с этим именем (`token_env`) и токеном, который Mattermost выдаст при создании Outgoing Webhook для канала этой team.
3. Перезапустить бота — при старте он сам создаст недостающие стенды и привяжет их к своей team.

Если `token_env`, указанный в конфиге, отсутствует в окружении — соответствующая team пропускается
(в лог пишется warning), остальные team продолжают работать как обычно.

## Быстрый старт

Первый запуск — одна команда, настраивает всё: зависимости, `.env`, git-хуки, локальный Mattermost,
подключение бота к нему и сам бот:

```bash
cd akb-stands-bot
make init
```

В процессе потребуется один ручной шаг — создать администратора и команду в Mattermost через браузер
(это единственное, что нельзя автоматизировать).

## Полезные make-команды

```bash
make help       # список всех команд
make up         # поднять бота + Postgres (dev)
make down       # остановить бота + Postgres
make up-prod    # поднять бота в prod-конфигурации
make down-prod  # остановить бота (prod)
make mm-up      # поднять уже развёрнутый локальный Mattermost
make mm-down    # остановить локальный Mattermost
make test       # прогнать тесты (без докера)
make lint       # проверить код ruff
make format     # отформатировать код ruff
make hooks      # установить git pre-commit хуки
```

## Локальный Mattermost

`make init` разворачивает официальный `mattermost/docker` в `./mattermost` (каталог в `.gitignore`,
не часть репозитория). Скрипт `scripts/setup-mattermost.sh` превентивно применяет фиксы известных
проблем локального запуска на macOS/Docker Desktop (именованные volumes вместо bind-mount, корректный
`SITEURL`, `DOMAIN=localhost`), поднимает Mattermost и после того, как вы создали аккаунт и команду,
автоматически разрешает боту (`stands-bot`) подключаться как untrusted internal connection.

Дальше управлять им можно отдельно: `make mm-up` / `make mm-down`.

## Интеграция с Mattermost

Используется **Outgoing Webhook**. Приватные каналы не поддерживаются, только публичные.

### Настройка (один раз на канал/team)
1. Публичный канал → **System Console → Integrations → Outgoing Webhooks** → Add outgoing webhook.
2. Триггер-слова: `--list`, `--take`, `--free` (`trigger_when = "first word starts with"`).
3. Callback URL: `http://stands-bot:8000/webhook` (_локально_).
4. Сохранить выданный токен в переменную `.env`, указанную как `token_env` для этой team в
   `config/channels.yml` (см. [Конфигурация команд](#конфигурация-команд-configchannelsyml)).

## Команды бота

| Команда              | Действие                                                           |
|----------------------|--------------------------------------------------------------------|
| `--list`             | Показать список стендов со статусами                               |
| `--take <num\|name>` | Занять стенд (принудительно, перезаписывает текущего владельца)    |
| `--free <num\|name>` | Освободить стенд                                                   |

Команды указываются без `/`, так как сообщения с `/` перехватываются клиентом Mattermost как
slash-команды и не доходят до сервера.

## Мониторинг и наблюдаемость

- `GET /health/live` — процесс жив (liveness probe).
- `GET /health/ready` — доступность Postgres (readiness probe), 200/503.
- `GET /metrics` — Prometheus, RED-метрики (rate, errors, duration) по всем эндпоинтам.
- **Sentry** — включается автоматически, если задан `SENTRY_DSN`.
- **Elastic APM** — включается автоматически, если задан `ELASTIC_APM_SERVER_URL`.
- Логи — структурированные (structlog): человекочитаемые в `local`/`dev`, JSON в `prod`.

## Схема взаимодействия

```
Пользователь пишет в канале: "--list" / "--take slplay7" / "--release slplay7"
              │
              ▼
   Mattermost (Outgoing Webhook)
              │  POST /webhook (form-urlencoded: token, channel_id, user_name, text, trigger_word)
              ▼
        Stand Booking Bot (FastAPI)
              │  1. проверка токена
              │  2. CommandDispatcher → Command по trigger_word
              │  3. чтение/запись состояния стенда в PostgreSQL
              ▼
   Ответ бота (JSON { "text": "..." })
              │
              ▼
   Mattermost публикует ответ как обычное сообщение в тот же канал
```
