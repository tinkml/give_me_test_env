up:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build

down:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml down

up-prod:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d --build

down-prod:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml down
