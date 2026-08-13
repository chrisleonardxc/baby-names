.PHONY: up down build seed seed-country logs

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

seed:
	docker compose --profile tools run --rm ingestion --all

seed-country:
	docker compose --profile tools run --rm ingestion --sources $(COUNTRY)

logs:
	docker compose logs -f
