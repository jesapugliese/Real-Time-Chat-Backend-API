.PHONY: up down restart logs ps test

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

test:
	docker compose --env-file .env.test -f compose.test.yml up -d test-database
	docker compose --env-file .env.test -f compose.test.yml run --rm --build tests pytest -v; \
	status=$$?; \
	docker compose --env-file .env.test -f compose.test.yml down; \
	exit $$status