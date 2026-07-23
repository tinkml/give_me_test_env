#!/usr/bin/env bash
# Проверяет/устанавливает зависимости разработки и готовит .env.
# Вызывается из `make init`, вручную не запускается.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v uv >/dev/null 2>&1; then
  echo "uv не найден, устанавливаю..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker не найден. Установите Docker Desktop: https://www.docker.com/products/docker-desktop/" >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin не найден. Обновите Docker Desktop." >&2
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env создан из .env.example — при необходимости заполните значения."
else
  echo ".env уже существует, пропускаю."
fi
