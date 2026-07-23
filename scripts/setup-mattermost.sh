#!/usr/bin/env bash
# Разворачивает локальный Mattermost с нуля (официальный docker-compose,
# https://docs.mattermost.com/deployment-guide/server/deploy-containers.html)
# внутри give_me_test_env/mattermost и превентивно применяет фиксы известных
# проблем локального запуска на macOS/Docker Desktop:
#   - именованные Docker volumes вместо bind-mount (permission denied на VirtioFS);
#   - DOMAIN=localhost вместо 127.0.0.1 (иначе CORS-рассинхрон после онбординга);
#   - MM_SERVICESETTINGS_SITEURL по http, без TLS (nginx/сертификаты тут не нужны).
# Вызывается из `make init`, вручную не запускается.
set -euo pipefail

cd "$(dirname "$0")/.."

MM_DIR="mattermost"

if ! command -v git >/dev/null 2>&1; then
  echo "git не найден, он нужен для скачивания mattermost/docker." >&2
  exit 1
fi

if [ -d "$MM_DIR" ]; then
  echo "Каталог $MM_DIR уже существует, пропускаю скачивание."
else
  echo "Скачиваю официальный docker-compose Mattermost..."
  git clone --depth 1 https://github.com/mattermost/docker.git "$MM_DIR"
fi

cd "$MM_DIR"

if [ ! -f .env ]; then
  cp env.example .env
fi

sed -i.bak \
  -e 's/^DOMAIN=.*/DOMAIN=localhost/' \
  -e 's|^MM_SERVICESETTINGS_SITEURL=.*|MM_SERVICESETTINGS_SITEURL=http://${DOMAIN}:${APP_PORT}|' \
  .env

if [ ! -f docker-compose.override.yml ]; then
  cat >docker-compose.override.yml <<'EOF'
volumes:
  postgres_data:
  mattermost_config:
  mattermost_data:
  mattermost_logs:
  mattermost_plugins:
  mattermost_client_plugins:
  mattermost_bleve_indexes:
EOF
fi

# *_PATH переменные должны ссылаться на именованные volume из override.yml выше,
# а не на bind-mount пути — это и есть обход permission denied на macOS.
sed -i.bak \
  -e 's|^POSTGRES_DATA_PATH=.*|POSTGRES_DATA_PATH=postgres_data|' \
  -e 's|^MATTERMOST_CONFIG_PATH=.*|MATTERMOST_CONFIG_PATH=mattermost_config|' \
  -e 's|^MATTERMOST_DATA_PATH=.*|MATTERMOST_DATA_PATH=mattermost_data|' \
  -e 's|^MATTERMOST_LOGS_PATH=.*|MATTERMOST_LOGS_PATH=mattermost_logs|' \
  -e 's|^MATTERMOST_PLUGINS_PATH=.*|MATTERMOST_PLUGINS_PATH=mattermost_plugins|' \
  -e 's|^MATTERMOST_CLIENT_PLUGINS_PATH=.*|MATTERMOST_CLIENT_PLUGINS_PATH=mattermost_client_plugins|' \
  -e 's|^MATTERMOST_BLEVE_INDEXES_PATH=.*|MATTERMOST_BLEVE_INDEXES_PATH=mattermost_bleve_indexes|' \
  .env
rm -f .env.bak

# shellcheck disable=SC1091
APP_PORT="$(grep -E '^APP_PORT=' .env | cut -d= -f2)"
APP_PORT="${APP_PORT:-8065}"

echo "Поднимаю Mattermost..."
docker compose -f docker-compose.yml -f docker-compose.without-nginx.yml -f docker-compose.override.yml up -d

echo "Жду, пока Mattermost станет доступен на http://localhost:${APP_PORT}..."
for _ in $(seq 1 30); do
  if curl -sf "http://localhost:${APP_PORT}/api/v4/system/ping" >/dev/null 2>&1; then
    echo "Mattermost готов."
    break
  fi
  sleep 2
done

cat <<EOF

Mattermost поднят: http://localhost:${APP_PORT}
1. Откройте адрес в браузере.
2. При первом запуске Mattermost попросит создать администратора и команду — это
   единственный шаг, который нельзя автоматизировать (интерактивная регистрация).

EOF

read -rp "Нажмите Enter, когда аккаунт и команда созданы и вы вошли в Mattermost..."
