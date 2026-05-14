.PHONY: up-staging up-prod up-staging-proxy up-prod-proxy down logs ps

up-staging:
	docker compose --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml up -d --build

up-prod:
	docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build

up-staging-proxy:
	docker compose --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml -f docker-compose.proxy.yml up -d --build

up-prod-proxy:
	docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.proxy.yml up -d --build

down:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml -f docker-compose.prod.yml -f docker-compose.proxy.yml -f docker-compose.proxy.tls.yml down

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps
