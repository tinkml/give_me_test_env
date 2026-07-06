up:
    docker compose -f docker/docker-compose.yml up -d --build

down:
    docker compose -f docker/docker-compose.yml down

up-local:
    docker compose -f docker/docker-compose.local.yml up -d --build

down-local:
    docker compose -f docker/docker-compose.local.yml down