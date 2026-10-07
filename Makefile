up:
	docker compose up --build

up-d:
	docker compose up -d --build

down:
	docker compose down

reset:
	docker compose down -v

pipeline:
	docker compose run --rm analytics

test:
	docker compose run --rm analytics pytest -q

logs:
	docker compose logs -f
