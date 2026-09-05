.PHONY: up down restart logs ps test

up:
	docker compose build --no-cache
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

test:
	docker compose --env-file .env.test -f compose.test.yml build --no-cache tests
	docker compose --env-file .env.test -f compose.test.yml up -d test-database
	docker compose --env-file .env.test -f compose.test.yml run --rm tests pytest -v; \
	status=$$?; \
	docker compose --env-file .env.test -f compose.test.yml down; \
	exit $$status