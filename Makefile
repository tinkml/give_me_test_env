.PHONY: help init up down up-prod down-prod mm-up mm-down test lint format hooks

help:
	@echo "make init       - первичная настройка (зависимости, .env, git hooks, Mattermost, бот)"
	@echo "make up         - поднять бота + Postgres (dev)"
	@echo "make down       - остановить бота + Postgres (dev)"
	@echo "make up-prod    - поднять бота в prod-конфигурации"
	@echo "make down-prod  - остановить бота в prod-конфигурации"
	@echo "make mm-up      - поднять уже развёрнутый локальный Mattermost"
	@echo "make mm-down    - остановить локальный Mattermost"
	@echo "make test       - прогнать тесты (без докера)"
	@echo "make lint       - проверить код ruff"
	@echo "make format     - отформатировать код ruff"
	@echo "make hooks      - установить git pre-commit хуки"

init:
	bash scripts/setup-env.sh
	uv sync --group dev
	$(MAKE) hooks
	bash scripts/setup-mattermost.sh
	bash scripts/connect-bot.sh
	$(MAKE) up
	@echo "Готово: бот и Mattermost подняты."

up:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build

down:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml down

reload:
	make down && make up

up-prod:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d --build

down-prod:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml down

reload-prod:
	make down-prod && make up-prod

mm-up:
	docker compose -f mattermost/docker-compose.yml -f mattermost/docker-compose.without-nginx.yml -f mattermost/docker-compose.override.yml up -d

mm-down:
	docker compose -f mattermost/docker-compose.yml -f mattermost/docker-compose.without-nginx.yml -f mattermost/docker-compose.override.yml down

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

hooks:
	uv run pre-commit install
