#!/usr/bin/env bash
# Подключает бота к локальному Mattermost: разрешает исходящий webhook-callback
# на внутренний хост stands-bot (Mattermost по умолчанию блокирует запросы к
# untrusted internal connections). Вызывается из `make init` после того, как
# setup-mattermost.sh дождался, что разработчик вошёл в Mattermost.
set -euo pipefail

MM_CONTAINER="mattermost-mattermost-1"

if ! docker ps --format '{{.Names}}' | grep -qx "$MM_CONTAINER"; then
  echo "Контейнер $MM_CONTAINER не запущен. Сначала выполните make mm-up." >&2
  exit 1
fi

echo "Разрешаю боту stands-bot подключаться к Mattermost (untrusted internal connections)..."
docker exec "$MM_CONTAINER" mmctl config set ServiceSettings.AllowedUntrustedInternalConnections "stands-bot" --local

cat <<'EOF'

Готово. Осталось настроить Outgoing Webhook в интерфейсе Mattermost
(см. README.md, раздел "Интеграция с Mattermost") и указать выданный
токен в STANDS_BOT_WEBHOOK_TOKEN в .env.
EOF
